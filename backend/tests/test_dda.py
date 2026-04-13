"""Dynamic Difficulty Adjustment engine. PLAN §25."""
from __future__ import annotations

from django.core.cache import cache
from django.test import SimpleTestCase

from apps.progress import dda


class DDAStateTests(SimpleTestCase):
    def test_accuracy_empty_is_neutral(self):
        self.assertEqual(dda.DDAState().accuracy, 0.5)

    def test_accuracy_weights_recent_answers_more(self):
        # 5 wrong then 5 right -> recency weighting pushes accuracy above 0.5
        s = dda.DDAState(recent_results=[False] * 5 + [True] * 5)
        self.assertGreater(s.accuracy, 0.5)

    def test_frustration_streak(self):
        s = dda.DDAState(recent_results=[True, False, False, False])
        self.assertTrue(s.has_frustration_streak)
        s2 = dda.DDAState(recent_results=[False, False, True])
        self.assertFalse(s2.has_frustration_streak)

    def test_roundtrip_dict(self):
        s = dda.DDAState(recent_results=[True, False], current_level=5,
                         actions_since_adjustment=2, topic_levels={"astronomy": 5})
        again = dda.DDAState.from_dict(s.to_dict())
        self.assertEqual(again.to_dict(), s.to_dict())


class DDAEngineTests(SimpleTestCase):
    PID = "test-player"

    def setUp(self) -> None:
        cache.delete(dda._key(self.PID))

    def tearDown(self) -> None:
        cache.delete(dda._key(self.PID))

    def test_cold_start_default_level(self):
        self.assertEqual(dda.get_state(self.PID).current_level, 3)

    def test_persists_across_calls(self):
        s = dda.get_state(self.PID)
        s.current_level = 7
        dda.save_state(self.PID, s)
        self.assertEqual(dda.get_state(self.PID).current_level, 7)

    def test_high_accuracy_increases_after_cooldown(self):
        for _ in range(dda.COOLDOWN_ACTIONS):
            state = dda.record_answer(self.PID, True)
        self.assertEqual(state.current_level, 4)
        self.assertEqual(state.actions_since_adjustment, 0)

    def test_low_accuracy_decreases_after_cooldown(self):
        # Alternate so frustration streak never triggers but accuracy < 0.5
        results = [False, True, False, False, True]
        assert len(results) == dda.COOLDOWN_ACTIONS
        for r in results:
            state = dda.record_answer(self.PID, r)
        self.assertEqual(state.current_level, 2)

    def test_frustration_streak_bypasses_cooldown(self):
        for _ in range(dda.FRUSTRATION_STREAK):
            state = dda.record_answer(self.PID, False)
        self.assertEqual(state.current_level, 2)
        self.assertLess(state.actions_since_adjustment, dda.COOLDOWN_ACTIONS)

    def test_level_clamped_at_min(self):
        s = dda.DDAState(current_level=dda.MIN_LEVEL,
                         recent_results=[False] * dda.FRUSTRATION_STREAK)
        dda.save_state(self.PID, s)
        state = dda.record_answer(self.PID, False)
        self.assertEqual(state.current_level, dda.MIN_LEVEL)

    def test_level_clamped_at_max(self):
        s = dda.DDAState(current_level=dda.MAX_LEVEL,
                         recent_results=[True] * dda.WINDOW_SIZE,
                         actions_since_adjustment=dda.COOLDOWN_ACTIONS - 1)
        dda.save_state(self.PID, s)
        state = dda.record_answer(self.PID, True)
        self.assertEqual(state.current_level, dda.MAX_LEVEL)

    def test_window_is_bounded(self):
        for _ in range(dda.WINDOW_SIZE * 3):
            state = dda.record_answer(self.PID, True)
        self.assertEqual(len(state.recent_results), dda.WINDOW_SIZE)

    def test_topic_level_recorded_on_adjust(self):
        for _ in range(dda.COOLDOWN_ACTIONS):
            state = dda.record_answer(self.PID, True, topic="astronomy")
        self.assertEqual(state.topic_levels.get("astronomy"), 4)


class ContentConfigTests(SimpleTestCase):
    def test_quiz_config_scales(self):
        easy = dda.get_content_config("quiz", 2)
        hard = dda.get_content_config("quiz", 9)
        self.assertEqual(easy["choices"], 2)
        self.assertEqual(hard["choices"], 4)
        self.assertIsNone(easy["time_limit"])
        self.assertEqual(hard["time_limit"], 45)

    def test_jigsaw_config_scales(self):
        self.assertEqual(dda.get_content_config("jigsaw", 1)["piece_count"], 12)
        self.assertEqual(dda.get_content_config("jigsaw", 5)["piece_count"], 24)
        self.assertEqual(dda.get_content_config("jigsaw", 9)["piece_count"], 48)
        self.assertFalse(dda.get_content_config("jigsaw", 2)["rotation_enabled"])
        self.assertTrue(dda.get_content_config("jigsaw", 5)["rotation_enabled"])

    def test_unknown_game_type(self):
        self.assertEqual(dda.get_content_config("unknown", 3), {})
