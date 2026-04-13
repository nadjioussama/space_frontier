"""Leaderboard service backed by Redis sorted sets. PLAN §8.4, §3.8.

Keys:
  leaderboard:weekly        — global weekly XP ranking
  leaderboard:planet:{slug} — per-planet XP ranking

Weekly reset happens via a Celery Beat task.
Pseudonyms only — display names go through moderation (Phase 3).
No PvP; all competition is vs. personal best or collective goals.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Optional

from django.conf import settings
from redis import Redis

logger = logging.getLogger(__name__)

_redis = Redis.from_url(settings.REDIS_URL)

WEEKLY_KEY = "leaderboard:weekly"
PLANET_KEY_PREFIX = "leaderboard:planet:"
TOP_N = 50


def add_xp(player_id: int, xp: int, planet_slug: str = "") -> None:
    """Increment a player's score on the weekly and optionally planet board."""
    _redis.zincrby(WEEKLY_KEY, xp, str(player_id))
    if planet_slug:
        _redis.zincrby(f"{PLANET_KEY_PREFIX}{planet_slug}", xp, str(player_id))


def get_weekly_top(n: int = TOP_N) -> list[dict]:
    """Return top-N players on the weekly board as [{player_id, score, rank}, ...]."""
    raw = _redis.zrevrange(WEEKLY_KEY, 0, n - 1, withscores=True)
    return [
        {"player_id": int(pid), "score": int(score), "rank": i + 1}
        for i, (pid, score) in enumerate(raw)
    ]


def get_planet_top(planet_slug: str, n: int = TOP_N) -> list[dict]:
    key = f"{PLANET_KEY_PREFIX}{planet_slug}"
    raw = _redis.zrevrange(key, 0, n - 1, withscores=True)
    return [
        {"player_id": int(pid), "score": int(score), "rank": i + 1}
        for i, (pid, score) in enumerate(raw)
    ]


def get_player_rank(player_id: int, key: str = WEEKLY_KEY) -> Optional[dict]:
    """Return {rank, score} for a specific player, or None if not ranked."""
    score = _redis.zscore(key, str(player_id))
    if score is None:
        return None
    rank = _redis.zrevrank(key, str(player_id))
    return {"rank": (rank or 0) + 1, "score": int(score)}


def reset_weekly() -> int:
    """Archive and clear the weekly board. Returns number of entries cleared."""
    # Archive key for historical reference
    archive_key = f"leaderboard:archive:{datetime.utcnow().strftime('%Y-W%W')}"
    count = _redis.zcard(WEEKLY_KEY)
    if count > 0:
        _redis.copy(WEEKLY_KEY, archive_key)
        _redis.expire(archive_key, int(timedelta(days=90).total_seconds()))
    _redis.delete(WEEKLY_KEY)
    logger.info("Weekly leaderboard reset: %d entries archived to %s", count, archive_key)
    return count
