"""Logging configuration for Yakhteh services."""

import logging
import sys
from typing import Optional


def setup_logging(
    service_name: str,
    level: str = "INFO",
    format_string: Optional[str] = None
) -> logging.Logger:
    """Setup consistent logging across all services."""
    
    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "[%(filename)s:%(lineno)d] - %(message)s"
        )
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    
    # Create service-specific logger
    logger = logging.getLogger(service_name)
    
    # Suppress some noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific module."""
    return logging.getLogger(name)