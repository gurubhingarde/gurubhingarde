"""Session configuration.

Captures the same knobs the original tool stored in its app settings
(addresses, baudrate, security key, block sizes, transport selection) in a
plain dataclass that loads from / saves to JSON.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Optional


@dataclass
class Config:
    # transport selection: "doip" | "can"
    transport: str = "doip"

    # --- DoIP / Ethernet ---
    doip_host: str = ""              # ECU/entity IP (blank => use discovery)
    doip_port: int = 13400
    doip_bind_addr: str = "0.0.0.0"  # local NIC IP to send/bind from
    doip_activation_type: int = 0x00

    # --- CAN / CAN-FD ---
    can_interface: str = "virtual"   # python-can interface (pcan/vector/zlgcan/...)
    can_channel: str = "0"
    can_fd: bool = False
    can_bitrate: int = 500000
    can_data_bitrate: int = 2000000
    can_extended_id: bool = False
    can_tx_id: int = 0x18DA00F9      # tester -> ECU (29-bit example)
    can_rx_id: int = 0x18DAF900      # ECU -> tester

    # --- diagnostic addressing (logical addresses) ---
    tester_addr: int = 0x0E00        # DoIP source / "TOOL_SA" analogue
    ecu_addr: int = 0x0E80           # DoIP target / "TE_ADDR" analogue

    # --- flash parameters ---
    security_level: int = 0x01       # SecurityAccess request-seed level (odd)
    security_key: str = "0xFFFF"     # shared secret / key seed (SecKey analogue)
    block_size: int = 0x400          # max TransferData block payload (MinDataSizeDoIP)
    addr_len: int = 4                # RequestDownload address length
    size_len: int = 4                # RequestDownload size length
    compression: int = 0x0           # data-format high nibble (0 = none)
    encryption: int = 0x0            # data-format low nibble (0 = none)

    # --- mapping / zone preset (from Actiway_DownLoad_Tool.xml / Zones_Config) ---
    preset_name: str = ""            # selected Mapping desc, e.g. "Multic-S -> CALIB"
    zone: int = 0                    # memory zone value
    addr_start: Optional[int] = None  # flash window start (preset)
    addr_end: Optional[int] = None    # flash window end (preset, inclusive)
    sha256_start: Optional[int] = None   # where the image SHA-256 is stored
    sha256_length: Optional[int] = None  # length of the stored SHA-256
    mem_check: int = 0               # memory-check flag

    # --- timing ---
    p2_timeout: float = 2.0
    p2_star_timeout: float = 5.0
    tester_present_interval: float = 2.0

    @classmethod
    def load(cls, path: str) -> "Config":
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        known = {f: data[f] for f in cls.__dataclass_fields__ if f in data}
        return cls(**known)

    def save(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(asdict(self), fh, indent=2)

    @property
    def data_format(self) -> int:
        return ((self.compression & 0xF) << 4) | (self.encryption & 0xF)
