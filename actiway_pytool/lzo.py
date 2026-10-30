"""LZO1X compression shim (original: SimmoTech.Utils.Compression.MiniLZO).

The original embeds a C# LZO1X port used when the 'LZO' option is set. Python
has no stdlib LZO; this wraps the optional `lzo` package if present and raises a
clear error otherwise, so the flash flow can fall back to uncompressed.
    pip install python-lzo
"""
from __future__ import annotations

try:
    import lzo as _lzo  # python-lzo
    _HAVE = True
except Exception:  # pragma: no cover
    _HAVE = False


def available() -> bool:
    return _HAVE


def compress(data: bytes) -> bytes:
    if not _HAVE:
        raise RuntimeError("python-lzo not installed: pip install python-lzo")
    # python-lzo's compress signature varies by version/build; try the richest
    # form first, then fall back. header=False = raw LZO1X stream.
    for args in ((data, 9, False), (data, 9), (data,)):
        try:
            return _lzo.compress(*args)
        except TypeError:
            continue
    return _lzo.compress(data)


def decompress(data: bytes, out_len: int) -> bytes:
    if not _HAVE:
        raise RuntimeError("python-lzo not installed: pip install python-lzo")
    return _lzo.decompress(data, False, out_len)
