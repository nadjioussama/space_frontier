from __future__ import annotations

import logging
from datetime import date

from django.db.models import Sum

from apps.games.models import Mission
from .models import Attempt, PlayerStreak

logger = logging.getLogger(__name__)


def record_attempt(player, mission: Mission, *, xp: int, quiz_correct: int,
                   quiz_total: int = 0, jigsaw_completed: bool) -> dict:
    """Persist an attempt, update DDA/leaderboard/streak, return player snapshot.

    Phase 5 integrates DDA difficulty tracking, leaderboard updates, and
    streak maintenance alongside the basic attempt recording from Phase 1.
    """
    is_authed = player and player.is_authenticated

    # Get current DDA level for this player
    dda_level = 3
    if is_authed:
        from . import dda
        dda_state = dda.get_state(player.id)
        dda_level = dda_state.current_level

    attempt = Attempt.objects.create(
        player=player if is_authed else None,
        anon_id="",
        mission=mission,
        quiz_correct=quiz_correct,
        quiz_total=quiz_total,
        jigsaw_completed=jigsaw_completed,
        xp_earned=xp,
        difficulty_level=dda_level,
    )

    total_xp = 0
    dda_info = {"level": dda_level, "accuracy": 0.5}

    if is_authed:
        total_xp = player.attempts.aggregate(x=Sum("xp_earned"))["x"] or 0

        # DDA: record per-question results
        from . import dda
        topic = _topic_for_mission(mission)
        if quiz_total > 0:
            for i in range(quiz_total):
                is_correct = i < quiz_correct
                dda_state = dda.record_answer(player.id, is_correct, topic)
            dda_info = {
                "level": dda_state.current_level,
                "accuracy": round(dda_state.accuracy, 2),
            }

        # Leaderboard: add XP
        from . import leaderboard
        planet_slug = ""
        if mission.planet_id:
            planet_slug = mission.planet.slug
        leaderboard.add_xp(player.id, xp, planet_slug=planet_slug)

        # Streak: update daily play streak
        _update_streak(player)

    return {
        "attempt_id": attempt.id,
        "total_xp": total_xp,
        "rank": _rank_for(total_xp),
        "dda": dda_info,
    }


def _update_streak(player) -> None:
    """Update the player's daily play streak."""
    today = date.today()
    streak, created = PlayerStreak.objects.get_or_create(player=player)
    if streak.last_play_date == today:
        return  # already played today
    if streak.last_play_date and (today - streak.last_play_date).days == 1:
        streak.current_streak += 1
    elif streak.last_play_date and (today - streak.last_play_date).days > 1:
        streak.current_streak = 1  # streak broken
    else:
        streak.current_streak = 1  # first play
    streak.longest_streak = max(streak.longest_streak, streak.current_streak)
    streak.last_play_date = today
    streak.save(update_fields=["current_streak", "longest_streak", "last_play_date"])


def _topic_for_mission(mission: Mission) -> str:
    """Map mission type to a DDA topic."""
    mapping = {
        "apod_daily": "astronomy",
        "mars_rover": "geology",
        "neo_defense": "planetary_defense",
        "epic_observer": "earth_science",
        "exoplanet_explorer": "exoplanets",
        "cross_api": "astronomy",
    }
    return mapping.get(mission.mission_type, "astronomy")


def _rank_for(xp: int) -> str:
    for threshold, rank in [
        (5000, "Legend"), (2000, "Admiral"), (800, "Captain"),
        (300, "Commander"), (100, "Pilot"),
    ]:
        if xp >= threshold:
            return rank
    return "Cadet"


def get_player_progress(player) -> dict:
    """Full progress snapshot for the player profile endpoint."""
    if not player or not player.is_authenticated:
        return {}

    total_xp = player.attempts.aggregate(x=Sum("xp_earned"))["x"] or 0
    attempt_count = player.attempts.count()
    missions_completed = player.attempts.values("mission").distinct().count()

    from . import dda, leaderboard
    dda_state = dda.get_state(player.id)
    rank_info = leaderboard.get_player_rank(player.id)

    streak = PlayerStreak.objects.filter(player=player).first()
    earned_stars = player.earned_stars.count() if hasattr(player, "earned_stars") else 0
    achievements = player.achievements.count() if hasattr(player, "achievements") else 0

    return {
        "total_xp": total_xp,
        "rank": _rank_for(total_xp),
        "attempt_count": attempt_count,
        "missions_completed": missions_completed,
        "dda_level": dda_state.current_level,
        "dda_accuracy": round(dda_state.accuracy, 2),
        "leaderboard_rank": rank_info["rank"] if rank_info else None,
        "leaderboard_score": rank_info["score"] if rank_info else 0,
        "streak": streak.current_streak if streak else 0,
        "longest_streak": streak.longest_streak if streak else 0,
        "earned_stars": earned_stars,
        "achievements": achievements,
    }
