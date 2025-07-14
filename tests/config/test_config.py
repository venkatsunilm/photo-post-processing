from pro_photo_processor.config import config


def test_config_defaults():
    # NOTE: Minimal test for coverage. Full config validation will be added later.
    assert hasattr(config, "DEFAULT_OUTPUT_DIR")
    assert hasattr(config, "DEFAULT_INPUT_PATH")
    assert hasattr(config, "RESOLUTIONS")
    assert isinstance(config.RESOLUTIONS, dict)
