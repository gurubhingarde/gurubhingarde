"""Hex / ASCII / byte conversion helpers.

Small, dependency-free utilities used across the transports and the
firmware parser. Equivalent in purpose to the conversion helpers found in
most diagnostic tools, written here from scratch.
"""

from __future__ import annotations

from typing import Iterable, Union

BytesLike = Union[bytes, bytearray, Iterable[int]]


def to_bytes(value: Union[str, BytesLike]) -> bytes:
    """Coerce a hex string (``"0x1A2B"`` / ``"1A 2B"``) or int iterable to bytes."""
    if isinstance(value, (bytes, bytearray)):
        return bytes(value)
    if isinstance(value, str):
        return hex_to_bytes(value)
    return bytes(value)


def hex_to_bytes(text: str) -> bytes:
    """Parse a loose hex string into bytes.

    Accepts ``0x`` prefixes, spaces, commas and dashes as separators.
    An odd number of nibbles is left-padded with a zero.
    """
    cleaned = (
        text.strip()
        .replace("0x", "")
        .replace("0X", "")
        .replace(" ", "")
        .replace(",", "")
        .replace("-", "")
        .replace("_", "")
        .replace(":", "")
    )
    if not cleaned:
        return b""
    if len(cleaned) % 2:
        cleaned = "0" + cleaned
    return bytes.fromhex(cleaned)


def bytes_to_hex(data: BytesLike, sep: str = " ", upper: bool = True) -> str:
    """Render bytes as a separated hex string, e.g. ``"1A 2B 3C"``."""
    data = bytes(data)
    out = sep.join(f"{b:02x}" for b in data)
    return out.upper() if upper else out


def to_ascii(data: BytesLike, printable_only: bool = True, placeholder: str = ".") -> str:
    """Decode bytes to ASCII, replacing non-printable bytes with ``placeholder``."""
    data = bytes(data)
    chars = []
    for b in data:
        if 0x20 <= b < 0x7F or not printable_only:
            chars.append(chr(b))
        else:
            chars.append(placeholder)
    return "".join(chars)


def from_ascii(text: str) -> bytes:
    """Encode an ASCII string to bytes (latin-1 so every value round-trips)."""
    return text.encode("latin-1", errors="replace")


def int_to_bytes(value: int, length: int, big_endian: bool = True) -> bytes:
    """Encode an unsigned integer into ``length`` bytes."""
    return value.to_bytes(length, "big" if big_endian else "little")


def bytes_to_int(data: BytesLike, big_endian: bool = True) -> int:
    """Decode bytes into an unsigned integer."""
    return int.from_bytes(bytes(data), "big" if big_endian else "little")


def parse_addr(value: Union[str, int]) -> int:
    """Parse an address/identifier given as int or hex/decimal string."""
    if isinstance(value, int):
        return value
    text = value.strip().lower()
    if text.startswith("0x"):
        return int(text, 16)
    # Diagnostic identifiers are conventionally hex even without 0x; but a
    # plain decimal is also accepted. Prefer hex when it contains a-f.
    try:
        return int(text, 10)
    except ValueError:
        return int(text, 16)
