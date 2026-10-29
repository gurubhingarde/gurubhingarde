"""Cryptography and checksum primitives for the Actiway-style download tool.

All algorithms here were reconstructed from the original .NET assemblies
(CDownload.dll / Acita_CSG.AESHelper / Common.RSACryption). Where the original
IL did not fully reveal a constant (CRC polynomial, cipher mode, seed->key
mixing), the behaviour is parameterised and marked `CALIBRATE` so you can match
it bit-for-bit against a real ECU/firmware during testing.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass

try:
    # Optional: only needed for the AES helpers. The tool runs without it; the
    # GUI just disables AES features if PyCryptodome is absent.
    from Crypto.Cipher import AES  # type: ignore
    _HAVE_AES = True
except Exception:  # pragma: no cover - environment dependent
    _HAVE_AES = False


# ---------------------------------------------------------------------------
# AES-128  (original: ACTIA.clDownloadApp.jiaMi/JieMi, Acita_CSG.AESHelper)
# ---------------------------------------------------------------------------
# The original derives a 16-byte key from a UTF-8 passphrase, zero-padded /
# truncated to 16 bytes (new byte[16] + Math.Min + Array.Copy), zero IV.
DEFAULT_AES_PASSPHRASE = "actiacsg"  # hard-coded in the original binary


def _derive_key(passphrase: str) -> bytes:
    raw = passphrase.encode("utf-8")
    key = bytearray(16)
    key[: min(16, len(raw))] = raw[:16]
    return bytes(key)


@dataclass
class AesConfig:
    passphrase: str = DEFAULT_AES_PASSPHRASE
    mode: str = "CBC"          # CALIBRATE: original set Mode explicitly (CBC/ECB)
    iv: bytes = b"\x00" * 16    # zero IV (not explicitly set in original)


def aes_available() -> bool:
    return _HAVE_AES


def aes_encrypt(data: bytes, cfg: AesConfig = AesConfig()) -> bytes:
    if not _HAVE_AES:
        raise RuntimeError("PyCryptodome not installed: pip install pycryptodome")
    key = _derive_key(cfg.passphrase)
    data = _zero_pad(data, 16)
    if cfg.mode.upper() == "ECB":
        return AES.new(key, AES.MODE_ECB).encrypt(data)
    return AES.new(key, AES.MODE_CBC, cfg.iv).encrypt(data)


def aes_decrypt(data: bytes, cfg: AesConfig = AesConfig()) -> bytes:
    if not _HAVE_AES:
        raise RuntimeError("PyCryptodome not installed: pip install pycryptodome")
    key = _derive_key(cfg.passphrase)
    if cfg.mode.upper() == "ECB":
        return AES.new(key, AES.MODE_ECB).decrypt(data)
    return AES.new(key, AES.MODE_CBC, cfg.iv).decrypt(data)


def _zero_pad(data: bytes, block: int) -> bytes:
    rem = len(data) % block
    return data if rem == 0 else data + b"\x00" * (block - rem)


# ---------------------------------------------------------------------------
# SHA-256  (original: dltoolGUI.SHA256Helper)
# ---------------------------------------------------------------------------
def sha256_hex(data: bytes, upper: bool = False) -> str:
    h = hashlib.sha256(data).hexdigest()
    return h.upper() if upper else h


def sha256_text(text: str) -> str:
    return sha256_hex(text.encode("utf-8"), upper=False)


# ---------------------------------------------------------------------------
# CRC-32  (original: ACTIA.clDownloadApp.CRC_32 / GetCRC32Table)
# ---------------------------------------------------------------------------
# Standard reflected CRC-32 (zlib / Ethernet). The original builds its own 256
# entry table; the polynomial was not visible in the decoded anchors.
# CALIBRATE: adjust `poly`, `init`, `xorout`, `refin/refout` if your ECU uses a
# different variant (the GUI exposes these).
@dataclass
class Crc32Config:
    poly: int = 0xEDB88320
    init: int = 0xFFFFFFFF
    xorout: int = 0xFFFFFFFF
    refout: bool = True


def _crc32_table(poly: int) -> list[int]:
    table = []
    for i in range(256):
        c = i
        for _ in range(8):
            c = (c >> 1) ^ poly if (c & 1) else (c >> 1)
        table.append(c & 0xFFFFFFFF)
    return table


def crc32(data: bytes, cfg: Crc32Config = Crc32Config()) -> int:
    table = _crc32_table(cfg.poly)
    crc = cfg.init
    for b in data:
        crc = (crc >> 8) ^ table[(crc ^ b) & 0xFF]
    crc &= 0xFFFFFFFF
    if cfg.refout:
        crc ^= cfg.xorout
    return crc & 0xFFFFFFFF


def crc32_hex(data: bytes, cfg: Crc32Config = Crc32Config()) -> str:
    return f"{crc32(data, cfg):08X}"


# ---------------------------------------------------------------------------
# UDS SecurityAccess seed -> key
# (original: ACTIA.clDownloadApp.u16Main_eSecKey_Calcul, 16-bit, uses u16SecKey)
# ---------------------------------------------------------------------------
# The original is a short reversible 16-bit mix keyed by `sec_key` (config
# `SecKey`, default 0xFFFF) using 0x1F/0x0F shift/mask constants. The exact mix
# needs the full method body to be bit-exact; this is a plausible, configurable
# default. Override `seed_to_key` for your ECU.
def seed_to_key_u16(seed: int, sec_key: int = 0xFFFF) -> int:
    """Default 16-bit seed->key. CALIBRATE against the real ECU."""
    seed &= 0xFFFF
    sec_key &= 0xFFFF
    key = seed ^ sec_key
    # rotate-left by 5 within 16 bits, then mix (placeholder structure matching
    # the 0x1F / 0x0F constants seen in the original IL)
    key = ((key << 5) | (key >> 11)) & 0xFFFF
    key = (key + ((sec_key & 0x1F) << 8) + (sec_key & 0x0F)) & 0xFFFF
    return key


def seed_to_key_bytes(seed: bytes, sec_key: int = 0xFFFF, width: int = 2) -> bytes:
    """Generic adapter: treat the first `width` seed bytes as a big-endian int."""
    s = int.from_bytes(seed[:width], "big") if seed else 0
    k = seed_to_key_u16(s, sec_key)
    return k.to_bytes(width, "big")
