#!/usr/bin/env python3
"""
NexaBoot Tester — Next Generation Secure Bootloader Validation Tool
====================================================================
NexaBoot v2.2 | S32K144 | ISO 14229 UDS | ISO 15765-2 ISO-TP

Requirements:
    pip install python-can can-isotp pycryptodome
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading, struct, time, zlib, os, queue, sys, json, socket

# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════

APP_VERSION = "v2.2"
APP_NAME    = "NexaBoot Tester"

VEHICLE_MODELS = {
    "9M Bus":        0x0001,
    "12M City Bus":  0x0002,
    "12M Staff Bus": 0x0003,
    "4x2 TT":        0x0004,
    "6x4 TT":        0x0005,
}

# NRC descriptions — detailed for tester
NRC_INFO = {
    0x10: ("generalReject",                  "ECU rejected the request."),
    0x11: ("serviceNotSupported",            "This UDS service is not supported."),
    0x12: ("subFunctionNotSupported",        "Sub-function not supported. Check session type."),
    0x13: ("incorrectMessageLength",         "Message too short or too long. Check payload."),
    0x22: ("conditionsNotCorrect",           "Wrong sequence or wrong session. Check OTA state."),
    0x24: ("requestSequenceError",           "Service called out of order. Must follow: erase→download→transfer→exit."),
    0x31: ("requestOutOfRange",              "Model mismatch, version downgrade, or unknown DID/routine."),
    0x33: ("securityAccessDenied",           "Security not unlocked. Call 0x27 01/02 first."),
    0x35: ("invalidKey",                     "Wrong security access key. Check AES key."),
    0x36: ("exceededNumberOfAttempts",       "Too many wrong keys — ECU locked. Wait 10 seconds."),
    0x70: ("uploadDownloadNotAccepted",      "ECDSA signature verification failed. Wrong firmware or key."),
    0x72: ("generalProgrammingFailure",      "Decompress or flash write failed. Retry OTA."),
    0x73: ("wrongBlockSequenceCounter",      "Block sequence number wrong. Restart download."),
    0x78: ("requestPending",                 "ECU busy processing. Keep waiting — do not retry."),
    0x7E: ("subFunctionNotSupported", "Sub-function not supported in current session."),
    0x7F: ("serviceNotSupportedInSession",   "Service not allowed in current session."),
}

# DTC descriptions — all 10 NexaBoot DTCs
DTC_INFO = {
    0xC10001: ("FLASH_ERASE_FAIL",    "Flash erase failed. Hardware issue possible.",          "red"),
    0xC10002: ("FLASH_PROGRAM_FAIL",  "Flash write failed. Hardware issue possible.",           "red"),
    0xC10003: ("CRC_MISMATCH",        "App CRC mismatch — app corrupted or incomplete flash.", "red"),
    0xC10004: ("SA_LOCKOUT",          "Security access locked — 3 wrong keys entered.",        "orange"),
    0xC10005: ("META_WRITE_FAIL",     "Metadata write failed after OTA.",                      "red"),
    0xC10006: ("CRYPTO_FAIL",         "ECDSA or AES operation failed. Check firmware/key.",    "red"),
    0xC10007: ("DEV_MODE_USED",       "Developer bypass used — audit trail entry.",             "cyan"),
    0xC10008: ("OTA_INTERRUPTED",     "OTA was interrupted (power cut, abort or timeout).",    "orange"),
    0xC10009: ("INVALID_SEQUENCE",    "UDS services called out of order.",                     "orange"),
    0xC1000A: ("COMP_STORE_FAIL",     "Compressed store write failed during transfer.",        "red"),
}

# ══════════════════════════════════════════════════════════════════════════════
# THEME
# ══════════════════════════════════════════════════════════════════════════════

# Deep navy dark theme — NexaBoot signature colors
C_BG       = "#080C14"   # deepest background
C_BG2      = "#0E1520"   # card background
C_BG3      = "#141E30"   # input background
C_BG4      = "#1A2640"   # hover
C_BLUE     = "#0EA5E9"   # NexaBoot primary blue
C_BLUE2    = "#38BDF8"   # lighter blue
C_CYAN     = "#06B6D4"   # cyan accent
C_GREEN    = "#22C55E"   # success
C_GREEN2   = "#4ADE80"   # light green
C_RED      = "#EF4444"   # error
C_RED2     = "#F87171"   # light red
C_ORANGE   = "#F97316"   # warning
C_YELLOW   = "#EAB308"   # caution
C_FG       = "#E2E8F0"   # primary text
C_FG2      = "#64748B"   # secondary text
C_FG3      = "#334155"   # muted
C_BORDER   = "#1E3A5F"   # border
C_PURPLE   = "#A855F7"   # developer mode

FONT_MONO  = ("Consolas",  10)
FONT_MONO_S= ("Consolas",   9)
FONT_UI    = ("Segoe UI",  10)
FONT_UI_S  = ("Segoe UI",   9)
FONT_UI_B  = ("Segoe UI",  10, "bold")
FONT_HDR   = ("Segoe UI",  11, "bold")
FONT_TITLE = ("Segoe UI",  20, "bold")
FONT_LOGO  = ("Segoe UI",  28, "bold")

# ══════════════════════════════════════════════════════════════════════════════
# CRYPTO
# ══════════════════════════════════════════════════════════════════════════════

def xtea_derive_key(seed_bytes: bytes, aes_key: bytes) -> bytes:
    key = struct.unpack(">4I", aes_key)
    v0  = struct.unpack(">I", seed_bytes)[0]
    v1  = 0
    s   = 0
    DELTA = 0x9E3779B9
    for _ in range(8):
        v0 = (v0 + (((v1 << 4 ^ v1 >> 5) + v1) ^ (s + key[s & 3]))) & 0xFFFFFFFF
        s  = (s + DELTA) & 0xFFFFFFFF
        v1 = (v1 + (((v0 << 4 ^ v0 >> 5) + v0) ^ (s + key[(s >> 11) & 3]))) & 0xFFFFFFFF
    return struct.pack(">I", v0)

def aes_ctr_encrypt(data: bytes, key: bytes, nonce: bytes) -> bytes:
    from Crypto.Cipher import AES
    from Crypto.Util import Counter
    ctr = Counter.new(32, prefix=nonce, initial_value=0, little_endian=False)
    return AES.new(key, AES.MODE_CTR, counter=ctr).encrypt(data)

# ══════════════════════════════════════════════════════════════════════════════
# CAN / ISO-TP
# ══════════════════════════════════════════════════════════════════════════════

class CANBus:
    def __init__(self):
        self.bus  = None
        self.tp   = None
        self.lock = threading.Lock()
        self.log_q = None

    def connect(self, interface, channel, bitrate=250000, rx_id=0x7E8, tx_id=0x7E0):
        import can, isotp
        if interface == "pcan":
            self.bus = can.interface.Bus(interface="pcan", channel=channel,
                                         bitrate=bitrate, fd=False)
        else:
            self.bus = can.interface.Bus(interface=interface, channel=channel,
                                         bitrate=bitrate)
        addr = isotp.Address(isotp.AddressingMode.Normal_11bits,
                             rxid=rx_id, txid=tx_id)
        try:
            self.tp = isotp.CanStack(self.bus, address=addr)
            if hasattr(self.tp, 'set_sleep_time'):
                self.tp.set_sleep_time(0.001)
        except TypeError:
            self.tp = isotp.CanStack(self.bus, address=addr)

    def disconnect(self):
        try:
            if self.tp: self.tp = None
        except: pass
        try:
            if self.bus:
                self.bus.shutdown()
                self.bus = None
        except: pass

    def _put_log(self, msg, tag):
        if self.log_q:
            self.log_q.put((msg, tag))

    def request(self, data: bytes, timeout=10.0) -> bytes:
        with self.lock:
            self.tp.send(data)
            deadline = time.time() + 5.0
            while time.time() < deadline:
                self.tp.process()
                if hasattr(self.tp, 'transmitting'):
                    if not self.tp.transmitting(): break
                else:
                    time.sleep(0.05); break
                time.sleep(0.001)

            deadline    = time.time() + timeout
            stale_count = 0
            while time.time() < deadline:
                self.tp.process()
                if self.tp.available():
                    resp = bytes(self.tp.recv())
                    if len(resp) < 1: continue
                    if resp[0] == 0x7F and len(resp) >= 3 and resp[2] == 0x78:
                        self._put_log("[0x78] ECU busy — waiting...\n", "WARN")
                        deadline = min(time.time() + timeout, time.time() + 300.0)
                        continue
                    expected_sid = data[0] + 0x40
                    if resp[0] != expected_sid and resp[0] != 0x7F:
                        stale_count += 1
                        if stale_count <= 3: continue
                        raise RuntimeError(f"Unexpected response 0x{resp[0]:02X}")
                    if resp[0] == 0x7F:
                        nrc = resp[2] if len(resp) >= 3 else 0
                        sid = resp[1] if len(resp) >= 2 else 0
                        nrc_name, nrc_desc = NRC_INFO.get(nrc, ("unknown", "Unknown NRC"))
                        raise RuntimeError(
                            f"NRC 0x{nrc:02X} ({nrc_name})\n"
                            f"  SID: 0x{sid:02X} | {nrc_desc}")
                    return resp
                time.sleep(0.001)
            raise TimeoutError("Response timeout — ECU not responding")

# ══════════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ══════════════════════════════════════════════════════════════════════════════

class NexaBootTester(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"NexaBoot Tester  {APP_VERSION}")
        self.geometry("1280x860")
        self.minsize(1100, 750)
        self.configure(bg=C_BG)
        self.resizable(True, True)

        self.can        = CANBus()
        self.q          = queue.Queue()
        self.can.log_q  = self.q
        self.connected  = False
        self.aes_key    = None
        self.ota_abort  = False
        self.ota_thread = None

        self.model_var  = tk.StringVar(value="9M Bus")
        self.dev_mode   = tk.BooleanVar(value=False)
        self.iface_var  = tk.StringVar(value="pcan")
        self.chan_var    = tk.StringVar(value="PCAN_USBBUS1")
        self.brate_var  = tk.StringVar(value="250000")
        self.rxid_var   = tk.StringVar(value="0x7E8")
        self.txid_var   = tk.StringVar(value="0x7E0")
        self.key_var    = tk.StringVar(value="00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F")
        self.fw_path    = tk.StringVar()
        self.sw_ver_var = tk.StringVar(value="—")

        self.config_file = os.path.join(os.path.expanduser("~"), ".nexaboot_tester.json")

        self._build_ui()
        self._poll_queue()
        self._load_config()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ──────────────────────────────────────────────────────────────────────────
    # UI BUILD
    # ──────────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        self._setup_styles()
        self._build_titlebar()
        self._build_body()

    def _setup_styles(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("TNotebook",      background=C_BG,  borderwidth=0)
        s.configure("TNotebook.Tab",  background=C_BG3, foreground=C_FG2,
                    padding=[14, 7],  font=FONT_UI_B,   borderwidth=0)
        s.map("TNotebook.Tab",
              background=[("selected", C_BG2)],
              foreground=[("selected", C_BLUE)])
        s.configure("TFrame",         background=C_BG)
        s.configure("TPanedwindow",   background=C_BG)
        s.configure("OTA.Horizontal.TProgressbar",
                    troughcolor=C_BG3, background=C_BLUE, thickness=16)
        s.configure("OK.Horizontal.TProgressbar",
                    troughcolor=C_BG3, background=C_GREEN, thickness=16)
        s.configure("ERR.Horizontal.TProgressbar",
                    troughcolor=C_BG3, background=C_RED, thickness=16)
        s.configure("TCombobox",
                    fieldbackground=C_BG3, background=C_BG3,
                    foreground=C_FG, selectbackground=C_BG4,
                    arrowcolor=C_BLUE)
        s.map("TCombobox",
              fieldbackground=[("readonly", C_BG3)],
              selectbackground=[("readonly", C_BG3)],
              selectforeground=[("readonly", C_FG)])

    def _build_titlebar(self):
        bar = tk.Frame(self, bg=C_BG2, height=64)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)

        # Left — logo
        logo_frame = tk.Frame(bar, bg=C_BG2)
        logo_frame.pack(side=tk.LEFT, padx=16)

        # N hexagon icon
        canvas = tk.Canvas(logo_frame, width=42, height=42,
                           bg=C_BG2, highlightthickness=0)
        canvas.pack(side=tk.LEFT, pady=11)
        # Draw hexagon
        import math
        cx, cy, r = 21, 21, 18
        pts = []
        for i in range(6):
            angle = math.radians(60 * i - 30)
            pts += [cx + r * math.cos(angle), cy + r * math.sin(angle)]
        canvas.create_polygon(pts, fill=C_BLUE, outline=C_BLUE2, width=2)
        canvas.create_text(cx, cy, text="N", fill="white",
                          font=("Segoe UI", 14, "bold"))

        tk.Label(logo_frame, text="NexaBoot", font=("Segoe UI", 18, "bold"),
                 fg=C_FG, bg=C_BG2).pack(side=tk.LEFT, padx=(8, 0), pady=11)
        tk.Label(logo_frame, text=f"Tester  {APP_VERSION}",
                 font=("Segoe UI", 10), fg=C_FG2, bg=C_BG2).pack(
                 side=tk.LEFT, padx=(6, 0), pady=18)

        # Center — ECU info bar
        self.ecu_bar = tk.Frame(bar, bg=C_BG3, bd=0)
        self.ecu_bar.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=10)
        self.ecu_info_labels = {}
        for key, label in [("BL", "BL Ver"), ("SW", "SW Ver"), ("Model", "Model")]:
            f = tk.Frame(self.ecu_bar, bg=C_BG3)
            f.pack(side=tk.LEFT, padx=12, pady=4)
            tk.Label(f, text=label, font=FONT_UI_S, fg=C_FG2,
                     bg=C_BG3).pack()
            lbl = tk.Label(f, text="—", font=("Consolas", 9, "bold"),
                           fg=C_BLUE2, bg=C_BG3)
            lbl.pack()
            self.ecu_info_labels[key] = lbl

        # Right — status
        status_frame = tk.Frame(bar, bg=C_BG2)
        status_frame.pack(side=tk.RIGHT, padx=16)
        self.status_dot = tk.Label(status_frame, text="⬤", font=("Segoe UI", 14),
                                   fg=C_RED, bg=C_BG2)
        self.status_dot.pack(side=tk.LEFT, pady=16)
        self.status_lbl = tk.Label(status_frame, text="DISCONNECTED",
                                   font=("Consolas", 10, "bold"),
                                   fg=C_RED, bg=C_BG2)
        self.status_lbl.pack(side=tk.LEFT, padx=(4, 0), pady=16)

        # Separator line
        sep = tk.Frame(self, bg=C_BORDER, height=1)
        sep.pack(fill=tk.X)

    def _build_body(self):
        pane = tk.PanedWindow(self, orient=tk.HORIZONTAL,
                              bg=C_BG, sashwidth=4,
                              sashrelief=tk.FLAT, sashpad=2)
        pane.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        left  = tk.Frame(pane, bg=C_BG)
        right = tk.Frame(pane, bg=C_BG)
        pane.add(left,  minsize=300)
        pane.add(right, minsize=500)
        pane.paneconfig(left,  width=400)
        pane.paneconfig(right, width=880)

        self._build_left(left)
        self._build_right(right)

    # ── LEFT PANEL ────────────────────────────────────────────────────────────

    def _build_left(self, parent):
        scroll_frame = tk.Frame(parent, bg=C_BG)
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # ── CAN Connection ────────────────────────────────────────────────────
        self._section(scroll_frame, "CAN CONNECTION")

        card = self._card(scroll_frame)

        # FIX: create widgets with the row as parent (obtained from _field_row)
        row = self._field_row(card, "Interface")
        self._combo(row, self.iface_var,
                    ["pcan", "socketcan", "kvaser", "vector", "virtual"], 14).pack(
                    side=tk.LEFT, padx=4)

        row = self._field_row(card, "Channel")
        self._entry(row, self.chan_var, 18).pack(side=tk.LEFT, padx=4)

        row = self._field_row(card, "Baud Rate")
        self._combo(row, self.brate_var,
                    ["250000", "500000", "1000000"], 14).pack(side=tk.LEFT, padx=4)

        # RX/TX IDs
        idrow = tk.Frame(card, bg=C_BG2)
        idrow.pack(fill=tk.X, pady=3)
        tk.Label(idrow, text="RX ID", fg=C_FG2, bg=C_BG2,
                 font=FONT_UI_S, width=8, anchor=tk.W).pack(side=tk.LEFT, padx=6)
        self._entry(idrow, self.rxid_var, 9).pack(side=tk.LEFT)
        tk.Label(idrow, text="TX ID", fg=C_FG2, bg=C_BG2,
                 font=FONT_UI_S).pack(side=tk.LEFT, padx=(8, 4))
        self._entry(idrow, self.txid_var, 9).pack(side=tk.LEFT)

        btnrow = tk.Frame(card, bg=C_BG2)
        btnrow.pack(fill=tk.X, pady=(6, 4))
        self._btn(btnrow, "⬡  CONNECT",    self._connect,    C_BLUE, True).pack(side=tk.LEFT, padx=6)
        self._btn(btnrow, "⬡  DISCONNECT", self._disconnect, C_RED,  False).pack(side=tk.LEFT)

        # ── AES Key ───────────────────────────────────────────────────────────
        self._section(scroll_frame, "AES-128 KEY")
        card2 = self._card(scroll_frame)

        keyrow = tk.Frame(card2, bg=C_BG2)
        keyrow.pack(fill=tk.X, pady=4)
        self.key_entry = tk.Entry(keyrow, textvariable=self.key_var, width=34,
                                  bg=C_BG3, fg=C_YELLOW,
                                  insertbackground=C_BLUE,
                                  relief=tk.FLAT, font=FONT_MONO_S, show="*")
        self.key_entry.pack(side=tk.LEFT, padx=6)
        self.key_vis = False
        def _toggle():
            self.key_vis = not self.key_vis
            self.key_entry.config(show="" if self.key_vis else "*")
            btn_vis.config(text="Hide" if self.key_vis else "Show")
        btn_vis = tk.Button(keyrow, text="Show", command=_toggle,
                            bg=C_BG4, fg=C_FG2, relief=tk.FLAT,
                            font=FONT_UI_S, padx=6, cursor="hand2")
        btn_vis.pack(side=tk.LEFT, padx=2)

        kr2 = tk.Frame(card2, bg=C_BG2)
        kr2.pack(fill=tk.X, pady=(0, 4))
        self._btn(kr2, "Load .bin", self._load_key_file, C_CYAN, False).pack(side=tk.LEFT, padx=6)
        self.key_status = tk.Label(kr2, text="⚠ not validated",
                                   fg=C_YELLOW, bg=C_BG2, font=FONT_UI_S)
        self.key_status.pack(side=tk.LEFT, padx=4)

        # ── Quick Actions ─────────────────────────────────────────────────────
        self._section(scroll_frame, "QUICK ACTIONS")
        card3 = self._card(scroll_frame)

        actions = [
            ("Tester Present",           self._tester_present,  C_BLUE,  "0x3E 00"),
            ("Enter Prog Session",       self._enter_prog,      C_BLUE,  "0x10 02"),
            ("Security Access",          self._security_access, C_GREEN, "0x27 01/02"),
            ("Read BL Version",          self._read_bl_version, C_CYAN,  "0x22 F181"),
            ("Read SW Version",          self._read_sw_version, C_CYAN,  "0x22 F189"),
            ("Read Fingerprint",         self._read_fingerprint,C_CYAN,  "0x22 F15B"),
            ("Read DTC",                 self._read_dtc,        C_YELLOW,"0x19 02 FF"),
            ("Clear DTC",                self._clear_dtc,       C_ORANGE,"0x14 FF FF FF"),
            ("Verify CRC",               self._verify_crc,      C_GREEN, "0x31 FF01"),
            ("ECU Reset",                self._ecu_reset,       C_RED,   "0x11 01"),
        ]
        for label, cmd, col, hint in actions:
            row = tk.Frame(card3, bg=C_BG2)
            row.pack(fill=tk.X, pady=2)
            b = tk.Button(row, text=label,
                          command=cmd,
                          bg=C_BG3, fg=col,
                          activebackground=C_BG4, activeforeground=col,
                          relief=tk.FLAT, font=FONT_UI_S,
                          padx=10, pady=4, cursor="hand2",
                          anchor=tk.W)
            b.pack(side=tk.LEFT, fill=tk.X, expand=True)
            tk.Label(row, text=hint, fg=C_FG3, bg=C_BG2,
                     font=("Consolas", 8)).pack(side=tk.RIGHT, padx=6)

    # ── RIGHT PANEL ───────────────────────────────────────────────────────────

    def _build_right(self, parent):
        nb = ttk.Notebook(parent)
        nb.pack(fill=tk.BOTH, expand=True, padx=6, pady=8)

        # Tab 1 — OTA Flash
        ota_f = tk.Frame(nb, bg=C_BG)
        nb.add(ota_f, text="  ⬡ OTA FLASH  ")
        self._build_ota_tab(ota_f)

        # Tab 2 — DTC Monitor
        dtc_f = tk.Frame(nb, bg=C_BG)
        nb.add(dtc_f, text="  ⬡ DTC MONITOR  ")
        self._build_dtc_tab(dtc_f)

        # Tab 3 — Fingerprint
        fp_f = tk.Frame(nb, bg=C_BG)
        nb.add(fp_f, text="  ⬡ FINGERPRINT  ")
        self._build_fp_tab(fp_f)

        # Tab 4 — Raw UDS
        raw_f = tk.Frame(nb, bg=C_BG)
        nb.add(raw_f, text="  ⬡ RAW UDS  ")
        self._build_raw_tab(raw_f)

        # Tab 5 — Log
        log_f = tk.Frame(nb, bg=C_BG)
        nb.add(log_f, text="  ⬡ LOG  ")
        self._build_log_tab(log_f)

    # ── OTA TAB ───────────────────────────────────────────────────────────────

    def _build_ota_tab(self, parent):
        top = tk.Frame(parent, bg=C_BG)
        top.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        # File section
        self._section(top, "FIRMWARE FILE")
        fc = self._card(top)

        frow = tk.Frame(fc, bg=C_BG2)
        frow.pack(fill=tk.X, pady=4)
        self.fw_entry = tk.Entry(frow, textvariable=self.fw_path, width=42,
                                 bg=C_BG3, fg=C_FG,
                                 insertbackground=C_BLUE,
                                 relief=tk.FLAT, font=FONT_MONO_S)
        self.fw_entry.pack(side=tk.LEFT, padx=6)
        self._btn(frow, "Browse…", self._browse_fw, C_CYAN, False).pack(side=tk.LEFT, padx=4)

        # File info bar
        self.fw_info = tk.Frame(fc, bg=C_BG3, height=28)
        self.fw_info.pack(fill=tk.X, padx=6, pady=(0, 6))
        self.fw_info.pack_propagate(False)
        self.fw_info_lbl = tk.Label(self.fw_info, text="No file selected",
                                    fg=C_FG2, bg=C_BG3, font=FONT_UI_S,
                                    anchor=tk.W)
        self.fw_info_lbl.pack(fill=tk.X, padx=8, pady=4)

        # Info chips
        chips = tk.Frame(fc, bg=C_BG2)
        chips.pack(fill=tk.X, padx=6, pady=(0, 6))
        self.chip_model   = self._chip(chips, "Model", "—",       C_BLUE)
        self.chip_version = self._chip(chips, "Version", "—",     C_GREEN)
        self.chip_size    = self._chip(chips, "Raw Size", "—",    C_FG2)
        self.chip_comp    = self._chip(chips, "Compressed", "—",  C_CYAN)

        # Options
        self._section(top, "OTA OPTIONS")
        oc = self._card(top)

        # FIX: same parent fix applied here
        row = self._field_row(oc, "Vehicle Model")
        self._combo(row, self.model_var, list(VEHICLE_MODELS.keys()), 18).pack(
            side=tk.LEFT, padx=4)

        sn_row = tk.Frame(oc, bg=C_BG2)
        sn_row.pack(fill=tk.X, pady=3)
        tk.Label(sn_row, text="Station ID", fg=C_FG2, bg=C_BG2,
                 font=FONT_UI_S, width=12, anchor=tk.W).pack(side=tk.LEFT, padx=6)
        _pc = socket.gethostname()[:10]
        self.sn_var = tk.StringVar(value=_pc)
        self._entry(sn_row, self.sn_var, 16).pack(side=tk.LEFT)
        tk.Label(sn_row, text=f"(PC: {_pc})", fg=C_FG3, bg=C_BG2,
                 font=FONT_UI_S).pack(side=tk.LEFT, padx=6)

        sw_row = tk.Frame(oc, bg=C_BG2)
        sw_row.pack(fill=tk.X, pady=3)
        tk.Label(sw_row, text="SW Version", fg=C_FG2, bg=C_BG2,
                 font=FONT_UI_S, width=12, anchor=tk.W).pack(side=tk.LEFT, padx=6)
        tk.Label(sw_row, textvariable=self.sw_ver_var,
                 fg=C_BLUE2, bg=C_BG2, font=("Consolas", 10, "bold")).pack(side=tk.LEFT)
        tk.Label(sw_row, text="  ← auto from file", fg=C_FG3,
                 bg=C_BG2, font=FONT_UI_S).pack(side=tk.LEFT)

        dev_row = tk.Frame(oc, bg=C_BG2)
        dev_row.pack(fill=tk.X, pady=4)
        tk.Checkbutton(dev_row, text="Developer Mode  —  bypass model/version check (0x27 11/12) — DTC C10007 logged",
                       variable=self.dev_mode,
                       fg=C_PURPLE, bg=C_BG2, selectcolor=C_BG3,
                       activebackground=C_BG2, font=FONT_UI_S).pack(side=tk.LEFT, padx=6)

        # Progress section
        self._section(top, "OTA PROGRESS")
        pc = self._card(top)

        # Step indicator
        self.step_labels = ["Reset","Catch","Session","SA","Erase",
                            "Download","Transfer","Verify","CRC","FP","Reset"]
        step_frame = tk.Frame(pc, bg=C_BG2)
        step_frame.pack(fill=tk.X, padx=6, pady=6)
        self.step_dots = []
        for i, s in enumerate(self.step_labels):
            sf = tk.Frame(step_frame, bg=C_BG2)
            sf.pack(side=tk.LEFT, expand=True)
            dot = tk.Label(sf, text="⬡", font=("Segoe UI", 11),
                           fg=C_FG3, bg=C_BG2)
            dot.pack()
            tk.Label(sf, text=s, font=("Segoe UI", 7),
                     fg=C_FG3, bg=C_BG2).pack()
            self.step_dots.append(dot)

        self.ota_status_lbl = tk.Label(pc, text="Ready — select firmware to begin",
                                       fg=C_FG2, bg=C_BG2, font=FONT_UI_S,
                                       anchor=tk.W)
        self.ota_status_lbl.pack(fill=tk.X, padx=8, pady=(4, 2))

        self.ota_progress = ttk.Progressbar(pc, style="OTA.Horizontal.TProgressbar",
                                            mode="determinate", maximum=100)
        self.ota_progress.pack(fill=tk.X, padx=8, pady=4)

        pct_row = tk.Frame(pc, bg=C_BG2)
        pct_row.pack(fill=tk.X, padx=8, pady=(0, 6))
        self.ota_pct_lbl  = tk.Label(pct_row, text="0%", fg=C_BLUE,
                                      bg=C_BG2, font=("Consolas", 10, "bold"))
        self.ota_pct_lbl.pack(side=tk.LEFT)
        self.ota_bytes_lbl = tk.Label(pct_row, text="",  fg=C_FG2,
                                       bg=C_BG2, font=FONT_MONO_S)
        self.ota_bytes_lbl.pack(side=tk.RIGHT)

        # Buttons
        btnrow = tk.Frame(top, bg=C_BG)
        btnrow.pack(fill=tk.X, pady=8)
        self.btn_ota = self._btn(btnrow, "▶   START FULL OTA FLASH",
                                  self._start_ota, C_GREEN, True)
        self.btn_ota.pack(side=tk.LEFT, padx=0, ipadx=20, ipady=4)
        self._btn(btnrow, "■  ABORT", self._abort_ota, C_RED, False).pack(
            side=tk.LEFT, padx=8)

    # ── DTC TAB ───────────────────────────────────────────────────────────────

    def _build_dtc_tab(self, parent):
        top = tk.Frame(parent, bg=C_BG)
        top.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        self._section(top, "DIAGNOSTIC TROUBLE CODES")

        # Buttons
        br = tk.Frame(top, bg=C_BG)
        br.pack(fill=tk.X, pady=(0, 8))
        self._btn(br, "⟳  READ DTC",   self._read_dtc_tab, C_YELLOW, True).pack(side=tk.LEFT, padx=0)
        self._btn(br, "✕  CLEAR DTC",  self._clear_dtc,    C_RED,    True).pack(side=tk.LEFT, padx=8)
        self.dtc_count_lbl = tk.Label(br, text="", fg=C_FG2, bg=C_BG, font=FONT_UI_S)
        self.dtc_count_lbl.pack(side=tk.LEFT, padx=8)

        # DTC display frame
        dtc_outer = tk.Frame(top, bg=C_BG2, bd=0,
                             highlightbackground=C_BORDER, highlightthickness=1)
        dtc_outer.pack(fill=tk.BOTH, expand=True)

        # Header
        hdr = tk.Frame(dtc_outer, bg=C_BG3)
        hdr.pack(fill=tk.X)
        for text, w in [("DTC Code", 12), ("Name", 22), ("Status", 8), ("Description", 40)]:
            tk.Label(hdr, text=text, fg=C_FG2, bg=C_BG3,
                     font=FONT_UI_B, width=w, anchor=tk.W,
                     padx=8, pady=6).pack(side=tk.LEFT)

        # Scrollable DTC list
        dtc_scroll = tk.Frame(dtc_outer, bg=C_BG2)
        dtc_scroll.pack(fill=tk.BOTH, expand=True)
        self.dtc_list_frame = dtc_scroll

        # Known DTC reference
        self._section(top, "NEXABOOT DTC REFERENCE")
        ref_card = self._card(top)
        ref_text = scrolledtext.ScrolledText(ref_card, height=8,
                                              bg=C_BG3, fg=C_FG,
                                              font=FONT_MONO_S,
                                              relief=tk.FLAT,
                                              insertbackground=C_BLUE)
        ref_text.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        for code, (name, desc, _) in DTC_INFO.items():
            ref_text.insert(tk.END, f"  C{code:06X}  {name:<22}  {desc}\n")
        ref_text.config(state=tk.DISABLED)

    # ── FINGERPRINT TAB ───────────────────────────────────────────────────────

    def _build_fp_tab(self, parent):
        top = tk.Frame(parent, bg=C_BG)
        top.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        # Read section
        self._section(top, "READ FINGERPRINT")
        rc = self._card(top)
        self.fp_display = tk.Text(rc, height=7, bg=C_BG3, fg=C_FG,
                                   font=FONT_MONO_S, relief=tk.FLAT,
                                   insertbackground=C_BLUE)
        self.fp_display.pack(fill=tk.X, padx=6, pady=6)
        self._btn(rc, "⟳  READ FINGERPRINT + SW VERSION",
                  self._read_fingerprint, C_BLUE, True).pack(anchor=tk.W, padx=6, pady=(0, 6))

        # Write section
        self._section(top, "WRITE FINGERPRINT  (0x2E / DID F15B)")
        wc = self._card(top)

        ts_row = tk.Frame(wc, bg=C_BG2)
        ts_row.pack(fill=tk.X, pady=3)
        tk.Label(ts_row, text="Timestamp", fg=C_FG2, bg=C_BG2,
                 font=FONT_UI_S, width=12, anchor=tk.W).pack(side=tk.LEFT, padx=6)
        self.fp_ts_var = tk.StringVar(value=str(int(time.time())))
        self._entry(ts_row, self.fp_ts_var, 14).pack(side=tk.LEFT)
        self._btn(ts_row, "Now", lambda: self.fp_ts_var.set(str(int(time.time()))),
                  C_FG2, False).pack(side=tk.LEFT, padx=6)

        sn_row = tk.Frame(wc, bg=C_BG2)
        sn_row.pack(fill=tk.X, pady=3)
        tk.Label(sn_row, text="Tester S/N", fg=C_FG2, bg=C_BG2,
                 font=FONT_UI_S, width=12, anchor=tk.W).pack(side=tk.LEFT, padx=6)
        self.fp_sn_var = tk.StringVar(value=socket.gethostname()[:10])
        self._entry(sn_row, self.fp_sn_var, 14).pack(side=tk.LEFT)

        ver_row = tk.Frame(wc, bg=C_BG2)
        ver_row.pack(fill=tk.X, pady=3)
        tk.Label(ver_row, text="SW Version", fg=C_FG2, bg=C_BG2,
                 font=FONT_UI_S, width=12, anchor=tk.W).pack(side=tk.LEFT, padx=6)
        self.fp_ver_var = tk.StringVar(value="01 00 00 00")
        self._entry(ver_row, self.fp_ver_var, 14).pack(side=tk.LEFT)
        tk.Label(ver_row, text="(BCD hex, 4 bytes)", fg=C_FG3,
                 bg=C_BG2, font=FONT_UI_S).pack(side=tk.LEFT, padx=6)

        self._btn(wc, "✎  WRITE FINGERPRINT",
                  self._write_fingerprint, C_GREEN, True).pack(
                  fill=tk.X, padx=6, pady=(6, 6), ipady=3)

    # ── RAW UDS TAB ───────────────────────────────────────────────────────────

    def _build_raw_tab(self, parent):
        top = tk.Frame(parent, bg=C_BG)
        top.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        self._section(top, "CUSTOM UDS REQUEST")
        rc = self._card(top)

        tk.Label(rc, text="Hex bytes (space separated):",
                 fg=C_FG2, bg=C_BG2, font=FONT_UI_S).pack(anchor=tk.W, padx=6, pady=(4, 2))
        self.raw_entry = tk.Entry(rc, width=50,
                                  bg=C_BG3, fg=C_YELLOW,
                                  insertbackground=C_BLUE,
                                  relief=tk.FLAT, font=FONT_MONO)
        self.raw_entry.pack(fill=tk.X, padx=6, pady=(0, 4))
        self.raw_entry.insert(0, "3E 00")

        rrow = tk.Frame(rc, bg=C_BG2)
        rrow.pack(fill=tk.X, pady=4)
        self._btn(rrow, "⬡  SEND", self._raw_send, C_BLUE, True).pack(side=tk.LEFT, padx=6)
        tk.Label(rrow, text="Timeout (s):", fg=C_FG2, bg=C_BG2,
                 font=FONT_UI_S).pack(side=tk.LEFT, padx=8)
        self.raw_timeout = tk.StringVar(value="5")
        self._entry(rrow, self.raw_timeout, 5).pack(side=tk.LEFT)

        # Quick commands — grouped
        self._section(top, "QUICK COMMANDS")
        qc = self._card(top)

        groups = [
            ("SESSION", [
                ("10 02", "Enter Prog Session"),
                ("10 01", "Enter Default Session"),
                ("3E 00", "Tester Present"),
                ("11 01", "ECU Reset Hard"),
            ]),
            ("SECURITY", [
                ("27 01", "SA Request Seed (Prod)"),
                ("27 11", "SA Request Seed (Dev)"),
            ]),
            ("READ", [
                ("22 F1 81", "Read BL Version"),
                ("22 F1 89", "Read SW Version"),
                ("22 F1 5B", "Read Fingerprint"),
                ("22 F1 86", "Read Active Session"),
                ("19 02 FF", "Read DTC All"),
            ]),
            ("CONTROL", [
                ("14 FF FF FF",       "Clear DTC"),
                ("31 01 FF 01",       "Verify CRC"),
                ("28 03 01",          "CommCtrl Disable"),
                ("28 00 01",          "CommCtrl Enable"),
                ("85 02",             "DTC Setting Off"),
                ("85 01",             "DTC Setting On"),
            ]),
        ]

        for grp_name, cmds in groups:
            gf = tk.Frame(qc, bg=C_BG2)
            gf.pack(fill=tk.X, pady=(4, 0))
            tk.Label(gf, text=grp_name, fg=C_FG3, bg=C_BG2,
                     font=("Segoe UI", 8, "bold"), width=10,
                     anchor=tk.W).pack(side=tk.LEFT, padx=6)
            for cmd, label in cmds:
                b = tk.Button(gf, text=label,
                              command=lambda c=cmd: self._quick_cmd(c),
                              bg=C_BG3, fg=C_FG2,
                              activebackground=C_BG4, activeforeground=C_BLUE,
                              relief=tk.FLAT, font=FONT_UI_S,
                              padx=6, pady=3, cursor="hand2")
                b.pack(side=tk.LEFT, padx=2)

        # NRC Reference
        self._section(top, "NRC REFERENCE")
        nrc_card = self._card(top)
        nrc_text = scrolledtext.ScrolledText(nrc_card, height=8,
                                              bg=C_BG3, fg=C_FG,
                                              font=FONT_MONO_S,
                                              relief=tk.FLAT)
        nrc_text.pack(fill=tk.BOTH, padx=4, pady=4)
        for nrc, (name, desc) in NRC_INFO.items():
            nrc_text.insert(tk.END, f"  0x{nrc:02X}  {name:<35}  {desc}\n")
        nrc_text.config(state=tk.DISABLED)

    # ── LOG TAB ───────────────────────────────────────────────────────────────

    def _build_log_tab(self, parent):
        ctrl = tk.Frame(parent, bg=C_BG)
        ctrl.pack(fill=tk.X, padx=8, pady=6)
        tk.Label(ctrl, text="UDS Transaction Log",
                 fg=C_FG2, bg=C_BG, font=FONT_HDR).pack(side=tk.LEFT)
        self._btn(ctrl, "Clear", self._clear_log, C_FG2, False).pack(side=tk.RIGHT, padx=4)
        self._btn(ctrl, "Save…", self._save_log,  C_FG2, False).pack(side=tk.RIGHT, padx=4)

        log_outer = tk.Frame(parent, bg=C_BG2,
                             highlightbackground=C_BORDER, highlightthickness=1)
        log_outer.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        self.log = scrolledtext.ScrolledText(
            log_outer, bg=C_BG, fg=C_FG, font=FONT_MONO_S,
            relief=tk.FLAT, insertbackground=C_BLUE,
            selectbackground=C_BG3, wrap=tk.WORD)
        self.log.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        tags = {
            "TX":   C_BLUE,    "RX":   C_GREEN2,
            "ERR":  C_RED,     "INFO": C_FG2,
            "OK":   C_GREEN,   "WARN": C_YELLOW,
            "DTC":  C_ORANGE,  "HEAD": C_BLUE2,
        }
        for tag, color in tags.items():
            self.log.tag_config(tag, foreground=color)

    # ──────────────────────────────────────────────────────────────────────────
    # WIDGET HELPERS
    # ──────────────────────────────────────────────────────────────────────────

    def _section(self, parent, text):
        f = tk.Frame(parent, bg=C_BG)
        f.pack(fill=tk.X, pady=(8, 2))
        tk.Label(f, text=text, fg=C_BLUE, bg=C_BG,
                 font=("Consolas", 9, "bold")).pack(side=tk.LEFT)
        tk.Frame(f, bg=C_BORDER, height=1).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))

    def _card(self, parent):
        f = tk.Frame(parent, bg=C_BG2, bd=0,
                     highlightbackground=C_BORDER, highlightthickness=1)
        f.pack(fill=tk.X, pady=(0, 4))
        return f

    def _field_row(self, parent, label):
        """Create a labelled row and return it so callers can pack widgets into it."""
        row = tk.Frame(parent, bg=C_BG2)
        row.pack(fill=tk.X, pady=3)
        tk.Label(row, text=label, fg=C_FG2, bg=C_BG2,
                 font=FONT_UI_S, width=12, anchor=tk.W).pack(side=tk.LEFT, padx=6)
        return row

    def _entry(self, parent, var, width=20):
        e = tk.Entry(parent, textvariable=var, width=width,
                     bg=C_BG3, fg=C_FG,
                     insertbackground=C_BLUE,
                     relief=tk.FLAT, font=FONT_MONO_S)
        return e

    def _combo(self, parent, var, values, width=14):
        cb = ttk.Combobox(parent, textvariable=var,
                          values=values, width=width,
                          font=FONT_MONO_S, state="readonly")
        return cb

    def _btn(self, parent, text, cmd, color=C_BLUE, fill=False):
        b = tk.Button(parent, text=text, command=cmd,
                      bg=C_BG3, fg=color,
                      activebackground=C_BG4, activeforeground=color,
                      relief=tk.FLAT, font=FONT_UI_B,
                      padx=12, pady=5, cursor="hand2",
                      highlightbackground=color, highlightthickness=1)
        return b

    def _chip(self, parent, label, value, color):
        f = tk.Frame(parent, bg=C_BG3,
                     highlightbackground=color, highlightthickness=1)
        f.pack(side=tk.LEFT, padx=4, pady=4)
        tk.Label(f, text=label, fg=C_FG3, bg=C_BG3,
                 font=("Segoe UI", 7)).pack(padx=6, pady=(2, 0))
        lbl = tk.Label(f, text=value, fg=color, bg=C_BG3,
                       font=("Consolas", 9, "bold"))
        lbl.pack(padx=6, pady=(0, 2))
        return lbl

    # ──────────────────────────────────────────────────────────────────────────
    # LOG
    # ──────────────────────────────────────────────────────────────────────────

    def _log(self, msg, tag="INFO"):
        ts = time.strftime("%H:%M:%S")
        self.q.put((f"[{ts}]  {msg}\n", tag))

    def _poll_queue(self):
        try:
            while True:
                msg, tag = self.q.get_nowait()
                self.log.insert(tk.END, msg, tag)
                self.log.see(tk.END)
        except queue.Empty:
            pass
        self.after(50, self._poll_queue)

    def _clear_log(self):
        self.log.delete("1.0", tk.END)

    def _save_log(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text", "*.txt"), ("All", "*.*")],
            title="Save Log")
        if path:
            with open(path, "w") as f:
                f.write(self.log.get("1.0", tk.END))
            self._log(f"Log saved: {path}", "OK")

    def _hex(self, b: bytes) -> str:
        return " ".join(f"{x:02X}" for x in b)

    # ──────────────────────────────────────────────────────────────────────────
    # CONNECTION
    # ──────────────────────────────────────────────────────────────────────────

    def _connect(self):
        if self.connected: self._disconnect()
        try:
            self._log(f"Connecting {self.iface_var.get()} / "
                      f"{self.chan_var.get()} @ {self.brate_var.get()} bps…", "INFO")
            self.can.connect(
                self.iface_var.get(), self.chan_var.get(),
                int(self.brate_var.get()),
                int(self.rxid_var.get(), 16),
                int(self.txid_var.get(), 16))
            self.connected = True
            self._set_status(True)
            self._log("Connected ✓", "OK")
            self._save_config()
        except Exception as e:
            self._log(f"Connection failed: {e}", "ERR")
            self._set_status(False)

    def _disconnect(self):
        try: self.can.disconnect()
        except: pass
        self.connected = False
        self._set_status(False)
        self._log("Disconnected", "INFO")

    def _set_status(self, ok):
        if ok:
            self.status_dot.config(fg=C_GREEN)
            self.status_lbl.config(fg=C_GREEN, text="CONNECTED")
        else:
            self.status_dot.config(fg=C_RED)
            self.status_lbl.config(fg=C_RED, text="DISCONNECTED")

    # ──────────────────────────────────────────────────────────────────────────
    # KEY
    # ──────────────────────────────────────────────────────────────────────────

    def _get_key(self):
        try:
            raw = bytes.fromhex(self.key_var.get().replace(" ", ""))
            if len(raw) != 16:
                raise ValueError("Key must be exactly 16 bytes")
            self.aes_key = raw
            self.key_status.config(text="✓ 16 bytes valid", fg=C_GREEN)
            return raw
        except Exception as e:
            self.key_status.config(text=f"✗ {e}", fg=C_RED)
            messagebox.showerror("Key Error", str(e))
            return None

    def _load_key_file(self):
        path = filedialog.askopenfilename(
            title="Select AES key binary (16 bytes)",
            filetypes=[("Binary", "*.bin"), ("All", "*.*")])
        if not path: return
        with open(path, "rb") as f: raw = f.read()
        if len(raw) != 16:
            messagebox.showerror("Key Error", f"File is {len(raw)} bytes — need 16")
            return
        self.key_var.set(" ".join(f"{b:02X}" for b in raw))
        self.aes_key = raw
        self.key_status.config(text="✓ loaded from file", fg=C_GREEN)

    # ──────────────────────────────────────────────────────────────────────────
    # UDS HELPERS
    # ──────────────────────────────────────────────────────────────────────────

    def _run(self, fn):
        if not self.connected:
            messagebox.showwarning("Not Connected", "Connect to CAN bus first.")
            return
        threading.Thread(target=fn, daemon=True).start()

    def _uds(self, data: bytes, timeout=10.0) -> bytes:
        self._log(f"TX: {self._hex(data)}", "TX")
        resp = self.can.request(data, timeout)
        self._log(f"RX: {self._hex(resp)}", "RX")
        return resp

    def _unlock(self, key: bytes, dev=False):
        self._uds(bytes([0x10, 0x02]))
        sl = 0x11 if dev else 0x01
        resp = self._uds(bytes([0x27, sl]))
        seed = resp[2:6]
        if seed != bytes(4):
            dkey = xtea_derive_key(seed, key)
            self._uds(bytes([0x27, sl + 1]) + dkey)
            self._log(f"Seed: {self._hex(seed)}  Key: {self._hex(dkey)}", "INFO")
        if dev:
            self._log("Developer Mode unlocked ✓  (DTC C10007 will be logged)", "WARN")
        else:
            self._log("Security Access unlocked ✓", "OK")

    # ──────────────────────────────────────────────────────────────────────────
    # QUICK ACTIONS
    # ──────────────────────────────────────────────────────────────────────────

    def _tester_present(self):
        def _do():
            try:
                self._uds(bytes([0x3E, 0x00]))
                self._log("TesterPresent OK ✓", "OK")
            except Exception as e:
                self._log(f"TesterPresent FAILED: {e}", "ERR")
        self._run(_do)

    def _enter_prog(self):
        def _do():
            try:
                self._uds(bytes([0x10, 0x02]))
                self._log("Programming session entered ✓", "OK")
            except Exception as e:
                self._log(f"Enter prog session FAILED: {e}", "ERR")
        self._run(_do)

    def _security_access(self):
        def _do():
            key = self._get_key()
            if not key: return
            try:
                self._unlock(key, dev=self.dev_mode.get())
            except Exception as e:
                self._log(f"Security Access FAILED: {e}", "ERR")
        self._run(_do)

    def _read_bl_version(self):
        def _do():
            try:
                resp = self._uds(bytes([0x22, 0xF1, 0x81]))
                ver  = resp[3:].decode("ascii", errors="replace").rstrip("\x00")
                self._log(f"BL Version: {ver}", "OK")
                self.after(0, lambda: self.ecu_info_labels["BL"].config(text=ver[:12]))
            except Exception as e:
                self._log(f"Read BL Version FAILED: {e}", "ERR")
        self._run(_do)

    def _read_sw_version(self):
        def _do():
            try:
                resp = self._uds(bytes([0x22, 0xF1, 0x89]))
                ver  = self._hex(resp[3:])
                self._log(f"SW Version (BCD): {ver}", "OK")
                self.after(0, lambda: self.ecu_info_labels["SW"].config(text=ver))
            except Exception as e:
                self._log(f"Read SW Version FAILED: {e}", "ERR")
        self._run(_do)

    def _read_fingerprint(self):
        def _do():
            try:
                resp = self._uds(bytes([0x22, 0xF1, 0x5B]))
                ts   = struct.unpack(">I", resp[3:7])[0]
                sn   = resp[7:17].decode("ascii", errors="replace").rstrip("\x00")
                ts_str = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(ts))
                self._log(f"Fingerprint timestamp: {ts} ({ts_str})", "OK")
                self._log(f"Fingerprint tester S/N: {sn}", "OK")
                text = (f"Timestamp : {ts_str}\n"
                        f"Tester S/N: {sn}\n"
                        f"Raw       : {self._hex(resp[3:])}\n")
                try:
                    r2  = self._uds(bytes([0x22, 0xF1, 0x89]))
                    sw  = self._hex(r2[3:])
                    text += f"SW Version: {sw}\n"
                    self._log(f"SW Version: {sw}", "OK")
                    self.after(0, lambda: self.ecu_info_labels["SW"].config(text=sw))
                except: pass
                self.after(0, lambda: (
                    self.fp_display.delete("1.0", tk.END),
                    self.fp_display.insert("1.0", text)))
            except Exception as e:
                self._log(f"Read Fingerprint FAILED: {e}", "ERR")
        self._run(_do)

    def _read_dtc(self):
        def _do():
            try:
                resp = self._uds(bytes([0x19, 0x02, 0xFF]))
                self._parse_dtcs(resp)
            except Exception as e:
                self._log(f"Read DTC FAILED: {e}", "ERR")
        self._run(_do)

    def _read_dtc_tab(self):
        def _do():
            try:
                resp = self._uds(bytes([0x19, 0x02, 0xFF]))
                self._parse_dtcs(resp)
                self._refresh_dtc_tab(resp)
            except Exception as e:
                self._log(f"Read DTC FAILED: {e}", "ERR")
        self._run(_do)

    def _parse_dtcs(self, resp):
        dtcs   = resp[4:]
        count  = len(dtcs) // 4
        if count == 0:
            self._log("DTC: no faults stored ✓", "OK")
            self.after(0, lambda: self.dtc_count_lbl.config(
                text="No faults stored ✓", fg=C_GREEN))
            return
        self._log(f"DTC: {count} fault(s) found:", "WARN")
        self.after(0, lambda: self.dtc_count_lbl.config(
            text=f"{count} fault(s) active", fg=C_RED))
        for i in range(count):
            d      = dtcs[i*4:(i+1)*4]
            code   = (d[0] << 16) | (d[1] << 8) | d[2]
            status = d[3]
            name, desc, _ = DTC_INFO.get(code, ("UNKNOWN", "Unknown DTC code", "red"))
            self._log(f"  C{code:06X}  {name:<22}  {desc}  [status=0x{status:02X}]", "DTC")

    def _refresh_dtc_tab(self, resp):
        def _update():
            for w in self.dtc_list_frame.winfo_children():
                w.destroy()
            dtcs  = resp[4:]
            count = len(dtcs) // 4
            if count == 0:
                tk.Label(self.dtc_list_frame,
                         text="  ✓  No faults stored",
                         fg=C_GREEN, bg=C_BG2, font=FONT_UI_B,
                         pady=20).pack()
                return
            for i in range(count):
                d      = dtcs[i*4:(i+1)*4]
                code   = (d[0] << 16) | (d[1] << 8) | d[2]
                status = d[3]
                name, desc, col_str = DTC_INFO.get(code, ("UNKNOWN", "Unknown DTC", "red"))
                col = {"red": C_RED, "orange": C_ORANGE, "cyan": C_CYAN}.get(col_str, C_RED)
                row = tk.Frame(self.dtc_list_frame,
                               bg=C_BG2 if i % 2 == 0 else C_BG3)
                row.pack(fill=tk.X)
                tk.Label(row, text=f"  C{code:06X}", fg=col,
                         bg=row.cget("bg"), font=("Consolas", 10, "bold"),
                         width=12, anchor=tk.W, pady=6).pack(side=tk.LEFT)
                tk.Label(row, text=name, fg=col,
                         bg=row.cget("bg"), font=FONT_UI_B,
                         width=22, anchor=tk.W).pack(side=tk.LEFT)
                tk.Label(row, text=f"0x{status:02X}", fg=C_FG2,
                         bg=row.cget("bg"), font=FONT_MONO_S,
                         width=8, anchor=tk.W).pack(side=tk.LEFT)
                tk.Label(row, text=desc, fg=C_FG2,
                         bg=row.cget("bg"), font=FONT_UI_S,
                         anchor=tk.W, padx=8).pack(side=tk.LEFT, fill=tk.X)
        self.after(0, _update)

    def _clear_dtc(self):
        if not messagebox.askyesno("Clear DTC",
            "Clear all Diagnostic Trouble Codes?"):
            return
        def _do():
            try:
                self._uds(bytes([0x14, 0xFF, 0xFF, 0xFF]))
                self._log("DTC cleared ✓", "OK")
                self.after(0, lambda: self.dtc_count_lbl.config(
                    text="Cleared ✓", fg=C_GREEN))
                for w in self.dtc_list_frame.winfo_children():
                    self.after(0, w.destroy)
            except Exception as e:
                self._log(f"Clear DTC FAILED: {e}", "ERR")
        self._run(_do)

    def _verify_crc(self):
        key = self._get_key()
        if not key: return
        def _do():
            try:
                self._unlock(key, dev=self.dev_mode.get())
                resp = self._uds(bytes([0x31, 0x01, 0xFF, 0x01]), timeout=30.0)
                ok   = resp[4] if len(resp) >= 5 else 0
                if ok == 0x01:
                    self._log("CRC verify: PASS ✓  App slot is valid", "OK")
                else:
                    self._log("CRC verify: FAIL ✗  No valid app flashed", "WARN")
            except Exception as e:
                self._log(f"Verify CRC FAILED: {e}", "ERR")
        self._run(_do)

    def _ecu_reset(self):
        def _do():
            try:
                self._uds(bytes([0x11, 0x01]))
                self._log("ECU Reset sent ✓", "OK")
            except TimeoutError:
                self._log("ECU Reset sent (no response — ECU restarting) ✓", "OK")
            except Exception as e:
                self._log(f"ECU Reset FAILED: {e}", "ERR")
        self._run(_do)

    # ──────────────────────────────────────────────────────────────────────────
    # FINGERPRINT WRITE
    # ──────────────────────────────────────────────────────────────────────────

    def _write_fingerprint(self):
        def _do():
            try:
                ts  = int(self.fp_ts_var.get())
                sn  = self.fp_sn_var.get().encode("ascii")[:10].ljust(10)
                ver = bytes.fromhex(
                    self.fp_ver_var.get().replace(" ", ""))[:4].ljust(4, b'\x00')
                pl  = bytes([0x2E, 0xF1, 0x5B])
                pl += struct.pack(">I", ts) + sn + ver
                self._uds(pl)
                self._log("Fingerprint written ✓", "OK")
            except Exception as e:
                self._log(f"Write Fingerprint FAILED: {e}", "ERR")
        self._run(_do)

    # ──────────────────────────────────────────────────────────────────────────
    # RAW UDS
    # ──────────────────────────────────────────────────────────────────────────

    def _raw_send(self):
        def _do():
            try:
                raw = bytes.fromhex(self.raw_entry.get().replace(" ", ""))
                t   = float(self.raw_timeout.get())
                self._uds(raw, timeout=t)
            except Exception as e:
                self._log(f"Raw UDS FAILED: {e}", "ERR")
        self._run(_do)

    def _quick_cmd(self, hex_str):
        self.raw_entry.delete(0, tk.END)
        self.raw_entry.insert(0, hex_str)

    # ──────────────────────────────────────────────────────────────────────────
    # OTA FLASH
    # ──────────────────────────────────────────────────────────────────────────

    def _browse_fw(self):
        path = filedialog.askopenfilename(
            title="Select signed firmware (.bin)",
            filetypes=[("Binary", "*.bin"), ("All", "*.*")])
        if not path: return
        self.fw_path.set(path)
        data = open(path, "rb").read()
        sz   = len(data)
        comp = len(zlib.compress(data, level=9))

        SIGN_MAGIC = 0xEC5A1234
        MODEL_BY_ID = {v: k for k, v in VEHICLE_MODELS.items()}

        if len(data) >= 13 and struct.unpack('>I', data[0:4])[0] == SIGN_MAGIC:
            fw_model = struct.unpack('>H', data[8:10])[0]
            vm, vn, vp = data[10], data[11], data[12]
            model_name = MODEL_BY_ID.get(fw_model, f"0x{fw_model:04X}")
            self.sw_ver_var.set(f"{vm}.{vn}.{vp}")
            if fw_model in MODEL_BY_ID:
                self.model_var.set(model_name)
            self.chip_model.config(  text=model_name)
            self.chip_version.config(text=f"v{vm}.{vn}.{vp}")
            self.chip_size.config(   text=f"{sz:,} B")
            self.chip_comp.config(   text=f"{comp:,} B ({100*comp//sz}%)")
            self.fw_info_lbl.config(
                text=f"{os.path.basename(path)}  —  SignHeader OK ✓",
                fg=C_GREEN)
            self.ecu_info_labels["Model"].config(text=model_name)
            self._log(f"Loaded: {path}", "INFO")
            self._log(f"  Model: {model_name} (0x{fw_model:04X})  "
                      f"Version: v{vm}.{vn}.{vp}  "
                      f"Size: {sz:,} B → {comp:,} B compressed", "OK")
        else:
            self.sw_ver_var.set("—")
            self.chip_model.config(  text="—")
            self.chip_version.config(text="—")
            self.chip_size.config(   text=f"{sz:,} B")
            self.chip_comp.config(   text=f"{comp:,} B ({100*comp//sz}%)")
            self.fw_info_lbl.config(
                text="⚠  SignHeader not found — raw binary",
                fg=C_YELLOW)

    def _set_step(self, step):
        def _upd():
            for i, dot in enumerate(self.step_dots):
                if i < step:
                    dot.config(fg=C_GREEN, text="⬡")
                elif i == step:
                    dot.config(fg=C_BLUE, text="⬡")
                else:
                    dot.config(fg=C_FG3, text="⬡")
        self.after(0, _upd)

    def _ota_update(self, msg, pct, bytes_str=""):
        self.after(0, self.ota_status_lbl.config, {"text": msg})
        self.after(0, self.ota_progress.config,   {"value": pct})
        self.after(0, self.ota_pct_lbl.config,    {"text": f"{pct}%"})
        self.after(0, self.ota_bytes_lbl.config,  {"text": bytes_str})

    def _start_ota(self):
        if not self.connected:
            messagebox.showwarning("Not Connected", "Connect to CAN bus first."); return
        key = self._get_key()
        if not key: return
        fw_path = self.fw_path.get()
        if not fw_path or not os.path.exists(fw_path):
            messagebox.showerror("No Firmware", "Select signed firmware .bin first."); return
        self.ota_abort = False
        self.btn_ota.config(state=tk.DISABLED)
        self.ota_thread = threading.Thread(
            target=self._run_ota, args=(fw_path, key), daemon=True)
        self.ota_thread.start()

    def _abort_ota(self):
        self.ota_abort = True
        self._log("OTA abort requested…", "WARN")

    def _run_ota(self, fw_path: str, key: bytes):
        try:
            self._log("=" * 60, "HEAD")
            self._log("NexaBoot OTA Flash — Starting", "HEAD")
            self._log("=" * 60, "HEAD")

            # ── Load + compress + encrypt ──────────────────────────────────
            self._set_step(0)
            with open(fw_path, "rb") as f: raw = f.read()

            SIGN_MAGIC  = 0xEC5A1234
            fw_model    = 0x0001
            fw_ver      = (1, 0, 0)
            MODEL_BY_ID = {v: k for k, v in VEHICLE_MODELS.items()}

            if len(raw) >= 13 and struct.unpack('>I', raw[0:4])[0] == SIGN_MAGIC:
                fw_model = struct.unpack('>H', raw[8:10])[0]
                fw_ver   = (raw[10], raw[11], raw[12])
                self._log(f"SignHeader: model=0x{fw_model:04X} "
                          f"ver={fw_ver[0]}.{fw_ver[1]}.{fw_ver[2]}", "INFO")
            else:
                self._log("⚠ SignHeader not found — using defaults", "WARN")

            sel_model = VEHICLE_MODELS.get(self.model_var.get(), 0x0001)
            if (fw_model not in (0xFFFF, 0x0000) and
                fw_model != sel_model and
                not self.dev_mode.get()):
                raise RuntimeError(
                    f"Model mismatch!\n"
                    f"  File: {MODEL_BY_ID.get(fw_model,'0x{fw_model:04X}')}\n"
                    f"  Selected: {self.model_var.get()}\n"
                    f"  Enable Developer Mode to bypass.")

            self._ota_update("Compressing firmware…", 2)
            compressed = zlib.compress(raw, level=9)
            self._log(f"Firmware: {len(raw):,} B → {len(compressed):,} B "
                      f"({100*len(compressed)//len(raw)}%)", "INFO")

            nonce     = os.urandom(12)
            self._ota_update("Encrypting…", 3)
            encrypted = aes_ctr_encrypt(compressed, key, nonce)
            self._log(f"Encrypted: {len(encrypted):,} B  nonce={nonce.hex()}", "INFO")

            if self.ota_abort: raise RuntimeError("Aborted by user")

            # ── Blind reset ───────────────────────────────────────────────
            self._set_step(0)
            self._ota_update("Triggering app reset…", 4)
            self._log("Blind send 0x10 0x02 — triggering reset…", "INFO")
            try:
                with self.can.lock:
                    self.can.tp.send(bytes([0x10, 0x02]))
                    t = time.time() + 0.08
                    while time.time() < t:
                        self.can.tp.process()
                        time.sleep(0.001)
            except: pass
            time.sleep(2.0)

            if self.ota_abort: raise RuntimeError("Aborted by user")

            # ── Catch bootloader ──────────────────────────────────────────
            self._set_step(1)
            self._ota_update("Catching bootloader…", 5)
            self._log("Waiting for bootloader (10/sec, max 10s)…", "INFO")
            caught = False
            for attempt in range(100):
                try:
                    self._uds(bytes([0x10, 0x02]), timeout=0.08)
                    self._log(f"Bootloader in session ✓ (attempt {attempt+1})", "OK")
                    caught = True
                    break
                except: pass
                time.sleep(0.02)
            if not caught:
                self._uds(bytes([0x10, 0x02]))

            # ── Flush + re-enter session ──────────────────────────────────
            self._set_step(2)
            try:
                with self.can.lock:
                    flush_end = time.time() + 0.3
                    while time.time() < flush_end:
                        self.can.tp.process()
                        if self.can.tp.available():
                            stale = self.can.tp.recv()
                            self._log(f"Flushed stale: {bytes(stale).hex()}", "INFO")
                        time.sleep(0.001)
            except: pass

            self._ota_update("Re-entering session…", 6)
            self._uds(bytes([0x10, 0x02]))
            self._log("Session confirmed ✓", "OK")
            time.sleep(0.1)

            if self.ota_abort: raise RuntimeError("Aborted by user")

            # ── Security Access ───────────────────────────────────────────
            self._set_step(3)
            self._ota_update("Security Access…", 8)
            dev = self.dev_mode.get()
            sl  = 0x11 if dev else 0x01
            resp = self._uds(bytes([0x27, sl]))
            seed = resp[2:6]
            if seed != bytes(4):
                dkey = xtea_derive_key(seed, key)
                self._uds(bytes([0x27, sl + 1]) + dkey)
                self._log(f"Seed: {self._hex(seed)}  Key: {self._hex(dkey)}", "INFO")
            self._log("Security unlocked ✓", "OK")
            if dev:
                self._log("⚠ Developer mode — DTC C10007 will be logged by ECU", "WARN")

            if self.ota_abort: raise RuntimeError("Aborted by user")

            # ── Erase ─────────────────────────────────────────────────────
            self._set_step(4)
            self._ota_update("Erasing app slot…", 12)
            self._log(f"Erasing — model=0x{fw_model:04X} "
                      f"ver={fw_ver[0]}.{fw_ver[1]}.{fw_ver[2]}", "WARN")
            erase_cmd = bytes([
                0x31, 0x01, 0xFF, 0x00,
                (fw_model >> 8) & 0xFF, fw_model & 0xFF,
                fw_ver[0], fw_ver[1], fw_ver[2]
            ])
            self._uds(erase_cmd, timeout=60.0)
            self._log("Erase complete ✓  BL config saved — model locked", "OK")

            if self.ota_abort: raise RuntimeError("Aborted by user")

            # ── Request Download ──────────────────────────────────────────
            self._set_step(5)
            self._ota_update("Request Download…", 16)
            addr_b = struct.pack(">I", 0x00014000)
            size_b = struct.pack(">I", len(encrypted))
            req_dl = bytes([0x34, 0x11, 0x44]) + addr_b + size_b + nonce
            resp   = self._uds(req_dl)
            max_blk = resp[2] if len(resp) >= 3 else 128
            self._log(f"Download accepted ✓  maxBlock={max_blk} bytes", "OK")

            # ── Transfer Data ─────────────────────────────────────────────
            self._set_step(6)
            total    = len(encrypted)
            offset   = 0
            bsn      = 1
            tp_last  = time.time()

            while offset < total:
                if self.ota_abort: raise RuntimeError("Aborted by user")
                chunk   = encrypted[offset: offset + max_blk]
                self._uds(bytes([0x36, bsn]) + chunk, timeout=15.0)
                offset += len(chunk)
                bsn     = (bsn + 1) & 0xFF
                if bsn == 0: bsn = 1
                pct = 18 + int(74 * offset / total)
                self._ota_update(f"Transferring…  {offset:,} / {total:,} bytes",
                                 pct, f"{offset:,} / {total:,} B")
                if (time.time() - tp_last) >= 1.5:
                    try: self._uds(bytes([0x3E, 0x80]), timeout=0.5)
                    except: pass
                    tp_last = time.time()

            self._log("Transfer complete ✓", "OK")
            if self.ota_abort: raise RuntimeError("Aborted by user")

            # ── Transfer Exit ─────────────────────────────────────────────
            self._set_step(7)
            self._ota_update("TransferExit — decrypt + verify (up to 3 min)…", 92)
            self._log("TransferExit — ECU decrypting + verifying…", "WARN")
            self._log("  DTC C10008 written by ECU at start of verify", "INFO")
            self._uds(bytes([0x37]), timeout=300.0)
            self._log("TransferExit OK ✓  DTC C10008 cleared by ECU on success", "OK")

            # ── CRC Verify ────────────────────────────────────────────────
            self._set_step(8)
            self._ota_update("Verifying CRC…", 94)
            resp = self._uds(bytes([0x31, 0x01, 0xFF, 0x01]), timeout=30.0)
            ok   = resp[4] if len(resp) >= 5 else 0
            if ok != 0x01:
                raise RuntimeError("ECU CRC verify FAILED — flash may be corrupt")
            self._log("CRC verify PASS ✓", "OK")

            # ── Fingerprint ───────────────────────────────────────────────
            self._set_step(9)
            self._ota_update("Writing fingerprint…", 96)
            sn_raw  = self.sn_var.get().encode("ascii")[:10].ljust(10)
            ver_raw = bytes([fw_ver[0], fw_ver[1], fw_ver[2], 0x00])
            fp_pl   = bytes([0x2E, 0xF1, 0x5B])
            fp_pl  += struct.pack(">I", int(time.time()))
            fp_pl  += sn_raw + ver_raw
            self._uds(fp_pl)
            self._log(f"Fingerprint written ✓  "
                      f"(ver={fw_ver[0]}.{fw_ver[1]}.{fw_ver[2]}  "
                      f"station={self.sn_var.get()})", "OK")

            # ── ECU Reset ─────────────────────────────────────────────────
            self._set_step(10)
            self._ota_update("Resetting ECU…", 99)
            try: self._uds(bytes([0x11, 0x01]))
            except TimeoutError: pass
            self._log("ECU Reset sent ✓", "OK")

            # ── Done ──────────────────────────────────────────────────────
            self._ota_update("OTA FLASH COMPLETE ✓", 100,
                             f"{total:,} / {total:,} B")
            for dot in self.step_dots:
                self.after(0, dot.config, {"fg": C_GREEN})
            self._log("=" * 60, "HEAD")
            self._log("OTA FLASH COMPLETE ✓  App is starting…", "OK")
            self._log(f"  Model:   {MODEL_BY_ID.get(fw_model, '?')}", "OK")
            self._log(f"  Version: v{fw_ver[0]}.{fw_ver[1]}.{fw_ver[2]}", "OK")
            self._log(f"  Station: {self.sn_var.get()}", "OK")
            self._log("=" * 60, "HEAD")
            self.after(0, self.ota_progress.configure, {"style": "OK.Horizontal.TProgressbar"})

        except Exception as e:
            self._log(f"OTA FAILED: {e}", "ERR")
            self._ota_update(f"FAILED: {e}", 0)
            self.after(0, self.ota_progress.configure, {"style": "ERR.Horizontal.TProgressbar"})
        finally:
            self.after(0, self.btn_ota.config, {"state": tk.NORMAL})

    # ──────────────────────────────────────────────────────────────────────────
    # CONFIG SAVE / LOAD
    # ──────────────────────────────────────────────────────────────────────────

    def _save_config(self):
        try:
            cfg = {
                "interface": self.iface_var.get(),
                "channel":   self.chan_var.get(),
                "bitrate":   self.brate_var.get(),
                "rxid":      self.rxid_var.get(),
                "txid":      self.txid_var.get(),
            }
            with open(self.config_file, "w") as f:
                json.dump(cfg, f)
        except: pass

    def _load_config(self):
        try:
            with open(self.config_file) as f:
                cfg = json.load(f)
            self.iface_var.set(cfg.get("interface", "pcan"))
            self.chan_var.set(  cfg.get("channel",   "PCAN_USBBUS1"))
            self.brate_var.set(cfg.get("bitrate",   "250000"))
            self.rxid_var.set( cfg.get("rxid",       "0x7E8"))
            self.txid_var.set( cfg.get("txid",       "0x7E0"))
        except: pass

    def _on_close(self):
        self.ota_abort = True
        self._save_config()
        try: self.can.disconnect()
        except: pass
        self.destroy()

# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = NexaBootTester()
    app.mainloop()
