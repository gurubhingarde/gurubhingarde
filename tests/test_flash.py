from dltool.config import Config
from dltool.firmware import Firmware, ReprogrammingBlock, Segment
from dltool.uds.client import UdsClient
from dltool import security
from dltool.flash import flash_firmware


class SimEcu:
    """A minimal UDS server simulating the reprogramming sequence."""

    def __init__(self, max_block=0x0102):
        self.max_block = max_block
        self.received = bytearray()
        self.events = []
        self._resp = b""

    def request(self, payload, timeout):
        sid = payload[0]
        self.events.append(sid)
        if sid == 0x10:   # session control
            self._resp = b"\x50" + payload[1:2] + b"\x00\x32\x01\xf4"
        elif sid == 0x27 and len(payload) == 2:  # seed
            self._resp = b"\x67" + payload[1:2] + b"\x01\x02\x03\x04"
        elif sid == 0x27:  # key
            self._resp = b"\x67" + payload[1:2]
        elif sid == 0x34:  # request download
            self._resp = b"\x74\x20" + self.max_block.to_bytes(2, "big")
        elif sid == 0x36:  # transfer data
            self.received.extend(payload[2:])
            self._resp = b"\x76" + payload[1:2]
        elif sid == 0x37:  # transfer exit
            self._resp = b"\x77"
        elif sid == 0x11:  # ecu reset
            self._resp = b"\x51" + payload[1:2]
        elif sid == 0x3e:  # tester present (suppressed => no resp expected)
            self._resp = b"\x7e\x00"
        else:
            self._resp = b"\x7f" + bytes([sid, 0x11])
        return self._resp

    def receive(self, timeout):
        r, self._resp = self._resp, b""
        return r


def test_flash_firmware_delivers_all_bytes():
    data = bytes(range(256)) * 4   # 1024 bytes
    fw = Firmware(blocks=[ReprogrammingBlock(name="APP",
                  segments=[Segment(0x08000000, bytearray(data))])])
    sim = SimEcu(max_block=0x0102)  # => 0x100 payload per block
    cfg = Config(block_size=0x400, tester_present_interval=999)
    client = UdsClient(sim)

    flash_firmware(client, fw, cfg, security.get("passthrough"), reset=True)

    assert bytes(sim.received) == data
    assert 0x10 in sim.events and 0x27 in sim.events
    assert 0x34 in sim.events and 0x36 in sim.events and 0x37 in sim.events
    assert 0x11 in sim.events  # reset at the end


def test_block_size_respects_ecu_max():
    data = bytes(500)
    fw = Firmware(blocks=[ReprogrammingBlock(segments=[Segment(0, bytearray(data))])])
    sim = SimEcu(max_block=0x0102)  # 258 => usable payload 256
    cfg = Config(block_size=0x400)
    flash_firmware(UdsClient(sim), fw, cfg, security.get("passthrough"), reset=False)
    assert bytes(sim.received) == data
