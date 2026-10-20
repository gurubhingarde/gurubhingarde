"""Optional LZO compression for flash segments.

The original tool has an **LZO Compression** checkbox: when enabled, each flash
segment is LZO-compressed before TransferData and the RequestDownload
dataFormatIdentifier advertises the compression method so the ECU bootloader
decompresses on the fly.

LZO byte-compatibility matters (the ECU must decode exactly what we send), so
this uses the real LZO library via the optional ``python-lzo`` package rather
than a re-implementation. Install with ``pip install 'dltool[lzo]'``.

NOTE: the exact on-wire framing (LZO1X vs LZO1X-999, whether a length/stride
header precedes each block, and whether RequestDownload carries the compressed
or uncompressed size) is ECU-specific. Verify against a known-good transfer
before trusting it on hardware. ``compression_method`` and the size policy are
left configurable for that reason.
"""

from __future__ import annotations


def available() -> bool:
    try:
        import lzo  # noqa: F401
        return True
    except ImportError:
        return False


def lzo_compress(data: bytes, level: int = 9, header: bool = False) -> bytes:
    """LZO1X-compress ``data``.

    :param level: 1 = LZO1X-1 (fast), 9 = LZO1X-999 (best) — python-lzo maps
        its ``level`` argument the same way.
    :param header: include python-lzo's own 5-byte header. ECUs almost never
        expect it, so the default is ``False`` (raw LZO1X stream).
    """
    try:
        import lzo
    except ImportError as exc:  # pragma: no cover - env dependent
        raise RuntimeError(
            "LZO compression requires the optional dependency. Install with:\n"
            "    pip install 'dltool[lzo]'\n"
            f"(import failed: {exc})"
        ) from exc
    return lzo.compress(bytes(data), level, header)
