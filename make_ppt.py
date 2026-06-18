#!/usr/bin/env python3
"""Generate JSW FlashXpert upgrade presentation."""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
import copy

# ── Brand colours ─────────────────────────────────────────────────────────────
JSW_DARK   = RGBColor(0x16, 0x3C, 0x69)   # dark navy
JSW_BLUE   = RGBColor(0x1F, 0x4E, 0x96)   # mid blue
JSW_ACCENT = RGBColor(0x27, 0xAE, 0x60)   # green
JSW_ORANGE = RGBColor(0xE6, 0x7E, 0x22)   # orange
JSW_RED    = RGBColor(0xE7, 0x4C, 0x3C)   # red
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_BG   = RGBColor(0xF6, 0xF8, 0xFB)
GREY       = RGBColor(0x6B, 0x72, 0x80)
DARK_TEXT  = RGBColor(0x11, 0x18, 0x27)

prs = Presentation()
prs.slide_width  = Inches(13.33)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]   # completely blank

# ── Helpers ───────────────────────────────────────────────────────────────────

def add_rect(slide, x, y, w, h, fill=None, line=None, line_w=None):
    shape = slide.shapes.add_shape(1, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.line.fill.background()
    if fill:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill
    else:
        shape.fill.background()
    if line:
        shape.line.color.rgb = line
        if line_w:
            shape.line.width = line_w
    else:
        shape.line.fill.background()
    return shape

def add_text(slide, text, x, y, w, h, size=18, bold=False, color=DARK_TEXT,
             align=PP_ALIGN.LEFT, italic=False, wrap=True):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = wrap
    p  = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size  = Pt(size)
    run.font.bold  = bold
    run.font.color.rgb = color
    run.font.italic = italic
    return tb

def navy_header(slide, title, subtitle=None):
    """Full-width navy top bar with title."""
    add_rect(slide, 0, 0, 13.33, 1.4, fill=JSW_DARK)
    add_text(slide, title, 0.4, 0.18, 12.0, 0.8,
             size=28, bold=True, color=WHITE, align=PP_ALIGN.LEFT)
    if subtitle:
        add_text(slide, subtitle, 0.4, 0.88, 12.0, 0.4,
                 size=13, color=RGBColor(0x93, 0xC5, 0xFD), align=PP_ALIGN.LEFT)
    # light bg for body
    add_rect(slide, 0, 1.4, 13.33, 6.1, fill=LIGHT_BG)

def bullet_box(slide, title, bullets, x, y, w, h,
               title_color=JSW_DARK, accent=JSW_BLUE):
    """Card with coloured left bar, title and bullet list."""
    add_rect(slide, x, y, w, h, fill=WHITE,
             line=RGBColor(0xE5, 0xE7, 0xEB))
    add_rect(slide, x, y, 0.06, h, fill=accent)
    add_text(slide, title, x+0.15, y+0.10, w-0.25, 0.38,
             size=14, bold=True, color=title_color)
    tb = slide.shapes.add_textbox(
        Inches(x+0.15), Inches(y+0.52), Inches(w-0.3), Inches(h-0.65))
    tf = tb.text_frame
    tf.word_wrap = True
    for i, b in enumerate(bullets):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_before = Pt(3)
        run = p.add_run()
        run.text = f"•  {b}"
        run.font.size  = Pt(11.5)
        run.font.color.rgb = DARK_TEXT

def tag(slide, text, x, y, bg=JSW_BLUE, fg=WHITE, size=10):
    add_rect(slide, x, y, len(text)*0.088+0.18, 0.28, fill=bg)
    add_text(slide, text, x+0.07, y+0.03, len(text)*0.088+0.1, 0.22,
             size=size, bold=True, color=fg)

def footer(slide):
    add_rect(slide, 0, 7.18, 13.33, 0.32, fill=JSW_DARK)
    add_text(slide, "JSW Greentech Limited  —  Controls & Software Department  |  CONFIDENTIAL",
             0.3, 7.20, 10, 0.26, size=9, color=RGBColor(0xBF, 0xDB, 0xFF))
    add_text(slide, "JSW FlashXpert  V2.0",
             11.0, 7.20, 2.0, 0.26, size=9, bold=True,
             color=WHITE, align=PP_ALIGN.RIGHT)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 1 — Title
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)

add_rect(s, 0, 0, 13.33, 7.5, fill=JSW_DARK)
# diagonal accent strip
add_rect(s, 0, 5.1, 13.33, 0.08, fill=JSW_ACCENT)
add_rect(s, 0, 5.2, 13.33, 2.3, fill=JSW_BLUE)

add_text(s, "JSW FlashXpert", 0.8, 1.1, 11.5, 1.1,
         size=52, bold=True, color=WHITE)
add_text(s, "V2.0 — Tool Upgrade Presentation",
         0.8, 2.25, 11.5, 0.7,
         size=24, color=RGBColor(0x93, 0xC5, 0xFD))

add_text(s, "New Capabilities Added:", 0.8, 3.2, 11.5, 0.4,
         size=14, bold=True, color=RGBColor(0x6E, 0xD8, 0xA4))
add_text(s,
         "  ✦  Oil Pump ECU Flashing      ✦  Air Pump ECU Flashing      ✦  Phase 2 — VCU FOTA Flashing",
         0.8, 3.65, 12.0, 0.5, size=14, color=WHITE)

add_text(s, "Controls & Software Department\nR&D — JSW Greentech Limited",
         0.8, 5.45, 8, 0.9, size=13, color=RGBColor(0xBF, 0xDB, 0xFF))
add_text(s, "2025", 11.5, 5.45, 1.5, 0.4,
         size=13, color=RGBColor(0xBF, 0xDB, 0xFF), align=PP_ALIGN.RIGHT)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 2 — Agenda
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
navy_header(s, "Agenda", "What this presentation covers")

items = [
    ("01", "Tool Overview",            "Original JSW FlashXpert capabilities",       JSW_BLUE),
    ("02", "Oil Pump Flashing",        "Custom CAN protocol — OEM block parser",     JSW_ACCENT),
    ("03", "Air Pump Flashing",        "Same protocol, different ECU address",       JSW_ORANGE),
    ("04", "Phase 2 — VCU FOTA",       "UDS over ISO-TP, 10-step sequence",          JSW_RED),
    ("05", "Live Pump Monitor",        "Real-time CAN data dashboard",               RGBColor(0x70, 0x5D, 0xD6)),
    ("06", "Architecture & Key Facts", "Protocol summary, CAN IDs, tech stack",      JSW_DARK),
]

for i, (num, title, desc, col) in enumerate(items):
    col_idx = i % 3
    row_idx = i // 3
    bx = 0.35 + col_idx * 4.33
    by = 1.65 + row_idx * 2.4
    add_rect(s, bx, by, 4.0, 2.0, fill=WHITE, line=RGBColor(0xE5,0xE7,0xEB))
    add_rect(s, bx, by, 0.06, 2.0, fill=col)
    add_text(s, num, bx+0.18, by+0.15, 0.7, 0.5,
             size=26, bold=True, color=col)
    add_text(s, title, bx+0.18, by+0.65, 3.6, 0.4,
             size=14, bold=True, color=JSW_DARK)
    add_text(s, desc, bx+0.18, by+1.1, 3.6, 0.55,
             size=10.5, color=GREY)

footer(s)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 3 — Tool Overview (Before)
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
navy_header(s, "JSW FlashXpert — Original Tool", "Capabilities before this upgrade")

bullet_box(s, "Original Supported Controllers", [
    "JSW EVCU  (Electric Vehicle Control Unit)",
    "JSW MCU   (Motor Control Unit)",
    "JSW DCDC  (DC-DC Converter)",
], 0.35, 1.6, 5.9, 2.5, accent=JSW_BLUE)

bullet_box(s, "Flash Protocol (UDS)", [
    "Custom 8-byte CAN frames over extended IDs",
    "Programming session → Erase → Download → Verify → Reset",
    "CRC32 post-flash handshake",
    "Ignition OFF → ON procedure for all controllers",
], 6.5, 1.6, 6.5, 2.5, accent=JSW_BLUE)

bullet_box(s, "Other Features", [
    "Read firmware version (JSW MCU & EVCU)",
    "Progress sidebar with 6-step visual tracker",
    "Save / clear flash log",
    "Domain-join security check",
], 0.35, 4.35, 5.9, 2.5, accent=JSW_DARK)

bullet_box(s, "Hardware Support", [
    "PEAK PCAN (PCANBasic.dll)",
    "Vector CANalyzer interface",
    "Kvaser CAN adapter",
    "Fixed 250 kbps for all controllers",
], 6.5, 4.35, 6.5, 2.5, accent=JSW_DARK)

footer(s)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 4 — What's New (Summary)
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
navy_header(s, "V2.0 — What's New at a Glance", "Three major features added to JSW FlashXpert")

cards = [
    (JSW_ACCENT, "Oil Pump\nECU Flashing",
     ["Custom 8-byte CAN protocol", "OEM stride-anomaly block parser",
      "Broadcast wakeup (live ECU)", "Power OFF → ON procedure",
      "dev_id = 0x05  |  250 kbps"]),
    (JSW_ORANGE, "Air Pump\nECU Flashing",
     ["Same custom CAN protocol", "Sequential block builder",
      "Broadcast wakeup support", "Power OFF → ON procedure",
      "dev_id = 0x06  |  250 kbps"]),
    (JSW_RED,    "Phase 2\nVCU FOTA Flash",
     ["UDS over ISO-TP (can-isotp)", "10-step UDS sequence",
      "SecurityAccess.dll key derive", "OTA binary with OtaPlainHdr",
      "TX 0x7E0 / RX 0x7E8"]),
]

for i, (col, title, pts) in enumerate(cards):
    bx = 0.4 + i * 4.3
    add_rect(s, bx, 1.55, 4.0, 5.55, fill=WHITE, line=RGBColor(0xE5,0xE7,0xEB))
    add_rect(s, bx, 1.55, 4.0, 0.85, fill=col)
    add_text(s, title, bx+0.18, 1.60, 3.6, 0.75,
             size=16, bold=True, color=WHITE)
    tb = s.shapes.add_textbox(Inches(bx+0.18), Inches(2.5), Inches(3.6), Inches(4.4))
    tf = tb.text_frame; tf.word_wrap = True
    for j, pt in enumerate(pts):
        p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
        p.space_before = Pt(5)
        run = p.add_run(); run.text = f"✓  {pt}"
        run.font.size = Pt(12); run.font.color.rgb = DARK_TEXT

footer(s)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 5 — Oil Pump Flashing
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
navy_header(s, "Oil Pump ECU Flashing", "JSW Oil Pump  —  dev_id 0x05  |  Custom 8-byte CAN protocol")

# Left: protocol
bullet_box(s, "CAN IDs", [
    "Broadcast  : 0x1800FFFF",
    "Tool → ECU : 0x180005FF",
    "ECU → Tool : 0x1800FF05",
    "NAK        : 0x1800EEEE",
], 0.35, 1.6, 4.0, 2.55, accent=JSW_ACCENT)

bullet_box(s, "Flash Sequence", [
    "1. Broadcast wakeup (FF 02 05 …) — reboots live ECU",
    "2. Heartbeat until ECU responds (up to 60 × 100 ms)",
    "3. Block init + erase per block (0x04 frame)",
    "4. Data frames toggle 0x01 / 0x02 (6 bytes payload each)",
    "5. End-of-block frame (0x00 + block_id)",
    "6. Program CRC address (0x04 on CRC addr)",
    "7. Verify CRC (0x01 frame)",
    "8. Close session (0x03 frame)",
], 4.55, 1.6, 8.4, 2.55, accent=JSW_ACCENT)

bullet_box(s, "Firmware Versions", [
    "VER1: stride anomalies → OEM block parser (7 blocks)",
    "VER2 / VER3: sequential → 5 blocks at 0x3E8000",
    "Stride anomaly detection: gap > prev_bc ÷ 2",
    "Block IDs auto-computed from BLOCK_ID_BASE",
], 0.35, 4.35, 5.9, 2.5, accent=JSW_DARK)

bullet_box(s, "Frame Format", [
    "8 bytes:  [TYPE][P1][P2][P3][P4][P5][P6][XOR8]",
    "XOR8 = XOR of first 7 bytes",
    "ACK = ECU echoes exact frame on ECU ID",
    "Payload = 6 bytes of firmware data per frame",
], 6.5, 4.35, 6.5, 2.5, accent=JSW_DARK)

footer(s)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 6 — Air Pump Flashing
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
navy_header(s, "Air Pump ECU Flashing", "JSW Air Pump  —  dev_id 0x06  |  Same protocol, different address")

bullet_box(s, "CAN IDs", [
    "Broadcast  : 0x1800FFFF  (shared)",
    "Tool → ECU : 0x180006FF",
    "ECU → Tool : 0x1800FF06",
    "NAK        : 0x1800EEEE  (shared)",
], 0.35, 1.6, 4.0, 2.4, accent=JSW_ORANGE)

bullet_box(s, "Key Differences vs Oil Pump", [
    "ECU address byte 0x06 (Oil Pump = 0x05)",
    "No stride anomalies — always sequential blocks",
    "Heartbeat byte auto-computed from hex base address",
    "Same 8-byte frame format, same ACK mechanism",
    "Same Power OFF → ON procedure in GUI",
], 4.55, 1.6, 8.4, 2.4, accent=JSW_ORANGE)

bullet_box(s, "Heartbeat Byte Formula", [
    "hb_byte = (BLOCK_ID_BASE − base_addr) ÷ 0x2000 + 1",
    "BLOCK_ID_BASE = 0x003F4000",
    "Example: base 0x3E8000 → hb_byte = 0x07",
    "Example: base 0x3EA000 → hb_byte = 0x06",
    "Auto-detected from Intel HEX file — no manual config",
], 0.35, 4.2, 6.2, 2.65, accent=JSW_DARK)

bullet_box(s, "GUI Flow (Both Pumps)", [
    "1. Select pump type (Air / Oil)",
    "2. Select CAN hardware + browse HEX file",
    "3. Click Start Flashing",
    "4. Dialog: TURN OFF power → click OK",
    "5. Dialog: TURN ON power → flashing starts automatically",
    "6. Progress sidebar turns green step by step",
], 6.75, 4.2, 6.2, 2.65, accent=JSW_ORANGE)

footer(s)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 7 — Phase 2 VCU FOTA
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
navy_header(s, "Phase 2 — VCU FOTA Flashing", "S32K144 ECU  |  UDS over ISO-TP  |  SecurityAccess.dll")

# Step sequence diagram
steps = [
    ("01", "Diag\nSession",   "0x10 0x02\nCatch bootloader"),
    ("02", "Security\nAccess","0x27 01 seed\n0x27 02 key"),
    ("03", "Erase",           "0x31 01 FF 00\nApp slot"),
    ("04", "Download",        "0x34 Request\n0x36 Transfer"),
    ("05", "Verify",          "0x37 Exit\n0x31 01 FF 01 CRC"),
    ("06", "ECU\nReset",      "0x2E F1 5B FP\n0x11 01 Reset"),
]

for i, (num, title, detail) in enumerate(steps):
    bx = 0.35 + i * 2.12
    # box
    add_rect(s, bx, 1.6, 1.9, 2.2, fill=JSW_DARK if i == 0 else WHITE,
             line=JSW_DARK)
    add_text(s, num, bx+0.1, 1.65, 0.5, 0.4,
             size=10, bold=True, color=JSW_ACCENT if i > 0 else RGBColor(0x6E,0xD8,0xA4))
    add_text(s, title, bx+0.1, 2.05, 1.7, 0.55,
             size=13, bold=True, color=WHITE if i == 0 else JSW_DARK)
    add_text(s, detail, bx+0.1, 2.65, 1.7, 0.9,
             size=9, color=RGBColor(0xBF,0xDB,0xFF) if i == 0 else GREY)
    # arrow
    if i < 5:
        add_text(s, "→", bx+1.92, 2.4, 0.25, 0.35,
                 size=18, bold=True, color=JSW_DARK, align=PP_ALIGN.CENTER)

bullet_box(s, "OTA Binary Format (OtaPlainHdr)", [
    "Magic       : 0xB00710AD (4 bytes)",
    "Model ID    : 2 bytes  (e.g. 0x0001 = 9M Bus)",
    "Version     : 3 bytes  (major.minor.patch)",
    "Reserved    : 3 bytes",
    "Comp Size   : 4 bytes  (compressed payload size)",
    "Nonce       : 12 bytes (encryption nonce)",
    "Payload     : encrypted + compressed firmware",
], 0.35, 4.1, 6.0, 3.1, accent=JSW_RED)

bullet_box(s, "Security & Infrastructure", [
    "SecurityAccess.dll — key derivation (ComputeKey)",
    "ISO-TP framing via can-isotp library",
    "CAN IDs: TX 0x7E0 / RX 0x7E8 (standard 11-bit)",
    "0x78 NRC: ECU busy → auto-extend timeout to 5 min",
    "Separate tab (Phase 2) in GUI — different workflow",
    "Coloured log: green=OK  red=error  orange=warn",
], 6.6, 4.1, 6.4, 3.1, accent=JSW_RED)

footer(s)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 8 — Live Pump Monitor
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
navy_header(s, "Bonus: Live Pump CAN Monitor", "pump_monitor_gui.py  —  Replicates OEM candebug.exe tool")

bullet_box(s, "What It Shows (Oil Pump)", [
    "Bus Voltage  •  Output Voltage  •  Output Current",
    "Set Frequency  •  Output Frequency  •  RPM",
    "Controller Temperature  •  Motor Temperature",
    "Run Enable  •  CAN Enable  •  Hardwire Enable",
    "Fault Code  (row turns RED when non-zero)",
    "Stator R  •  D/Q Inductance  •  Back-EMF  •  PID gains",
], 0.35, 1.6, 6.0, 3.5, accent=RGBColor(0x70,0x5D,0xD6))

bullet_box(s, "Monitor CAN IDs (from OEM tool)", [
    "0x4181 → Bus V, Output V, Current",
    "0x4182 → Set Freq, Output Freq, RPM",
    "0x4183 → Ctrl Temp, Motor Temp, Enable, Fault",
    "0x4184 → CAN/Hardwire Enable flags",
    "0x5010 → Motor parameters (R, L, EMF)",
    "0x5011 → PID gains (DKp, DKi, QKp, QKi)",
    "Each frame = 4 × uint16 big-endian values",
], 6.6, 1.6, 6.4, 3.5, accent=RGBColor(0x70,0x5D,0xD6))

bullet_box(s, "GUI Features", [
    "Active CAN IDs light up GREEN when receiving frames",
    "CAN ID turns grey if silent > 1 second",
    "PEAK channel selector: PCAN_USBBUS1 / 2 / 3",
    "Frame counter displayed in real time",
    "Status bar shows interface + bitrate",
], 0.35, 5.3, 6.0, 1.95, accent=JSW_DARK)

bullet_box(s, "Source: OEM Tool Analysis", [
    "Reverse-engineered from candebug.exe config XMLs",
    "dcac_oil_config.xml  •  dcac_gas_config.xml",
    "dev_id 0x05 = Oil Pump  •  0x06 = Air Pump",
    "BaudRate=3 → 250 kbps  confirmed",
], 6.6, 5.3, 6.4, 1.95, accent=JSW_DARK)

footer(s)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 9 — Architecture & CAN ID Table
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
navy_header(s, "Architecture & CAN ID Reference", "All controllers supported by JSW FlashXpert V2.0")

# Table
headers = ["Controller", "Protocol", "Tool → ECU ID", "ECU → Tool ID", "Bitrate", "Flash File"]
rows = [
    ["JSW EVCU",     "Custom UDS",    "0x0B00D0D9 (ext)", "0x0B00D9D0 (ext)", "250 kbps", ".hex / .bin"],
    ["JSW MCU",      "Custom UDS",    "0x0B00D0D9 (ext)", "0x0B00D9D0 (ext)", "250 kbps", ".hex / .bin"],
    ["JSW DCDC",     "Custom UDS",    "0x0B00D0D9 (ext)", "0x0B00D9D0 (ext)", "250 kbps", ".hex / .bin"],
    ["JSW Oil Pump", "Custom 8-byte", "0x180005FF (ext)", "0x1800FF05 (ext)", "250 kbps", "Intel HEX"],
    ["JSW Air Pump", "Custom 8-byte", "0x180006FF (ext)", "0x1800FF06 (ext)", "250 kbps", "Intel HEX"],
    ["VCU FOTA",     "UDS / ISO-TP",  "0x7E0 (std 11bit)","0x7E8 (std 11bit)","250 kbps", "OTA .bin"],
]

col_w = [1.7, 1.6, 2.1, 2.1, 1.1, 1.5]
col_x = [0.35]
for w in col_w[:-1]:
    col_x.append(col_x[-1] + w)

# Header row
for j, (hdr, cx, cw) in enumerate(zip(headers, col_x, col_w)):
    add_rect(s, cx, 1.6, cw, 0.38, fill=JSW_DARK)
    add_text(s, hdr, cx+0.06, 1.63, cw-0.1, 0.32,
             size=10, bold=True, color=WHITE)

# Data rows
row_colors = [LIGHT_BG, WHITE]
highlight_rows = {3: JSW_ACCENT, 4: JSW_ORANGE, 5: JSW_RED}
for i, row in enumerate(rows):
    ry = 1.98 + i * 0.42
    bg = row_colors[i % 2]
    for j, (cell, cx, cw) in enumerate(zip(row, col_x, col_w)):
        fill = bg
        add_rect(s, cx, ry, cw, 0.41, fill=fill,
                 line=RGBColor(0xE5,0xE7,0xEB))
        txt_col = DARK_TEXT
        if i in highlight_rows and j == 0:
            txt_col = highlight_rows[i]
        add_text(s, cell, cx+0.06, ry+0.06, cw-0.1, 0.3,
                 size=9.5, color=txt_col, bold=(j == 0))

# Legend
tag(s, "OIL PUMP", 0.35, 4.65, bg=JSW_ACCENT)
tag(s, "AIR PUMP", 1.65, 4.65, bg=JSW_ORANGE)
tag(s, "VCU FOTA", 2.95, 4.65, bg=JSW_RED)
tag(s, "EXISTING", 4.25, 4.65, bg=JSW_DARK)

bullet_box(s, "Software Architecture", [
    "flashing_logic.py  — all protocol logic classes",
    "  ├─ CANBusWrapper       (PEAK / Vector / Kvaser)",
    "  ├─ FlashingLogic       (UDS, existing controllers)",
    "  ├─ PumpFlashingLogic   (Oil + Air Pump)",
    "  └─ FOTAFlashingLogic   (VCU FOTA, ISO-TP)",
    "jsw_gui.py       — Phase 1 + Phase 2 tabbed GUI",
    "pump_monitor_gui.py — live CAN data monitor",
], 0.35, 5.1, 12.6, 2.7, accent=JSW_BLUE)

footer(s)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 10 — Summary & Benefits
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
navy_header(s, "Summary — JSW FlashXpert V2.0", "Single tool for all JSW powertrain ECU flashing needs")

cards2 = [
    (JSW_ACCENT, "Oil + Air Pump", [
        "Both pump types in one tool",
        "Live ECU broadcast wakeup",
        "OEM-compatible block parser",
        "No separate OEM tool needed",
    ]),
    (JSW_RED, "VCU FOTA", [
        "Full 10-step UDS sequence",
        "Separate Phase 2 tab",
        "OTA binary + DLL workflow",
        "Up to 5 min transfer exit",
    ]),
    (RGBColor(0x70,0x5D,0xD6), "Pump Monitor", [
        "Live CAN data dashboard",
        "RPM, voltage, temp, faults",
        "OEM-equivalent monitoring",
        "PEAK hardware support",
    ]),
    (JSW_DARK, "Tool Quality", [
        "Single .exe deployment",
        "Domain-join security check",
        "Coloured step-by-step sidebar",
        "Elapsed time + save log",
    ]),
]

for i, (col, title, pts) in enumerate(cards2):
    bx = 0.35 + (i % 2) * 6.42
    by = 1.6  + (i // 2) * 2.65
    add_rect(s, bx, by, 6.1, 2.45, fill=WHITE, line=RGBColor(0xE5,0xE7,0xEB))
    add_rect(s, bx, by, 6.1, 0.52, fill=col)
    add_text(s, title, bx+0.18, by+0.10, 5.7, 0.38,
             size=15, bold=True, color=WHITE)
    tb = s.shapes.add_textbox(Inches(bx+0.18), Inches(by+0.65),
                               Inches(5.7), Inches(1.65))
    tf = tb.text_frame; tf.word_wrap = True
    for j, pt in enumerate(pts):
        p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
        p.space_before = Pt(4)
        run = p.add_run(); run.text = f"✓  {pt}"
        run.font.size = Pt(12.5); run.font.color.rgb = DARK_TEXT

footer(s)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 11 — Thank You
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
add_rect(s, 0, 0, 13.33, 7.5, fill=JSW_DARK)
add_rect(s, 0, 5.5, 13.33, 0.07, fill=JSW_ACCENT)
add_rect(s, 0, 5.57, 13.33, 1.93, fill=JSW_BLUE)

add_text(s, "Thank You", 1.0, 1.4, 11.0, 1.4,
         size=58, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
add_text(s, "JSW FlashXpert V2.0 is ready for deployment.",
         1.0, 3.1, 11.0, 0.55,
         size=18, color=RGBColor(0x93,0xC5,0xFD), align=PP_ALIGN.CENTER)
add_text(s, "For queries contact the Controls & Software Department, R&D — JSW Greentech Limited",
         1.0, 5.75, 11.0, 0.45,
         size=11, color=RGBColor(0xBF,0xDB,0xFF), align=PP_ALIGN.CENTER)

# ── Save ──────────────────────────────────────────────────────────────────────
out = "JSW_FlashXpert_V2_Upgrade.pptx"
prs.save(out)
print(f"Saved: {out}")
