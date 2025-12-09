"""Logging configuration for the application."""

import logging
import sys
from typing import Optional

from app.config import get_settings


def setup_logging(level: Optional[str] = None) -> logging.Logger:
    """Configure and return the application logger."""
    settings = get_settings()
    
    log_level = level or ("DEBUG" if settings.debug else "INFO")
    
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    
    logger = logging.getLogger("blockai")
    logger.setLevel(log_level)
    logger.addHandler(handler)
    
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    return logger


logger = setup_logging()
