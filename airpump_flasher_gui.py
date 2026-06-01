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

# ── Protocol constants (same as CLI tool) ─────────────────────────────────────

TOOL_ID  = 0x180006FF
ECU_ID   = 0x1800FF06
BCAST_ID = 0x1800FFFF

HEARTBEAT          = bytes([0x00, 0x00, 0x07, 0x00, 0x00, 0x00, 0x00, 0x07])
HEARTBEAT_INTERVAL = 0.101
HEARTBEAT_COUNT    = 20
ECU_WAKEUP_TIMEOUT = 3.0
PAYLOAD_BYTES      = 6
ERASE_TIMEOUT      = 2.0
PROG_TIMEOUT       = 2.0
ACK_TIMEOUT        = 0.5
LAST_FRAME_TIMEOUT = 0.5


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

def load_hex(path):
    """
    Parse Intel HEX using ADDRESS-MAPPED reading.
    Each record is written at its actual flash address; gaps become 0xFF.
    Returns (firmware_bytes, crc_4bytes, crc_flash_addr, hex_base_addr).
    firmware_bytes is a flat buffer from ECU_FLASH_BASE to crc_flash_addr (exclusive).
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
            if bc == 4:
                crc_addr = ela | addr   # last 4-byte record = CRC
            if base_addr is None and bc > 4:
                base_addr = ela | addr  # first real data record

    if crc_addr is None:
        raise ValueError("No 4-byte CRC record found in hex file")
    if base_addr is None:
        raise ValueError("No data records found in hex file")

    buf_size = crc_addr + 4 - ECU_FLASH_BASE
    if buf_size <= 0:
        raise ValueError(f"CRC addr 0x{crc_addr:08X} below ECU_FLASH_BASE 0x{ECU_FLASH_BASE:08X}")
    buf = bytearray(b'\xFF' * buf_size)

    ela = 0
    for bc, addr, rt, data in records:
        if rt == 4:
            ela = int.from_bytes(data, "big") << 16
        elif rt == 0:
            full_addr = ela | addr
            offset    = full_addr - ECU_FLASH_BASE
            if 0 <= offset and offset + bc <= buf_size:
                buf[offset:offset + bc] = data
        elif rt == 1:
            break

    crc_bytes = bytes(buf[crc_addr - ECU_FLASH_BASE : crc_addr - ECU_FLASH_BASE + 4])

    # If ECU_FLASH_BASE has no code (hex starts at a higher address), copy the
    # first 8 bytes from the first code page into offset 0.  The ECU reads back
    # flash[ECU_FLASH_BASE+4] (ARM reset-vector) after writing block 1 and will
    # abort the session if it is 0xFFFFFFFF (erased).  For old firmware whose
    # linker placed vectors at 0x3EA000 rather than 0x3E8000, those 8 bytes
    # (initial-SP + reset-handler) are a valid stand-in — the bootloader sets
    # VTOR before jumping to the app so only the app's own vector table matters
    # at runtime.
    if all(b == 0xFF for b in buf[0:8]):
        first_code = next(
            (off for off in range(0x2000, buf_size, 0x2000)
             if any(b != 0xFF for b in buf[off:off + 8])),
            None
        )
        if first_code is not None:
            buf[0:8] = buf[first_code:first_code + 8]

    firmware  = bytes(buf[:crc_addr - ECU_FLASH_BASE])
    return firmware, crc_bytes, crc_addr, base_addr


# ── Block builder ─────────────────────────────────────────────────────────────

ECU_FLASH_BASE = 0x003E8000

def build_blocks(firmware, hex_base_addr):
    """
    Build flash blocks from address-mapped firmware buffer.
    Block size=0x4000, address step=0x2000 (interleaved pattern).
    Always starts from ECU_FLASH_BASE (offset 0 = 0x3E8000); ECU requires
    this as the mandatory first block address.
    """
    ADDR_STEP = 0x2000
    MAX_BLOCK = 0x4000

    # Always start from ECU_FLASH_BASE (offset 0) — ECU hard-requires the
    # first 04 INIT to be at 0x3E8000 regardless of hex start address.
    last_nonff  = max((i for i, b in enumerate(firmware) if b != 0xFF), default=0)
    data_end    = last_nonff + 1

    offsets = []
    off = 0
    while True:
        offsets.append(off)
        if off + MAX_BLOCK >= data_end:
            break
        off += ADDR_STEP

    total     = len(offsets)
    # IDs count down naturally: first block = total, last block = 1
    block_ids = list(range(total, 0, -1))

    blocks = []
    for b_id, off in zip(block_ids, offsets):
        size  = min(MAX_BLOCK, len(firmware) - off)
        chunk = firmware[off:off + size]
        blocks.append({"addr": ECU_FLASH_BASE + off, "size": size,
                        "data": chunk, "block_id": b_id})
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
    def __init__(self, interface, channel, bitrate, hex_path, log_q, progress_q):
        self.interface  = interface
        self.channel    = channel
        self.bitrate    = bitrate
        self.hex_path   = hex_path
        self.log_q      = log_q      # queue for log messages (str)
        self.progress_q = progress_q # queue for progress (0.0–1.0)
        self.bus        = None
        self.abort      = False

    def log(self, msg):
        self.log_q.put(msg)

    def progress(self, val):
        self.progress_q.put(max(0.0, min(1.0, val)))

    def send_and_wait(self, data, timeout=ACK_TIMEOUT):
        assert verify_frame(data)
        msg = can.Message(arbitration_id=TOOL_ID, data=data, is_extended_id=True)
        self.bus.send(msg)
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.abort:
                raise RuntimeError("Aborted by user")
            rx = self.bus.recv(timeout=min(0.05, deadline - time.monotonic()))
            if rx and rx.arbitration_id == ECU_ID and bytes(rx.data) == data:
                return
        raise RuntimeError(f"No ACK for {data.hex().upper()}")

    def run(self):
        try:
            # ── Parse hex ────────────────────────────────────────────────────
            self.log("Loading hex file...")
            firmware, crc_bytes, crc_addr, base_addr = load_hex(self.hex_path)
            crc_int = int.from_bytes(crc_bytes, "big")
            self.log(f"  Firmware : {len(firmware):,} bytes")
            self.log(f"  Base addr: 0x{base_addr:08X}")
            self.log(f"  CRC      : 0x{crc_int:08X}")
            self.log(f"  CRC addr : 0x{crc_addr:08X}")

            blocks = build_blocks(firmware, base_addr)
            self.log(f"  Blocks   : {len(blocks)}")
            for b in blocks:
                self.log(f"    0x{b['addr']:08X}  {b['size']:5d} B  id=0x{b['block_id']:02X}")

            total_frames = sum(
                -(-b["size"] // PAYLOAD_BYTES) for b in blocks
            )

            # ── Open CAN ─────────────────────────────────────────────────────
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

            # ── Phase 1: Keepalive ────────────────────────────────────────────
            self.log("\n[1/5] Keepalive — waking ECU...")
            hb_msg = can.Message(arbitration_id=TOOL_ID, data=HEARTBEAT, is_extended_id=True)
            for i in range(HEARTBEAT_COUNT):
                if self.abort:
                    raise RuntimeError("Aborted")
                self.bus.send(hb_msg)
                time.sleep(HEARTBEAT_INTERVAL)
                self.progress(0.01 * i / HEARTBEAT_COUNT)

            deadline = time.monotonic() + ECU_WAKEUP_TIMEOUT
            while time.monotonic() < deadline:
                if self.abort:
                    raise RuntimeError("Aborted")
                rx = self.bus.recv(timeout=0.2)
                if rx and rx.arbitration_id == ECU_ID:
                    self.log(f"  ECU responded ✓  ({bytes(rx.data).hex().upper()})")
                    break
            else:
                raise RuntimeError("ECU did not respond to keepalive")

            # ── Phase 2: Flash blocks ─────────────────────────────────────────
            self.log(f"\n[2/5] Flashing {len(blocks)} blocks...")
            frames_done = 0

            for blk_idx, block in enumerate(blocks):
                if self.abort:
                    raise RuntimeError("Aborted")
                self.log(f"  Block {blk_idx+1}/{len(blocks)}  "
                         f"0x{block['addr']:08X}  {block['size']} B  "
                         f"id=0x{block['block_id']:02X}")

                # 04 init
                init_pl = addr_to_04_payload(block["addr"], block["size"])
                self.send_and_wait(make_frame(0x04, init_pl), timeout=ERASE_TIMEOUT)
                self.log(f"    Erase ACK ✓")

                # data frames
                toggle  = 0x01
                data    = block["data"]
                n       = -(-block["size"] // PAYLOAD_BYTES)
                offset  = 0
                chunk   = b""

                for fi in range(n):
                    if self.abort:
                        raise RuntimeError("Aborted")
                    chunk = data[offset:offset + PAYLOAD_BYTES]
                    # Pad only if firmware doesn't divide evenly (last frame),
                    # using 0xFF (= erased flash value). Do NOT force FF FF —
                    # those two bytes are real firmware data in every block.
                    if len(chunk) < PAYLOAD_BYTES:
                        chunk = chunk.ljust(PAYLOAD_BYTES, b'\xFF')
                    is_last = (fi == n - 1)
                    t = LAST_FRAME_TIMEOUT if is_last else ACK_TIMEOUT
                    self.send_and_wait(make_frame(toggle, chunk), timeout=t)
                    toggle = 0x02 if toggle == 0x01 else 0x01
                    offset += PAYLOAD_BYTES
                    frames_done += 1
                    self.progress(0.05 + 0.85 * frames_done / total_frames)

                # end-of-block
                eob_pl = bytes([0x00, block["block_id"]]) + bytes(chunk[2:6])
                self.send_and_wait(make_frame(0x00, eob_pl))
                self.log(f"    Block done ✓")

            # ── Phase 3: Program ──────────────────────────────────────────────
            self.log("\n[3/5] Program command (writing CRC to NVM)...")
            prog_pl = addr_to_04_payload(crc_addr, 4)
            self.send_and_wait(make_frame(0x04, prog_pl), timeout=PROG_TIMEOUT)
            self.log("  Program ACK ✓")
            self.progress(0.93)

            # ── Phase 4: Verify ───────────────────────────────────────────────
            self.log("\n[4/5] Verify...")
            crc_pl = bytes([0x00]) + crc_bytes[1:4] + bytes([0xFF, 0xFF])
            self.send_and_wait(make_frame(0x01, crc_pl))
            self.log("  Verify ACK ✓")
            self.progress(0.96)

            # ── Phase 5: Close ────────────────────────────────────────────────
            self.log("\n[5/5] Close session...")
            self.send_and_wait(make_frame(0x03, crc_pl), timeout=0.5)
            self.log("  Close ACK ✓")
            self.progress(0.99)

            # Broadcast
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
            self.progress(-1)  # signal failure
        finally:
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
    """
    Probe every PCAN_USBBUS1..8 channel at 500k to find which ones are
    physically present.  Returns a list of working channel names.
    Works on Windows (Peak driver) and Linux (SocketCAN peak_usb).
    """
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
        self.title("Airpump ECU Flash Tool")
        self.resizable(False, False)
        self.configure(bg="#1e1e2e")

        self.worker    = None
        self.log_q     = queue.Queue()
        self.prog_q    = queue.Queue()
        self._build_ui()
        self._poll()

    # ── UI build ──────────────────────────────────────────────────────────────

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

        # ── Hex file ──────────────────────────────────────────────────────────
        fg = ttk.LabelFrame(root, text=" Firmware File ", padding=10)
        fg.pack(fill="x", **PAD)

        self.hex_var = tk.StringVar()
        ttk.Entry(fg, textvariable=self.hex_var, width=52,
                  font=("Segoe UI", 10)).pack(side="left", padx=(0, 8))
        ttk.Button(fg, text="Browse…", command=self._browse).pack(side="left")

        # ── CAN settings ──────────────────────────────────────────────────────
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

        # ── Flash button + progress ───────────────────────────────────────────
        bg = ttk.Frame(root)
        bg.pack(fill="x", **CPAD)

        self.flash_btn = ttk.Button(bg, text="⚡  Flash ECU", style="Flash.TButton",
                                    command=self._start_flash, width=18)
        self.flash_btn.pack(side="left")

        self.abort_btn = ttk.Button(bg, text="Stop", command=self._abort,
                                    state="disabled", width=8)
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

        # ── Log console ───────────────────────────────────────────────────────
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

        # colour tags
        self.console.tag_config("ok",    foreground="#a6e3a1")
        self.console.tag_config("err",   foreground="#f38ba8")
        self.console.tag_config("info",  foreground="#89dceb")
        self.console.tag_config("dim",   foreground="#6c7086")

        clr = ttk.Button(root, text="Clear log", command=self._clear_log)
        clr.pack(anchor="e", padx=12, pady=(0, 4))

    # ── Helpers ───────────────────────────────────────────────────────────────

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
        # only show Detect button for PCAN
        if iface == "pcan":
            self.detect_btn.pack(side="left", padx=(0, 18))
        else:
            self.detect_btn.pack_forget()

    def _detect_channels(self):
        """Probe PCAN USB channels and populate the dropdown."""
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

    # ── Flash start/stop ──────────────────────────────────────────────────────

    def _start_flash(self):
        path = self.hex_var.get().strip()
        if not path:
            self._log("❌  ERROR: No hex file selected")
            return

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
        )
        threading.Thread(target=self.worker.run, daemon=True).start()

    def _abort(self):
        if self.worker:
            self.worker.abort = True
        self.status_lbl.configure(text="Aborting…", foreground="#f38ba8")

    # ── Poll queues ───────────────────────────────────────────────────────────

    def _poll(self):
        # drain log queue
        while not self.log_q.empty():
            self._log(self.log_q.get_nowait())

        # drain progress queue
        while not self.prog_q.empty():
            val = self.prog_q.get_nowait()
            if val < 0:  # failure signal
                self.prog_bar.configure(style="red.Horizontal.TProgressbar")
                self.prog_var.set(100)
                self.status_lbl.configure(text="Failed", foreground="#f38ba8")
                self._set_running(False)
            else:
                self.prog_var.set(val * 100)
                if val >= 1.0:
                    self.status_lbl.configure(text="Done ✓", foreground="#a6e3a1")
                    self._set_running(False)

        self.after(80, self._poll)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = App()
    app.mainloop()
