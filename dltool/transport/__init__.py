"""Transport layer: a common interface over DoIP (Ethernet) and CAN/ISO-TP."""

from .base import Transport, TransportError

__all__ = ["Transport", "TransportError"]
