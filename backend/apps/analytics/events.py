"""Event taxonomy + PII-stripping validation. PLAN §24.2.

Every event passes through `validate()` before it touches Redis. This is the
single chokepoint where we guarantee no child PII enters the analytics pipeline.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any

# Allow-list of event types and the payload keys each may carry. Anything not
# listed is dropped — "minimal collection" (§24.1) is enforced structurally.
EVENT_SCHEMA: dict[str, set[str]] = {
    "session.started":          {"device_type", "screen_size", "is_returning"},
    "session.ended":            {"duration_seconds", "screens_visited", "missions_played"},
    "mission.started":          {"mission_id", "planet_id", "game_type", "difficulty_level"},
    "mission.completed":        {"mission_id", "score", "time_seconds", "attempts", "hints_used"},
    "mission.abandoned":        {"mission_id", "time_before_abandon", "last_screen"},
    "quiz.answered":            {"quiz_id", "mission_id", "is_correct", "time_to_answer_ms", "hint_tier_used", "concept"},
    "jigsaw.completed":         {"puzzle_id", "piece_count", "time_seconds", "misplacements"},
    "collection.earned":        {"item_type", "item_id", "earned_from_mission"},
    "navigation.planet_visited": {"planet_id", "source_screen"},
    "dda.adjustment":           {"direction", "old_level", "new_level", "trigger_reason"},
    "streak.updated":           {"new_streak", "previous_streak"},
    "onboarding.step_completed": {"step_number", "time_on_step"},
    "break_reminder.shown":     {"session_duration_at_trigger"},
    "break_reminder.accepted":  {"session_duration_at_trigger"},
    "content.nasa_image_viewed": {"content_type", "content_id", "view_duration_ms"},
    "error.game_crash":         {"game_type", "error_code", "device_info"},
    "experiment.exposed":       {"experiment", "variant"},
}

# Payload keys that must NEVER appear (defensive — schema already excludes them,
# but a buggy client could send extras).
_PII_KEYS = {"name", "display_name", "email", "ip", "address", "location", "dob", "phone"}

AGE_GROUPS = {"6-8", "9-11", "12-14"}


@dataclass(slots=True)
class AnalyticsEvent:
    event_type: str
    player_id: str
    session_id: str
    age_group: str
    timestamp: datetime
    payload: dict[str, Any] = field(default_factory=dict)

    def to_record(self) -> dict[str, Any]:
        d = asdict(self)
        d["timestamp"] = self.timestamp.isoformat()
        return d


def validate(raw: dict[str, Any], *, player_id: uuid.UUID | None, age_group: str | None) -> AnalyticsEvent | None:
    """Return a sanitized event, or ``None`` if the event must be dropped.

    Never raises on bad client input — analytics must not break gameplay.
    """
    etype = raw.get("event_type")
    allowed = EVENT_SCHEMA.get(etype)
    if allowed is None:
        return None

    payload = raw.get("payload") or {}
    if not isinstance(payload, dict):
        return None
    clean = {k: v for k, v in payload.items() if k in allowed and k not in _PII_KEYS}

    # Strings capped to 200 chars — prevents free-text smuggling.
    for k, v in list(clean.items()):
        if isinstance(v, str):
            clean[k] = v[:200]

    ag = age_group if age_group in AGE_GROUPS else "unknown"

    try:
        sid = str(uuid.UUID(str(raw.get("session_id"))))
    except (ValueError, TypeError):
        return None

    return AnalyticsEvent(
        event_type=etype,
        player_id=str(player_id) if player_id else str(uuid.UUID(int=0)),
        session_id=sid,
        age_group=ag,
        timestamp=datetime.now(timezone.utc),  # server clock, never trust client
        payload=clean,
    )
