"""Celery ingestion tasks. PLAN §7.3.

Each task follows the same template:
  1. Acquire distributed Redis lock (prevents double-fetch from duplicate beat triggers)
  2. Call NASA client (behind circuit breaker + quota counter)
  3. Transform raw JSON -> Django models
  4. Trigger mission/quiz/puzzle generation
  5. Warm Redis cache
"""
from __future__ import annotations

import logging

from celery import shared_task
from django.core.cache import cache
from requests.exceptions import ConnectionError, HTTPError, Timeout
from redis.lock import Lock
from redis import Redis
from django.conf import settings

from .circuit import CircuitOpenError
from .clients.base import QuotaExhaustedError

logger = logging.getLogger(__name__)

_redis = Redis.from_url(settings.REDIS_URL)

_RETRY_KWARGS = dict(
    autoretry_for=(Timeout, ConnectionError, HTTPError),
    retry_backoff=60,
    retry_backoff_max=1800,
    retry_jitter=True,
    max_retries=5,
)


def _acquire_lock(name: str, timeout: int = 300):
    lock = Lock(_redis, f"lock:ingest:{name}", timeout=timeout, blocking=False)
    if not lock.acquire(blocking=False):
        return None
    return lock


def _safe_release(lock):
    try:
        lock.release()
    except Exception:
        pass


# --------------------------------------------------------------------------- #
# APOD (Phase 1)
# --------------------------------------------------------------------------- #

@shared_task(**_RETRY_KWARGS)
def ingest_apod() -> dict:
    lock = _acquire_lock("apod")
    if not lock:
        return {"skipped": True}
    try:
        from .clients.apod import APODClient
        from .transformers.apod import APODTransformer
        try:
            raw = APODClient().fetch_today()
        except (CircuitOpenError, QuotaExhaustedError) as exc:
            logger.warning("ingest_apod short-circuited: %s", exc)
            return {"skipped": True, "reason": str(exc)}
        entry = APODTransformer(raw).to_model()
        from apps.games.services import generate_apod_mission
        generate_apod_mission(entry)
        from apps.games.serializers import TodayPayloadSerializer
        cache.set("nasa:today", TodayPayloadSerializer.build(entry), timeout=3600)
        return {"ok": True, "date": entry.date.isoformat()}
    finally:
        _safe_release(lock)


# --------------------------------------------------------------------------- #
# Mars Rover Photos (Phase 4)
# --------------------------------------------------------------------------- #

@shared_task(**_RETRY_KWARGS)
def ingest_mars() -> dict:
    lock = _acquire_lock("mars")
    if not lock:
        return {"skipped": True}
    try:
        from .clients.mars import MarsRoverClient
        from .transformers.mars import MarsPhotoTransformer
        try:
            photos = MarsRoverClient().fetch_latest("perseverance")
        except (CircuitOpenError, QuotaExhaustedError) as exc:
            logger.warning("ingest_mars short-circuited: %s", exc)
            return {"skipped": True, "reason": str(exc)}
        entries = MarsPhotoTransformer(photos).to_models(limit=20)
        from apps.games.services import generate_mars_missions
        generate_mars_missions(entries)
        return {"ok": True, "count": len(entries)}
    finally:
        _safe_release(lock)


# --------------------------------------------------------------------------- #
# NeoWs — Near Earth Objects (Phase 4)
# --------------------------------------------------------------------------- #

@shared_task(**_RETRY_KWARGS)
def ingest_neows() -> dict:
    lock = _acquire_lock("neows")
    if not lock:
        return {"skipped": True}
    try:
        from .clients.neows import NeoWsClient
        from .transformers.neows import NeoWsTransformer
        try:
            feed = NeoWsClient().fetch_today()
        except (CircuitOpenError, QuotaExhaustedError) as exc:
            logger.warning("ingest_neows short-circuited: %s", exc)
            return {"skipped": True, "reason": str(exc)}
        neos = NeoWsTransformer(feed).to_models()
        from apps.games.services import generate_neo_missions
        generate_neo_missions(neos)
        cache.set("neo:approaching_count", len(neos), timeout=7200)
        return {"ok": True, "count": len(neos)}
    finally:
        _safe_release(lock)


# --------------------------------------------------------------------------- #
# EPIC — Earth observation (Phase 4)
# --------------------------------------------------------------------------- #

@shared_task(**_RETRY_KWARGS)
def ingest_epic() -> dict:
    lock = _acquire_lock("epic")
    if not lock:
        return {"skipped": True}
    try:
        from .clients.epic import EPICClient
        from .transformers.epic import EPICTransformer
        try:
            images = EPICClient().fetch_recent()
        except (CircuitOpenError, QuotaExhaustedError) as exc:
            logger.warning("ingest_epic short-circuited: %s", exc)
            return {"skipped": True, "reason": str(exc)}
        entries = EPICTransformer(images).to_models(limit=12)
        from apps.games.services import generate_epic_missions
        generate_epic_missions(entries)
        return {"ok": True, "count": len(entries)}
    finally:
        _safe_release(lock)


# --------------------------------------------------------------------------- #
# Exoplanets (Phase 4 — weekly)
# --------------------------------------------------------------------------- #

@shared_task(**_RETRY_KWARGS)
def ingest_exoplanets() -> dict:
    lock = _acquire_lock("exoplanets", timeout=600)
    if not lock:
        return {"skipped": True}
    try:
        from .clients.exoplanet import ExoplanetClient
        from .transformers.exoplanet import ExoplanetTransformer
        try:
            records = ExoplanetClient().fetch_confirmed(limit=100)
        except (CircuitOpenError, QuotaExhaustedError) as exc:
            logger.warning("ingest_exoplanets short-circuited: %s", exc)
            return {"skipped": True, "reason": str(exc)}
        entries = ExoplanetTransformer(records).to_models()
        from apps.games.services import generate_exoplanet_missions
        generate_exoplanet_missions(entries)
        return {"ok": True, "count": len(entries)}
    finally:
        _safe_release(lock)
