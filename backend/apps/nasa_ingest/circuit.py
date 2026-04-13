"""NASA circuit breaker. PLAN §6.7.

CLOSED    -> normal operation
OPEN      -> NASA unreachable; skip all calls, serve archive
HALF_OPEN -> send one probe; success closes, failure reopens

State lives in Redis so multiple Celery workers share it.
"""
from __future__ import annotations

import logging
import time
from typing import Callable, TypeVar

from django.core.cache import cache

logger = logging.getLogger(__name__)

T = TypeVar("T")

FAILURE_THRESHOLD = 5           # consecutive failures before opening
RECOVERY_TIMEOUT = 300          # seconds before probing

_STATE_KEY = "circuit:nasa:state"
_FAIL_KEY = "circuit:nasa:failures"
_OPENED_AT_KEY = "circuit:nasa:opened_at"


class CircuitOpenError(RuntimeError):
    """Raised when the breaker is open and the call is short-circuited."""


def state() -> str:
    return cache.get(_STATE_KEY) or "CLOSED"


def _on_success() -> None:
    cache.delete(_FAIL_KEY)
    cache.set(_STATE_KEY, "CLOSED", timeout=None)
    cache.delete(_OPENED_AT_KEY)


def _on_failure() -> None:
    fails = cache.get(_FAIL_KEY) or 0
    fails += 1
    cache.set(_FAIL_KEY, fails, timeout=3600)
    if fails >= FAILURE_THRESHOLD:
        cache.set(_STATE_KEY, "OPEN", timeout=None)
        cache.set(_OPENED_AT_KEY, time.time(), timeout=None)
        logger.warning("NASA circuit OPEN after %d failures", fails)


def _should_probe() -> bool:
    opened_at = cache.get(_OPENED_AT_KEY) or 0
    return (time.time() - opened_at) > RECOVERY_TIMEOUT


def call(fn: Callable[..., T], *args, **kwargs) -> T:
    """Wrap a NASA call. Raises CircuitOpenError if short-circuited."""
    current = state()

    if current == "OPEN":
        if _should_probe():
            cache.set(_STATE_KEY, "HALF_OPEN", timeout=None)
        else:
            raise CircuitOpenError("NASA circuit open — using archive")

    try:
        result = fn(*args, **kwargs)
    except Exception:
        _on_failure()
        raise
    else:
        _on_success()
        return result
