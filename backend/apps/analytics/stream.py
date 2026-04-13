"""Redis Streams buffer between the ingest endpoint and Postgres. PLAN §24.3.

Gameplay latency must never depend on analytics writes, so the API view does an
O(1) XADD and returns. A Celery worker drains the stream into the partitioned
table in batches.
"""
from __future__ import annotations

import json

from django.conf import settings
from redis import Redis

_redis = Redis.from_url(settings.REDIS_URL)

STREAM = getattr(settings, "ANALYTICS_STREAM_KEY", "nse:analytics:events")
GROUP = "analytics-writer"
CONSUMER = "worker"
MAXLEN = 100_000  # cap stream size; trimmed approximately


def push(record: dict) -> None:
    try:
        _redis.xadd(STREAM, {"e": json.dumps(record)}, maxlen=MAXLEN, approximate=True)
    except Exception:
        # Analytics must never break gameplay — silently drop if Redis is unavailable
        pass


def ensure_group() -> None:
    try:
        _redis.xgroup_create(STREAM, GROUP, id="0", mkstream=True)
    except Exception:
        pass  # BUSYGROUP — already exists


def read_batch(count: int = 500, block_ms: int = 2000) -> list[tuple[bytes, dict]]:
    ensure_group()
    resp = _redis.xreadgroup(GROUP, CONSUMER, {STREAM: ">"}, count=count, block=block_ms)
    out: list[tuple[bytes, dict]] = []
    for _stream, entries in resp or []:
        for msg_id, fields in entries:
            try:
                out.append((msg_id, json.loads(fields[b"e"])))
            except (KeyError, ValueError):
                _redis.xack(STREAM, GROUP, msg_id)
    return out


def ack(ids: list[bytes]) -> None:
    if ids:
        _redis.xack(STREAM, GROUP, *ids)
