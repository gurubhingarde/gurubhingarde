"""Firmware image parsing: Motorola S-record and Intel HEX.

Reconstructed from FileConverter.GestMotoValue / Segment / ReprogrammingBlock in
the original tool. Produces a flat address->byte map plus contiguous segments,
which is what the UDS RequestDownload/TransferData flow consumes.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Segment:
    """A contiguous run of bytes at a start address (FileConverter.Segment)."""
    start_addr: int
    data: bytes

    @property
    def end_addr(self) -> int:
        return self.start_addr + len(self.data) - 1

    @property
    def size(self) -> int:
        return len(self.data)

    def __repr__(self) -> str:
        return f"Segment(0x{self.start_addr:08X}..0x{self.end_addr:08X}, {self.size} bytes)"


@dataclass
class ReprogrammingBlock:
    """One logical block to flash (FileConverter.ReprogrammingBlock)."""
    name: str = ""
    logical_index: int = 0
    file_name: str = ""
    file_type: str = ""
    segments: list[Segment] = field(default_factory=list)

    @property
    def total_size(self) -> int:
        return sum(s.size for s in self.segments)


class FirmwareParseError(ValueError):
    pass


# ---------------------------------------------------------------------------
# Motorola S-record
# ---------------------------------------------------------------------------
def parse_srec(text: str) -> list[Segment]:
    chunks: dict[int, int] = {}  # addr -> byte
    for ln, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line or not line.startswith("S"):
            continue
        rtype = line[1]
        try:
            count = int(line[2:4], 16)
            body = bytes.fromhex(line[4:4 + count * 2])
        except ValueError as e:
            raise FirmwareParseError(f"S-record line {ln}: {e}") from e
        # checksum validation
        got = body[-1]
        calc = (~(count + sum(body[:-1])) & 0xFF)
        if got != calc:
            raise FirmwareParseError(
                f"S-record line {ln}: checksum 0x{got:02X} != 0x{calc:02X}")
        addr_len = {"1": 2, "2": 3, "3": 4}.get(rtype)
        if addr_len is None:
            continue  # S0 header, S5/6 count, S7/8/9 start-addr -> skip
        addr = int.from_bytes(body[:addr_len], "big")
        payload = body[addr_len:-1]
        for i, b in enumerate(payload):
            chunks[addr + i] = b
    return _coalesce(chunks)


# ---------------------------------------------------------------------------
# Intel HEX
# ---------------------------------------------------------------------------
def parse_ihex(text: str) -> list[Segment]:
    chunks: dict[int, int] = {}
    base = 0
    for ln, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line or not line.startswith(":"):
            continue
        try:
            raw = bytes.fromhex(line[1:])
        except ValueError as e:
            raise FirmwareParseError(f"Intel HEX line {ln}: {e}") from e
        count, addr, rtype = raw[0], int.from_bytes(raw[1:3], "big"), raw[3]
        data = raw[4:4 + count]
        if (sum(raw) & 0xFF) != 0:
            raise FirmwareParseError(f"Intel HEX line {ln}: bad checksum")
        if rtype == 0x00:      # data
            for i, b in enumerate(data):
                chunks[base + addr + i] = b
        elif rtype == 0x01:    # EOF
            break
        elif rtype == 0x02:    # extended segment address
            base = int.from_bytes(data, "big") << 4
        elif rtype == 0x04:    # extended linear address
            base = int.from_bytes(data, "big") << 16
        # 0x03/0x05 start-address records -> ignored
    return _coalesce(chunks)


def _coalesce(chunks: dict[int, int]) -> list[Segment]:
    if not chunks:
        return []
    segs: list[Segment] = []
    buf = bytearray()
    start = prev = None
    for addr in sorted(chunks):
        if start is None:
            start = prev = addr
            buf = bytearray([chunks[addr]])
        elif addr == prev + 1:
            buf.append(chunks[addr])
            prev = addr
        else:
            segs.append(Segment(start, bytes(buf)))
            start = prev = addr
            buf = bytearray([chunks[addr]])
    segs.append(Segment(start, bytes(buf)))
    return segs


def load_firmware(path: str) -> ReprogrammingBlock:
    """Auto-detect S-record vs Intel HEX vs raw binary from `path`."""
    with open(path, "rb") as f:
        raw = f.read()
    import os
    name = os.path.basename(path)
    ext = os.path.splitext(name)[1].lower()
    head = raw[:4].lstrip()
    if ext in (".s19", ".s28", ".s37", ".srec", ".mot", ".mhx") or head.startswith(b"S"):
        segs = parse_srec(raw.decode("ascii", "replace"))
        ftype = "SREC"
    elif ext in (".hex", ".ihex") or head.startswith(b":"):
        segs = parse_ihex(raw.decode("ascii", "replace"))
        ftype = "IHEX"
    else:
        segs = [Segment(0, raw)]   # treat as raw binary at address 0
        ftype = "BIN"
    return ReprogrammingBlock(name=name, file_name=name, file_type=ftype, segments=segs)


def filter_range(block: ReprogrammingBlock, start: int, end: int) -> ReprogrammingBlock:
    """Clip a block's segments to [start, end] (inclusive) if end > start."""
    if end <= start:
        return block
    out: list[Segment] = []
    for s in block.segments:
        lo, hi = max(s.start_addr, start), min(s.end_addr, end)
        if lo <= hi:
            out.append(Segment(lo, s.data[lo - s.start_addr: hi - s.start_addr + 1]))
    return ReprogrammingBlock(block.name, block.logical_index, block.file_name,
                              block.file_type, out)
