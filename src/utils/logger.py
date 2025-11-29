#src/utils/logger.py
import logging
import os
from logging.handlers import RotatingFileHandler
from src.config.settings import settings

os.makedirs("logs", exist_ok=True)

def get_logger(name: str):
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    handler = RotatingFileHandler(
        settings.LOG_FILE, maxBytes=2_000_000, backupCount=3
    )
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    )

    logger.addHandler(handler)
    return logger
