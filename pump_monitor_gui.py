#!/usr/bin/env python3
"""
pump_monitor_gui.py  —  Live CAN monitor for JSW Air Pump / Oil Pump
Replicates the OEM candebug.exe monitor using python-can / PCANBasic.

CAN IDs (extended, 29-bit):
  Tool → Pump : 0x4185  (command)
  Pump → Tool : 0x4181 – 0x4184, 0x5000, 0x5002, 0x5004, 0x5007, 0x5010, 0x5011
Each frame = 4 × uint16 big-endian values.
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
import struct
import queue

from flashing_logic import CANBusWrapper

# ── CAN ID → starting channel index ─────────────────────────────────────────
MONITOR_IDS = {
    0x4181: 0,
    0x4182: 4,
    0x4183: 8,
    0x4184: 12,
    0x5000: 16,
    0x5002: 20,
    0x5004: 24,
    0x5007: 28,
    0x5010: 32,
    0x5011: 36,
}

# ── Oil Pump channel definitions ─────────────────────────────────────────────
OIL_CHANNELS = {
    0:  ("Bus Voltage",       "V",   0.1),
    1:  ("Output Voltage",    "V",   0.1),
    2:  ("Output Current",    "A",   0.1),
    4:  ("Set Frequency",     "Hz",  0.1),
    5:  ("Output Frequency",  "Hz",  0.1),
    6:  ("RPM",               "rpm", 1.0),
    8:  ("Controller Temp",   "°C",  1.0),
    9:  ("Motor Temp",        "°C",  1.0),
    10: ("Run Enable",        "",    1.0),
    11: ("Fault Code",        "",    1.0),
    12: ("CAN Enable",        "",    1.0),
    13: ("Hardwire Enable",   "",    1.0),
    32: ("Stator Resistance", "",    1.0),
    33: ("D-Axis Inductance", "",    1.0),
    34: ("Q-Axis Inductance", "",    1.0),
    35: ("Back-EMF",          "",    1.0),
    36: ("D Kp",              "",    1.0),
    37: ("D Ki",              "",    1.0),
    38: ("Q Kp",              "",    1.0),
    39: ("Q Ki",              "",    1.0),
}

# ── Air Pump channel definitions ─────────────────────────────────────────────
AIR_CHANNELS = {
    0:  ("Status",            "",    1.0),
    4:  ("Set Frequency",     "Hz",  0.1),
    5:  ("Output Frequency",  "Hz",  0.1),
    6:  ("RPM",               "rpm", 1.0),
    8:  ("Controller Temp",   "°C",  1.0),
    9:  ("Motor Temp",        "°C",  1.0),
    10: ("Run Enable",        "",    1.0),
    11: ("Fault Code",        "",    1.0),
    12: ("CAN Enable",        "",    1.0),
    13: ("Hardwire Enable",   "",    1.0),
}

PUMP_CHANNELS = {
    "JSW Oil Pump": OIL_CHANNELS,
    "JSW Air Pump": AIR_CHANNELS,
}

CAN_INTERFACE_MAP = {
    "Peak":   {"interface": "peak",   "channel": 0, "bitrate": 250000},
    "Vector": {"interface": "vector", "channel": 0, "bitrate": 250000},
    "Kvaser": {"interface": "kvaser", "channel": 0, "bitrate": 250000},
}

BG      = "#F5F7FA"
BG2     = "#FFFFFF"
DARK    = "#1E2A3A"
BLUE    = "#154385"
GREEN   = "#27AE60"
RED     = "#E74C3C"
GREY    = "#6B7280"
BORDER  = "#E5E7EB"
TEXT    = "#111827"
YELLOW  = "#D97706"


class PumpMonitorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("JSW Pump Live Monitor")
        self.geometry("860x680")
        self.resizable(False, False)
        self.configure(bg=BG)

        self._bus    = None
        self._thread = None
        self._stop   = threading.Event()
        self._q      = queue.Queue()
        self._channels = {}   # channel_index → raw uint16
        self._last_seen = {}  # can_id → timestamp
        self._rx_count  = 0
        self._running   = False

        self._build_ui()
        self._poll()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=BLUE, height=56)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="JSW Pump Live Monitor",
                 font=("Segoe UI", 15, "bold"),
                 fg="white", bg=BLUE).pack(side="left", padx=20, pady=12)
        self._dot = tk.Label(hdr, text="●", font=("Segoe UI", 18),
                             fg="#93C5FD", bg=BLUE)
        self._dot.pack(side="right", padx=20)

        # Controls row
        ctrl = tk.Frame(self, bg=BG2, highlightbackground=BORDER, highlightthickness=1)
        ctrl.pack(fill="x", padx=14, pady=(10, 4))
        inner = tk.Frame(ctrl, bg=BG2)
        inner.pack(fill="x", padx=12, pady=8)

        tk.Label(inner, text="Pump", font=("Segoe UI", 10),
                 fg=GREY, bg=BG2).pack(side="left")
        self._pump_var = tk.StringVar(value="JSW Oil Pump")
        ttk.Combobox(inner, textvariable=self._pump_var,
                     values=list(PUMP_CHANNELS.keys()),
                     state="readonly", width=16,
                     font=("Segoe UI", 10)).pack(side="left", padx=(4, 20))

        tk.Label(inner, text="Hardware", font=("Segoe UI", 10),
                 fg=GREY, bg=BG2).pack(side="left")
        self._iface_var = tk.StringVar(value="Peak")
        ttk.Combobox(inner, textvariable=self._iface_var,
                     values=list(CAN_INTERFACE_MAP.keys()),
                     state="readonly", width=10,
                     font=("Segoe UI", 10)).pack(side="left", padx=(4, 20))

        tk.Label(inner, text="Bitrate", font=("Segoe UI", 10),
                 fg=GREY, bg=BG2).pack(side="left")
        self._baud_var = tk.StringVar(value="250000")
        ttk.Combobox(inner, textvariable=self._baud_var,
                     values=["250000", "500000"],
                     state="readonly", width=10,
                     font=("Segoe UI", 10)).pack(side="left", padx=(4, 20))

        self._start_btn = tk.Button(inner, text="▶  Start",
                                    font=("Segoe UI", 10, "bold"),
                                    bg=GREEN, fg="white",
                                    relief="flat", cursor="hand2", padx=14,
                                    command=self._start)
        self._start_btn.pack(side="left", padx=(0, 6))

        self._stop_btn = tk.Button(inner, text="■  Stop",
                                   font=("Segoe UI", 10, "bold"),
                                   bg=GREY, fg="white",
                                   relief="flat", cursor="hand2", padx=14,
                                   state="disabled",
                                   command=self._stop_monitor)
        self._stop_btn.pack(side="left")

        self._rx_var = tk.StringVar(value="Frames: 0")
        tk.Label(inner, textvariable=self._rx_var,
                 font=("Segoe UI", 10), fg=GREY, bg=BG2).pack(side="right")

        # Active CAN IDs row
        tk.Label(self, text="Active CAN IDs", font=("Segoe UI", 9, "bold"),
                 fg=GREY, bg=BG).pack(anchor="w", padx=14, pady=(4, 2))
        id_card = tk.Frame(self, bg=BG2, highlightbackground=BORDER, highlightthickness=1)
        id_card.pack(fill="x", padx=14, pady=(0, 6))
        id_inner = tk.Frame(id_card, bg=BG2)
        id_inner.pack(fill="x", padx=10, pady=6)
        self._id_labels = {}
        for can_id in sorted(MONITOR_IDS.keys()):
            f = tk.Frame(id_inner, bg=BG2)
            f.pack(side="left", padx=6)
            lbl = tk.Label(f, text=f"0x{can_id:04X}",
                           font=("Consolas", 9, "bold"),
                           bg="#F3F4F6", fg=GREY,
                           relief="flat", padx=6, pady=2)
            lbl.pack()
            self._id_labels[can_id] = lbl

        # Data table
        tk.Label(self, text="Live Data", font=("Segoe UI", 9, "bold"),
                 fg=GREY, bg=BG).pack(anchor="w", padx=14, pady=(2, 2))

        tbl_frame = tk.Frame(self, bg=BG2,
                             highlightbackground=BORDER, highlightthickness=1)
        tbl_frame.pack(fill="both", expand=True, padx=14, pady=(0, 6))

        cols = ("Parameter", "Value", "Unit", "Raw")
        self._tree = ttk.Treeview(tbl_frame, columns=cols, show="headings",
                                  height=16)
        style = ttk.Style()
        style.configure("Treeview", font=("Segoe UI", 11), rowheight=26)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

        widths = {"Parameter": 280, "Value": 120, "Unit": 80, "Raw": 80}
        for c in cols:
            self._tree.heading(c, text=c)
            self._tree.column(c, width=widths[c], anchor="w" if c == "Parameter" else "center")

        self._tree.tag_configure("ok",    background=BG2)
        self._tree.tag_configure("fault", background="#FEF2F2", foreground=RED)
        self._tree.tag_configure("warn",  background="#FFFBEB", foreground=YELLOW)

        sb = ttk.Scrollbar(tbl_frame, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=sb.set)
        self._tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self._row_ids = {}   # channel_idx → treeview iid
        self._build_table_rows()

        # Status bar
        self._status_var = tk.StringVar(value="Status: Idle — select pump and click Start")
        tk.Label(self, textvariable=self._status_var,
                 font=("Segoe UI", 10), bg=BLUE, fg="white",
                 anchor="w", padx=12).pack(fill="x", side="bottom")

    def _build_table_rows(self):
        for item in self._tree.get_children():
            self._tree.delete(item)
        self._row_ids.clear()
        ch_defs = PUMP_CHANNELS[self._pump_var.get()]
        for ch_idx in sorted(ch_defs.keys()):
            name, unit, scale = ch_defs[ch_idx]
            iid = self._tree.insert("", "end", values=(name, "—", unit, "—"),
                                    tags=("ok",))
            self._row_ids[ch_idx] = iid

    # ── Monitor thread ────────────────────────────────────────────────────────

    def _start(self):
        self._build_table_rows()
        self._channels.clear()
        self._last_seen.clear()
        self._rx_count = 0
        self._rx_var.set("Frames: 0")

        cfg = CAN_INTERFACE_MAP[self._iface_var.get()]
        self._stop.clear()
        self._running = True

        self._start_btn.config(state="disabled")
        self._stop_btn.config(state="normal")
        self._dot.config(fg="#FCD34D")
        self._status_var.set(f"Connecting {self._iface_var.get()} @ {self._baud_var.get()} bps...")

        self._thread = threading.Thread(
            target=self._monitor_thread,
            args=(cfg["interface"], cfg["channel"], int(self._baud_var.get())),
            daemon=True)
        self._thread.start()

    def _stop_monitor(self):
        self._stop.set()
        self._running = False
        self._stop_btn.config(state="disabled")
        self._dot.config(fg="#93C5FD")
        self._status_var.set("Status: Stopped")

    def _monitor_thread(self, interface, channel, bitrate):
        try:
            bus = CANBusWrapper(interface, channel, bitrate)
            self._bus = bus
        except Exception as e:
            self._q.put(("err", f"CAN open failed: {e}"))
            return

        self._q.put(("connected", None))
        pump = self._pump_var.get()
        ch_defs = PUMP_CHANNELS[pump]

        try:
            while not self._stop.is_set():
                rx = bus.recv(timeout=0.05)
                if not rx:
                    continue
                arb_id = rx["arbitration_id"]
                data   = bytes(rx["data"])
                now    = time.time()

                if arb_id not in MONITOR_IDS:
                    continue
                if len(data) < 8:
                    continue

                base_ch = MONITOR_IDS[arb_id]
                values  = struct.unpack(">HHHH", data[:8])
                self._last_seen[arb_id] = now
                self._rx_count += 1

                updates = []
                for i, raw in enumerate(values):
                    ch_idx = base_ch + i
                    self._channels[ch_idx] = raw
                    if ch_idx in ch_defs:
                        name, unit, scale = ch_defs[ch_idx]
                        scaled = raw * scale
                        updates.append((ch_idx, name, scaled, unit, raw))

                if updates:
                    self._q.put(("data", updates))
                self._q.put(("rx_count", self._rx_count))
                self._q.put(("ids", dict(self._last_seen)))

        except Exception as e:
            self._q.put(("err", str(e)))
        finally:
            try:
                bus.shutdown()
            except Exception:
                pass
            self._q.put(("disconnected", None))

    # ── GUI poll ──────────────────────────────────────────────────────────────

    def _poll(self):
        try:
            while True:
                msg = self._q.get_nowait()
                kind, payload = msg

                if kind == "connected":
                    self._dot.config(fg=GREEN)
                    self._status_var.set(
                        f"Monitoring {self._pump_var.get()} — "
                        f"{self._iface_var.get()} @ {self._baud_var.get()} bps")
                    self._start_btn.config(state="disabled")
                    self._stop_btn.config(state="normal")

                elif kind == "disconnected":
                    self._dot.config(fg="#93C5FD")
                    self._start_btn.config(state="normal")
                    self._stop_btn.config(state="disabled")
                    self._running = False

                elif kind == "data":
                    for ch_idx, name, scaled, unit, raw in payload:
                        iid = self._row_ids.get(ch_idx)
                        if iid:
                            if unit in ("", ) and name in ("Fault Code",):
                                tag = "fault" if scaled != 0 else "ok"
                            elif name in ("Run Enable", "CAN Enable", "Hardwire Enable"):
                                tag = "ok" if scaled == 1 else "warn"
                            else:
                                tag = "ok"
                            fmt = f"{scaled:.1f}" if scaled != int(scaled) else f"{int(scaled)}"
                            self._tree.item(iid, values=(name, fmt, unit, f"0x{raw:04X}"),
                                            tags=(tag,))

                elif kind == "rx_count":
                    self._rx_var.set(f"Frames: {payload}")

                elif kind == "ids":
                    now = time.time()
                    for can_id, lbl in self._id_labels.items():
                        if can_id in payload and (now - payload[can_id]) < 1.0:
                            lbl.config(bg="#D1FAE5", fg="#065F46")
                        else:
                            lbl.config(bg="#F3F4F6", fg=GREY)

                elif kind == "err":
                    self._status_var.set(f"❌ {payload}")
                    self._dot.config(fg=RED)
                    self._start_btn.config(state="normal")
                    self._stop_btn.config(state="disabled")

        except queue.Empty:
            pass
        self.after(80, self._poll)


if __name__ == "__main__":
    app = PumpMonitorApp()
    app.mainloop()
