"""Settings, zones, mapping presets and the DID catalogue.

Mapping presets and zones are loaded from the SAME XML files the supplier tool
uses (`data/presets.xml` == Actiway_DownLoad_Tool.xml,
`data/zones.xml` == Actiway_Zones_Config.xml), so the full list of mappings is
available and you can add/edit mappings by editing the XML — exactly like the
original. A hardcoded fallback is used only if the XML is missing.

Each mapping carries its own address range, min block sizes, optional SHA-256
region, and optional Sec Key. Selecting a mapping in the GUI auto-fills the Sec
Key and Zone, matching the supplier tool's behaviour.
"""
from __future__ import annotations

import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# Defaults straight from the original *.exe.config
DEFAULTS = {
    "TOOL_SA": 0xF9,
    "CAN_SA": 0xFE,
    "EXTEND_PRIO": 0x18,
    "SecKey": 0xFFFF,          # used when a mapping has no <seckey> of its own
    "MinDataSizeCAN": 0x10,
    "MinDataSizeDoIP": 0x400,
    "CAN_Baudrate": 500000,
    "TE": 0x0E00,              # DoIP tester (source) address seen in the tool
}
DEFAULT_SECKEY = DEFAULTS["SecKey"]


# ---------------------------------------------------------------------------
# Mapping presets (Actiway_DownLoad_Tool.xml)
# ---------------------------------------------------------------------------
@dataclass
class Preset:
    desc: str
    zone: int = 0
    start: int = 0
    end: int = 0
    min_can: int = 0x10
    min_doip: int = 0x400
    mem_check: int = 0
    seckey: int | None = None          # None -> use DEFAULTS["SecKey"]
    sha256_start: int | None = None
    sha256_length: int | None = None

    @property
    def effective_seckey(self) -> int:
        return DEFAULT_SECKEY if self.seckey is None else self.seckey


def preset_for_range(presets: "list[Preset]", lo: int, hi: int) -> "Preset | None":
    """Return the tightest mapping whose [start, end] window fully contains the
    image span [lo, hi]. Used to auto-target the right zone (EA/WIRING/EW/...)
    from a loaded firmware's addresses: a smaller matching window beats a larger
    one, so an EW image (0x18480000-0x18FFFFF7) picks the EW mapping rather than
    the all-encompassing APP_ALL+BSP. Returns None if no window contains it."""
    best = None
    for p in presets:
        if p.end > p.start and p.start <= lo and hi <= p.end:
            if best is None or (p.end - p.start) < (best.end - best.start):
                best = p
    return best


def _text_int(node, tag, default=None):
    el = node.find(tag)
    if el is None or el.text is None or not el.text.strip():
        return default
    return int(el.text.strip(), 0)


def load_presets(path: str | None = None) -> list[Preset]:
    path = path or os.path.join(_DATA, "presets.xml")
    try:
        root = ET.parse(path).getroot()
    except (OSError, ET.ParseError):
        return list(_FALLBACK_PRESETS)
    out: list[Preset] = []
    for p in root.findall("preset"):
        desc_el = p.find("desc")
        desc = (desc_el.text or "").strip() if desc_el is not None else ""
        out.append(Preset(
            desc=desc,
            zone=_text_int(p, "zone", 0),
            start=_text_int(p, "start", 0),
            end=_text_int(p, "end", 0),
            min_can=_text_int(p, "MinDataSizeCAN", 0x10),
            min_doip=_text_int(p, "MinDataSizeDoIP", 0x400),
            mem_check=_text_int(p, "memCheck", 0),
            seckey=_text_int(p, "seckey", None),
            sha256_start=_text_int(p, "SHA256Start", None),
            sha256_length=_text_int(p, "SHA256Length", None),
        ))
    return out or list(_FALLBACK_PRESETS)


# ---------------------------------------------------------------------------
# Zones (Actiway_Zones_Config.xml) -- note Index (list position) != Value
# ---------------------------------------------------------------------------
@dataclass
class Zone:
    name: str
    index: int
    value: int


def load_zones(path: str | None = None) -> list[Zone]:
    path = path or os.path.join(_DATA, "zones.xml")
    try:
        root = ET.parse(path).getroot()
    except (OSError, ET.ParseError):
        return list(_FALLBACK_ZONES)
    out: list[Zone] = []
    for z in root.findall("Zone"):
        name_el = z.find("Name")
        name = " ".join((name_el.text or "").split()) if name_el is not None else ""
        out.append(Zone(name=name,
                        index=_text_int(z, "Index", 0),
                        value=_text_int(z, "Value", 0)))
    return out or list(_FALLBACK_ZONES)


def zone_by_value(zones: list[Zone], value: int) -> Zone | None:
    for z in zones:
        if z.value == value:
            return z
    return None


# Loaded once at import for convenience; the GUI re-loads to pick up edits.
PRESETS: list[Preset] = load_presets()
ZONES: list[Zone] = load_zones()


# ---------------------------------------------------------------------------
# Diagnostic DID catalogue (MulticS.xml, SID 0x22 ReadDataByIdentifier)
# ---------------------------------------------------------------------------
INFO_DIDS = {
    0xF180: "Boot Software version",
    0xF181: "Monitor Software Banner",
    0xF182: "Calibration DATA Software Banner",
    0xF190: "VIN",
    0xFE00: "BSP Software Library Banner",
    0xFE04: "Kwp Software Library Banner",
    0xFE05: "DoC Software Library Banner",
    0xFE06: "J1939 Software Library Banner",
    0xFE07: "Eeprom Software Library Banner",
    0xFE08: "TcpIP Software Library Banner",
    0xFE09: "DoIP Software Library Banner",
}


# ---------------------------------------------------------------------------
# Fallbacks (used only if the XML files are absent) -- full supplier list
# ---------------------------------------------------------------------------
_FALLBACK_PRESETS = [
    Preset("Multic-SX -> APP_ALL+BSP", 0, 0x18080000, 0x18FFFFF7, 0x20),
    Preset("Multic-S -> CALIB", 1, 0x18040000, 0x1807FFF7, 0x10,
           seckey=0xFFFFFFFF, sha256_start=0x1807FFC4, sha256_length=32),
    Preset("Multic-S -> APP_MONITOR+BSP", 2, 0x18080000, 0x1827FFF7, 0x10,
           seckey=0xFFFFFFFF, sha256_start=0x1827FFC4, sha256_length=32),
    Preset("Multic-S -> APP_EA_Vx_xx", 3, 0x18280000, 0x1843FFF7, 0x10),
    Preset("Multic-S -> APP_WIRING", 4, 0x18440000, 0x1847FFF7, 0x10),
    Preset("Multic-S -> APP_EW_Vx_xx", 5, 0x18480000, 0x18FFFFF7, 0x10),
    Preset("IRB-STD3X -> APP_ALL+BSP", 0, 0x60080000, 0x60FFFFF7, 0x20),
    Preset("IRB-STD3 -> CALIB", 1, 0x60040000, 0x6007FFF7, 0x10),
    Preset("IRB-STD3 -> APP_MONITOR+BSP", 2, 0x60080000, 0x6027FFF7, 0x10),
    Preset("IRB-STD3 -> APP_EA_Vx_xx", 3, 0x60280000, 0x6043FFF7, 0x10),
    Preset("IRB-STD3 -> APP_WIRING", 4, 0x60440000, 0x6047FFF7, 0x10),
    Preset("IRB-STD3 -> APP_EW_Vx_xx", 5, 0x60480000, 0x60FFFFF7, 0x10),
    Preset("CSG -> CALIB", 1, 0x18080000, 0x1808FFF7, 0x10),
    Preset("CSG -> APP_MONITOR+BSP", 2, 0x180C0000, 0x181FFFF7, 0x10,
           seckey=0xFFFFFFFF, sha256_start=0x181FFFC4, sha256_length=32),
    Preset("CSG -> APP_EA_Vx_xx", 3, 0x18280000, 0x1843FFF7, 0x10),
    Preset("Power33S", 0, 0x00FE0030, 0x00FFFFFF, 0x20),
    Preset("ACH-PowersC", 0, 0x00020000, 0x000FFFFF, 0x20),
    Preset("ACH-LCC", 0, 0x00FC0030, 0x00FFFFFF, 0x20),
]

_FALLBACK_ZONES = [
    Zone("0  : Main MCU Application (*)", 0, 0),
    Zone("1  : Main MCU Calibration (*)", 1, 1),
    Zone("2  : Main MCU Data", 2, 2),
    Zone("3  : Main MCU AppAndData", 3, 3),
    Zone("4  : Main MCU Eeprom", 4, 4),
    Zone("5  : Main MCU NVRam", 5, 5),
    Zone("10: Aux MCU Application", 6, 10),
    Zone("11: Aux MCU Calibration", 7, 11),
    Zone("12: Aux MCU Data", 8, 12),
    Zone("13: Aux MCU Application and Data", 9, 13),
    Zone("14: Aux MCU Eeprom", 10, 14),
    Zone("15: Aux MCU NVRam", 11, 15),
    Zone("20: FPGA Bitstream", 12, 20),
    Zone("30: PLCRteAll", 13, 30),
    Zone("31: PLCRte", 14, 31),
    Zone("32: PLC application code", 15, 32),
    Zone("33: PLC Application Calibration", 16, 33),
    Zone("34: PLC Secondary Application", 17, 34),
]
