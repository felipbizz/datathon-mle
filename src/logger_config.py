# =============================================================================
# BIBLIOTECAS E MÓDULOS
# =============================================================================

import sys
from pathlib import Path
from typing import Optional

from loguru import logger

# =============================================================================
# FUNÇÕES
# =============================================================================

logging_config = lambda sink_root_dir: {
    "handlers": [
        {
            "sink": sink_root_dir / "log/info.log",
            "rotation": "1 week",
            "retention": "1 month",
            "level": "INFO",
            "format": "{time} | {level} | {file}:{name}:{function}:{line} - {message}",
            "backtrace": True,
            "diagnose": True,
        },
        {
            "sink": sink_root_dir / "log/debugging.log",
            "rotation": "1 week",
            "retention": "1 month",
            "level": "TRACE",
            "format": "{time} | {level} | {file}:{name}:{function}:{line} - {message}",
            "backtrace": True,
            "diagnose": True,
        },
        {
            "sink": sink_root_dir / "log/errors.log",
            "rotation": "1 week",
            "retention": "1 month",
            "level": "WARNING",
            "format": "{time} | {level} | {file}:{name}:{function}:{line} - {message}",
            "backtrace": True,
            "diagnose": True,
        },
    ]
}


def configure_logging(
    sink_root_dir: Path,
    log_to_file: Optional[bool] = False,
    log_level: str = "INFO",
) -> None:
    """
    Configure the logger for the project.

    Args:
        log_file: Name of the log file (if None, a default name will be used)
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        rotation: When to rotate the log file
        retention: How long to keep the log files
    """
    # Remove default handlers
    logger.remove()

    # Add file handler if requested
    if log_to_file:
        logger.configure(**logging_config(sink_root_dir))

    # Add stdout handler
    logger.add(
        sys.stdout,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    )
