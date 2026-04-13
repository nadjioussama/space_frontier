"""Phase 8 analytics: event validation + A/B bucketing determinism."""
from __future__ import annotations

import uuid

from django.test import SimpleTestCase

from apps.analytics.events import validate, EVENT_SCHEMA
from apps.analytics.ab_testing import _bucket


class EventValidationTests(SimpleTestCase):
    def _raw(self, **over):
        base = {
            "event_type": "mission.completed",
            "session_id": str(uuid.uuid4()),
            "payload": {"mission_id": 1, "score": 80, "time_seconds": 42,
                        "attempts": 1, "hints_used": 0},
        }
        base.update(over)
        return base

    def test_happy_path(self):
        ev = validate(self._raw(), player_id=uuid.uuid4(), age_group="9-11")
        self.assertIsNotNone(ev)
        self.assertEqual(ev.age_group, "9-11")
        self.assertEqual(set(ev.payload), EVENT_SCHEMA["mission.completed"])

    def test_unknown_event_type_dropped(self):
        self.assertIsNone(validate(self._raw(event_type="nope"), player_id=None, age_group=None))

    def test_pii_and_extra_keys_stripped(self):
        raw = self._raw()
        raw["payload"]["email"] = "kid@example.com"
        raw["payload"]["unexpected"] = "x"
        ev = validate(raw, player_id=uuid.uuid4(), age_group="6-8")
        self.assertNotIn("email", ev.payload)
        self.assertNotIn("unexpected", ev.payload)

    def test_bad_session_id_dropped(self):
        self.assertIsNone(validate(self._raw(session_id="not-a-uuid"), player_id=None, age_group=None))

    def test_unknown_age_group_normalized(self):
        ev = validate(self._raw(), player_id=None, age_group="adult")
        self.assertEqual(ev.age_group, "unknown")

    def test_string_payload_values_capped(self):
        raw = self._raw(event_type="error.game_crash",
                        payload={"game_type": "x" * 500, "error_code": "E1", "device_info": "d"})
        ev = validate(raw, player_id=None, age_group="6-8")
        self.assertEqual(len(ev.payload["game_type"]), 200)


class BucketingTests(SimpleTestCase):
    def test_deterministic(self):
        pid = uuid.uuid4()
        self.assertEqual(_bucket(pid, "exp-a"), _bucket(pid, "exp-a"))

    def test_distribution_roughly_uniform(self):
        hits = sum(1 for _ in range(2000) if _bucket(uuid.uuid4(), "exp") < 10)
        # ~10% of 2000 = 200; allow generous slack so the test isn't flaky.
        self.assertGreater(hits, 120)
        self.assertLess(hits, 280)
