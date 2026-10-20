"""Tkinter desktop GUI for dltool.

A thin front-end over the same library the CLI uses: discover DoIP entities,
connect, read version identifiers, and flash an S-record firmware file with a
progress bar. Long operations run on worker threads so the window stays
responsive; all widget updates are marshalled back to the Tk main thread.

Run with:  ``dltool-gui``  or  ``python -m dltool.gui``
"""

from __future__ import annotations

import queue
import threading
import traceback
from typing import Callable, Optional

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from . import security
from .config import Config
from .firmware import parse_srecord_file
from .hexutil import bytes_to_hex, parse_addr, to_ascii
from .uds.client import UdsClient
from .uds.services import COMMON_DIDS, Session


class DltoolGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("dltool — DoIP / CAN ECU tool")
        self.geometry("820x600")
        self.minsize(720, 520)

        self._events: "queue.Queue[Callable[[], None]]" = queue.Queue()
        self._busy = False

        self._build_widgets()
        self.after(50, self._drain_events)

    # -- layout ---------------------------------------------------------------
    def _build_widgets(self) -> None:
        pad = dict(padx=6, pady=4)

        # Transport / connection frame
        conn = ttk.LabelFrame(self, text="Connection")
        conn.pack(fill="x", **pad)

        self.transport = tk.StringVar(value="doip")
        ttk.Radiobutton(conn, text="DoIP (Ethernet)", variable=self.transport,
                        value="doip", command=self._sync_transport).grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(conn, text="CAN / CAN-FD", variable=self.transport,
                        value="can", command=self._sync_transport).grid(row=0, column=1, sticky="w")

        # DoIP fields
        self.doip_frame = ttk.Frame(conn)
        self.doip_frame.grid(row=1, column=0, columnspan=4, sticky="we")
        self.ecu_ip = self._labeled_entry(self.doip_frame, "ECU IP:", 0, "")
        self.bind_ip = self._labeled_entry(self.doip_frame, "Local NIC IP:", 1, "")
        self.tester_addr = self._labeled_entry(self.doip_frame, "Tester addr:", 2, "0x0E00", width=10)
        self.ecu_addr = self._labeled_entry(self.doip_frame, "ECU addr:", 3, "0x0E80", width=10)

        # CAN fields
        self.can_frame = ttk.Frame(conn)
        self.can_iface = self._labeled_entry(self.can_frame, "Interface:", 0, "pcan", width=12)
        self.can_channel = self._labeled_entry(self.can_frame, "Channel:", 1, "0", width=12)
        self.can_tx = self._labeled_entry(self.can_frame, "TX id:", 2, "0x18DA00F9", width=12)
        self.can_rx = self._labeled_entry(self.can_frame, "RX id:", 3, "0x18DAF900", width=12)
        self.can_fd = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.can_frame, text="CAN-FD", variable=self.can_fd).grid(row=0, column=4, padx=6)

        btns = ttk.Frame(conn)
        btns.grid(row=2, column=0, columnspan=4, sticky="w", pady=4)
        self.btn_discover = ttk.Button(btns, text="Discover", command=self.on_discover)
        self.btn_discover.pack(side="left", padx=3)
        self.btn_connect = ttk.Button(btns, text="Read ECU Info", command=self.on_info)
        self.btn_connect.pack(side="left", padx=3)

        # Firmware / flash frame
        flashf = ttk.LabelFrame(self, text="Firmware flash")
        flashf.pack(fill="x", **pad)
        self.fw_path = tk.StringVar()
        ttk.Entry(flashf, textvariable=self.fw_path).grid(row=0, column=0, sticky="we", padx=6, pady=4)
        ttk.Button(flashf, text="Browse…", command=self.on_browse).grid(row=0, column=1, padx=3)
        ttk.Button(flashf, text="Inspect", command=self.on_inspect).grid(row=0, column=2, padx=3)
        flashf.columnconfigure(0, weight=1)

        opts = ttk.Frame(flashf)
        opts.grid(row=1, column=0, columnspan=3, sticky="w")
        self.sec_algo = tk.StringVar(value="passthrough")
        ttk.Label(opts, text="Security algo:").pack(side="left", padx=(6, 2))
        ttk.Combobox(opts, textvariable=self.sec_algo, values=security.available(),
                     width=14, state="readonly").pack(side="left")
        self.sec_level = self._inline_entry(opts, "Level:", "0x01", 6)
        self.block_size = self._inline_entry(opts, "Block:", "0x400", 8)
        self.btn_flash = ttk.Button(opts, text="FLASH", command=self.on_flash)
        self.btn_flash.pack(side="left", padx=10)

        self.progress = ttk.Progressbar(flashf, mode="determinate")
        self.progress.grid(row=2, column=0, columnspan=3, sticky="we", padx=6, pady=4)

        # Log output
        logf = ttk.LabelFrame(self, text="Log")
        logf.pack(fill="both", expand=True, **pad)
        self.log = tk.Text(logf, height=12, wrap="word", state="disabled",
                           bg="#101418", fg="#d6dee6", insertbackground="#d6dee6")
        self.log.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(logf, command=self.log.yview)
        sb.pack(side="right", fill="y")
        self.log.config(yscrollcommand=sb.set)

        self.status = tk.StringVar(value="Ready.")
        ttk.Label(self, textvariable=self.status, relief="sunken", anchor="w").pack(fill="x")

        self._sync_transport()

    def _labeled_entry(self, parent, label, col, default, width=18):
        ttk.Label(parent, text=label).grid(row=0, column=col * 2, sticky="e", padx=(6, 2), pady=3)
        var = tk.StringVar(value=default)
        ttk.Entry(parent, textvariable=var, width=width).grid(row=0, column=col * 2 + 1, sticky="w")
        return var

    def _inline_entry(self, parent, label, default, width):
        ttk.Label(parent, text=label).pack(side="left", padx=(10, 2))
        var = tk.StringVar(value=default)
        ttk.Entry(parent, textvariable=var, width=width).pack(side="left")
        return var

    def _sync_transport(self):
        if self.transport.get() == "doip":
            self.can_frame.grid_forget()
            self.doip_frame.grid(row=1, column=0, columnspan=4, sticky="we")
            self.btn_discover.state(["!disabled"])
        else:
            self.doip_frame.grid_forget()
            self.can_frame.grid(row=1, column=0, columnspan=4, sticky="we")
            self.btn_discover.state(["disabled"])

    # -- thread/event plumbing ------------------------------------------------
    def _post(self, fn: Callable[[], None]) -> None:
        """Queue a callable to run on the Tk main thread."""
        self._events.put(fn)

    def _drain_events(self) -> None:
        try:
            while True:
                self._events.get_nowait()()
        except queue.Empty:
            pass
        self.after(50, self._drain_events)

    def logln(self, text: str) -> None:
        def _append():
            self.log.config(state="normal")
            self.log.insert("end", text + "\n")
            self.log.see("end")
            self.log.config(state="disabled")
        self._post(_append)

    def set_status(self, text: str) -> None:
        self._post(lambda: self.status.set(text))

    def set_progress(self, done: int, total: int) -> None:
        def _p():
            self.progress.config(maximum=max(total, 1), value=done)
        self._post(_p)

    def _run_worker(self, fn: Callable[[], None]) -> None:
        if self._busy:
            messagebox.showinfo("Busy", "An operation is already running.")
            return
        self._busy = True
        self.set_status("Working…")

        def wrap():
            try:
                fn()
            except Exception as exc:  # noqa: BLE001
                self.logln(f"ERROR: {exc}")
                self.logln(traceback.format_exc())
                self.set_status(f"Error: {exc}")
            finally:
                self._busy = False
                self._post(lambda: self.set_status("Ready."))

        threading.Thread(target=wrap, daemon=True).start()

    # -- config from widgets --------------------------------------------------
    def _config(self) -> Config:
        cfg = Config()
        cfg.transport = self.transport.get()
        if cfg.transport == "doip":
            cfg.doip_host = self.ecu_ip.get().strip()
            cfg.doip_bind_addr = self.bind_ip.get().strip() or "0.0.0.0"
            cfg.tester_addr = parse_addr(self.tester_addr.get())
            cfg.ecu_addr = parse_addr(self.ecu_addr.get())
        else:
            cfg.can_interface = self.can_iface.get().strip()
            cfg.can_channel = self.can_channel.get().strip()
            cfg.can_tx_id = parse_addr(self.can_tx.get())
            cfg.can_rx_id = parse_addr(self.can_rx.get())
            cfg.can_fd = bool(self.can_fd.get())
            cfg.can_extended_id = cfg.can_tx_id > 0x7FF
        return cfg

    def _open_client(self, cfg: Config):
        from .transport.factory import build_transport
        t = build_transport(cfg)
        t.open()
        return t, UdsClient(t, p2_timeout=cfg.p2_timeout, p2_star_timeout=cfg.p2_star_timeout)

    # -- actions --------------------------------------------------------------
    def on_discover(self):
        def work():
            from .transport.doip_discovery import discover
            bind = self.bind_ip.get().strip() or "0.0.0.0"
            self.logln(f"Discovering DoIP entities (bind {bind})…")
            ents = discover(timeout=3.0, bind_addr=bind)
            if not ents:
                self.logln("No entities responded. Check NIC, subnet and UDP 13400 firewall.")
                return
            for e in ents:
                self.logln("  " + str(e))
            first = ents[0]
            self._post(lambda: (self.ecu_ip.set(first.ip_address),
                                self.ecu_addr.set(f"0x{first.logical_address:04X}")))
            self.logln(f"Filled ECU IP/addr from first entity ({first.ip_address}).")
        self._run_worker(work)

    def on_info(self):
        cfg = self._config()

        def work():
            self.logln(f"Connecting via {cfg.transport}…")
            t, client = self._open_client(cfg)
            try:
                client.diagnostic_session_control(Session.EXTENDED)
                self.logln("Connected. Reading identifiers:")
                for did, val in client.read_identifiers(list(COMMON_DIDS)).items():
                    name = COMMON_DIDS.get(did, "")
                    if isinstance(val, Exception):
                        self.logln(f"  0x{did:04X} {name:<34} -- {val}")
                    else:
                        self.logln(f"  0x{did:04X} {name:<34} {to_ascii(val)!r} [{bytes_to_hex(val)}]")
            finally:
                t.close()
        self._run_worker(work)

    def on_browse(self):
        path = filedialog.askopenfilename(
            title="Select firmware",
            filetypes=[("S-record", "*.s19 *.srec *.mot *.s28 *.s37 *.hex"), ("All files", "*.*")],
        )
        if path:
            self.fw_path.set(path)

    def on_inspect(self):
        path = self.fw_path.get().strip()
        if not path:
            messagebox.showinfo("No file", "Choose a firmware file first.")
            return

        def work():
            fw = parse_srecord_file(path)
            self.logln(f"{path}: {len(fw.blocks)} block(s), {fw.total_size} bytes")
            for b in fw.blocks:
                for s in b.segments:
                    self.logln(f"  0x{s.start_addr:08X}..0x{s.end_addr:08X}  ({s.size} bytes)")
        self._run_worker(work)

    def on_flash(self):
        path = self.fw_path.get().strip()
        if not path:
            messagebox.showinfo("No file", "Choose a firmware file first.")
            return
        if not messagebox.askyesno(
            "Confirm flash",
            "Flashing can render an ECU inoperable if interrupted or wrong.\n\n"
            "Ensure stable power and the correct file. Continue?",
        ):
            return
        cfg = self._config()
        cfg.block_size = parse_addr(self.block_size.get())
        cfg.security_level = parse_addr(self.sec_level.get())
        key_fn = security.get(self.sec_algo.get())

        def work():
            from .flash import flash_firmware
            fw = parse_srecord_file(path)
            self.logln(f"Flashing {path} ({fw.total_size} bytes)…")

            def prog(label, done, total):
                self.set_progress(done, total)
                self.set_status(f"{label}: {done}/{total}")

            t, client = self._open_client(cfg)
            try:
                flash_firmware(client, fw, cfg, key_fn, progress=prog, reset=True)
                self.logln("Flash complete.")
                self.set_progress(1, 1)
            finally:
                t.close()
        self._run_worker(work)


def main() -> int:
    app = DltoolGui()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
