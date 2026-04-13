"""Celery tasks for Phase 5 progression features."""
from __future__ import annotations

import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def reset_weekly_leaderboard() -> dict:
    """Reset the weekly leaderboard. Runs every Monday at 00:00 UTC."""
    from . import leaderboard
    count = leaderboard.reset_weekly()
    return {"reset": True, "entries_archived": count}


@shared_task
def generate_cross_api_missions() -> dict:
    """Generate/refresh cross-API missions. Runs weekly."""
    from apps.games.services import generate_cross_api_missions
    missions = generate_cross_api_missions()
    return {"ok": True, "count": len(missions)}
