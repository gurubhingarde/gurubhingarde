"""Download presets ("Mapping") and memory zones.

The original tool's Download tab has a **Mapping** dropdown (e.g.
"Multic-S -> CALIB") and a **Zone** dropdown. Those lists come from two XML
files that ship beside the executable:

* ``Actiway_DownLoad_Tool.xml`` - the preset list (one ``<preset>`` per entry)
* ``Actiway_Zones_Config.xml``  - the zone list

This module parses both formats so dltool can offer the same dropdowns. A
preset carries the flash address window, per-transport block size, optional
security key and optional SHA-256 integrity location; :func:`apply_preset`
copies those onto a :class:`~dltool.config.Config`.

You can point the loaders at the original XML files, or at the copies bundled
under ``dltool/data/``.
"""

from __future__ import annotations

import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List, Optional

from .config import Config

_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DEFAULT_PRESETS_XML = os.path.join(_DATA_DIR, "presets.xml")
DEFAULT_ZONES_XML = os.path.join(_DATA_DIR, "zones.xml")


def _text(node: Optional[ET.Element]) -> str:
    return (node.text or "").strip() if node is not None else ""


def _int(node: Optional[ET.Element]) -> Optional[int]:
    t = _text(node)
    if not t:
        return None
    return int(t, 0)  # accepts 0x.. and decimal


@dataclass
class Preset:
    """One Mapping entry: product/zone profile + flash window + block size."""

    desc: str
    zone: int = 0
    start: Optional[int] = None
    end: Optional[int] = None
    min_data_can: int = 0x10
    min_data_doip: int = 0x400
    sha256_start: Optional[int] = None
    sha256_length: Optional[int] = None
    seckey: Optional[int] = None
    mem_check: int = 0

    @property
    def size(self) -> Optional[int]:
        if self.start is None or self.end is None:
            return None
        return self.end - self.start + 1

    def block_size(self, transport: str) -> int:
        return self.min_data_doip if transport == "doip" else self.min_data_can

    def __str__(self) -> str:
        win = (f"0x{self.start:08X}..0x{self.end:08X}"
               if self.start is not None and self.end is not None else "-")
        return f"{self.desc:<28} zone={self.zone:<2} {win}"


@dataclass
class Zone:
    """One Zone entry from the zones config."""

    name: str
    index: int
    value: int


def load_presets(path: Optional[str] = None) -> List[Preset]:
    """Parse the preset ("Mapping") XML into a list of :class:`Preset`."""
    path = path or DEFAULT_PRESETS_XML
    root = ET.parse(path).getroot()
    out: List[Preset] = []
    for p in root.findall("preset"):
        out.append(Preset(
            desc=_text(p.find("desc")),
            zone=_int(p.find("zone")) or 0,
            start=_int(p.find("start")),
            end=_int(p.find("end")),
            min_data_can=_int(p.find("MinDataSizeCAN")) or 0x10,
            min_data_doip=_int(p.find("MinDataSizeDoIP")) or 0x400,
            sha256_start=_int(p.find("SHA256Start")),
            sha256_length=_int(p.find("SHA256Length")),
            seckey=_int(p.find("seckey")),
            mem_check=_int(p.find("memCheck")) or 0,
        ))
    return out


def load_zones(path: Optional[str] = None) -> List[Zone]:
    """Parse the zones XML into a list of :class:`Zone`."""
    path = path or DEFAULT_ZONES_XML
    root = ET.parse(path).getroot()
    out: List[Zone] = []
    for z in root.findall("Zone"):
        out.append(Zone(
            name=_text(z.find("Name")),
            index=_int(z.find("Index")) or 0,
            value=_int(z.find("Value")) or 0,
        ))
    return out


def find_preset(presets: List[Preset], desc: str) -> Preset:
    """Look up a preset by its (whitespace-insensitive) description."""
    key = desc.strip().lower()
    for p in presets:
        if p.desc.strip().lower() == key:
            return p
    raise KeyError(f"no preset named {desc!r}; available: {[p.desc for p in presets]}")


def apply_preset(cfg: Config, preset: Preset) -> Config:
    """Copy a preset's flash parameters onto ``cfg`` (in place) and return it."""
    cfg.preset_name = preset.desc
    cfg.zone = preset.zone
    cfg.addr_start = preset.start
    cfg.addr_end = preset.end
    cfg.block_size = preset.block_size(cfg.transport)
    cfg.sha256_start = preset.sha256_start
    cfg.sha256_length = preset.sha256_length
    cfg.mem_check = preset.mem_check
    if preset.seckey is not None:
        cfg.security_key = f"0x{preset.seckey:X}"
    return cfg
