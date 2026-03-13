"""
Logging Configuration

Provides centralized logging setup for the application.
"""
import logging
import os
from typing import Optional


def setup_logger(
    logger_name: str,
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    formatter: Optional[logging.Formatter] = None
) -> logging.Logger:
    """
    Set up a logger instance with custom configuration
    
    Args:
        logger_name: Name for the logger (usually __name__)
        level: Logging level (default: INFO)
        log_file: Optional file path for file logging
        formatter: Optional custom formatter
        
    Returns:
        Configured logger instance
        
    Example:
        logger = setup_logger(__name__)
        logger.info("Application started")
    """
    # Get or create logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Default formatter
    if formatter is None:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        log_path = os.path.join(os.getcwd(), log_file)
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger
