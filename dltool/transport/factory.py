"""Build a transport from a :class:`dltool.config.Config`."""

from __future__ import annotations

from ..config import Config
from .base import Transport
from .doip import DoIPTransport
from .can_isotp import CanIsoTpTransport


def build_transport(cfg: Config) -> Transport:
    """Create the transport selected by ``cfg.transport`` ("doip" or "can")."""
    if cfg.transport == "doip":
        if not cfg.doip_host:
            raise ValueError("doip_host is empty; run discovery or set the ECU IP")
        return DoIPTransport(
            host=cfg.doip_host,
            port=cfg.doip_port,
            source_addr=cfg.tester_addr,
            target_addr=cfg.ecu_addr,
            activation_type=cfg.doip_activation_type,
        )
    if cfg.transport == "can":
        channel = cfg.can_channel
        try:
            channel = int(str(channel), 0)
        except (TypeError, ValueError):
            pass
        return CanIsoTpTransport(
            tx_id=cfg.can_tx_id,
            rx_id=cfg.can_rx_id,
            interface=cfg.can_interface,
            channel=channel,
            extended_id=cfg.can_extended_id,
            fd=cfg.can_fd,
            bitrate=cfg.can_bitrate,
            data_bitrate=cfg.can_data_bitrate,
        )
    raise ValueError(f"unknown transport {cfg.transport!r}")
