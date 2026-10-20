"""CAN / CAN-FD transport for UDS using ISO-TP (ISO 15765-2).

This wraps :mod:`python-can` (bus access) and :mod:`can-isotp` (segmentation)
so the UDS client can run over CAN exactly as it does over DoIP. Both are
optional dependencies, imported lazily, so importing :mod:`dltool` never
requires CAN hardware or drivers.

Vendor hardware (the devices the original tool shipped drivers for) maps onto
python-can *interface* names:

    ZLG USBCANFD / PCIe-CANFD ... interface="zlgcan"
    PEAK PCAN ................... interface="pcan"
    Vector XL ................... interface="vector"
    Kvaser ...................... interface="kvaser"
    SocketCAN (Linux) ........... interface="socketcan"
    Virtual (no hardware) ....... interface="virtual"

See python-can's documentation for the per-interface ``channel`` / bitrate
arguments.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from .base import Transport, TransportError

log = logging.getLogger("dltool.can")


@dataclass
class CanIsoTpTransport(Transport):
    """UDS-over-CAN transport.

    :param tx_id: request (tester -> ECU) CAN identifier.
    :param rx_id: response (ECU -> tester) CAN identifier.
    :param interface: python-can interface name (see module docstring).
    :param channel: python-can channel (device/port dependent).
    :param extended_id: use 29-bit identifiers.
    :param fd: enable CAN-FD.
    :param bitrate: arbitration bitrate.
    :param data_bitrate: CAN-FD data-phase bitrate.
    :param bus_kwargs: extra keyword args forwarded to ``can.Bus``.
    :param tx_padding: ISO-TP padding byte (None disables padding).
    """

    tx_id: int
    rx_id: int
    interface: str = "virtual"
    channel: Any = 0
    extended_id: bool = False
    fd: bool = False
    bitrate: int = 500000
    data_bitrate: int = 2000000
    tx_padding: Optional[int] = 0x00
    bus_kwargs: Dict[str, Any] = field(default_factory=dict)

    _bus: Any = None
    _stack: Any = None
    _notifier: Any = None

    def open(self) -> None:
        try:
            import can  # type: ignore
            import isotp  # type: ignore
        except ImportError as exc:  # pragma: no cover - env dependent
            raise TransportError(
                "CAN support requires the optional dependencies. Install with:\n"
                "    pip install 'dltool[can]'\n"
                f"(import failed: {exc})"
            ) from exc

        kwargs = dict(self.bus_kwargs)
        kwargs.setdefault("bitrate", self.bitrate)
        if self.fd:
            kwargs.setdefault("fd", True)
            kwargs.setdefault("data_bitrate", self.data_bitrate)

        log.info("CAN bus up: interface=%s channel=%s fd=%s", self.interface, self.channel, self.fd)
        self._bus = can.Bus(interface=self.interface, channel=self.channel, **kwargs)

        addr = isotp.Address(
            isotp.AddressingMode.Normal_29bits if self.extended_id
            else isotp.AddressingMode.Normal_11bits,
            txid=self.tx_id,
            rxid=self.rx_id,
        )
        params = {
            "tx_padding": self.tx_padding,
            "blocksize": 0,
            "stmin": 0,
            "can_fd": self.fd,
        }
        if self.fd:
            params["tx_data_length"] = 64
            params["tx_data_min_length"] = 8
        # python-can Notifier drives the isotp stack from the bus.
        self._stack = isotp.NotifierBasedCanStack(self._bus, addr, params=params) \
            if hasattr(isotp, "NotifierBasedCanStack") else \
            isotp.CanStack(self._bus, address=addr, params=params)

    def close(self) -> None:
        try:
            if self._stack is not None and hasattr(self._stack, "stop"):
                self._stack.stop()
        finally:
            self._stack = None
            if self._bus is not None:
                self._bus.shutdown()
                self._bus = None

    def send(self, payload: bytes) -> None:
        if self._stack is None:
            raise TransportError("transport not open")
        self._stack.send(payload)

    def receive(self, timeout: float) -> bytes:
        import time
        if self._stack is None:
            raise TransportError("transport not open")
        deadline = time.monotonic() + timeout
        # NotifierBasedCanStack runs on its own thread; CanStack needs process().
        needs_process = hasattr(self._stack, "process")
        while time.monotonic() < deadline:
            if needs_process:
                self._stack.process()
            if self._stack.available():
                return bytes(self._stack.recv())
            time.sleep(0.005)
        return b""
