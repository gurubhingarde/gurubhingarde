#!/usr/bin/env python3
"""
Airpump ECU Flash Tool — GUI
Requires: pip install python-can
"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import threading
import time
import logging
import queue
import sys

import can

# ── Protocol constants ────────────────────────────────────────────────────────

PUMP_TYPES = {
    "Air Pump": {"tool_id": 0x180006FF, "ecu_id": 0x1800FF06},
    "Oil Pump": {"tool_id": 0x180005FF, "ecu_id": 0x1800FF05},
}
BCAST_ID = 0x1800FFFF

HEARTBEAT_INTERVAL  = 0.101
HEARTBEAT_COUNT     = 60
ECU_WAKEUP_TIMEOUT  = 3.0
PAYLOAD_BYTES      = 6
ERASE_TIMEOUT      = 5.0
PROG_TIMEOUT       = 5.0
ACK_TIMEOUT        = 1.0
LAST_FRAME_TIMEOUT = 1.0


# ── Protocol helpers ──────────────────────────────────────────────────────────

def xor8(data):
    r = 0
    for b in data[:7]:
        r ^= b
    return r

def make_frame(b0, payload):
    raw = bytes([b0]) + bytes(payload)
    return raw + bytes([xor8(raw)])

def verify_frame(data):
    return len(data) == 8 and xor8(data) == data[7]


# ── Hex loader ────────────────────────────────────────────────────────────────

ECU_FLASH_BASE = 0x003E8000
BLOCK_ID_BASE  = ECU_FLASH_BASE + 6 * 0x2000  # 0x003F4000


def load_hex(path):
    """
    Address-aware Intel HEX reader.
    Returns (segments, crc_bytes, crc_addr, base_addr) where segments is a list of
    (start_addr, data_bytes) tuples for each contiguous address region in the file.
    """
    records = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line.startswith(':'):
                continue
            bc   = int(line[1:3], 16)
            addr = int(line[3:7], 16)
            rt   = int(line[7:9], 16)
            data = bytes.fromhex(line[9:9 + bc * 2])
            records.append((bc, addr, rt, data))

    ela = 0
    crc_addr  = None
    base_addr = None
    for bc, addr, rt, data in records:
        if rt == 4:
            ela = int.from_bytes(data, "big") << 16
        elif rt == 0:
            full = ela | addr
            if bc == 4:
                crc_addr = full
            if base_addr is None and bc > 4:
                base_addr = full

    if crc_addr is None:
        raise ValueError("No 4-byte CRC record found in hex file")
    if base_addr is None:
        raise ValueError("No data records found in hex file")

    addr_map = {}
    seq = bytearray()
    ela = 0
    for bc, addr, rt, data in records:
        if rt == 4:
            ela = int.from_bytes(data, "big") << 16
        elif rt == 0:
            full = ela | addr
            for i, b in enumerate(data):
                addr_map[full + i] = b
            seq += data
        elif rt == 1:
            break

    # CRC from sequential tail — robust against multiple bc==4 records in file
    crc_bytes = bytes(seq[-4:])
    for i in range(4):
        addr_map.pop(crc_addr + i, None)

    segments = []
    if addr_map:
        sorted_addrs = sorted(addr_map.keys())
        seg_start = sorted_addrs[0]
        seg_data  = bytearray()
        prev_addr = sorted_addrs[0] - 1
        for a in sorted_addrs:
            if a != prev_addr + 1:
                if seg_data:
                    segments.append((seg_start, bytes(seg_data)))
                seg_start = a
                seg_data  = bytearray()
            seg_data.append(addr_map[a])
            prev_addr = a
        if seg_data:
            segments.append((seg_start, bytes(seg_data)))

    return segments, crc_bytes, crc_addr, base_addr


# ── Block builder ─────────────────────────────────────────────────────────────

def build_blocks(segments, log_fn=None):
    """
    Build flash blocks from (addr, data) segments, preserving non-aligned patches.

    Block-id rules (reverse-engineered from OEM traces):
      - Aligned + full (== 16 KB) : id = (BLOCK_ID_BASE - addr) // 8KB
      - Aligned + partial         : id = formula + 1
      - Non-aligned (patch)       : id = formula on floor(addr, 8KB)
      - Last block overall        : id = 1
    """
    ADDR_STEP = 0x2000
    MAX_BLOCK = 0x4000
    blocks    = []
    for seg_addr, seg_data in segments:
        offset = 0
        addr   = seg_addr
        while offset < len(seg_data):
            chunk   = seg_data[offset:offset + MAX_BLOCK]
            is_full = (len(chunk) == MAX_BLOCK)
            aligned = (addr % ADDR_STEP == 0)

            if aligned and is_full:
                b_id = (BLOCK_ID_BASE - addr) // ADDR_STEP
            elif aligned:
                b_id = (BLOCK_ID_BASE - addr) // ADDR_STEP + 1
            else:
                floor_addr = (addr // ADDR_STEP) * ADDR_STEP
                b_id = (BLOCK_ID_BASE - floor_addr) // ADDR_STEP

            if log_fn:
                log_fn(f"    0x{addr:08X}  {len(chunk):5d} B  id=0x{b_id:02X}")
            blocks.append({"addr": addr, "size": len(chunk),
                            "data": chunk, "block_id": b_id})
            offset += MAX_BLOCK
            addr   += ADDR_STEP

    if blocks:
        blocks[-1]["block_id"] = 1
    return blocks

def addr_to_04_payload(full_addr, size):
    return bytes([
        (full_addr >> 24) & 0xFF,
        (full_addr >> 16) & 0xFF,
        (full_addr >>  8) & 0xFF,
        (full_addr      ) & 0xFF,
        (size      >>  8) & 0xFF,
         size             & 0xFF,
    ])


# ── Flash worker (runs in background thread) ──────────────────────────────────

class FlashWorker:
    def __init__(self, interface, channel, bitrate, hex_path, log_q, progress_q,
                 tool_id, ecu_id):
        self.interface  = interface
        self.channel    = channel
        self.bitrate    = bitrate
        self.hex_path   = hex_path
        self.log_q      = log_q
        self.tool_id    = tool_id
        self.ecu_id     = ecu_id
        self.progress_q = progress_q
        self.bus        = None
        self.abort      = False

    def log(self, msg):
        self.log_q.put(msg)

    def progress(self, val):
        self.progress_q.put(val)

    def send_and_wait(self, data, timeout=ACK_TIMEOUT):
        assert verify_frame(data)
        msg = can.Message(arbitration_id=self.tool_id, data=data, is_extended_id=True)
        self.bus.send(msg)
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.abort:
                raise RuntimeError("Aborted by user")
            rx = self.bus.recv(timeout=min(0.05, deadline - time.monotonic()))
            if rx and rx.arbitration_id == self.ecu_id and bytes(rx.data) == data:
                return
            if rx and rx.arbitration_id == 0x1800EEEE:
                nak_data = bytes(rx.data)
                self.log(f"  ⚠️  ECU NAK (0x1800EEEE): {nak_data.hex().upper()}")
                raise RuntimeError(
                    f"ECU rejected frame — address incompatible with current firmware.\n"
                    f"  Sent   : {data.hex().upper()}\n"
                    f"  ECU NAK: {nak_data.hex().upper()}\n"
                    f"  Likely cause: hex file base address (0x{int.from_bytes(nak_data[0:4],'big'):08X}) "
                    f"differs from firmware currently in ECU.\n"
                    f"  The ECU bootloader only accepts reflashing at the same base address.\n"
                    f"  Solution: use a hex file built for base address 0x003E8000, or obtain\n"
                    f"  the correct production hex from the OEM."
                )
        raise RuntimeError(f"No ACK for {data.hex().upper()}")

    def run(self):
        try:
            self.log("Loading hex file...")
            self.log(f"  Tool ID  : 0x{self.tool_id:08X}  ECU ID: 0x{self.ecu_id:08X}")
            segments, crc_bytes, crc_addr, base_addr = load_hex(self.hex_path)
            crc_int   = int.from_bytes(crc_bytes, "big")
            total_seg = sum(len(d) for _, d in segments)
            self.log(f"  Segments : {len(segments)} ({total_seg:,} bytes total)")
            self.log(f"  Base addr: 0x{base_addr:08X}")
            self.log(f"  CRC      : 0x{crc_int:08X}  at 0x{crc_addr:08X}")

            self.log(f"  Blocks:")
            blocks = build_blocks(segments, log_fn=self.log)

            total_frames = sum(-(-b["size"] // PAYLOAD_BYTES) for b in blocks)

            self.log(f"\nOpening CAN: {self.interface} / {self.channel} @ {self.bitrate} bps")
            try:
                self.bus = can.interface.Bus(
                    interface=self.interface,
                    channel=self.channel,
                    bitrate=self.bitrate,
                )
            except Exception as e:
                hint = ""
                msg  = str(e).lower()
                if "invalid" in msg or "handle" in msg:
                    hint = (
                        "\n  Hint: Channel not found — use '🔍 Detect' button to find"
                        " your PCAN device,\n  or check that PCAN-USB is plugged in"
                        " and the Peak driver is installed."
                    )
                elif "access" in msg or "permission" in msg:
                    hint = "\n  Hint: Permission denied — try running as Administrator (Windows) or check udev rules (Linux)."
                elif "bitrate" in msg or "baud" in msg:
                    hint = "\n  Hint: Bitrate mismatch — try 500000 bps."
                raise RuntimeError(f"Cannot open CAN bus: {e}{hint}") from None
            self.log("  CAN bus open ✓")

            hb_byte = (BLOCK_ID_BASE - base_addr) // 0x2000 + 1
            hb_data = make_frame(0x00, bytes([0x00, hb_byte, 0x00, 0x00, 0x00, 0x00]))
            self.log("\n[1/5] Keepalive — waking ECU...")
            self.log(f"  Heartbeat byte: 0x{hb_byte:02X}  (base 0x{base_addr:08X})")
            self.log(f"  Waiting up to {HEARTBEAT_COUNT * HEARTBEAT_INTERVAL:.0f} s "
                     f"(works with powered-on ECU or live ECU app)...")
            hb_msg  = can.Message(arbitration_id=self.tool_id, data=hb_data, is_extended_id=True)
            ecu_woke = False
            hb_sent  = 0
            for i in range(HEARTBEAT_COUNT):
                if self.abort:
                    raise RuntimeError("Aborted")
                self.bus.send(hb_msg)
                hb_sent += 1
                self.progress(0.01 * i / HEARTBEAT_COUNT)
                rx = self.bus.recv(timeout=0.08)
                if rx and rx.arbitration_id == self.ecu_id:
                    elapsed = hb_sent * HEARTBEAT_INTERVAL
                    mode = "live ECU → rebooted to bootloader" if hb_sent > 15 else "bootloader / cold-start"
                    self.log(f"  ECU responded ✓  ({bytes(rx.data).hex().upper()})")
                    self.log(f"  Mode detected : {mode}  (after {hb_sent} heartbeats, ~{elapsed:.1f} s)")
                    ecu_woke = True
                    break
                time.sleep(max(0, HEARTBEAT_INTERVAL - 0.08))

            if not ecu_woke:
                deadline = time.monotonic() + ECU_WAKEUP_TIMEOUT
                while time.monotonic() < deadline:
                    if self.abort:
                        raise RuntimeError("Aborted")
                    rx = self.bus.recv(timeout=0.2)
                    if rx and rx.arbitration_id == self.ecu_id:
                        self.log(f"  ECU responded ✓  ({bytes(rx.data).hex().upper()})")
                        ecu_woke = True
                        break

            if not ecu_woke:
                raise RuntimeError(
                    "ECU did not respond to keepalive.\n"
                    "  • For cold-start: power on ECU while tool is running\n"
                    "  • For live flash : ECU app must be running before clicking Flash"
                )

            self.log(f"\n[2/5] Flashing {len(blocks)} blocks...")
            frames_done = 0

            for blk_idx, block in enumerate(blocks):
                if self.abort:
                    raise RuntimeError("Aborted")
                self.log(f"  Block {blk_idx+1}/{len(blocks)}  "
                         f"0x{block['addr']:08X}  {block['size']} B  "
                         f"id=0x{block['block_id']:02X}")

                init_pl = addr_to_04_payload(block["addr"], block["size"])
                self.send_and_wait(make_frame(0x04, init_pl), timeout=ERASE_TIMEOUT)
                self.log(f"    Erase ACK ✓")

                toggle  = 0x01
                data    = block["data"]
                n       = -(-block["size"] // PAYLOAD_BYTES)
                offset  = 0
                chunk   = b""

                for fi in range(n):
                    if self.abort:
                        raise RuntimeError("Aborted")
                    chunk = data[offset:offset + PAYLOAD_BYTES]
                    if len(chunk) < PAYLOAD_BYTES:
                        chunk = chunk.ljust(PAYLOAD_BYTES, b'\xFF')
                    is_last = (fi == n - 1)
                    t = LAST_FRAME_TIMEOUT if is_last else ACK_TIMEOUT
                    self.send_and_wait(make_frame(toggle, chunk), timeout=t)
                    toggle = 0x02 if toggle == 0x01 else 0x01
                    offset += PAYLOAD_BYTES
                    frames_done += 1
                    self.progress(0.05 + 0.85 * frames_done / total_frames)

                eob_pl = bytes([0x00, block["block_id"]]) + bytes(chunk[2:6])
                self.send_and_wait(make_frame(0x00, eob_pl))
                self.log(f"    Block done ✓")

            self.log("\n[3/5] Program command (writing CRC to NVM)...")
            prog_pl = addr_to_04_payload(crc_addr, 4)
            self.send_and_wait(make_frame(0x04, prog_pl), timeout=PROG_TIMEOUT)
            self.log("  Program ACK ✓")
            self.progress(0.93)

            self.log("\n[4/5] Verify...")
            crc_pl = bytes([0x00]) + crc_bytes[1:4] + bytes([0xFF, 0xFF])
            self.send_and_wait(make_frame(0x01, crc_pl))
            self.log("  Verify ACK ✓")
            self.progress(0.96)

            self.log("\n[5/5] Close session...")
            self.send_and_wait(make_frame(0x03, crc_pl), timeout=0.5)
            self.log("  Close ACK ✓")
            self.progress(0.99)

            deadline = time.monotonic() + 2.0
            while time.monotonic() < deadline:
                rx = self.bus.recv(timeout=0.2)
                if rx and rx.arbitration_id == BCAST_ID:
                    self.log(f"  Broadcast: {bytes(rx.data).hex().upper()} ✓")
                    break

            self.progress(1.0)
            self.log("\n✅  FLASH COMPLETE!")

        except Exception as e:
            self.log(f"\n❌  ERROR: {e}")
        finally:
            self.progress(-1)
            if self.bus:
                self.bus.shutdown()


# ── GUI ───────────────────────────────────────────────────────────────────────

INTERFACES = ["pcan", "socketcan", "kvaser", "vector", "ixxat", "usb2can", "virtual"]

PCAN_CHANNELS = [
    "PCAN_USBBUS1", "PCAN_USBBUS2", "PCAN_USBBUS3", "PCAN_USBBUS4",
    "PCAN_PCIBUS1", "PCAN_PCIBUS2",
]
SOCKETCAN_CHANNELS = ["can0", "can1", "vcan0"]
KVASER_CHANNELS    = ["0", "1", "2"]
VECTOR_CHANNELS    = ["0", "1", "2"]
DEFAULT_CHANNELS   = {
    "pcan":      PCAN_CHANNELS,
    "socketcan": SOCKETCAN_CHANNELS,
    "kvaser":    KVASER_CHANNELS,
    "vector":    VECTOR_CHANNELS,
    "ixxat":     ["0", "1"],
    "usb2can":   ["COM3", "COM4", "/dev/ttyUSB0"],
    "virtual":   ["0"],
}

BITRATES = ["125000", "250000", "500000", "1000000"]


def detect_pcan_channels():
    found = []
    try:
        import can
        for ch in ["PCAN_USBBUS1","PCAN_USBBUS2","PCAN_USBBUS3","PCAN_USBBUS4",
                   "PCAN_USBBUS5","PCAN_USBBUS6","PCAN_USBBUS7","PCAN_USBBUS8"]:
            try:
                bus = can.interface.Bus(interface="pcan", channel=ch, bitrate=500_000)
                bus.shutdown()
                found.append(ch)
            except Exception:
                pass
    except Exception:
        pass
    return found


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ECU Flash Tool")
        self.resizable(False, False)
        self.configure(bg="#1e1e2e")

        self.worker    = None
        self.log_q     = queue.Queue()
        self.prog_q    = queue.Queue()
        self._build_ui()
        self._poll()

    def _build_ui(self):
        PAD  = dict(padx=12, pady=6)
        CPAD = dict(padx=12, pady=3)

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TLabel",      background="#1e1e2e", foreground="#cdd6f4",
                        font=("Segoe UI", 10))
        style.configure("TFrame",      background="#1e1e2e")
        style.configure("TLabelframe", background="#1e1e2e", foreground="#89b4fa",
                        font=("Segoe UI", 10, "bold"))
        style.configure("TLabelframe.Label", background="#1e1e2e", foreground="#89b4fa")
        style.configure("TButton",     font=("Segoe UI", 10, "bold"),
                        background="#313244", foreground="#cdd6f4")
        style.map("TButton",
                  background=[("active", "#45475a"), ("disabled", "#181825")],
                  foreground=[("disabled", "#6c7086")])
        style.configure("Flash.TButton", background="#89b4fa", foreground="#1e1e2e",
                        font=("Segoe UI", 11, "bold"))
        style.map("Flash.TButton",
                  background=[("active", "#b4befe"), ("disabled", "#313244")],
                  foreground=[("disabled", "#6c7086")])
        style.configure("TCombobox",   fieldbackground="#313244", background="#313244",
                        foreground="#cdd6f4", selectbackground="#45475a")
        style.configure("TEntry",      fieldbackground="#313244", foreground="#cdd6f4",
                        insertcolor="#cdd6f4")
        style.configure("green.Horizontal.TProgressbar",
                        troughcolor="#313244", background="#a6e3a1", thickness=18)
        style.configure("red.Horizontal.TProgressbar",
                        troughcolor="#313244", background="#f38ba8", thickness=18)

        root = ttk.Frame(self, padding=16)
        root.pack(fill="both", expand=True)

        pg = ttk.LabelFrame(root, text=" Pump Type ", padding=10)
        pg.pack(fill="x", **PAD)

        self.pump_var = tk.StringVar(value="Air Pump")
        for name in PUMP_TYPES:
            ttk.Radiobutton(
                pg, text=name, variable=self.pump_var, value=name,
                style="TRadiobutton",
            ).pack(side="left", padx=16)

        style.configure("TRadiobutton", background="#1e1e2e", foreground="#cdd6f4",
                        font=("Segoe UI", 10))
        style.map("TRadiobutton",
                  background=[("active", "#1e1e2e")],
                  foreground=[("active", "#89b4fa")])

        fg = ttk.LabelFrame(root, text=" Firmware File ", padding=10)
        fg.pack(fill="x", **PAD)

        self.hex_var = tk.StringVar()
        ttk.Entry(fg, textvariable=self.hex_var, width=52,
                  font=("Segoe UI", 10)).pack(side="left", padx=(0, 8))
        ttk.Button(fg, text="Browse…", command=self._browse).pack(side="left")

        cg = ttk.LabelFrame(root, text=" CAN Settings ", padding=10)
        cg.pack(fill="x", **PAD)

        row1 = ttk.Frame(cg)
        row1.pack(fill="x", pady=(0, 4))

        ttk.Label(row1, text="Interface").pack(side="left")
        self.iface_var = tk.StringVar(value="pcan")
        iface_cb = ttk.Combobox(row1, textvariable=self.iface_var,
                                values=INTERFACES, width=14, state="readonly")
        iface_cb.pack(side="left", padx=(6, 24))
        iface_cb.bind("<<ComboboxSelected>>", self._iface_changed)

        ttk.Label(row1, text="Channel").pack(side="left")
        self.chan_var = tk.StringVar(value="PCAN_USBBUS1")
        self.chan_cb  = ttk.Combobox(row1, textvariable=self.chan_var,
                                     values=PCAN_CHANNELS, width=18)
        self.chan_cb.pack(side="left", padx=(6, 6))

        self.detect_btn = ttk.Button(row1, text="🔍 Detect",
                                     command=self._detect_channels, width=10)
        self.detect_btn.pack(side="left", padx=(0, 18))

        ttk.Label(row1, text="Bitrate").pack(side="left")
        self.baud_var = tk.StringVar(value="500000")
        ttk.Combobox(row1, textvariable=self.baud_var,
                     values=BITRATES, width=10, state="readonly").pack(side="left", padx=6)

        bg = ttk.Frame(root)
        bg.pack(fill="x", **CPAD)

        self.flash_btn = ttk.Button(bg, text="⚡  Flash ECU", style="Flash.TButton",
                                    command=self._start_flash, width=18)
        self.flash_btn.pack(side="left")

        self.abort_btn = ttk.Button(bg, text="■  Stop", command=self._abort,
                                    state="disabled", width=9)
        self.abort_btn.pack(side="left", padx=8)

        self.status_lbl = ttk.Label(bg, text="Ready", foreground="#a6e3a1",
                                    font=("Segoe UI", 10, "italic"))
        self.status_lbl.pack(side="left", padx=12)

        self.prog_var  = tk.DoubleVar(value=0)
        self.prog_bar  = ttk.Progressbar(root, variable=self.prog_var,
                                         maximum=100,
                                         style="green.Horizontal.TProgressbar",
                                         length=520)
        self.prog_bar.pack(fill="x", **CPAD)

        lg = ttk.LabelFrame(root, text=" Log ", padding=6)
        lg.pack(fill="both", expand=True, **PAD)

        self.console = scrolledtext.ScrolledText(
            lg, height=16, width=72,
            bg="#181825", fg="#cdd6f4",
            font=("Consolas", 9),
            insertbackground="#cdd6f4",
            state="disabled",
            relief="flat",
        )
        self.console.pack(fill="both", expand=True)

        self.console.tag_config("ok",    foreground="#a6e3a1")
        self.console.tag_config("err",   foreground="#f38ba8")
        self.console.tag_config("info",  foreground="#89dceb")
        self.console.tag_config("dim",   foreground="#6c7086")

        bot = ttk.Frame(root)
        bot.pack(fill="x", padx=12, pady=(0, 4))
        ttk.Button(bot, text="Clear log", command=self._clear_log).pack(side="left")
        ttk.Button(bot, text="Exit", command=self._exit).pack(side="right")

    def _browse(self):
        path = filedialog.askopenfilename(
            title="Select firmware hex file",
            filetypes=[("Intel HEX", "*.hex"), ("All files", "*.*")],
        )
        if path:
            self.hex_var.set(path)

    def _iface_changed(self, _=None):
        iface = self.iface_var.get()
        channels = DEFAULT_CHANNELS.get(iface, ["0"])
        self.chan_cb["values"] = channels
        self.chan_var.set(channels[0])
        if iface == "pcan":
            self.detect_btn.pack(side="left", padx=(0, 18))
        else:
            self.detect_btn.pack_forget()

    def _detect_channels(self):
        self.detect_btn.configure(state="disabled", text="Scanning…")
        self.status_lbl.configure(text="Detecting…", foreground="#fab387")
        self.update_idletasks()

        def _scan():
            found = detect_pcan_channels()
            self.after(0, lambda: self._on_detect_done(found))

        threading.Thread(target=_scan, daemon=True).start()

    def _on_detect_done(self, found):
        self.detect_btn.configure(state="normal", text="🔍 Detect")
        if found:
            self.chan_cb["values"] = found
            self.chan_var.set(found[0])
            self.status_lbl.configure(
                text=f"Found: {', '.join(found)}", foreground="#a6e3a1")
            self._log(f"Detected PCAN channels: {', '.join(found)}")
        else:
            self.status_lbl.configure(
                text="No PCAN device found", foreground="#f38ba8")
            self._log(
                "❌  No PCAN device detected.\n"
                "    • Make sure the PCAN-USB is plugged in\n"
                "    • Windows: install PCAN driver from peak-system.com\n"
                "    • Linux:   sudo modprobe peak_usb  (then use socketcan/can0)"
            )

    def _clear_log(self):
        self.console.configure(state="normal")
        self.console.delete("1.0", "end")
        self.console.configure(state="disabled")

    def _log(self, msg):
        self.console.configure(state="normal")
        if msg.startswith("✅"):
            tag = "ok"
        elif msg.startswith("❌") or "ERROR" in msg or "FAILED" in msg:
            tag = "err"
        elif msg.startswith("[") or msg.startswith("\n["):
            tag = "info"
        elif msg.strip().startswith("0x") or "id=0x" in msg:
            tag = "dim"
        else:
            tag = None
        self.console.insert("end", msg + "\n", tag)
        self.console.see("end")
        self.console.configure(state="disabled")

    def _set_running(self, running: bool):
        self.flash_btn.configure(state="disabled" if running else "normal")
        self.abort_btn.configure(state="normal"   if running else "disabled")

    def _start_flash(self):
        path = self.hex_var.get().strip()
        if not path:
            self._log("❌  ERROR: No hex file selected")
            return

        pump = PUMP_TYPES[self.pump_var.get()]
        self.prog_var.set(0)
        self.prog_bar.configure(style="green.Horizontal.TProgressbar")
        self.status_lbl.configure(text="Flashing…", foreground="#fab387")
        self._set_running(True)
        self._clear_log()

        self.worker = FlashWorker(
            interface=self.iface_var.get(),
            channel=self.chan_var.get(),
            bitrate=int(self.baud_var.get()),
            hex_path=path,
            log_q=self.log_q,
            progress_q=self.prog_q,
            tool_id=pump["tool_id"],
            ecu_id=pump["ecu_id"],
        )
        threading.Thread(target=self.worker.run, daemon=True).start()

    def _abort(self):
        if self.worker:
            self.worker.abort = True
        self.abort_btn.configure(state="disabled", text="Stopping…")
        self.status_lbl.configure(text="Stopping…", foreground="#f38ba8")
        self.after(3000, self._force_reset_if_stopping)

    def _exit(self):
        if self.worker:
            self.worker.abort = True
        self.destroy()

    def _reset_progress(self):
        self.prog_var.set(0)
        self.prog_bar.configure(style="green.Horizontal.TProgressbar")
        self.status_lbl.configure(text="Ready", foreground="#a6e3a1")

    def _force_reset_if_stopping(self):
        if self.status_lbl.cget("text") in ("Stopping…", "Aborting…"):
            self.abort_btn.configure(text="■  Stop")
            self._set_running(False)
            self._reset_progress()

    def _poll(self):
        while not self.log_q.empty():
            self._log(self.log_q.get_nowait())

        while not self.prog_q.empty():
            val = self.prog_q.get_nowait()
            if val < 0:
                if self.status_lbl.cget("text") == "Done ✓":
                    continue
                self.prog_bar.configure(style="red.Horizontal.TProgressbar")
                self.prog_var.set(100)
                was_aborted = self.worker and self.worker.abort
                self.status_lbl.configure(
                    text="Stopped" if was_aborted else "Failed",
                    foreground="#f38ba8",
                )
                self.abort_btn.configure(text="■  Stop")
                self._set_running(False)
                self.after(2000, self._reset_progress)
            else:
                self.prog_var.set(min(val, 1.0) * 100)
                if val >= 1.0:
                    self.status_lbl.configure(text="Done ✓", foreground="#a6e3a1")
                    self._set_running(False)

        self.after(80, self._poll)


if __name__ == "__main__":
    app = App()
    app.mainloop()
