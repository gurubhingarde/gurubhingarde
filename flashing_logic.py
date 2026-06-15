import os
import time
import zlib
from intelhex import IntelHex

# -----------------------------
# CAN / UDS constants
# -----------------------------
TX_ID = 0xB00D0D9  # Tester → ECU
RX_ID = 0xB00D9D0  # ECU → Tester
CHUNK_SIZE = 3200  # UDS block size

# -----------------------------
# CAN wrapper
# -----------------------------
class CANBusWrapper:
    def __init__(self, interface, channel=0, bitrate=250000):
        self.interface = interface
        self.channel = channel
        self.bitrate = bitrate
        self.pcan = None
        self.bus = None
        if interface == "pcan":
            from PCANBasic import PCANBasic, PCAN_USBBUS1, PCAN_BAUD_250K
            self.pcan = PCANBasic()
            channel_map = [PCAN_USBBUS1]
            pcan_channel = channel_map[channel]
            baudrate_map = {250000: PCAN_BAUD_250K}
            status = self.pcan.Initialize(pcan_channel, baudrate_map[bitrate])
            if status != 0:
                raise RuntimeError("PCAN init failed: %s" % self.pcan.GetErrorText(status)[1])
            self._pcan_channel = pcan_channel
        else:
            import can
            self.bus = can.interface.Bus(interface=interface, channel=channel, bitrate=bitrate)

    def send(self, arbitration_id, data, is_extended_id=True):
        if self.pcan:
            from ctypes import c_ubyte
            from PCANBasic import TPCANMsg, PCAN_MESSAGE_EXTENDED, PCAN_MESSAGE_STANDARD
            msg = TPCANMsg()
            msg.ID = arbitration_id
            msg.LEN = len(data)
            msg.MSGTYPE = PCAN_MESSAGE_EXTENDED if is_extended_id else PCAN_MESSAGE_STANDARD
            data_list = list(data)
            msg.DATA = (c_ubyte * 8)(*(data_list + [0] * (8 - len(data_list))))
            status = self.pcan.Write(self._pcan_channel, msg)
            return status == 0
        else:
            import can
            msg = can.Message(arbitration_id=arbitration_id, data=bytes(data), is_extended_id=is_extended_id)
            self.bus.send(msg)
            return True

    def recv(self, timeout=0.05):
        if self.pcan:
            status, rx_msg, _ = self.pcan.Read(self._pcan_channel)
            if status == 0:
                return {
                    'arbitration_id': rx_msg.ID,
                    'data': list(rx_msg.DATA[:rx_msg.LEN]),
                    'is_extended_id': bool(rx_msg.MSGTYPE & 0x02)
                }
            return None
        else:
            msg = self.bus.recv(timeout=timeout)
            if msg:
                return {
                    'arbitration_id': msg.arbitration_id,
                    'data': list(msg.data),
                    'is_extended_id': msg.is_extended_id
                }
            return None

    def shutdown(self):
        if self.pcan:
            self.pcan.Uninitialize(self._pcan_channel)
        elif self.bus:
            self.bus.shutdown()

# -----------------------------
# Flashing logic
# -----------------------------
class FlashingLogic:
    def __init__(self, interface, channel, bitrate, log_callback=None):
        self.interface = interface if interface != "peak" else "pcan"
        self.channel = channel
        self.bitrate = bitrate
        self.log_callback = log_callback

    def log_write(self, msg):
        print(msg)
        if self.log_callback:
            self.log_callback(msg)

    def clear_log(self, log_path=None):
        if log_path:
            try:
                with open(log_path, "w") as f:
                    f.truncate()
            except Exception:
                pass

    def extract_firmware_data_and_crc(self, path, app_start=None, app_end=None):
        ext = os.path.splitext(path)[1].lower()
        if ext == '.bin':
            with open(path, 'rb') as f:
                data = f.read()
            if app_start is not None and app_end is not None:
                start = app_start
                end = app_end + 1
                if end > len(data):
                    raise ValueError(f"End address 0x{end:X} exceeds file length (0x{len(data):X})")
                data = data[start:end]
            crc32 = zlib.crc32(data) & 0xFFFFFFFF
            return bytearray(data), crc32
        elif ext in ['.hex', '.s19', '.srec', '.mot']:
            ih = IntelHex()
            if ext == '.hex':
                ih.fromfile(path, format='hex')
            else:
                ih.fromfile(path, format='srec')
            min_addr = ih.minaddr()
            max_addr = ih.maxaddr()
            start_addr = app_start if app_start is not None else min_addr
            end_addr = app_end if app_end is not None else max_addr
            data = ih.tobinarray(start=start_addr, end=end_addr)
            crc32 = zlib.crc32(data) & 0xFFFFFFFF
            return bytearray(data), crc32
        else:
            raise ValueError("Unsupported file type: " + ext)

    def split_blocks(self, data, block_size=CHUNK_SIZE):
        return [data[i:i+block_size] for i in range(0, len(data), block_size)]

    def generate_block_headers(self, app_bytes, chunk_size=CHUNK_SIZE+5):
        HEADER_SIZE = 5
        data_payload_size = chunk_size - HEADER_SIZE
        num_blocks = (len(app_bytes) + data_payload_size - 1) // data_payload_size
        block_headers = []
        block_counter_value = 0
        for block_num in range(num_blocks):
            if block_num > 0:
                if (block_num - 1) % 2 == 0:
                    block_counter_value += 12
                else:
                    block_counter_value += 13
            start_idx = block_num * data_payload_size
            end_idx = min(start_idx + data_payload_size, len(app_bytes))
            block_data = app_bytes[start_idx:end_idx]
            first_data_byte = block_data[0] if len(block_data) > 0 else 0x00
            if block_num == num_blocks - 1:
                chunk_length = len(block_data) + HEADER_SIZE
            else:
                chunk_length = chunk_size
            chunk_len_hi = (chunk_length >> 8) & 0x0F
            chunk_len_lo = chunk_length & 0xFF
            byte0 = (0x10 | chunk_len_hi)
            byte1 = chunk_len_lo
            alternator = 0x80 if block_num % 2 == 1 else 0x00
            bc0 = (block_counter_value) & 0xFF
            bc1 = (block_counter_value >> 8) & 0xFF
            bc2 = (block_counter_value >> 16) & 0xFF
            header = [byte0, byte1, 0x36, alternator, bc0, bc1, bc2, first_data_byte]
            block_headers.append(bytearray(header))
        return block_headers

    def send_uds(self, bus, data):
        bus.send(TX_ID, data, is_extended_id=True)
        self.log_write(f"→ Sent: ID=0x{TX_ID:X} Data={bytes(data).hex()}")

    def recv_uds(self, bus, timeout=0.1):
        msg = bus.recv(timeout=timeout)
        if msg and msg['arbitration_id'] == RX_ID:
            self.log_write(f"← Received: ID=0x{msg['arbitration_id']:X} Data={bytes(msg['data']).hex()}")
            return msg['data']
        return None

    def send_until_response(self, bus, data, expected_prefix, timeout=4.0, send_interval=0.01, stop_event=None):
        end_time = time.time() + timeout
        while time.time() < end_time:
            if stop_event is not None and stop_event.is_set():
                self.log_write("⛔ Cancelled by user during session wait")
                return None
            self.send_uds(bus, data)
            t0 = time.time()
            while time.time() - t0 < send_interval:
                msg = self.recv_uds(bus, send_interval)
                if msg and bytes(msg).startswith(expected_prefix):
                    return msg
        self.log_write(f"❌ Timeout: No expected response starting with {expected_prefix.hex()}")
        return None

    def wait_for_response(self, bus, expected_prefix, timeout=4):
        end = time.time() + timeout
        while time.time() < end:
            msg = self.recv_uds(bus, 0.1)
            if msg and bytes(msg).startswith(expected_prefix):
                return msg
        return None

    def enter_programming_session(self, bus, stop_event=None):
        self.log_write("\n▶ Entering Programming Session...")
        session_request = [0x10, 0x0B, 0x10, 0x02, 0x00, 0x00, 0x00, 0x59]
        return self.send_until_response(bus, session_request, b'\x30', timeout=100.0, send_interval=0.01, stop_event=stop_event)

    def send_consecutive_frame(self, bus):
        self.log_write("\n▶ Sending Consecutive Frame...")
        cf = [0x21, 0x56, 0x43, 0x55, 0x02, 0x00, 0x55, 0x55]
        return self.send_until_response(bus, cf, b'\x10\x0A', timeout=4.0, send_interval=0.01)

    def send_flow_control(self, bus):
        self.log_write("\n▶ Sending Flow Control...")
        fc = [0x30, 0x00, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
        return self.send_until_response(bus, fc, b'\x21\x56', timeout=4.0, send_interval=0.01)

    def erase_memory(self, bus):
        self.log_write("\n▶ Erasing Memory...")
        erase_cmd = [0x10, 0x0C, 0x31, 0x01, 0xFF, 0x00, 0xFF, 0xFF]
        if not self.send_until_response(bus, erase_cmd, b'\x30', timeout=4.0, send_interval=0.01):
            return False
        erase2 = [0x21, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x55]
        return self.send_until_response(bus, erase2, b'\x05', timeout=4.0, send_interval=0.01)

    def request_download(self, bus, data):
        self.log_write("\n▶ Requesting Download...")
        req = [0x10, 0x0B, 0x34, 0x00, 0x44, 0xFF, 0xFF, 0xFF]
        if not self.send_until_response(bus, req, b'\x30', timeout=4.0, send_interval=0.01):
            return False
        total_len = len(data)
        len_bytes = total_len.to_bytes(4, 'little')
        req2 = [0x21, 0xFF] + list(len_bytes) + [0x55, 0x55]
        return self.send_until_response(bus, req2, b'\x02\x74\x20', timeout=4.0, send_interval=0.01)

    def wait_for_block_flow(self, bus, timeout=4):
        end = time.time() + timeout
        while time.time() < end:
            msg = self.recv_uds(bus, 0.05)
            if msg and len(msg) == 8 and msg[0] == 0x30 and msg[1] == 0x00 and msg[2] == 0x01 and all(b == 0xAA for b in msg[3:]):
                return True
        self.log_write("❌ Timeout waiting for ECU '30 00 01 AA AA AA AA AA'")
        return False

    def wait_for_block_ack(self, bus, timeout=2):
        t0 = time.time()
        while time.time() - t0 < timeout:
            msg = self.recv_uds(bus, 0.1)
            if msg and msg[0] == 0x05 and msg[1] == 0x76:
                self.log_write(f"✅ Got 05 76 after block")
                return True
        self.log_write("❌ Timeout waiting for 05 76 after block")
        return False

    def send_transfer_data(self, bus, blocks, block_headers, progress_callback=None):
        self.log_write("\n▶ Sending Transfer Data blocks...")
        for block_index, chunk in enumerate(blocks):
            try:
                header = bytearray(block_headers[block_index])
            except IndexError:
                self.log_write(f"❌ No block header defined for block {block_index+1}")
                return False
            header[-1] = chunk[0]
            self.send_uds(bus, header)
            if not self.wait_for_block_flow(bus):
                self.log_write(f"❌ No flow control after block header {block_index+1}")
                return False
            seq = 1
            sent = 1
            while sent < len(chunk):
                data7 = list(chunk[sent:sent+7])
                cf = [0x20 | seq] + data7
                cf += [0xFF] * (8 - len(cf))
                self.send_uds(bus, cf)
                seq = (seq + 1) & 0x0F
                sent += 7
                time.sleep(0)
            self.log_write(f"✅ Block {block_index+1} sent ({len(chunk)} bytes)")
            if not self.wait_for_block_ack(bus):
                self.log_write(f"❌ Timeout waiting for 05 76 after block {block_index+1}")
                return False
            if progress_callback:
                progress_callback("block", block_index+1, len(blocks))
        self.log_write("🎉 All blocks sent!")
        return True

    def send_post_flash_handshake_split_crc(self, bus, crc_value):
        self.log_write("\n▶ Post-flash handshake (split CRC)...")
        def send_and_wait(send_bytes, expect_prefix, step_desc="", timeout=3):
            self.send_uds(bus, send_bytes)
            t0 = time.time()
            while time.time() - t0 < timeout:
                msg = self.recv_uds(bus, 0.05)
                if msg and bytes(msg).startswith(expect_prefix):
                    self.log_write(f"← {step_desc} reply: {bytes(msg).hex()}")
                    return msg
            self.log_write(f"❌ Timeout waiting for {step_desc} (prefix {expect_prefix.hex()})")
            return None

        crc_bytes = crc_value.to_bytes(4, 'big')
        crc_hi = list(crc_bytes[:2])
        crc_lo = list(crc_bytes[2:])
        if not send_and_wait([0x01, 0x37] + [0x55]*6, b'\x01\x77', "Step 1"):
            return False
        msg2 = [0x10, 0x08, 0x32, 0x01, 0x02, 0x02] + crc_hi
        if not send_and_wait(msg2, b'\x30\x00\x01', "Step 2"):
            return False
        msg3 = [0x21] + crc_lo + [0x55]*5
        if not send_and_wait(msg3, b'\x05\x72', "Step 3"):
            return False
        if not send_and_wait([0x02, 0x11, 0x01] + [0x55]*5, b'\x02\x51', "Step 4"):
            return False
        self.log_write("✅ Post-flash handshake completed!")
        return True

    def flash_firmware(self, firmware_path, app_start=None, app_end=None, log_path=None, progress_callback=None, stop_event=None):
        self.clear_log(log_path)
        try:
            data, _ = self.extract_firmware_data_and_crc(firmware_path, app_start, app_end)
        except Exception as e:
            self.log_write(f"❌ Error extracting firmware: {e}")
            return False

        crc32 = zlib.crc32(data) & 0xFFFFFFFF
        self.log_write(f"✅ [AUTO-CALC] CRC32 for handshake: 0x{crc32:08X}")

        blocks = self.split_blocks(data, CHUNK_SIZE)
        self.log_write(f"✅ Data split into {len(blocks)} blocks of up to {CHUNK_SIZE} bytes")

        block_headers = self.generate_block_headers(data, chunk_size=CHUNK_SIZE + 5)

        if len(block_headers) < len(blocks):
            self.log_write(f"❌ Not enough block headers for {len(blocks)} blocks. Only {len(block_headers)} found!")
            return False

        bus = CANBusWrapper(self.interface, self.channel, self.bitrate)
        try:
            if progress_callback: progress_callback("step", 0, 6)
            if not self.enter_programming_session(bus, stop_event=stop_event): return False
            if progress_callback: progress_callback("step", 1, 6)
            if not self.send_consecutive_frame(bus): return False
            if progress_callback: progress_callback("step", 2, 6)
            if not self.send_flow_control(bus): return False
            if progress_callback: progress_callback("step", 3, 6)
            if not self.erase_memory(bus): return False
            if progress_callback: progress_callback("step", 4, 6)
            if not self.request_download(bus, data): return False
            if progress_callback: progress_callback("step", 5, 6)
            if not self.send_transfer_data(bus, blocks, block_headers, progress_callback=progress_callback):
                self.log_write("❌ Block transfer failed!")
                return False
            final_crc = zlib.crc32(data) & 0xFFFFFFFF
            self.log_write(f"✅ [POST-TRANSFER] CRC32 of all blocks transferred: 0x{final_crc:08X}")
            if not self.send_post_flash_handshake_split_crc(bus, crc32):
                self.log_write("❌ Post-flash handshake failed!")
                return False
            if progress_callback: progress_callback("complete", 1, 1)
            self.log_write("\n🎉 Flashing Completed Successfully!")
            return True
        except Exception as e:
            self.log_write("❌ ERROR: " + str(e))
            return False
        finally:
            bus.shutdown()
            self.log_write("🔌 CAN Bus shutdown.")

    def read_version_pages_ascii(self, can_id=0x18F10ED0, listen_time=10.0):
        import collections, string
        label_map = {
            1: "ASW_ID_01", 2: "ASW_ID_02", 3: "ASW_ID_03", 4: "ASW_ID_04",
            5: "ASW_ID_05", 6: "ASW_ID_06", 7: "ASW_ID_07", 8: "ASW_ID_08",
            9: "ASW_ID_09", 10: "ASW_ID_10", 11: "ASW_ID_11",
        }
        results = {}
        printable = set(bytes(string.printable, "ascii"))
        bus = CANBusWrapper(self.interface, self.channel, self.bitrate)
        self.log_write(f"▶ Reading multiplexed version frames on ID 0x{can_id:X} (extended) ...")
        try:
            end = time.time() + listen_time
            while time.time() < end:
                msg = bus.recv(timeout=0.1)
                if not msg:
                    continue
                if not msg.get("is_extended_id", True):
                    continue
                if msg["arbitration_id"] != can_id:
                    continue
                data = msg["data"]
                if not data or len(data) < 2:
                    continue
                pg = data[0]
                payload = bytes(b for b in data[1:8] if b in printable).decode("ascii", "ignore").strip("\x00").strip()
                if not payload:
                    continue
                label = label_map.get(pg, f"Pg_{pg:02d}")
                results[label] = payload
            ordered = collections.OrderedDict()
            for k in range(1, 12):
                label = label_map.get(k)
                if label in results:
                    ordered[label] = results[label]
            for k, v in results.items():
                if k not in ordered:
                    ordered[k] = v
            if ordered:
                self.log_write("✅ Read Ver pages: " + ", ".join(f"{k}='{v}'" for k, v in ordered.items()))
            else:
                self.log_write("❌ No version pages received within listen window.")
            return ordered
        finally:
            bus.shutdown()


# ============================================================
# Air Pump / Oil Pump flashing logic (custom CAN protocol)
# ============================================================

# Flash memory layout
_PUMP_ECU_FLASH_BASE = 0x003E8000
_PUMP_BLOCK_ID_BASE  = 0x003F4000   # ECU_FLASH_BASE + 6 * 0x2000
_PUMP_ADDR_STEP      = 0x2000
_PUMP_MAX_BLOCK      = 0x4000
_PUMP_PAYLOAD_BYTES  = 6

# Timing
_PUMP_HEARTBEAT_INTERVAL = 0.101
_PUMP_HEARTBEAT_COUNT    = 60       # up to ~6 s; stops early on ECU response
_PUMP_WAKEUP_EXTRA       = 3.0
_PUMP_ERASE_TIMEOUT      = 5.0
_PUMP_PROG_TIMEOUT       = 5.0
_PUMP_ACK_TIMEOUT        = 1.0
_PUMP_LAST_FRAME_TIMEOUT = 1.0

# CAN IDs per pump type
PUMP_CAN_CONFIG = {
    "Air Pump": {"tool_id": 0x180006FF, "ecu_id": 0x1800FF06},
    "Oil Pump": {"tool_id": 0x180005FF, "ecu_id": 0x1800FF05},
}
_PUMP_BCAST_ID  = 0x1800FFFF
_PUMP_NAK_ID    = 0x1800EEEE


def _pump_xor8(data):
    r = 0
    for b in data[:7]:
        r ^= b
    return r

def _pump_make_frame(b0, payload):
    raw = bytes([b0]) + bytes(payload)
    return raw + bytes([_pump_xor8(raw)])

def _pump_verify_frame(data):
    return len(data) == 8 and _pump_xor8(data) == data[7]

def _pump_addr_payload(full_addr, size):
    return bytes([
        (full_addr >> 24) & 0xFF,
        (full_addr >> 16) & 0xFF,
        (full_addr >>  8) & 0xFF,
        (full_addr      ) & 0xFF,
        (size      >>  8) & 0xFF,
         size             & 0xFF,
    ])

def _pump_load_hex(path):
    """Parse Intel HEX firmware for pump ECUs.

    Returns (firmware, crc_bytes, crc_addr, base_addr, oem_blocks, fw_size).
    oem_blocks is None for normal sequential hex files; for files with stride
    anomalies (like Oil Pump VER1) it is a list of block dicts so the OEM
    flashing sequence can be reproduced exactly.
    """
    records = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line.startswith(':'):
                continue
            bc   = int(line[1:3],  16)
            addr = int(line[3:7],  16)
            rt   = int(line[7:9],  16)
            data = bytes.fromhex(line[9:9 + bc * 2])
            records.append((bc, addr, rt, data))

    ela = 0
    crc_addr  = None
    base_addr = None
    for bc, addr, rt, data in records:
        if rt == 4:
            ela = int.from_bytes(data, "big") << 16
        elif rt == 0:
            if bc == 4:
                crc_addr = ela | addr
            if base_addr is None and bc > 4:
                base_addr = ela | addr

    if crc_addr is None:
        raise ValueError("No 4-byte CRC record found in hex file")
    if base_addr is None:
        raise ValueError("No data records found in hex file")

    # Detect stride anomalies (skip the gap between last data record and CRC)
    has_anomaly = False
    ela = 0; prev_bc2 = None; prev_full2 = None
    for bc, addr, rt, data in records:
        if rt == 4:
            ela = int.from_bytes(data, "big") << 16
            prev_bc2 = None; prev_full2 = None
        elif rt == 0:
            full_addr = ela | addr
            if (prev_bc2 is not None and prev_full2 is not None and
                    full_addr != crc_addr and
                    (full_addr - prev_full2) > prev_bc2 // 2):
                has_anomaly = True
                break
            prev_bc2 = bc; prev_full2 = full_addr
        elif rt == 1:
            break

    if has_anomaly:
        oem_blocks, crc_bytes = _pump_build_oem_blocks(records, crc_addr)
        firmware_size = sum(b["size"] for b in oem_blocks)
        return None, crc_bytes, crc_addr, base_addr, oem_blocks, firmware_size
    else:
        seq = bytearray(); ela = 0
        for bc, addr, rt, data in records:
            if rt == 4:
                ela = int.from_bytes(data, "big") << 16
            elif rt == 0:
                seq += data
            elif rt == 1:
                break
        crc_bytes = bytes(seq[-4:])
        firmware  = bytes(seq[:-4])
        return firmware, crc_bytes, crc_addr, base_addr, None, len(firmware)


def _pump_build_oem_blocks(records, crc_addr):
    """Build blocks replicating OEM tool behaviour for stride-anomaly hex files."""
    blocks = []
    cur_addr = None; cur_data = bytearray(); cur_sector = -1
    prev_bc = None; prev_full = None; prev_ela = None; ela = 0; crc_bytes = None

    for bc, addr, rt, data in records:
        if rt == 4:
            new_ela = int.from_bytes(data, "big") << 16
            if prev_ela is not None and new_ela != prev_ela and cur_addr is not None:
                blocks.append({"addr": cur_addr, "data": bytes(cur_data), "size": len(cur_data)})
                cur_addr = None; cur_data = bytearray(); cur_sector = -1
                prev_bc = None; prev_full = None
            ela = new_ela; prev_ela = new_ela; continue
        if rt == 1:
            break
        if rt != 0:
            continue
        full_addr = ela | addr
        if full_addr == crc_addr and bc == 4:
            if cur_addr is not None:
                blocks.append({"addr": cur_addr, "data": bytes(cur_data), "size": len(cur_data)})
            crc_bytes = bytes(data); break
        sector = (full_addr // _PUMP_ADDR_STEP) * _PUMP_ADDR_STEP
        stride_anomaly = (prev_bc is not None and prev_full is not None and
                          (full_addr - prev_full) > prev_bc // 2)
        if cur_addr is None or sector != cur_sector or stride_anomaly:
            if cur_addr is not None:
                blocks.append({"addr": cur_addr, "data": bytes(cur_data), "size": len(cur_data)})
            cur_addr = full_addr; cur_data = bytearray(data); cur_sector = sector
        else:
            cur_data += data
        prev_bc = bc; prev_full = full_addr

    # Assign block IDs matching OEM tool logic
    prev_id = None; prev_sector = None
    for i, blk in enumerate(blocks):
        is_last = (i == len(blocks) - 1)
        sector = (blk["addr"] // _PUMP_ADDR_STEP) * _PUMP_ADDR_STEP
        if is_last:
            blk["block_id"] = 1
        elif prev_id is None:
            blk["block_id"] = (_PUMP_BLOCK_ID_BASE - blk["addr"]) // _PUMP_ADDR_STEP
        elif sector == prev_sector:
            blk["block_id"] = prev_id - 1
        elif blk["size"] == 16384:
            blk["block_id"] = (_PUMP_BLOCK_ID_BASE - blk["addr"]) // _PUMP_ADDR_STEP
        else:
            blk["block_id"] = prev_id
        prev_id = blk["block_id"]; prev_sector = sector

    return blocks, crc_bytes


def _pump_build_blocks_sequential(firmware, base_addr):
    """Sequential block builder for normal (no stride anomaly) hex files."""
    blocks = []
    total  = -(-len(firmware) // _PUMP_MAX_BLOCK)
    offset, addr = 0, base_addr
    for i in range(total):
        chunk   = firmware[offset:offset + _PUMP_MAX_BLOCK]
        is_last = (i == total - 1)
        b_id    = 1 if is_last else (_PUMP_BLOCK_ID_BASE - addr) // _PUMP_ADDR_STEP
        blocks.append({"addr": addr, "size": len(chunk), "data": chunk, "block_id": b_id})
        offset += _PUMP_MAX_BLOCK
        addr   += _PUMP_ADDR_STEP
    return blocks


class PumpFlashingLogic:
    """
    Flash logic for Air Pump and Oil Pump ECUs (S32K144, custom 8-byte CAN protocol).
    Exposes the same flash_firmware() interface as FlashingLogic so the GUI can
    use both interchangeably.
    """

    def __init__(self, pump_type, interface, channel, bitrate=250000, log_callback=None):
        if pump_type not in PUMP_CAN_CONFIG:
            raise ValueError(f"Unknown pump type: {pump_type}")
        cfg = PUMP_CAN_CONFIG[pump_type]
        self.tool_id      = cfg["tool_id"]
        self.ecu_id       = cfg["ecu_id"]
        self.interface    = interface if interface != "peak" else "pcan"
        self.channel      = channel
        self.bitrate      = bitrate
        self.log_callback = log_callback

    def log_write(self, msg):
        print(msg)
        if self.log_callback:
            self.log_callback(msg)

    def _send_and_wait(self, bus, data, timeout, stop_event=None):
        assert _pump_verify_frame(data)
        bus.send(self.tool_id, list(data), is_extended_id=True)
        deadline = time.time() + timeout
        while time.time() < deadline:
            if stop_event and stop_event.is_set():
                raise RuntimeError("Aborted by user")
            rx = bus.recv(timeout=min(0.05, max(0.001, deadline - time.time())))
            if not rx:
                continue
            if rx['arbitration_id'] == self.ecu_id and bytes(rx['data']) == data:
                return
            if rx['arbitration_id'] == _PUMP_NAK_ID:
                nak = bytes(rx['data'])
                addr_val = int.from_bytes(nak[0:4], 'big')
                raise RuntimeError(
                    f"ECU rejected frame (0x1800EEEE NAK).\n"
                    f"  Sent   : {data.hex().upper()}\n"
                    f"  NAK    : {nak.hex().upper()}\n"
                    f"  Address: 0x{addr_val:08X}\n"
                    f"  Cause  : hex file base address differs from firmware currently in ECU.\n"
                    f"  Fix    : use a hex file built for base 0x003E8000, or flash on an ECU\n"
                    f"           that already has firmware at the same base address."
                )
        raise RuntimeError(f"No ACK for {data.hex().upper()}")

    def flash_firmware(self, firmware_path, app_start=None, app_end=None,
                       log_path=None, progress_callback=None, stop_event=None):
        # ── Load hex ────────────────────────────────────────────────────────
        self.log_write("Loading hex file...")
        try:
            firmware, crc_bytes, crc_addr, base_addr, oem_blocks, fw_size = \
                _pump_load_hex(firmware_path)
        except Exception as e:
            self.log_write(f"❌ Error loading hex: {e}")
            return False

        crc_int = int.from_bytes(crc_bytes, "big")
        self.log_write(f"  Firmware : {fw_size:,} bytes")
        self.log_write(f"  Base addr: 0x{base_addr:08X}")
        self.log_write(f"  CRC      : 0x{crc_int:08X}  at 0x{crc_addr:08X}")

        if oem_blocks is not None:
            self.log_write(f"  Mode     : OEM block parser (stride anomalies detected)")
            blocks = oem_blocks
        else:
            blocks = _pump_build_blocks_sequential(firmware, base_addr)
        self.log_write(f"  Blocks   : {len(blocks)}")
        for b in blocks:
            self.log_write(f"    0x{b['addr']:08X}  {b['size']:5d} B  id=0x{b['block_id']:02X}")

        total_frames = sum(-(-b["size"] // _PUMP_PAYLOAD_BYTES) for b in blocks)

        # Derive ECU address byte from ecu_id (low byte of the 3rd octet)
        ecu_addr = self.ecu_id & 0xFF

        bus = CANBusWrapper(self.interface, self.channel, self.bitrate)
        try:
            # ── Step 0: Keepalive ────────────────────────────────────────────
            if progress_callback: progress_callback("step", 0, 6)
            hb_byte = (_PUMP_BLOCK_ID_BASE - base_addr) // _PUMP_ADDR_STEP + 1
            hb_data = _pump_make_frame(0x00, bytes([0x00, hb_byte, 0x00, 0x00, 0x00, 0x00]))
            self.log_write(f"\n[1/5] Keepalive — waking ECU (up to {_PUMP_HEARTBEAT_COUNT * _PUMP_HEARTBEAT_INTERVAL:.0f} s)...")
            self.log_write(f"  Heartbeat byte: 0x{hb_byte:02X}  (supports live ECU and cold-start)")

            # Send "enter bootloader" broadcast so a live (running) ECU reboots
            # into bootloader without needing a power cycle.
            # Frame: FF 02 <ecu_addr> 00 00 00 00 <XOR>  on 0x1800FFFF
            bcast_raw   = bytes([0xFF, 0x02, ecu_addr, 0x00, 0x00, 0x00, 0x00])
            bcast_xor   = 0
            for b in bcast_raw:
                bcast_xor ^= b
            bcast_frame = bcast_raw + bytes([bcast_xor])
            bus.send(_PUMP_BCAST_ID, list(bcast_frame), is_extended_id=True)
            self.log_write(f"  Broadcast 'enter bootloader': {bcast_frame.hex().upper()}")

            # Wait up to 500 ms for broadcast ACK (FF 82 <ecu_addr> ...)
            bcast_acked = False
            deadline = time.time() + 0.5
            while time.time() < deadline:
                rx = bus.recv(timeout=0.05)
                if rx and rx['arbitration_id'] == self.ecu_id:
                    d = bytes(rx['data'])
                    if d[0] == 0xFF and d[1] == 0x82:
                        self.log_write(f"  Broadcast ACK ✓  ({d.hex().upper()})")
                        bcast_acked = True
                        break
            if bcast_acked:
                self.log_write("  ECU rebooting to bootloader — waiting 300 ms...")
                time.sleep(0.3)
            else:
                self.log_write("  No broadcast ACK (ECU may already be in bootloader)")

            ecu_woke = False
            for i in range(_PUMP_HEARTBEAT_COUNT):
                if stop_event and stop_event.is_set():
                    self.log_write("⛔ Cancelled by user")
                    return False
                bus.send(self.tool_id, list(hb_data), is_extended_id=True)
                rx = bus.recv(timeout=0.08)
                if rx and rx['arbitration_id'] == self.ecu_id:
                    mode = "live ECU → rebooted to bootloader" if i > 15 else "bootloader / cold-start"
                    self.log_write(f"  ECU responded ✓  ({bytes(rx['data']).hex().upper()})")
                    self.log_write(f"  Mode: {mode}  (after {i+1} heartbeats)")
                    ecu_woke = True
                    break
                time.sleep(max(0, _PUMP_HEARTBEAT_INTERVAL - 0.08))

            if not ecu_woke:
                deadline = time.time() + _PUMP_WAKEUP_EXTRA
                while time.time() < deadline:
                    rx = bus.recv(timeout=0.2)
                    if rx and rx['arbitration_id'] == self.ecu_id:
                        self.log_write(f"  ECU responded ✓  ({bytes(rx['data']).hex().upper()})")
                        ecu_woke = True
                        break

            if not ecu_woke:
                self.log_write("❌ ECU did not respond to keepalive.")
                return False

            # ── Step 1-2: Flash blocks ───────────────────────────────────────
            if progress_callback: progress_callback("step", 1, 6)
            self.log_write(f"\n[2/5] Flashing {len(blocks)} blocks...")
            frames_done = 0

            for blk_idx, block in enumerate(blocks):
                if stop_event and stop_event.is_set():
                    self.log_write("⛔ Cancelled by user")
                    return False
                self.log_write(f"  Block {blk_idx+1}/{len(blocks)}  "
                               f"0x{block['addr']:08X}  {block['size']} B  "
                               f"id=0x{block['block_id']:02X}")

                init_pl = _pump_addr_payload(block["addr"], block["size"])
                self._send_and_wait(bus, _pump_make_frame(0x04, init_pl),
                                    _PUMP_ERASE_TIMEOUT, stop_event)
                self.log_write(f"    Erase ACK ✓")

                toggle = 0x01
                data   = block["data"]
                n      = -(-block["size"] // _PUMP_PAYLOAD_BYTES)
                offset = 0
                chunk  = b""

                for fi in range(n):
                    if stop_event and stop_event.is_set():
                        self.log_write("⛔ Cancelled by user")
                        return False
                    chunk = data[offset:offset + _PUMP_PAYLOAD_BYTES]
                    if len(chunk) < _PUMP_PAYLOAD_BYTES:
                        chunk = chunk.ljust(_PUMP_PAYLOAD_BYTES, b'\xFF')
                    t = _PUMP_LAST_FRAME_TIMEOUT if fi == n - 1 else _PUMP_ACK_TIMEOUT
                    self._send_and_wait(bus, _pump_make_frame(toggle, chunk), t, stop_event)
                    toggle = 0x02 if toggle == 0x01 else 0x01
                    offset += _PUMP_PAYLOAD_BYTES
                    frames_done += 1
                    if progress_callback:
                        progress_callback("block", frames_done, total_frames)

                eob_pl = bytes([0x00, block["block_id"]]) + bytes(chunk[2:6])
                self._send_and_wait(bus, _pump_make_frame(0x00, eob_pl),
                                    _PUMP_ACK_TIMEOUT, stop_event)
                self.log_write(f"    Block done ✓")

            if progress_callback: progress_callback("step", 2, 6)

            # ── Step 3: Program (write CRC) ──────────────────────────────────
            if progress_callback: progress_callback("step", 3, 6)
            self.log_write("\n[3/5] Program command (writing CRC)...")
            prog_pl = _pump_addr_payload(crc_addr, 4)
            self._send_and_wait(bus, _pump_make_frame(0x04, prog_pl),
                                _PUMP_PROG_TIMEOUT, stop_event)
            self.log_write("  Program ACK ✓")

            # ── Step 4: Verify ───────────────────────────────────────────────
            if progress_callback: progress_callback("step", 4, 6)
            self.log_write("\n[4/5] Verify...")
            crc_pl = bytes([0x00]) + crc_bytes[1:4] + bytes([0xFF, 0xFF])
            self._send_and_wait(bus, _pump_make_frame(0x01, crc_pl),
                                _PUMP_ACK_TIMEOUT, stop_event)
            self.log_write("  Verify ACK ✓")

            # ── Step 5: Close session ────────────────────────────────────────
            if progress_callback: progress_callback("step", 5, 6)
            self.log_write("\n[5/5] Close session...")
            self._send_and_wait(bus, _pump_make_frame(0x03, crc_pl), 0.5, stop_event)
            self.log_write("  Close ACK ✓")

            # Wait for app broadcast (ECU reset confirmation)
            deadline = time.time() + 4.0
            while time.time() < deadline:
                rx = bus.recv(timeout=0.2)
                if rx and rx['arbitration_id'] == _PUMP_BCAST_ID:
                    self.log_write(f"  ECU broadcast: {bytes(rx['data']).hex().upper()} ✓")
                    break

            if progress_callback: progress_callback("complete", 1, 1)
            self.log_write("\n🎉 Flashing Completed Successfully!")
            return True

        except Exception as e:
            self.log_write(f"❌ ERROR: {e}")
            return False
        finally:
            bus.shutdown()
            self.log_write("🔌 CAN Bus shutdown.")
