"""
Improved logging configuration for the photo processing application.
"""
import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    format_type: str = "detailed"
) -> None:
    """
    Configure logging for the application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        format_type: Format type ('detailed' or 'simple')
    """
    formatters = {
        'detailed': logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        ),
        'simple': logging.Formatter('%(levelname)s - %(message)s')
    }

    # Create handlers
    handlers = [logging.StreamHandler(sys.stdout)]

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))

    # Configure logging
    formatter = formatters.get(format_type, formatters['detailed'])
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        handlers=[],  # We'll add handlers manually
    )

    # Configure handlers with formatter
    for handler in handlers:
        handler.setFormatter(formatter)
        logging.getLogger().addHandler(handler)

    # Set specific loggers
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("numpy").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)
