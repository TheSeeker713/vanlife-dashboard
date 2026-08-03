"""Rotating local log file, separate from the short user-facing messages
the UI shows. See AGENTS.md / Error handling & resilience: full error
detail goes here, not just a toast the user dismisses and loses."""
from __future__ import annotations

import logging
import logging.handlers

from . import config

_configured = False


def configure_logging() -> logging.Logger:
    global _configured
    logger = logging.getLogger("vldash")
    if _configured:
        return logger

    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    handler = logging.handlers.RotatingFileHandler(
        config.LOG_PATH, maxBytes=2_000_000, backupCount=3, encoding="utf-8"
    )
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
    )
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    _configured = True
    return logger
