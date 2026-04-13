"""Small read helpers used by /metrics and anomaly alerts."""
from __future__ import annotations

from datetime import date, timedelta

from django.conf import settings
from django.core.cache import cache
from redis import Redis

from .models import DailyEngagementRollup, MissionRollup, QuizQuestionRollup

_redis = Redis.from_url(settings.REDIS_URL)


def current_dau() -> int:
    today = date.today()
    return sum(
        DailyEngagementRollup.objects.filter(date=today).values_list("dau", flat=True)
    )


def dau_on(d: date) -> int:
    return sum(DailyEngagementRollup.objects.filter(date=d).values_list("dau", flat=True))


def avg_session_seconds(d: date) -> float:
    rows = DailyEngagementRollup.objects.filter(date=d)
    vals = [r.avg_session_seconds for r in rows if r.sessions]
    return sum(vals) / len(vals) if vals else 0.0


def mission_completion_rate(mission_id: int, d: date) -> float | None:
    rows = MissionRollup.objects.filter(date=d, mission_id=mission_id)
    starts = sum(r.starts for r in rows)
    comps = sum(r.completions for r in rows)
    return comps / starts if starts else None


def broken_quizzes(d: date, *, accuracy_max: float, min_attempts: int) -> list[int]:
    out = []
    for r in QuizQuestionRollup.objects.filter(date=d, attempts__gte=min_attempts):
        if r.attempts and (r.correct_count / r.attempts) < accuracy_max:
            out.append(r.quiz_id)
    return out


def onboarding_funnel(d: date) -> dict[int, float]:
    """step -> completion rate vs step 1."""
    from django.db import connection
    with connection.cursor() as cur:
        cur.execute(
            "SELECT (payload->>'step_number')::int AS step, COUNT(DISTINCT player_id) "
            "FROM analytics_rawevent WHERE event_type='onboarding.step_completed' "
            "AND \"timestamp\"::date = %s GROUP BY 1 ORDER BY 1;",
            [d],
        )
        rows = cur.fetchall()
    if not rows:
        return {}
    base = rows[0][1] or 1
    return {step: cnt / base for step, cnt in rows}


def redis_hit_rate() -> float:
    info = _redis.info("stats")
    hits, misses = info.get("keyspace_hits", 0), info.get("keyspace_misses", 0)
    total = hits + misses
    return hits / total if total else 1.0


def nasa_quota_used() -> int:
    return int(cache.get("nasa:quota:hour", 0) or 0)


def rolling_avg(metric_fn, *, days: int) -> float:
    today = date.today()
    vals = [metric_fn(today - timedelta(days=i)) for i in range(1, days + 1)]
    vals = [v for v in vals if v]
    return sum(vals) / len(vals) if vals else 0.0
