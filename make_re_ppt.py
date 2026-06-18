#!/usr/bin/env python3
"""Generate Reverse Engineering PPT for Pump ECU Flash Protocol."""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

prs = Presentation()
prs.slide_width  = Inches(13.33)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]

# ── Colours ───────────────────────────────────────────────────────────────────
NAVY   = RGBColor(0x16, 0x3C, 0x69)
BLUE   = RGBColor(0x1F, 0x4E, 0x96)
GREEN  = RGBColor(0x27, 0xAE, 0x60)
ORANGE = RGBColor(0xE6, 0x7E, 0x22)
RED    = RGBColor(0xE7, 0x4C, 0x3C)
PURPLE = RGBColor(0x70, 0x5D, 0xD6)
GREY   = RGBColor(0x6B, 0x72, 0x80)
LGREY  = RGBColor(0xF6, 0xF8, 0xFB)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
BLACK  = RGBColor(0x11, 0x18, 0x27)
CBLUE  = RGBColor(0x93, 0xC5, 0xFD)
CGREEN = RGBColor(0x6E, 0xD8, 0xA4)
DARK   = RGBColor(0x1E, 0x2A, 0x3A)

# ── Helpers ───────────────────────────────────────────────────────────────────

def rect(slide, x, y, w, h, fill=None, line=None):
    s = slide.shapes.add_shape(1, Inches(x), Inches(y), Inches(w), Inches(h))
    s.line.fill.background()
    if fill:
        s.fill.solid(); s.fill.fore_color.rgb = fill
    else:
        s.fill.background()
    if line:
        s.line.color.rgb = line
        s.line.width = Pt(0.75)
    else:
        s.line.fill.background()
    return s

def txt(slide, text, x, y, w, h, size=12, bold=False, color=BLACK,
        align=PP_ALIGN.LEFT, italic=False):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.alignment = align
    r = p.add_run(); r.text = text
    r.font.size = Pt(size); r.font.bold = bold
    r.font.color.rgb = color; r.font.italic = italic
    return tb

def header(slide, title, subtitle=None, accent=NAVY):
    rect(slide, 0, 0, 13.33, 1.35, fill=NAVY)
    rect(slide, 0, 1.35, 13.33, 0.06, fill=accent)
    rect(slide, 0, 1.41, 13.33, 6.09, fill=LGREY)
    txt(slide, title, 0.4, 0.14, 12.5, 0.72, size=26, bold=True, color=WHITE)
    if subtitle:
        txt(slide, subtitle, 0.4, 0.88, 12.5, 0.38, size=11, color=CBLUE)

def footer(slide):
    rect(slide, 0, 7.18, 13.33, 0.32, fill=NAVY)
    txt(slide, "JSW Greentech Limited  —  Controls & Software Department  |  CONFIDENTIAL",
        0.3, 7.20, 10, 0.26, size=8.5, color=CBLUE)
    txt(slide, "JSW FlashXpert  V2.0", 10.8, 7.20, 2.3, 0.26,
        size=8.5, bold=True, color=WHITE, align=PP_ALIGN.RIGHT)

def card(slide, x, y, w, h, title, bullets, accent=BLUE, title_size=13, bullet_size=11):
    rect(slide, x, y, w, h, fill=WHITE, line=RGBColor(0xE5,0xE7,0xEB))
    rect(slide, x, y, 0.07, h, fill=accent)
    txt(slide, title, x+0.18, y+0.10, w-0.28, 0.38,
        size=title_size, bold=True, color=NAVY)
    tb = slide.shapes.add_textbox(
        Inches(x+0.18), Inches(y+0.52), Inches(w-0.28), Inches(h-0.65))
    tf = tb.text_frame; tf.word_wrap = True
    for i, b in enumerate(bullets):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_before = Pt(3)
        r = p.add_run(); r.text = b
        r.font.size = Pt(bullet_size); r.font.color.rgb = BLACK

def mono_block(slide, x, y, w, h, lines, bg=DARK, fg=CGREEN, size=9):
    rect(slide, x, y, w, h, fill=bg)
    tb = slide.shapes.add_textbox(
        Inches(x+0.15), Inches(y+0.12), Inches(w-0.3), Inches(h-0.24))
    tf = tb.text_frame; tf.word_wrap = False
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        r = p.add_run(); r.text = line
        r.font.size = Pt(size); r.font.color.rgb = fg
        r.font.name = "Courier New"; r.font.bold = True

def step_box(slide, x, y, num, title, detail, color=NAVY, w=2.0, h=2.4):
    rect(slide, x, y, w, h, fill=WHITE, line=RGBColor(0xE5,0xE7,0xEB))
    rect(slide, x, y, w, 0.55, fill=color)
    txt(slide, num,   x+0.12, y+0.08, 0.5, 0.38, size=10, bold=True,
        color=CGREEN if color == NAVY else WHITE)
    txt(slide, title, x+0.12, y+0.58, w-0.2, 0.55, size=12, bold=True, color=NAVY)
    txt(slide, detail, x+0.12, y+1.18, w-0.2, 1.1,  size=9.5, color=GREY)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 1 — TITLE
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
rect(s, 0, 0, 13.33, 7.5, fill=NAVY)
rect(s, 0, 5.3, 13.33, 0.07, fill=GREEN)
rect(s, 0, 5.37, 13.33, 2.13, fill=BLUE)

txt(s, "Reverse Engineering", 0.8, 0.8, 12.0, 0.9,
    size=44, bold=True, color=WHITE)
txt(s, "Pump ECU Flash Protocol", 0.8, 1.7, 12.0, 0.9,
    size=44, bold=True, color=CGREEN)
txt(s, "How JSW Controls & Software decoded a proprietary CAN protocol,\n"
       "adapted it to our hardware, and eliminated all OEM tool dependency.",
    0.8, 2.75, 11.5, 0.95, size=15, color=CBLUE)

txt(s, "JSW Air Pump  ✦  JSW Oil Pump  ✦  PEAK PCAN Hardware  ✦  Zero OEM Dependency",
    0.8, 3.9, 12.0, 0.42, size=12, color=RGBColor(0xFF,0xD7,0x00))

txt(s, "Controls & Software Department\nR&D — JSW Greentech Limited  |  2025",
    0.8, 5.65, 9.0, 0.8, size=12, color=CBLUE)
txt(s, "JSW\nFlashXpert\nV2.0", 11.5, 5.55, 1.6, 1.0,
    size=12, bold=True, color=WHITE, align=PP_ALIGN.RIGHT)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 2 — THE PROBLEM
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
header(s, "The Problem — OEM Tool Dependency",
       "Before reverse engineering: no control, no visibility, no integration", accent=RED)

card(s, 0.35, 1.55, 6.15, 2.75, "OEM Tool Blockers", [
    "✗  candebug.exe — closed binary, no source code",
    "✗  Requires USBCAN hardware (not our PEAK adapters)",
    "✗  GUI-only — no automation or scripting possible",
    "✗  OEM presence required for every firmware update",
    "✗  Zero error details — pass/fail only",
    "✗  Cannot integrate with our existing JSW FlashXpert tool",
], accent=RED)

card(s, 6.75, 1.55, 6.15, 2.75, "Business Risk", [
    "✗  Single point of failure — if OEM tool breaks, no flash",
    "✗  Production line dependency on OEM availability",
    "✗  Protocol fully unknown — cannot debug field failures",
    "✗  No log, no traceability for flashed units",
    "✗  Different workflow for pumps vs all other ECUs",
    "✗  Cannot detect bad flash sectors proactively",
], accent=RED)

rect(s, 0.35, 4.5, 12.55, 0.9, fill=RGBColor(0xFE,0xF2,0xF2),
     line=RGBColor(0xFC,0xA5,0xA5))
txt(s, "Goal:  Fully decode the protocol from CAN traffic alone → implement in Python → "
       "run on PEAK hardware we already own → ship as part of JSW FlashXpert → "
       "never need the OEM tool again.",
    0.55, 4.58, 12.15, 0.72, size=11, bold=False, color=RED)

card(s, 0.35, 5.55, 12.55, 1.62, "Scope", [
    "✦  JSW Oil Pump  (ECU addr 0x05)     ✦  JSW Air Pump  (ECU addr 0x06)",
    "✦  Custom 8-byte CAN protocol over 29-bit extended IDs at 250 kbps",
    "✦  Intel HEX firmware files  |  VER1, VER2, VER3 variants",
], accent=NAVY, bullet_size=11.5)

footer(s)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 3 — REVERSE ENGINEERING METHOD
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
header(s, "Reverse Engineering Method — 4-Step Approach",
       "No documentation, no source code — protocol decoded entirely from live CAN traffic", accent=BLUE)

steps = [
    ("01", "Passive\nCAN Capture",
     "Connected PEAK PCAN-USB to the vehicle CAN bus\n"
     "Ran OEM tool to flash a known-good pump ECU\n"
     "Captured full timestamped CAN log during flash",
     NAVY),
    ("02", "Frame\nIdentification",
     "Filtered IDs 0x180005FF ↔ 0x1800FF05\n"
     "Confirmed 0x1800FFFF as broadcast channel\n"
     "Identified 0x1800EEEE as NAK/error channel",
     BLUE),
    ("03", "Pattern\nAnalysis",
     "All frames exactly 8 bytes — consistent structure\n"
     "Byte[7] = XOR of bytes[0..6] → checksum rule\n"
     "Byte[0] cycles: 0x04→0x01→0x02→0x01→… per block",
     GREEN),
    ("04", "ACK\nMechanism",
     "ECU replies with the EXACT same 8 bytes\n"
     "Reply arrives on ECU ID (not tool ID)\n"
     "No echo within window = timeout → retry / fail",
     ORANGE),
    ("05", "Firmware\nMapping",
     "Decoded address payload: 4B addr + 2B size\n"
     "Matched HEX file records to CAN data frames\n"
     "Verified 6 payload bytes per data frame",
     PURPLE),
    ("06", "Validate &\nReplicate",
     "Wrote Python script to replay captured sequence\n"
     "Compared byte-for-byte with OEM log\n"
     "Flashed ECU successfully — protocol confirmed ✓",
     RED),
]

for i, (num, title, detail, col) in enumerate(steps):
    bx = 0.35 + (i % 3) * 4.33
    by = 1.6  + (i // 3) * 2.65
    step_box(s, bx, by, num, title, detail, color=col, w=4.0, h=2.45)
    if i % 3 < 2:
        txt(s, "→", bx+4.02, by+1.05, 0.3, 0.4,
            size=18, bold=True, color=GREY, align=PP_ALIGN.CENTER)

footer(s)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 4 — PROTOCOL DECODED
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
header(s, "Protocol Fully Decoded — 8-Byte Custom CAN Frame",
       "Complete frame specification recovered from CAN traffic analysis", accent=GREEN)

mono_block(s, 0.35, 1.55, 12.65, 0.55,
    ["  Frame layout:   [ TYPE ][ P1 ][ P2 ][ P3 ][ P4 ][ P5 ][ P6 ][ XOR8 ]        "
     "XOR8 = P0 XOR P1 XOR P2 XOR P3 XOR P4 XOR P5 XOR P6"],
    size=10)

frame_types = [
    ("0x00", "Heartbeat / End-of-Block",
     "Wakeup: 00 00 <hb_byte> 00 00 00 00 <XOR>\n"
     "End-of-block: 00 00 <block_id> … <XOR>",
     NAVY),
    ("0x01", "Data Frame  (Toggle A)",
     "Payload = P1..P6 = 6 bytes of firmware data\n"
     "Alternates with 0x02 for every 6-byte chunk",
     BLUE),
    ("0x02", "Data Frame  (Toggle B)",
     "Identical to 0x01 but TYPE byte = 0x02\n"
     "Toggle ensures ECU detects duplicate/lost frames",
     BLUE),
    ("0x03", "Close Session",
     "Sent after verify — closes flash session\n"
     "Payload carries CRC bytes from HEX file",
     ORANGE),
    ("0x04", "Block Init / Erase",
     "P1-P4 = full 32-bit address (big-endian)\n"
     "P5-P6 = block size in bytes (big-endian)",
     RED),
]

for i, (ftype, title, detail, col) in enumerate(frame_types):
    bx = 0.35 + (i % 3) * 4.33
    by = 2.25 + (i // 3) * 2.35
    rect(s, bx, by, 4.0, 2.2, fill=WHITE, line=RGBColor(0xE5,0xE7,0xEB))
    rect(s, bx, by, 4.0, 0.48, fill=col)
    txt(s, ftype, bx+0.12, by+0.07, 1.1, 0.35,
        size=14, bold=True, color=WHITE, align=PP_ALIGN.LEFT)
    txt(s, title, bx+1.1, by+0.10, 2.7, 0.32,
        size=11, bold=True, color=WHITE)
    txt(s, detail, bx+0.14, by+0.60, 3.72, 1.45, size=10, color=BLACK)

# Broadcast box
rect(s, 0.35, 6.58, 12.65, 0.68, fill=DARK,
     line=RGBColor(0x6E,0xD8,0xA4))
txt(s, "Broadcast Wakeup (live ECU):   FF 02 <ecu_addr> 00 00 00 00 <XOR>   "
       "→  sent on 0x1800FFFF  "
       "→  ECU ACKs with  FF 82 <ecu_addr> …  then reboots to bootloader in 300 ms",
    0.55, 6.63, 12.2, 0.55, size=10, bold=True, color=CGREEN)

footer(s)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 5 — CAN ID MAP
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
header(s, "CAN ID Map & Flash Sequence",
       "All extended 29-bit IDs at 250 kbps  |  Echo-ACK model", accent=BLUE)

# CAN ID table
headers_row = ["CAN ID", "Direction", "Purpose", "Example Frame"]
rows = [
    ["0x1800FFFF", "Tool → All ECUs",  "Broadcast wakeup",       "FF 02 05 00 00 00 00 FD"],
    ["0x180005FF", "Tool → Oil Pump",  "Commands & data",        "04 00 3E 80 00 20 00 BC"],
    ["0x1800FF05", "Oil Pump → Tool",  "Echo-ACK (mirrors frame)","04 00 3E 80 00 20 00 BC"],
    ["0x180006FF", "Tool → Air Pump",  "Commands & data",        "00 00 07 00 00 00 00 07"],
    ["0x1800FF06", "Air Pump → Tool",  "Echo-ACK (mirrors frame)","00 00 07 00 00 00 00 07"],
    ["0x1800EEEE", "ECU → Tool",       "NAK / Error response",   "00 3E 80 00 04 00 00 00"],
]

col_w = [2.2, 2.4, 3.2, 4.55]
col_x = [0.35, 2.6, 5.05, 8.3]

rect(s, 0.35, 1.55, 12.5, 0.42, fill=NAVY)
for j, (h, cx, cw) in enumerate(zip(headers_row, col_x, col_w)):
    txt(s, h, cx+0.08, 1.58, cw-0.1, 0.35, size=10, bold=True, color=WHITE)

row_bg = [LGREY, WHITE]
hi = {0: GREEN, 1: BLUE, 2: BLUE, 3: ORANGE, 4: ORANGE, 5: RED}
for i, row in enumerate(rows):
    ry = 1.97 + i * 0.44
    for j, (cell, cx, cw) in enumerate(zip(row, col_x, col_w)):
        rect(s, cx, ry, cw, 0.43, fill=row_bg[i % 2],
             line=RGBColor(0xE5,0xE7,0xEB))
        col_c = hi.get(i, NAVY) if j == 0 else BLACK
        txt(s, cell, cx+0.08, ry+0.08, cw-0.12, 0.30,
            size=9.5, bold=(j == 0), color=col_c)

# Flash sequence flow
rect(s, 0.35, 4.65, 12.55, 0.38, fill=NAVY)
txt(s, "COMPLETE FLASH SEQUENCE", 0.55, 4.68, 8.0, 0.30,
    size=10, bold=True, color=WHITE)

seq = [
    ("1", "Broadcast\nWakeup", "FF 02 05…\non 0x1800FFFF"),
    ("2", "Heartbeat\nLoop", "00 00 07…\n60× @ 100ms"),
    ("3", "Block Init\n& Erase", "04 <addr>\n<size>"),
    ("4", "Data\nFrames", "01/02 toggle\n6B each"),
    ("5", "End of\nBlock", "00 00 <id>\n…"),
    ("6", "Write\nCRC", "04 on CRC\naddress"),
    ("7", "Verify &\nClose", "01 verify\n03 close"),
]

for i, (num, title, detail) in enumerate(seq):
    bx = 0.35 + i * 1.81
    rect(s, bx, 5.1, 1.65, 2.1, fill=WHITE, line=RGBColor(0xE5,0xE7,0xEB))
    rect(s, bx, 5.1, 1.65, 0.35, fill=BLUE)
    txt(s, num, bx+0.08, 5.12, 0.3, 0.28, size=10, bold=True, color=CGREEN)
    txt(s, title, bx+0.08, 5.5, 1.5, 0.55, size=10, bold=True, color=NAVY)
    txt(s, detail, bx+0.08, 6.1, 1.5, 0.85, size=8.5, color=GREY, italic=True)
    if i < 6:
        txt(s, "→", bx+1.66, 6.0, 0.2, 0.35,
            size=14, bold=True, color=NAVY, align=PP_ALIGN.CENTER)

footer(s)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 6 — STRIDE ANOMALY DISCOVERY
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
header(s, "Key Discovery — VER1 Stride Anomaly & OEM Block Parser",
       "Why Oil Pump VER1 needed a special block-splitting algorithm", accent=ORANGE)

card(s, 0.35, 1.55, 5.9, 2.5, "What Went Wrong with VER1", [
    "✗  Our first tool sent 5 sequential 16 KB blocks",
    "✗  Flash appeared to complete — no errors reported",
    "✗  ECU booted BUT firmware CRC mismatch on reboot",
    "✗  ECU rejected firmware and stayed in bootloader",
    "",
    "Root cause: OEM tool splits VER1 differently — 7 blocks",
], accent=RED)

card(s, 6.5, 1.55, 6.5, 2.5, "How We Found It", [
    "✦  Captured OEM tool CAN log for VER1 flash",
    "✦  Compared 0x04 (block init) frame addresses",
    "✦  OEM sends 7 block-init frames — we sent only 5",
    "✦  Analysed VER1 Intel HEX file record addresses",
    "✦  Discovered non-contiguous records at 2 locations",
    "✦  Gap between records > half the record byte count",
], accent=ORANGE)

rect(s, 0.35, 4.2, 12.55, 0.38, fill=ORANGE)
txt(s, "STRIDE ANOMALY DETECTION ALGORITHM", 0.55, 4.23, 10, 0.30,
    size=10, bold=True, color=WHITE)

mono_block(s, 0.35, 4.65, 6.1, 1.12, [
    "for each record in HEX file:",
    "  if (current_addr - prev_addr) > prev_byte_count / 2:",
    "      → STRIDE ANOMALY  →  start new block here",
    "  if sector changes (addr // 0x2000 differs):",
    "      → SECTOR BOUNDARY  →  start new block here",
], size=9)

card(s, 6.6, 4.65, 6.4, 1.12, "Block ID Assignment", [
    "block_id = (0x3F4000 − block_addr) ÷ 0x2000",
    "Last block always gets block_id = 1",
    "VER1 → 7 blocks:  IDs  6, 5, 5, 4, 3, 2, 1",
    "VER2/3 → 5 blocks: IDs  6, 5, 4, 3, 1  (no anomaly)",
], accent=ORANGE, bullet_size=10.5)

card(s, 0.35, 5.88, 12.55, 1.32, "Result", [
    "✅  Auto-detection: parse HEX → detect anomalies → choose OEM parser OR sequential parser automatically",
    "✅  VER1 now flashes correctly with exactly the same block structure as the OEM tool",
    "✅  VER2 and VER3 use the simpler sequential path — no OEM parser needed",
], accent=GREEN, bullet_size=11)

footer(s)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 7 — HEARTBEAT & ADDRESSING
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
header(s, "Addressing, Heartbeat Formula & Wakeup Modes",
       "How the tool identifies the ECU and handles both live and cold-start scenarios", accent=PURPLE)

card(s, 0.35, 1.55, 4.0, 2.55, "ECU Addressing", [
    "dev_id in CAN ID (low byte):",
    "  Oil Pump  → 0x05",
    "  Air Pump  → 0x06",
    "",
    "Tool TX:  0x1800 00 <dev_id> FF",
    "ECU  RX:  0x1800 FF <dev_id> 00",
    "Broadcast: 0x1800FFFF (shared)",
], accent=PURPLE)

card(s, 4.6, 1.55, 4.35, 2.55, "Heartbeat Byte Formula", [
    "hb_byte = (BLOCK_ID_BASE − base_addr)",
    "          ÷ ADDR_STEP + 1",
    "",
    "BLOCK_ID_BASE = 0x003F4000",
    "ADDR_STEP     = 0x2000  (8 KB)",
    "",
    "base 0x3E8000 → hb_byte = 0x07",
    "base 0x3EA000 → hb_byte = 0x06",
    "Auto-read from Intel HEX file ✓",
], accent=PURPLE)

card(s, 9.2, 1.55, 3.78, 2.55, "Why It Matters", [
    "hb_byte tells ECU which",
    "flash sectors to unlock",
    "",
    "Wrong hb_byte →",
    "ECU ignores heartbeat",
    "→ flash never starts",
    "",
    "OEM tool hardcoded it.",
    "We compute it from HEX.",
], accent=NAVY)

rect(s, 0.35, 4.25, 12.55, 0.38, fill=PURPLE)
txt(s, "TWO WAKEUP MODES — HANDLED AUTOMATICALLY", 0.55, 4.28, 10, 0.30,
    size=10, bold=True, color=WHITE)

card(s, 0.35, 4.72, 6.1, 2.5, "Mode A — Live Running ECU", [
    "ECU is powered and running application firmware",
    "",
    "1. Send broadcast: FF 02 <ecu_addr> 00…  on 0x1800FFFF",
    "2. ECU ACKs with:  FF 82 <ecu_addr> 00…  on ecu_id",
    "3. ECU reboots into bootloader (300 ms)",
    "4. Start heartbeat loop — ECU responds quickly",
    "5. Flash proceeds normally",
], accent=GREEN, bullet_size=10.5)

card(s, 6.6, 4.72, 6.1, 2.5, "Mode B — Cold Start / Already in Bootloader", [
    "ECU is powered off or already in bootloader",
    "",
    "1. Send broadcast (no ACK expected — ECU not running)",
    "2. Start heartbeat loop — 60 attempts × 100 ms = 6 s",
    "3. User powers on ECU during heartbeat window",
    "4. ECU boots into bootloader, sees heartbeat, responds",
    "5. Flash proceeds normally",
], accent=ORANGE, bullet_size=10.5)

footer(s)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 8 — INTEGRATION INTO FLASHXPERT
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
header(s, "Integration into JSW FlashXpert",
       "From reverse-engineered protocol to production-ready flashing tool", accent=GREEN)

card(s, 0.35, 1.55, 6.1, 2.6, "Software Architecture", [
    "flashing_logic.py",
    "  ├─ CANBusWrapper       PEAK / Vector / Kvaser",
    "  ├─ FlashingLogic       Existing UDS controllers",
    "  ├─ PumpFlashingLogic   Oil Pump + Air Pump",
    "  │    ├─ _pump_load_hex()         HEX parser",
    "  │    ├─ _pump_build_oem_blocks() VER1 parser",
    "  │    └─ _pump_build_blocks_sequential()",
    "  └─ FOTAFlashingLogic   Phase 2 VCU FOTA",
    "",
    "jsw_gui.py  — unified GUI, Phase 1 + Phase 2 tabs",
], accent=GREEN, bullet_size=10)

card(s, 6.6, 1.55, 6.4, 2.6, "What Was Eliminated", [
    "✅  candebug.exe — no longer needed",
    "✅  USBCAN hardware — no longer needed",
    "✅  OEM engineer dependency — gone",
    "✅  Separate workflow for pumps — gone",
    "✅  Unknown error codes — now fully logged",
    "✅  Manual block counting — auto-detected",
    "✅  Hardcoded heartbeat byte — computed from HEX",
    "✅  No traceability — full timestamped log",
    "✅  Single EXE — no Python needed on target PC",
], accent=GREEN, bullet_size=10.5)

card(s, 0.35, 4.35, 3.9, 2.85, "Hardware", [
    "PEAK PCAN-USB",
    "(already in field)",
    "",
    "PCANBasic.dll",
    "direct integration",
    "",
    "No additional",
    "hardware purchase",
], accent=NAVY, bullet_size=11)

card(s, 4.5, 4.35, 4.1, 2.85, "Validated On Vehicle", [
    "✅ Oil Pump VER1 — 7 OEM blocks",
    "✅ Oil Pump VER2 — 5 seq blocks",
    "✅ Oil Pump VER3 — 5 seq blocks",
    "✅ Air Pump — live ECU wakeup",
    "✅ Bad sector ECU diagnosed",
    "    (1798ms vs 860ms erase time)",
    "✅ Broadcast wakeup confirmed",
], accent=NAVY, bullet_size=11)

card(s, 8.85, 4.35, 4.1, 2.85, "Key Numbers", [
    "8 bytes  — frame size",
    "6 bytes  — payload per frame",
    "250 kbps — CAN bitrate",
    "8 KB     — sector / addr step",
    "16 KB    — max block size",
    "0x2000   — ADDR_STEP",
    "0x3F4000 — BLOCK_ID_BASE",
], accent=BLUE, bullet_size=11)

footer(s)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 9 — OUTCOMES & THANK YOU
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
rect(s, 0, 0, 13.33, 7.5, fill=NAVY)
rect(s, 0, 4.9, 13.33, 0.08, fill=GREEN)
rect(s, 0, 4.98, 13.33, 2.52, fill=BLUE)

txt(s, "Full Protocol Ownership.", 0.8, 0.55, 12.0, 1.1,
    size=48, bold=True, color=WHITE)
txt(s, "Zero OEM Dependency.", 0.8, 1.6,  12.0, 1.1,
    size=48, bold=True, color=CGREEN)

txt(s, "We reverse-engineered a proprietary CAN flash protocol from captured traffic alone,\n"
       "implemented it in Python using PEAK hardware we already own, auto-detect all firmware\n"
       "variants, handle live and cold-start ECUs — and shipped it as part of JSW FlashXpert.",
    0.8, 2.85, 12.0, 1.0, size=13, color=CBLUE)

txt(s, "Controls & Software Department  —  R&D, JSW Greentech Limited  |  2025",
    0.8, 5.3, 11.0, 0.42, size=11, color=CBLUE)
txt(s, "JSW FlashXpert  V2.0",
    0.8, 5.75, 5.0, 0.38, size=11, bold=True, color=WHITE)

footer(s)

# ── Save ──────────────────────────────────────────────────────────────────────
out = "JSW_PumpFlash_ReverseEngineering.pptx"
prs.save(out)
print(f"Saved: {out}")
