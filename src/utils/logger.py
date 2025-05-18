"""
Logging Module

This module provides a centralized logging system for the Sierra Outfitters application.
It configures loggers with file handlers for error tracking.
"""
import logging
from pathlib import Path
from datetime import datetime

# Create a logs directory if it doesn't exist
LOGS_DIR = Path(__file__).parent.parent.parent / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Configure the logger
def configure_logger(name: str = 'sierra_outfitters') -> logging.Logger:
    logger = logging.getLogger(name)
    
    # Only configure if handlers haven't been added yet
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        
        # Create a log formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Create a file handler for all logs
        log_file = LOGS_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(file_handler)
    
    return logger

# Create a default logger
logger = configure_logger()
