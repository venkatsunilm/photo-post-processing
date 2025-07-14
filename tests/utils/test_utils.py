from pro_photo_processor.utils import get_mode_prefix


def test_get_mode_prefix_known_presets():
    assert get_mode_prefix("portrait_subtle") == "sub"
    assert get_mode_prefix("portrait_natural") == "nat"
    assert get_mode_prefix("sports_action") == "spt"
    assert get_mode_prefix("resize_only") == "res"
    assert get_mode_prefix("custom") == "cst"


def test_get_mode_prefix_unknown():
    assert get_mode_prefix("unknown_preset") == "prc"
