from dltool.presets import load_presets, load_zones, find_preset, apply_preset
from dltool.config import Config


def test_bundled_presets_load():
    presets = load_presets()
    descs = [p.desc for p in presets]
    assert "Multic-S -> CALIB" in descs
    assert "Multic-SX -> APP_ALL+BSP" in descs
    assert "ACH-LCC" in descs
    assert len(presets) >= 17


def test_preset_fields():
    p = find_preset(load_presets(), "Multic-S -> CALIB")
    assert p.zone == 1
    assert p.start == 0x18040000
    assert p.end == 0x1807FFF7
    assert p.min_data_can == 0x10
    assert p.min_data_doip == 0x400
    assert p.sha256_start == 0x1807FFC4
    assert p.sha256_length == 32
    assert p.seckey == 0xFFFFFFFF
    assert p.size == 0x1807FFF7 - 0x18040000 + 1


def test_block_size_per_transport():
    p = find_preset(load_presets(), "Multic-SX -> APP_ALL+BSP")
    assert p.block_size("doip") == 0x400
    assert p.block_size("can") == 0x20


def test_apply_preset_to_config():
    cfg = Config(transport="doip")
    p = find_preset(load_presets(), "Multic-S -> CALIB")
    apply_preset(cfg, p)
    assert cfg.preset_name == "Multic-S -> CALIB"
    assert cfg.zone == 1
    assert cfg.addr_start == 0x18040000
    assert cfg.block_size == 0x400
    assert cfg.security_key == "0xFFFFFFFF"


def test_zones_load():
    zones = load_zones()
    assert zones[0].value == 0 and "Main MCU Application" in zones[0].name
    assert any(z.value == 33 and "PLC Application Calibration" in z.name for z in zones)
