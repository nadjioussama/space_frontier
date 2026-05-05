"""Anomaly detection rules -> Slack. PLAN §27.5.

Each rule is a pure function returning ``None`` (healthy) or a human-readable
string (fire). The runner posts fires to Slack and records them in cache so we
don't re-page on every 15-minute tick.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Callable

import requests
from django.conf import settings
from django.core.cache import cache

from . import rollups
from .models import MissionRollup

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Rule:
    name: str
    severity: str
    channel: str
    check: Callable[[], str | None]


def _dau_drop() -> str | None:
    today, last_week = date.today(), date.today() - timedelta(days=7)
    now, prev = rollups.dau_on(today), rollups.dau_on(last_week)
    if prev >= 50 and now < prev * 0.80:
        return f"DAU {now} is {100 - now * 100 // prev}% below same weekday last week ({prev})"
    return None


def _mission_completion_crash() -> str | None:
    today, yday = date.today(), date.today() - timedelta(days=1)
    bad = []
    for mid in MissionRollup.objects.filter(date=today).values_list("mission_id", flat=True).distinct():
        cur = rollups.mission_completion_rate(mid, today)
        prev = rollups.mission_completion_rate(mid, yday)
        if cur is not None and prev and prev > 0.2 and cur < prev * 0.75:
            bad.append(f"mission {mid}: {prev:.0%}→{cur:.0%}")
    return "Completion-rate crash: " + "; ".join(bad) if bad else None


def _dda_oscillation() -> str | None:
    from django.db import connection
    with connection.cursor() as cur:
        cur.execute(
            "WITH per_session AS ("
            "  SELECT session_id, COUNT(*) AS changes FROM analytics_rawevent "
            "  WHERE event_type='dda.adjustment' AND \"timestamp\"::date = CURRENT_DATE "
            "  GROUP BY 1) "
            "SELECT COUNT(*) FILTER (WHERE changes >= 3), COUNT(*) FROM per_session;"
        )
        bad, total = cur.fetchone()
    if total and bad / total > 0.10:
        return f"{bad}/{total} sessions had ≥3 DDA swings today"
    return None


def _quiz_broken() -> str | None:
    ids = rollups.broken_quizzes(date.today(), accuracy_max=0.10, min_attempts=50)
    return f"Quiz questions <10% accuracy: {sorted(ids)}" if ids else None


def _onboarding_dropout() -> str | None:
    funnel = rollups.onboarding_funnel(date.today())
    weak = {s: r for s, r in funnel.items() if r < 0.70}
    return f"Onboarding steps below 70%: {weak}" if weak else None


def _session_length_anomaly() -> str | None:
    today_val = rollups.avg_session_seconds(date.today())
    base = rollups.rolling_avg(rollups.avg_session_seconds, days=7)
    if base and abs(today_val - base) / base > 0.30:
        return f"Avg session {today_val:.0f}s vs 7-day avg {base:.0f}s (>30% delta)"
    return None


ALERT_RULES: list[Rule] = [
    Rule("dau_drop",                 "high",   "#analytics-alerts", _dau_drop),
    Rule("mission_completion_crash", "high",   "#game-design",      _mission_completion_crash),
    Rule("dda_oscillation",          "medium", "#game-design",      _dda_oscillation),
    Rule("quiz_broken",              "medium", "#content-team",     _quiz_broken),
    Rule("onboarding_dropout",       "high",   "#product",          _onboarding_dropout),
    Rule("session_length_anomaly",   "medium", "#analytics-alerts", _session_length_anomaly),
]

_DEDUP_TTL = 60 * 60 * 6  # don't repeat the same alert for 6h


def _post_slack(channel: str, text: str) -> None:
    url = getattr(settings, "SLACK_WEBHOOK_URL", "")
    if not url:
        logger.warning("[slack disabled] %s %s", channel, text)
        return
    requests.post(url, json={"channel": channel, "text": text}, timeout=5)


def run_alert_rules() -> list[str]:
    fired: list[str] = []
    for rule in ALERT_RULES:
        try:
            msg = rule.check()
        except Exception:
            logger.exception("alert rule %s failed", rule.name)
            continue
        if not msg:
            continue
        key = f"alert:fired:{rule.name}:{date.today()}"
        if cache.get(key):
            continue
        cache.set(key, 1, _DEDUP_TTL)
        _post_slack(rule.channel, f":rotating_light: *[{rule.severity}] {rule.name}* — {msg}")
        fired.append(rule.name)
    return fired
