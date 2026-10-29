"""In-process UDS ECU simulator.

Lets you exercise the entire flash workflow (session, security access, request
download, transfer data, transfer exit, reset, read-DID) with no hardware.
The seed->key check uses the same `crypto.seed_to_key_u16`, so a correctly
configured client unlocks it; a wrong SecKey is rejected, exactly like a real
ECU. This is the backend to use for "then I will test it".
"""
from __future__ import annotations

import os

from .base import Transport
from .. import crypto

NRC = {
    0x10: "generalReject", 0x11: "serviceNotSupported",
    0x22: "conditionsNotCorrect", 0x24: "requestSequenceError",
    0x31: "requestOutOfRange", 0x33: "securityAccessDenied",
    0x35: "invalidKey", 0x36: "exceedNumberOfAttempts",
    0x72: "generalProgrammingFailure", 0x7E: "subFunctionNotSupportedInActiveSession",
    0x7F: "serviceNotSupportedInActiveSession",
}


class SimulatorTransport(Transport):
    name = "Simulator (no hardware)"

    def __init__(self, sec_key: int = 0xFFFF, memory_size: int = 0, log=print,
                 ecu_addr: int = 0x01):
        self.sec_key = sec_key
        self.ecu_addr = ecu_addr
        self._log = log
        self.session = 0x01
        self.unlocked = False
        self._pending_seed = None
        self._dl_addr = None
        self._dl_remaining = 0
        self._block_seq = 0
        self.memory = bytearray()      # captured flashed bytes
        self.dids = {
            0xF180: b"BOOT_V1.0.27",
            0xF181: b"MON_V2.3",
            0xF182: b"CAL_V0.9",
            0xF190: b"VIN-SIMULATOR-0001",
        }

    # -- lifecycle ----------------------------------------------------------
    def open(self):
        self._log("[sim] ECU powered on, default session")

    def close(self):
        self._log("[sim] ECU offline")

    # -- messaging ----------------------------------------------------------
    def send(self, payload: bytes):
        self._req = bytes(payload)

    def recv(self, timeout: float = 2.0) -> bytes:
        return self._handle(self._req)

    # -- UDS server logic ---------------------------------------------------
    def _nrc(self, sid: int, code: int) -> bytes:
        self._log(f"[sim] NRC 0x{code:02X} ({NRC.get(code,'?')}) for SID 0x{sid:02X}")
        return bytes([0x7F, sid, code])

    def _ok(self, sid: int, *rest: int) -> bytes:
        return bytes([sid + 0x40, *rest])

    def _handle(self, req: bytes) -> bytes:
        if not req:
            return self._nrc(0x00, 0x10)
        sid = req[0]

        if sid == 0x10:  # DiagnosticSessionControl
            self.session = req[1] if len(req) > 1 else 0x01
            self._log(f"[sim] session -> 0x{self.session:02X}")
            return self._ok(sid, self.session, 0x00, 0x32, 0x01, 0xF4)

        if sid == 0x11:  # ECUReset
            self._log("[sim] ECU reset")
            self.unlocked = False
            self.session = 0x01
            return self._ok(sid, req[1] if len(req) > 1 else 0x01)

        if sid == 0x22:  # ReadDataByIdentifier
            did = int.from_bytes(req[1:3], "big")
            val = self.dids.get(did)
            if val is None:
                return self._nrc(sid, 0x31)
            return self._ok(sid, *req[1:3], *val)

        if sid == 0x27:  # SecurityAccess
            sub = req[1]
            if sub % 2 == 1:  # requestSeed
                self._pending_seed = os.urandom(2)
                self._log(f"[sim] seed = {self._pending_seed.hex().upper()}")
                return self._ok(sid, sub, *self._pending_seed)
            else:             # sendKey
                if self._pending_seed is None:
                    return self._nrc(sid, 0x24)
                expect = crypto.seed_to_key_bytes(self._pending_seed, self.sec_key, 2)
                got = req[2:4]
                if got == expect:
                    self.unlocked = True
                    self._log("[sim] UNLOCKED")
                    return self._ok(sid, sub)
                self._log(f"[sim] key {got.hex().upper()} != {expect.hex().upper()}")
                return self._nrc(sid, 0x35)

        if sid == 0x34:  # RequestDownload
            if not self.unlocked:
                return self._nrc(sid, 0x33)
            # fmt: ... dataFormatId, addrLenFmt, addr[], size[]
            alf = req[2]
            alen, slen = alf & 0x0F, (alf >> 4) & 0x0F
            self._dl_addr = int.from_bytes(req[3:3 + alen], "big")
            self._dl_remaining = int.from_bytes(req[3 + alen:3 + alen + slen], "big")
            self._block_seq = 1
            self._log(f"[sim] RequestDownload addr=0x{self._dl_addr:08X} "
                      f"size={self._dl_remaining}")
            # maxNumberOfBlockLength (2-byte length param)
            return self._ok(sid, 0x20, 0x04, 0x02)  # => 0x0402 = 1026 bytes

        if sid == 0x36:  # TransferData
            if self._dl_addr is None:
                return self._nrc(sid, 0x24)
            seq = req[1]
            if seq != (self._block_seq & 0xFF):
                return self._nrc(sid, 0x73 if False else 0x24)
            data = req[2:]
            self.memory += data
            self._dl_remaining -= len(data)
            self._block_seq += 1
            return self._ok(sid, seq)

        if sid == 0x37:  # RequestTransferExit
            self._log(f"[sim] TransferExit, captured {len(self.memory)} bytes")
            self._dl_addr = None
            return self._ok(sid)

        if sid == 0x31:  # RoutineControl (e.g. CRC / erase)
            return self._ok(sid, req[1], *req[2:4], 0x00)

        return self._nrc(sid, 0x11)
