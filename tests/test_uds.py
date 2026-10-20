import pytest

from dltool.uds.client import UdsClient, NegativeResponse
from dltool.uds.services import NRC, ServiceId
from dltool import security


class FakeTransport:
    """Scripted transport: maps a request to a queued list of responses."""

    def __init__(self):
        self.script = []          # list of (matcher, [responses...])
        self.sent = []
        self._pending = []

    def expect(self, prefix: bytes, *responses: bytes):
        self.script.append((prefix, list(responses)))
        return self

    def request(self, payload, timeout):
        self.sent.append(payload)
        for prefix, responses in self.script:
            if payload.startswith(prefix):
                self._pending = responses[1:]
                return responses[0]
        raise AssertionError(f"no scripted response for {payload.hex()}")

    def receive(self, timeout):
        return self._pending.pop(0) if self._pending else b""


def test_positive_and_negative():
    t = FakeTransport()
    t.expect(b"\x10\x03", b"\x50\x03\x00\x32\x01\xf4")   # session control OK
    t.expect(b"\x27\x01", b"\x7f\x27\x33")               # security denied
    c = UdsClient(t)
    assert c.diagnostic_session_control(0x03)[0] == 0x50
    with pytest.raises(NegativeResponse) as ei:
        c.security_access_request_seed(0x01)
    assert ei.value.nrc == NRC.SECURITY_ACCESS_DENIED


def test_response_pending_then_final():
    t = FakeTransport()
    # 0x78 pending, then the real positive response
    t.expect(b"\x22\xf1\x90",
             b"\x7f\x22\x78",
             b"\x62\xf1\x90WVWZZZ")
    c = UdsClient(t)
    val = c.read_data_by_identifier(0xF190)
    assert val == b"WVWZZZ"


def test_request_download_block_length():
    t = FakeTransport()
    # 0x74 | lengthFormat(0x20 => 2 length bytes) | maxBlock=0x0402
    t.expect(b"\x34", b"\x74\x20\x04\x02")
    c = UdsClient(t)
    max_block = c.request_download(0x08000000, 1024, addr_len=4, size_len=4)
    assert max_block == 0x0402
    # ALFID byte must encode size_len<<4 | addr_len
    sent = t.sent[-1]
    assert sent[0] == ServiceId.REQUEST_DOWNLOAD
    assert sent[2] == (4 << 4) | 4


def test_security_unlock_handshake():
    t = FakeTransport()
    t.expect(b"\x27\x01", b"\x67\x01\x11\x22\x33\x44")   # seed
    t.expect(b"\x27\x02", b"\x67\x02")                   # key accepted
    c = UdsClient(t)
    key_fn = security.xor_key(b"\xff\xff")
    c.unlock(0x01, key_fn)
    # the key sent must be seed XOR ffff repeated
    key_sent = t.sent[-1][2:]
    assert key_sent == bytes(b ^ 0xFF for b in b"\x11\x22\x33\x44")


def test_unlock_already_unlocked_sends_no_key():
    t = FakeTransport()
    t.expect(b"\x27\x01", b"\x67\x01\x00\x00\x00\x00")   # zero seed => unlocked
    c = UdsClient(t)
    c.unlock(0x01, lambda s: b"\xde\xad")
    assert all(not s.startswith(b"\x27\x02") for s in t.sent)
