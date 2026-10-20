"""Flash-download orchestration.

Implements the standard UDS reprogramming sequence used to download a
firmware block into an ECU:

    1. Enter extended/programming session
    2. SecurityAccess unlock
    3. (optional) RoutineControl erase
    4. Per segment: RequestDownload -> TransferData* -> RequestTransferExit
    5. (optional) RoutineControl check-dependencies
    6. ECUReset

TesterPresent is sent in the background to keep the session alive.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Callable, Optional

from .config import Config
from .firmware import Firmware, ReprogrammingBlock, Segment
from .uds.client import UdsClient
from .uds.services import ResetType, RoutineControlType, Session

log = logging.getLogger("dltool.flash")

ProgressCb = Callable[[str, int, int], None]  # (label, done, total)


class _TesterPresentLoop:
    """Background thread sending TesterPresent (suppressed response)."""

    def __init__(self, client: UdsClient, interval: float):
        self._client = client
        self._interval = interval
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def _run(self) -> None:
        while not self._stop.wait(self._interval):
            try:
                with self._lock:
                    self._client.tester_present(suppress_response=True)
            except Exception as exc:  # noqa: BLE001
                log.debug("tester-present failed: %s", exc)

    def start(self) -> None:
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=1.0)

    @property
    def lock(self) -> threading.Lock:
        return self._lock


def flash_segment(
    client: UdsClient,
    segment: Segment,
    cfg: Config,
    *,
    progress: Optional[ProgressCb] = None,
) -> None:
    """RequestDownload + TransferData* + RequestTransferExit for one segment."""
    payload_data = bytes(segment.data)
    data_format = cfg.data_format
    if cfg.lzo:
        from .compression import lzo_compress
        payload_data = lzo_compress(payload_data)
        data_format = ((cfg.lzo_method & 0xF) << 4) | (cfg.encryption & 0xF)
        log.info("LZO: segment %d -> %d bytes compressed", segment.size, len(payload_data))
    # ISO 14229 memorySize is the uncompressed size even when compression is used.
    max_block = client.request_download(
        segment.start_addr,
        segment.size,
        addr_len=cfg.addr_len,
        size_len=cfg.size_len,
        data_format=data_format,
    )
    # The server's maxNumberOfBlockLength includes the service+counter bytes;
    # reserve 2 for SID+blockSequenceCounter. Honour the configured cap too.
    chunk = max(1, min(cfg.block_size, (max_block - 2) if max_block > 2 else cfg.block_size))
    log.info("segment @0x%08X size=%d: block=%d (ecu max=%d)",
             segment.start_addr, segment.size, chunk, max_block)

    counter = 1
    sent = 0
    data = payload_data
    for off in range(0, len(data), chunk):
        client.transfer_data(counter, data[off:off + chunk])
        counter = (counter + 1) & 0xFF
        if counter == 0:
            counter = 1  # block sequence counter wraps 0xFF -> 0x01 (never 0)
        sent = min(len(data), off + chunk)
        if progress:
            progress(f"0x{segment.start_addr:08X}", sent, len(data))
    client.request_transfer_exit()


def flash_block(
    client: UdsClient,
    block: ReprogrammingBlock,
    cfg: Config,
    *,
    progress: Optional[ProgressCb] = None,
    erase_routine: Optional[int] = None,
) -> None:
    """Flash all segments of one reprogramming block."""
    if erase_routine is not None:
        log.info("erase routine 0x%04X", erase_routine)
        start = block.start_addr or 0
        size = block.total_size
        client.routine_control(
            erase_routine,
            RoutineControlType.START,
            start.to_bytes(cfg.addr_len, "big") + size.to_bytes(cfg.size_len, "big"),
        )
    for seg in block.segments:
        flash_segment(client, seg, cfg, progress=progress)


def flash_firmware(
    client: UdsClient,
    firmware: Firmware,
    cfg: Config,
    key_fn: Callable[[bytes], bytes],
    *,
    progress: Optional[ProgressCb] = None,
    erase_routine: Optional[int] = None,
    check_routine: Optional[int] = None,
    reset: bool = True,
) -> None:
    """Run the full reprogramming sequence for a parsed firmware file."""
    tp = _TesterPresentLoop(client, cfg.tester_present_interval)
    try:
        log.info("enter programming session")
        client.diagnostic_session_control(Session.PROGRAMMING)
        tp.start()

        levels = [cfg.security_level]
        if cfg.unlock_all:
            # try every odd request-seed level the ECU might expose
            levels = sorted({cfg.security_level, 0x01, 0x03, 0x05, 0x07, 0x09, 0x11})
        for lvl in levels:
            try:
                log.info("security access level 0x%02X", lvl)
                client.unlock(lvl, key_fn)
            except Exception as exc:  # noqa: BLE001
                if not cfg.unlock_all:
                    raise
                log.warning("security level 0x%02X not unlocked: %s", lvl, exc)

        for block in firmware.blocks:
            log.info("flashing block %r (%d bytes)", block.name, block.total_size)
            flash_block(client, block, cfg, progress=progress, erase_routine=erase_routine)

        if check_routine is not None:
            log.info("check-dependencies routine 0x%04X", check_routine)
            client.routine_control(check_routine, RoutineControlType.START)

        if reset:
            log.info("ECU reset")
            client.ecu_reset(ResetType.HARD)
    finally:
        tp.stop()
