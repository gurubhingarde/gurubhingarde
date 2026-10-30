"""Native PCAN transport built directly on PEAK's PCANBasic.py (PCANBasic.dll),
with a self-contained ISO-TP (ISO 15765-2) layer for classic CAN and CAN-FD.

This bypasses python-can entirely — it talks to PCANBasic.dll exactly like the
supplier tool does, so it avoids the python-can PCAN backend quirks and gives
full control over framing, padding and FD timing.

Requires PEAK's PCANBasic.py on the import path (it is bundled in the package
directory). The PCAN driver (PCANBasic.dll) must be installed and match the
Python bitness.
"""
from __future__ import annotations

import time

from .base import Transport, TransportError

try:
    import PCANBasic as P
    _HAVE = True
except Exception:  # pragma: no cover - needs PEAK wrapper + DLL
    # PCANBasic.py is bundled in the package dir; add it to the path and retry.
    import os
    import sys
    _pkg = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if _pkg not in sys.path:
        sys.path.insert(0, _pkg)
    try:
        import PCANBasic as P
        _HAVE = True
    except Exception:
        _HAVE = False

# Channel name -> handle
_CHANNELS = {f"PCAN_USBBUS{i}": 0x50 + i if i <= 8 else 0x500 + i for i in range(1, 17)}
for _i in range(1, 9):
    _CHANNELS[f"PCAN_USBBUS{_i}"] = 0x50 + _i   # 0x51..0x58

# CAN-FD valid payload lengths
_FD_LENS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 16, 20, 24, 32, 48, 64]


def _len2dlc(n):
    for i, v in enumerate(_FD_LENS):
        if v >= n:
            return i, v
    return 15, 64


def _dlc2len(dlc):
    return _FD_LENS[dlc] if 0 <= dlc < len(_FD_LENS) else 0


def _round_fd(n):
    for v in _FD_LENS:
        if v >= n:
            return v
    return 64


def pcan_available():
    return _HAVE


def fd_bitrate_string(params: dict) -> bytes:
    """Build the PCAN InitializeFD bit-rate string from timing kwargs."""
    order = ["f_clock_mhz", "nom_brp", "nom_tseg1", "nom_tseg2", "nom_sjw",
             "data_brp", "data_tseg1", "data_tseg2", "data_sjw"]
    return (",".join(f"{k}={params[k]}" for k in order if k in params)).encode()


_BAUD = {1000000: 0x0014, 800000: 0x0016, 500000: 0x001C, 250000: 0x011C,
         125000: 0x031C, 100000: 0x432F, 50000: 0x472F, 20000: 0x532F, 10000: 0x672F}


class PcanNativeTransport(Transport):
    name = "PCAN native (PCANBasic.dll)"

    def __init__(self, channel="PCAN_USBBUS1", is_fd=True, bitrate=500000,
                 data_bitrate=2000000, req_id=0x18DA00F9, resp_id=0x18DAF900,
                 extended_id=True, min_size=8, padding=0xFF, st_min=0.0,
                 log=print):
        if not _HAVE:
            raise TransportError(
                "PCANBasic.py not importable. Put PEAK's PCANBasic.py on the path "
                "(it is bundled in the package) and install the PCAN driver.")
        self.channel_name = channel
        self.handle = _CHANNELS.get(channel, 0x51)
        self.is_fd = is_fd
        self.bitrate = bitrate
        self.data_bitrate = data_bitrate
        self.req_id = req_id
        self.resp_id = resp_id
        self.extended = extended_id
        self.min_size = min_size
        self.padding = padding & 0xFF
        self.st_min = st_min
        self.log = log
        self._api = None

    # -- lifecycle ----------------------------------------------------------
    def open(self):
        self._api = P.PCANBasic()
        if self.is_fd:
            from .can_isotp import pcan_fd_params
            brs = fd_bitrate_string(pcan_fd_params(self.bitrate, self.data_bitrate))
            self.log(f"[pcan] InitializeFD {self.channel_name} {brs.decode()}")
            st = self._api.InitializeFD(P.TPCANHandle(self.handle), P.TPCANBitrateFD(brs))
        else:
            baud = _BAUD.get(self.bitrate, 0x001C)
            self.log(f"[pcan] Initialize {self.channel_name} baud=0x{baud:04X}")
            st = self._api.Initialize(P.TPCANHandle(self.handle), P.TPCANBaudrate(baud))
        if st != P.PCAN_ERROR_OK:
            txt = self._err(st)
            self._api = None
            hint = ("Close PCAN-View / the supplier tool (channel busy), check the "
                    "channel name, or toggle CAN-FD.")
            if self.is_fd and st == getattr(P, "PCAN_ERROR_ILLOPERATION", 0x8000000):
                hint = ("FD init rejected. Your PCAN-USB may be a NON-FD model, or the "
                        "PCAN driver is too old. Untick CAN-FD to use classic 500k, "
                        "and run pcan_native_probe.py to check FD capability. If another "
                        "program owns the channel, close it first.")
            raise TransportError(f"PCAN init failed (0x{st:X}: {txt}). {hint}")

    def close(self):
        if self._api is not None:
            try:
                self._api.Uninitialize(P.TPCANHandle(self.handle))
            finally:
                self._api = None

    def _err(self, st):
        try:
            r, msg = self._api.GetErrorText(st, 0x09)
            return msg.decode(errors="replace") if r == P.PCAN_ERROR_OK else hex(st)
        except Exception:
            return hex(st)

    # -- raw frame layer ----------------------------------------------------
    def _msgtype(self):
        t = P.PCAN_MESSAGE_EXTENDED if self.extended else P.PCAN_MESSAGE_STANDARD
        if self.is_fd:
            t |= P.PCAN_MESSAGE_FD | P.PCAN_MESSAGE_BRS
        return t

    def send_frame(self, can_id: int, data: bytes):
        data = bytes(data)
        if self.is_fd:
            n = _round_fd(max(len(data), self.min_size))
            buf = data + bytes([self.padding]) * (n - len(data))
            dlc, _ = _len2dlc(n)
            msg = P.TPCANMsgFD()
            msg.ID = can_id
            msg.MSGTYPE = self._msgtype()
            msg.DLC = dlc
            for i in range(n):
                msg.DATA[i] = buf[i]
            st = self._api.WriteFD(P.TPCANHandle(self.handle), msg)
        else:
            buf = (data + bytes([self.padding]) * 8)[:8]
            msg = P.TPCANMsg()
            msg.ID = can_id
            msg.MSGTYPE = self._msgtype()
            msg.LEN = 8
            for i in range(8):
                msg.DATA[i] = buf[i]
            st = self._api.Write(P.TPCANHandle(self.handle), msg)
        if st != P.PCAN_ERROR_OK:
            raise TransportError(f"CAN write failed: {self._err(st)}")

    def recv_frame(self, timeout: float, accept=None):
        """Return (can_id, data bytes) for the next matching frame, or None."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.is_fd:
                st, msg, _ = self._api.ReadFD(P.TPCANHandle(self.handle))
            else:
                st, msg, _ = self._api.Read(P.TPCANHandle(self.handle))
            if st == P.PCAN_ERROR_OK:
                if getattr(msg, "MSGTYPE", 0) & P.PCAN_MESSAGE_STATUS:
                    continue
                n = _dlc2len(msg.DLC) if self.is_fd else msg.LEN
                data = bytes(msg.DATA[i] for i in range(n))
                cid = int(msg.ID)
                if accept is None or accept(cid):
                    return cid, data
            elif st & P.PCAN_ERROR_QRCVEMPTY:
                time.sleep(0.001)
            else:
                # transient bus errors: keep polling until timeout
                time.sleep(0.001)
        return None

    # -- ISO-TP -------------------------------------------------------------
    def send(self, payload: bytes):
        payload = bytes(payload)
        fs = 64 if self.is_fd else 8
        n = len(payload)
        if n <= 7:
            self.send_frame(self.req_id, bytes([n]) + payload)
            return
        if self.is_fd and n <= fs - 2:
            self.send_frame(self.req_id, bytes([0x00, n]) + payload)
            return
        self._send_multiframe(payload, fs)

    def _send_multiframe(self, payload: bytes, fs: int):
        n = len(payload)
        if n <= 0x0FFF:
            ff = bytes([0x10 | ((n >> 8) & 0x0F), n & 0xFF]) + payload[:fs - 2]
            off = fs - 2
        else:
            ff = bytes([0x10, 0x00]) + n.to_bytes(4, "big") + payload[:fs - 6]
            off = fs - 6
        self.send_frame(self.req_id, ff)
        bs, stmin = self._wait_fc()
        seq = 1
        sent_in_block = 0
        while off < n:
            self.send_frame(self.req_id, bytes([0x20 | (seq & 0x0F)]) + payload[off:off + fs - 1])
            off += fs - 1
            seq += 1
            sent_in_block += 1
            if stmin:
                time.sleep(stmin)
            elif self.st_min:
                time.sleep(self.st_min)
            if bs and sent_in_block >= bs and off < n:
                bs, stmin = self._wait_fc()
                sent_in_block = 0

    def _wait_fc(self, timeout=1.0):
        r = self.recv_frame(timeout, accept=lambda cid: cid == self.resp_id)
        if r is None:
            raise TransportError("ISO-TP: no Flow Control frame from ECU")
        data = r[1]
        if (data[0] & 0xF0) != 0x30:
            raise TransportError(f"ISO-TP: expected FC, got {data[:1].hex()}")
        fs = data[0] & 0x0F
        if fs == 1:                      # wait
            return self._wait_fc(timeout)
        if fs == 2:
            raise TransportError("ISO-TP: ECU flow-control overflow")
        bs = data[1] if len(data) > 1 else 0
        stmin_raw = data[2] if len(data) > 2 else 0
        stmin = (stmin_raw / 1000.0) if stmin_raw <= 0x7F else 0.0001
        return bs, stmin

    def recv(self, timeout: float = 2.0) -> bytes:
        r = self.recv_frame(timeout, accept=lambda cid: cid == self.resp_id)
        if r is None:
            raise TransportError(f"ISO-TP receive timeout ({timeout}s)")
        data = r[1]
        pci = data[0] >> 4
        if pci == 0x0:                   # single frame
            length = data[0] & 0x0F
            if length == 0:              # FD escape SF
                length = data[1]
                return data[2:2 + length]
            return data[1:1 + length]
        if pci == 0x1:                   # first frame -> multi-frame receive
            length = ((data[0] & 0x0F) << 8) | data[1]
            if length == 0:
                length = int.from_bytes(data[2:6], "big")
                buf = bytearray(data[6:])
            else:
                buf = bytearray(data[2:])
            # send Flow Control: CTS, BS=0 (all), STmin=0
            self.send_frame(self.req_id, bytes([0x30, 0x00, 0x00]))
            expected = 1
            while len(buf) < length:
                fr = self.recv_frame(timeout, accept=lambda cid: cid == self.resp_id)
                if fr is None:
                    raise TransportError("ISO-TP: timeout collecting consecutive frames")
                d = fr[1]
                if (d[0] & 0xF0) != 0x20:
                    continue
                buf += d[1:]
                expected = (expected + 1) & 0x0F
            return bytes(buf[:length])
        raise TransportError(f"ISO-TP: unexpected PCI 0x{data[0]:02X}")

    # -- autodetect ---------------------------------------------------------
    def raw_probe(self, probes, payload: bytes, listen: float = 0.3):
        """Send `payload` (ISO-TP single frame) to each (id, extended) in probes
        and collect responders. Returns list of (resp_id, extended, data)."""
        found = {}
        orig_ext = self.extended
        sf = bytes([len(payload)]) + payload
        for pid, ext in probes:
            self.extended = ext
            try:
                self.send_frame(pid, sf)
            except TransportError as e:
                self.log(f"[autodetect] send 0x{pid:X} failed: {e}")
                continue
            deadline = time.time() + listen
            while time.time() < deadline:
                r = self.recv_frame(max(0.0, deadline - time.time()),
                                    accept=lambda cid: cid != pid)
                if r is None:
                    break
                if r[0] not in found:
                    found[r[0]] = (r[0], ext, r[1])
                    self.log(f"[autodetect] <- 0x{r[0]:X} {r[1].hex(' ').upper()}")
        self.extended = orig_ext
        return list(found.values())
