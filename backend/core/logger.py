"""
Logging Configuration

Sets up structured logging with Loguru for the application.
"""

import sys
from loguru import logger
from backend.core.config import settings


def setup_logger() -> logger:
    """
    Configure Loguru with custom formatting and levels
    based on application settings.
    """
    # Remove default handler
    logger.remove()

    # Map log levels
    log_level = settings.log_level.upper()
    level_map = {
        "DEBUG": "DEBUG",
        "INFO": "INFO",
        "WARNING": "WARNING",
        "ERROR": "ERROR",
    }
    level = level_map.get(log_level, "INFO")

    # Console handler with colorization
    logger.add(
        sys.stderr,
        level=level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
        colorize=True,
    )

    # File handler (rotating log file)
    logger.add(
        "logs/app_{time:YYYY-MM-DD}.log",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        level="DEBUG",
        format=(
            "{time:YYYY-MM-DD HH:mm:ss} | "
            "{level: <8} | "
            "{name}:{function}:{line} | "
            "{message}"
        ),
        encoding="utf-8",
    )

    return logger


# Initialize logger
log = setup_logger()