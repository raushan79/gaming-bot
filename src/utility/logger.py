import logging
import sys
from logging.handlers import RotatingFileHandler

def get_logger(name: str = __name__, log_file: str = "app.log") -> logging.Logger:
    """
    Configure and return a logger that logs to both console and a file.

    Args:
        name (str): Name of the logger (usually __name__).
        log_file (str): Path to the log file.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Prevent duplicate handlers
    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)

        # File handler (rotating 150MB, keep 5 backups)
        file_handler = RotatingFileHandler(log_file, maxBytes=150*1024*1024, backupCount=5)
        file_handler.setLevel(logging.DEBUG)

        # Log format
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        # Add handlers
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger
