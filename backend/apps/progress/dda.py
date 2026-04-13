"""Dynamic Difficulty Adjustment engine. PLAN §25.

State lives in Redis (hot path); Postgres `Attempt` table is the durable fallback.
The DDA tracks a rolling window of recent answers per player and adjusts the
difficulty level (1-10) based on accuracy thresholds and frustration streaks.

Integration: called from `apps.progress.services.record_attempt` after every
mission submission. The returned `DDAState.current_level` is forwarded to the
frontend so it can request appropriately-leveled content next time.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Optional

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

WINDOW_SIZE = 10
INCREASE_THRESHOLD = 0.80
DECREASE_THRESHOLD = 0.50
FRUSTRATION_STREAK = 3
COOLDOWN_ACTIONS = 5
MIN_LEVEL = 1
MAX_LEVEL = 10

_DDA_KEY_PREFIX = "dda:"
_DDA_TTL = 7 * 24 * 3600  # 7 days


@dataclass
class DDAState:
    recent_results: list[bool] = field(default_factory=list)
    current_level: int = 3
    actions_since_adjustment: int = 0
    topic_levels: dict[str, int] = field(default_factory=dict)

    @property
    def accuracy(self) -> float:
        if not self.recent_results:
            return 0.5
        weights = [1.0 + (i * 0.1) for i in range(len(self.recent_results))]
        weighted_correct = sum(w for w, r in zip(weights, self.recent_results) if r)
        return weighted_correct / sum(weights)

    @property
    def has_frustration_streak(self) -> bool:
        if len(self.recent_results) < FRUSTRATION_STREAK:
            return False
        return not any(self.recent_results[-FRUSTRATION_STREAK:])

    def to_dict(self) -> dict:
        return {
            "recent_results": self.recent_results,
            "current_level": self.current_level,
            "actions_since_adjustment": self.actions_since_adjustment,
            "topic_levels": self.topic_levels,
        }

    @classmethod
    def from_dict(cls, data: dict) -> DDAState:
        return cls(
            recent_results=data.get("recent_results", []),
            current_level=data.get("current_level", 3),
            actions_since_adjustment=data.get("actions_since_adjustment", 0),
            topic_levels=data.get("topic_levels", {}),
        )


def _key(player_id: int | str) -> str:
    return f"{_DDA_KEY_PREFIX}{player_id}"


def get_state(player_id: int | str) -> DDAState:
    """Load DDA state from Redis. Cold start returns default level 3."""
    raw = cache.get(_key(player_id))
    if raw:
        return DDAState.from_dict(raw)
    return DDAState(current_level=3)


def save_state(player_id: int | str, state: DDAState) -> None:
    cache.set(_key(player_id), state.to_dict(), timeout=_DDA_TTL)


def record_answer(player_id: int | str, is_correct: bool, topic: str = "") -> DDAState:
    """Record an answer, adjust difficulty if thresholds are met. Returns updated state."""
    state = get_state(player_id)
    state.recent_results.append(is_correct)
    state.recent_results = state.recent_results[-WINDOW_SIZE:]
    state.actions_since_adjustment += 1

    old_level = state.current_level
    adjusted = False

    # Frustration streak: immediate decrease, bypass cooldown
    if state.has_frustration_streak and state.current_level > MIN_LEVEL:
        state.current_level -= 1
        state.actions_since_adjustment = 0
        adjusted = True
        logger.info("DDA: player %s frustration decrease -> level %d", player_id, state.current_level)

    # Normal threshold check with cooldown
    elif state.actions_since_adjustment >= COOLDOWN_ACTIONS:
        if state.accuracy > INCREASE_THRESHOLD and state.current_level < MAX_LEVEL:
            state.current_level += 1
            state.actions_since_adjustment = 0
            adjusted = True
        elif state.accuracy < DECREASE_THRESHOLD and state.current_level > MIN_LEVEL:
            state.current_level -= 1
            state.actions_since_adjustment = 0
            adjusted = True

    if topic and adjusted:
        state.topic_levels[topic] = state.current_level

    save_state(player_id, state)
    return state


def get_content_config(game_type: str, level: int) -> dict:
    """Return game-type-specific difficulty parameters for the given level. PLAN §25.3."""
    configs = {
        "quiz": {
            "choices": 2 if level <= 3 else 4,
            "hint_tiers": 3 if level <= 6 else 1,
            "auto_nudge_seconds": 15 if level <= 3 else (30 if level <= 6 else None),
            "time_limit": None if level <= 6 else 45,
            "question_difficulty_max": level,
        },
        "jigsaw": {
            "piece_count": 12 if level <= 3 else (24 if level <= 6 else 48),
            "rotation_enabled": level > 3,
            "preview_enabled": level <= 6,
            "edge_hints": level <= 6,
        },
        "action": {
            "speed_multiplier": round(0.5 + (level - 1) * 0.11, 2),
            "obstacle_density": round(3 + (level - 1) * 0.6, 1),
            "combo_patterns": level > 6,
        },
    }
    return configs.get(game_type, {})
