from __future__ import annotations

import os

from loguru import logger as _logger


def get_logger():
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    try:
        _logger.remove()
    except Exception:
        pass
    _logger.add(lambda msg: print(msg, end=""))
    _logger.level(level)
    return _logger


def log_json(level: str, message: str, **fields):
    log = get_logger()
    # Keep it simple; downstream can parse key=value pairs
    payload = {"msg": message, **fields}
    log.log(level.upper(), str(payload))


__all__ = ["get_logger", "log_json"]
