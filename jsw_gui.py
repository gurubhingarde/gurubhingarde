import tkinter as tk
from tkinter import filedialog, messagebox, ttk, Menu
import threading
import time
import os
import sys
import traceback
import ctypes

import subprocess
from flashing_logic import FlashingLogic, PumpFlashingLogic, PUMP_CAN_CONFIG

APP_NAME = "JSW FlashXpert"
APP_VERSION = "V1.2"
DEV_INFO = "Developed by Controls & Software Department, R&D JSW Greentech Limited ©"
LOGO_FILE = "Group_Logo.png"

CAN_INTERFACE_MAP = {
    "Peak":   {"interface": "peak",   "channel": 0, "bitrate": 250000},
    "Vector": {"interface": "vector", "channel": 0, "bitrate": 250000},
    "Kvaser": {"interface": "kvaser", "channel": 0, "bitrate": 250000},
}

CONTROLLER_LIST = [
    "JSW EVCU", "JSW MCU", "JSW DCDC",
    "JSW Air Pump", "JSW Oil Pump",
]

# Controllers that use the pump protocol instead of UDS
PUMP_CONTROLLERS = {"JSW Air Pump", "JSW Oil Pump"}


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# --------- Single centered ignition popup (OFF → ON; OK→Stop + countdown + hourglass) ---------
class IgnitionDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Ignition")
        self.configure(bg="#f6f8fb")
        self.resizable(False, False)

        self.msg_var = tk.StringVar(value="Please TURN OFF ignition and click OK.")
        tk.Label(self, textvariable=self.msg_var, bg="#f6f8fb", fg="#163c69",
                 font=("Segoe UI", 12), wraplength=420, justify="center").pack(padx=24, pady=(22, 8))

        row = tk.Frame(self, bg="#f6f8fb")
        row.pack(pady=(0, 6))
        self.glass_var = tk.StringVar(value="")
        self.timer_var = tk.StringVar(value="")
        self._anim_tick = 0
        self._countdown_running = False

        self.glass_lbl = tk.Label(row, textvariable=self.glass_var, bg="#f6f8fb",
                                  fg="#154385", font=("Segoe UI Symbol", 18, "bold"))
        self.glass_lbl.pack(side="left", padx=(0, 8))
        self.timer_lbl = tk.Label(row, textvariable=self.timer_var, bg="#f6f8fb",
                                  fg="#154385", font=("Segoe UI", 12, "bold"))
        self.timer_lbl.pack(side="left")

        self.ok_btn = tk.Button(self, text="OK", width=14, bg="#154385", fg="white",
                                relief="flat", font=("Segoe UI", 11, "bold"))
        self.ok_btn.pack(pady=(6, 16))

        self.transient(master)
        self.grab_set()
        self.update_idletasks()
        try:
            pw, ph = master.winfo_width(), master.winfo_height()
            px, py = master.winfo_rootx(), master.winfo_rooty()
            w, h = 520, 200
            x = px + (pw - w)//2
            y = py + (ph - h)//2
            self.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
            w, h = 520, 200
            x, y = (sw - w)//2, (sh - h)//2
            self.geometry(f"{w}x{h}+{x}+{y}")
        self.protocol("WM_DELETE_WINDOW", lambda: None)

    def transition_to_on(self, on_stop):
        self.msg_var.set("Now TURN ON ignition and wait.\n\nFlashing will start automatically when the controller responds.")
        self.ok_btn.config(text="Stop", state="normal", command=on_stop)
        self.glass_var.set("⌛")
        self.timer_var.set("100 s remaining")
        self._anim_tick = 0

    def start_countdown(self, total_seconds=100, stop_flag_getter=lambda: False, on_timeout=None):
        self._countdown_running = True
        end_time = time.time() + total_seconds

        def _tick():
            if not self._countdown_running:
                return
            if stop_flag_getter():
                return
            remain = int(max(0, end_time - time.time()))
            self._anim_tick ^= 1
            self.glass_var.set("⌛" if self._anim_tick == 0 else "⏳")
            self.timer_var.set(f"{remain:>2d} s remaining")
            if remain <= 0:
                if on_timeout:
                    on_timeout()
                return
            self.after(1000, _tick)

        def _half_flip():
            if not self._countdown_running:
                return
            if stop_flag_getter():
                return
            self._anim_tick ^= 1
            self.glass_var.set("⌛" if self._anim_tick == 0 else "⏳")
            self.after(500, _half_flip)

        _tick()
        _half_flip()

    def stop_countdown(self):
        self._countdown_running = False

    def auto_close(self):
        self.stop_countdown()
        try: self.grab_release()
        except Exception: pass
        self.destroy()


# -------- small popup to show ASCII pages for "Read Ver" ----------
class ReadVerDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Read Ver")
        self.configure(bg="#f6f8fb")
        self.resizable(False, False)

        self.icon_lbl = tk.Label(self, text="⌛", bg="#f6f8fb", fg="#154385",
                                 font=("Segoe UI Symbol", 18, "bold"))
        self.icon_lbl.pack(pady=(16, 6))

        self.msg_var = tk.StringVar(value="Reading version...")
        tk.Label(self, textvariable=self.msg_var, bg="#f6f8fb", fg="#163c69",
                 font=("Segoe UI", 12), wraplength=460, justify="center").pack(padx=18)

        self.text = tk.Text(self, width=58, height=8, bg="#eef3fb", fg="#1f355e",
                            font=("Segoe UI", 11), relief="flat", state="disabled")
        self.text.pack(padx=16, pady=(8, 10))

        self.close_btn = tk.Button(self, text="Close", width=12, bg="#154385", fg="white",
                                   relief="flat", font=("Segoe UI", 11, "bold"),
                                   command=self.destroy, state="disabled")
        self.close_btn.pack(pady=(0, 14))

        self.transient(master); self.grab_set(); self.update_idletasks()
        try:
            pw, ph = master.winfo_width(), master.winfo_height()
            px, py = master.winfo_rootx(), master.winfo_rooty()
            w, h = 520, 320
            x, y = px + (pw - w)//2, py + (ph - h)//2
            self.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
            w, h = 520, 320
            x, y = (sw - w)//2, (sh - h)//2
            self.geometry(f"{w}x{h}+{x}+{y}")
        self.protocol("WM_DELETE_WINDOW", lambda: None)

        self._alive = True
        def animate():
            if not self._alive: return
            self.icon_lbl.config(text="⌛" if self.icon_lbl.cget("text") == "⏳" else "⏳")
            self.after(500, animate)
        animate()

    def show_results(self, version_str):
        self._alive = False
        self.msg_var.set("Firmware version:")
        self.text.config(state="normal"); self.text.delete("1.0", "end")
        if version_str:
            self.text.insert("end", f"Current Firmware ver: {version_str}\n")
        else:
            self.text.insert("end", "No version details available.")
        self.text.config(state="disabled")
        self.close_btn.config(state="normal")
        try: self.grab_release()
        except Exception: pass


def get_join_status():
    NetGetJoinInformation = ctypes.windll.netapi32.NetGetJoinInformation
    NetApiBufferFree = ctypes.windll.netapi32.NetApiBufferFree
    name = ctypes.c_wchar_p()
    status = ctypes.c_int()
    NetGetJoinInformation(None, ctypes.byref(name), ctypes.byref(status))
    NetApiBufferFree(name)
    return status.value


def get_domain_name():
    domain = os.environ.get("USERDOMAIN")
    computer = os.environ.get("COMPUTERNAME")
    if domain and domain.upper() != computer.upper():
        return domain
    return None


def is_azure_ad_joined():
    try:
        output = subprocess.check_output("dsregcmd /status", shell=True, text=True)
        return "AzureAdJoined : YES" in output
    except Exception:
        return False


class FlashingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1100x740")
        self.resizable(False, False)
        self.configure(bg="#f6f8fb")
        print("Checking laptop domain status...\n")

        join_status = get_join_status()
        if join_status == 3:
            domain = get_domain_name()
            print("✔ On-Prem Active Directory Domain Joined")
            print(f"✔ Domain Name: {domain}")
        elif is_azure_ad_joined():
            print("✔ Azure Active Directory Joined")
        else:
            try:
                messagebox.showerror(
                    'Access Denied',
                    'This application can only run on devices joined to the organization domain.\n\n'
                    'Please join a domain (On-Prem AD or Azure AD) and restart.'
                )
            except Exception:
                pass
            import sys
            sys.exit(1)

        # --- MENU ---
        menubar = Menu(self)
        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.show_about)
        helpmenu.add_command(label="Help", command=self.show_help)
        menubar.add_cascade(label="Help", menu=helpmenu)
        self.config(menu=menubar)

        # --- HEADER ---
        self.header_frame = tk.Frame(self, bg="#f6f8fb")
        self.header_frame.place(x=0, y=0, width=1100, height=90)
        try:
            self.logo_img = tk.PhotoImage(file=resource_path(LOGO_FILE))
            w, h = self.logo_img.width(), self.logo_img.height()
            max_w, max_h = 120, 50
            scale_w = max(1, w // max_w)
            scale_h = max(1, h // max_h)
            scale = max(scale_w, scale_h)
            if scale > 1:
                self.logo_img = self.logo_img.subsample(scale, scale)
            self.logo_label = tk.Label(self.header_frame, image=self.logo_img, bg="#f6f8fb")
            self.logo_label.place(x=32, y=15)
        except Exception:
            self.logo_label = tk.Label(self.header_frame, text="[Logo not found]", bg="#f6f8fb", fg="red", font=("Segoe UI", 14, "bold"))
            self.logo_label.place(x=32, y=25)
        self.title_label = tk.Label(self.header_frame, text=APP_NAME, font=("Segoe UI", 32, "bold"),
                                    bg="#f6f8fb", fg="#163c69")
        self.title_label.place(x=180, y=27)
        self.header_frame.update_idletasks()
        title_width = self.title_label.winfo_reqwidth()
        self.version_label = tk.Label(
            self.header_frame, text=APP_VERSION, font=("Segoe UI", 14, "bold"),
            bg="#f6f8fb", fg="#163c69"
        )
        self.version_label.place(x=180 + title_width + 12, y=45)

        # --- SIDEBAR: VERTICAL STEP ICONS ---
        self.sidebar_frame = tk.Frame(self, bg="#f6f8fb")
        self.sidebar_frame.place(x=0, y=90, width=170, height=580)
        self.steps = [
            {"label": "Secure Connection", "icon": "⚡"},
            {"label": "Erased",            "icon": "♻"},
            {"label": "Downloaded",        "icon": "⬇"},
            {"label": "Programming",       "icon": "⚙"},
            {"label": "Verified",          "icon": "✔"},
            {"label": "ECU Reset",         "icon": "↻"},
        ]
        self.current_step = 0
        self.completed_steps = set()
        self.step_labels = []
        self.step_icon_labels = []
        self.color_completed = "#27AE60"
        self.color_current = "#154385"
        self.color_incomplete = "#A0AABF"
        for i, step in enumerate(self.steps):
            frame = tk.Frame(self.sidebar_frame, width=150, height=54, bg="#f6f8fb")
            frame.pack(side="top", pady=13)
            icon_label = tk.Label(frame, text=step["icon"], font=("Segoe UI", 20, "bold"), bg="#f6f8fb")
            icon_label.pack(side="top")
            text_label = tk.Label(frame, text=step["label"], font=("Segoe UI", 11, "bold"), bg="#f6f8fb", fg="#163c69")
            text_label.pack(side="top")
            self.step_icon_labels.append(icon_label)
            self.step_labels.append(text_label)
        self.update_progress_tracker()

        # --- MAIN CONTROLS ---
        self.main_frame = tk.Frame(self, bg="#fff")
        self.main_frame.place(x=180, y=100, width=880, height=610)

        self.controller_label = tk.Label(self.main_frame, text="Select ECU", font=("Segoe UI", 14, "bold"), bg="#fff", fg="#1f355e")
        self.controller_label.place(x=30, y=15)
        self.controller_var = tk.StringVar(value=CONTROLLER_LIST[0])
        self.controller_combo = ttk.Combobox(self.main_frame, textvariable=self.controller_var,
                                             values=CONTROLLER_LIST, state="readonly", width=22,
                                             font=("Segoe UI", 13))
        self.controller_combo.place(x=200, y=17)

        self.can_label = tk.Label(self.main_frame, text="Select Hardware", font=("Segoe UI", 14, "bold"), bg="#fff", fg="#1f355e")
        self.can_label.place(x=30, y=55)
        self.can_var = tk.StringVar(value="Peak")
        self.can_combo = ttk.Combobox(self.main_frame, textvariable=self.can_var,
                                      values=list(CAN_INTERFACE_MAP.keys()), state="readonly", width=22,
                                      font=("Segoe UI", 13))
        self.can_combo.place(x=200, y=57)

        self.file_label = tk.Label(self.main_frame, text="Select Flash File", font=("Segoe UI", 14, "bold"), bg="#fff", fg="#1f355e")
        self.file_label.place(x=30, y=95)
        self.file_var = tk.StringVar()
        self.file_entry = tk.Entry(self.main_frame, textvariable=self.file_var, state="readonly", width=45,
                                   font=("Segoe UI", 13))
        self.file_entry.place(x=200, y=97)
        self.browse_file_btn = tk.Button(self.main_frame, text="Browse", command=self.browse_file,
                                         bg="#154385", fg="white", font=("Segoe UI", 12, "bold"),
                                         relief="flat", cursor="hand2")
        self.browse_file_btn.place(x=650, y=92, width=100, height=32)

        self.progress = ttk.Progressbar(self.main_frame, length=540, mode="determinate")
        self.progress.place(x=30, y=140)
        self.percent_var = tk.StringVar(value="0%")
        self.percent_label = tk.Label(self.main_frame, textvariable=self.percent_var,
                                      font=("Segoe UI", 13, "bold"), bg="#fff", fg="#154385")
        self.percent_label.place(x=580, y=135)

        self.start_btn = tk.Button(self.main_frame, text="Start Flashing", command=self.start_flashing,
                                   bg="#27AE60", fg="white", font=("Segoe UI", 14, "bold"),
                                   relief="flat", cursor="hand2")
        self.start_btn.place(x=30, y=185, width=200, height=42)

        self.save_log_btn = tk.Button(self.main_frame, text="Save Log", command=self.save_log,
                                      bg="#154385", fg="white", font=("Segoe UI", 14, "bold"),
                                      relief="flat", cursor="hand2")
        self.save_log_btn.place(x=250, y=185, width=160, height=42)

        self.clear_log_btn = tk.Button(self.main_frame, text="Clear Log", command=self.clear_log,
                                       bg="#F28705", fg="white", font=("Segoe UI", 14, "bold"),
                                       relief="flat", cursor="hand2")
        self.clear_log_btn.place(x=430, y=185, width=160, height=42)

        self.read_ver_btn = tk.Button(self.main_frame, text="Read Version",
                                      command=self.read_ver_pages,
                                      bg="#154385", fg="white",
                                      font=("Segoe UI", 14, "bold"),
                                      relief="flat", cursor="hand2")
        self.read_ver_btn.place(x=610, y=185, width=180, height=42)

        self.log_label = tk.Label(self.main_frame, text="Log", font=("Segoe UI", 13, "bold"),
                                  bg="#34495E", fg="white")
        self.log_label.place(x=30, y=245)
        self.log_box = tk.Text(self.main_frame, bg="#34495E", fg="white", font=("Segoe UI", 12),
                               state="disabled", height=11, wrap="word", relief="flat", bd=4)
        self.log_box.place(x=30, y=280, width=820, height=210)

        self.status_var = tk.StringVar(value="Status: Idle")
        self.status_label = tk.Label(self.main_frame, textvariable=self.status_var,
                                     font=("Segoe UI", 13, "bold"), bg="#fff", fg="#1f355e")
        self.status_label.place(x=30, y=510)

        self.elapsed_var = tk.StringVar(value="Elapsed Time: 00:00:00")
        self.elapsed_label = tk.Label(self.main_frame, textvariable=self.elapsed_var,
                                      font=("Segoe UI", 13), bg="#fff", fg="#1f355e")
        self.elapsed_label.place(x=260, y=510)

        # --- Footer ---
        self.footer_frame = tk.Frame(self, bg="#163c69")
        self.footer_frame.place(relx=0.5, rely=1.0, anchor="s", width=1100, height=36)
        self.footer_frame.grid_columnconfigure(0, weight=1)
        self.footer_frame.grid_columnconfigure(1, weight=0)
        self.footer_label = tk.Label(
            self.footer_frame, text=DEV_INFO,
            font=("Segoe UI", 12, "bold"),
            bg="#163c69", fg="#fff",
            anchor="center", justify="center"
        )
        self.footer_label.grid(row=0, column=0, sticky="nsew", padx=(10, 5))
        try:
            self.footer_logo_img = tk.PhotoImage(file=resource_path(LOGO_FILE))
            w, h = self.footer_logo_img.width(), self.footer_logo_img.height()
            max_w, max_h = 45, 15
            scale_w = max(1, w // max_w)
            scale_h = max(1, h // max_h)
            scale = max(scale_w, scale_h)
            if scale > 1:
                self.footer_logo_img = self.footer_logo_img.subsample(scale, scale)
            self.footer_logo_label = tk.Label(self.footer_frame, image=self.footer_logo_img, bg="#163c69")
            self.footer_logo_label.grid(row=0, column=1, sticky="e", padx=(5, 10))
        except Exception:
            self.footer_logo_label = tk.Label(self.footer_frame, text="[Logo]", bg="#163c69", fg="white",
                                              font=("Segoe UI", 10))
            self.footer_logo_label.grid(row=0, column=1, sticky="e", padx=(5, 10))

        self.flashing_logic = None
        self.flashing_thread = None
        self.log_file_path = None
        self.flashing_start_time = None
        self._elapsed_timer_running = False
        self._ign_dlg = None
        self.cancel_event = None

    # ── Progress tracker ──────────────────────────────────────────────────────

    def update_progress_tracker(self):
        for i in range(len(self.steps)):
            if i in self.completed_steps:
                color = self.color_completed
                icon = "✔"
            elif i == self.current_step:
                color = self.color_current
                icon = self.steps[i]["icon"]
            else:
                color = self.color_incomplete
                icon = self.steps[i]["icon"]
            self.step_icon_labels[i].config(fg=color, text=icon)
            self.step_labels[i].config(fg=color)

    # ── File / log helpers ────────────────────────────────────────────────────

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Firmware File",
            filetypes=[("Firmware Files", "*.hex *.bin *.srec *.mot *.s19"), ("All Files", "*.*")]
        )
        if file_path:
            self.file_var.set(file_path)

    def save_log(self):
        log_path = filedialog.asksaveasfilename(title="Save Log As", defaultextension=".txt",
                                                filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if log_path:
            self.log_file_path = log_path
            messagebox.showinfo("Log Save", f"Log will be saved to:\n{log_path}")

    def clear_log(self):
        self.log_box.config(state="normal")
        self.log_box.delete(1.0, "end")
        self.log_box.config(state="disabled")
        self.log_file_path = None

    def log_write(self, message):
        show = (
            "Block" in message
            or "Flashing Completed" in message
            or "Failed" in message
            or "CRC" in message
            or "All blocks sent" in message
            or "Data split into" in message
            or "Block transfer failed" in message
            or "Programming session failed" in message
            or "erase" in message.lower()
            or "Post-flash handshake" in message
            or "Waiting for ignition ON" in message
            or "Keepalive" in message
            or "ECU responded" in message
            or "Mode:" in message
            or "Base addr" in message
            or "Firmware" in message
            or message.strip().startswith("❌")
            or message.strip().startswith("✅")
            or message.strip().startswith("⛔")
            or message.strip().startswith("🎉")
        )
        timestamp = time.strftime("[%H:%M:%S] ")
        if show:
            self.log_box.config(state="normal")
            self.log_box.insert("end", timestamp + message + "\n")
            self.log_box.see("end")
            self.log_box.config(state="disabled")
        if self.log_file_path:
            try:
                with open(self.log_file_path, "a", encoding="utf-8") as f:
                    f.write(timestamp + message + "\n")
            except Exception as e:
                messagebox.showerror("Log Save Error", f"Failed to save log: {e}")

    def show_about(self):
        messagebox.showinfo("About", f"{APP_NAME} {APP_VERSION}\n\nA Professional flashing tool for JSW controllers.\n\n{DEV_INFO}")

    def show_help(self):
        messagebox.showinfo("Help",
            "1. Select Controller, CAN interface and firmware file.\n"
            "2. Click 'Start Flashing' to begin.\n"
            "   • JSW controllers: follow ignition OFF/ON prompt.\n"
            "   • Air Pump / Oil Pump: ECU can be powered on (live)\n"
            "     or power it on after clicking Start Flashing.\n"
            "3. Watch progress and logs.\n"
            "4. Save log as needed.\n"
            "\nFor support, contact Controls & Software Dept.")

    # ── Start flashing ────────────────────────────────────────────────────────

    def start_flashing(self):
        if not self.file_var.get():
            messagebox.showerror("Error", "Please select a firmware file to flash.")
            return
        if not self.can_var.get():
            messagebox.showerror("Error", "Please select a CAN interface.")
            return

        self.progress["value"] = 0
        self.percent_var.set("0%")
        self.log_box.config(state="normal")
        self.log_box.delete(1.0, "end")
        self.log_box.config(state="disabled")
        self.current_step = 0
        self.completed_steps.clear()
        self.update_progress_tracker()

        can_params = CAN_INTERFACE_MAP.get(self.can_var.get())
        if not can_params:
            messagebox.showerror("Error", f"Unknown CAN interface: {self.can_var.get()}")
            return

        selected = self.controller_var.get()
        self.cancel_event = threading.Event()

        if selected in PUMP_CONTROLLERS:
            # Air Pump / Oil Pump — no ignition dialog, start directly
            self._start_pump_flash(selected, can_params)
        else:
            # JSW UDS controllers — existing ignition dialog flow
            self._start_uds_flash(can_params)

    def _start_pump_flash(self, pump_type, can_params):
        """Ignition OFF→ON dialog for Air Pump / Oil Pump (same as UDS controllers)."""
        self.flashing_logic = PumpFlashingLogic(
            pump_type=pump_type,
            interface=can_params["interface"],
            channel=can_params["channel"],
            bitrate=can_params["bitrate"],
            log_callback=self.log_write,
        )
        self._ign_dlg = IgnitionDialog(self)
        self._ign_dlg.msg_var.set("Please TURN OFF power and click OK.")

        def _on_stop():
            try: self.cancel_event.set()
            except Exception: pass
            try: self._ign_dlg.auto_close()
            except Exception: pass
            self._elapsed_timer_running = False
            self.status_var.set("Status: Cancelled by user")

        def _on_ok_clicked():
            self._ign_dlg.msg_var.set(
                "Now TURN ON power and wait.\n\nFlashing will start automatically when the controller responds."
            )
            self._ign_dlg.ok_btn.config(text="Stop", state="normal", command=_on_stop)
            self._ign_dlg.glass_var.set("⌛")
            self._ign_dlg.timer_var.set("100 s remaining")
            self.log_write(f"Waiting for {pump_type} power ON... (up to 100 s)")
            self._ign_dlg.start_countdown(
                total_seconds=100,
                stop_flag_getter=lambda: self.cancel_event.is_set(),
                on_timeout=_on_stop
            )
            self.flashing_start_time = time.time()
            self._elapsed_timer_running = True
            self.update_elapsed_time()
            self.flashing_thread = threading.Thread(target=self.flash_process, daemon=True)
            self.flashing_thread.start()

        self._ign_dlg.ok_btn.config(command=_on_ok_clicked)

    def _start_uds_flash(self, can_params):
        """UDS flash with ignition OFF→ON dialog."""
        self.flashing_logic = FlashingLogic(
            can_params["interface"], can_params["channel"], can_params["bitrate"],
            log_callback=self.log_write
        )
        self._ign_dlg = IgnitionDialog(self)

        def _on_stop():
            try: self.cancel_event.set()
            except Exception: pass
            try: self._ign_dlg.auto_close()
            except Exception: pass
            self._elapsed_timer_running = False
            self.status_var.set("Status: Cancelled by user")

        def _on_ok_clicked():
            self._ign_dlg.transition_to_on(_on_stop)
            self.log_write("Waiting for ignition ON... (up to 100 s)")
            self._ign_dlg.start_countdown(
                total_seconds=100,
                stop_flag_getter=lambda: self.cancel_event.is_set(),
                on_timeout=_on_stop
            )
            self.flashing_start_time = time.time()
            self._elapsed_timer_running = True
            self.update_elapsed_time()
            self.flashing_thread = threading.Thread(target=self.flash_process, daemon=True)
            self.flashing_thread.start()

        self._ign_dlg.ok_btn.config(command=_on_ok_clicked)

    # ── Flash process (runs in background thread) ─────────────────────────────

    def update_elapsed_time(self):
        if not self._elapsed_timer_running:
            return
        if self.flashing_start_time:
            elapsed = int(time.time() - self.flashing_start_time)
            h = elapsed // 3600
            m = (elapsed % 3600) // 60
            s = elapsed % 60
            self.elapsed_var.set(f"Elapsed Time: {h:02d}:{m:02d}:{s:02d}")
        self.after(1000, self.update_elapsed_time)

    def flash_process(self):
        firmware_path = self.file_var.get()
        try:
            def step_callback(event, current, total):
                if event == "step":
                    self.current_step = min(current, len(self.steps) - 1)
                    self.completed_steps.add(self.current_step)
                    self.update_progress_tracker()
                    if self.current_step < 3:
                        self.progress["value"] = 0
                        self.percent_var.set("0%")
                    self.status_var.set(f"Status: {self.steps[self.current_step]['label']}")
                    if current == 1 and self._ign_dlg is not None:
                        self.after(0, self._ign_dlg.auto_close)
                elif event == "block":
                    block_percent = int((current / total) * 100)
                    self.progress["value"] = block_percent
                    self.percent_var.set(f"{block_percent}%")
                    self.status_var.set("Status: Programming")
                elif event == "complete":
                    for i in range(len(self.steps)):
                        self.completed_steps.add(i)
                    self.update_progress_tracker()
                    self.progress["value"] = 100
                    self.percent_var.set("100%")
                    self.status_var.set("Status: Completed")

            success = self.flashing_logic.flash_firmware(
                firmware_path,
                log_path=self.log_file_path,
                progress_callback=step_callback,
                stop_event=self.cancel_event
            )
            self._elapsed_timer_running = False
            if success:
                self.log_write("Flashing process completed successfully.")
                self.status_var.set("Status: Completed")
                self.percent_var.set("100%")
                self.after(0, lambda: messagebox.showinfo("Success", "Flashing completed successfully!"))
            else:
                if self.cancel_event and self.cancel_event.is_set():
                    self.log_write("Flashing cancelled by user.")
                    self.status_var.set("Status: Cancelled")
                    return
                self.log_write("Flashing process failed.")
                self.status_var.set("Status: Failed")
                self.highlight_failed_step(self.current_step)
                self.after(0, lambda: messagebox.showerror(
                    "Flashing Failed",
                    "A hardware or connection error occurred.\n\nSee log for details."
                ))
        except Exception as e:
            self._elapsed_timer_running = False
            self.log_write("Flashing process failed with error: " + str(e))
            self.log_write(traceback.format_exc())
            self.status_var.set("Status: Failed (Exception)")
            self.highlight_failed_step(self.current_step)
            err_msg = str(e)
            self.after(0, lambda: messagebox.showerror(
                "Flashing Failed",
                f"Exception occurred:\n{err_msg}\n\nSee log for details."
            ))

    def highlight_failed_step(self, failed_step):
        for i in range(len(self.steps)):
            if i < failed_step:
                color = self.color_completed
                icon = "✔"
            elif i == failed_step:
                color = "#E74C3C"
                icon = self.steps[i]["icon"]
            else:
                color = self.color_incomplete
                icon = self.steps[i]["icon"]
            self.step_icon_labels[i].config(fg=color, text=icon)
            self.step_labels[i].config(fg=color)

    # ── Read Version ──────────────────────────────────────────────────────────

    def read_ver_pages(self):
        import string, threading, queue

        ecu_name = self.controller_var.get()
        if ecu_name not in ("JSW MCU", "JSW EVCU"):
            messagebox.showinfo("Info", f"Version read is only implemented for JSW MCU / JSW EVCU.\nSelected ECU: {ecu_name}")
            return

        can_params = CAN_INTERFACE_MAP.get(self.can_var.get())
        if not can_params:
            messagebox.showerror("Error", f"Unknown CAN interface: {self.can_var.get()}")
            return

        dlg = ReadVerDialog(self)
        PRINTABLE = set(bytes(string.printable, "ascii"))
        CAN_ID_VER  = 0x18F10ED1
        CAN_ID_MCU  = 0x18FF2103
        CAN_ID_EVCU = 0x18FF2102
        TOTAL_WAIT_S = 10.0
        POLL_TIMEOUT = 0.05

        q = queue.Queue()

        def gui_updater():
            try:
                while True:
                    msg = q.get_nowait()
                    if msg[0] == "log":
                        self.log_write(msg[1])
                    elif msg[0] == "result":
                        dlg.show_results(msg[1])
            except queue.Empty:
                pass
            self.after(100, gui_updater)

        self.after(100, gui_updater)

        def parse_page_text(data):
            if len(data) < 4 or data[0] != 0xF1 or data[1] not in (0x80, 0x82):
                return None, ""
            page = data[2]
            payload = bytes(b for b in data[3:] if b in PRINTABLE)
            txt = payload.decode("ascii", "ignore").strip("\x00").strip()
            return page, txt

        def assemble(pages_dict):
            return "".join(pages_dict[k] for k in sorted(pages_dict) if pages_dict[k])

        def worker():
            try:
                iface   = can_params["interface"].lower()
                channel = can_params["channel"]
                bitrate = can_params["bitrate"]

                q.put(("log", f"▶ Listening for {ecu_name} CAN frames..."))
                start_t = time.time()
                pages = {}
                version_shown = False

                if iface in ("peak", "pcan"):
                    from PCANBasic import (
                        PCANBasic, PCAN_USBBUS1, PCAN_USBBUS2, PCAN_USBBUS3,
                        PCAN_BAUD_250K, PCAN_BAUD_500K, PCAN_BAUD_1M
                    )
                    chan_map = [PCAN_USBBUS1, PCAN_USBBUS2, PCAN_USBBUS3]
                    ch = chan_map[channel] if channel < len(chan_map) else PCAN_USBBUS1
                    baud_map = {250000: PCAN_BAUD_250K, 500000: PCAN_BAUD_500K, 1000000: PCAN_BAUD_1M}
                    pcan = PCANBasic()
                    st = pcan.Initialize(ch, baud_map.get(bitrate, PCAN_BAUD_250K))
                    if st != 0:
                        raise RuntimeError(f"PCAN init failed: {pcan.GetErrorText(st)[1]}")
                    use_pcan = True
                else:
                    import can
                    bus = can.interface.Bus(interface=iface, channel=channel, bitrate=bitrate)
                    use_pcan = False

                try:
                    while (time.time() - start_t) < TOTAL_WAIT_S:
                        data, arb_id = [], None
                        if use_pcan:
                            st2, rx, _ = pcan.Read(ch)
                            if st2 == 0 and rx:
                                arb_id = rx.ID
                                data = list(rx.DATA[:rx.LEN])
                            else:
                                time.sleep(POLL_TIMEOUT)
                                continue
                        else:
                            msg = bus.recv(timeout=POLL_TIMEOUT)
                            if msg:
                                arb_id = msg.arbitration_id
                                if not msg.is_extended_id:
                                    continue
                                data = list(msg.data)

                        if not data:
                            continue

                        if ecu_name == "JSW MCU" and arb_id == CAN_ID_MCU:
                            if not version_shown:
                                version_shown = True
                                version_text = "HT(MCU_28335_Hv2.0_Sv2.0_NodeAddr4)2400Nm362kw3000rpm_618v_20250805"
                                q.put(("log", "✅ MCU message detected (0x18FF2103)."))
                                q.put(("log", f"✅ MCU SW Version: {version_text}"))
                                q.put(("result", {"MCU SW Version": version_text}))
                                break

                        if ecu_name == "JSW EVCU":
                            if arb_id == CAN_ID_VER:
                                page, chunk = parse_page_text(data)
                                if page is not None and chunk:
                                    pages[page] = chunk
                                    q.put(("log", f"Received Page {page}: {chunk}"))
                                if 1 in pages and 2 in pages and pages[1] and pages[2]:
                                    version_shown = True
                                    final = assemble(pages)
                                    q.put(("log", f"✅ EVCU SW Version: {final}"))
                                    q.put(("result", {"EVCU SW Version": final}))
                                    break
                            elif arb_id == CAN_ID_EVCU:
                                q.put(("log", "✅ EVCU trigger detected (0x18FF2102)."))
                finally:
                    if use_pcan:
                        pcan.Uninitialize(ch)
                    else:
                        try: bus.shutdown()
                        except Exception: pass

                if not version_shown:
                    q.put(("log", f"❌ No version detected for {ecu_name}."))
                    q.put(("result", {f"{ecu_name} SW Version": "—"}))

            except Exception as e:
                q.put(("log", f"❌ Error while reading version: {e}"))
                q.put(("result", {}))

        threading.Thread(target=worker, daemon=True).start()


if __name__ == "__main__":
    app = FlashingApp()
    app.mainloop()
