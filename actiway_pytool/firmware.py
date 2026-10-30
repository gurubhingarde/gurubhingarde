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


def parse_actia_banner(data: bytes) -> str:
    """Decode an ACTIA Multic DID banner (SID 22 response payload after the DID).

    Layout (66 bytes): tag(1) version(3) partno(10) name(20) vendor(10)
    date(12) time(10), each string NUL-padded. Returns a one-line summary;
    falls back to a hex/ascii dump for anything that doesn't fit the layout.
    """
    def s(b):
        return b.split(b"\x00", 1)[0].decode("latin1", "replace").strip()

    if len(data) >= 66 and data[0] == 0x42:
        ver = ".".join(str(x) for x in data[1:4])
        part = s(data[4:14])
        name = s(data[14:34])
        vendor = s(data[34:44])
        date = s(data[44:56])
        tm = s(data[56:66])
        return f"{name}  part={part}  v{ver}  {vendor}  {date} {tm}".strip()
    if all(b == 0xFF for b in data):
        return "(not programmed)"
    txt = "".join(chr(c) if 32 <= c < 127 else "." for c in data)
    return f"{data.hex(' ').upper()}  |{txt}|"


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


def build_download_blocks(block: ReprogrammingBlock, align: int = 0x400,
                          pad: int = 0xFF) -> list[Segment]:
    """Merge raw segments into page-aligned download blocks, matching the
    supplier tool (FileConverter.MegreData): each segment is widened to `align`
    page boundaries, overlapping/adjacent pages are merged, and interior gaps
    (and the alignment padding) are filled with `pad`.

    Returns one Segment per RequestDownload. Verified against EA_V1_00.Mot to
    reproduce the supplier's 4 download blocks exactly.
    """
    if not block.segments:
        return []
    # 1) page-align each segment's [start, end]
    spans = []
    for s in block.segments:
        lo = s.start_addr - (s.start_addr % align)
        hi = s.end_addr + (align - 1 - (s.end_addr % align))
        spans.append((lo, hi, s))
    spans.sort(key=lambda x: x[0])

    # 2) merge overlapping / adjacent aligned spans
    blocks: list[list] = []
    for lo, hi, s in spans:
        if blocks and lo <= blocks[-1][1] + 1:
            blocks[-1][1] = max(blocks[-1][1], hi)
            blocks[-1][2].append(s)
        else:
            blocks.append([lo, hi, [s]])

    # 3) materialise each block, pad-filled, with real segment bytes placed in
    out: list[Segment] = []
    for lo, hi, segs in blocks:
        buf = bytearray([pad]) * (hi - lo + 1)
        for s in segs:
            off = s.start_addr - lo
            buf[off:off + len(s.data)] = s.data
        out.append(Segment(lo, bytes(buf)))
    return out


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
