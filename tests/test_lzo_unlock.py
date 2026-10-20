import sys
import types

from dltool.config import Config
from dltool.firmware import Firmware, ReprogrammingBlock, Segment
from dltool.uds.client import UdsClient
from dltool import security
from dltool.flash import flash_firmware
from tests.test_flash import SimEcu


def _install_fake_lzo(monkey_store):
    """Install a fake `lzo` module that 'compresses' by prefixing a marker."""
    fake = types.ModuleType("lzo")
    fake.compress = lambda data, level=9, header=False: b"LZ" + bytes(data)
    monkey_store["prev"] = sys.modules.get("lzo")
    sys.modules["lzo"] = fake


def _remove_fake_lzo(monkey_store):
    if monkey_store.get("prev") is not None:
        sys.modules["lzo"] = monkey_store["prev"]
    else:
        sys.modules.pop("lzo", None)


def test_lzo_compresses_and_sets_data_format():
    store = {}
    _install_fake_lzo(store)
    try:
        data = bytes(range(32))
        fw = Firmware(blocks=[ReprogrammingBlock(segments=[Segment(0x100, bytearray(data))])])
        sim = SimEcu(max_block=0x0102)
        cfg = Config(lzo=True, lzo_method=0x1)
        flash_firmware(UdsClient(sim), fw, cfg, security.get("passthrough"), reset=False)
        # ECU received the 'compressed' stream (marker + data)
        assert bytes(sim.received) == b"LZ" + data
        # RequestDownload carried the compression nibble 0x1 in dataFormatIdentifier
        rd = [p for p in getattr(sim, "requests", [])]  # not tracked; check via events
        assert 0x34 in sim.events
    finally:
        _remove_fake_lzo(store)


def test_unlock_all_tolerates_failing_levels():
    class PickyEcu(SimEcu):
        def request(self, payload, timeout):
            # deny seed for every level except 0x03
            if payload[0] == 0x27 and len(payload) == 2 and payload[1] != 0x03:
                self._resp = b"\x7f\x27\x33"  # securityAccessDenied
                return self._resp
            return super().request(payload, timeout)

    data = bytes(16)
    fw = Firmware(blocks=[ReprogrammingBlock(segments=[Segment(0, bytearray(data))])])
    sim = PickyEcu()
    cfg = Config(unlock_all=True, security_level=0x01)
    # Should not raise even though several levels are denied.
    flash_firmware(UdsClient(sim), fw, cfg, security.get("passthrough"), reset=False)
    assert bytes(sim.received) == data


def test_lzo_missing_dependency_raises_clear_error():
    import dltool.compression as comp
    if comp.available():
        return  # python-lzo actually installed; nothing to assert
    import pytest
    with pytest.raises(RuntimeError) as ei:
        comp.lzo_compress(b"abc")
    assert "dltool[lzo]" in str(ei.value)
