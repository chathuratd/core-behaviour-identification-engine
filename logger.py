"""
logger.py
=========
Centralised structured JSON logger for the CBIE microservice.

All modules should import the logger via:
    from logger import get_logger
    log = get_logger(__name__)

Log Format (JSON):
    {
        "timestamp": "2026-03-04T22:11:00.000000+00:00",
        "level":     "INFO",
        "logger":    "pipeline",
        "message":   "Starting CBIE Pipeline",
        "user_id":   "pilot_user_1",
        "job_id":    "a1b2c3-...",
        "stage":     "TOPIC_DISCOVERY",
        ...extra fields...
    }

Future Loki/Promtail Integration:
    - Promtail should be configured to scrape the log file (see LOG_FILE_PATH).
    - Since logs are newline-delimited JSON, no regex pipeline is needed in Promtail.
    - In Grafana, filter by `level`, `logger`, `user_id`, `job_id`, or `stage`.
"""
from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Any


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
LOG_FILE_PATH = os.environ.get("LOG_FILE", os.path.join(os.path.dirname(__file__), "cbie.log"))


# ---------------------------------------------------------------------------
# JSON Formatter
# ---------------------------------------------------------------------------

class JsonFormatter(logging.Formatter):
    """
    Formats every log record as a single-line JSON object.
    Extra keyword arguments passed to log calls are included as top-level JSON fields.
    Compatible with Promtail's automatic JSON parsing pipeline.
    """

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level":     record.levelname,
            "logger":    record.name,
            "message":   record.getMessage(),
        }

        # Append any extra structured fields passed by the caller
        # e.g.  log.info("msg", extra={"user_id": "u1", "stage": "CLUSTERING"})
        reserved = {
            "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
            "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
            "created", "msecs", "relativeCreated", "thread", "threadName",
            "processName", "process", "message", "taskName",
        }
        for key, value in record.__dict__.items():
            if key not in reserved and not key.startswith("_"):
                payload[key] = value

        # Attach exception info if present
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


# ---------------------------------------------------------------------------
# Handler Setup (console + rotating file)
# ---------------------------------------------------------------------------

def _build_handlers() -> list[logging.Handler]:
    handlers: list[logging.Handler] = []

    # 1. Console (stdout) — always on, so uvicorn / docker logs show JSON in real-time
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(JsonFormatter())
    handlers.append(console)

    # 2. Rotating file — picked up by Promtail; roll at 10 MB, keep last 5
    try:
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            LOG_FILE_PATH,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(JsonFormatter())
        handlers.append(file_handler)
    except Exception as exc:  # noqa: BLE001  # don't crash if log dir is unwriteable
        logging.getLogger(__name__).warning(
            "Could not create file log handler: %s — logging to console only.", exc
        )

    return handlers


# ---------------------------------------------------------------------------
# Root CBIE logger
# ---------------------------------------------------------------------------

_root_logger: logging.Logger | None = None


def _initialise_root() -> logging.Logger:
    global _root_logger  # noqa: PLW0603
    if _root_logger is not None:
        return _root_logger

    root = logging.getLogger("cbie")
    root.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    if not root.handlers:
        for h in _build_handlers():
            root.addHandler(h)

    # Prevent log records from bubbling to the generic Python root logger
    root.propagate = False

    _root_logger = root
    return root


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_logger(name: str) -> logging.Logger:
    """
    Returns a child of the root CBIE logger.
    Call this at the top of every module:

        from logger import get_logger
        log = get_logger(__name__)
    """
    _initialise_root()
    return logging.getLogger(f"cbie.{name}")
