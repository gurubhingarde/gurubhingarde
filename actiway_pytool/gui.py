"""Tkinter GUI for the Actiway-style download tool.

Thin presentation layer over the GUI-free core (uds / firmware / crypto /
transport). Runs the flash on a worker thread so the window stays responsive,
and streams the UDS log live. Tkinter ships with CPython on Windows/macOS and
is `apt install python3-tk` on Linux.
"""
from __future__ import annotations

import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from . import __version__, config, crypto, firmware
from .transport.base import TransportError
from .transport.simulator import SimulatorTransport
from .uds import FlashConfig, FlashSequencer, UdsClient, UdsError


def _int(s, default=0):
    try:
        return int(str(s), 0)
    except ValueError:
        return default


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"Actiway Download Tool (Python) v{__version__}")
        self.geometry("920x680")
        self.minsize(820, 560)

        self._logq: queue.Queue[str] = queue.Queue()
        self._worker: threading.Thread | None = None
        self._abort = threading.Event()
        self._block: firmware.ReprogrammingBlock | None = None

        self._build()
        self.after(60, self._drain_log)

    # ---- layout -----------------------------------------------------------
    def _build(self):
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=False, padx=8, pady=(8, 4))

        self._build_transport_tab(nb)
        self._build_flash_tab(nb)
        self._build_crypto_tab(nb)

        # action bar
        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=8)
        self.btn_info = ttk.Button(bar, text="Read ECU Info", command=self.on_info)
        self.btn_flash = ttk.Button(bar, text="Flash", command=self.on_flash)
        self.btn_abort = ttk.Button(bar, text="Abort", command=self.on_abort, state="disabled")
        self.btn_info.pack(side="left")
        self.btn_flash.pack(side="left", padx=6)
        self.btn_abort.pack(side="left")
        self.progress = ttk.Progressbar(bar, mode="determinate", length=320)
        self.progress.pack(side="right", padx=4)
        self.pct = ttk.Label(bar, text="0%")
        self.pct.pack(side="right")

        # log
        frame = ttk.LabelFrame(self, text="Log")
        frame.pack(fill="both", expand=True, padx=8, pady=8)
        self.log = tk.Text(frame, height=16, wrap="none", font=("Consolas", 9))
        ys = ttk.Scrollbar(frame, orient="vertical", command=self.log.yview)
        self.log.configure(yscrollcommand=ys.set)
        self.log.pack(side="left", fill="both", expand=True)
        ys.pack(side="right", fill="y")

    def _build_transport_tab(self, nb):
        tab = ttk.Frame(nb); nb.add(tab, text="Transport")
        self.var_transport = tk.StringVar(value="Simulator")
        ttk.Label(tab, text="Transport:").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        cb = ttk.Combobox(tab, textvariable=self.var_transport, state="readonly",
                          values=["Simulator", "CAN / CAN-FD", "DoIP"])
        cb.grid(row=0, column=1, sticky="w"); cb.bind("<<ComboboxSelected>>", self._sync)

        # CAN params
        self.var_can_bustype = tk.StringVar(value="pcan")
        self.var_can_channel = tk.StringVar(value="PCAN_USBBUS1")
        self.var_can_fd = tk.BooleanVar(value=True)
        self.var_can_req = tk.StringVar(value="0x18DA10F9")
        self.var_can_resp = tk.StringVar(value="0x18DAF910")
        self.var_can_bitrate = tk.StringVar(value="500000")
        self.var_can_dbitrate = tk.StringVar(value="2000000")

        self.can_frame = ttk.LabelFrame(tab, text="CAN / CAN-FD")
        self.can_frame.grid(row=1, column=0, columnspan=4, sticky="we", padx=6, pady=6)
        rows = [("Driver (bustype)", self.var_can_bustype),
                ("Channel", self.var_can_channel),
                ("Request ID", self.var_can_req),
                ("Response ID", self.var_can_resp),
                ("Arb bitrate", self.var_can_bitrate),
                ("Data bitrate (FD)", self.var_can_dbitrate)]
        for i, (lbl, var) in enumerate(rows):
            ttk.Label(self.can_frame, text=lbl).grid(row=i, column=0, sticky="w", padx=4, pady=2)
            ttk.Entry(self.can_frame, textvariable=var, width=18).grid(row=i, column=1, sticky="w")
        ttk.Checkbutton(self.can_frame, text="CAN-FD", variable=self.var_can_fd)\
            .grid(row=0, column=2, padx=10)

        # DoIP params
        self.var_doip_host = tk.StringVar(value="192.168.1.100")
        self.var_doip_port = tk.StringVar(value="13400")
        self.var_doip_sa = tk.StringVar(value="0x0E80")
        self.var_doip_ta = tk.StringVar(value="0x1000")
        self.doip_frame = ttk.LabelFrame(tab, text="DoIP")
        self.doip_frame.grid(row=2, column=0, columnspan=4, sticky="we", padx=6, pady=6)
        rows = [("ECU host/IP", self.var_doip_host), ("Port", self.var_doip_port),
                ("Source addr", self.var_doip_sa), ("Target addr", self.var_doip_ta)]
        for i, (lbl, var) in enumerate(rows):
            ttk.Label(self.doip_frame, text=lbl).grid(row=i, column=0, sticky="w", padx=4, pady=2)
            ttk.Entry(self.doip_frame, textvariable=var, width=18).grid(row=i, column=1, sticky="w")
        self._sync()

    def _build_flash_tab(self, nb):
        tab = ttk.Frame(nb); nb.add(tab, text="Flash")
        # firmware picker
        self.var_file = tk.StringVar()
        ttk.Label(tab, text="Firmware:").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        ttk.Entry(tab, textvariable=self.var_file, width=58).grid(row=0, column=1, sticky="we")
        ttk.Button(tab, text="Browse...", command=self.on_browse).grid(row=0, column=2, padx=4)

        # preset
        self.var_preset = tk.StringVar(value=config.PRESETS[0].desc)
        ttk.Label(tab, text="Preset:").grid(row=1, column=0, sticky="w", padx=6)
        ttk.Combobox(tab, textvariable=self.var_preset, state="readonly", width=40,
                     values=[p.desc for p in config.PRESETS])\
            .grid(row=1, column=1, sticky="w", pady=4)

        # zone
        self.var_zone = tk.StringVar(value=config.ZONES[0].name)
        ttk.Label(tab, text="Zone:").grid(row=2, column=0, sticky="w", padx=6)
        ttk.Combobox(tab, textvariable=self.var_zone, state="readonly", width=40,
                     values=[f"{z.index}: {z.name}" for z in config.ZONES])\
            .grid(row=2, column=1, sticky="w", pady=4)

        # config grid
        cf = ttk.LabelFrame(tab, text="Download config (from original *.exe.config)")
        cf.grid(row=3, column=0, columnspan=3, sticky="we", padx=6, pady=8)
        self.var_seckey = tk.StringVar(value="0xFFFF")
        self.var_session = tk.StringVar(value="0x02")
        self.var_addrlen = tk.StringVar(value="4")
        self.var_sizelen = tk.StringVar(value="4")
        self.var_tool_sa = tk.StringVar(value="0xF9")
        self.var_lzo = tk.BooleanVar(value=False)
        grid = [("SecKey", self.var_seckey), ("Programming session", self.var_session),
                ("Addr length", self.var_addrlen), ("Size length", self.var_sizelen),
                ("Tool SA", self.var_tool_sa)]
        for i, (lbl, var) in enumerate(grid):
            ttk.Label(cf, text=lbl).grid(row=i // 2, column=(i % 2) * 2, sticky="w", padx=4, pady=3)
            ttk.Entry(cf, textvariable=var, width=12).grid(row=i // 2, column=(i % 2) * 2 + 1, sticky="w")
        ttk.Checkbutton(cf, text="LZO compress", variable=self.var_lzo)\
            .grid(row=3, column=0, sticky="w", padx=4, pady=3)

        # segment view
        sv = ttk.LabelFrame(tab, text="Parsed segments")
        sv.grid(row=4, column=0, columnspan=3, sticky="nswe", padx=6, pady=6)
        self.seg_tree = ttk.Treeview(sv, columns=("start", "end", "size"),
                                     show="headings", height=6)
        for c, t in (("start", "Start"), ("end", "End"), ("size", "Size")):
            self.seg_tree.heading(c, text=t)
            self.seg_tree.column(c, width=160, anchor="w")
        self.seg_tree.pack(fill="both", expand=True)
        tab.columnconfigure(1, weight=1)
        tab.rowconfigure(4, weight=1)

    def _build_crypto_tab(self, nb):
        tab = ttk.Frame(nb); nb.add(tab, text="Crypto / Checksum")
        self.var_aes_pass = tk.StringVar(value=crypto.DEFAULT_AES_PASSPHRASE)
        self.var_aes_mode = tk.StringVar(value="CBC")
        self.var_crc_poly = tk.StringVar(value="0xEDB88320")
        self.var_crc_init = tk.StringVar(value="0xFFFFFFFF")
        self.var_crc_xor = tk.StringVar(value="0xFFFFFFFF")
        rows = [("AES passphrase", self.var_aes_pass), ("AES mode (CBC/ECB)", self.var_aes_mode),
                ("CRC poly", self.var_crc_poly), ("CRC init", self.var_crc_init),
                ("CRC xorout", self.var_crc_xor)]
        for i, (lbl, var) in enumerate(rows):
            ttk.Label(tab, text=lbl).grid(row=i, column=0, sticky="w", padx=6, pady=4)
            ttk.Entry(tab, textvariable=var, width=24).grid(row=i, column=1, sticky="w")
        ttk.Label(tab, text="(These are recovered defaults; adjust to match your ECU.)",
                  foreground="#666").grid(row=len(rows), column=0, columnspan=2, sticky="w", padx=6, pady=8)

    # ---- helpers ----------------------------------------------------------
    def _sync(self, *_):
        t = self.var_transport.get()
        state_can = "normal" if t.startswith("CAN") else "disabled"
        state_doip = "normal" if t == "DoIP" else "disabled"
        for w in self.can_frame.winfo_children():
            try: w.configure(state=state_can)
            except tk.TclError: pass
        for w in self.doip_frame.winfo_children():
            try: w.configure(state=state_doip)
            except tk.TclError: pass

    def _flash_config(self) -> FlashConfig:
        crc = crypto.Crc32Config(poly=_int(self.var_crc_poly.get(), 0xEDB88320),
                                 init=_int(self.var_crc_init.get(), 0xFFFFFFFF),
                                 xorout=_int(self.var_crc_xor.get(), 0xFFFFFFFF))
        aes = crypto.AesConfig(passphrase=self.var_aes_pass.get(),
                               mode=self.var_aes_mode.get())
        return FlashConfig(sec_key=_int(self.var_seckey.get(), 0xFFFF),
                           programming_session=_int(self.var_session.get(), 0x02),
                           addr_len=_int(self.var_addrlen.get(), 4),
                           size_len=_int(self.var_sizelen.get(), 4),
                           use_lzo=self.var_lzo.get(), crc=crc, aes=aes)

    def _make_transport(self):
        t = self.var_transport.get()
        log = self._logq.put
        if t == "Simulator":
            return SimulatorTransport(sec_key=_int(self.var_seckey.get(), 0xFFFF), log=log)
        if t.startswith("CAN"):
            from .transport.can_isotp import CanIsoTpTransport
            return CanIsoTpTransport(
                channel=self.var_can_channel.get(), bustype=self.var_can_bustype.get(),
                req_id=_int(self.var_can_req.get()), resp_id=_int(self.var_can_resp.get()),
                is_fd=self.var_can_fd.get(), bitrate=_int(self.var_can_bitrate.get(), 500000),
                data_bitrate=_int(self.var_can_dbitrate.get(), 2000000), log=log)
        from .transport.doip import DoIPTransport
        return DoIPTransport(host=self.var_doip_host.get(), port=_int(self.var_doip_port.get(), 13400),
                             source_addr=_int(self.var_doip_sa.get()),
                             target_addr=_int(self.var_doip_ta.get()), log=log)

    # ---- actions ----------------------------------------------------------
    def on_browse(self):
        path = filedialog.askopenfilename(
            title="Select firmware",
            filetypes=[("Firmware", "*.s19 *.s28 *.s37 *.srec *.mot *.hex *.bin"),
                       ("All files", "*.*")])
        if not path:
            return
        self.var_file.set(path)
        try:
            self._block = firmware.load_firmware(path)
        except Exception as e:
            messagebox.showerror("Parse error", str(e)); return
        for i in self.seg_tree.get_children():
            self.seg_tree.delete(i)
        for s in self._block.segments:
            self.seg_tree.insert("", "end", values=(f"0x{s.start_addr:08X}",
                                                     f"0x{s.end_addr:08X}", f"{s.size}"))
        self._logq.put(f"Loaded {self._block.file_type} '{self._block.name}': "
                       f"{len(self._block.segments)} segment(s), {self._block.total_size} bytes")

    def on_info(self):
        self._run(self._do_info)

    def on_flash(self):
        if not self._block:
            messagebox.showwarning("No firmware", "Load a firmware file first."); return
        self._run(self._do_flash)

    def on_abort(self):
        self._abort.set()
        self._logq.put("** abort requested **")

    def _run(self, fn):
        if self._worker and self._worker.is_alive():
            return
        self._abort.clear()
        self.btn_flash.configure(state="disabled")
        self.btn_info.configure(state="disabled")
        self.btn_abort.configure(state="normal")
        self._worker = threading.Thread(target=self._wrap, args=(fn,), daemon=True)
        self._worker.start()

    def _wrap(self, fn):
        try:
            fn()
        except (UdsError, TransportError) as e:
            self._logq.put(f"ERROR: {e}")
        except Exception as e:  # pragma: no cover
            self._logq.put(f"UNEXPECTED: {e!r}")
        finally:
            self._logq.put("__DONE__")

    def _do_info(self):
        t = self._make_transport()
        with t:
            c = UdsClient(t, log=self._logq.put)
            c.diagnostic_session(0x03)
            for did, name in config.INFO_DIDS.items():
                try:
                    val = c.read_did(did)
                    self._logq.put(f"  {did:04X} {name}: {val!r}")
                except Exception as e:
                    self._logq.put(f"  {did:04X} {name}: {e}")

    def _do_flash(self):
        cfg = self._flash_config()
        t = self._make_transport()

        def prog(done, total):
            pct = int(done * 100 / total) if total else 0
            self._logq.put(f"__PROG__{pct}")

        with t:
            c = UdsClient(t, log=self._logq.put)
            seq = FlashSequencer(c, cfg, progress=prog)
            for i, s in enumerate(list(self._block.segments)):
                if self._abort.is_set():
                    self._logq.put("aborted before completion"); return
            digest = seq.run(self._block)
            self._logq.put(f"FLASH COMPLETE — image CRC-32 = {digest}")

    # ---- log pump ---------------------------------------------------------
    def _drain_log(self):
        try:
            while True:
                msg = self._logq.get_nowait()
                if msg == "__DONE__":
                    self.btn_flash.configure(state="normal")
                    self.btn_info.configure(state="normal")
                    self.btn_abort.configure(state="disabled")
                elif msg.startswith("__PROG__"):
                    pct = int(msg[8:])
                    self.progress["value"] = pct
                    self.pct.configure(text=f"{pct}%")
                else:
                    self.log.insert("end", msg + "\n")
                    self.log.see("end")
        except queue.Empty:
            pass
        self.after(60, self._drain_log)


def main():
    App().mainloop()


if __name__ == "__main__":
    main()
