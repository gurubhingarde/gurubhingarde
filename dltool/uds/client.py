"""Transport-agnostic UDS (ISO 14229) client.

The client speaks UDS *application PDUs* (a SID byte followed by service
data). It does not know whether those PDUs travel over DoIP or CAN/ISO-TP:
that is the job of a :class:`dltool.transport.base.Transport`, which this
client drives through :meth:`~dltool.transport.base.Transport.request`.

Response-pending (NRC 0x78) is handled transparently by waiting for the
final response.
"""

from __future__ import annotations

import logging
import time
from typing import Callable, List, Optional

from .services import (
    NEGATIVE_RESPONSE_SID,
    POSITIVE_RESPONSE_OFFSET,
    NRC,
    ResetType,
    RoutineControlType,
    ServiceId,
    Session,
    nrc_name,
)

log = logging.getLogger("dltool.uds")


class NegativeResponse(Exception):
    """Raised when the server returns a negative response (0x7F)."""

    def __init__(self, request_sid: int, nrc: int):
        self.request_sid = request_sid
        self.nrc = nrc
        super().__init__(
            f"Negative response to service 0x{request_sid:02X}: "
            f"{nrc_name(nrc)} (0x{nrc:02X})"
        )


class UdsClient:
    """A UDS client bound to a transport.

    :param transport: object exposing ``request(payload, timeout) -> bytes``.
    :param p2_timeout: default response timeout (seconds).
    :param p2_star_timeout: timeout used while the server keeps replying 0x78.
    """

    def __init__(self, transport, p2_timeout: float = 2.0, p2_star_timeout: float = 5.0):
        self.transport = transport
        self.p2_timeout = p2_timeout
        self.p2_star_timeout = p2_star_timeout

    # -- core request/response -------------------------------------------------
    def request(
        self,
        payload: bytes,
        *,
        timeout: Optional[float] = None,
        expect_response: bool = True,
    ) -> bytes:
        """Send a raw UDS request and return the raw positive response.

        Handles NRC 0x78 (responsePending) by continuing to read until a
        final response or timeout. Raises :class:`NegativeResponse` on 0x7F.
        """
        timeout = self.p2_timeout if timeout is None else timeout
        req_sid = payload[0]
        resp = self.transport.request(payload, timeout=timeout)
        if not expect_response:
            return b""

        deadline = time.monotonic() + self.p2_star_timeout
        while resp and resp[0] == NEGATIVE_RESPONSE_SID and len(resp) >= 3 and \
                resp[2] == NRC.REQUEST_CORRECTLY_RECEIVED_RESPONSE_PENDING:
            log.debug("0x78 response pending for service 0x%02X", req_sid)
            if time.monotonic() > deadline:
                raise NegativeResponse(req_sid, NRC.REQUEST_CORRECTLY_RECEIVED_RESPONSE_PENDING)
            resp = self.transport.receive(timeout=self.p2_star_timeout)

        if not resp:
            raise TimeoutError(f"no response to service 0x{req_sid:02X}")
        if resp[0] == NEGATIVE_RESPONSE_SID:
            nrc = resp[2] if len(resp) >= 3 else 0
            raise NegativeResponse(req_sid, nrc)
        if resp[0] != (req_sid + POSITIVE_RESPONSE_OFFSET):
            raise ValueError(
                f"unexpected response SID 0x{resp[0]:02X} to request 0x{req_sid:02X}"
            )
        return resp

    # -- services --------------------------------------------------------------
    def diagnostic_session_control(self, session: int = Session.EXTENDED) -> bytes:
        return self.request(bytes([ServiceId.DIAGNOSTIC_SESSION_CONTROL, session]))

    def ecu_reset(self, reset_type: int = ResetType.HARD) -> bytes:
        return self.request(bytes([ServiceId.ECU_RESET, reset_type]))

    def tester_present(self, suppress_response: bool = False) -> bytes:
        sub = 0x80 if suppress_response else 0x00
        return self.request(
            bytes([ServiceId.TESTER_PRESENT, sub]),
            expect_response=not suppress_response,
        )

    def read_data_by_identifier(self, did: int) -> bytes:
        """Return the record bytes for a Data Identifier (the DID echo stripped)."""
        resp = self.request(bytes([ServiceId.READ_DATA_BY_IDENTIFIER, did >> 8, did & 0xFF]))
        return resp[3:]

    def write_data_by_identifier(self, did: int, data: bytes) -> bytes:
        return self.request(
            bytes([ServiceId.WRITE_DATA_BY_IDENTIFIER, did >> 8, did & 0xFF]) + data
        )

    def security_access_request_seed(self, level: int) -> bytes:
        """Request a seed for an *odd* security level; returns the seed bytes."""
        resp = self.request(bytes([ServiceId.SECURITY_ACCESS, level]))
        return resp[2:]

    def security_access_send_key(self, level: int, key: bytes) -> bytes:
        """Send the computed key for the matching *even* level (seed level + 1)."""
        return self.request(bytes([ServiceId.SECURITY_ACCESS, level]) + key)

    def unlock(self, level: int, key_fn: Callable[[bytes], bytes]) -> bytes:
        """Full SecurityAccess handshake.

        ``level`` is the odd request-seed level; ``key_fn`` maps seed->key.
        The key is sent at ``level + 1``. If the seed is all zeroes the ECU is
        already unlocked and no key is sent.
        """
        seed = self.security_access_request_seed(level)
        if all(b == 0 for b in seed):
            log.info("security level 0x%02X already unlocked", level)
            return b""
        key = key_fn(seed)
        return self.security_access_send_key(level + 1, key)

    def routine_control(
        self,
        routine_id: int,
        control: int = RoutineControlType.START,
        data: bytes = b"",
    ) -> bytes:
        return self.request(
            bytes([ServiceId.ROUTINE_CONTROL, control, routine_id >> 8, routine_id & 0xFF])
            + data
        )

    def communication_control(self, control_type: int, communication_type: int = 0x01) -> bytes:
        return self.request(
            bytes([ServiceId.COMMUNICATION_CONTROL, control_type, communication_type])
        )

    def control_dtc_setting(self, setting_type: int) -> bytes:
        return self.request(bytes([ServiceId.CONTROL_DTC_SETTING, setting_type]))

    def clear_diagnostic_information(self, group: int = 0xFFFFFF) -> bytes:
        return self.request(
            bytes([ServiceId.CLEAR_DIAGNOSTIC_INFORMATION,
                   (group >> 16) & 0xFF, (group >> 8) & 0xFF, group & 0xFF])
        )

    # -- data transfer (flash) -------------------------------------------------
    def request_download(
        self,
        address: int,
        size: int,
        *,
        addr_len: int = 4,
        size_len: int = 4,
        data_format: int = 0x00,
    ) -> int:
        """RequestDownload (0x34). Returns the server's maxNumberOfBlockLength.

        ``data_format`` encodes compression (high nibble) and encryption
        (low nibble); 0x00 means neither.
        """
        alfid = (size_len << 4) | addr_len
        payload = (
            bytes([ServiceId.REQUEST_DOWNLOAD, data_format, alfid])
            + address.to_bytes(addr_len, "big")
            + size.to_bytes(size_len, "big")
        )
        resp = self.request(payload)
        # resp: SID(0x74) | lengthFormatIdentifier | maxNumberOfBlockLength...
        length_fmt = resp[1] >> 4
        max_block = int.from_bytes(resp[2:2 + length_fmt], "big")
        return max_block

    def transfer_data(self, block_counter: int, data: bytes) -> bytes:
        return self.request(
            bytes([ServiceId.TRANSFER_DATA, block_counter & 0xFF]) + data
        )

    def request_transfer_exit(self, data: bytes = b"") -> bytes:
        return self.request(bytes([ServiceId.REQUEST_TRANSFER_EXIT]) + data)

    # -- convenience -----------------------------------------------------------
    def read_identifiers(self, dids: List[int]) -> dict:
        """Read several DIDs, tolerating per-DID negative responses."""
        out = {}
        for did in dids:
            try:
                out[did] = self.read_data_by_identifier(did)
            except (NegativeResponse, TimeoutError, ValueError) as exc:
                out[did] = exc
        return out
