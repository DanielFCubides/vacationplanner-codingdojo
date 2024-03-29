import logging
import os
from typing import Optional


def setup_logger(
    logger_name: str,
    level=logging.INFO,
    log_file: Optional[str] = None,
    formatter: Optional[logging.Formatter] = None
) -> logging.Logger:
    """Set up a logger instance with a specific formatter and logger names"""

    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    formatter = formatter or logging.Formatter(
        '%(asctime)s - %(pathname)s - %(levelname)s - %(message)s'
    )

    if log_file:
        log_path = os.path.join(os.getcwd(), log_file)
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
