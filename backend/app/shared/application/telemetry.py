"""Sinais estruturados sem conteúdo de requisições ou identificadores de negócio."""

import json
import logging
import time
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone

request_id = ContextVar("request_id", default=None)
logger = logging.getLogger("lgd")


class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps(
            {
                "time": datetime.now(timezone.utc).isoformat(),
                "level": record.levelname,
                "event": record.getMessage(),
                "request_id": request_id.get(),
                **getattr(record, "fields", {}),
            },
            ensure_ascii=False,
        )


def configure():
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False


def emit(event, **fields):
    logger.info(event, extra={"fields": fields})


@contextmanager
def measured(phase, **fields):
    started = time.perf_counter()
    try:
        yield
    finally:
        emit(
            "phase",
            phase=phase,
            duration_ms=round((time.perf_counter() - started) * 1000, 2),
            **fields,
        )
