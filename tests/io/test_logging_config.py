import logging
from pro_photo_processor.io import logging_config


def test_logging_config_basic():
    # NOTE: Minimal test for coverage. Full tests will be added later.
    logger = logging_config.get_logger("test_logger")
    assert isinstance(logger, logging.Logger)
    logger.info("Test log message")
