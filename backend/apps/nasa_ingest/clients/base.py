"""Shared NASA HTTP client. PLAN §6.3, §9.7.

Every NASA call goes through here. Guarantees:
  - API key is attached server-side; never leaks to frontend logs
  - Hourly quota counter in Redis; soft-warn at 70%, hard-stop at 95%
  - Circuit breaker wraps every call
  - Timeouts so a hung NASA server doesn't wedge a worker
"""
from __future__ import annotations

import logging
from datetime import datetime

import requests
from django.conf import settings
from django.core.cache import cache

from .. import circuit

logger = logging.getLogger(__name__)


class QuotaExhaustedError(RuntimeError):
    pass


class NASAClient:
    """Base for per-API clients (APODClient, NeoWsClient, ...)."""

    TIMEOUT_SECONDS = 15

    def _quota_key(self) -> str:
        return f"nasa:quota:{datetime.utcnow():%Y%m%d%H}"

    def _check_quota(self) -> int:
        key = self._quota_key()
        used = cache.get(key) or 0
        if used >= settings.NASA_QUOTA_HARD_STOP_AT:
            raise QuotaExhaustedError(
                f"NASA quota {used}/{settings.NASA_QUOTA_PER_HOUR} — refusing to call"
            )
        if used >= settings.NASA_QUOTA_WARN_AT:
            logger.warning("NASA quota at %d/%d this hour", used, settings.NASA_QUOTA_PER_HOUR)
        return used

    def _increment_quota(self) -> None:
        key = self._quota_key()
        try:
            new = cache.incr(key)
        except ValueError:
            cache.set(key, 1, timeout=3600)
            new = 1
        # Ensure key expires even on the first increment in an empty Redis
        cache.expire(key, 3600)
        return new

    def _do_get(self, url: str, params: dict | None = None) -> dict:
        params = {**(params or {}), "api_key": settings.NASA_API_KEY}
        self._check_quota()
        resp = requests.get(url, params=params, timeout=self.TIMEOUT_SECONDS)
        self._increment_quota()
        resp.raise_for_status()
        return resp.json()

    def get(self, url: str, params: dict | None = None) -> dict:
        """Public entry — wraps the HTTP call in the circuit breaker."""
        return circuit.call(self._do_get, url, params)
