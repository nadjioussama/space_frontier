"""Celery tasks: drain stream -> partitioned table, refresh rollups, prune old
partitions, run anomaly checks, score experiments, warm caches. PLAN §24.3/§27.5/§6.4."""
from __future__ import annotations

import logging
from datetime import date, datetime, timedelta, timezone

from celery import shared_task
from django.db import connection

from . import stream
from .alerts import run_alert_rules
from .ab_testing import score_experiment
from .models import Experiment
from apps.games.views import TodayView, PlanetListView
from django.test import RequestFactory

logger = logging.getLogger(__name__)

RETENTION_DAYS = 90


def _partition_name(d: date) -> str:
    return f"analytics_rawevent_{d:%Y%m%d}"


def _ensure_partition(cur, d: date) -> None:
    name = _partition_name(d)
    lo, hi = d.isoformat(), (d + timedelta(days=1)).isoformat()
    cur.execute(
        f'CREATE TABLE IF NOT EXISTS {name} PARTITION OF analytics_rawevent '
        f"FOR VALUES FROM ('{lo}') TO ('{hi}');"
    )


@shared_task(queue="analytics")
def drain_event_stream(max_batches: int = 20) -> dict:
    """Move events from Redis Stream into Postgres in batches.

    Runs every minute from Beat; also safe to invoke ad-hoc. Idempotent via
    XACK — a crash mid-batch re-delivers unacked messages on the next run.
    """
    total = 0
    seen_days: set[date] = set()
    with connection.cursor() as cur:
        for _ in range(max_batches):
            batch = stream.read_batch()
            if not batch:
                break
            ids: list[bytes] = []
            for msg_id, rec in batch:
                ts = datetime.fromisoformat(rec["timestamp"])
                d = ts.date()
                if d not in seen_days:
                    _ensure_partition(cur, d)
                    seen_days.add(d)
                cur.execute(
                    'INSERT INTO analytics_rawevent '
                    '(event_type, player_id, session_id, age_group, "timestamp", payload) '
                    'VALUES (%s, %s, %s, %s, %s, %s)',
                    [rec["event_type"], rec["player_id"], rec["session_id"],
                     rec["age_group"], ts, json_dump(rec["payload"])],
                )
                ids.append(msg_id)
            stream.ack(ids)
            total += len(ids)
    return {"written": total}


def json_dump(obj):
    import json
    return json.dumps(obj)


@shared_task(queue="analytics")
def refresh_rollups() -> None:
    """REFRESH MATERIALIZED VIEW CONCURRENTLY for all rollups. Runs every 15min."""
    with connection.cursor() as cur:
        for mv in ("analytics_daily_engagement", "analytics_mission_rollup", "analytics_quiz_rollup"):
            cur.execute(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {mv};")


@shared_task(queue="analytics")
def manage_partitions() -> dict:
    """Create tomorrow's partition; drop partitions older than RETENTION_DAYS.
    Dropping a partition is O(1) DDL — no row-level DELETE. PLAN §24.1 retention."""
    today = datetime.now(timezone.utc).date()
    dropped = []
    with connection.cursor() as cur:
        _ensure_partition(cur, today)
        _ensure_partition(cur, today + timedelta(days=1))
        cutoff = today - timedelta(days=RETENTION_DAYS)
        cur.execute(
            "SELECT c.relname FROM pg_inherits i "
            "JOIN pg_class c ON c.oid = i.inhrelid "
            "JOIN pg_class p ON p.oid = i.inhparent "
            "WHERE p.relname = 'analytics_rawevent';"
        )
        for (name,) in cur.fetchall():
            try:
                d = datetime.strptime(name.removeprefix("analytics_rawevent_"), "%Y%m%d").date()
            except ValueError:
                continue
            if d < cutoff:
                cur.execute(f"DROP TABLE IF EXISTS {name};")
                dropped.append(name)
    return {"dropped": dropped}


@shared_task(queue="analytics")
def run_anomaly_checks() -> dict:
    fired = run_alert_rules()
    return {"alerts": fired}


@shared_task(queue="analytics")
def score_running_experiments() -> dict:
    n = 0
    for exp in Experiment.objects.filter(status="running"):
        score_experiment(exp)
        n += 1
    return {"scored": n}


@shared_task
def warm_caches() -> dict:
    """Rebuild hot Redis keys after a cold start / failover. PLAN §6.4, §11.10.

    Calls the same view-layer code paths a real request would, so the cache
    contents match exactly what clients will read.
    """
    rf = RequestFactory()
    warmed = 0
    for view, path in ((TodayView, "/api/v1/nasa/today/"), (PlanetListView, "/api/v1/planets/")):
        try:
            view.as_view()(rf.get(path))
            warmed += 1
        except Exception:  # pragma: no cover — warming is best-effort
            logger.exception("warm_caches: %s failed", path)
    return {"warmed": warmed}
