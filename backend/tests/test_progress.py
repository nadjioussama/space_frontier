"""Progress services: rank, streak, record_attempt. PLAN §3.4, §3.3."""
from __future__ import annotations

from datetime import date, timedelta
from unittest import mock

from django.core.cache import cache
from django.test import SimpleTestCase, TestCase

from apps.progress import services
from apps.progress.models import Attempt, PlayerStreak

from .factories import make_apod, make_mission, make_player


class RankTests(SimpleTestCase):
    def test_thresholds(self):
        self.assertEqual(services._rank_for(0), "Cadet")
        self.assertEqual(services._rank_for(99), "Cadet")
        self.assertEqual(services._rank_for(100), "Pilot")
        self.assertEqual(services._rank_for(300), "Commander")
        self.assertEqual(services._rank_for(800), "Captain")
        self.assertEqual(services._rank_for(2000), "Admiral")
        self.assertEqual(services._rank_for(5000), "Legend")
        self.assertEqual(services._rank_for(999999), "Legend")


class TopicMappingTests(TestCase):
    def test_known_types(self):
        m = make_mission(mission_type="neo_defense")
        self.assertEqual(services._topic_for_mission(m), "planetary_defense")

    def test_unknown_falls_back(self):
        m = make_mission(slug="m2", mission_type="something_new")
        self.assertEqual(services._topic_for_mission(m), "astronomy")


class StreakTests(TestCase):
    def _seed(self, player, current, longest, last_play):
        PlayerStreak.objects.create(
            player=player, current_streak=current, longest_streak=longest,
            last_play_date=last_play,
        )

    def test_first_play(self):
        p = make_player()
        services._update_streak(p)
        s = PlayerStreak.objects.get(player=p)
        self.assertEqual(s.current_streak, 1)
        self.assertEqual(s.longest_streak, 1)
        self.assertEqual(s.last_play_date, date.today())

    def test_consecutive_day_increments(self):
        p = make_player()
        self._seed(p, current=3, longest=5, last_play=date.today() - timedelta(days=1))
        services._update_streak(p)
        s = PlayerStreak.objects.get(player=p)
        self.assertEqual(s.current_streak, 4)
        self.assertEqual(s.longest_streak, 5)

    def test_same_day_noop(self):
        p = make_player()
        self._seed(p, current=3, longest=5, last_play=date.today())
        services._update_streak(p)
        s = PlayerStreak.objects.get(player=p)
        self.assertEqual(s.current_streak, 3)

    def test_gap_resets(self):
        p = make_player()
        self._seed(p, current=7, longest=7, last_play=date.today() - timedelta(days=3))
        services._update_streak(p)
        s = PlayerStreak.objects.get(player=p)
        self.assertEqual(s.current_streak, 1)
        self.assertEqual(s.longest_streak, 7)

    def test_longest_updates_when_surpassed(self):
        p = make_player()
        self._seed(p, current=4, longest=4, last_play=date.today() - timedelta(days=1))
        services._update_streak(p)
        s = PlayerStreak.objects.get(player=p)
        self.assertEqual(s.current_streak, 5)
        self.assertEqual(s.longest_streak, 5)


@mock.patch("apps.progress.leaderboard.add_xp")
class RecordAttemptTests(TestCase):
    def setUp(self) -> None:
        cache.clear()
        self.player = make_player()
        self.mission = make_mission(apod=make_apod())

    def test_anonymous_creates_attempt_without_side_effects(self, mock_lb):
        snap = services.record_attempt(None, self.mission, xp=30,
                                       quiz_correct=2, quiz_total=3,
                                       jigsaw_completed=True)
        self.assertEqual(Attempt.objects.count(), 1)
        self.assertEqual(snap["total_xp"], 0)
        self.assertEqual(snap["rank"], "Cadet")
        mock_lb.assert_not_called()
        self.assertFalse(PlayerStreak.objects.filter(player=self.player).exists())

    def test_authenticated_full_pipeline(self, mock_lb):
        snap = services.record_attempt(self.player, self.mission, xp=40,
                                       quiz_correct=3, quiz_total=3,
                                       jigsaw_completed=True)
        self.assertEqual(Attempt.objects.filter(player=self.player).count(), 1)
        self.assertEqual(snap["total_xp"], 40)
        # Leaderboard updated with planet slug
        mock_lb.assert_called_once_with(self.player.id, 40, planet_slug="earth")
        # Streak created
        self.assertEqual(PlayerStreak.objects.get(player=self.player).current_streak, 1)
        # DDA reflected
        self.assertIn("level", snap["dda"])
        self.assertIn("accuracy", snap["dda"])

    @mock.patch("apps.progress.leaderboard.get_player_rank", return_value={"rank": 1, "score": 40})
    def test_get_player_progress_shape(self, _rank, _lb):
        services.record_attempt(self.player, self.mission, xp=40,
                                quiz_correct=2, quiz_total=3, jigsaw_completed=False)
        snap = services.get_player_progress(self.player)
        for key in ("total_xp", "rank", "attempt_count", "missions_completed",
                    "dda_level", "dda_accuracy", "leaderboard_rank",
                    "leaderboard_score", "streak", "longest_streak",
                    "earned_stars", "achievements"):
            self.assertIn(key, snap)
        self.assertEqual(snap["total_xp"], 40)
        self.assertEqual(snap["missions_completed"], 1)
