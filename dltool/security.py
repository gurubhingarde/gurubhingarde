"""SecurityAccess key computation.

ISO 14229 defines the SecurityAccess handshake (request seed -> compute key
-> send key) but leaves the *seed -> key* algorithm to the vehicle
manufacturer. This module provides a couple of common, generic algorithms and
a registry so you can plug in the one your ECU actually uses.

Register your own with :func:`register`, or pass a callable straight to
:meth:`dltool.uds.client.UdsClient.unlock`.
"""

from __future__ import annotations

from typing import Callable, Dict

KeyFn = Callable[[bytes], bytes]
_REGISTRY: Dict[str, KeyFn] = {}


def register(name: str, fn: KeyFn) -> None:
    _REGISTRY[name] = fn


def get(name: str) -> KeyFn:
    if name not in _REGISTRY:
        raise KeyError(f"unknown security algorithm {name!r}; known: {sorted(_REGISTRY)}")
    return _REGISTRY[name]


def available() -> list:
    return sorted(_REGISTRY)


def xor_key(secret: bytes) -> KeyFn:
    """key = seed XOR secret (secret repeated/truncated to seed length)."""
    def _fn(seed: bytes) -> bytes:
        if not secret:
            return seed
        rep = (secret * ((len(seed) // len(secret)) + 1))[: len(seed)]
        return bytes(a ^ b for a, b in zip(seed, rep))
    return _fn


def add_constant_key(constant: int, width: int = 4) -> KeyFn:
    """key = (seed_as_int + constant) mod 2**(8*width)."""
    def _fn(seed: bytes) -> bytes:
        val = (int.from_bytes(seed, "big") + constant) & ((1 << (8 * width)) - 1)
        return val.to_bytes(width, "big")
    return _fn


# Two illustrative defaults. Replace/extend for your ECU.
register("xor_ffff", xor_key(b"\xff\xff"))
register("passthrough", lambda seed: seed)
