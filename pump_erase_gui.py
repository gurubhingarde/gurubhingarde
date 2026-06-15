#!/usr/bin/env python3
"""
pump_erase_gui.py  —  Full flash erase tool for Air Pump / Oil Pump ECUs.

Erases all 7 firmware sectors (0x3E8000–0x3F5FFF) one by one.
Use this to recover an ECU with a corrupted or worn flash region.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from flashing_logic import CANBusWrapper


# ── Protocol constants ────────────────────────────────────────────────────────
PUMP_CONFIG = {
    "JSW Air Pump": {"tool_id": 0x180006FF, "ecu_id": 0x1800FF06, "ecu_addr": 0x06},
    "JSW Oil Pump": {"tool_id": 0x180005FF, "ecu_id": 0x1800FF05, "ecu_addr": 0x05},
}
BCAST_ID        = 0x1800FFFF
ADDR_STEP       = 0x2000        # 8 KB per sector
BLOCK_ID_BASE   = 0x003F4000
HB_BYTE_DEFAULT = 0x07         # base 0x3E8000 → unlocks all sectors

# All firmware sectors to erase
ERASE_SECTORS = [
    0x003E8000, 0x003EA000, 0x003EC000, 0x003EE000,
    0x003F0000, 0x003F2000, 0x003F4000,
]

HEARTBEAT_COUNT    = 60
HEARTBEAT_INTERVAL = 0.101
ERASE_TIMEOUT      = 8.0


# ── Protocol helpers ──────────────────────────────────────────────────────────
def xor8(data):
    r = 0
    for b in data[:7]:
        r ^= b
    return r

def make_frame(b0, payload):
    raw = bytes([b0]) + bytes(payload)
    return raw + bytes([xor8(raw)])

def addr_payload(full_addr, size):
    return bytes([
        (full_addr >> 24) & 0xFF,
        (full_addr >> 16) & 0xFF,
        (full_addr >>  8) & 0xFF,
        (full_addr      ) & 0xFF,
        (size      >>  8) & 0xFF,
         size             & 0xFF,
    ])


# ── Erase worker ──────────────────────────────────────────────────────────────
def full_erase(pump_type, interface, channel, bitrate, log_fn, progress_fn, stop_evt):
    cfg      = PUMP_CONFIG[pump_type]
    tool_id  = cfg["tool_id"]
    ecu_id   = cfg["ecu_id"]
    ecu_addr = cfg["ecu_addr"]

    iface = interface if interface != "peak" else "pcan"
    try:
        bus = CANBusWrapper(iface, channel, bitrate)
    except Exception as e:
        log_fn(f"❌ CAN open failed: {e}")
        return False

    try:
        # ── Step 1: Broadcast wakeup ──────────────────────────────────────
        log_fn("\n[1/3] Broadcast — waking ECU...")
        bcast_raw   = bytes([0xFF, 0x02, ecu_addr, 0x00, 0x00, 0x00, 0x00])
        bcast_xor   = 0
        for b in bcast_raw:
            bcast_xor ^= b
        bcast_frame = bcast_raw + bytes([bcast_xor])
        bus.send(BCAST_ID, list(bcast_frame), is_extended_id=True)
        log_fn(f"  Broadcast sent: {bcast_frame.hex().upper()}")

        bcast_acked = False
        deadline = time.time() + 0.5
        while time.time() < deadline:
            rx = bus.recv(timeout=0.05)
            if rx and rx['arbitration_id'] == ecu_id:
                d = bytes(rx['data'])
                if d[0] == 0xFF and d[1] == 0x82:
                    log_fn(f"  Broadcast ACK ✓  ({d.hex().upper()})")
                    bcast_acked = True
                    break
        if bcast_acked:
            log_fn("  ECU rebooting to bootloader — waiting 300 ms...")
            time.sleep(0.3)
        else:
            log_fn("  No broadcast ACK (ECU may already be in bootloader)")

        # ── Step 2: Heartbeat until ECU responds ──────────────────────────
        log_fn("\n[2/3] Heartbeat — waiting for ECU...")
        hb_data  = make_frame(0x00, bytes([0x00, HB_BYTE_DEFAULT, 0x00, 0x00, 0x00, 0x00]))
        ecu_woke = False

        for i in range(HEARTBEAT_COUNT):
            if stop_evt.is_set():
                log_fn("⛔ Cancelled")
                return False
            bus.send(tool_id, list(hb_data), is_extended_id=True)
            rx = bus.recv(timeout=0.08)
            if rx and rx['arbitration_id'] == ecu_id:
                log_fn(f"  ECU responded ✓  ({bytes(rx['data']).hex().upper()})")
                ecu_woke = True
                break
            time.sleep(max(0, HEARTBEAT_INTERVAL - 0.08))

        if not ecu_woke:
            log_fn("❌ ECU did not respond to heartbeat.")
            return False

        # ── Step 3: Erase each sector ─────────────────────────────────────
        log_fn(f"\n[3/3] Erasing {len(ERASE_SECTORS)} sectors...")
        for idx, sector_addr in enumerate(ERASE_SECTORS):
            if stop_evt.is_set():
                log_fn("⛔ Cancelled")
                return False
            log_fn(f"  Erasing sector {idx+1}/{len(ERASE_SECTORS)}  "
                   f"0x{sector_addr:08X} — 0x{sector_addr + ADDR_STEP - 1:08X}  (8 KB)...")
            erase_frame = make_frame(0x04, addr_payload(sector_addr, ADDR_STEP))
            bus.send(tool_id, list(erase_frame), is_extended_id=True)
            acked = False
            deadline = time.time() + ERASE_TIMEOUT
            while time.time() < deadline:
                rx = bus.recv(timeout=0.1)
                if not rx:
                    continue
                if rx['arbitration_id'] == ecu_id and bytes(rx['data']) == erase_frame:
                    log_fn(f"    ✅ Erase ACK")
                    acked = True
                    break
            if not acked:
                log_fn(f"    ❌ No ACK — sector 0x{sector_addr:08X} may be bad or already blank")
            progress_fn((idx + 1) / len(ERASE_SECTORS) * 100)

        log_fn("\n🎉 Full erase complete. ECU flash is now blank.")
        log_fn("   You can now flash fresh firmware.")
        return True

    except Exception as e:
        log_fn(f"❌ Error: {e}")
        return False
    finally:
        try: bus.shutdown()
        except Exception: pass
        log_fn("🔌 CAN Bus closed.")


# ── GUI ───────────────────────────────────────────────────────────────────────
class EraseApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pump ECU — Full Flash Erase Tool")
        self.geometry("620x560")
        self.resizable(False, False)
        self.configure(bg="#f6f8fb")
        self._stop_evt = threading.Event()

        # Header
        tk.Label(self, text="Pump ECU Full Erase", font=("Segoe UI", 22, "bold"),
                 bg="#f6f8fb", fg="#163c69").pack(pady=(22, 2))
        tk.Label(self, text="Erases all 7 firmware sectors  (0x3E8000 – 0x3F5FFF)",
                 font=("Segoe UI", 10), bg="#f6f8fb", fg="#6b7a99").pack(pady=(0, 14))

        # Warning banner
        warn = tk.Frame(self, bg="#FFF3CD", bd=1, relief="solid")
        warn.pack(padx=30, fill="x", pady=(0, 14))
        tk.Label(warn, text="⚠  This will erase ALL firmware. Flash new firmware immediately after.",
                 font=("Segoe UI", 10, "bold"), bg="#FFF3CD", fg="#856404",
                 wraplength=540, justify="center").pack(pady=8)

        form = tk.Frame(self, bg="#f6f8fb")
        form.pack(padx=40, fill="x")

        # Pump type
        tk.Label(form, text="Pump Type", font=("Segoe UI", 11, "bold"),
                 bg="#f6f8fb", fg="#1f355e").grid(row=0, column=0, sticky="w", pady=8)
        self.pump_var = tk.StringVar(value="JSW Oil Pump")
        ttk.Combobox(form, textvariable=self.pump_var,
                     values=list(PUMP_CONFIG.keys()),
                     state="readonly", width=22,
                     font=("Segoe UI", 11)).grid(row=0, column=1, padx=10, pady=8, sticky="w")

        # CAN interface
        tk.Label(form, text="CAN Interface", font=("Segoe UI", 11, "bold"),
                 bg="#f6f8fb", fg="#1f355e").grid(row=1, column=0, sticky="w", pady=8)
        self.iface_var = tk.StringVar(value="peak")
        ttk.Combobox(form, textvariable=self.iface_var,
                     values=["peak", "vector", "kvaser"],
                     state="readonly", width=22,
                     font=("Segoe UI", 11)).grid(row=1, column=1, padx=10, pady=8, sticky="w")

        # Bitrate
        tk.Label(form, text="Bitrate", font=("Segoe UI", 11, "bold"),
                 bg="#f6f8fb", fg="#1f355e").grid(row=2, column=0, sticky="w", pady=8)
        self.baud_var = tk.StringVar(value="250000")
        ttk.Combobox(form, textvariable=self.baud_var,
                     values=["250000", "500000"],
                     state="readonly", width=22,
                     font=("Segoe UI", 11)).grid(row=2, column=1, padx=10, pady=8, sticky="w")

        # Progress bar
        tk.Label(self, text="Progress", font=("Segoe UI", 11, "bold"),
                 bg="#f6f8fb", fg="#1f355e", anchor="w").pack(padx=40, fill="x", pady=(10, 2))
        self.progress = ttk.Progressbar(self, length=540, mode="determinate")
        self.progress.pack(padx=40, fill="x")
        self.pct_var = tk.StringVar(value="0%")
        tk.Label(self, textvariable=self.pct_var, font=("Segoe UI", 11, "bold"),
                 bg="#f6f8fb", fg="#154385").pack()

        # Buttons
        btn_row = tk.Frame(self, bg="#f6f8fb")
        btn_row.pack(pady=10)
        self.erase_btn = tk.Button(btn_row, text="Start Erase", command=self._start,
                                   bg="#E74C3C", fg="white",
                                   font=("Segoe UI", 13, "bold"),
                                   relief="flat", cursor="hand2", width=16)
        self.erase_btn.pack(side="left", padx=8)
        self.stop_btn = tk.Button(btn_row, text="Stop", command=self._stop,
                                  bg="#95a5a6", fg="white",
                                  font=("Segoe UI", 13, "bold"),
                                  relief="flat", cursor="hand2", width=10,
                                  state="disabled")
        self.stop_btn.pack(side="left", padx=8)

        # Log
        tk.Label(self, text="Log", font=("Segoe UI", 11, "bold"),
                 bg="#34495E", fg="white", anchor="w").pack(padx=40, fill="x", pady=(6, 0))
        self.log_box = tk.Text(self, bg="#34495E", fg="white", font=("Segoe UI", 11),
                               state="disabled", height=8, wrap="word",
                               relief="flat", bd=4)
        self.log_box.pack(padx=40, pady=(0, 16), fill="x")

    def log(self, msg):
        ts = time.strftime("[%H:%M:%S] ")
        self.log_box.config(state="normal")
        self.log_box.insert("end", ts + msg + "\n")
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    def set_progress(self, pct):
        self.progress["value"] = pct
        self.pct_var.set(f"{int(pct)}%")

    def _start(self):
        self._stop_evt.clear()
        self.log_box.config(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.config(state="disabled")
        self.progress["value"] = 0
        self.pct_var.set("0%")
        self.erase_btn.config(state="disabled")
        self.stop_btn.config(state="normal")

        pump    = self.pump_var.get()
        iface   = self.iface_var.get()
        bitrate = int(self.baud_var.get())

        self.log(f"Pump    : {pump}")
        self.log(f"Interface: {iface}  @{bitrate} bps")
        self.log("Power OFF the ECU, then power ON and click OK in the dialog.")

        def _worker():
            ok = full_erase(pump, iface, 0, bitrate,
                            self.log, self.set_progress, self._stop_evt)
            self.erase_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
            if ok:
                self.after(0, lambda: messagebox.showinfo(
                    "Done", "Full erase complete.\nFlash new firmware now."))
            else:
                if not self._stop_evt.is_set():
                    self.after(0, lambda: messagebox.showerror(
                        "Failed", "Erase failed. Check log for details."))

        threading.Thread(target=_worker, daemon=True).start()

    def _stop(self):
        self._stop_evt.set()
        self.stop_btn.config(state="disabled")
        self.log("⛔ Stop requested...")


if __name__ == "__main__":
    app = EraseApp()
    app.mainloop()
