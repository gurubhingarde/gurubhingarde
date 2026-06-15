#!/usr/bin/env python3
"""
hex_rebase_gui.py  —  GUI tool to shift the load address of an Intel HEX firmware file.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import threading


def ihex_checksum(record_bytes):
    return ((~sum(record_bytes) + 1) & 0xFF)


def rebase_hex(src_path, dst_path, from_base, to_base, log_fn):
    offset = to_base - from_base
    log_fn(f"Input  : {os.path.basename(src_path)}")
    log_fn(f"Output : {os.path.basename(dst_path)}")
    log_fn(f"Shift  : 0x{from_base:08X} → 0x{to_base:08X}  (offset {offset:+d})")

    records_in = 0
    records_mod = 0
    ela = 0
    out_lines = []

    with open(src_path) as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line.startswith(':'):
                out_lines.append(line)
                continue

            bc   = int(line[1:3],  16)
            addr = int(line[3:7],  16)
            rt   = int(line[7:9],  16)
            data = bytes.fromhex(line[9:9 + bc * 2])
            records_in += 1

            if rt == 4:
                ela = int.from_bytes(data, "big") << 16
                out_lines.append(line)
                continue

            if rt != 0:
                out_lines.append(line)
                continue

            full_addr     = ela | addr
            new_full_addr = full_addr + offset
            new_ela       = new_full_addr & 0xFFFF0000
            new_addr16    = new_full_addr & 0x0000FFFF

            if new_ela != ela:
                new_ela_data = (new_ela >> 16).to_bytes(2, "big")
                ela_body     = bytes([0x02, 0x00, 0x00, 0x04]) + new_ela_data
                ela_cs       = ihex_checksum(ela_body)
                out_lines.append(f":{ela_body.hex().upper()}{ela_cs:02X}")
                ela = new_ela
                log_fn(f"⚠  ELA boundary crossed at 0x{full_addr:08X} — new ELA 0x{new_ela >> 16:04X}")

            body = bytes([bc,
                          (new_addr16 >> 8) & 0xFF,
                           new_addr16       & 0xFF,
                          rt]) + data
            cs   = ihex_checksum(body)
            out_lines.append(f":{body.hex().upper()}{cs:02X}")
            records_mod += 1

    with open(dst_path, "w") as f:
        for l in out_lines:
            f.write(l + "\n")

    log_fn(f"Records processed  : {records_in}")
    log_fn(f"Data records moved : {records_mod}")
    log_fn(f"✅ Done → {dst_path}")


class HexRebaseApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HEX Rebase Tool")
        self.geometry("640x520")
        self.resizable(False, False)
        self.configure(bg="#f6f8fb")

        # ── Header ──────────────────────────────────────────────────────────
        tk.Label(self, text="HEX Rebase Tool", font=("Segoe UI", 22, "bold"),
                 bg="#f6f8fb", fg="#163c69").pack(pady=(24, 2))
        tk.Label(self, text="Shift Intel HEX firmware load address",
                 font=("Segoe UI", 11), bg="#f6f8fb", fg="#6b7a99").pack(pady=(0, 18))

        form = tk.Frame(self, bg="#f6f8fb")
        form.pack(padx=40, fill="x")

        # ── Input file ──────────────────────────────────────────────────────
        tk.Label(form, text="Input HEX File", font=("Segoe UI", 11, "bold"),
                 bg="#f6f8fb", fg="#1f355e").grid(row=0, column=0, sticky="w", pady=6)
        self.src_var = tk.StringVar()
        tk.Entry(form, textvariable=self.src_var, state="readonly", width=38,
                 font=("Segoe UI", 11)).grid(row=0, column=1, padx=8, pady=6)
        tk.Button(form, text="Browse", command=self._browse_src,
                  bg="#154385", fg="white", font=("Segoe UI", 10, "bold"),
                  relief="flat", cursor="hand2", width=8).grid(row=0, column=2, pady=6)

        # ── Output file ─────────────────────────────────────────────────────
        tk.Label(form, text="Output HEX File", font=("Segoe UI", 11, "bold"),
                 bg="#f6f8fb", fg="#1f355e").grid(row=1, column=0, sticky="w", pady=6)
        self.dst_var = tk.StringVar()
        tk.Entry(form, textvariable=self.dst_var, state="readonly", width=38,
                 font=("Segoe UI", 11)).grid(row=1, column=1, padx=8, pady=6)
        tk.Button(form, text="Browse", command=self._browse_dst,
                  bg="#154385", fg="white", font=("Segoe UI", 10, "bold"),
                  relief="flat", cursor="hand2", width=8).grid(row=1, column=2, pady=6)

        # ── From address ────────────────────────────────────────────────────
        tk.Label(form, text="From Address", font=("Segoe UI", 11, "bold"),
                 bg="#f6f8fb", fg="#1f355e").grid(row=2, column=0, sticky="w", pady=6)
        self.from_var = tk.StringVar(value="0x3E8000")
        tk.Entry(form, textvariable=self.from_var, width=20,
                 font=("Segoe UI", 11)).grid(row=2, column=1, padx=8, pady=6, sticky="w")

        # ── To address ──────────────────────────────────────────────────────
        tk.Label(form, text="To Address", font=("Segoe UI", 11, "bold"),
                 bg="#f6f8fb", fg="#1f355e").grid(row=3, column=0, sticky="w", pady=6)
        self.to_var = tk.StringVar(value="0x3EA000")
        tk.Entry(form, textvariable=self.to_var, width=20,
                 font=("Segoe UI", 11)).grid(row=3, column=1, padx=8, pady=6, sticky="w")

        # ── Quick presets ────────────────────────────────────────────────────
        preset_frame = tk.Frame(self, bg="#f6f8fb")
        preset_frame.pack(padx=40, fill="x", pady=(4, 0))
        tk.Label(preset_frame, text="Quick Presets:", font=("Segoe UI", 10, "bold"),
                 bg="#f6f8fb", fg="#6b7a99").pack(side="left")
        tk.Button(preset_frame, text="VER1→VER2  (0x3E8000→0x3EA000)",
                  command=lambda: self._set_preset("0x3E8000", "0x3EA000"),
                  bg="#e8edf7", fg="#154385", font=("Segoe UI", 10),
                  relief="flat", cursor="hand2").pack(side="left", padx=8)
        tk.Button(preset_frame, text="VER2→VER1  (0x3EA000→0x3E8000)",
                  command=lambda: self._set_preset("0x3EA000", "0x3E8000"),
                  bg="#e8edf7", fg="#154385", font=("Segoe UI", 10),
                  relief="flat", cursor="hand2").pack(side="left")

        # ── Convert button ───────────────────────────────────────────────────
        tk.Button(self, text="Convert", command=self._run,
                  bg="#27AE60", fg="white", font=("Segoe UI", 13, "bold"),
                  relief="flat", cursor="hand2", width=18).pack(pady=18)

        # ── Log ─────────────────────────────────────────────────────────────
        tk.Label(self, text="Log", font=("Segoe UI", 11, "bold"),
                 bg="#34495E", fg="white", anchor="w").pack(fill="x", padx=40)
        self.log_box = tk.Text(self, bg="#34495E", fg="white", font=("Segoe UI", 11),
                               state="disabled", height=8, wrap="word",
                               relief="flat", bd=4)
        self.log_box.pack(padx=40, pady=(0, 20), fill="x")

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _set_preset(self, frm, to):
        self.from_var.set(frm)
        self.to_var.set(to)

    def _browse_src(self):
        p = filedialog.askopenfilename(
            title="Select Input HEX File",
            filetypes=[("Intel HEX", "*.hex"), ("All Files", "*.*")]
        )
        if p:
            self.src_var.set(p)
            # auto-suggest output filename
            base, ext = os.path.splitext(p)
            self.dst_var.set(base + "_rebased" + ext)

    def _browse_dst(self):
        p = filedialog.asksaveasfilename(
            title="Save Output HEX File As",
            defaultextension=".hex",
            filetypes=[("Intel HEX", "*.hex"), ("All Files", "*.*")]
        )
        if p:
            self.dst_var.set(p)

    def log(self, msg):
        self.log_box.config(state="normal")
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    def _run(self):
        src = self.src_var.get()
        dst = self.dst_var.get()
        from_str = self.from_var.get().strip()
        to_str   = self.to_var.get().strip()

        if not src:
            messagebox.showerror("Error", "Please select an input HEX file.")
            return
        if not dst:
            messagebox.showerror("Error", "Please select an output file path.")
            return
        try:
            from_base = int(from_str, 16)
            to_base   = int(to_str,   16)
        except ValueError:
            messagebox.showerror("Error", "Addresses must be hex values e.g. 0x3E8000")
            return
        if from_base == to_base:
            messagebox.showerror("Error", "From and To addresses are the same.")
            return

        self.log_box.config(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.config(state="disabled")
        self.log("Converting...")

        def worker():
            try:
                rebase_hex(src, dst, from_base, to_base, self.log)
                self.after(0, lambda: messagebox.showinfo(
                    "Done", f"Conversion complete!\n\nSaved to:\n{dst}"))
            except Exception as e:
                self.log(f"❌ Error: {e}")
                self.after(0, lambda: messagebox.showerror("Error", str(e)))

        threading.Thread(target=worker, daemon=True).start()


if __name__ == "__main__":
    app = HexRebaseApp()
    app.mainloop()
