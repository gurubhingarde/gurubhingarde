"""Firmware containers and the Motorola S-record parser.

Mirrors the data model a flash tool needs:

* :class:`Segment`          - one contiguous address range of bytes.
* :class:`ReprogrammingBlock` - a named logical block (one flash job):
  metadata + an ordered list of segments.
* :class:`Firmware`         - a whole file: one or more blocks.

The S-record (SREC) reader supports S0/S1/S2/S3 data records and
S5/S7/S8/S9 count/termination records, validates checksums, and coalesces
adjacent/overlapping data into contiguous segments.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Segment:
    """A contiguous run of program bytes at ``start_addr``."""

    start_addr: int
    data: bytearray = field(default_factory=bytearray)

    @property
    def end_addr(self) -> int:
        """Address of the last byte + 1 (exclusive end)."""
        return self.start_addr + len(self.data)

    @property
    def size(self) -> int:
        return len(self.data)

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return (
            f"Segment(start=0x{self.start_addr:08X}, "
            f"end=0x{self.end_addr:08X}, size={self.size})"
        )


@dataclass
class ReprogrammingBlock:
    """One logical flash block (what the tool downloads as a unit)."""

    name: str = ""
    logical_index: int = 0
    file_name: str = ""
    file_type: str = "SREC"
    ident_value: str = ""
    addr_len: int = 4           # bytes used to encode an address in RequestDownload
    size_len: int = 4           # bytes used to encode a length in RequestDownload
    segments: List[Segment] = field(default_factory=list)

    @property
    def total_size(self) -> int:
        return sum(s.size for s in self.segments)

    @property
    def start_addr(self) -> Optional[int]:
        return min((s.start_addr for s in self.segments), default=None)

    @property
    def end_addr(self) -> Optional[int]:
        return max((s.end_addr for s in self.segments), default=None)


@dataclass
class Firmware:
    """A parsed firmware file: an ordered set of reprogramming blocks."""

    blocks: List[ReprogrammingBlock] = field(default_factory=list)
    entry_point: Optional[int] = None
    header: bytes = b""

    @property
    def segments(self) -> List[Segment]:
        out: List[Segment] = []
        for b in self.blocks:
            out.extend(b.segments)
        return out

    @property
    def total_size(self) -> int:
        return sum(b.total_size for b in self.blocks)


class SRecordError(ValueError):
    """Raised on a malformed or checksum-failing S-record line."""


# Number of bytes in the address field, keyed by record type.
_ADDR_BYTES = {
    "0": 2, "1": 2, "2": 3, "3": 4,
    "5": 2, "6": 3,
    "7": 4, "8": 3, "9": 2,
}
_DATA_TYPES = {"1", "2", "3"}
_TERM_TYPES = {"7", "8", "9"}


def parse_srecord(text: str, *, coalesce: bool = True) -> Firmware:
    """Parse Motorola S-record *text* into a :class:`Firmware`.

    One reprogramming block is produced containing the coalesced data
    segments. ``entry_point`` is taken from the S7/S8/S9 termination record.
    """
    header = b""
    entry: Optional[int] = None
    raw: List[Segment] = []

    for lineno, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        if not line.startswith("S"):
            raise SRecordError(f"line {lineno}: does not start with 'S': {line!r}")
        rtype = line[1]
        if rtype not in _ADDR_BYTES:
            raise SRecordError(f"line {lineno}: unknown record type S{rtype}")

        try:
            byte_count = int(line[2:4], 16)
            payload = bytes.fromhex(line[4:])
        except ValueError as exc:
            raise SRecordError(f"line {lineno}: bad hex ({exc})") from exc

        if len(payload) != byte_count:
            raise SRecordError(
                f"line {lineno}: byte count {byte_count} != {len(payload)} actual"
            )

        # Checksum: ones-complement of the sum of count+address+data bytes.
        chk_calc = (~(byte_count + sum(payload[:-1])) & 0xFF)
        if chk_calc != payload[-1]:
            raise SRecordError(
                f"line {lineno}: checksum 0x{payload[-1]:02X} != 0x{chk_calc:02X}"
            )

        addr_bytes = _ADDR_BYTES[rtype]
        addr = int.from_bytes(payload[:addr_bytes], "big")
        body = payload[addr_bytes:-1]  # strip address and trailing checksum

        if rtype == "0":
            header = body
        elif rtype in _DATA_TYPES:
            raw.append(Segment(addr, bytearray(body)))
        elif rtype in _TERM_TYPES:
            entry = addr
        # S5/S6 are record counts - validated implicitly, nothing to store.

    segments = _coalesce(raw) if coalesce else raw
    block = ReprogrammingBlock(name="SREC", segments=segments)
    return Firmware(blocks=[block], entry_point=entry, header=header)


def parse_srecord_file(path: str, **kwargs) -> Firmware:
    with open(path, "r", encoding="latin-1") as fh:
        return parse_srecord(fh.read(), **kwargs)


def _coalesce(segments: List[Segment]) -> List[Segment]:
    """Merge address-adjacent/overlapping segments into contiguous runs."""
    if not segments:
        return []
    ordered = sorted(segments, key=lambda s: s.start_addr)
    merged: List[Segment] = [Segment(ordered[0].start_addr, bytearray(ordered[0].data))]
    for seg in ordered[1:]:
        last = merged[-1]
        if seg.start_addr == last.end_addr:
            last.data.extend(seg.data)
        elif seg.start_addr < last.end_addr:
            # Overlap: extend only with the non-overlapping tail.
            overlap = last.end_addr - seg.start_addr
            if overlap < seg.size:
                last.data.extend(seg.data[overlap:])
        else:
            merged.append(Segment(seg.start_addr, bytearray(seg.data)))
    return merged
