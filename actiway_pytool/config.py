"""Default settings and zone/preset tables, taken from the original tool's
Actiway_DownLoad_Tool.exe.config, Actiway_Zones_Config.xml and
Actiway_DownLoad_Tool.xml.
"""
from __future__ import annotations

from dataclasses import dataclass

# Defaults straight from the original *.exe.config
DEFAULTS = {
    "TOOL_SA": 0xF9,
    "CAN_SA": 0xFE,
    "EXTEND_PRIO": 0x18,
    "SecKey": 0xFFFF,
    "MinDataSizeCAN": 0x10,
    "MinDataSizeDoIP": 0x400,
    "CAN_Baudrate": 500000,
}


@dataclass
class Zone:
    index: int
    name: str


# From Actiway_Zones_Config.xml
ZONES = [
    Zone(0, "Main MCU Application"),
    Zone(1, "Main MCU Calibration"),
    Zone(2, "BSP / Bootstrap"),
    Zone(3, "Wiring Data"),
    Zone(4, "Straton VM / Application"),
]


@dataclass
class Preset:
    desc: str
    zone: int
    start: int
    end: int
    min_can: int = 0x20
    min_doip: int = 0x400
    mem_check: int = 0


# From Actiway_DownLoad_Tool.xml
PRESETS = [
    Preset("Multic-SX -> APP_ALL+BSP", 0, 0x18080000, 0x18FFFFF7, 0x20, 0x400, 0),
    Preset("Multic-S -> CALIB", 1, 0x00000000, 0x00000000, 0x10, 0x400, 0),
]

# Diagnostic DID catalogue (from MulticS.xml, SID 0x22 ReadDataByIdentifier)
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
