"""
============================================================
 GB/T 27930  —  Virtual BMS Validator  (JSW Greentech)
 Author : Guru / JSW Greentech SIDV Team
 Ref    : GB/T 27930-2015, J1939-21 (TPCM/TPDT)
 Log    : charge_with_switch_charger.asc (CAN4)
 DBC    : GBbyT_27930_Socket1_07Oct25.dbc
============================================================

HOW TO RUN
----------
  pip install python-can
  sudo modprobe vcan
  sudo ip link add dev vcan0 type vcan
  sudo ip link set up vcan0
  python3 gbt27930_bms_validator.py              # virtual CAN (no HW)
  python3 gbt27930_bms_validator.py --iface vcan0
  python3 gbt27930_bms_validator.py --iface can0 --bustype socketcan

ARCHITECTURE
------------
  Real Charger  <--CAN bus--> [Virtual BMS (this script)]
  OR
  [Charger Simulator (this script)] <--internal bus--> [Virtual BMS (this script)]

  The script can run in two modes:
  A) VALIDATE MODE  – Real charger on CAN hardware, BMS is simulated here
  B) DEMO MODE      – Both charger & BMS simulated internally (no HW needed)

============================================================
 CHANGE LOG (this revision)
============================================================
  1. BRO double-send fixed: _rx_CML no longer fires an immediate
     BRO=0x00 AND starts the periodic loop (which also sends BRO=0x00
     as its first action). The periodic loop's first iteration now
     serves as the initial send, eliminating the back-to-back
     duplicate frame observed in captured logs (~1ms apart instead
     of the spec'd ~250ms cadence).
  2. BSD/CSD ordering fixed per official GB/T 27930-2015 Appendix D
     (Table D.1): BSD's start condition is "Receive CST message" --
     NOT "receive CSD". CSD's start condition is "Receive BSD
     message" (i.e. the charger replies with CSD only after seeing
     our BSD). The previous code waited for CSD before ever sending
     BSD, which would deadlock against a real charger. BSD is now
     sent directly from _rx_CST (right after BST); _rx_CSD now only
     records the charger's session summary.
  3. decode_CCS() now also decodes the two fields the official CCS
     table (PGN 0x1200 / SPN 3081-3083, 3929) actually specifies but
     the original code silently dropped: cumulative charging time
     (1 min/bit) and the charging-permissible flag.
  4. j1939_id(): DP (data page) bit corrected from bit 25 to bit 24
     per SAE J1939-21 PDU layout (Priority[3] Reserved[1] DP[1]
     PF[8] PS[8] SA[8]). Every PGN actually used by GB/T 27930 has
     DP=0, so this was dormant/cosmetic -- fixed for correctness in
     case a Page-1 PGN is ever added.
  5. GUI _id_to_name(): added explicit BST/BSD matches so they no
     longer fall through to a generic "0x19"/"0x1C" display in the
     CAN Log tab.
============================================================
"""

import sys, time, threading, queue, struct, datetime, argparse, logging, enum, importlib
from collections import defaultdict

# ──────────────────────────────────────────────────────────
# Try tkinter (GUI mode) or fall back to text UI
# ──────────────────────────────────────────────────────────
try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext, font as tkfont
    HAS_TK = True
except ImportError:
    HAS_TK = False

# ──────────────────────────────────────────────────────────
# Try python-can (hardware CAN)
# ──────────────────────────────────────────────────────────
try:
    import can
    HAS_CAN = True
    CAN_IMPORT_ERROR = ""
except ImportError as e:
    HAS_CAN = False
    CAN_IMPORT_ERROR = str(e)

# ============================================================
# GB/T 27930  CAN ID constants (J1939 29-bit extended frames)
# Source Address: Charger=0x56  BMS=0xF4
# ============================================================
SA_CHARGER = 0x56
SA_BMS     = 0xF4

def j1939_id(pgn: int, sa: int, da: int = 0xFF, prio: int = 6) -> int:
    """Build 29-bit J1939 CAN ID.  PF<240 → PDU1 (DA in PS), PF>=240 → PDU2.
    Layout: Priority[3] Reserved[1] DP[1] PF[8] PS[8] SA[8] (SAE J1939-21).
    """
    pf = (pgn >> 8) & 0xFF
    if pf < 0xF0:               # PDU1 – peer-to-peer
        ps = da
        pgn_base = pgn & 0xFF00
    else:                       # PDU2 – broadcast
        ps = pgn & 0xFF
        pgn_base = pgn & 0xFF00
    dp = (pgn >> 16) & 0x01
    return (prio << 26) | (dp << 24) | (pgn_base << 8) | (ps << 8) | sa

# PGN definitions (GB/T 27930-2015 Table 1)
class PGN:
    CHM  = 0x0000  + (0x26 << 8)   # 0x2600  Charger Handshake
    BHM  = 0x0000  + (0x27 << 8)   # 0x2700  Battery Handshake
    _CHM  = 0x2600
    _BHM  = 0x2700
    _CRM  = 0x0100
    _BRM  = 0x0200
    _BCP  = 0x0600
    _CTS  = 0x0700
    _CML  = 0x0800
    _BRO  = 0x0900
    _CRO  = 0x0A00
    _BCL  = 0x1000
    _BCS  = 0x1100
    _CCS  = 0x1200
    _BSM  = 0x1300
    _BMV  = 0x1500
    _BMT  = 0x1600
    _BSP  = 0x1700
    _BST  = 0x1900
    _CST  = 0x1A00
    _BSD  = 0x1C00
    _CSD  = 0x1D00
    _BEM  = 0x1E00
    _CEM  = 0x1F00
    # J1939 Transport Protocol
    TPCM  = 0xEC00
    TPDT  = 0xEB00

# Pre-built CAN IDs used in real log (from DBC + log analysis)
class CID:
    """CAN IDs exactly matching the captured log (CAN4, SA=0x56 charger, SA=0xF4 BMS)"""
    CHM   = 0x1826F456   # Charger→BMS  Handshake
    BHM   = 0x182756F4   # BMS→Charger  Handshake
    CRM   = 0x18009856   # Charger→BMS  Recognition (recalc from DBC: 2550264918=0x982756=?)
    BRM   = 0x18009AF4   # BMS→Charger  Recognition (multi-packet)
    CTS   = 0x18009156   # Charger→BMS  Time Sync
    BCP   = 0x1809F4     # BMS→Charger  Parameters (multi-packet)
    CML   = 0x18009356   # Charger→BMS  Max Limits
    CRO   = 0x18009456   # Charger→BMS  Ready Output
    BRO   = 0x1809F4     # BMS→Charger  Ready Output
    BCS   = 0x18009604   # BMS→Charger  Charge Status
    BCL   = 0x18009704   # BMS→Charger  Charge Limits
    BSM   = 0x18009804   # BMS→Charger  Status Message
    CCS   = 0x18009956   # Charger→BMS  Charge Status
    BSD   = 0x18009A04   # BMS→Charger  Stop Details
    CST   = 0x18009B56   # Charger→BMS  Stop
    BST   = 0x18009C04   # BMS→Charger  Stop
    CSD   = 0x18009D56   # Charger→BMS  Stop Details
    # From actual DBC message IDs (decimal):
    # CRM1=2550264918=0x982756×something – let's use direct hex from DBC
    # DBC IDs are stored without the MSB extension bit
    # 2550264918 = 0x982756 = wait, 0x98 = PGN hi, 0x12 PGN lo, SA=0x56
    # Let's just hardcode from decoded log values
    TPCM_C2B = 0x1CECF456   # Charger→BMS TP.CM
    TPCM_B2C = 0x1CEC56F4   # BMS→Charger TP.CM
    TPDT_B2C = 0x1CEB56F4   # BMS→Charger TP.DT
    TPDT_C2B = 0x1CEBF456   # Charger(0x56)→BMS(0xF4) TP.DT
    # Actual periodic from log
    CCS_ACTUAL = 0x1C3FF456  # 0x1C3FF456 → CCS (charger charge status 250ms)
    BCS_ACTUAL = 0x181056F4  # 0x181056F4 → BCS
    CCS2_ACTUAL = 0x1812F456 # CCS secondary
    CHM_ACTUAL = 0x1826F456
    BHM_ACTUAL = 0x182756F4


class DEMO_CID:
    """GB/T 27930-2015 table-aligned CAN IDs used by the built-in demo charger and BMS."""
    SA_CHARGER = SA_CHARGER
    SA_BMS = SA_BMS
    CHM = j1939_id(PGN._CHM, SA_CHARGER, SA_BMS, prio=6)
    BHM = j1939_id(PGN._BHM, SA_BMS, SA_CHARGER, prio=6)
    CRM = j1939_id(PGN._CRM, SA_CHARGER, SA_BMS, prio=6)
    CTS = j1939_id(PGN._CTS, SA_CHARGER, SA_BMS, prio=6)
    CML = j1939_id(PGN._CML, SA_CHARGER, SA_BMS, prio=6)
    CRO = j1939_id(PGN._CRO, SA_CHARGER, SA_BMS, prio=4)
    CCS = j1939_id(PGN._CCS, SA_CHARGER, SA_BMS, prio=6)
    CST = j1939_id(PGN._CST, SA_CHARGER, SA_BMS, prio=4)
    CSD = j1939_id(PGN._CSD, SA_CHARGER, SA_BMS, prio=6)
    BRO = j1939_id(PGN._BRO, SA_BMS, SA_CHARGER, prio=4)
    BCL = j1939_id(PGN._BCL, SA_BMS, SA_CHARGER, prio=6)
    BCS = j1939_id(PGN._BCS, SA_BMS, SA_CHARGER, prio=7)
    BSM = j1939_id(PGN._BSM, SA_BMS, SA_CHARGER, prio=6)
    BST = j1939_id(PGN._BST, SA_BMS, SA_CHARGER, prio=4)
    BSD = j1939_id(PGN._BSD, SA_BMS, SA_CHARGER, prio=6)
    BEM = j1939_id(PGN._BEM, SA_BMS, SA_CHARGER, prio=2)      # BMS -> Charger error message
    CEM = j1939_id(PGN._CEM, SA_CHARGER, SA_BMS, prio=2)      # Charger -> BMS error message


class REAL_CID:
    """REAL_CID is an alias for SOCKET2_CID (SA_CHARGER=0x55, SA_BMS=0xF5).
    Populated after SOCKET2_CID is defined — see post-class assignment below.
    """
    pass


class SOCKET2_CID:
    """Socket 2 CAN IDs — SA_CHARGER=0x55, SA_BMS=0xF5 (real charger on CAN bus)."""
    SA_CHARGER = 0x55
    SA_BMS     = 0xF5
    # Charger→BMS (SA=0x55, DA=0xF5)
    CHM = 0x1826F555   # PGN 0x2600, prio 6
    CRM = 0x1801F555   # PGN 0x0100
    CTS = 0x1807F555   # PGN 0x0700
    CML = 0x1808F555   # PGN 0x0800
    CRO = 0x100AF555   # PGN 0x0A00, prio 4
    CCS = 0x1812F555   # PGN 0x1200
    CST = 0x101AF555   # PGN 0x1A00, prio 4
    CSD = 0x181DF555   # PGN 0x1D00
    CEM = 0x081FF555   # PGN 0x1F00
    # BMS→Charger (SA=0xF5, DA=0x55)
    BHM = 0x182755F5   # PGN 0x2700, prio 6
    BRM = 0x1C0255F5   # PGN 0x0200 (multi-packet)
    BCP = 0x1C0655F5   # PGN 0x0600 (multi-packet)
    BRO = 0x100955F5   # PGN 0x0900, prio 4
    BCL = 0x181055F5   # PGN 0x1000
    BCS = 0x1C1155F5   # PGN 0x1100
    BSM = 0x181355F5   # PGN 0x1300
    BST = 0x101955F5   # PGN 0x1900, prio 4
    BSD = 0x181C55F5   # PGN 0x1C00
    BEM = 0x081E55F5   # PGN 0x1E00


# REAL_CID is always the same as SOCKET2_CID
REAL_CID = SOCKET2_CID

PROFILE_OPTIONS = {
    'single_socket1': ('Single Gun - Socket 1', DEMO_CID),
    'single_socket2': ('Single Gun - Socket 2', SOCKET2_CID),
    'dual': ('Dual Gun', None),
}

# ============================================================
# GB/T 27930 Charge State Machine
# ============================================================
class ChargeState(enum.Enum):
    IDLE         = "IDLE"
    HANDSHAKE    = "HANDSHAKE"       # CHM / BHM
    RECOGNITION  = "RECOGNITION"     # CRM / BRM (TPCM/TPDT)
    PARAMETER    = "PARAMETER"       # CTS,BCP,CML
    READY        = "READY"           # CRO / BRO
    CHARGING     = "CHARGING"        # BCS,BCL,BSM / CCS
    STOPPING     = "STOPPING"        # BST / CST
    STOP_DONE    = "STOP_DONE"       # BSD / CSD
    ERROR        = "ERROR"

# ============================================================
# J1939 Transport Protocol (TPCM / TPDT)
# Per J1939-21 and GB/T 27930 multi-frame messages
# ============================================================
class J1939_TP:
    """Handles multi-packet TX/RX using TPCM (TP.CM) and TPDT (TP.DT)."""

    # TPCM Control Bytes
    CM_RTS = 0x10   # Request to Send
    CM_CTS = 0x11   # Clear to Send
    CM_EOM = 0x13   # End of Message Acknowledgement
    CM_BAM = 0x20   # Broadcast Announce Message
    CM_ABORT = 0xFF # Connection Abort
    CTS_WINDOW = 1
    ABORT_REASON_GENERIC = 250
    ABORT_REASON_BAD_SEQ = 7
    ABORT_REASON_UNEXPECTED_TPDT = 6

    def __init__(self, bus_tx_cb, sa: int, da: int, log_cb=None):
        self.bus_tx  = bus_tx_cb   # callback(can_id, data_bytes)
        self.sa      = sa
        self.da      = da
        self.log     = log_cb or (lambda *a: None)
        self._rx_buf: dict = {}    # pgn → {total, packets, data}
        self._tx_session: dict | None = None
        self.on_eom_cb = None      # optional callback(pgn) fired when EOM received for our TX session

    # ── TX side ──────────────────────────────────────────
    def send_bam(self, pgn: int, data: bytes):
        """BAM broadcast (used for BRM, BCP etc. → all nodes)."""
        n_bytes   = len(data)
        n_packets = (n_bytes + 6) // 7
        # TPCM BAM
        tpcm_id = self._build_id(PGN.TPCM, self.sa, 0xFF)
        tpcm_data = bytes([
            self.CM_BAM,
            n_bytes & 0xFF, (n_bytes >> 8) & 0xFF,
            n_packets,
            0xFF,
            pgn & 0xFF, (pgn >> 8) & 0xFF, (pgn >> 16) & 0xFF
        ])
        self.bus_tx(tpcm_id, tpcm_data)
        time.sleep(0.010)
        # TPDT packets
        for seq in range(1, n_packets + 1):
            chunk = data[(seq-1)*7 : seq*7]
            chunk = chunk.ljust(7, b'\xFF')
            tpdt_id   = self._build_id(PGN.TPDT, self.sa, 0xFF)
            self.bus_tx(tpdt_id, bytes([seq]) + chunk)
            time.sleep(0.010)

    def send_rts(self, pgn: int, data: bytes):
        """Peer-to-peer RTS/CTS handshake."""
        n_bytes   = len(data)
        n_packets = (n_bytes + 6) // 7
        self._tx_session = {
            'pgn': pgn,
            'data': bytes(data),
            'n_bytes': n_bytes,
            'n_pkt': n_packets,
            'last_seq_sent': 0,
        }
        tpcm_id = self._build_id(PGN.TPCM, self.sa, self.da)
        tpcm_data = bytes([
            self.CM_RTS,
            n_bytes & 0xFF, (n_bytes >> 8) & 0xFF,
            n_packets,
            self.CTS_WINDOW,
            pgn & 0xFF, (pgn >> 8) & 0xFF, (pgn >> 16) & 0xFF
        ])
        self.bus_tx(tpcm_id, tpcm_data)
        self.log(f"TP RTS sent PGN=0x{pgn:04X} n={n_packets} sz={n_bytes}; waiting for CTS")

    # ── RX side ──────────────────────────────────────────
    def on_tpcm(self, pgn_from_id: int, data: bytes) -> None:
        if len(data) < 8:
            self.log(f"TPCM RX short frame len={len(data)} data={data.hex(' ')}")
            return
        ctrl = data[0]
        total_bytes   = data[1] | (data[2] << 8)
        total_packets = data[3]
        pgn_target    = data[5] | (data[6] << 8) | (data[7] << 16)
        if ctrl in (self.CM_RTS, self.CM_BAM):
            self._rx_buf[pgn_target] = {
                'total': total_bytes,
                'n_pkt': total_packets,
                'pkts':  {},
                'mode': ctrl,
                'expected_seq': 1,
                # BAM: all packets allowed immediately; RTS: window set by first CTS we send
                'window_start': 1,
                'window_end': total_packets if ctrl == self.CM_BAM else min(total_packets, self.CTS_WINDOW),
                'next_cts_at': min(total_packets, self.CTS_WINDOW),
            }
            grant = min(total_packets, self.CTS_WINDOW)
            self.log(f"TPCM RX  ctrl={'BAM' if ctrl==0x20 else 'RTS'} "
                     f"PGN=0x{pgn_target:04X} n={total_packets} sz={total_bytes}")
            if ctrl == self.CM_RTS:
                self._send_cts(pgn_target, 1, grant)
        elif ctrl == self.CM_CTS:
            grant = data[1]
            next_seq = data[2]
            self.log(f"TPCM RX  ctrl=CTS PGN=0x{pgn_target:04X} grant={grant} next_seq={next_seq}")
            self._handle_cts(pgn_target, next_seq, grant)
        elif ctrl == self.CM_EOM:
            self.log(f"TPCM RX  ctrl=EOM PGN=0x{pgn_target:04X} complete")
            if self._tx_session and self._tx_session.get('pgn') == pgn_target:
                self._tx_session = None
                if callable(self.on_eom_cb):          # notify upper layer immediately
                    self.on_eom_cb(pgn_target)
        elif ctrl == self.CM_ABORT:
            self.log(f"TPCM RX  ctrl=ABORT PGN=0x{pgn_target:04X}")
            if self._tx_session and self._tx_session.get('pgn') == pgn_target:
                self._tx_session = None
                if callable(self.on_eom_cb):
                    self.on_eom_cb(pgn_target)

    def on_tpdt(self, data: bytes) -> tuple[int, bytes] | None:
        seq   = data[0]
        chunk = data[1:8]
        # find active rx session
        for pgn, rec in list(self._rx_buf.items()):
            if rec.get('mode') == self.CM_RTS:
                expected = rec.get('expected_seq', 1)
                win_start = rec.get('window_start', expected)
                win_end = rec.get('window_end', expected - 1)
                if seq < win_start or seq > win_end:
                    self.log(f"TPDT RX out-of-window PGN=0x{pgn:04X} seq={seq} allowed={win_start}..{win_end}; aborting")
                    self._send_abort(pgn, self.ABORT_REASON_UNEXPECTED_TPDT)
                    del self._rx_buf[pgn]
                    return None
                if seq != expected:
                    self.log(f"TPDT RX bad sequence PGN=0x{pgn:04X} seq={seq} expected={expected}; aborting")
                    self._send_abort(pgn, self.ABORT_REASON_BAD_SEQ)
                    del self._rx_buf[pgn]
                    return None
            rec['pkts'][seq] = chunk
            rec['expected_seq'] = seq + 1
            if len(rec['pkts']) == rec['n_pkt']:
                assembled = b''
                for i in range(1, rec['n_pkt'] + 1):
                    assembled += rec['pkts'].get(i, b'\xFF' * 7)
                assembled = assembled[:rec['total']]
                del self._rx_buf[pgn]
                self.log(f"TPDT assembled PGN=0x{pgn:04X} {assembled.hex(' ')}")
                if rec.get('mode') == self.CM_RTS:
                    self._send_eom(pgn, rec['total'], rec['n_pkt'])
                return pgn, assembled
            if rec.get('mode') == self.CM_RTS:
                contiguous = 0
                while (contiguous + 1) in rec['pkts']:
                    contiguous += 1
                if contiguous >= rec['next_cts_at'] and contiguous < rec['n_pkt']:
                    next_seq = contiguous + 1
                    grant = min(rec['n_pkt'] - contiguous, self.CTS_WINDOW)
                    rec['next_cts_at'] = contiguous + grant
                    self._send_cts(pgn, next_seq, grant)
        return None

    def _handle_cts(self, pgn: int, next_seq: int, grant: int):
        if not self._tx_session or self._tx_session.get('pgn') != pgn:
            return
        if grant == 0:
            self.log(f"CTS hold for PGN=0x{pgn:04X}")
            return
        start = max(1, next_seq)
        end = min(self._tx_session['n_pkt'], start + grant - 1)
        tpdt_id = self._build_id(PGN.TPDT, self.sa, self.da)
        for seq in range(start, end + 1):
            chunk = self._tx_session['data'][(seq - 1) * 7: seq * 7]
            chunk = chunk.ljust(7, b'\xFF')
            self.bus_tx(tpdt_id, bytes([seq]) + chunk)
            self._tx_session['last_seq_sent'] = seq
            time.sleep(0.005)
        if end >= self._tx_session['n_pkt']:
            self.log(f"TPDT window sent PGN=0x{pgn:04X} seq={start}..{end}; waiting for EOM")
        else:
            self.log(f"TPDT window sent PGN=0x{pgn:04X} seq={start}..{end}; waiting for next CTS")

    def _send_cts(self, pgn: int, next_seq: int, grant: int):
        rec = self._rx_buf.get(pgn)
        if rec is not None:
            rec['window_start'] = next_seq
            rec['window_end'] = next_seq + max(grant, 1) - 1
        cts_id = self._build_id(PGN.TPCM, self.sa, self.da)
        cts = bytes([
            self.CM_CTS,
            grant & 0xFF,
            next_seq & 0xFF,
            0xFF, 0xFF,
            pgn & 0xFF, (pgn >> 8) & 0xFF, (pgn >> 16) & 0xFF
        ])
        self.bus_tx(cts_id, cts)
        self.log(f"TPCM TX  ctrl=CTS PGN=0x{pgn:04X} grant={grant} next_seq={next_seq}")

    def _send_eom(self, pgn: int, total_bytes: int, total_packets: int):
        eom_id = self._build_id(PGN.TPCM, self.sa, self.da)
        eom = bytes([
            self.CM_EOM,
            total_bytes & 0xFF, (total_bytes >> 8) & 0xFF,
            total_packets & 0xFF,
            0xFF,
            pgn & 0xFF, (pgn >> 8) & 0xFF, (pgn >> 16) & 0xFF
        ])
        self.bus_tx(eom_id, eom)
        self.log(f"TPCM TX  ctrl=EOM PGN=0x{pgn:04X} n={total_packets} sz={total_bytes}")

    def _send_abort(self, pgn: int, reason: int):
        abort_id = self._build_id(PGN.TPCM, self.sa, self.da)
        abort = bytes([
            self.CM_ABORT,
            0xFF, 0xFF,
            0xFF,
            reason & 0xFF,
            pgn & 0xFF, (pgn >> 8) & 0xFF, (pgn >> 16) & 0xFF
        ])
        self.bus_tx(abort_id, abort)
        self.log(f"TPCM TX  ctrl=ABORT PGN=0x{pgn:04X} reason={reason}")

    def _build_id(self, pgn: int, sa: int, da: int, prio: int = 7) -> int:
        pf = (pgn >> 8) & 0xFF
        if pf < 0xF0:
            return (prio << 26) | (pgn << 8) | (da << 8) | sa
        else:
            return (prio << 26) | (pgn << 8) | sa


def pad_j1939(data: bytes, fill: int = 0xFF) -> bytes:
    """J1939 classical CAN frames use 8-byte payloads; pad unused bytes with 0xFF."""
    if len(data) >= 8:
        return data[:8]
    return data + bytes([fill] * (8 - len(data)))

# ============================================================
# Signal encoder / decoder (from DBC)
# ============================================================
def encode_signal(raw_data: bytearray, start_bit: int, length: int, value: float,
                  factor: float = 1.0, offset: float = 0.0):
    """Pack a signal into a bytearray (little-endian / Intel byte order)."""
    raw_val = int(round((value - offset) / factor))
    raw_val = max(0, min(raw_val, (1 << length) - 1))
    for i in range(length):
        bit_pos = start_bit + i
        byte_idx = bit_pos // 8
        bit_idx  = bit_pos %  8
        if byte_idx < len(raw_data):
            if raw_val & (1 << i):
                raw_data[byte_idx] |= (1 << bit_idx)
            else:
                raw_data[byte_idx] &= ~(1 << bit_idx)

def decode_signal(data: bytes, start_bit: int, length: int,
                  factor: float = 1.0, offset: float = 0.0) -> float:
    raw = 0
    for i in range(length):
        bit_pos  = start_bit + i
        byte_idx = bit_pos // 8
        bit_idx  = bit_pos %  8
        if byte_idx < len(data) and (data[byte_idx] >> bit_idx) & 1:
            raw |= (1 << i)
    return raw * factor + offset

# ============================================================
# Message Builders  (Virtual BMS  →  sends these)
# ============================================================
class BMSMessages:
    """Builds all BMS→Charger messages per GB/T 27930."""

    def __init__(self, params: dict):
        self.p = params   # BMS parameter dict

    def BHM(self) -> bytes:
        """BHM – Battery Handshake Message (2 bytes)"""
        d = bytearray(2)
        voltage = self.p.get('max_total_voltage', 700.0)  # V
        encode_signal(d, 0, 16, voltage, 0.1, 0.0)
        return bytes(d)

    def BRM(self) -> bytes:
        """BRM – Battery Recognition Message (49 bytes, multi-packet via TPCM/TPDT)"""
        d = bytearray(49)
        # Byte 0-5: Battery type, capacity, nominal voltage etc.
        d[0] = self.p.get('battery_type', 0x01)        # 01=LFP
        pack_cap = int(self.p.get('pack_capacity', 200.0) * 10)   # 0.1Ah
        d[1] = pack_cap & 0xFF
        d[2] = (pack_cap >> 8) & 0xFF
        nom_v = int(self.p.get('nominal_voltage', 560.0) * 10)
        d[3] = nom_v & 0xFF
        d[4] = (nom_v >> 8) & 0xFF
        d[5] = self.p.get('battery_vendor_id', 0x01)
        # BMS SW version (bytes 41-48)
        now = datetime.date.today()
        d[41] = now.year & 0xFF
        d[42] = (now.year >> 8) & 0xFF
        d[43] = now.month
        d[44] = now.day
        d[45] = 0x01   # serial
        return bytes(d)

    def BCP(self) -> bytes:
        """BCP – Battery Charge Parameters (13 bytes, multi-packet)"""
        d = bytearray(13)
        # MaxBattCellChargingVoltage  [0:16]  factor=0.01
        encode_signal(d,  0, 16, self.p.get('cell_max_v',     3.65),  0.01, 0.0)
        # MaxPermChargingCurrent      [16:32] factor=0.1 offset=-400
        encode_signal(d, 16, 16, self.p.get('max_charge_cur', 250.0), 0.1, -400.0)
        # TotalNominalEnergy          [32:48] factor=0.1
        encode_signal(d, 32, 16, self.p.get('nominal_energy', 112.0), 0.1, 0.0)
        # TotalMaxPermChargingVoltage [48:64] factor=0.1
        encode_signal(d, 48, 16, self.p.get('max_total_voltage', 700.0), 0.1, 0.0)
        # MaxPermTemperature          [64:72] factor=1 offset=-50
        encode_signal(d, 64,  8, self.p.get('max_temp', 45.0),         1.0, -50.0)
        # StatusOfCharge              [72:88] factor=0.1
        encode_signal(d, 72, 16, self.p.get('soc', 20.0),              0.1, 0.0)
        # CurrentBatteryVoltage       [88:104] factor=0.1
        encode_signal(d, 88, 16, self.p.get('pack_voltage', 560.0),    0.1, 0.0)
        return bytes(d)

    def BRO(self, ready: bool = True) -> bytes:
        """BRO – Battery Ready Output (1 byte)"""
        return bytes([0xAA if ready else 0x00])

    def BCL(self, v_demand: float, i_demand: float, mode: int = 1) -> bytes:
        """BCL – Battery Charge Limits (5 bytes): demand V, demand I, mode"""
        d = bytearray(5)
        encode_signal(d,  0, 16, v_demand, 0.1, 0.0)   # VoltageDemand
        encode_signal(d, 16, 16, i_demand, 0.1, -400.0) # CurrentDemand
        d[4] = mode    # 0=const-V, 1=const-I
        return bytes(d)

    def BCS(self, v_meas: float, i_meas: float, soc: float,
            t_remain: int, cell_max_v: float, cell_max_grp: int = 1) -> bytes:
        """BCS – Battery Charge Status (9 bytes)"""
        d = bytearray(9)
        encode_signal(d,  0, 16, v_meas,    0.1, 0.0)      # MeasuredChargingVoltage
        encode_signal(d, 16, 16, i_meas,    0.1, -400.0)   # MeasuredChargingCurrent
        encode_signal(d, 32, 12, cell_max_v, 0.01, 0.0)    # HighestVoltage
        encode_signal(d, 44,  4, cell_max_grp, 1.0, 0.0)   # GroupNr
        encode_signal(d, 48,  8, soc,        1.0, 0.0)     # CurrentSOC
        encode_signal(d, 56, 16, t_remain,   1.0, 0.0)     # EstRemaining min
        return bytes(d)

    def BSM(self, max_v: float, max_v_grp: int, max_t: float,
            min_v: float, min_v_grp: int, min_t: float,
            max_t_grp: int, flags: int = 0) -> bytes:
        """BSM – Battery Status Message (7 bytes)
        Byte 0-1: MaxSingleBatteryVoltage  factor=0.01 V
        Byte 2:   MaxSingleBatteryVoltageNo
        Byte 3-4: MinSingleBatteryVoltage  factor=0.01 V
        Byte 5:   MinSingleBatteryVoltageNo   ← was wrongly at d[4]
        Byte 6:   MaxTempProbeNo
        """
        d = bytearray(7)
        encode_signal(d,  0, 16, max_v,  0.01, 0.0)   # bits  0-15 → bytes 0-1
        d[2] = max_v_grp & 0xFF                         # byte 2
        encode_signal(d, 24, 16, min_v,  0.01, 0.0)   # bits 24-39 → bytes 3-4
        d[5] = min_v_grp & 0xFF                         # byte 5 (FIXED: was d[4])
        d[6] = max_t_grp & 0xFF                         # byte 6 (FIXED: was d[5])
        return bytes(d)

    def BST(self, reason: int = 0x00) -> bytes:
        """BST – Battery Stop Transmission (4 bytes)"""
        d = bytearray(4)
        d[0] = reason  # bit 0=SOC reached, bit2=fault etc.
        return bytes(d)

    def BSD(self, soc: float, min_v: float, max_v: float,
            min_t: float, max_t: float) -> bytes:
        """BSD – Battery Stop Data (7 bytes)"""
        d = bytearray(7)
        d[0] = int(soc)
        encode_signal(d,  8, 16, min_v, 0.01, 0.0)
        encode_signal(d, 24, 16, max_v, 0.01, 0.0)
        encode_signal(d, 40,  8, min_t, 1.0, -50.0)
        encode_signal(d, 48,  8, max_t, 1.0, -50.0)
        return bytes(d)

    def BEM(self, timeouts: dict = None) -> bytes:
        """BEM – Battery Error Message (4 bytes)"""
        d = bytearray(4)
        if timeouts:
            for bit, key in [(0, 'CRO_NotReady'), (2, 'CRO_Ready'),
                             (8, 'CTS_CML'), (10, 'CRO'), (16, 'CCS'),
                             (18, 'CST'), (24, 'CSD')]:
                if timeouts.get(key, 0):
                    encode_signal(d, bit, 2, timeouts[key], 1.0, 0.0)
        return bytes(d)

# ============================================================
# Message Decoders (Charger → BMS)
# ============================================================
class ChargerMessages:
    @staticmethod
    def decode_CHM(data: bytes) -> dict:
        if len(data) < 3: return {}
        return {'version': f"{data[0]}.{data[1]}.{data[2]}"}

    @staticmethod
    def decode_CRM(data: bytes) -> dict:
        if len(data) < 8: return {}
        result  = data[0]   # 0xAA=recognized, 0x00=not
        charger_num = int.from_bytes(data[1:5], 'little')
        location    = int.from_bytes(data[5:8], 'little')
        return {'recognized': result == 0xAA, 'charger_no': charger_num,
                'location': location}

    @staticmethod
    def decode_CTS(data: bytes) -> dict:
        if len(data) < 7: return {}
        return {
            'seconds':   data[0], 'minutes': data[1], 'hours': data[2],
            'day':       data[3], 'month':   data[4],
            'year':      data[5], 'century': data[6]
        }

    @staticmethod
    def decode_CML(data: bytes) -> dict:
        if len(data) < 8: return {}
        return {
            'max_v': decode_signal(data, 0,  16, 0.1),
            'min_v': decode_signal(data, 16, 16, 0.1),
            'max_i': decode_signal(data, 32, 16, 0.1, -400.0),
            'min_i': decode_signal(data, 48, 16, 0.1, -400.0),
        }

    @staticmethod
    def decode_CRO(data: bytes) -> dict:
        if len(data) < 1: return {}
        return {'ready': data[0] == 0xAA}

    @staticmethod
    def decode_CCS(data: bytes) -> dict:
        """CCS – Charger Charging Status (PGN 0x1200 / 4608).
        Per GB/T 27930-2015 Table 19 (SPN 3081-3083, 3929):
          bytes 0-1: voltage output value (0.1V/bit)
          bytes 2-3: current output value (0.1A/bit, -400A offset)
          bytes 4-5: cumulative charging time (1 min/bit, 0-600min)
          byte  6.1: charging permissible (2 bits: 00=suspend, 01=permit)
        The two time/permissible fields were previously decoded but
        discarded -- now returned so callers can react to a charger
        that asks the BMS to suspend.
        """
        if len(data) < 8: return {}
        charging_time_min = decode_signal(data, 32, 16, 1.0, 0.0)
        permissible_raw   = decode_signal(data, 48, 2, 1.0, 0.0)
        return {
            'voltage':          decode_signal(data,  0, 16, 0.1),
            'current':          decode_signal(data, 16, 16, 0.1, -400.0),
            'charging_time_min': charging_time_min,
            'charging_permissible': permissible_raw == 1,
        }

    @staticmethod
    def decode_CST(data: bytes) -> dict:
        if len(data) < 4: return {}
        return {'stop_reason': data[0], 'fault': data[2]}

    @staticmethod
    def decode_CSD(data: bytes) -> dict:
        if len(data) < 8: return {}
        time_min   = int.from_bytes(data[0:2], 'little')
        energy_kwh = decode_signal(data, 16, 16, 0.1)
        charger_no = int.from_bytes(data[4:8], 'little')
        return {'charging_time_min': time_min, 'energy_kwh': energy_kwh,
                'charger_no': charger_no}

# ============================================================
# Virtual Bus (internal, no hardware needed)
# ============================================================
class VirtualBus:
    """Zero-hardware internal CAN bus with subscriber pattern.

    send() is non-reentrant-safe by design: frames are queued and dispatched
    on a dedicated thread so that a subscriber responding to a frame (e.g. a
    charger sending CTS in response to an RTS) does not recursively re-enter
    other subscribers mid-delivery. Without this, dual-gun TP handshakes corrupt
    each other's J1939_TP state machines through deep synchronous call chains.
    """
    def __init__(self):
        self._subs: list = []
        self._log_q = queue.Queue()
        self._tx_q: queue.Queue = queue.Queue()
        self._dispatch_thread = threading.Thread(target=self._dispatch_loop, daemon=True)
        self._dispatch_thread.start()

    def _dispatch_loop(self):
        while True:
            can_id, data = self._tx_q.get()
            for cb in self._subs:
                try:
                    cb(can_id, bytes(data))
                except Exception:
                    pass

    def send(self, can_id: int, data: bytes, channel: str = "vbus"):
        msg = {'id': can_id, 'data': data, 'ts': time.time(), 'ch': channel}
        self._log_q.put(msg)
        self._tx_q.put((can_id, data))

    def log_frame(self, can_id: int, data: bytes, channel: str = "log-only", ts: float | None = None):
        """Record a frame for GUI/text monitoring without publishing it to subscribers."""
        self._log_q.put({'id': can_id, 'data': bytes(data), 'ts': ts or time.time(), 'ch': channel})

    def subscribe(self, cb):
        self._subs.append(cb)

    def get_log(self, timeout=0):
        try:
            return self._log_q.get(timeout=timeout)
        except queue.Empty:
            return None

# ============================================================
# Virtual BMS State Machine
# ============================================================
class VirtualBMS:
    """
    Simulates BMS communication side.
    Responds to Charger messages following GB/T 27930 handshake sequence.
    Uses J1939 TPCM/TPDT for multi-packet messages (BRM, BCP).
    """

    def __init__(self, bus_send, params: dict, log_cb=None, cid_profile=DEMO_CID):
        self.bus_send = bus_send
        self.params   = params
        self.log      = log_cb or print
        self.cid      = cid_profile
        self.sa_bms   = getattr(cid_profile, 'SA_BMS', SA_BMS)
        self.sa_chg   = getattr(cid_profile, 'SA_CHARGER', SA_CHARGER)
        self.state    = ChargeState.IDLE
        self.msgs     = BMSMessages(params)
        self.tp       = J1939_TP(self._tp_send, self.sa_bms, self.sa_chg, log_cb)

        # Timers / intervals
        self._bhm_timer  = None
        self._bcs_timer  = None
        self._bcl_timer  = None
        self._bsm_timer  = None
        self._chm_last   = 0
        self._lock       = threading.RLock()

        # Charge simulation state
        self.sim_soc         = params.get('soc', 20.0)
        self.sim_pack_v      = params.get('pack_voltage', 560.0)
        self.sim_current     = 0.0
        self.sim_cell_max_v  = params.get('cell_max_v_now', 3.30)
        self.sim_temp_max    = params.get('temp_max_now', 30.0)

        # Validation log
        self.violations: list[str] = []
        self.event_log:  list[str] = []

        # Received charger data
        self._cml = {}
        self._cro_ready = False
        self._ccs_data  = {}
        self._cst_data  = {}
        self._csd_data  = {}
        self._crm_data  = {}
        self._cts_data  = {}
        self._bro_running = False
        self._bro_thread = None
        self._bro_generation = 0
        self._bro_ready_sent = False
        self._cml_received = False
        self._brm_running = False
        self._brm_thread = None
        self._bcp_running = False
        self._bcp_thread = None
        self._bsd_sent = False   # guards against double-sending BSD
        self._bsm_started = False   # Table D.1: BSM must not send before first CCS
        self._bcp_started = False   # guards against starting BCP twice per session
        self._pending_timeouts: dict = {}   # key -> threading.Timer, for BEM watchdogs

    TP_PGNS = {
        'BRM': PGN._BRM,
        'BCP': PGN._BCP,
        'BCS': PGN._BCS,
        'BSD': PGN._BSD,
    }

    # ── TX helpers ────────────────────────────────────────
    def _send(self, can_id: int, data: bytes):
        self.bus_send(can_id, pad_j1939(data))

    def _tp_send(self, can_id: int, data: bytes):
        self.bus_send(can_id, data)

    def _send_app(self, label: str, can_id: int, data: bytes, pgn: int | None = None,
                  wait_for_eom: bool = False, timeout: float = 5.0):
        if len(data) <= 8:
            self._send(can_id, data)
            return
        tp_pgn = pgn if pgn is not None else self.TP_PGNS.get(label)
        if tp_pgn is None:
            self._violation(f"{label} is {len(data)} bytes but has no TP PGN mapping")
            return
        self.tp.send_rts(tp_pgn, data)
        if wait_for_eom:
            self._wait_for_tp_completion(tp_pgn, label, len(data), timeout=timeout)

    def _log(self, msg: str, level='INFO'):
        ts = f"{time.time():.3f}"
        entry = f"[{ts}] [BMS] [{level}] {msg}"
        self.event_log.append(entry)
        self.log(entry)

    def _violation(self, msg: str):
        ts = f"{time.time():.3f}"
        entry = f"[{ts}] ⚠ VIOLATION: {msg}"
        self.violations.append(entry)
        self.event_log.append(entry)
        self.log(entry)

    # ── BEM timeout watchdogs ─────────────────────────────
    # Arms/disarms a one-shot timer keyed by name; used to detect the
    # charger failing to respond within spec timeouts for CML/CRO/CSD,
    # matching the BEM bit fields already defined in BMSMessages.BEM().
    def _arm_timeout(self, key: str, seconds: float, callback):
        self._disarm_timeout(key)
        t = threading.Timer(seconds, callback)
        t.daemon = True
        self._pending_timeouts[key] = t
        t.start()

    def _disarm_timeout(self, key: str):
        t = self._pending_timeouts.pop(key, None)
        if t is not None:
            t.cancel()

    def _disarm_all_timeouts(self):
        for key in list(self._pending_timeouts.keys()):
            self._disarm_timeout(key)

    def _send_BEM(self, bem_field: str):
        """Send Battery Error Message flagging a timeout on `bem_field`
        (must be one of the keys BMSMessages.BEM() understands:
        CRO_NotReady, CRO_Ready, CTS_CML, CRO, CCS, CST, CSD)."""
        self._violation(f"BEM: no response within timeout, flagging {bem_field}")
        bem_cid = getattr(self.cid, 'BEM', None)
        if bem_cid is None:
            self._log(f"Cannot send BEM ({bem_field}) — this profile has no BEM CID", level='WARN')
            return
        self._log(f"Sending BEM ({bem_field}=1)")
        self._send(bem_cid, self.msgs.BEM({bem_field: 1}))

    def _rx_CEM(self, data: bytes):
        """CEM (PGN 0x1F00) -- charger has reported its own error and is
        aborting the session. Stop all BMS transmissions; do not attempt
        to continue the charge sequence."""
        self._violation("RX CEM: charger reported an error and is aborting the session")
        self._log(f"RX CEM data={data.hex(' ')}")
        self._disarm_all_timeouts()
        self._stop_periodic()
        self._stop_bhm_periodic()
        self._stop_brm_periodic()
        self._stop_bro_periodic()
        self.state = ChargeState.ERROR

    # ── Main RX dispatcher ───────────────────────────────
    def on_message(self, can_id: int, data: bytes):
        with self._lock:
            self._dispatch(can_id, data)

    def _dispatch(self, can_id: int, data: bytes):
        cid = can_id & 0x1FFFFFFF
        pf  = (cid >> 16) & 0xFF
        sa  = cid & 0xFF

        # Ignore looped-back frames that originated from this BMS instance.
        if sa == self.sa_bms:
            return

        # Transport Protocol — filter by destination address so dual-gun sessions
        # don't cross-contaminate each other's RTS/CTS handshakes.
        if pf == 0xEC:   # TPCM
            da = (cid >> 8) & 0xFF
            if da != self.sa_bms and da != 0xFF:
                return  # addressed to the other BMS instance; ignore
            self.tp.on_tpcm(cid, data)
            return
        if pf == 0xEB:   # TPDT
            if sa != self.sa_chg:
                return  # data packets from the other charger; ignore
            result = self.tp.on_tpdt(data)
            if result:
                pgn_inner, assembled = result
                self._on_assembled(pgn_inner, assembled, sa)
            return

        # ── Primary match: exact CAN ID from active cid_profile ──
        if cid == self.cid.CHM:
            self._rx_CHM(data, sa)
        elif cid == self.cid.CRM:
            self._rx_CRM(data, sa)
        elif cid == self.cid.CTS:
            self._rx_CTS(data)
        elif cid == self.cid.CML:
            self._rx_CML(data)
        elif cid == self.cid.CRO:
            self._rx_CRO(data)
        elif cid == self.cid.CCS:
            self._rx_CCS(data)
        elif cid == self.cid.CST:
            self._rx_CST(data)
        elif cid == self.cid.CSD:
            self._rx_CSD(data)
        elif cid == getattr(self.cid, 'CEM', None):
            self._rx_CEM(data)
        # ── Fallback: PF-based match works for any SA ──
        elif pf == 0x26 and sa == self.sa_chg:
            self._rx_CHM(data, sa)       # CHM (PGN 0x2600)
        elif pf == 0x01 and sa == self.sa_chg:
            self._rx_CRM(data, sa)       # CRM (PGN 0x0100)
        elif pf == 0x07 and sa == self.sa_chg:
            self._rx_CTS(data)           # CTS (PGN 0x0700)
        elif pf == 0x08 and sa == self.sa_chg:
            self._rx_CML(data)           # CML (PGN 0x0800)
        elif pf == 0x0A and sa == self.sa_chg:
            self._rx_CRO(data)           # CRO (PGN 0x0A00)
        elif pf == 0x12 and sa == self.sa_chg:
            self._rx_CCS(data)           # CCS (PGN 0x1200)
        elif pf == 0x1A and sa == self.sa_chg:
            self._rx_CST(data)           # CST (PGN 0x1A00)
        elif pf == 0x1D and sa == self.sa_chg:
            self._rx_CSD(data)           # CSD (PGN 0x1D00)
        elif pf == 0x1F and sa == self.sa_chg:
            self._rx_CEM(data)           # CEM (PGN 0x1F00) -- charger error message
        # ── Last resort for unknown charger SA ──
        elif sa not in (self.sa_bms,):
            pf8 = (cid >> 16) & 0xFF
            ps  = (cid >> 8) & 0xFF
            self._dispatch_charger(pf8, ps, data, cid)

    def _dispatch_charger(self, pf: int, ps: int, data: bytes, cid: int):
        """Last-resort router for unknown/unrecognised charger SA."""
        if pf == 0x26:
            self._rx_CHM(data, self.sa_chg)
            return
        msg = self._classify_charger_message(cid, data)
        if msg == 'CRM':
            self._rx_CRM(data, self.sa_chg)
        elif msg == 'CTS':
            self._rx_CTS(data)
        elif msg == 'CML':
            self._rx_CML(data)
        elif msg == 'CRO':
            self._rx_CRO(data)
        elif msg == 'CCS':
            self._rx_CCS(data)
        elif msg == 'CCS2':
            self._rx_CCS2(data)
        elif msg == 'CST':
            self._rx_CST(data)
        elif msg == 'CSD':
            self._rx_CSD(data)
        else:
            self._try_match_charger(cid, data)

    def _try_match_charger(self, cid: int, data: bytes):
        """Match charger messages by full 29-bit ID patterns from captured log."""
        # From log analysis - actual IDs seen on CAN4 from charger:
        m = cid & 0x1FFFFFFF
        if   m == self.cid.CHM: self._rx_CHM(data, self.sa_chg)
        elif m == self.cid.CRM: self._rx_CRM(data, self.sa_chg)
        elif m == self.cid.CTS: self._rx_CTS(data)
        elif m == self.cid.CML: self._rx_CML(data)
        elif m == self.cid.CRO: self._rx_CRO(data)
        elif m == self.cid.CCS: self._rx_CCS(data)
        elif m == self.cid.CST: self._rx_CST(data)
        elif m == self.cid.CSD: self._rx_CSD(data)
        elif (m & 0xFF) == self.sa_chg and ((m >> 16) & 0xFF) == 0x01:
            self._rx_CRM(data, self.sa_chg)
        elif (m & 0xFF) == self.sa_chg and ((m >> 16) & 0xFF) == 0x07:
            self._rx_CTS(data)

    def _classify_charger_message(self, cid: int, data: bytes) -> str | None:
        m = cid & 0x1FFFFFFF
        pf = (m >> 16) & 0xFF
        if m == self.cid.CCS or pf == 0x12:
            return 'CCS'
        if self._looks_like_cts(data) and self.state in {ChargeState.RECOGNITION, ChargeState.PARAMETER}:
            return 'CTS'
        if self._looks_like_crm(data) and self.state in {ChargeState.HANDSHAKE, ChargeState.RECOGNITION}:
            return 'CRM'
        if self._looks_like_cro(data) and self.state == ChargeState.READY:
            return 'CRO'
        if self.state == ChargeState.PARAMETER and len(data) >= 8:
            return 'CML'
        if self.state in {ChargeState.READY, ChargeState.CHARGING} and len(data) >= 4 and pf in (0x1D, 0x9B):
            return 'CST'
        if self.state == ChargeState.STOPPING and len(data) >= 8:
            return 'CSD'
        return None

    def _looks_like_crm(self, data: bytes) -> bool:
        return len(data) >= 8 and data[0] in (0x00, 0xAA)

    def _looks_like_cts(self, data: bytes) -> bool:
        return (
            len(data) >= 7 and
            0 <= data[0] < 60 and
            0 <= data[1] < 60 and
            0 <= data[2] < 24 and
            1 <= data[3] <= 31 and
            1 <= data[4] <= 12 and
            0 <= data[5] <= 99 and
            19 <= data[6] <= 21
        )

    def _looks_like_cro(self, data: bytes) -> bool:
        if not data:
            return False
        tail = data[1:]
        return data[0] in (0x00, 0xAA) and all(b in (0x00, 0xFF) for b in tail)

    def _on_assembled(self, pgn: int, data: bytes, sa: int):
        """Callback for fully assembled multi-packet messages."""
        self._log(f"TP assembled PGN=0x{pgn:04X} len={len(data)}")
        # CRM assembled
        if 0x98 <= pgn <= 0x9F:
            if pgn == 0x98: self._rx_CRM(data, sa)

    def _require_state(self, allowed_states, msg_name: str) -> bool:
        if self.state in allowed_states:
            return True
        allowed = ", ".join(state.value for state in allowed_states)
        self._violation(f"{msg_name} received in state {self.state.value}; expected one of: {allowed}")
        return False

    # ── Individual message handlers ───────────────────────
    def _rx_CHM(self, data: bytes, sa: int):
        if self.state == ChargeState.IDLE:
            self.state = ChargeState.HANDSHAKE
            self._log("RX CHM → starting handshake, starting periodic BHM")
            self._start_bhm_periodic()
        # Validate timing: CHM should repeat at 250ms
        now = time.time()
        if self._chm_last and (now - self._chm_last) > 0.3:
            self._violation(f"CHM interval {(now-self._chm_last)*1000:.0f}ms > 300ms (spec 250ms ±20%)")
        self._chm_last = now
        dec = ChargerMessages.decode_CHM(data)
        self._log(f"CHM ver={dec.get('version','?')}")

    def _start_bhm_periodic(self, period: float = 0.250):
        """BHM must be sent at 250ms throughout HANDSHAKE and RECOGNITION phases.
        Per GB/T 27930 the BMS keeps broadcasting BHM until the charger moves to
        PARAMETER phase (i.e. until CTS/CML arrives).
        """
        if getattr(self, '_bhm_running', False):
            return
        self._bhm_running = True
        def _loop():
            while self._bhm_running and self.state in {
                    ChargeState.HANDSHAKE, ChargeState.RECOGNITION}:
                self._send(self.cid.BHM, self.msgs.BHM())
                time.sleep(period)
            self._bhm_running = False
        t = threading.Thread(target=_loop, daemon=True)
        t.start()

    def _stop_bhm_periodic(self):
        self._bhm_running = False

    def _rx_CRM(self, data: bytes, sa: int):
        if not self._require_state({ChargeState.HANDSHAKE, ChargeState.RECOGNITION}, "CRM"):
            return
        self._crm_data = ChargerMessages.decode_CRM(data)
        ack = data[0] if data else 0xFF
        self._log(f"RX CRM ack=0x{ack:02X} charger#={self._crm_data.get('charger_no',0)}")
        self.state = ChargeState.RECOGNITION
        # Spec Table D.1: BHM stops when any CRM is received
        self._stop_bhm_periodic()
        if ack == 0x00:
            self._log("CRM=0x00: pre-recognition, starting/continuing BRM loop")
            if not self._brm_running:
                self._start_brm_periodic()
            return
        if ack == 0xAA:
            # Guard: CRM=AA repeats every 250ms — only start BCP once per session
            if getattr(self, '_bcp_started', False):
                return
            self._bcp_started = True
            self._log("CRM=0xAA: recognition complete — stopping BRM, starting BCP")
            self._stop_brm_periodic()
            self._bcp_running = False
            self._bro_ready_sent = False
            def _start_bcp_after_brm():
                deadline = time.time() + 2.0
                while time.time() < deadline:
                    if not self.tp._tx_session:
                        break
                    time.sleep(0.010)
                self._log("BRM cleared — starting BCP")
                threading.Thread(target=self._send_BCP, daemon=True).start()
            threading.Thread(target=_start_bcp_after_brm, daemon=True).start()
            return
        self._violation(f"Unexpected CRM acknowledgement 0x{ack:02X}")

    def _send_BRM(self):
        """Send BRM via RTS/CTS then WAIT for EOM before returning.
        On real 250kbps CAN each DT packet takes ~157ms so a full 7-packet
        transfer takes ~1.1s.  We must not fire a new RTS while the previous
        transfer is still in progress — the charger would abort.
        """
        brm_pgn    = PGN._BRM
        brm_data   = self.msgs.BRM()
        brm_can_id = j1939_id(PGN._BRM, self.sa_bms, self.sa_chg, prio=6)
        self._send_app("BRM", brm_can_id, brm_data, pgn=brm_pgn, wait_for_eom=True)

    def _on_brm_eom(self, pgn: int):
        """Called by TP layer when charger ACKs our BRM with EOM.
        The charger requires at least 2 complete BRM transfers before it
        sends CRM=0xAA. We keep the loop running — it stops only when
        CRM=0xAA is received (in _rx_CRM). The 500ms inter-transfer gap
        gives the charger time to process BRM data before the next RTS.
        """
        if pgn == PGN._BRM:
            self._log("EOM received for BRM — loop continues until CRM=0xAA")

    def _start_brm_periodic(self, period: float = 0.250):
        self._stop_brm_periodic()
        self._brm_running = True
        # Register EOM callback for logging only — loop stops only when CRM=0xAA received
        self.tp.on_eom_cb = self._on_brm_eom

        def _loop():
            while self._brm_running and self.state in {ChargeState.RECOGNITION, ChargeState.PARAMETER}:
                self._send_BRM()   # blocks until EOM or timeout
                if not self._brm_running:
                    break          # CRM=0xAA arrived during send → stop
                # Wait 500ms after EOM before next RTS.
                # Real charger (0x0521 state 0x84) needs ~154ms to exit EOM-wait,
                # then additional time to update state machine.
                # 500ms gives reliable margin on 250kbps CAN.
                time.sleep(0.500)

        self._brm_thread = threading.Thread(target=_loop, daemon=True)
        self._brm_thread.start()

    def _stop_brm_periodic(self):
        self._brm_running = False
        # Clear EOM callback when BRM phase ends
        if hasattr(self, 'tp') and self.tp.on_eom_cb is self._on_brm_eom:
            self.tp.on_eom_cb = None

    def _rx_CTS(self, data: bytes):
        if not self._require_state({ChargeState.RECOGNITION, ChargeState.PARAMETER}, "CTS"):
            return
        # CTS is time-sync from charger — sent AFTER charger receives BCP.
        # BCP was already started by CRM=0xAA handler (spec Table D.1).
        # Just update state and log.
        self._stop_brm_periodic()   # belt-and-suspenders
        self.state = ChargeState.PARAMETER
        self._cts_data = ChargerMessages.decode_CTS(data)
        self._log(f"RX CTS (time sync from charger) — BCP already running")

    def _send_BCP(self):
        """Send BCP once via RTS/CTS then wait for EOM.
        Table D.1: BRO starts on CML receipt — NOT on BCP completion.
        _rx_CML handles BRO start. _send_BCP just transfers data.
        """
        self._bcp_running = True
        bcp_pgn    = PGN._BCP
        bcp_can_id = j1939_id(PGN._BCP, self.sa_bms, self.sa_chg, prio=6)
        bcp_data   = self.msgs.BCP()
        self._log("Sending BCP (single-shot RTS/CTS)")
        self._send_app("BCP", bcp_can_id, bcp_data, pgn=bcp_pgn, wait_for_eom=True)
        self._bcp_running = False
        self._log("BCP complete — waiting for CML to trigger BRO")
        # Table D.1 / BEM: arm a watchdog for the charger's CML response.
        self._arm_timeout('cml', 5.0, lambda: self._send_BEM('CTS_CML'))

    def _start_bcp_periodic(self, period: float = 0.500):
        pass   # BCP is driven by _send_BCP loop

    def _stop_bcp_periodic(self):
        self._bcp_running = False

    def _wait_for_tp_completion(self, pgn: int, label: str, size: int, timeout: float = 10.0):
        deadline = time.time() + timeout
        while time.time() < deadline:
            session = self.tp._tx_session
            if not session or session.get('pgn') != pgn:
                self._log(f"{label} sent ({size} bytes via TP with EOM ACK)")
                return
            # Allow BCP loop to be interrupted by CML (_bcp_running=False)
            if label == "BCP" and not self._bcp_running:
                self._log("BCP interrupted by CML during TP transfer")
                return
            # Allow BRM loop to be interrupted by stop signal
            if label == "BRM" and not self._brm_running:
                return
            time.sleep(0.01)
        self._violation(f"{label} TP transfer timed out waiting for EOM ACK")

    def _rx_CML(self, data: bytes):
        if not self._require_state(
                {ChargeState.PARAMETER, ChargeState.RECOGNITION}, "CML"):
            return
        self._disarm_timeout('cml')
        # Advance to PARAMETER if still in RECOGNITION (CML can arrive before CTS)
        self.state = ChargeState.PARAMETER
        self._stop_brm_periodic()   # ensure BRM stopped (may still be looping)
        self._stop_bcp_periodic()   # signal BCP loop to stop after current transfer
        self._cml = ChargerMessages.decode_CML(data)
        self._cml_received = True
        self._log(f"RX CML max_v={self._cml.get('max_v',0):.1f}V "
                  f"max_i={self._cml.get('max_i',0):.1f}A "
                  f"min_i={self._cml.get('min_i',0):.1f}A")
        # Validate: BMS requested max_v should not exceed CML max_v
        bms_max_v = self.params.get('max_total_voltage', 700.0)
        charger_max_v = self._cml.get('max_v', 9999)
        if bms_max_v > charger_max_v:
            self._violation(f"BCP max_v={bms_max_v}V > CML max_v={charger_max_v}V")
        # Table D.1: BRO starts on CML receipt.
        # FIX: previously this sent BRO=00 immediately *and* started the
        # periodic loop (whose first iteration also sends BRO=00),
        # producing two BRO=0x00 frames ~1ms apart instead of the correct
        # ~250ms cadence. The periodic loop's first iteration is the
        # initial send -- do not send here as well.
        if self._bro_ready_sent or self._bro_running:
            return
        self._start_bro_periodic(ready=False, period=0.250)

    def _send_BRO(self, ready: bool):
        self._bro_ready_sent = bool(ready)
        self._log(f"Sending BRO ready={ready}")
        self._send(self.cid.BRO, self.msgs.BRO(ready))

    def _start_bro_periodic(self, ready: bool = False, period: float = 0.250,
                             unready_count: int = 5):
        """BRO periodic loop.
        ready=False : send BRO=0x00 for unready_count samples (5 × 250ms = 1.25s),
                      then automatically switch to BRO=0xAA.
        ready=True  : send BRO=0xAA immediately and keep sending.
        """
        self._stop_bro_periodic()
        self._bro_generation += 1
        generation = self._bro_generation
        self._bro_running = True

        def _loop():
            if not ready:
                self._log(f"BRO: sending 0x00 for {unready_count} samples then 0xAA")
                for _ in range(unready_count):
                    if not self._bro_running or generation != self._bro_generation:
                        return
                    self._send_BRO(False)
                    time.sleep(period)
                self._log("BRO: switching to 0xAA")
                # Spec §10.2.5: if charger not ready within 60s of BRO=AA,
                # BMS should react per Appendix C.1 -- flag via BEM.
                self._arm_timeout('cro', 60.0, lambda: self._send_BEM('CRO'))
            # BRO=AA continuously until stopped
            while self._bro_running and generation == self._bro_generation:
                self._send_BRO(True)
                time.sleep(period)

        self._bro_thread = threading.Thread(target=_loop, daemon=True)
        self._bro_thread.start()

    def _stop_bro_periodic(self):
        self._bro_running = False
        self._bro_generation += 1

    def _rx_CRO(self, data: bytes):
        if not self._require_state({ChargeState.PARAMETER, ChargeState.READY}, "CRO"):
            return
        info = ChargerMessages.decode_CRO(data)
        self._cro_ready = info.get('ready', False)
        self._log(f"RX CRO ready={self._cro_ready}")
        if not self._cro_ready:
            # CRO=00: charger acknowledged BRO=00.
            # BRO loop (started in _rx_CML) sends 5×BRO=00 then auto-flips to BRO=AA.
            # Nothing to do here except update state.
            self._log("CRO=00 received — BRO loop handles 5×00 then AA automatically")
            self.state = ChargeState.READY
            return
        self._disarm_timeout('cro')
        self._stop_bro_periodic()
        self.state = ChargeState.CHARGING
        self._log("CHARGING STARTED -> periodic BCL/BCS/BSM")
        self._start_periodic()

    def _rx_CCS(self, data: bytes):
        if self.state != ChargeState.CHARGING:
            return
        self._ccs_data = ChargerMessages.decode_CCS(data)
        v = self._ccs_data.get('voltage', 0)
        i = self._ccs_data.get('current', 0)
        permissible = self._ccs_data.get('charging_permissible', True)
        self._log(f"RX CCS V={v:.1f} I={i:.1f}A permissible={permissible}")
        if not permissible:
            self._violation("CCS charging_permissible=0 (charger requests suspend)")
        # Table D.1: BSM starts on first CCS message
        if not getattr(self, '_bsm_started', False):
            self._bsm_started = True
            self._log("First CCS received — BSM transmission enabled (Table D.1)")
        # Update simulated pack state.
        # Charging current is negative by convention (current flowing INTO
        # the battery); only a negative reading should count as charge
        # accumulation. Using `i` directly here made SOC/pack_v *drop*
        # during a negative-current (i.e. actually-charging) session --
        # use the charge magnitude instead so charging always increases
        # both, and a stray non-negative reading contributes nothing.
        self.sim_current = i
        dt = 0.25
        charge_i = max(0.0, -i)   # magnitude of charging current, 0 if not charging
        self.sim_pack_v += charge_i * 0.001 * dt
        self.sim_soc    += (charge_i * dt) / (3600 * self.params.get('pack_capacity', 200)) * 100

    def _rx_CCS2(self, data: bytes):
        """CCS secondary (CCS2 0x1812F456 in log)"""
        pass

    def _rx_CST(self, data: bytes):
        if not self._require_state({ChargeState.CHARGING, ChargeState.READY}, "CST"):
            return
        self._cst_data = ChargerMessages.decode_CST(data)
        reason = self._cst_data.get('stop_reason', 0)
        self._log(f"RX CST stop_reason=0x{reason:02X}")
        self.state = ChargeState.STOPPING
        self._stop_periodic()
        # Table D.1: BST starts on CST/self-initiated-stop; BSD's own start
        # condition is "receive CST message" (NOT "receive CSD" -- CSD's
        # start condition is "receive BSD message", i.e. the charger only
        # replies with CSD after seeing our BSD). Previously BSD only fired
        # from _rx_CSD, which would deadlock waiting for a CSD the charger
        # is itself waiting on us to trigger. Send both here, in order.
        self._send_BST()
        self._send_BSD()

    def _send_BST(self, reason: int = 0x01):
        self._log("Sending BST")
        self._send(self.cid.BST, self.msgs.BST(reason))

    def _rx_CSD(self, data: bytes):
        if not self._require_state({ChargeState.STOPPING}, "CSD"):
            return
        self._disarm_timeout('csd')
        self._csd_data = ChargerMessages.decode_CSD(data)
        self._log(f"RX CSD time={self._csd_data.get('charging_time_min',0)}min "
                  f"energy={self._csd_data.get('energy_kwh',0):.2f}kWh")
        self.state = ChargeState.STOP_DONE
        # BSD was already sent from _rx_CST per Table D.1 (BSD start
        # condition = "receive CST"). CSD is the charger's own summary
        # reply and needs no further response from the BMS.
        if not self._bsd_sent:
            # Defensive fallback: if CST was somehow missed (e.g. this
            # BMS attached mid-session) but CSD still arrived, send BSD
            # now rather than leaving the charger without one at all.
            self._log("BSD not yet sent (CST may have been missed) — sending now as fallback")
            self._send_BSD()

    def _send_BSD(self):
        if self._bsd_sent:
            return
        self._bsd_sent = True
        self._log("Sending BSD")
        d = self.msgs.BSD(
            soc=self.sim_soc,
            min_v=self.sim_cell_max_v - 0.3,
            max_v=self.sim_cell_max_v,
            min_t=self.sim_temp_max - 5,
            max_t=self.sim_temp_max
        )
        self._send_app("BSD", self.cid.BSD, d)
        # CSD's own start condition is "receive BSD message" -- watch for it.
        self._arm_timeout('csd', 5.0, lambda: self._send_BEM('CSD'))

    # ── Periodic charging messages (BCL, BCS, BSM) ───────
    def _start_periodic(self):
        self._running = True
        self._periodic_thread = threading.Thread(target=self._periodic_loop, daemon=True)
        self._periodic_thread.start()

    def _stop_periodic(self):
        self._running = False

    def _periodic_loop(self):
        """BCL @ 50ms, BCS @ 250ms, BSM @ 250ms — per verified working log."""
        last_bcs = last_bsm = time.time()
        while self._running and self.state == ChargeState.CHARGING:
            now = time.time()
            # BCL @ 50ms
            bcl = self.msgs.BCL(
                v_demand=min(self.params.get('max_total_voltage', 700.0),
                             self.sim_pack_v + 5),
                i_demand=self.params.get('charge_current_demand', 100.0)
            )
            self._send(self.cid.BCL, bcl)
            

            # BCS @ 250ms
            if now - last_bcs >= 0.250:
                t_remain = max(0, int((self.params.get('target_soc', 80) - self.sim_soc)
                               / max(abs(self.sim_current) * 0.1, 0.01)))
                bcs = self.msgs.BCS(
                    v_meas=self.sim_pack_v,
                    i_meas=self.sim_current,
                    soc=self.sim_soc,
                    t_remain=t_remain,
                    cell_max_v=self.sim_cell_max_v
                )
                self._send_app("BCS", self.cid.BCS, bcs, wait_for_eom=True, timeout=2.0)
                last_bcs = now

                # BSM @ 250ms -- Table D.1: BSM start condition is
                # "receive CCS", not "charging started". Previously this
                # sent unconditionally as soon as CHARGING began, which
                # could put BSM on the bus before any CCS was ever seen.
                if self._bsm_started:
                    bsm = self.msgs.BSM(
                        max_v=self.sim_cell_max_v, max_v_grp=1,
                        max_t=self.sim_temp_max,
                        min_v=self.sim_cell_max_v - 0.05, min_v_grp=2,
                        min_t=self.sim_temp_max - 2,
                        max_t_grp=1
                    )
                    self._send(self.cid.BSM, bsm)
                    last_bsm = now

            # Check stop condition
            if self.sim_soc >= self.params.get('target_soc', 80.0):
                self._log(f"SOC reached {self.sim_soc:.1f}% → sending BST")
                self._stop_periodic()
                self._send_BST(reason=0x01)  # SOC target reached
                self.state = ChargeState.STOPPING
                break

            time.sleep(0.050)

    def get_status(self) -> dict:
        return {
            'state':    self.state.value,
            'soc':      self.sim_soc,
            'pack_v':   self.sim_pack_v,
            'current':  self.sim_current,
            'cell_v':   self.sim_cell_max_v,
            'temp':     self.sim_temp_max,
            'violations': len(self.violations),
        }


# ============================================================
# Charger Simulator (for DEMO mode – no real charger needed)
# ============================================================
class ChargerSimulator:
    """Simulates a GB/T 27930 compliant DC charger."""

    DEFAULT_FAULTS = {
        'skip_crm': False,
        'skip_cts': False,
        'limit_cml_voltage': False,
        'cro_not_ready': False,
        'slow_ccs': False,
        'early_stop': False,
    }

    def __init__(self, bus_send, log_cb=None, cid_profile=DEMO_CID, params: dict | None = None):
        self.bus_send = bus_send
        self.log      = log_cb or print
        self.cid      = cid_profile
        self.sa_bms   = getattr(cid_profile, 'SA_BMS', SA_BMS)
        self.sa_chg   = getattr(cid_profile, 'SA_CHARGER', SA_CHARGER)
        self.params   = dict(params or {})
        self.tp       = J1939_TP(self._tp_send, self.sa_chg, self.sa_bms, log_cb)
        self._running = False
        self._state   = ChargeState.IDLE
        self._bms_responses: queue.Queue = queue.Queue()
        self._thread  = None
        self.faults   = dict(self.DEFAULT_FAULTS)
        self.violations: list[str] = []
        self.event_log: list[str] = []
        self.last_bms_msg = "—"
        self.last_bms_voltage = 0.0
        self.last_bms_current = 0.0
        self.last_bms_soc = 0.0
        self._got_bhm = False
        self._got_brm = False
        self._got_bcp = False
        self._bms_ready = False

    def on_message(self, can_id: int, data: bytes):
        """Receive BMS messages."""
        self._bms_responses.put((can_id, data))
        cid = can_id & 0x1FFFFFFF
        pf = (cid >> 16) & 0xFF
        sa = cid & 0xFF
        if sa == self.sa_chg:
            return
        if pf == 0xEC:
            da = (cid >> 8) & 0xFF
            if da != self.sa_chg and da != 0xFF:
                return  # TPCM addressed to the other charger; ignore
            self.tp.on_tpcm(cid, data)
            return
        if pf == 0xEB:
            if sa != self.sa_bms:
                return  # TPDT from the other BMS; ignore
            result = self.tp.on_tpdt(data)
            if result:
                pgn, payload = result
                self._handle_bms_tp_payload(pgn, payload)
            return
        if sa != self.sa_bms:
            return
        self.last_bms_msg = f"0x{cid:08X}"
        if cid == self.cid.BHM or pf == 0x27:
            self._got_bhm = True
            self._log("RX BHM")
        elif cid == self.cid.BCS or pf in (0x10, 0x96):
            self.last_bms_voltage = decode_signal(data, 0, 16, 0.1)
            self.last_bms_current = decode_signal(data, 16, 16, 0.1, -400.0)
            self.last_bms_soc = decode_signal(data, 48, 8, 1.0, 0.0) if len(data) >= 7 else self.last_bms_soc
            self._log(f"RX BCS V={self.last_bms_voltage:.1f} I={self.last_bms_current:.1f}A SOC={self.last_bms_soc:.0f}%")
        elif cid == self.cid.BRO or pf == 0x95:
            self._bms_ready = (data[:1] == b'\xAA')
            self._log(f"RX BRO ready={self._bms_ready}")
        elif cid == self.cid.BCL or pf == 0x97:
            self._log("RX BCL")
        elif cid == self.cid.BSM or pf in (0x98, 0x08):
            self._log("RX BSM")
        elif cid == self.cid.BST or pf == 0x9C:
            self._log(f"RX BST reason=0x{data[0]:02X}" if data else "RX BST")
        elif cid == self.cid.BSD or pf == 0x9A:
            self._log("RX BSD")

    def _handle_bms_tp_payload(self, pgn: int, payload: bytes):
        self._log(f"TP assembled from BMS PGN=0x{pgn:04X} len={len(payload)}")
        if pgn == PGN._BRM:
            self._got_brm = True
            self._log("RX BRM (TP)")
            return
        if pgn == PGN._BCP:
            self._got_bcp = True
            self._log("RX BCP (TP)")
            return
        if pgn == PGN._BCS:
            self.last_bms_voltage = decode_signal(payload, 0, 16, 0.1)
            self.last_bms_current = decode_signal(payload, 16, 16, 0.1, -400.0)
            self.last_bms_soc = decode_signal(payload, 48, 8, 1.0, 0.0) if len(payload) >= 7 else self.last_bms_soc
            self._log(f"RX BCS (TP) V={self.last_bms_voltage:.1f} I={self.last_bms_current:.1f}A SOC={self.last_bms_soc:.0f}%")
            return
        if pgn == PGN._BSD:
            self._log("RX BSD (TP)")

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def set_faults(self, faults: dict):
        self.faults.update({k: bool(v) for k, v in faults.items() if k in self.DEFAULT_FAULTS})

    def _log(self, msg: str, level='INFO'):
        entry = f"[{time.time():.3f}] [CHG] [{level}] {msg}"
        self.event_log.append(entry)
        self.log(entry)

    def _violation(self, msg: str):
        entry = f"[{time.time():.3f}] ⚠ VIOLATION: {msg}"
        self.violations.append(entry)
        self.event_log.append(entry)
        self.log(entry)

    def _send(self, can_id: int, data: bytes):
        payload = pad_j1939(data)
        self.bus_send(can_id, payload)
        self._log(f"TX 0x{can_id:08X}  {payload.hex(' ')}")

    def _tp_send(self, can_id: int, data: bytes):
        self.bus_send(can_id, data)
        self._log(f"TP TX 0x{can_id:08X}  {data.hex(' ')}")

    def _wait_response(self, timeout=5.0):
        try:
            return self._bms_responses.get(timeout=timeout)
        except queue.Empty:
            return None, None

    def _wait_until(self, predicate, timeout: float, interval: float = 0.05) -> bool:
        deadline = time.time() + timeout
        while self._running and time.time() < deadline:
            if predicate():
                return True
            time.sleep(interval)
        return predicate()

    def _run(self):
        try:
            self._state = ChargeState.HANDSHAKE
            self._handshake_phase()
            if not self._running:
                return
            self._state = ChargeState.RECOGNITION
            self._recognition_phase()
            if self.faults['skip_crm']:
                return
            if not self._running:
                return
            self._state = ChargeState.PARAMETER
            self._parameter_phase()
            if self.faults['cro_not_ready']:
                self._state = ChargeState.READY
                return
            if not self._running:
                return
            self._state = ChargeState.CHARGING
            self._charging_phase()
            if not self._running:
                return
            self._state = ChargeState.STOPPING
            self._stop_phase()
            self._state = ChargeState.STOP_DONE
        except Exception as e:
            self._state = ChargeState.ERROR
            self._log(f"ERROR: {e}", level='ERROR')

    def _handshake_phase(self):
        """Appendix A: periodically send CHM until BHM is received or timeout."""
        self._log("=== HANDSHAKE PHASE ===")
        self._got_bhm = False
        deadline = time.time() + 5.0
        while self._running and time.time() < deadline and not self._got_bhm:
            self._send(self.cid.CHM, bytes([0x01, 0x00, 0x00]))
            time.sleep(0.25)
        if not self._got_bhm:
            self._violation("BHM not received within 5s of CHM start")
            self._running = False

    def _recognition_phase(self):
        """Standard 10.1.3/10.1.4: send CRM=0x00 until BRM, then CRM=0xAA."""
        self._log("=== RECOGNITION PHASE ===")
        if self.faults['skip_crm']:
            self._violation("Fault injection active: CRM skipped")
            return
        self._got_brm = False
        crm = bytearray(8)
        crm_no = 12345678
        crm[1:5] = crm_no.to_bytes(4, 'little')
        crm[5:8] = (1234).to_bytes(3, 'little')
        deadline = time.time() + 15.0
        while self._running and time.time() < deadline and not self._got_brm:
            crm[0] = 0x00
            self._send(self.cid.CRM, bytes(crm))
            time.sleep(0.25)
        if not self._got_brm:
            self._violation("BRM not received within 5s of CRM start")
            self._running = False
            return
        # Table D.1: CRM stops on BCP receipt.
        # Send CRM=AA until BCP received or 2s timeout (whichever first).
        crm_aa_deadline = time.time() + 2.0
        while self._running and time.time() < crm_aa_deadline and not self._got_bcp:
            crm[0] = 0xAA
            self._send(self.cid.CRM, bytes(crm))
            time.sleep(0.25)

    def _parameter_phase(self):
        """Appendix A: send CTS/CML until BCP, then CRO=00+CML until BRO=AA, then CRO=AA."""
        self._log("=== PARAMETER PHASE ===")
        # Do NOT reset _got_bcp — BMS sends BCP once during CRM=AA window
        # before _parameter_phase starts. Resetting causes 5s timeout.
        self._bms_ready = False
        if not self.faults['skip_cts']:
            now = datetime.datetime.now()
            cts = bytes([now.second, now.minute, now.hour,
                         now.day, now.month, now.year % 100, now.year // 100])
        else:
            cts = None
            self._violation("Fault injection active: CTS skipped")
        cml = bytearray(8)
        max_v = 520.0 if self.faults['limit_cml_voltage'] else self.params.get('charger_max_v', 800.0)
        encode_signal(cml,  0, 16, max_v,  0.1)
        encode_signal(cml, 16, 16, 200.0,  0.1)
        encode_signal(cml, 32, 16, self.params.get('charger_max_i', 250.0),  0.1, -400.0)
        encode_signal(cml, 48, 16, 0.0,    0.1, -400.0)
        # Loop 1: CTS@500ms + CML@250ms until BCP (skips instantly if already received)
        deadline = time.time() + 5.0
        last_cts = last_cml = 0.0
        while self._running and time.time() < deadline and not self._got_bcp:
            now = time.time()
            if cts is not None and (now - last_cts) >= 0.500:
                self._send(self.cid.CTS, cts)
                last_cts = now
            if (now - last_cml) >= 0.250:
                self._send(self.cid.CML, bytes(cml))
                last_cml = now
            time.sleep(0.05)
        if not self._got_bcp:
            self._violation("BCP not received within 5s of CTS/CML start")
            self._running = False
            return
        # Loop 2: CRO=00@250ms + CML@250ms until BRO=AA (§10.2.5: 60s timeout)
        # Table D.1: CML continues until BRO=AA; CTS continues until BRO=AA
        cro_unready = bytes([0x00])
        deadline = time.time() + 60.0
        last_cml = last_cts = 0.0
        while self._running and time.time() < deadline and not self._bms_ready:
            now = time.time()
            if cts is not None and (now - last_cts) >= 0.500:
                self._send(self.cid.CTS, cts)
                last_cts = now
            if (now - last_cml) >= 0.250:
                self._send(self.cid.CML, bytes(cml))
                last_cml = now
            self._send(self.cid.CRO, cro_unready)
            time.sleep(0.25)
        if not self._bms_ready:
            self._violation("BRO=AA not received within 60s of CRO=00 (§10.2.5)")
            self._running = False
            return
        self._send(self.cid.CRO, bytes([0x00 if self.faults['cro_not_ready'] else 0xAA]))
        if self.faults['cro_not_ready']:
            self._violation("Fault injection active: CRO sent as NOT READY")
            self._running = False
            return

    def _charging_phase(self):
        """Send CCS at 250ms while charging."""
        self._log("=== CHARGING PHASE ===")
        v = self.params.get('pack_voltage', 560.0)
        i = self.params.get('charge_current_demand', 100.0)
        cycles = 12 if self.faults['early_stop'] else 200
        ccs_period = 0.8 if self.faults['slow_ccs'] else 0.050
        if self.faults['slow_ccs']:
            self._violation("Fault injection active: slow CCS period")
        elapsed_min = 0.0
        for cycle in range(cycles):
            if not self._running:
                return
            ccs = bytearray(8)
            encode_signal(ccs,  0, 16, v, 0.1)
            encode_signal(ccs, 16, 16, i, 0.1, -400.0)
            elapsed_min = min(600, int((cycle * ccs_period) / 60.0))
            encode_signal(ccs, 32, 16, elapsed_min, 1.0, 0.0)   # cumulative charging time (min)
            encode_signal(ccs, 48, 2, 1, 1.0, 0.0)              # charging permissible = 1 (permit)
            self._send(self.cid.CCS, bytes(ccs))
            v += 0.5
            # Taper the magnitude of the (negative, i.e. charging) current
            # toward a floor of -10A as the session progresses -- staying
            # negative throughout. The previous `max(10, i - 0.2)` clamped
            # ANY negative starting current straight to +10A on the very
            # first iteration (e.g. -100 - 0.2 = -100.2, max(10, -100.2)
            # = 10), which is why the simulated charger's own CCS output
            # went positive almost immediately regardless of the demand
            # sign requested via BCL.
            i = max(10.0, i - 0.2)   # taper current down toward 10A floor
            time.sleep(ccs_period)

    def _stop_phase(self):
        """Send CST, wait for BST, send CSD."""
        self._log("=== STOP PHASE ===")
        cst = bytearray(4)
        cst[0] = 0x01   # normal stop – SOC target
        self._send(self.cid.CST, bytes(cst))
        time.sleep(1.0)
        # CSD
        csd = bytearray(8)
        csd[0:2] = (45).to_bytes(2, 'little')   # 45 min
        encode_signal(csd, 16, 16, 22.4, 0.1)    # 22.4 kWh
        csd[4:8] = (12345678).to_bytes(4, 'little')
        self._send(self.cid.CSD, bytes(csd))

    def get_status(self) -> dict:
        return {
            'state': self._state.value,
            'soc': self.last_bms_soc,
            'pack_v': self.last_bms_voltage,
            'current': self.last_bms_current,
            'cell_v': 0.0,
            'temp': 0.0,
            'violations': len(self.violations),
        }


class MultiSessionRuntime:
    """Aggregates one or more independent gun sessions behind a single UI/runtime facade."""

    def __init__(self, sessions: list[dict], log_cb=None):
        self.sessions = sessions
        self.log = log_cb or (lambda *a: None)
        self.cid_profiles = [s['cid'] for s in sessions]

    @property
    def violations(self):
        issues = []
        for s in self.sessions:
            node = s.get('node')
            if node and hasattr(node, 'violations'):
                issues.extend(node.violations)
            charger = s.get('charger')
            if charger and hasattr(charger, 'violations'):
                issues.extend(charger.violations)
        return issues

    @property
    def event_log(self):
        events = []
        for s in self.sessions:
            node = s.get('node')
            if node and hasattr(node, 'event_log'):
                events.extend(node.event_log)
            charger = s.get('charger')
            if charger and hasattr(charger, 'event_log'):
                events.extend(charger.event_log)
        return events

    def start(self):
        for s in self.sessions:
            charger = s.get('charger')
            if charger and hasattr(charger, 'start'):
                charger.start()

    def stop(self):
        for s in self.sessions:
            charger = s.get('charger')
            if charger and hasattr(charger, 'stop'):
                charger.stop()
            node = s.get('node')
            if node and hasattr(node, '_stop_periodic'):
                node._stop_periodic()

    def set_faults(self, faults: dict):
        for s in self.sessions:
            charger = s.get('charger')
            if charger and hasattr(charger, 'set_faults'):
                charger.set_faults(faults)

    def apply_params(self, params: dict):
        for s in self.sessions:
            node = s.get('node')
            if node and hasattr(node, 'params'):
                node.params.update(params)
                if hasattr(node, 'msgs'):
                    node.msgs.p = node.params
                if hasattr(node, 'sim_soc'):
                    node.sim_soc = params.get('soc', node.sim_soc)
                if hasattr(node, 'sim_pack_v'):
                    node.sim_pack_v = params.get('pack_voltage', node.sim_pack_v)
            charger = s.get('charger')
            if charger and hasattr(charger, 'params'):
                charger.params.update(params)

    def request_stop_from_bms(self):
        for s in self.sessions:
            node = s.get('node')
            if node and hasattr(node, 'request_stop'):
                node.request_stop(0x01)

    def request_stop_from_charger(self):
        for s in self.sessions:
            charger = s.get('charger')
            if charger and hasattr(charger, 'request_stop'):
                charger.request_stop(0x01)

    def get_socket_statuses(self):
        out = {}
        for s in self.sessions:
            label = s['label']
            source = s.get('node') or s.get('charger')
            if source and hasattr(source, 'get_status'):
                out[label] = source.get_status()
        return out

    def get_status(self) -> dict:
        statuses = list(self.get_socket_statuses().values())
        if not statuses:
            return {'state': 'IDLE', 'soc': 0.0, 'pack_v': 0.0, 'current': 0.0, 'cell_v': 0.0, 'temp': 0.0, 'violations': 0}
        state_priority = ['ERROR', 'CHARGING', 'READY', 'PARAMETER', 'RECOGNITION', 'HANDSHAKE', 'STOPPING', 'STOP_DONE', 'IDLE']
        states = [s.get('state', 'IDLE') for s in statuses]
        aggregate_state = next((state for state in state_priority if state in states), states[0])
        return {
            'state': aggregate_state,
            'soc': sum(s.get('soc', 0.0) for s in statuses) / len(statuses),
            'pack_v': sum(s.get('pack_v', 0.0) for s in statuses) / len(statuses),
            'current': sum(s.get('current', 0.0) for s in statuses),
            'cell_v': max(s.get('cell_v', 0.0) for s in statuses),
            'temp': max(s.get('temp', 0.0) for s in statuses),
            'violations': sum(s.get('violations', 0) for s in statuses),
        }


# ============================================================
# Protocol Validator
# ============================================================
class ProtocolValidator:
    """
    Cross-checks the actual observed message sequence against
    GB/T 27930 specification rules.
    """

    GB_RULES = {
        'CHM_interval_ms':  (200, 300),   # 250ms nominal
        'BHM_timeout_ms':   5000,
        'CRM_timeout_ms':   5000,
        'CTS_timeout_ms':   5000,
        'CML_timeout_ms':   5000,
        'CRO_timeout_ms':   5000,
        'CCS_interval_ms':  (200, 300),
        'BCL_interval_ms':  (40, 100),
        'BCS_interval_ms':  (200, 300),
        'BSM_interval_ms':  (200, 300),
    }

    def __init__(self):
        self.results: list[dict] = []
        self._msg_times: dict = defaultdict(list)

    def reset(self):
        self.results.clear()
        self._msg_times.clear()

    def record(self, msg_name: str, ts: float):
        self._msg_times[msg_name].append(ts)

    def check_intervals(self, msg_name: str) -> list[str]:
        times = self._msg_times.get(msg_name, [])
        issues = []
        key = f"{msg_name}_interval_ms"
        if key not in self.GB_RULES:
            return []
        lo, hi = self.GB_RULES[key]
        for i in range(1, len(times)):
            dt = (times[i] - times[i-1]) * 1000
            if dt < lo or dt > hi:
                issues.append(f"{msg_name}: interval {dt:.0f}ms out of [{lo},{hi}]ms")
        return issues

    def full_report(self) -> str:
        lines = ["=" * 60, "  GB/T 27930 Validation Report", "=" * 60]
        for msg in ['CHM', 'BCS', 'BCL', 'BSM', 'CCS']:
            issues = self.check_intervals(msg)
            counts = len(self._msg_times.get(msg, []))
            lines.append(f"\n{msg}: {counts} frames")
            if issues:
                for iss in issues:
                    lines.append(f"  ⚠  {iss}")
            else:
                lines.append("  ✓  Timing OK")
        return "\n".join(lines)


# ============================================================
#  GUI  (Tkinter)
# ============================================================
COLORS = {
    'bg':          '#0b1220',
    'panel':       '#121b2f',
    'panel_alt':   '#0f1728',
    'border':      '#27324a',
    'accent':      '#ff8a65',
    'accent_soft': '#33231d',
    'green':       '#2fbf8f',
    'green_soft':  '#16392f',
    'yellow':      '#f5b942',
    'yellow_soft': '#3b2e12',
    'blue':        '#55b6ff',
    'blue_soft':   '#173248',
    'text':        '#eef4ff',
    'subtext':     '#93a4bd',
    'muted':       '#62748f',
    'charging':    '#69c0ff',
    'error':       '#ff6b6b',
    'error_soft':  '#3a1c24',
}

class BMS_ValidatorGUI:

    def __init__(self, root, bms, vbus: VirtualBus,
                 charger_sim, session_mode: str = 'demo', iface: str | None = None,
                 bustype: str = 'socketcan', role: str = 'bms'):
        self.root        = root
        self.bms         = bms
        self.vbus        = vbus
        self.charger_sim = charger_sim
        self.session_mode = session_mode
        self.iface = iface
        self.hw_bus = None
        self.current_bustype = bustype
        self.current_role = role
        self.current_profile_key = 'single_socket1'
        self.current_cid = getattr(bms, 'cid', DEMO_CID)
        self.current_profiles = [self.current_cid]
        self.validator   = ProtocolValidator()
        self._running    = False
        self._tp_log_sessions: dict[tuple[int, int], int] = {}

        root.title("GB/T 27930  —  BMS Validator  |  JSW GTL SIDV")
        root.configure(bg=COLORS['bg'])
        root.geometry("1280x800")
        root.minsize(820, 560)

        self._configure_styles()
        self._build_ui()
        self._start_bus_monitor()
        self._refresh_loop()

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background=COLORS['bg'], borderwidth=0, tabmargins=(0, 0, 0, 0))
        style.configure('TNotebook.Tab', background=COLORS['panel'], foreground=COLORS['subtext'],
                        font=('Segoe UI Semibold', 10), padding=(16, 8), borderwidth=0)
        style.map('TNotebook.Tab',
                  background=[('selected', COLORS['accent'])],
                  foreground=[('selected', COLORS['bg'])])
        style.configure('TCombobox',
                        fieldbackground=COLORS['panel_alt'],
                        background=COLORS['panel_alt'],
                        foreground=COLORS['text'],
                        bordercolor=COLORS['border'],
                        lightcolor=COLORS['border'],
                        darkcolor=COLORS['border'],
                        arrowcolor=COLORS['accent'],
                        selectbackground=COLORS['panel_alt'],
                        selectforeground=COLORS['text'],
                        padding=6)

    # ── UI construction ──────────────────────────────────
    def _build_ui(self):
        # Title bar
        title_frame = tk.Frame(self.root, bg=COLORS['panel'], height=72,
                               highlightthickness=1, highlightbackground=COLORS['border'])
        title_frame.pack(fill='x', side='top', padx=10, pady=(10, 0))
        title_frame.pack_propagate(False)
        brand = tk.Frame(title_frame, bg=COLORS['panel'])
        brand.pack(side='left', fill='y', padx=18)
        tk.Label(brand, text="JSW GTL SIDV", bg=COLORS['panel'], fg=COLORS['accent'],
                 font=('Segoe UI Semibold', 9)).pack(anchor='w', pady=(10, 0))
        tk.Label(brand, text="GB/T 27930 Charge Session Studio",
                 bg=COLORS['panel'], fg=COLORS['text'],
                 font=('Segoe UI Semibold', 18)).pack(anchor='w')
        tk.Label(brand, text="Protocol simulation, validation and CAN session monitoring",
                 bg=COLORS['panel'], fg=COLORS['subtext'],
                 font=('Segoe UI', 9)).pack(anchor='w', pady=(0, 10))
        badge = tk.Frame(title_frame, bg=COLORS['panel_alt'],
                         highlightthickness=1, highlightbackground=COLORS['border'])
        badge.pack(side='right', padx=18, pady=14)
        self.state_lbl = tk.Label(badge, text="IDLE",
                                  bg=COLORS['panel_alt'], fg=COLORS['subtext'],
                                  font=('Segoe UI Semibold', 12), padx=18, pady=8)
        self.state_lbl.pack()

        # Main paned layout
        paned = tk.PanedWindow(self.root, orient='horizontal', bg=COLORS['bg'],
                               sashwidth=4, sashrelief='flat')
        paned.pack(fill='both', expand=True, padx=10, pady=10)

        left  = tk.Frame(paned, bg=COLORS['bg'])
        right = tk.Frame(paned, bg=COLORS['bg'])
        paned.add(left,  minsize=350)
        paned.add(right, minsize=500)

        left_canvas = tk.Canvas(left, bg=COLORS['bg'], highlightthickness=0, relief='flat')
        left_scroll = tk.Scrollbar(left, orient='vertical', command=left_canvas.yview)
        left_inner = tk.Frame(left_canvas, bg=COLORS['bg'])
        left_inner.bind(
            '<Configure>',
            lambda e: left_canvas.configure(scrollregion=left_canvas.bbox('all'))
        )
        left_window = left_canvas.create_window((0, 0), window=left_inner, anchor='nw')
        left_canvas.configure(yscrollcommand=left_scroll.set)
        left_canvas.pack(side='left', fill='both', expand=True)
        left_scroll.pack(side='right', fill='y')
        left_canvas.bind('<Configure>', lambda e: left_canvas.itemconfigure(left_window, width=e.width))
        left_canvas.bind_all('<MouseWheel>', lambda e: left_canvas.yview_scroll(int(-e.delta / 120), 'units'))

        self._build_left(left_inner)
        self._build_right(right)

    def _build_left(self, parent):
        mf = self._panel(parent, "Session", COLORS['panel'])
        mf.pack(fill='x', pady=(0, 6))
        mode_text = self.session_mode.replace('_', ' ').title()
        iface_text = self.iface or 'internal'
        self._mode_text = tk.StringVar(value=f"Mode: {mode_text}")
        self._iface_text = tk.StringVar(value=f"Interface: {iface_text}")
        self._profile_text = tk.StringVar(value=f"Topology: {PROFILE_OPTIONS[self.current_profile_key][0]}")
        tk.Label(mf, textvariable=self._mode_text,
                 bg=COLORS['panel'], fg=COLORS['text'],
                 font=('Segoe UI Semibold', 11),
                 anchor='w').pack(fill='x', padx=12, pady=(10, 2))
        tk.Label(mf, textvariable=self._iface_text,
                 bg=COLORS['panel'], fg=COLORS['subtext'],
                 font=('Segoe UI', 9),
                 anchor='w').pack(fill='x', padx=12, pady=(0, 4))
        tk.Label(mf, textvariable=self._profile_text,
                 bg=COLORS['panel'], fg=COLORS['subtext'],
                 font=('Segoe UI', 9),
                 anchor='w').pack(fill='x', padx=12, pady=(0, 4))
        tk.Label(mf, text=f"Python: {sys.executable}",
                 bg=COLORS['panel'], fg=COLORS['subtext'],
                 font=('Segoe UI', 8),
                 anchor='w', wraplength=320, justify='left').pack(fill='x', padx=12, pady=(0, 10))

        tool_default = 'vector' if self.current_bustype == 'vector' else 'peak'
        iface_default = self.iface or ('0' if tool_default == 'vector' else 'PCAN_USBBUS1')
        self._tool_var = tk.StringVar(value=tool_default)
        self._iface_var = tk.StringVar(value=iface_default)
        self._role_var = tk.StringVar(value=self.current_role)
        self._profile_labels = {key: label for key, (label, _prof) in PROFILE_OPTIONS.items()}
        self._profile_reverse = {label: key for key, label in self._profile_labels.items()}
        self._profile_var = tk.StringVar(value=self._profile_labels[self.current_profile_key])

        profile_row = tk.Frame(mf, bg=COLORS['panel'])
        profile_row.pack(fill='x', padx=10, pady=2)
        tk.Label(profile_row, text="Topology", bg=COLORS['panel'], fg=COLORS['subtext'],
                 font=('Segoe UI', 9), width=14, anchor='w').pack(side='left')
        profile_box = ttk.Combobox(profile_row, textvariable=self._profile_var,
                                   values=list(self._profile_labels.values()), state='readonly', width=22)
        profile_box.pack(side='left', padx=4)

        tool_row = tk.Frame(mf, bg=COLORS['panel'])
        tool_row.pack(fill='x', padx=10, pady=2)
        tk.Label(tool_row, text="CAN Tool", bg=COLORS['panel'], fg=COLORS['subtext'],
                 font=('Segoe UI', 9), width=14, anchor='w').pack(side='left')
        tool_box = ttk.Combobox(tool_row, textvariable=self._tool_var,
                                values=['peak', 'vector'], state='readonly', width=14)
        tool_box.pack(side='left', padx=4)
        tool_box.bind('<<ComboboxSelected>>', lambda _e: self._sync_tool_defaults())

        iface_row = tk.Frame(mf, bg=COLORS['panel'])
        iface_row.pack(fill='x', padx=10, pady=2)
        tk.Label(iface_row, text="Channel", bg=COLORS['panel'], fg=COLORS['subtext'],
                 font=('Segoe UI', 9), width=14, anchor='w').pack(side='left')
        tk.Entry(iface_row, textvariable=self._iface_var, bg=COLORS['bg'], fg=COLORS['text'],
                 insertbackground=COLORS['text'], font=('Segoe UI', 9), width=16,
                 relief='flat', highlightthickness=1,
                 highlightbackground=COLORS['border']).pack(side='left', padx=4)

        role_row = tk.Frame(mf, bg=COLORS['panel'])
        role_row.pack(fill='x', padx=10, pady=(2, 8))
        tk.Label(role_row, text="Action Mode", bg=COLORS['panel'], fg=COLORS['subtext'],
                 font=('Segoe UI', 9), width=14, anchor='w').pack(side='left')
        role_box = ttk.Combobox(role_row, textvariable=self._role_var,
                                values=['bms', 'charger'], state='readonly', width=14)
        role_box.pack(side='left', padx=4)

        quick = tk.Frame(mf, bg=COLORS['panel'])
        quick.pack(fill='x', padx=10, pady=(6, 10))
        quick_top = tk.Frame(quick, bg=COLORS['panel'])
        quick_top.pack(fill='x')
        quick_bottom = tk.Frame(quick, bg=COLORS['panel'])
        quick_bottom.pack(fill='x', pady=(6, 0))
        tk.Button(quick_top, text="Demo",
                  command=self._start_demo,
                  bg=COLORS['accent'], fg=COLORS['bg'],
                  font=('Segoe UI Semibold', 9),
                  relief='flat', cursor='hand2', pady=6
                  ).pack(side='left', fill='x', expand=True, padx=(0, 4))
        tk.Button(quick_top, text="Demo on CAN",
                  command=self._start_demo_on_can,
                  bg=COLORS['charging'], fg=COLORS['bg'],
                  font=('Segoe UI Semibold', 9),
                  relief='flat', cursor='hand2', pady=6
                  ).pack(side='left', fill='x', expand=True, padx=(4, 0))
        tk.Button(quick_bottom, text="Simulate BMS",
                  command=self._start_simulate_bms,
                  bg=COLORS['green'], fg=COLORS['bg'],
                  font=('Segoe UI Semibold', 9),
                  relief='flat', cursor='hand2', pady=6
                  ).pack(side='left', fill='x', expand=True, padx=(0, 4))
        tk.Button(quick_bottom, text="Simulate Charger",
                  command=self._start_simulate_charger,
                  bg=COLORS['yellow'], fg=COLORS['bg'],
                  font=('Segoe UI Semibold', 9),
                  relief='flat', cursor='hand2', pady=6
                  ).pack(side='left', fill='x', expand=True, padx=4)
        tk.Button(quick_bottom, text="Stop Session",
                  command=self._stop,
                  bg=COLORS['border'], fg=COLORS['text'],
                  font=('Segoe UI Semibold', 9),
                  relief='flat', cursor='hand2', pady=6
                  ).pack(side='left', fill='x', expand=True, padx=(4, 0))
        # ── BMS Parameters ────────────────────────────
        pf = self._panel(parent, "BMS Configuration", COLORS['panel'])
        pf.pack(fill='x', pady=(0, 6))

        self._params = {}
        rows = [
            ("Pack Voltage (V)",       'pack_voltage',        '560.0'),
            ("Max Total Voltage (V)",  'max_total_voltage',   '700.0'),
            ("Pack Capacity (Ah)",     'pack_capacity',       '200.0'),
            ("Initial SOC (%)",        'soc',                 '20.0'),
            ("Target SOC (%)",         'target_soc',          '80.0'),
            ("Max Cell Voltage (V)",   'cell_max_v',          '3.65'),
            ("Max Charge Current (A)", 'max_charge_cur',      '250.0'),
            ("Nominal Energy (kWh)",   'nominal_energy',      '112.0'),
            ("Max Temperature (C)",    'max_temp',            '45.0'),
            ("Charge I Demand (A)",    'charge_current_demand','-100.0'),
        ]
        for label, key, default in rows:
            row = tk.Frame(pf, bg=COLORS['panel'])
            row.pack(fill='x', padx=10, pady=2)
            tk.Label(row, text=label, bg=COLORS['panel'], fg=COLORS['subtext'],
                     font=('Segoe UI', 9), width=22, anchor='w').pack(side='left')
            var = tk.StringVar(value=default)
            e = tk.Entry(row, textvariable=var, bg=COLORS['bg'], fg=COLORS['text'],
                         insertbackground=COLORS['text'],
                         font=('Segoe UI', 9), width=10,
                         relief='flat', highlightthickness=1,
                         highlightbackground=COLORS['border'])
            e.pack(side='left', padx=4)
            self._params[key] = var

        ff = self._panel(parent, "Fault Injection", COLORS['panel'])
        ff.pack(fill='x', pady=(0, 6))
        self._fault_vars = {}
        fault_rows = [
            ("Skip CRM", 'skip_crm'),
            ("Skip CTS", 'skip_cts'),
            ("Low CML Voltage", 'limit_cml_voltage'),
            ("CRO Not Ready", 'cro_not_ready'),
            ("Slow CCS", 'slow_ccs'),
            ("Early Stop", 'early_stop'),
        ]
        for label, key in fault_rows:
            row = tk.Frame(ff, bg=COLORS['panel'])
            row.pack(fill='x', padx=10, pady=1)
            var = tk.BooleanVar(value=False)
            cb = tk.Checkbutton(
                row, text=label, variable=var,
                state='normal' if self.charger_sim else 'disabled',
                command=self._apply_faults,
                bg=COLORS['panel'], fg=COLORS['text'],
                activebackground=COLORS['panel'], activeforeground=COLORS['accent'],
                selectcolor=COLORS['bg'], font=('Segoe UI', 9),
                anchor='w', relief='flat', highlightthickness=0
            )
            cb.pack(fill='x')
            self._fault_vars[key] = var

        # ── Live Status ───────────────────────────────
        sf = self._panel(parent, "Live Status", COLORS['panel'])
        sf.pack(fill='x', pady=(0, 6))

        self._status_vars = {}
        self._status_accents = {}
        status_rows = [
            ("State",        'state',      COLORS['charging'], COLORS['blue_soft']),
            ("SOC",          'soc',        COLORS['green'],    COLORS['green_soft']),
            ("Pack Voltage", 'pack_v',     COLORS['text'],     COLORS['panel_alt']),
            ("Current",      'current',    COLORS['yellow'],   COLORS['yellow_soft']),
            ("Cell Vmax",    'cell_v',     COLORS['text'],     COLORS['panel_alt']),
            ("Temperature",  'temp',       COLORS['text'],     COLORS['panel_alt']),
            ("Violations",   'violations', COLORS['error'],    COLORS['error_soft']),
        ]
        status_grid = tk.Frame(sf, bg=COLORS['panel'])
        status_grid.pack(fill='x', padx=10, pady=(6, 10))
        for idx, (label, key, color, bg) in enumerate(status_rows):
            row = idx // 2
            col = idx % 2
            card = tk.Frame(status_grid, bg=bg, highlightthickness=1,
                            highlightbackground=COLORS['border'])
            card.grid(row=row, column=col, sticky='nsew', padx=4, pady=4)
            status_grid.grid_columnconfigure(col, weight=1)
            tk.Label(card, text=label.upper(), bg=bg, fg=COLORS['subtext'],
                     font=('Segoe UI Semibold', 8), anchor='w').pack(fill='x', padx=12, pady=(10, 2))
            var = tk.StringVar(value='-')
            lbl = tk.Label(card, textvariable=var, bg=bg, fg=color,
                           font=('Segoe UI Semibold', 15), anchor='w')
            lbl.pack(fill='x', padx=12, pady=(0, 10))
            self._status_vars[key] = var
            self._status_accents[key] = lbl

        ops = self._panel(parent, "Operations", COLORS['panel'])
        ops.pack(fill='x', pady=(0, 6))
        tk.Label(ops,
                 text="Run controlled stop scenarios or export a validation report for review.",
                 bg=COLORS['panel'], fg=COLORS['subtext'],
                 font=('Segoe UI', 9), justify='left', wraplength=320,
                 anchor='w').pack(fill='x', padx=12, pady=(10, 8))

        stop_row = tk.Frame(ops, bg=COLORS['panel'])
        stop_row.pack(fill='x', padx=10, pady=(0, 6))
        tk.Button(stop_row, text="Stop from BMS",
                  command=self._stop_from_bms,
                  bg=COLORS['yellow'], fg=COLORS['bg'],
                  font=('Segoe UI Semibold', 9),
                  relief='flat', cursor='hand2', pady=6
                  ).pack(side='left', fill='x', expand=True, padx=(0, 4))
        tk.Button(stop_row, text="Stop from Charger",
                  command=self._stop_from_charger,
                  bg=COLORS['accent'], fg=COLORS['bg'],
                  font=('Segoe UI Semibold', 9),
                  relief='flat', cursor='hand2', pady=6
                  ).pack(side='left', fill='x', expand=True, padx=(4, 0))
        tk.Button(ops, text="Export Validation Report",
                  command=self._export_report,
                  bg=COLORS['panel_alt'], fg=COLORS['text'],
                  font=('Segoe UI Semibold', 9), relief='flat', pady=6,
                  cursor='hand2'
                  ).pack(fill='x', padx=10, pady=(0, 10))

    def _build_right(self, parent):
        shell = tk.Frame(parent, bg=COLORS['panel'],
                         highlightthickness=1, highlightbackground=COLORS['border'])
        shell.pack(fill='both', expand=True)

        topbar = tk.Frame(shell, bg=COLORS['panel'])
        topbar.pack(fill='x', padx=14, pady=(14, 8))
        tk.Label(topbar, text="Session Workbench",
                 bg=COLORS['panel'], fg=COLORS['text'],
                 font=('Segoe UI Semibold', 13)).pack(side='left')
        tk.Label(topbar, text="Live traffic, validation, sequence view and operating metrics",
                 bg=COLORS['panel'], fg=COLORS['subtext'],
                 font=('Segoe UI', 9)).pack(side='left', padx=12, pady=(2, 0))

        nb = ttk.Notebook(shell)
        nb.pack(fill='both', expand=True)

        log_frame = tk.Frame(nb, bg=COLORS['bg'])
        nb.add(log_frame, text="CAN Log")
        self._tab_header(log_frame, "Live CAN Traffic", "Decoded frames mirrored from the active session bus and hardware links.")
        self.can_log = scrolledtext.ScrolledText(
            log_frame, bg=COLORS['bg'], fg=COLORS['text'],
            font=('Consolas', 9), state='disabled',
            insertbackground=COLORS['text'],
            selectbackground=COLORS['border'],
            relief='flat', padx=10, pady=10)
        self.can_log.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        self.can_log.tag_config('CHM',  foreground='#79c0ff')
        self.can_log.tag_config('BHM',  foreground='#56d364')
        self.can_log.tag_config('TPCM', foreground='#d2a8ff')
        self.can_log.tag_config('TPDT', foreground='#d2a8ff')
        self.can_log.tag_config('CCS',  foreground='#ffa657')
        self.can_log.tag_config('BCS',  foreground='#79c0ff')
        self.can_log.tag_config('BCL',  foreground='#56d364')
        self.can_log.tag_config('VIOL', foreground='#f85149')
        self.can_log.tag_config('INFO', foreground='#8b949e')

        viol_frame = tk.Frame(nb, bg=COLORS['bg'])
        nb.add(viol_frame, text="Violations")
        self._tab_header(viol_frame, "Protocol Findings", "Timing, sequence and transport concerns collected by the validator.")
        self.viol_log = scrolledtext.ScrolledText(
            viol_frame, bg=COLORS['bg'], fg=COLORS['error'],
            font=('Consolas', 9), state='disabled', relief='flat', padx=10, pady=10)
        self.viol_log.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        seq_frame = tk.Frame(nb, bg=COLORS['bg'])
        nb.add(seq_frame, text="Sequence")
        self._tab_header(seq_frame, "Reference Sequence", "Standard-oriented charging timeline for quick operator comparison.")
        self.seq_view = scrolledtext.ScrolledText(
            seq_frame, bg=COLORS['bg'], fg=COLORS['text'],
            font=('Consolas', 8), state='disabled', relief='flat', padx=10, pady=10)
        self.seq_view.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        self._init_sequence_diagram()

        stat_frame = tk.Frame(nb, bg=COLORS['bg'])
        nb.add(stat_frame, text="Statistics")
        self._tab_header(stat_frame, "Session Metrics", "Current protocol state, timing summary and operating snapshot.")
        self.stat_view = scrolledtext.ScrolledText(
            stat_frame, bg=COLORS['bg'], fg=COLORS['text'],
            font=('Consolas', 9), state='disabled', relief='flat', padx=10, pady=10)
        self.stat_view.pack(fill='both', expand=True, padx=10, pady=(0, 10))

    def _tab_header(self, parent, title, subtitle):
        frame = tk.Frame(parent, bg=COLORS['bg'])
        frame.pack(fill='x', padx=10, pady=(10, 8))
        tk.Label(frame, text=title,
                 bg=COLORS['bg'], fg=COLORS['text'],
                 font=('Segoe UI Semibold', 11)).pack(anchor='w')
        tk.Label(frame, text=subtitle,
                 bg=COLORS['bg'], fg=COLORS['subtext'],
                 font=('Segoe UI', 9)).pack(anchor='w', pady=(2, 0))

    def _panel(self, parent, title, bg):
        f = tk.LabelFrame(parent, text=f"  {title}  ",
                          bg=bg, fg=COLORS['accent'],
                          font=('Segoe UI Semibold', 9),
                          relief='flat',
                          highlightthickness=1,
                          highlightbackground=COLORS['border'])
        return f

    def _sync_tool_defaults(self):
        tool = self._tool_var.get().lower()
        if tool == 'vector':
            if self._iface_var.get() in ('', 'PCAN_USBBUS1'):
                self._iface_var.set('0')
        else:
            if self._iface_var.get() in ('', '0'):
                self._iface_var.set('PCAN_USBBUS1')

    def _selected_profile(self):
        if hasattr(self, '_profile_var'):
            selected = self._profile_var.get()
            key = self._profile_reverse.get(selected, self.current_profile_key)
        else:
            key = self.current_profile_key
        return key, PROFILE_OPTIONS.get(key, PROFILE_OPTIONS['single_socket1'])

    def _close_hardware(self):
        if self.hw_bus:
            try:
                self.hw_bus.shutdown()
            except Exception:
                pass
            self.hw_bus = None

    def _make_demo_runtime(self, cid_profile):
        vbus = VirtualBus()
        bms = VirtualBMS(vbus.send, dict(self.bms.params), self.bms.log if hasattr(self.bms, 'log') else None,
                         cid_profile=cid_profile)
        charger = ChargerSimulator(vbus.send, bms.log, cid_profile=cid_profile, params=dict(bms.params))
        vbus.subscribe(bms.on_message)
        vbus.subscribe(charger.on_message)
        return bms, vbus, charger, 'demo'

    def _make_demo_can_runtime(self, bustype: str, iface: str, cid_profile):
        hw_bus = HardwareBus(iface, bustype, 250000)
        vbus = VirtualBus()

        def hybrid_send(cid, data):
            hw_bus.send(cid, data)
            vbus.log_frame(cid, data, channel='hw-tx')
            # Publish to the internal virtual bus after the hardware mirror so
            # external CAN tools see the original frame before any immediate
            # simulated response generated by local subscribers.
            vbus.send(cid, data, channel='demo')

        bms = VirtualBMS(hybrid_send, dict(self.bms.params),
                         self.bms.log if hasattr(self.bms, 'log') else None,
                         cid_profile=cid_profile)
        charger = ChargerSimulator(hybrid_send,
                                   self.bms.log if hasattr(self.bms, 'log') else None,
                                   cid_profile=cid_profile,
                                   params=dict(bms.params))
        vbus.subscribe(bms.on_message)
        vbus.subscribe(charger.on_message)
        return bms, vbus, charger, 'demo_hw', hw_bus

    def _make_real_runtime(self, bustype: str, iface: str, role: str, cid_profile):
        hw_bus = HardwareBus(iface, bustype, 250000)
        vbus = VirtualBus()

        def bus_send(cid, data):
            vbus.log_frame(cid, data, channel='hw-tx')
            hw_bus.send(cid, data)

        if role == 'bms':
            node = VirtualBMS(bus_send, dict(self.bms.params), self.bms.log if hasattr(self.bms, 'log') else None,
                              cid_profile=cid_profile)

            def on_hw_message(cid, data):
                vbus.log_frame(cid, data, channel='hw-rx')
                node.on_message(cid, data)

            hw_bus.subscribe(on_hw_message)
            charger = None
            mode = 'real_bms'
        else:
            node = ChargerSimulator(bus_send, self.bms.log if hasattr(self.bms, 'log') else None,
                                    cid_profile=cid_profile, params=dict(self.bms.params))

            def on_hw_message(cid, data):
                vbus.log_frame(cid, data, channel='hw-rx')
                node.on_message(cid, data)

            hw_bus.subscribe(on_hw_message)
            charger = node
            mode = 'real_charger'
        return node, vbus, charger, mode, hw_bus

    def _make_dual_demo_runtime(self):
        vbus = VirtualBus()
        log_cb = self.bms.log if hasattr(self.bms, 'log') else None
        s1_bms = VirtualBMS(vbus.send, dict(self.bms.params), log_cb, cid_profile=DEMO_CID)
        s1_chg = ChargerSimulator(vbus.send, log_cb, cid_profile=DEMO_CID, params=dict(s1_bms.params))
        s2_bms = VirtualBMS(vbus.send, dict(self.bms.params), log_cb, cid_profile=SOCKET2_CID)
        s2_chg = ChargerSimulator(vbus.send, log_cb, cid_profile=SOCKET2_CID, params=dict(s2_bms.params))
        for node in (s1_bms, s1_chg, s2_bms, s2_chg):
            vbus.subscribe(node.on_message)
        runtime = MultiSessionRuntime([
            {'label': 'Socket 1', 'node': s1_bms, 'charger': s1_chg, 'cid': DEMO_CID},
            {'label': 'Socket 2', 'node': s2_bms, 'charger': s2_chg, 'cid': SOCKET2_CID},
        ], log_cb=log_cb)
        return runtime, vbus, runtime, 'demo_dual'

    def _make_dual_demo_can_runtime(self, bustype: str, iface: str):
        hw_bus = HardwareBus(iface, bustype, 250000)
        vbus = VirtualBus()

        def hybrid_send(cid, data):
            hw_bus.send(cid, data)
            vbus.log_frame(cid, data, channel='hw-tx')
            vbus.send(cid, data, channel='demo')

        log_cb = self.bms.log if hasattr(self.bms, 'log') else None
        s1_bms = VirtualBMS(hybrid_send, dict(self.bms.params), log_cb, cid_profile=DEMO_CID)
        s1_chg = ChargerSimulator(hybrid_send, log_cb, cid_profile=DEMO_CID, params=dict(s1_bms.params))
        s2_bms = VirtualBMS(hybrid_send, dict(self.bms.params), log_cb, cid_profile=SOCKET2_CID)
        s2_chg = ChargerSimulator(hybrid_send, log_cb, cid_profile=SOCKET2_CID, params=dict(s2_bms.params))
        for node in (s1_bms, s1_chg, s2_bms, s2_chg):
            vbus.subscribe(node.on_message)
        runtime = MultiSessionRuntime([
            {'label': 'Socket 1', 'node': s1_bms, 'charger': s1_chg, 'cid': DEMO_CID},
            {'label': 'Socket 2', 'node': s2_bms, 'charger': s2_chg, 'cid': SOCKET2_CID},
        ], log_cb=log_cb)
        return runtime, vbus, runtime, 'demo_dual_hw', hw_bus

    def _make_dual_real_runtime(self, bustype: str, iface: str, role: str):
        hw_bus = HardwareBus(iface, bustype, 250000)
        vbus = VirtualBus()

        def bus_send(cid, data):
            vbus.log_frame(cid, data, channel='hw-tx')
            hw_bus.send(cid, data)

        log_cb = self.bms.log if hasattr(self.bms, 'log') else None
        sessions = []
        if role == 'bms':
            s1 = VirtualBMS(bus_send, dict(self.bms.params), log_cb, cid_profile=DEMO_CID)
            s2 = VirtualBMS(bus_send, dict(self.bms.params), log_cb, cid_profile=SOCKET2_CID)

            def on_hw_message(cid, data):
                vbus.log_frame(cid, data, channel='hw-rx')
                s1.on_message(cid, data)
                s2.on_message(cid, data)

            hw_bus.subscribe(on_hw_message)
            sessions = [
                {'label': 'Socket 1', 'node': s1, 'charger': None, 'cid': DEMO_CID},
                {'label': 'Socket 2', 'node': s2, 'charger': None, 'cid': SOCKET2_CID},
            ]
            runtime = MultiSessionRuntime(sessions, log_cb=log_cb)
            return runtime, vbus, None, 'real_bms_dual', hw_bus
        else:
            s1 = ChargerSimulator(bus_send, log_cb, cid_profile=DEMO_CID, params=dict(self.bms.params))
            s2 = ChargerSimulator(bus_send, log_cb, cid_profile=SOCKET2_CID, params=dict(self.bms.params))

            def on_hw_message(cid, data):
                vbus.log_frame(cid, data, channel='hw-rx')
                s1.on_message(cid, data)
                s2.on_message(cid, data)

            hw_bus.subscribe(on_hw_message)
            sessions = [
                {'label': 'Socket 1', 'node': None, 'charger': s1, 'cid': DEMO_CID},
                {'label': 'Socket 2', 'node': None, 'charger': s2, 'cid': SOCKET2_CID},
            ]
            runtime = MultiSessionRuntime(sessions, log_cb=log_cb)
            return runtime, vbus, runtime, 'real_charger_dual', hw_bus

    def _activate_runtime(self, node, vbus, charger, mode, hw_bus=None, iface=None, bustype=None, role=None, profile_key=None):
        self._close_hardware()
        self.bms = node
        self.vbus = vbus
        self.charger_sim = charger
        self.session_mode = mode
        self.hw_bus = hw_bus
        self.iface = iface
        if bustype:
            self.current_bustype = bustype
        if role:
            self.current_role = role
        if profile_key:
            self.current_profile_key = profile_key
        self.current_cid = getattr(node, 'cid', DEMO_CID)
        self.current_profiles = getattr(node, 'cid_profiles', [self.current_cid])
        self.validator.reset()
        self._mode_text.set(f"Mode: {mode.replace('_', ' ').title()}")
        self._iface_text.set(f"Interface: {iface or 'internal'}")
        self._profile_text.set(f"Topology: {PROFILE_OPTIONS[self.current_profile_key][0]}")
        if hasattr(self, '_tool_var') and bustype:
            self._tool_var.set('vector' if bustype == 'vector' else 'peak')
        if hasattr(self, '_iface_var'):
            self._iface_var.set(iface or ('0' if self._tool_var.get() == 'vector' else 'PCAN_USBBUS1'))
        if hasattr(self, '_role_var') and role in ('bms', 'charger'):
            self._role_var.set(role)
        if hasattr(self, '_profile_var'):
            self._profile_var.set(self._profile_labels[self.current_profile_key])

    def _init_sequence_diagram(self):
        diagram = """
  GB/T 27930  Charging Sequence  (J1939 TP  for multi-frame)
  ─────────────────────────────────────────────────────────────
  CHARGER (0x55/0x56)          BMS (0xF5/0xF4)
       │                           │
       │────── CHM (250ms) ───────▶│  Handshake
       │◀───── BHM ────────────────│
       │                           │
       │────── CRM (recognized) ──▶│  Recognition
       │◀═══ TPCM(BAM)+TPDT ═════│  BRM (49B multi-packet)
       │                           │
       │────── CTS ───────────────▶│  Time Sync
       │◀═══ TPCM(RTS)+CTS+TPDT ═│  BCP (13B multi-packet)
       │                           │
       │────── CML ───────────────▶│  Charger Max Limits
       │◀───── BRO (ready=0xAA) ───│
       │────── CRO (ready=0xAA) ──▶│
       │                           │
       │────── CCS (250ms) ───────▶│  ╔══════════════╗
       │◀───── BCL (50ms) ─────────│  ║  CHARGING    ║
       │◀───── BCS (250ms) ────────│  ║  PHASE       ║
       │◀───── BSM (250ms) ────────│  ╚══════════════╝
       │                           │
       │────── CST ───────────────▶│  Stop
       │◀───── BST ────────────────│
       │◀───── BSD ────────────────│  (BSD now fires off CST, not CSD)
       │────── CSD ───────────────▶│
       │                           │
  ─────────────────────────────────────────────────────────────
  TP.CM Byte[0]:  0x10=RTS  0x11=CTS  0x13=EOM  0x20=BAM
  TP.DT Byte[0]:  Sequence number (1..N)
"""
        self.seq_view.configure(state='normal')
        self.seq_view.insert('end', diagram)
        self.seq_view.configure(state='disabled')

    # ── Bus monitor ───────────────────────────────────────
    def _start_bus_monitor(self):
        self._bus_thread = threading.Thread(target=self._bus_loop, daemon=True)
        self._bus_thread.start()

    def _bus_loop(self):
        while True:
            msg = self.vbus.get_log(timeout=0.1)
            if msg:
                self.root.after(0, self._log_can_msg, msg)

    def _log_can_msg(self, msg):
        # "Demo on CAN" mirrors each frame to hardware and also republishes it on
        # the internal demo bus. Show only the hardware-side copy in the GUI to
        # avoid double-printing every frame.
        if self.session_mode == 'demo_hw' and msg.get('ch') == 'demo':
            return
        cid  = msg['id']
        data = msg['data']
        ts   = msg['ts']
        name, tag = self._tp_name(cid, data) or self._id_to_name(cid)
        line = (f"{ts:12.3f}  0x{cid:08X}  [{name:6s}]"
                f"  {data.hex(' ').upper():30s}\n")
        self.can_log.configure(state='normal')
        self.can_log.insert('end', line, tag)
        self.can_log.see('end')
        self.can_log.configure(state='disabled')
        # Record for validator
        logical_name = name.split('.', 1)[0] if '.' in name else name
        self.validator.record(logical_name, ts)

    def _pgn_to_name(self, pgn: int) -> str:
        names = {
            PGN._BRM: 'BRM',
            PGN._BCP: 'BCP',
            PGN._BCS: 'BCS',
            PGN._BSD: 'BSD',
        }
        return names.get(pgn, f"PGN{pgn:04X}")

    def _tp_name(self, cid: int, data: bytes) -> tuple[str, str] | None:
        m = cid & 0x1FFFFFFF
        pf = (m >> 16) & 0xFF
        if pf not in (0xEC, 0xEB):
            return None
        sa = m & 0xFF
        da = (m >> 8) & 0xFF
        if pf == 0xEC and len(data) >= 8:
            ctrl = data[0]
            pgn = data[5] | (data[6] << 8) | (data[7] << 16)
            logical = self._pgn_to_name(pgn)
            if ctrl in (J1939_TP.CM_BAM, J1939_TP.CM_RTS):
                self._tp_log_sessions[(sa, da)] = pgn
            elif ctrl in (J1939_TP.CM_EOM, J1939_TP.CM_ABORT):
                self._tp_log_sessions.pop((da, sa), None)
            ctrl_name = {
                J1939_TP.CM_BAM: 'BAM',
                J1939_TP.CM_RTS: 'RTS',
                J1939_TP.CM_CTS: 'CTS',
                J1939_TP.CM_EOM: 'EOM',
                J1939_TP.CM_ABORT: 'ABORT',
            }.get(ctrl, 'CM')
            return f"{logical}.{ctrl_name}", 'TPCM'
        if pf == 0xEB:
            pgn = self._tp_log_sessions.get((sa, da))
            if pgn is None:
                pgn = self._tp_log_sessions.get((sa, 0xFF))
            if pgn is None:
                return 'TPDT', 'TPDT'
            return f"{self._pgn_to_name(pgn)}.DT", 'TPDT'
        return None

    def _id_to_name(self, cid: int) -> tuple[str, str]:
        m = cid & 0x1FFFFFFF
        pf = (m >> 16) & 0xFF
        sa = m & 0xFF
        for cidp in getattr(self, 'current_profiles', [getattr(self, 'current_cid', DEMO_CID)]):
            sa_chg = getattr(cidp, 'SA_CHARGER', SA_CHARGER)
            sa_bms = getattr(cidp, 'SA_BMS', SA_BMS)
            if pf == 0x26 and sa == sa_chg: return 'CHM', 'CHM'
            if pf == 0x27 and sa == sa_bms: return 'BHM', 'BHM'
            if m == cidp.CRM or (sa == sa_chg and pf == 0x01): return 'CRM', 'INFO'
            if m == cidp.CTS: return 'CTS', 'INFO'
            if m == cidp.CML: return 'CML', 'INFO'
            if m == cidp.CRO: return 'CRO', 'INFO'
            if m == cidp.CST: return 'CST', 'INFO'
            if m == cidp.CSD: return 'CSD', 'INFO'
            if m == cidp.CCS or pf == 0x12: return 'CCS', 'CCS'
            if m == cidp.BRO or (sa == sa_bms and pf == 0x09): return 'BRO', 'INFO'
            if m == cidp.BCL or (sa == sa_bms and pf == 0x10): return 'BCL', 'BCL'
            if m == cidp.BCS or (sa == sa_bms and pf == 0x11): return 'BCS', 'BCS'
            if m == cidp.BSM or (sa == sa_bms and pf == 0x13): return 'BSM', 'BSM'
            if m == cidp.BST or (sa == sa_bms and pf == 0x19): return 'BST', 'INFO'
            if m == cidp.BSD or (sa == sa_bms and pf == 0x1C): return 'BSD', 'INFO'
        return f"0x{pf:02X}", 'INFO'

    # ── Controls ──────────────────────────────────────────
    def _apply_params(self):
        p = {}
        for k, v in self._params.items():
            try:
                p[k] = float(v.get())
            except ValueError:
                p[k] = 0.0
        if hasattr(self.bms, 'apply_params'):
            self.bms.apply_params(p)
            self._apply_faults()
            return
        if hasattr(self.bms, 'params'):
            self.bms.params.update(p)
        if hasattr(self.bms, 'msgs'):
            self.bms.msgs.p = self.bms.params
        if hasattr(self.bms, 'sim_soc'):
            self.bms.sim_soc = p.get('soc', 20.0)
        if hasattr(self.bms, 'sim_pack_v'):
            self.bms.sim_pack_v = p.get('pack_voltage', 560.0)
        self._apply_faults()

    def _apply_faults(self):
        if not self.charger_sim or not hasattr(self, '_fault_vars'):
            return
        self.charger_sim.set_faults({k: v.get() for k, v in self._fault_vars.items()})

    def _start_demo(self):
        self._apply_params()
        profile_key, (profile_name, cid_profile) = self._selected_profile()
        if profile_key == 'dual':
            node, vbus, charger, mode = self._make_dual_demo_runtime()
        else:
            node, vbus, charger, mode = self._make_demo_runtime(cid_profile)
        self._activate_runtime(node, vbus, charger, mode, profile_key=profile_key)
        self._apply_params()
        self._apply_faults()
        if self.charger_sim:
            self.charger_sim.start()
        self._append_can_log(f"──── DEMO MODE STARTED ({profile_name}) ────\n", 'INFO')

    def _start_demo_on_can(self):
        self._apply_params()
        profile_key, (profile_name, cid_profile) = self._selected_profile()
        bustype = 'vector' if self._tool_var.get().lower() == 'vector' else 'pcan'
        iface = self._iface_var.get().strip()
        if not iface:
            self._append_can_log("Select a CAN channel before starting demo on CAN.\n", 'VIOL')
            return
        try:
            if profile_key == 'dual':
                node, vbus, charger, mode, hw_bus = self._make_dual_demo_can_runtime(bustype, iface)
            else:
                node, vbus, charger, mode, hw_bus = self._make_demo_can_runtime(bustype, iface, cid_profile)
        except Exception as exc:
            self._append_can_log(f"Demo on CAN start failed: {exc}\n", 'VIOL')
            return
        self._activate_runtime(node, vbus, charger, mode, hw_bus=hw_bus, iface=iface, bustype=bustype, role='demo', profile_key=profile_key)
        self._apply_params()
        self._apply_faults()
        if self.charger_sim:
            self.charger_sim.start()
        self._append_can_log(f"──── DEMO ON CAN: {profile_name} mirrored to {self._tool_var.get()} {iface} ────\n", 'INFO')

    def _start_simulate_bms(self):
        self._role_var.set('bms')
        self._start_real()

    def _start_simulate_charger(self):
        self._role_var.set('charger')
        self._start_real()

    def _start_real(self):
        self._apply_params()
        profile_key, (profile_name, cid_profile) = self._selected_profile()
        bustype = 'vector' if self._tool_var.get().lower() == 'vector' else 'pcan'
        iface = self._iface_var.get().strip()
        role = self._role_var.get().strip() or 'bms'
        if not iface:
            self._append_can_log("Select a CAN channel before starting hardware mode.\n", 'VIOL')
            return
        try:
            if profile_key == 'dual':
                node, vbus, charger, mode, hw_bus = self._make_dual_real_runtime(bustype, iface, role)
            else:
                node, vbus, charger, mode, hw_bus = self._make_real_runtime(bustype, iface, role, cid_profile)
        except Exception as exc:
            self._append_can_log(f"Hardware start failed: {exc}\n", 'VIOL')
            return
        self._activate_runtime(node, vbus, charger, mode, hw_bus=hw_bus, iface=iface, bustype=bustype, role=role, profile_key=profile_key)
        self._apply_params()
        self._apply_faults()
        if role == 'charger' and self.charger_sim:
            self.charger_sim.start()
            self._append_can_log(f"──── SIMULATE CHARGER: {profile_name} on {self._tool_var.get()} {iface} ────\n", 'INFO')
        else:
            self._append_can_log(f"──── SIMULATE BMS: {profile_name} on {self._tool_var.get()} {iface} ────\n", 'INFO')

    def _stop(self):
        if self.charger_sim and hasattr(self.charger_sim, 'stop'):
            self.charger_sim.stop()
        if hasattr(self.bms, '_stop_periodic'):
            self.bms._stop_periodic()
        if hasattr(self.bms, 'stop'):
            self.bms.stop()
        self._close_hardware()
        self._update_violations()

    def _stop_from_bms(self):
        if hasattr(self.bms, 'request_stop_from_bms'):
            self.bms.request_stop_from_bms()
            self._append_can_log("Manual stop requested from all BMS sides.\n", 'INFO')
            return
        if hasattr(self.bms, 'request_stop'):
            self.bms.request_stop(0x01)
            self._append_can_log("Manual stop requested from BMS side.\n", 'INFO')

    def _stop_from_charger(self):
        if self.charger_sim and hasattr(self.charger_sim, 'request_stop_from_charger'):
            self.charger_sim.request_stop_from_charger()
            self._append_can_log("Manual stop requested from all charger sides.\n", 'INFO')
            return
        if self.charger_sim and hasattr(self.charger_sim, 'request_stop'):
            self.charger_sim.request_stop(0x01)
            self._append_can_log("Manual stop requested from charger side.\n", 'INFO')

    def _append_can_log(self, text: str, tag: str = ''):
        self.can_log.configure(state='normal')
        self.can_log.insert('end', text, tag)
        self.can_log.see('end')
        self.can_log.configure(state='disabled')

    def _update_violations(self):
        self.viol_log.configure(state='normal')
        self.viol_log.delete('1.0', 'end')
        if not self.bms.violations:
            self.viol_log.insert('end', "No violations detected\n")
        else:
            for v in self.bms.violations:
                self.viol_log.insert('end', v + '\n')
        self.viol_log.insert('end', '\n' + self.validator.full_report())
        self.viol_log.configure(state='disabled')

    def _export_report(self):
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            defaultextension='.txt',
            filetypes=[('Text', '*.txt'), ('All', '*.*')],
            title='Save Validation Report')
        if filename:
            with open(filename, 'w') as f:
                f.write("GB/T 27930 BMS Validator Report\n")
                f.write(f"Generated: {datetime.datetime.now()}\n\n")
                f.write("=== VIOLATIONS ===\n")
                for v in self.bms.violations:
                    f.write(v + '\n')
                f.write("\n=== EVENT LOG ===\n")
                for e in self.bms.event_log:
                    f.write(e + '\n')
                f.write("\n=== TIMING ANALYSIS ===\n")
                f.write(self.validator.full_report())
            self._append_can_log(f"Report saved to {filename}\n", 'INFO')

    def _update_stats_view(self):
        lines = []
        status = self.bms.get_status()
        lines.append("Session Summary")
        lines.append("=" * 60)
        lines.append(f"Mode      : {self.session_mode}")
        lines.append(f"Topology  : {PROFILE_OPTIONS[self.current_profile_key][0]}")
        lines.append(f"State     : {status['state']}")
        lines.append(f"SOC       : {status['soc']:.1f}%")
        lines.append(f"Pack V    : {status['pack_v']:.1f} V")
        lines.append(f"Current   : {status['current']:.1f} A")
        lines.append(f"Violations: {status['violations']}")
        if hasattr(self.bms, 'get_socket_statuses'):
            lines.append("")
            lines.append("Per Socket")
            lines.append("-" * 60)
            for label, sock in self.bms.get_socket_statuses().items():
                lines.append(
                    f"{label:8s}  state={sock['state']:12s}  soc={sock['soc']:5.1f}%  "
                    f"v={sock['pack_v']:7.1f}V  i={sock['current']:7.1f}A  viol={sock['violations']}"
                )
        self.stat_view.configure(state='normal')
        self.stat_view.delete('1.0', 'end')
        self.stat_view.insert('end', "\n".join(lines))
        self.stat_view.configure(state='disabled')

    # ── Refresh loop ──────────────────────────────────────
    def _refresh_loop(self):
        status = self.bms.get_status()
        st = status['state']
        state_colors = {
            'IDLE':     COLORS['subtext'],
            'HANDSHAKE':COLORS['yellow'],
            'RECOGNITION':COLORS['yellow'],
            'PARAMETER':COLORS['yellow'],
            'READY':    COLORS['green'],
            'CHARGING': COLORS['charging'],
            'STOPPING': COLORS['accent'],
            'STOP_DONE':COLORS['green'],
            'ERROR':    COLORS['error'],
        }
        self.state_lbl.config(text=st,
                               fg=state_colors.get(st, COLORS['text']))

        self._status_vars['state'].set(st)
        self._status_vars['soc'].set(f"{status['soc']:.1f}%")
        self._status_vars['pack_v'].set(f"{status['pack_v']:.1f} V")
        self._status_vars['current'].set(f"{status['current']:.1f} A")
        self._status_vars['cell_v'].set(f"{status['cell_v']:.3f} V")
        self._status_vars['temp'].set(f"{status['temp']:.1f} C")
        n_v = status['violations']
        self._status_vars['violations'].set(
            f"{n_v} alerts" if n_v else "0 OK")

        # Auto-update violations tab
        if n_v:
            self._update_violations()
        self._update_stats_view()

        self.root.after(500, self._refresh_loop)


# ============================================================
# Hardware CAN adapter (python-can)
# ============================================================
class HardwareBus:
    def __init__(self, interface: str, bustype: str, bitrate: int = 250000):
        global can, HAS_CAN, CAN_IMPORT_ERROR
        if not HAS_CAN:
            try:
                can = importlib.import_module('can')
                HAS_CAN = True
                CAN_IMPORT_ERROR = ""
            except Exception as e:
                raise RuntimeError(
                    f"python-can import failed in {sys.executable}: {e}"
                ) from e
        self.bus = can.interface.Bus(channel=interface, bustype=bustype,
                                     bitrate=bitrate)
        self._subs = []

    def send(self, can_id: int, data: bytes):
        msg = can.Message(arbitration_id=can_id, data=data,
                          is_extended_id=True, is_fd=False)
        self.bus.send(msg)

    def subscribe(self, cb):
        self._subs.append(cb)
        t = threading.Thread(target=self._rx_loop, args=(cb,), daemon=True)
        t.start()

    def _rx_loop(self, cb):
        for msg in self.bus:
            try:
                cb(msg.arbitration_id, bytes(msg.data))
            except Exception:
                pass

    def shutdown(self):
        try:
            self.bus.shutdown()
        except Exception:
            pass


# ============================================================
# MAIN
# ============================================================
def main():
    parser = argparse.ArgumentParser(description='GB/T 27930 BMS Validator')
    parser.add_argument('--iface',   default=None,       help='CAN interface (e.g. vcan0, can0)')
    parser.add_argument('--bustype', default='socketcan', help='python-can bustype')
    parser.add_argument('--bitrate', default=250000, type=int)
    parser.add_argument('--role',    default='bms', choices=['bms', 'charger'],
                        help='Virtual endpoint role on hardware CAN')
    parser.add_argument('--no-gui',  action='store_true', help='Text-only mode')
    args = parser.parse_args()

    # Default BMS parameters (from real JSW GTL SIDV truck)
    bms_params = {
        'pack_voltage':         560.0,
        'max_total_voltage':    700.0,
        'pack_capacity':        200.0,
        'soc':                  20.0,
        'target_soc':           80.0,
        'cell_max_v':           3.65,
        'cell_max_v_now':       3.30,
        'max_charge_cur':       250.0,
        'nominal_energy':       112.0,
        'nominal_voltage':      560.0,
        'max_temp':             45.0,
        'temp_max_now':         30.0,
        'charge_current_demand': -100.0,
        'battery_type':         0x01,
        'battery_vendor_id':    0x01,
    }

    log_q = queue.Queue()
    def log_cb(msg):
        log_q.put(msg)
        if args.no_gui:
            print(msg)

    # Select bus
    if args.iface and HAS_CAN:
        print(f"Using hardware CAN: {args.iface} ({args.bustype}) as virtual {args.role}")
        hw_bus = HardwareBus(args.iface, args.bustype, args.bitrate)
        vbus = VirtualBus()
        def bus_send(cid, data):
            vbus.log_frame(cid, data, channel='hw-tx')
            hw_bus.send(cid, data)
        if args.role == 'bms':
            bms  = VirtualBMS(bus_send, bms_params, log_cb, cid_profile=REAL_CID)
            def on_hw_message(cid, data):
                vbus.log_frame(cid, data, channel='hw-rx')
                bms.on_message(cid, data)
            hw_bus.subscribe(on_hw_message)
            charger_sim = None
            session_mode = 'real_bms'
            status_node = bms
        else:
            charger_sim = ChargerSimulator(bus_send, log_cb, cid_profile=DEMO_CID, params=bms_params)
            def on_hw_message(cid, data):
                vbus.log_frame(cid, data, channel='hw-rx')
                charger_sim.on_message(cid, data)
            hw_bus.subscribe(on_hw_message)
            bms = charger_sim
            session_mode = 'real_charger'
            status_node = charger_sim
    else:
        print("Using virtual internal bus (Demo mode)")
        vbus = VirtualBus()
        bms  = VirtualBMS(vbus.send, bms_params, log_cb, cid_profile=DEMO_CID)
        charger_sim = ChargerSimulator(vbus.send, log_cb, cid_profile=DEMO_CID, params=bms_params)
        vbus.subscribe(bms.on_message)
        vbus.subscribe(charger_sim.on_message)
        session_mode = 'demo'
        status_node = bms

    if args.no_gui or not HAS_TK:
        print("Text mode – monitoring bus")
        if charger_sim and session_mode in ('demo', 'real_charger'):
            charger_sim.start()
        try:
            while True:
                try:
                    msg = log_q.get(timeout=1)
                    print(msg)
                except queue.Empty:
                    s = status_node.get_status()
                    print(f"\rState={s['state']:12s} SOC={s['soc']:5.1f}% "
                          f"V={s['pack_v']:6.1f}V I={s['current']:6.1f}A "
                          f"Violations={s['violations']}", end='', flush=True)
        except KeyboardInterrupt:
            print("\nStopped.")
    else:
        root = tk.Tk()
        app  = BMS_ValidatorGUI(root, status_node, vbus, charger_sim, session_mode, args.iface,
                               args.bustype, args.role)
        root.mainloop()


if __name__ == '__main__':
    main()