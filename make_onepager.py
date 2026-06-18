#!/usr/bin/env python3
"""Generate 1-page technical brief: Reverse Engineering & Adapting Pump ECU Flashing."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

W, H = A4   # 595 x 842 pt

# ── Brand colours ────────────────────────────────────────────────────────────
NAVY    = HexColor("#163C69")
BLUE    = HexColor("#1F4E96")
GREEN   = HexColor("#27AE60")
ORANGE  = HexColor("#E67E22")
RED     = HexColor("#E74C3C")
GREY    = HexColor("#6B7280")
LGREY   = HexColor("#F6F8FB")
WHITE   = colors.white
BLACK   = HexColor("#111827")

def make_pdf(filename):
    c = canvas.Canvas(filename, pagesize=A4)

    # ── Header bar ───────────────────────────────────────────────────────────
    c.setFillColor(NAVY)
    c.rect(0, H-38*mm, W, 38*mm, fill=1, stroke=0)
    c.setFillColor(GREEN)
    c.rect(0, H-40*mm, W, 2*mm, fill=1, stroke=0)

    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(12*mm, H-16*mm, "Reverse Engineering Pump ECU Flash Protocol")
    c.setFont("Helvetica", 10)
    c.setFillColor(HexColor("#93C5FD"))
    c.drawString(12*mm, H-24*mm,
        "How JSW Controls & Software decoded a proprietary CAN protocol and built full in-house flash capability")
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(HexColor("#6ED8A4"))
    c.drawRightString(W-12*mm, H-16*mm, "JSW FlashXpert  V2.0")
    c.setFont("Helvetica", 9)
    c.setFillColor(HexColor("#93C5FD"))
    c.drawRightString(W-12*mm, H-24*mm, "Controls & Software Dept  |  R&D JSW Greentech")

    # ── Section helper ───────────────────────────────────────────────────────
    y = H - 46*mm

    def section(title, color=NAVY):
        nonlocal y
        y -= 4*mm
        c.setFillColor(color)
        c.rect(12*mm, y-1*mm, W-24*mm, 6.5*mm, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(14*mm, y+1.2*mm, title.upper())
        y -= 7*mm

    def body(lines, indent=14, line_h=4.3, color=BLACK, font="Helvetica", size=8.5):
        nonlocal y
        c.setFont(font, size)
        c.setFillColor(color)
        for line in lines:
            if y < 20*mm:
                break
            c.drawString(indent*mm, y, line)
            y -= line_h*mm

    def two_col(left_lines, right_lines, line_h=4.3):
        nonlocal y
        mid = W/2
        c.setFont("Helvetica", 8.5)
        c.setFillColor(BLACK)
        max_lines = max(len(left_lines), len(right_lines))
        for i in range(max_lines):
            if y < 20*mm: break
            if i < len(left_lines):
                c.drawString(14*mm, y, left_lines[i])
            if i < len(right_lines):
                c.drawString(mid+2*mm, y, right_lines[i])
            y -= line_h*mm

    def mono(lines, indent=14, line_h=4.2, bg=HexColor("#1E2A3A"), fg=HexColor("#6ED8A4")):
        nonlocal y
        box_h = len(lines) * line_h * mm + 3*mm
        c.setFillColor(bg)
        c.rect(indent*mm, y - box_h + 2*mm, W - (indent+indent-2)*mm, box_h, fill=1, stroke=0)
        c.setFont("Courier-Bold", 8)
        c.setFillColor(fg)
        ty = y - 0.5*mm
        for line in lines:
            c.drawString((indent+2)*mm, ty, line)
            ty -= line_h*mm
        y -= box_h + 1*mm

    def gap(n=3):
        nonlocal y
        y -= n*mm

    def divider():
        nonlocal y
        c.setStrokeColor(HexColor("#E5E7EB"))
        c.setLineWidth(0.4)
        c.line(12*mm, y, W-12*mm, y)
        y -= 2*mm

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 1 — THE PROBLEM
    # ════════════════════════════════════════════════════════════════════════
    section("1. The Problem — OEM Tool Dependency", NAVY)
    two_col(
        ["❌  Oil Pump & Air Pump ECUs shipped with a",
         "    proprietary Chinese OEM tool (candebug.exe)",
         "❌  Source code unavailable — closed binary",
         "❌  Uses USBCAN hardware — not our PEAK adapters",
         "❌  No automation possible — GUI-only operation"],
        ["❌  Protocol was completely undocumented",
         "❌  Any firmware update required OEM presence",
         "❌  Could not integrate into our existing workflow",
         "❌  Zero control over error handling or logging",
         "❌  Single point of failure for production flashing"]
    )
    gap(2)

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 2 — REVERSE ENGINEERING APPROACH
    # ════════════════════════════════════════════════════════════════════════
    section("2. Reverse Engineering Approach — CAN Log Capture & Analysis", BLUE)
    two_col(
        ["STEP 1 — Passive CAN Capture",
         "  • Connected PEAK PCAN-USB to the vehicle bus",
         "  • Ran OEM tool to flash a known-good ECU",
         "  • Captured full CAN bus log (timestamped frames)",
         "",
         "STEP 2 — Frame Identification",
         "  • Isolated frames on extended IDs 0x180005FF",
         "    and 0x1800FF05 (tool ↔ ECU pair)",
         "  • Confirmed broadcast ID 0x1800FFFF on connect",
         "  • Identified 0x1800EEEE as NAK / error channel"],
        ["STEP 3 — Pattern Analysis",
         "  • All frames exactly 8 bytes long",
         "  • Byte[7] = XOR of bytes [0..6]  → checksum",
         "  • Byte[0] cycles: 0x04 → 0x01 → 0x02 → 0x01…",
         "    then 0x00, then 0x04 → …  for each block",
         "",
         "STEP 4 — Confirm ACK Mechanism",
         "  • ECU replies with the EXACT same 8 bytes",
         "    on its own CAN ID (echo-ACK model)",
         "  • Timeout = no echo within window → retry/fail"]
    )
    gap(1)

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 3 — PROTOCOL DECODED
    # ════════════════════════════════════════════════════════════════════════
    section("3. Protocol Decoded — 8-Byte Custom CAN Frame", GREEN)
    mono([
        "Frame layout:  [ TYPE ][ P1 ][ P2 ][ P3 ][ P4 ][ P5 ][ P6 ][ XOR8 ]",
        "",
        "TYPE = 0x00  →  Heartbeat (wakeup)  or  End-of-Block  (with block_id in P2)",
        "TYPE = 0x01  →  Data frame  (toggle A)   payload = P1..P6  (6 bytes firmware)",
        "TYPE = 0x02  →  Data frame  (toggle B)   payload = P1..P6  (6 bytes firmware)",
        "TYPE = 0x03  →  Close session            payload = CRC bytes",
        "TYPE = 0x04  →  Block init / erase        payload = addr(4B) + size(2B)",
        "XOR8 = P0 XOR P1 XOR P2 XOR P3 XOR P4 XOR P5 XOR P6    (bytes 0..6)",
    ], bg=HexColor("#0F1E30"), fg=HexColor("#6ED8A4"))

    two_col(
        ["Broadcast wakeup (live ECU):",
         "  FF 02 <ecu_addr> 00 00 00 00 <XOR>",
         "  Sent on 0x1800FFFF — ECU ACKs with FF 82 …",
         "  ECU reboots to bootloader in ~300 ms",
         "",
         "Heartbeat byte formula:",
         "  hb = (0x3F4000 − base_addr) ÷ 0x2000 + 1",
         "  Auto-computed from Intel HEX base address"],
        ["Erase + data sequence per block:",
         "  04 <addr 4B> <size 2B> → erase ACK",
         "  01 <6 bytes>           → data toggle A",
         "  02 <6 bytes>           → data toggle B",
         "  01/02 … (repeat)       → all firmware bytes",
         "  00 00 <block_id> …     → end-of-block ACK",
         "  04 <CRC addr>          → write CRC",
         "  01 <CRC verify>        → verify + close"]
    )
    gap(1)

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 4 — STRIDE ANOMALY DISCOVERY
    # ════════════════════════════════════════════════════════════════════════
    section("4. Key Discovery — VER1 Stride Anomaly & OEM Block Parser", ORANGE)
    two_col(
        ["VER1 firmware flashing failed with our first tool:",
         "  • Tool sent 5 sequential 16 KB blocks",
         "  • ECU booted but CRC mismatch on reboot",
         "",
         "Root cause found by comparing HEX files:",
         "  • VER1 Intel HEX has non-contiguous records",
         "  • Gap between records > half the record size",
         "    → called a 'stride anomaly'",
         "  • OEM tool splits at anomaly boundaries",
         "    producing 7 blocks (not 5)"],
        ["Detection algorithm implemented:",
         "  if (addr − prev_addr) > prev_byte_count ÷ 2:",
         "      → stride anomaly → new block boundary",
         "",
         "Result — VER1 produces 7 OEM-compatible blocks:",
         "  Block IDs: 6,5,5,4,3,2,1  (ID formula driven)",
         "  Block ID = (0x3F4000 − addr) ÷ 0x2000",
         "  Last block always ID = 1",
         "",
         "VER2/VER3: no anomalies → 5 sequential blocks ✓"]
    )
    gap(1)

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 5 — INTEGRATION & OUTCOME
    # ════════════════════════════════════════════════════════════════════════
    section("5. Integration into JSW FlashXpert & Full Hardware Control", RED)
    two_col(
        ["✅  PumpFlashingLogic class in flashing_logic.py",
         "    — Works with PEAK PCAN hardware we already own",
         "    — Auto-detects VER1 vs VER2/VER3 from HEX file",
         "    — Full error handling: NAK, timeout, CRC fail",
         "    — Cancellable at any step via stop event",
         "",
         "✅  Integrated into JSW FlashXpert GUI",
         "    — Same Power OFF → ON dialog as VCU/MCU",
         "    — 6-step visual progress sidebar",
         "    — Detailed timestamped log output"],
        ["✅  Zero OEM dependency — full in-house control",
         "    — No candebug.exe required ever again",
         "    — No USBCAN hardware required",
         "    — Works with PEAK / Vector / Kvaser",
         "",
         "✅  Validated on vehicle:",
         "    — Oil Pump VER1, VER2, VER3 all flash successfully",
         "    — Air Pump validated on vehicle",
         "    — Bad sector ECU diagnosed (1798ms vs 860ms erase)",
         "",
         "✅  Single EXE deployment — no Python needed on PC"]
    )

    # ── Footer ───────────────────────────────────────────────────────────────
    c.setFillColor(NAVY)
    c.rect(0, 0, W, 10*mm, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica", 7.5)
    c.drawString(12*mm, 3.5*mm,
        "JSW Greentech Limited  —  Controls & Software Department, R&D  |  CONFIDENTIAL  |  JSW FlashXpert V2.0")
    c.setFont("Helvetica-Bold", 7.5)
    c.drawRightString(W-12*mm, 3.5*mm, "1 / 1")

    c.save()
    print(f"Saved: {filename}")

make_pdf("JSW_PumpFlash_ReverseEngineering.pdf")
