import sys as _sys

from loguru import logger

from src.config import settings
from src.enums import Environment

if settings.ENVIRONMENT_ == Environment.PROD:
    logger.remove()
    logger.add(
        _sys.stdout,
        level="DEBUG",
        filter=lambda record: record["level"].no < 40,
        enqueue=True,
    )
    logger.add(_sys.stderr, level="ERROR", enqueue=True)


def debug(value, name: str):
    try:
        logger.debug(f"{name}: {value}")
    except Exception as e:
        logger.exception(repr(e))
    return value
