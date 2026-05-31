#!/usr/bin/env python3
"""
NexaBoot Tester v2.2 — Next Generation Secure Bootloader Validation Tool
S32K144 | ISO 14229 UDS | ISO 15765-2 | Dual Theme
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading, struct, time, zlib, os, queue, json, socket, math

APP_VERSION = "v2.2"

VEHICLE_MODELS = {
    "9M Bus":        0x0001,
    "12M City Bus":  0x0002,
    "12M Staff Bus": 0x0003,
    "4x2 TT":        0x0004,
    "6x4 TT":        0x0005,
}

NRC_INFO = {
    0x10: ("generalReject",             "ECU rejected the request."),
    0x11: ("serviceNotSupported",       "Service not supported by ECU."),
    0x12: ("subFunctionNotSupported",   "Sub-function invalid. Check session."),
    0x13: ("incorrectMessageLength",    "Message length wrong. Check payload."),
    0x22: ("conditionsNotCorrect",      "Wrong session or OTA state. Check sequence."),
    0x24: ("requestSequenceError",      "Out of order: erase→download→transfer→exit."),
    0x31: ("requestOutOfRange",         "Model mismatch, version downgrade, or unknown DID."),
    0x33: ("securityAccessDenied",      "Not unlocked. Call 0x27 01/02 first."),
    0x35: ("invalidKey",                "Wrong key. Check AES key bytes."),
    0x36: ("exceededAttempts",          "3 wrong keys — ECU locked 10 seconds."),
    0x70: ("uploadDownloadNotAccepted", "ECDSA signature failed."),
    0x72: ("generalProgrammingFailure", "Decompress or flash write failed."),
    0x73: ("wrongBlockSequence",        "Block sequence wrong. Restart download."),
    0x78: ("requestPending",            "ECU busy — keep waiting."),
    0x7F: ("serviceNotSupportedInSession", "Service not allowed in session."),
}

DTC_INFO = {
    0xC10001: ("FLASH_ERASE_FAIL",   "Flash erase hardware failure.",                 "red"),
    0xC10002: ("FLASH_PROGRAM_FAIL", "Flash write hardware failure.",                 "red"),
    0xC10003: ("CRC_MISMATCH",       "App CRC mismatch — corrupted or partial flash.","red"),
    0xC10004: ("SA_LOCKOUT",         "Security locked — 3 wrong keys.",               "amber"),
    0xC10005: ("META_WRITE_FAIL",    "Metadata write failed after OTA.",              "red"),
    0xC10006: ("CRYPTO_FAIL",        "ECDSA or AES operation failed.",                "red"),
    0xC10007: ("DEV_MODE_USED",      "Developer bypass activated — audit trail.",      "blue"),
    0xC10008: ("OTA_INTERRUPTED",    "OTA interrupted: power cut, abort or timeout.", "amber"),
    0xC10009: ("INVALID_SEQUENCE",   "UDS services called out of order.",             "amber"),
    0xC1000A: ("COMP_STORE_FAIL",    "Compressed store write fail in transfer.",      "red"),
}

# ══════════════════════════════════════════════════════════════════════════════
# THEMES
# ══════════════════════════════════════════════════════════════════════════════
DARK = {
    "name":"dark",
    "BG":"#0B0F1A","BG2":"#111827","BG3":"#1A2235","BG4":"#1E2A40","BG5":"#0D1220",
    "PANEL":"#0F1623","CARD":"#141E30","CARD2":"#1C2840",
    "BLUE":"#3B82F6","BLUE2":"#60A5FA","BLUE_DIM":"#1D4ED8",
    "CYAN":"#22D3EE","GREEN":"#22C55E","GREEN2":"#4ADE80",
    "RED":"#EF4444","RED2":"#F87171","AMBER":"#F59E0B","PURPLE":"#A855F7",
    "FG":"#F1F5F9","FG2":"#94A3B8","FG3":"#475569","FG4":"#1E293B",
    "BORDER":"#1E3A5F","BORDER2":"#0F2040","SEP":"#1A2E50",
    "HL":"#2563EB","HL2":"#1D4ED8",
    "BTN_BG":"#1E3A5F","BTN_FG":"#FFFFFF",
    "INPUT_BG":"#0D1525","INPUT_FG":"#E2E8F0",
    "TAG_BG":"#162032","TAG_BORDER":"#1E3A5F",
    "ACCENT_LINE":"#3B82F6",
    "LOG_BG":"#080C14",
    "SHADOW":"#050810",
}
LIGHT = {
    "name":"light",
    "BG":"#F0F4FA","BG2":"#FFFFFF","BG3":"#F8FAFC","BG4":"#EEF2F8","BG5":"#E2EAF4",
    "PANEL":"#FFFFFF","CARD":"#FFFFFF","CARD2":"#F0F6FF",
    "BLUE":"#2563EB","BLUE2":"#3B82F6","BLUE_DIM":"#1D4ED8",
    "CYAN":"#0891B2","GREEN":"#16A34A","GREEN2":"#22C55E",
    "RED":"#DC2626","RED2":"#EF4444","AMBER":"#D97706","PURPLE":"#7C3AED",
    "FG":"#0F172A","FG2":"#475569","FG3":"#94A3B8","FG4":"#CBD5E1",
    "BORDER":"#CBD5E1","BORDER2":"#E2E8F0","SEP":"#E2E8F0",
    "HL":"#2563EB","HL2":"#1D4ED8",
    "BTN_BG":"#2563EB","BTN_FG":"#FFFFFF",
    "INPUT_BG":"#FFFFFF","INPUT_FG":"#0F172A",
    "TAG_BG":"#EFF6FF","TAG_BORDER":"#BFDBFE",
    "ACCENT_LINE":"#2563EB",
    "LOG_BG":"#F8FAFC",
    "SHADOW":"#C8D4E8",
}

T = dict(DARK)

FUI   = ("Segoe UI", 10)
FUI_S = ("Segoe UI",  9)
FUI_B = ("Segoe UI", 10, "bold")
FUI_H = ("Segoe UI", 11, "bold")
FMONO = ("Consolas", 10)
FMONO_S=("Consolas",  9)
FMONO_B=("Consolas", 10,"bold")
FBIG  = ("Segoe UI", 18, "bold")

# ══════════════════════════════════════════════════════════════════════════════
# CUSTOM WIDGETS
# ══════════════════════════════════════════════════════════════════════════════

class FlatButton(tk.Frame):
    """Clean flat button with hover and press states"""
    def __init__(self, parent, text, command, color=None,
                 width=120, height=32, icon="", **kw):
        super().__init__(parent, bg=parent.cget("bg"), **kw)
        self._color   = color or T["BLUE"]
        self._text    = (icon+"  "+text) if icon else text
        self._cmd     = command
        # FIX #1: use _bw/_bh so _draw() can read them without AttributeError
        self._bw      = width
        self._bh      = height
        self._pressed = False
        self._hover   = False

        self.canvas = tk.Canvas(self, width=width, height=height,
                                highlightthickness=0, bd=0,
                                bg=parent.cget("bg"), cursor="hand2")
        self.canvas.pack()
        self._draw()

        self.canvas.bind("<Enter>",          self._on_enter)
        self.canvas.bind("<Leave>",          self._on_leave)
        self.canvas.bind("<ButtonPress-1>",  self._on_press)
        self.canvas.bind("<ButtonRelease-1>",self._on_rel)

    def _r2h(self, r,g,b):
        return f"#{max(0,min(255,r)):02X}{max(0,min(255,g)):02X}{max(0,min(255,b)):02X}"
    def _h2r(self, h):
        h=h.lstrip('#')
        return int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)
    def _lighten(self,c,a=25):
        r,g,b=self._h2r(c); return self._r2h(r+a,g+a,b+a)
    def _darken(self,c,a=25):
        r,g,b=self._h2r(c); return self._r2h(r-a,g-a,b-a)
    def _alpha(self,c,a=0.15):
        r,g,b=self._h2r(c)
        br,bg_,bb=self._h2r(T["BG2"])
        return self._r2h(int(br+(r-br)*a),int(bg_+(g-bg_)*a),int(bb+(b-bb)*a))

    def _draw(self):
        self.canvas.delete("all")
        W,H = self._bw, self._bh
        r   = H//2
        col = self._color

        if self._pressed:
            bg  = self._darken(col, 30)
            fg  = "#FFFFFF"
            brd = self._darken(col, 40)
        elif self._hover:
            bg  = self._lighten(col, 15)
            fg  = "#FFFFFF"
            brd = self._lighten(col, 30)
        else:
            bg  = col
            fg  = "#FFFFFF"
            brd = self._darken(col, 10)

        # Rounded rect
        pts = [r,0, W-r,0, W,r, W,H-r, W-r,H, r,H, 0,H-r, 0,r]
        self.canvas.create_polygon(pts, smooth=True, fill=bg, outline=brd, width=1)

        # Subtle top highlight
        hl = self._lighten(bg, 40)
        self.canvas.create_line(r, 1, W-r, 1, fill=hl, width=1)

        # Text
        self.canvas.create_text(W//2+1, H//2+1, text=self._text,
                                 fill=self._darken(fg,60),
                                 font=FUI_B, anchor=tk.CENTER)
        self.canvas.create_text(W//2, H//2, text=self._text,
                                 fill=fg, font=FUI_B, anchor=tk.CENTER)

    def _on_enter(self,e): self._hover=True;  self._draw()
    def _on_leave(self,e): self._hover=False; self._draw()
    def _on_press(self,e): self._pressed=True; self._draw()
    def _on_rel(self,e):
        self._pressed=False; self._hover=False; self._draw()
        if self._cmd: self._cmd()

    def set_color(self, col):
        self._color = col; self._draw()

    def set_bg(self, bg):
        self.config(bg=bg)
        self.canvas.config(bg=bg)
        self._draw()


class IconButton(tk.Frame):
    """Small icon-style button"""
    def __init__(self, parent, text, command, color=None,
                 width=100, height=28, **kw):
        super().__init__(parent, bg=parent.cget("bg"), **kw)
        self._color   = color or T["BLUE"]
        self._text    = text
        self._cmd     = command
        # FIX #1: use _bw/_bh so _draw() can read them without AttributeError
        self._bw      = width
        self._bh      = height
        self._hover   = False

        self.canvas = tk.Canvas(self, width=width, height=height,
                                highlightthickness=0, bd=0,
                                bg=parent.cget("bg"), cursor="hand2")
        self.canvas.pack()
        self._draw()
        self.canvas.bind("<Enter>",          lambda e: (setattr(self,'_hover',True),  self._draw()))
        self.canvas.bind("<Leave>",          lambda e: (setattr(self,'_hover',False), self._draw()))
        self.canvas.bind("<ButtonRelease-1>",lambda e: self._cmd() if self._cmd else None)

    def _r2h(self,r,g,b): return f"#{max(0,min(255,r)):02X}{max(0,min(255,g)):02X}{max(0,min(255,b)):02X}"
    def _h2r(self,h):
        h=h.lstrip('#'); return int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)
    def _lighten(self,c,a=20):
        r,g,b=self._h2r(c); return self._r2h(r+a,g+a,b+a)
    def _alpha(self,c,a=0.12):
        r,g,b=self._h2r(c)
        br,bg_,bb=self._h2r(T.get("BG3","#111827"))
        return self._r2h(int(br+(r-br)*a),int(bg_+(g-bg_)*a),int(bb+(b-bb)*a))

    def _draw(self):
        self.canvas.delete("all")
        W,H = self._bw,self._bh
        r   = 5
        bg  = self._alpha(self._color, 0.25 if self._hover else 0.12)
        brd = self._alpha(self._color, 0.5)
        pts = [r,0, W-r,0, W,r, W,H-r, W-r,H, r,H, 0,H-r, 0,r]
        self.canvas.create_polygon(pts, smooth=True, fill=bg, outline=brd, width=1)
        self.canvas.create_text(W//2, H//2, text=self._text,
                                 fill=self._color if not self._hover else self._lighten(self._color),
                                 font=FUI_S, anchor=tk.CENTER)

    def set_bg(self,bg):
        self.config(bg=bg); self.canvas.config(bg=bg); self._draw()


class StatusDot(tk.Canvas):
    """Animated status dot"""
    def __init__(self, parent, **kw):
        super().__init__(parent, width=160, height=32,
                         highlightthickness=0, bd=0,
                         bg=parent.cget("bg"), **kw)
        self._connected = False
        self._draw()

    def set_status(self, connected):
        self._connected = connected
        self._draw()

    def _draw(self):
        self.delete("all")
        col  = T["GREEN"] if self._connected else T["RED2"]
        text = "CONNECTED" if self._connected else "DISCONNECTED"
        # Glow rings
        for i,a in [(8,0.15),(6,0.25),(4,0.5)]:
            r2,g2,b2 = int(col[1:3],16),int(col[3:5],16),int(col[5:7],16)
            br,bg_,bb_ = int(T["BG2"][1:3],16),int(T["BG2"][3:5],16),int(T["BG2"][5:7],16)
            gc = "#{:02X}{:02X}{:02X}".format(
                int(br+(r2-br)*a),int(bg_+(g2-bg_)*a),int(bb_+(b2-bb_)*a))
            self.create_oval(8-i,8-i,8+i+8,8+i+8, fill=gc, outline="")
        self.create_oval(10,8,24,22, fill=col, outline="")
        self.create_oval(12,9,17,14, fill="white" if self._connected else "#FCA5A5", outline="")
        self.create_text(32, 16, text=text, fill=col,
                         font=("Consolas",9,"bold"), anchor=tk.W)

    def set_bg(self,bg):
        self.config(bg=bg); self._draw()


class InfoChip(tk.Canvas):
    """Clean info chip with label + value"""
    def __init__(self, parent, label, value="—", color=None, chip_width=112, **kw):
        super().__init__(parent, width=chip_width, height=48,
                         highlightthickness=0, bd=0,
                         bg=parent.cget("bg"), **kw)
        self._label  = label
        self._value  = value
        self._color  = color or T["BLUE"]
        self._cw     = chip_width   # use _cw not _w (conflicts with tk internal)
        self._draw()

    def set_value(self, v):
        self._value = str(v); self._draw()

    def set_color(self, c):
        self._color = c; self._draw()

    def _draw(self):
        self.delete("all")
        W,H = self._cw, 48
        r   = 6
        col = self._color

        # Background
        pts = [r,1, W-r,1, W-1,r, W-1,H-r, W-r,H-1, r,H-1, 1,H-r, 1,r]
        self.create_polygon(pts, smooth=True, fill=T["BG3"], outline=T["BORDER"])

        # Color accent bar top
        bar_pts = [r+1,1, W-r-1,1, W-r-1,5, r+1,5]
        self.create_polygon(bar_pts, fill=col, outline="")

        # Label
        self.create_text(W//2, 18, text=self._label,
                         fill=T["FG3"], font=("Segoe UI",7,"bold"),
                         anchor=tk.CENTER)
        # Value
        self.create_text(W//2, 34, text=self._value,
                         fill=col, font=("Consolas",9,"bold"),
                         anchor=tk.CENTER)

    def set_bg(self,bg):
        self.config(bg=bg); self._draw()


class StepBar(tk.Canvas):
    """Clean horizontal step progress bar"""
    def __init__(self, parent, labels, **kw):
        n = len(labels)
        W = max(700, n*68)
        super().__init__(parent, width=W, height=52,
                         highlightthickness=0, bd=0,
                         bg=T["CARD"], **kw)
        self._labels  = labels
        self._cnt     = n
        self._sw      = W
        self._current = -1
        self._draw()

    def set_step(self, s): self._current = s; self._draw()
    def reset(self):        self._current = -1; self._draw()

    def _draw(self):
        self.delete("all")
        W,H  = self._sw, 52
        sw   = W // self._cnt
        cy   = 22

        for i, lbl in enumerate(self._labels):
            cx   = i*sw + sw//2
            r    = 11
            done = i < self._current
            curr = i == self._current

            # Connector line
            if i < self._cnt-1:
                lx  = cx+r+2
                rx  = (i+1)*sw+sw//2-r-2
                lc  = T["GREEN"] if done else T["FG4"]
                self.create_line(lx, cy, rx, cy, fill=lc, width=2)

            # Circle
            if done:
                fc, oc, tc = T["GREEN"],    T["GREEN2"],  "white"
            elif curr:
                fc, oc, tc = T["BLUE"],     T["BLUE2"],   "white"
            else:
                fc, oc, tc = T["BG4"],      T["FG4"],     T["FG3"]

            # Shadow
            self.create_oval(cx-r+1,cy-r+1,cx+r+1,cy+r+1, fill=T["SHADOW"], outline="")
            # Fill
            self.create_oval(cx-r, cy-r, cx+r, cy+r, fill=fc, outline=oc, width=1)

            # Icon
            icon = "✓" if done else str(i+1)
            self.create_text(cx, cy, text=icon,
                             fill=tc, font=("Segoe UI",8,"bold"))

            # Label
            lc2 = T["GREEN"] if done else (T["BLUE2"] if curr else T["FG3"])
            self.create_text(cx, cy+r+10, text=lbl,
                             fill=lc2, font=("Segoe UI",7))

    def set_bg(self,bg):
        self.config(bg=bg); self._draw()

# ══════════════════════════════════════════════════════════════════════════════
# CAN BUS
# ══════════════════════════════════════════════════════════════════════════════
class CANBus:
    def __init__(self):
        self.bus=None; self.tp=None
        self.lock=threading.Lock(); self.log_q=None

    def connect(self,interface,channel,bitrate=250000,rx_id=0x7E8,tx_id=0x7E0):
        import can,isotp
        self.bus=(can.interface.Bus(interface="pcan",channel=channel,bitrate=bitrate,fd=False)
                  if interface=="pcan" else
                  can.interface.Bus(interface=interface,channel=channel,bitrate=bitrate))
        addr=isotp.Address(isotp.AddressingMode.Normal_11bits,rxid=rx_id,txid=tx_id)
        self.tp=isotp.CanStack(self.bus,address=addr)
        if hasattr(self.tp,'set_sleep_time'): self.tp.set_sleep_time(0.001)

    def disconnect(self):
        try:
            if self.tp: self.tp=None
        except: pass
        try:
            if self.bus: self.bus.shutdown(); self.bus=None
        except: pass

    def request(self,data,timeout=10.0):
        with self.lock:
            self.tp.send(data)
            dl=time.time()+5
            while time.time()<dl:
                self.tp.process()
                if hasattr(self.tp,'transmitting'):
                    if not self.tp.transmitting(): break
                else: time.sleep(0.05); break
                time.sleep(0.001)
            dl=time.time()+timeout; sc=0
            while time.time()<dl:
                self.tp.process()
                if self.tp.available():
                    resp=bytes(self.tp.recv())
                    if len(resp)<1: continue
                    if resp[0]==0x7F and len(resp)>=3 and resp[2]==0x78:
                        if self.log_q: self.log_q.put(("[0x78] ECU busy…\n","WARN"))
                        dl=min(time.time()+timeout,time.time()+300); continue
                    ex=data[0]+0x40
                    if resp[0]!=ex and resp[0]!=0x7F:
                        sc+=1
                        if sc<=3: continue
                        raise RuntimeError(f"Unexpected 0x{resp[0]:02X}")
                    if resp[0]==0x7F:
                        nrc=resp[2] if len(resp)>=3 else 0
                        sid=resp[1] if len(resp)>=2 else 0
                        n,d=NRC_INFO.get(nrc,("unknown","Unknown NRC"))
                        raise RuntimeError(f"NRC 0x{nrc:02X} ({n})\n  SID 0x{sid:02X} | {d}")
                    return resp
                time.sleep(0.001)
            raise TimeoutError("Response timeout")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════════════════════════
class NexaBootTester(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"NexaBoot Tester  {APP_VERSION}")
        self.geometry("1320x900")
        self.minsize(1100,760)
        self.configure(bg=T["BG"])
        self.resizable(True,True)

        self.can=CANBus(); self.q=queue.Queue(); self.can.log_q=self.q
        self.connected=False; self.aes_key=None; self.ota_abort=False
        self._theme="dark"

        for name,val in [
            ("model_var","9M Bus"),("iface_var","pcan"),("chan_var","PCAN_USBBUS1"),
            ("brate_var","250000"),("rxid_var","0x7E8"),("txid_var","0x7E0"),
            ("key_var","00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F"),
            ("fw_path",""),("sw_ver_var","—"),("sn_var",socket.gethostname()[:10]),
            ("req_id_var","0x7E0"),("resp_id_var","0x7E8"),("app_addr_var","0x00014000"),
        ]:
            setattr(self,name,tk.StringVar(value=val))
        self.dev_mode=tk.BooleanVar(value=False)

        self.config_file=os.path.join(os.path.expanduser("~"),".nexaboot2.json")
        self._build(); self._poll_q()
        self._load_cfg(); self.protocol("WM_DELETE_WINDOW",self._on_close)

    # ── THEME ─────────────────────────────────────────────────────────────────
    def _toggle_theme(self):
        global T
        self._theme = "light" if self._theme=="dark" else "dark"
        T.clear(); T.update(LIGHT if self._theme=="light" else DARK)
        for w in self.winfo_children(): w.destroy()
        self.configure(bg=T["BG"])
        # FIX #10: don't call _load_cfg here — it would overwrite any unsaved
        # field edits the user has made since the last connect/save.
        self._build(); self._poll_q()

    # ── BUILD ─────────────────────────────────────────────────────────────────
    def _build(self):
        self._styles()
        self._titlebar()
        tk.Frame(self,bg=T["SEP"],height=1).pack(fill=tk.X)
        self._body()

    def _styles(self):
        s=ttk.Style(self); s.theme_use("clam")
        s.configure("TNotebook",       background=T["BG"],  borderwidth=0)
        s.configure("TNotebook.Tab",   background=T["BG3"], foreground=T["FG2"],
                    padding=[14,7],    font=FUI_B,           borderwidth=0)
        s.map("TNotebook.Tab",
              background=[("selected",T["BG2"])],
              foreground=[("selected",T["BLUE"])])
        s.configure("TFrame",          background=T["BG"])
        s.configure("TPanedwindow",    background=T["BG"])
        s.configure("TScrollbar",      background=T["BG3"], troughcolor=T["BG"],
                    borderwidth=0,     arrowcolor=T["FG3"])
        for n,c in [("Blue",T["BLUE"]),("Green",T["GREEN"]),("Red",T["RED"])]:
            s.configure(f"{n}.HP.Horizontal.TProgressbar",
                        troughcolor=T["BG4"], background=c, thickness=16,
                        borderwidth=0)
        s.configure("TCombobox", fieldbackground=T["INPUT_BG"],
                    background=T["INPUT_BG"], foreground=T["FG"],
                    selectbackground=T["BG4"], arrowcolor=T["BLUE"],
                    borderwidth=1, relief="flat")
        s.map("TCombobox",
              fieldbackground=[("readonly",T["INPUT_BG"])],
              selectbackground=[("readonly",T["BG4"])],
              selectforeground=[("readonly",T["FG"])])

    # ── TITLE BAR ─────────────────────────────────────────────────────────────
    def _titlebar(self):
        bar=tk.Frame(self,bg=T["BG2"],height=62)
        bar.pack(fill=tk.X); bar.pack_propagate(False)

        # Accent line at top
        al=tk.Canvas(bar,height=3,bg=T["BG2"],highlightthickness=0)
        al.place(x=0,y=0,relwidth=1)
        def _gl(e=None):
            al.delete("all"); W=al.winfo_width() or 1320
            cols=[(0x3B,0x82,0xF6),(0x22,0xD3,0xEE),(0x22,0xC5,0x5E)]
            segs=len(cols)-1
            for i in range(W):
                t=i/W; seg=min(int(t*segs),segs-1); lt=t*segs-seg
                r1,g1,b1=cols[seg]; r2,g2,b2=cols[seg+1]
                c=f"#{int(r1+(r2-r1)*lt):02X}{int(g1+(g2-g1)*lt):02X}{int(b1+(b2-b1)*lt):02X}"
                al.create_line(i,0,i,3,fill=c)
        al.bind("<Configure>",_gl); self.after(50,_gl)

        # Logo
        lf=tk.Frame(bar,bg=T["BG2"]); lf.pack(side=tk.LEFT,padx=16,pady=10)
        # Hex icon
        cv=tk.Canvas(lf,width=40,height=40,bg=T["BG2"],highlightthickness=0)
        cv.pack(side=tk.LEFT)
        def _hex():
            cx=cy=20; r=17
            pts=[cx+r*math.cos(math.radians(60*i-30)) for i in range(6)]
            all_pts=[]
            for i in range(6):
                a=math.radians(60*i-30)
                all_pts+=[cx+r*math.cos(a),cy+r*math.sin(a)]
            cv.create_polygon(all_pts,fill=T["BLUE"],outline=T["BLUE2"],width=1)
            # Inner gradient
            for ri in range(r-1,r-5,-1):
                t=(r-ri)/5
                rc=int(0x3B+(0x1D-0x3B)*t); gc=int(0x82+(0x4E-0x82)*t); bc=0xF6
                ipts=[]
                for i in range(6):
                    a=math.radians(60*i-30); ipts+=[cx+ri*math.cos(a),cy+ri*math.sin(a)]
                cv.create_polygon(ipts,fill=f"#{rc:02X}{gc:02X}{bc:02X}",outline="")
            cv.create_text(cx,cy,text="N",fill="white",font=("Segoe UI",14,"bold"))
        _hex()

        tf=tk.Frame(lf,bg=T["BG2"]); tf.pack(side=tk.LEFT,padx=(10,0))
        tk.Label(tf,text="NexaBoot",font=("Segoe UI",17,"bold"),
                 fg=T["FG"],bg=T["BG2"]).pack(anchor=tk.W)
        tk.Label(tf,text=f"Secure Bootloader Tester  {APP_VERSION}",
                 font=("Segoe UI",8),fg=T["FG2"],bg=T["BG2"]).pack(anchor=tk.W)

        # Separator
        tk.Frame(bar,bg=T["SEP"],width=1).pack(side=tk.LEFT,fill=tk.Y,pady=8,padx=12)

        # ECU chips
        cf=tk.Frame(bar,bg=T["BG2"]); cf.pack(side=tk.LEFT,pady=8)
        self.chip_bl    = InfoChip(cf,"BL VERSION","—",    T["BLUE"], chip_width=112)
        self.chip_sw    = InfoChip(cf,"SW VERSION","—",    T["GREEN"], chip_width=112)
        self.chip_model = InfoChip(cf,"MODEL",     "—",    T["CYAN"], chip_width=112)
        self.chip_dtc   = InfoChip(cf,"DTC STATUS","OK ✓", T["GREEN"], chip_width=112)
        for c in [self.chip_bl,self.chip_sw,self.chip_model,self.chip_dtc]:
            c.pack(side=tk.LEFT,padx=3)

        # Right controls
        rf=tk.Frame(bar,bg=T["BG2"]); rf.pack(side=tk.RIGHT,padx=14,pady=12)
        self.status_dot=StatusDot(rf); self.status_dot.pack(side=tk.RIGHT,padx=(8,0))
        # Theme btn
        theme_lbl="☀  Light" if self._theme=="dark" else "●  Dark"
        IconButton(rf,theme_lbl,self._toggle_theme,
                   T["FG3"],90,28).pack(side=tk.RIGHT,padx=4)

    # ── BODY ──────────────────────────────────────────────────────────────────
    def _body(self):
        pw=tk.PanedWindow(self,orient=tk.HORIZONTAL,bg=T["BG"],
                          sashwidth=4,sashrelief=tk.FLAT,sashpad=0)
        pw.pack(fill=tk.BOTH,expand=True)
        lf=tk.Frame(pw,bg=T["BG"])
        rf=tk.Frame(pw,bg=T["BG"])
        pw.add(lf,minsize=280); pw.add(rf,minsize=500)
        pw.paneconfig(lf,width=380); pw.paneconfig(rf,width=940)
        self._left(lf); self._right(rf)

    # ── LEFT PANEL ────────────────────────────────────────────────────────────
    def _left(self,parent):
        # Scrollable
        c=tk.Canvas(parent,bg=T["BG"],highlightthickness=0)
        sb=ttk.Scrollbar(parent,orient="vertical",command=c.yview)
        c.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT,fill=tk.Y)
        c.pack(side=tk.LEFT,fill=tk.BOTH,expand=True)
        inner=tk.Frame(c,bg=T["BG"])
        win=c.create_window((0,0),window=inner,anchor=tk.NW)
        inner.bind("<Configure>",lambda e: c.configure(scrollregion=c.bbox("all")))
        c.bind("<Configure>",lambda e: c.itemconfig(win,width=e.width))

        p=inner
        pad=dict(padx=10,pady=(0,2))

        # ── CAN Connection ────────────────────────────────────────────────────
        self._sec(p,"CAN CONNECTION")
        card=self._card(p)

        self._row(card,"Interface",
                  ttk.Combobox(card,textvariable=self.iface_var,
                               values=["pcan","socketcan","kvaser","vector","virtual"],
                               width=16,font=FMONO_S,state="readonly"))
        self._row(card,"Channel",   self._inp(card,self.chan_var,18))
        self._row(card,"Baud Rate",
                  ttk.Combobox(card,textvariable=self.brate_var,
                               values=["250000","500000","1000000"],
                               width=16,font=FMONO_S,state="readonly"))

        # RX/TX inline
        id_row=tk.Frame(card,bg=T["CARD"]); id_row.pack(fill=tk.X,padx=10,pady=3)
        for lbl,var,w in [("RX ID",self.rxid_var,9),(" TX ID",self.txid_var,9)]:
            tk.Label(id_row,text=lbl,fg=T["FG2"],bg=T["CARD"],
                     font=FUI_S).pack(side=tk.LEFT)
            self._inp(id_row,var,w).pack(side=tk.LEFT,padx=(2,6))

        # CONNECT / DISCONNECT buttons — large, clear, prominent
        br=tk.Frame(card,bg=T["CARD"]); br.pack(fill=tk.X,padx=10,pady=(8,10))
        self.btn_conn=FlatButton(br,"CONNECT",    self._connect,   T["GREEN"], 146,36)
        self.btn_disc=FlatButton(br,"DISCONNECT", self._disconnect,T["RED"],   146,36)
        self.btn_conn.pack(side=tk.LEFT)
        self.btn_disc.pack(side=tk.LEFT,padx=(6,0))
        # Fix background
        for b in [self.btn_conn,self.btn_disc]: b.set_bg(T["CARD"])

        # ── AES Key ───────────────────────────────────────────────────────────
        self._sec(p,"AES-128 KEY")
        kc=self._card(p)

        kr=tk.Frame(kc,bg=T["CARD"]); kr.pack(fill=tk.X,padx=10,pady=4)
        self.key_entry=tk.Entry(kr,textvariable=self.key_var,width=28,
                                 bg=T["INPUT_BG"],fg=T["AMBER"],
                                 insertbackground=T["BLUE"],
                                 relief=tk.FLAT,font=FMONO_S,show="*")
        self.key_entry.pack(side=tk.LEFT)
        self._key_vis=False
        def _tv():
            self._key_vis=not self._key_vis
            self.key_entry.config(show="" if self._key_vis else "*")
            vb.config(text="Hide" if self._key_vis else "Show")
        vb=tk.Button(kr,text="Show",command=_tv,
                     bg=T["BG4"],fg=T["FG2"],relief=tk.FLAT,
                     font=FUI_S,padx=6,cursor="hand2")
        vb.pack(side=tk.LEFT,padx=4)

        kr2=tk.Frame(kc,bg=T["CARD"]); kr2.pack(fill=tk.X,padx=10,pady=(0,8))
        IconButton(kr2,"Load .bin",self._load_key,T["CYAN"],84,26).pack(side=tk.LEFT)
        IconButton(kr2,"Set AES Key",self._set_key,T["BLUE"],96,26).pack(side=tk.LEFT,padx=6)
        self.key_lbl=tk.Label(kr2,text="⚠ not validated",
                               fg=T["AMBER"],bg=T["CARD"],font=FUI_S)
        self.key_lbl.pack(side=tk.LEFT,padx=4)

        # ── Address Config ────────────────────────────────────────────────────
        self._sec(p,"ADDRESS CONFIGURATION")
        ac=self._card(p)
        self._row(ac,"Request ID",  self._inp(ac,self.req_id_var, 12))
        self._row(ac,"Response ID", self._inp(ac,self.resp_id_var,12))
        self._row(ac,"App Address", self._inp(ac,self.app_addr_var,12))
        tk.Label(ac,text="  Changes apply on next CONNECT",
                 fg=T["FG3"],bg=T["CARD"],font=("Segoe UI",7),
                 anchor=tk.W).pack(fill=tk.X,padx=10,pady=(0,6))

        # ── Quick Actions ─────────────────────────────────────────────────────
        self._sec(p,"QUICK ACTIONS")
        qc=self._card(p)
        actions=[
            ("Tester Present",   self._tester_present,  T["BLUE"],  "3E 00"),
            ("Prog Session",     self._enter_prog,       T["BLUE"],  "10 02"),
            ("Security Access",  self._security_access,  T["GREEN"], "27 01/02"),
            ("Read BL Version",  self._read_bl_version,  T["CYAN"],  "22 F181"),
            ("Read SW Version",  self._read_sw_version,  T["CYAN"],  "22 F189"),
            ("Read Fingerprint", self._read_fingerprint, T["CYAN"],  "22 F15B"),
            ("Read DTC",         self._read_dtc,         T["AMBER"], "19 02 FF"),
            ("Clear DTC",        self._clear_dtc,        T["AMBER"], "14 FF FF FF"),
            ("Verify CRC",       self._verify_crc,       T["GREEN"], "31 FF01"),
            ("ECU Reset",        self._ecu_reset,        T["RED"],   "11 01"),
        ]
        for lbl,cmd,col,hint in actions:
            r=tk.Frame(qc,bg=T["CARD"]); r.pack(fill=tk.X,padx=2,pady=1)
            b=tk.Button(r,text=f"  {lbl}",command=cmd,
                        bg=T["CARD"],fg=col,
                        activebackground=T["BG4"],activeforeground=col,
                        relief=tk.FLAT,font=FUI_S,
                        padx=6,pady=4,cursor="hand2",anchor=tk.W)
            b.pack(side=tk.LEFT,fill=tk.X,expand=True)
            tk.Label(r,text=hint,fg=T["FG4"],bg=T["CARD"],
                     font=("Consolas",8)).pack(side=tk.RIGHT,padx=8)
        # Bottom padding
        tk.Frame(qc,bg=T["CARD"],height=6).pack()

    # ── RIGHT PANEL ───────────────────────────────────────────────────────────
    def _right(self,parent):
        nb=ttk.Notebook(parent)
        nb.pack(fill=tk.BOTH,expand=True,padx=6,pady=8)
        for title,fn in [
            ("  ⬡  OTA FLASH  ",    self._tab_ota),
            ("  ⬡  DTC MONITOR  ",  self._tab_dtc),
            ("  ⬡  FINGERPRINT  ",  self._tab_fp),
            ("  ⬡  RAW UDS  ",      self._tab_raw),
            ("  ⬡  LOG  ",          self._tab_log),
        ]:
            f=tk.Frame(nb,bg=T["BG"]); nb.add(f,text=title); fn(f)

    # ── OTA TAB ───────────────────────────────────────────────────────────────
    def _tab_ota(self,parent):
        p=tk.Frame(parent,bg=T["BG"]); p.pack(fill=tk.BOTH,expand=True,padx=12,pady=8)

        # File
        self._sec(p,"FIRMWARE FILE")
        fc=self._card(p)
        fr=tk.Frame(fc,bg=T["CARD"]); fr.pack(fill=tk.X,padx=10,pady=8)
        self.fw_entry=tk.Entry(fr,textvariable=self.fw_path,width=48,
                                bg=T["INPUT_BG"],fg=T["FG"],
                                insertbackground=T["BLUE"],
                                relief=tk.FLAT,font=FMONO_S)
        self.fw_entry.pack(side=tk.LEFT)
        IconButton(fr,"Browse…",self._browse_fw,T["CYAN"],76,28).pack(side=tk.LEFT,padx=8)

        # Info bar
        ib=tk.Frame(fc,bg=T["BG5"],height=24); ib.pack(fill=tk.X,padx=10,pady=(0,6))
        ib.pack_propagate(False)
        self.fw_info_lbl=tk.Label(ib,text="No file selected",
                                   fg=T["FG2"],bg=T["BG5"],
                                   font=FUI_S,anchor=tk.W)
        self.fw_info_lbl.pack(fill=tk.X,padx=8,pady=2)

        # Chips
        cr=tk.Frame(fc,bg=T["CARD"]); cr.pack(fill=tk.X,padx=10,pady=(0,8))
        self.fc_model  =InfoChip(cr,"MODEL",     "—",T["BLUE"], chip_width=112)
        self.fc_version=InfoChip(cr,"VERSION",   "—",T["GREEN"], chip_width=112)
        self.fc_size   =InfoChip(cr,"RAW SIZE",  "—",T["FG2"], chip_width=112)
        self.fc_comp   =InfoChip(cr,"COMPRESSED","—",T["CYAN"], chip_width=130)
        for c in [self.fc_model,self.fc_version,self.fc_size,self.fc_comp]:
            c.pack(side=tk.LEFT,padx=3)
            c.set_bg(T["CARD"])

        # Options
        self._sec(p,"OTA OPTIONS")
        oc=self._card(p)
        self._row(oc,"Vehicle Model",
                  ttk.Combobox(oc,textvariable=self.model_var,
                               values=list(VEHICLE_MODELS.keys()),
                               width=18,font=FMONO_S,state="readonly"))
        self._row(oc,"Station ID", self._inp(oc,self.sn_var,16))

        sv=tk.Frame(oc,bg=T["CARD"]); sv.pack(fill=tk.X,padx=10,pady=3)
        tk.Label(sv,text="SW Version",fg=T["FG2"],bg=T["CARD"],
                 font=FUI_S,width=12,anchor=tk.W).pack(side=tk.LEFT)
        tk.Label(sv,textvariable=self.sw_ver_var,
                 fg=T["BLUE2"],bg=T["CARD"],
                 font=("Consolas",10,"bold")).pack(side=tk.LEFT,padx=4)
        tk.Label(sv,text="← auto from file",
                 fg=T["FG3"],bg=T["CARD"],font=FUI_S).pack(side=tk.LEFT)

        dr=tk.Frame(oc,bg=T["CARD"]); dr.pack(fill=tk.X,padx=10,pady=(4,8))
        tk.Checkbutton(dr,
                        text="  Developer Mode  —  bypass model/version check (0x27 11/12)  →  DTC C10007 logged",
                        variable=self.dev_mode,fg=T["PURPLE"],bg=T["CARD"],
                        selectcolor=T["BG4"],activebackground=T["CARD"],
                        font=FUI_S).pack(side=tk.LEFT)

        # Progress
        self._sec(p,"OTA PROGRESS")
        pc=self._card(p)
        # FIX #8: added "Done" as 12th step so _step(11) is valid (index 0–11)
        self.step_bar=StepBar(pc,["Reset","Catch","Session","SA","Erase",
                                   "Download","Transfer","Verify","CRC","FP","Reset","Done"])
        self.step_bar.pack(fill=tk.X,padx=6,pady=8)
        self.step_bar.set_bg(T["CARD"])

        self.ota_lbl=tk.Label(pc,text="Ready — select firmware to begin",
                               fg=T["FG2"],bg=T["CARD"],font=FUI_S,anchor=tk.W)
        self.ota_lbl.pack(fill=tk.X,padx=12,pady=(0,4))

        self.ota_prog=ttk.Progressbar(pc,style="Blue.HP.Horizontal.TProgressbar",
                                       mode="determinate",maximum=100)
        self.ota_prog.pack(fill=tk.X,padx=10,pady=4)

        pr2=tk.Frame(pc,bg=T["CARD"]); pr2.pack(fill=tk.X,padx=12,pady=(0,10))
        self.ota_pct=tk.Label(pr2,text="0%",fg=T["BLUE"],bg=T["CARD"],
                               font=("Consolas",10,"bold"))
        self.ota_pct.pack(side=tk.LEFT)
        self.ota_bytes=tk.Label(pr2,text="",fg=T["FG2"],bg=T["CARD"],font=FMONO_S)
        self.ota_bytes.pack(side=tk.RIGHT)

        # Buttons
        br2=tk.Frame(p,bg=T["BG"]); br2.pack(fill=tk.X,pady=8)
        self.btn_ota=FlatButton(br2,"▶   START FULL OTA FLASH",
                                 self._start_ota,T["GREEN"],230,42)
        self.btn_ota.pack(side=tk.LEFT)
        FlatButton(br2,"■  ABORT",self._abort_ota,T["RED"],110,42).pack(
            side=tk.LEFT,padx=8)

    # ── DTC TAB ───────────────────────────────────────────────────────────────
    def _tab_dtc(self,parent):
        p=tk.Frame(parent,bg=T["BG"]); p.pack(fill=tk.BOTH,expand=True,padx=12,pady=8)
        self._sec(p,"DIAGNOSTIC TROUBLE CODES")

        br=tk.Frame(p,bg=T["BG"]); br.pack(fill=tk.X,pady=(0,8))
        FlatButton(br,"⟳  READ DTC", self._read_dtc_tab,T["AMBER"],130,34).pack(side=tk.LEFT)
        FlatButton(br,"✕  CLEAR DTC",self._clear_dtc,    T["RED"],  120,34).pack(side=tk.LEFT,padx=8)
        self.dtc_count_lbl=tk.Label(br,text="",fg=T["FG2"],bg=T["BG"],font=FUI)
        self.dtc_count_lbl.pack(side=tk.LEFT,padx=4)

        # Table header
        hf=tk.Frame(p,bg=T["BG3"]); hf.pack(fill=tk.X)
        for txt,w in [("DTC Code",12),("Name",22),("Status",8),("Description",40)]:
            tk.Label(hf,text=txt,fg=T["FG2"],bg=T["BG3"],
                     font=FUI_B,width=w,anchor=tk.W,padx=8,pady=5).pack(side=tk.LEFT)

        # List
        dtc_f=tk.Frame(p,bg=T["BG2"],
                        highlightbackground=T["BORDER"],highlightthickness=1)
        dtc_f.pack(fill=tk.BOTH,expand=True)
        self.dtc_list=tk.Frame(dtc_f,bg=T["BG2"]); self.dtc_list.pack(fill=tk.BOTH,expand=True)

        # Reference
        self._sec(p,"DTC REFERENCE")
        rc=self._card(p)
        rt=scrolledtext.ScrolledText(rc,height=7,bg=T["BG3"],fg=T["FG"],
                                      font=FMONO_S,relief=tk.FLAT)
        rt.pack(fill=tk.X,padx=6,pady=6)
        for code,(name,desc,ck) in DTC_INFO.items():
            rt.insert(tk.END,f"  C{code:06X}  ","code")
            rt.insert(tk.END,f"{name:<22}  ","name")
            rt.insert(tk.END,f"{desc}\n","desc")
        rt.tag_config("code",foreground=T["BLUE2"],font=FMONO_B)
        rt.tag_config("name",foreground=T["AMBER"])
        rt.tag_config("desc",foreground=T["FG2"])
        rt.config(state=tk.DISABLED)

    # ── FP TAB ────────────────────────────────────────────────────────────────
    def _tab_fp(self,parent):
        p=tk.Frame(parent,bg=T["BG"]); p.pack(fill=tk.BOTH,expand=True,padx=12,pady=8)

        self._sec(p,"READ FINGERPRINT")
        rc=self._card(p)
        self.fp_display=tk.Text(rc,height=7,bg=T["INPUT_BG"],fg=T["FG"],
                                 font=FMONO_S,relief=tk.FLAT,insertbackground=T["BLUE"])
        self.fp_display.pack(fill=tk.X,padx=8,pady=6)
        FlatButton(rc,"⟳  READ FINGERPRINT + SW VERSION",
                   self._read_fingerprint,T["BLUE"],260,32).pack(anchor=tk.W,padx=8,pady=(0,8))

        self._sec(p,"WRITE FINGERPRINT  (0x2E / F15B)")
        wc=self._card(p)
        self.fp_ts_var =tk.StringVar(value=str(int(time.time())))
        self.fp_sn_var =tk.StringVar(value=socket.gethostname()[:10])
        self.fp_ver_var=tk.StringVar(value="01 00 00 00")

        tr=tk.Frame(wc,bg=T["CARD"]); tr.pack(fill=tk.X,padx=10,pady=3)
        tk.Label(tr,text="Timestamp",fg=T["FG2"],bg=T["CARD"],
                 font=FUI_S,width=12,anchor=tk.W).pack(side=tk.LEFT)
        self._inp(tr,self.fp_ts_var,14).pack(side=tk.LEFT)
        tk.Button(tr,text="Now",command=lambda: self.fp_ts_var.set(str(int(time.time()))),
                  bg=T["BG4"],fg=T["FG2"],relief=tk.FLAT,
                  font=FUI_S,padx=6,cursor="hand2").pack(side=tk.LEFT,padx=6)

        self._row(wc,"Tester S/N", self._inp(wc,self.fp_sn_var, 14))
        self._row(wc,"SW Version", self._inp(wc,self.fp_ver_var,14))
        tk.Label(wc,text="  SW Version: BCD hex, 4 bytes  e.g. 01 02 00 00",
                 fg=T["FG3"],bg=T["CARD"],font=("Segoe UI",7),anchor=tk.W).pack(fill=tk.X)
        FlatButton(wc,"✎  WRITE FINGERPRINT",
                   self._write_fingerprint,T["GREEN"],200,34).pack(padx=10,pady=8,anchor=tk.W)

    # ── RAW TAB ───────────────────────────────────────────────────────────────
    def _tab_raw(self,parent):
        p=tk.Frame(parent,bg=T["BG"]); p.pack(fill=tk.BOTH,expand=True,padx=12,pady=8)

        self._sec(p,"CUSTOM UDS REQUEST")
        rc=self._card(p)
        tk.Label(rc,text="Hex bytes (space separated):",
                 fg=T["FG2"],bg=T["CARD"],font=FUI_S).pack(anchor=tk.W,padx=10,pady=(6,2))
        self.raw_entry=tk.Entry(rc,width=54,bg=T["INPUT_BG"],fg=T["AMBER"],
                                 insertbackground=T["BLUE"],relief=tk.FLAT,font=FMONO)
        self.raw_entry.pack(fill=tk.X,padx=10,pady=(0,6)); self.raw_entry.insert(0,"3E 00")
        rr=tk.Frame(rc,bg=T["CARD"]); rr.pack(fill=tk.X,padx=10,pady=(0,8))
        FlatButton(rr,"⬡  SEND",self._raw_send,T["BLUE"],100,30).pack(side=tk.LEFT)
        tk.Label(rr,text="Timeout (s):",fg=T["FG2"],bg=T["CARD"],font=FUI_S).pack(side=tk.LEFT,padx=8)
        self.raw_timeout=tk.StringVar(value="5")
        self._inp(rr,self.raw_timeout,5).pack(side=tk.LEFT)

        self._sec(p,"QUICK COMMANDS")
        qc=self._card(p)
        groups=[
            ("SESSION",  [("10 02","Prog Session"),("10 01","Default"),("3E 00","TesterPresent"),("11 01","ECU Reset")]),
            ("SECURITY", [("27 01","SA Seed Prod"),("27 11","SA Seed Dev")]),
            ("READ",     [("22 F1 81","BL Version"),("22 F1 89","SW Version"),("22 F1 5B","Fingerprint"),("19 02 FF","Read DTC"),("22 F1 86","Session")]),
            ("CONTROL",  [("14 FF FF FF","Clear DTC"),("31 01 FF 01","Verify CRC"),("28 03 01","CommCtrl Off"),("28 00 01","CommCtrl On"),("85 02","DTC Off"),("85 01","DTC On")]),
        ]
        for grp,cmds in groups:
            gf=tk.Frame(qc,bg=T["CARD"]); gf.pack(fill=tk.X,pady=(4,0),padx=8)
            tk.Label(gf,text=grp,fg=T["FG3"],bg=T["CARD"],
                     font=("Segoe UI",8,"bold"),width=9,anchor=tk.W).pack(side=tk.LEFT)
            for cmd,lbl in cmds:
                b=tk.Button(gf,text=lbl,command=lambda c=cmd: self._quick(c),
                            bg=T["BG4"],fg=T["FG2"],
                            activebackground=T["BG3"],activeforeground=T["BLUE"],
                            relief=tk.FLAT,font=FUI_S,padx=7,pady=3,cursor="hand2")
                b.pack(side=tk.LEFT,padx=2)
        tk.Frame(qc,bg=T["CARD"],height=6).pack()

        self._sec(p,"NRC REFERENCE")
        nrc_c=self._card(p)
        nt=scrolledtext.ScrolledText(nrc_c,height=8,bg=T["INPUT_BG"],fg=T["FG"],
                                      font=FMONO_S,relief=tk.FLAT)
        nt.pack(fill=tk.BOTH,padx=6,pady=6)
        for nrc,(name,desc) in NRC_INFO.items():
            nt.insert(tk.END,f"  0x{nrc:02X}  ","code")
            nt.insert(tk.END,f"{name:<35}  ","name")
            nt.insert(tk.END,f"{desc}\n","desc")
        nt.tag_config("code",foreground=T["RED2"],font=FMONO_B)
        nt.tag_config("name",foreground=T["AMBER"])
        nt.tag_config("desc",foreground=T["FG2"])
        nt.config(state=tk.DISABLED)

    # ── LOG TAB ───────────────────────────────────────────────────────────────
    def _tab_log(self,parent):
        ctrl=tk.Frame(parent,bg=T["BG"]); ctrl.pack(fill=tk.X,padx=10,pady=6)
        tk.Label(ctrl,text="UDS Transaction Log",fg=T["FG2"],bg=T["BG"],font=FUI_H).pack(side=tk.LEFT)
        IconButton(ctrl,"Save…",self._save_log,T["FG3"],70,26).pack(side=tk.RIGHT,padx=3)
        IconButton(ctrl,"Clear",self._clear_log,T["FG3"],70,26).pack(side=tk.RIGHT,padx=3)

        lo=tk.Frame(parent,bg=T["BG2"],
                    highlightbackground=T["BORDER"],highlightthickness=1)
        lo.pack(fill=tk.BOTH,expand=True,padx=10,pady=(0,8))
        self.log=scrolledtext.ScrolledText(lo,bg=T["LOG_BG"],fg=T["FG"],
                                            font=FMONO_S,relief=tk.FLAT,
                                            insertbackground=T["BLUE"],
                                            selectbackground=T["BG3"],wrap=tk.WORD)
        self.log.pack(fill=tk.BOTH,expand=True)
        for tag,col in [("TX",T["BLUE"]),("RX",T["GREEN2"]),
                         ("ERR",T["RED"]),("INFO",T["FG2"]),
                         ("OK",T["GREEN"]),("WARN",T["AMBER"]),
                         ("DTC",T["AMBER"]),("HEAD",T["BLUE2"])]:
            self.log.tag_config(tag,foreground=col)
        self.log.tag_config("HEAD",font=FMONO_B)

    # ── WIDGET HELPERS ────────────────────────────────────────────────────────
    def _sec(self,parent,text):
        f=tk.Frame(parent,bg=T["BG"]); f.pack(fill=tk.X,pady=(10,3))
        tk.Label(f,text=text,fg=T["BLUE"],bg=T["BG"],
                 font=("Consolas",9,"bold")).pack(side=tk.LEFT)
        tk.Frame(f,bg=T["SEP"],height=1).pack(side=tk.LEFT,fill=tk.X,expand=True,padx=(8,0))

    def _card(self,parent):
        outer=tk.Frame(parent,bg=T["BORDER"],bd=0)
        outer.pack(fill=tk.X,pady=(0,4))
        # Top accent line
        tk.Frame(outer,bg=T["ACCENT_LINE"],height=2).pack(fill=tk.X)
        inner=tk.Frame(outer,bg=T["CARD"],bd=0)
        inner.pack(fill=tk.X,padx=1,pady=(0,1))
        return inner

    def _row(self,parent,label,widget):
        r=tk.Frame(parent,bg=T["CARD"]); r.pack(fill=tk.X,padx=10,pady=3)
        tk.Label(r,text=label,fg=T["FG2"],bg=T["CARD"],
                 font=FUI_S,width=12,anchor=tk.W).pack(side=tk.LEFT)
        if widget: widget.pack(side=tk.LEFT,padx=4)
        return r

    def _inp(self,parent,var,width=16):
        return tk.Entry(parent,textvariable=var,width=width,
                        bg=T["INPUT_BG"],fg=T["FG"],
                        insertbackground=T["BLUE"],
                        relief=tk.FLAT,font=FMONO_S,
                        highlightthickness=1,
                        highlightbackground=T["BORDER"],
                        highlightcolor=T["BLUE"])

    # ── LOG HELPERS ───────────────────────────────────────────────────────────
    def _log(self,msg,tag="INFO"):
        self.q.put((f"[{time.strftime('%H:%M:%S')}]  {msg}\n",tag))

    def _poll_q(self):
        try:
            while True:
                msg,tag=self.q.get_nowait()
                self.log.insert(tk.END,msg,tag); self.log.see(tk.END)
        except queue.Empty: pass
        self.after(50,self._poll_q)

    def _clear_log(self): self.log.delete("1.0",tk.END)

    def _save_log(self):
        path=filedialog.asksaveasfilename(defaultextension=".txt",
                                          filetypes=[("Text","*.txt")])
        if path:
            # FIX #4: use context manager to avoid file handle leak
            with open(path,"w") as f: f.write(self.log.get("1.0",tk.END))
            self._log(f"Log saved: {path}","OK")

    def _hx(self,b): return " ".join(f"{x:02X}" for x in b)

    # ── CONNECTION ────────────────────────────────────────────────────────────
    def _connect(self):
        if self.connected: self._disconnect()
        try:
            rx=int(self.resp_id_var.get(),16)
            tx=int(self.req_id_var.get(),16)
            self.rxid_var.set(self.resp_id_var.get())
            self.txid_var.set(self.req_id_var.get())
            self._log(f"Connecting {self.iface_var.get()} / {self.chan_var.get()} "
                      f"@ {self.brate_var.get()}  RX=0x{rx:03X} TX=0x{tx:03X}…","INFO")
            self.can.connect(self.iface_var.get(),self.chan_var.get(),
                             int(self.brate_var.get()),rx,tx)
            self.connected=True
            self.status_dot.set_status(True)
            self._log("Connected ✓","OK"); self._save_cfg()
        except Exception as e:
            self._log(f"Connection failed: {e}","ERR")
            self.status_dot.set_status(False)

    def _disconnect(self):
        try: self.can.disconnect()
        except: pass
        self.connected=False; self.status_dot.set_status(False)
        self._log("Disconnected","INFO")

    # ── KEY ───────────────────────────────────────────────────────────────────
    def _set_key(self):
        try:
            raw=bytes.fromhex(self.key_var.get().replace(" ",""))
            if len(raw)!=16: raise ValueError("Key must be 16 bytes")
            self.aes_key=raw
            self.key_lbl.config(text="✓ 16 bytes valid",fg=T["GREEN"])
            return raw
        except Exception as e:
            self.key_lbl.config(text=f"✗ {e}",fg=T["RED"])
            return None

    def _get_key(self):
        # FIX #3: _get_key() updates UI — must only be called from the main thread.
        # All callers that start background threads now call this before Thread().
        key=self._set_key()
        if not key: messagebox.showerror("Key Error","Invalid AES key")
        return key

    def _load_key(self):
        path=filedialog.askopenfilename(filetypes=[("Binary","*.bin"),("All","*.*")])
        if not path: return
        # FIX #4: use context manager
        with open(path,"rb") as f: raw=f.read()
        if len(raw)!=16: messagebox.showerror("Key Error",f"File is {len(raw)}B — need 16"); return
        self.key_var.set(" ".join(f"{b:02X}" for b in raw))
        self.aes_key=raw; self.key_lbl.config(text="✓ loaded",fg=T["GREEN"])

    # ── UDS HELPERS ───────────────────────────────────────────────────────────
    def _run(self,fn):
        if not self.connected:
            messagebox.showwarning("Not Connected","Connect to CAN bus first."); return
        threading.Thread(target=fn,daemon=True).start()

    def _uds(self,data,timeout=10.0):
        self._log(f"TX: {self._hx(data)}","TX")
        resp=self.can.request(data,timeout)
        self._log(f"RX: {self._hx(resp)}","RX")
        return resp

    def _unlock(self,key,dev=False):
        self._uds(bytes([0x10,0x02]))
        sl=0x11 if dev else 0x01
        resp=self._uds(bytes([0x27,sl]))
        seed=resp[2:6]
        if seed!=bytes(4):
            dkey=self._xtea(seed,key)
            self._uds(bytes([0x27,sl+1])+dkey)
            self._log(f"Seed:{self._hx(seed)}  Key:{self._hx(dkey)}","INFO")
        self._log("Security unlocked ✓"+(
            "\n  ⚠ Dev mode — DTC C10007 logged" if dev else ""),"OK" if not dev else "WARN")

    def _xtea(self,seed,key):
        # FIX #6: use 32 iterations (= 64 Feistel rounds) — standard XTEA requirement
        k=struct.unpack(">4I",key); v0=struct.unpack(">I",seed)[0]
        v1,s,D=0,0,0x9E3779B9
        for _ in range(32):
            v0=(v0+(((v1<<4^v1>>5)+v1)^(s+k[s&3])))&0xFFFFFFFF
            s=(s+D)&0xFFFFFFFF
            v1=(v1+(((v0<<4^v0>>5)+v0)^(s+k[(s>>11)&3])))&0xFFFFFFFF
        return struct.pack(">I",v0)

    # ── QUICK ACTIONS ─────────────────────────────────────────────────────────
    def _tester_present(self):
        def _d():
            try: self._uds(bytes([0x3E,0x00])); self._log("TesterPresent OK ✓","OK")
            except Exception as e: self._log(f"TesterPresent FAILED: {e}","ERR")
        self._run(_d)

    def _enter_prog(self):
        def _d():
            try: self._uds(bytes([0x10,0x02])); self._log("Prog session entered ✓","OK")
            except Exception as e: self._log(f"Enter prog session FAILED: {e}","ERR")
        self._run(_d)

    def _security_access(self):
        # FIX #3: resolve key on the main thread before spawning the worker
        key=self._get_key()
        if not key: return
        def _d():
            try: self._unlock(key,dev=self.dev_mode.get())
            except Exception as e: self._log(f"Security Access FAILED: {e}","ERR")
        self._run(_d)

    def _read_bl_version(self):
        def _d():
            try:
                r=self._uds(bytes([0x22,0xF1,0x81]))
                v=r[3:].decode("ascii",errors="replace").rstrip("\x00")
                self._log(f"BL Version: {v}","OK")
                self.after(0,lambda: self.chip_bl.set_value(v[:12]))
            except Exception as e: self._log(f"Read BL Version FAILED: {e}","ERR")
        self._run(_d)

    def _read_sw_version(self):
        def _d():
            try:
                r=self._uds(bytes([0x22,0xF1,0x89]))
                v=self._hx(r[3:])
                self._log(f"SW Version: {v}","OK")
                self.after(0,lambda: self.chip_sw.set_value(v[:10]))
            except Exception as e: self._log(f"Read SW Version FAILED: {e}","ERR")
        self._run(_d)

    def _read_fingerprint(self):
        def _d():
            try:
                r=self._uds(bytes([0x22,0xF1,0x5B]))
                ts=struct.unpack(">I",r[3:7])[0]
                sn=r[7:17].decode("ascii",errors="replace").rstrip("\x00")
                ts_s=time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime(ts))
                self._log(f"Timestamp : {ts_s}","OK")
                self._log(f"Tester S/N: {sn}","OK")
                txt=f"Timestamp : {ts_s}\nTester S/N: {sn}\nRaw       : {self._hx(r[3:])}\n"
                try:
                    r2=self._uds(bytes([0x22,0xF1,0x89]))
                    sw=self._hx(r2[3:]); txt+=f"SW Version: {sw}\n"
                    self._log(f"SW Version: {sw}","OK")
                    self.after(0,lambda: self.chip_sw.set_value(sw[:10]))
                except: pass
                self.after(0,lambda:(self.fp_display.delete("1.0",tk.END),
                                     self.fp_display.insert("1.0",txt)))
            except Exception as e: self._log(f"Read Fingerprint FAILED: {e}","ERR")
        self._run(_d)

    def _read_dtc(self):
        def _d():
            try:
                r=self._uds(bytes([0x19,0x02,0xFF])); self._parse_dtc(r)
            except Exception as e: self._log(f"Read DTC FAILED: {e}","ERR")
        self._run(_d)

    def _read_dtc_tab(self):
        def _d():
            try:
                r=self._uds(bytes([0x19,0x02,0xFF]))
                self._parse_dtc(r); self._refresh_dtc(r)
            except Exception as e: self._log(f"Read DTC FAILED: {e}","ERR")
        self._run(_d)

    def _parse_dtc(self,resp):
        dtcs=resp[4:]; cnt=len(dtcs)//4
        if cnt==0:
            self._log("DTC: no faults ✓","OK")
            self.after(0,lambda:(self.dtc_count_lbl.config(text="No faults ✓",fg=T["GREEN"]),
                                  self.chip_dtc.set_value("OK ✓")))
            return
        self._log(f"DTC: {cnt} fault(s):","WARN")
        self.after(0,lambda:(self.dtc_count_lbl.config(text=f"{cnt} fault(s)",fg=T["RED"]),
                              self.chip_dtc.set_value(f"{cnt} DTC")))
        self.after(0,lambda: self.chip_dtc.set_color(T["RED"]))
        for i in range(cnt):
            d=dtcs[i*4:(i+1)*4]
            code=(d[0]<<16)|(d[1]<<8)|d[2]; st=d[3]
            name,desc,_=DTC_INFO.get(code,("UNKNOWN","Unknown DTC code","red"))
            self._log(f"  C{code:06X}  {name:<22}  [0x{st:02X}]  {desc}","DTC")

    def _refresh_dtc(self,resp):
        def _u():
            for w in self.dtc_list.winfo_children(): w.destroy()
            dtcs=resp[4:]; cnt=len(dtcs)//4
            if cnt==0:
                tk.Label(self.dtc_list,text="  ✓  No faults stored",
                         fg=T["GREEN"],bg=T["BG2"],font=FUI_B,pady=20).pack(); return
            cm={"red":T["RED"],"amber":T["AMBER"],"blue":T["BLUE"]}
            for i in range(cnt):
                d=dtcs[i*4:(i+1)*4]
                code=(d[0]<<16)|(d[1]<<8)|d[2]; st=d[3]
                name,desc,ck=DTC_INFO.get(code,("UNKNOWN","Unknown","red"))
                col=cm.get(ck,T["RED"]); bg=T["BG2"] if i%2==0 else T["BG3"]
                r=tk.Frame(self.dtc_list,bg=bg); r.pack(fill=tk.X)
                tk.Label(r,text=f"  C{code:06X}",fg=col,bg=bg,
                         font=FMONO_B,width=12,anchor=tk.W,pady=6).pack(side=tk.LEFT)
                tk.Label(r,text=name,fg=col,bg=bg,
                         font=FUI_B,width=22,anchor=tk.W).pack(side=tk.LEFT)
                tk.Label(r,text=f"0x{st:02X}",fg=T["FG2"],bg=bg,
                         font=FMONO_S,width=8,anchor=tk.W).pack(side=tk.LEFT)
                tk.Label(r,text=desc,fg=T["FG2"],bg=bg,
                         font=FUI_S,anchor=tk.W,padx=8).pack(side=tk.LEFT)
        self.after(0,_u)

    def _clear_dtc(self):
        if not messagebox.askyesno("Clear DTC","Clear all DTCs?"): return
        def _d():
            try:
                self._uds(bytes([0x14,0xFF,0xFF,0xFF]))
                self._log("DTC cleared ✓","OK")
                self.after(0,lambda:(
                    self.dtc_count_lbl.config(text="Cleared ✓",fg=T["GREEN"]),
                    self.chip_dtc.set_value("OK ✓"),
                    self.chip_dtc.set_color(T["GREEN"])))
                for w in self.dtc_list.winfo_children():
                    self.after(0,w.destroy)
            except Exception as e: self._log(f"Clear DTC FAILED: {e}","ERR")
        self._run(_d)

    def _verify_crc(self):
        # FIX #3: resolve key on the main thread before spawning the worker
        key=self._get_key()
        if not key: return
        def _d():
            try:
                self._unlock(key,dev=self.dev_mode.get())
                r=self._uds(bytes([0x31,0x01,0xFF,0x01]),timeout=30.0)
                ok=r[4] if len(r)>=5 else 0
                self._log("CRC verify: PASS ✓" if ok==0x01 else "CRC verify: FAIL ✗",
                          "OK" if ok==0x01 else "WARN")
            except Exception as e: self._log(f"Verify CRC FAILED: {e}","ERR")
        self._run(_d)

    def _ecu_reset(self):
        def _d():
            try: self._uds(bytes([0x11,0x01])); self._log("ECU Reset sent ✓","OK")
            except TimeoutError: self._log("ECU Reset sent (ECU restarting) ✓","OK")
            except Exception as e: self._log(f"ECU Reset FAILED: {e}","ERR")
        self._run(_d)

    def _write_fingerprint(self):
        def _d():
            try:
                ts=int(self.fp_ts_var.get())
                # FIX #9: pad with null bytes, not spaces
                sn=self.fp_sn_var.get().encode("ascii")[:10].ljust(10, b'\x00')
                ver=bytes.fromhex(self.fp_ver_var.get().replace(" ",""))[:4].ljust(4,b'\x00')
                pl=bytes([0x2E,0xF1,0x5B])+struct.pack(">I",ts)+sn+ver
                self._uds(pl); self._log("Fingerprint written ✓","OK")
            except Exception as e: self._log(f"Write Fingerprint FAILED: {e}","ERR")
        self._run(_d)

    def _raw_send(self):
        def _d():
            try:
                raw=bytes.fromhex(self.raw_entry.get().replace(" ",""))
                self._uds(raw,timeout=float(self.raw_timeout.get()))
            except Exception as e: self._log(f"Raw UDS FAILED: {e}","ERR")
        self._run(_d)

    def _quick(self,h): self.raw_entry.delete(0,tk.END); self.raw_entry.insert(0,h)

    # ── FIRMWARE BROWSE ───────────────────────────────────────────────────────
    def _browse_fw(self):
        path=filedialog.askopenfilename(
            title="Select signed firmware (.bin)",
            filetypes=[("Binary","*.bin"),("All","*.*")])
        if not path: return
        self.fw_path.set(path)
        # FIX #4: use context manager to avoid file handle leak
        with open(path,"rb") as f: data=f.read()
        sz=len(data)
        comp=len(zlib.compress(data,level=9))
        SM=0xEC5A1234; M2N={v:k for k,v in VEHICLE_MODELS.items()}
        if len(data)>=13 and struct.unpack('>I',data[0:4])[0]==SM:
            fm=struct.unpack('>H',data[8:10])[0]; vm,vn,vp=data[10],data[11],data[12]
            mn=M2N.get(fm,f"0x{fm:04X}")
            self.sw_ver_var.set(f"{vm}.{vn}.{vp}")
            if fm in M2N: self.model_var.set(mn)
            self.fc_model.set_value(mn[:12]);  self.fc_model.set_bg(T["CARD"])
            self.fc_version.set_value(f"v{vm}.{vn}.{vp}"); self.fc_version.set_bg(T["CARD"])
            self.fc_size.set_value(f"{sz//1024}KB");    self.fc_size.set_bg(T["CARD"])
            self.fc_comp.set_value(f"{comp//1024}KB ({100*comp//sz}%)"); self.fc_comp.set_bg(T["CARD"])
            self.fw_info_lbl.config(
                text=f"✓  {os.path.basename(path)}  |  SignHeader OK  |  {mn}  |  v{vm}.{vn}.{vp}",
                fg=T["GREEN"])
            self.chip_model.set_value(mn[:12])
            self._log(f"Firmware loaded: {os.path.basename(path)}","INFO")
            self._log(f"  Model: {mn}  Version: v{vm}.{vn}.{vp}  "
                      f"Size: {sz:,}B → {comp:,}B compressed","OK")
        else:
            self.sw_ver_var.set("—")
            for c in [self.fc_model,self.fc_version,self.fc_size,self.fc_comp]:
                c.set_value("—"); c.set_bg(T["CARD"])
            self.fc_size.set_value(f"{sz//1024}KB")
            self.fc_comp.set_value(f"{comp//1024}KB")
            self.fw_info_lbl.config(text="⚠  SignHeader not found — raw binary",fg=T["AMBER"])

    # ── OTA FLASH ─────────────────────────────────────────────────────────────
    def _start_ota(self):
        if not self.connected: messagebox.showwarning("Not Connected","Connect first."); return
        key=self._get_key()
        if not key: return
        fp=self.fw_path.get()
        if not fp or not os.path.exists(fp):
            messagebox.showerror("No Firmware","Select signed firmware .bin first."); return
        self.ota_abort=False
        self.btn_ota.set_color(T["AMBER"])
        threading.Thread(target=self._ota,args=(fp,key),daemon=True).start()

    def _abort_ota(self):
        self.ota_abort=True; self._log("OTA abort requested…","WARN")

    def _upd(self,msg,pct,bstr=""):
        self.after(0,self.ota_lbl.config,  {"text":msg})
        self.after(0,self.ota_prog.config,  {"value":pct})
        self.after(0,self.ota_pct.config,   {"text":f"{pct}%"})
        self.after(0,self.ota_bytes.config, {"text":bstr})

    def _step(self,n): self.after(0,lambda: self.step_bar.set_step(n))

    def _ota(self,fw_path,key):
        try:
            self._log("="*56,"HEAD"); self._log("NexaBoot OTA Flash — Starting","HEAD"); self._log("="*56,"HEAD")
            self.after(0,self.step_bar.reset)

            # FIX #4: use context manager
            with open(fw_path,"rb") as f: data=f.read()
            SM=0xEC5A1234; fw_m=0x0001; fw_v=(1,0,0); M2N={v:k for k,v in VEHICLE_MODELS.items()}
            if len(data)>=13 and struct.unpack('>I',data[0:4])[0]==SM:
                fw_m=struct.unpack('>H',data[8:10])[0]; fw_v=(data[10],data[11],data[12])
                self._log(f"SignHeader: model=0x{fw_m:04X} ver={fw_v[0]}.{fw_v[1]}.{fw_v[2]}","INFO")
            else: self._log("⚠ SignHeader not found","WARN")

            sm=VEHICLE_MODELS.get(self.model_var.get(),0x0001)
            if fw_m not in (0xFFFF,0x0000) and fw_m!=sm and not self.dev_mode.get():
                raise RuntimeError(f"Model mismatch!\n  File: {M2N.get(fw_m,'?')}\n  Selected: {self.model_var.get()}")

            self._upd("Compressing…",2)
            comp=zlib.compress(data,level=9)
            nonce=os.urandom(12)
            self._upd("Encrypting…",3)
            from Crypto.Cipher import AES
            from Crypto.Util import Counter
            ctr=Counter.new(32,prefix=nonce,initial_value=0,little_endian=False)
            enc=AES.new(key,AES.MODE_CTR,counter=ctr).encrypt(comp)
            self._log(f"Payload: {len(data):,}B → {len(comp):,}B → {len(enc):,}B","INFO")

            if self.ota_abort: raise RuntimeError("Aborted")

            # Blind reset
            self._step(0); self._upd("Triggering app reset…",4)
            try:
                with self.can.lock:
                    self.can.tp.send(bytes([0x10,0x02]))
                    t=time.time()+0.08
                    while time.time()<t: self.can.tp.process(); time.sleep(0.001)
            except: pass
            time.sleep(2.0)
            if self.ota_abort: raise RuntimeError("Aborted")

            # Catch BL
            self._step(1); self._upd("Catching bootloader…",5)
            caught=False
            for att in range(100):
                try: self._uds(bytes([0x10,0x02]),timeout=0.08); caught=True; break
                except: pass
                time.sleep(0.02)
            if not caught: self._uds(bytes([0x10,0x02]))
            self._log(f"Bootloader caught ✓","OK")

            # Flush + session
            self._step(2); self._upd("Re-entering session…",6)
            try:
                with self.can.lock:
                    fl=time.time()+0.3
                    while time.time()<fl:
                        self.can.tp.process()
                        if self.can.tp.available():
                            s=self.can.tp.recv(); self._log(f"Flushed: {bytes(s).hex()}","INFO")
                        time.sleep(0.001)
            except: pass
            self._uds(bytes([0x10,0x02])); time.sleep(0.1)
            self._log("Session confirmed ✓","OK")
            if self.ota_abort: raise RuntimeError("Aborted")

            # SA
            self._step(3); self._upd("Security Access…",8)
            dev=self.dev_mode.get(); sl=0x11 if dev else 0x01
            resp=self._uds(bytes([0x27,sl])); seed=resp[2:6]
            if seed!=bytes(4):
                dkey=self._xtea(seed,key); self._uds(bytes([0x27,sl+1])+dkey)
            self._log("Security unlocked ✓","OK")
            if dev: self._log("⚠ Dev mode — DTC C10007 logged","WARN")
            if self.ota_abort: raise RuntimeError("Aborted")

            # Erase
            self._step(4); self._upd("Erasing app slot…",12)
            er=bytes([0x31,0x01,0xFF,0x00,(fw_m>>8)&0xFF,fw_m&0xFF,fw_v[0],fw_v[1],fw_v[2]])
            self._uds(er,timeout=60.0); self._log("Erase complete ✓  BL config saved","OK")
            if self.ota_abort: raise RuntimeError("Aborted")

            # Download
            self._step(5); self._upd("Request Download…",16)
            app_addr=int(self.app_addr_var.get(),16)
            rd=bytes([0x34,0x11,0x44])+struct.pack(">I",app_addr)+struct.pack(">I",len(enc))+nonce
            resp=self._uds(rd); mb=resp[2] if len(resp)>=3 else 128
            self._log(f"Download accepted ✓  maxBlock={mb}B","OK")

            # Transfer
            self._step(6); total=len(enc); off=0; bsn=1; tpt=time.time()
            while off<total:
                if self.ota_abort: raise RuntimeError("Aborted")
                chunk=enc[off:off+mb]; self._uds(bytes([0x36,bsn])+chunk,timeout=15.0)
                off+=len(chunk)
                # FIX #2: explicit wrap — sequence numbers cycle 0x01..0xFF, skip 0x00
                bsn = bsn % 0xFF + 1
                pct=18+int(74*off/total)
                self._upd(f"Transferring…",pct,f"{off:,} / {total:,} B  ({100*off//total}%)")
                if time.time()-tpt>=1.5:
                    try: self._uds(bytes([0x3E,0x80]),timeout=0.5)
                    except: pass
                    tpt=time.time()
            self._log("Transfer complete ✓","OK")
            if self.ota_abort: raise RuntimeError("Aborted")

            # TransferExit
            self._step(7); self._upd("TransferExit — decrypt+verify (up to 3 min)…",92)
            self._log("ECU decrypting + verifying ECDSA — DTC C10008 written…","WARN")
            self._uds(bytes([0x37]),timeout=300.0)
            self._log("TransferExit OK ✓  DTC C10008 cleared","OK")

            # CRC
            self._step(8); self._upd("Verifying CRC…",94)
            r=self._uds(bytes([0x31,0x01,0xFF,0x01]),timeout=30.0)
            if (r[4] if len(r)>=5 else 0)!=0x01: raise RuntimeError("CRC verify FAILED")
            self._log("CRC verify PASS ✓","OK")

            # Fingerprint
            self._step(9); self._upd("Writing fingerprint…",96)
            # FIX #9: pad station ID with null bytes, not spaces
            sn=self.sn_var.get().encode("ascii")[:10].ljust(10, b'\x00')
            vr=bytes([fw_v[0],fw_v[1],fw_v[2],0x00])
            fp_payload=bytes([0x2E,0xF1,0x5B])+struct.pack(">I",int(time.time()))+sn+vr
            self._uds(fp_payload); self._log(f"Fingerprint written ✓  ver={fw_v[0]}.{fw_v[1]}.{fw_v[2]}","OK")

            # Reset
            self._step(10); self._upd("Resetting ECU…",99)
            try: self._uds(bytes([0x11,0x01]))
            except TimeoutError: pass
            self._log("ECU Reset sent ✓","OK")

            # Done — FIX #8: _step(11) now valid with 12-label StepBar
            self._step(11); self._upd("OTA FLASH COMPLETE ✓",100,f"{total:,} / {total:,} B")
            self.after(0,lambda: self.ota_prog.configure(style="Green.HP.Horizontal.TProgressbar"))
            self._log("="*56,"HEAD"); self._log("OTA FLASH COMPLETE ✓","OK")
            self._log(f"  Model  : {M2N.get(fw_m,'?')}","OK")
            self._log(f"  Version: v{fw_v[0]}.{fw_v[1]}.{fw_v[2]}","OK")
            self._log(f"  Station: {self.sn_var.get()}","OK"); self._log("="*56,"HEAD")
            self.after(0,lambda: self.btn_ota.set_color(T["GREEN"]))

        except Exception as e:
            self._log(f"OTA FAILED: {e}","ERR"); self._upd(f"FAILED: {e}",0)
            self.after(0,lambda: self.ota_prog.configure(style="Red.HP.Horizontal.TProgressbar"))
            self.after(0,lambda: self.btn_ota.set_color(T["RED"]))
        finally:
            self.after(2000,lambda: self.btn_ota.set_color(T["GREEN"]))

    # ── CONFIG ────────────────────────────────────────────────────────────────
    def _save_cfg(self):
        # FIX #4: use context manager
        try:
            with open(self.config_file,"w") as f:
                json.dump({"interface":self.iface_var.get(),"channel":self.chan_var.get(),
                           "bitrate":self.brate_var.get(),"rxid":self.resp_id_var.get(),
                           "txid":self.req_id_var.get(),"app_addr":self.app_addr_var.get(),
                           "theme":self._theme}, f)
        except: pass

    def _load_cfg(self):
        # FIX #4: use context manager
        try:
            with open(self.config_file) as f:
                cfg=json.load(f)
            self.iface_var.set(cfg.get("interface","pcan"))
            self.chan_var.set(cfg.get("channel","PCAN_USBBUS1"))
            self.brate_var.set(cfg.get("bitrate","250000"))
            self.resp_id_var.set(cfg.get("rxid","0x7E8"))
            self.req_id_var.set(cfg.get("txid","0x7E0"))
            self.rxid_var.set(cfg.get("rxid","0x7E8"))
            self.txid_var.set(cfg.get("txid","0x7E0"))
            self.app_addr_var.set(cfg.get("app_addr","0x00014000"))
        except: pass

    def _on_close(self):
        self.ota_abort=True; self._save_cfg()
        try: self.can.disconnect()
        except: pass
        self.destroy()

if __name__=="__main__":
    NexaBootTester().mainloop()
