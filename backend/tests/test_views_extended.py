"""Extended view tests covering edge cases not in existing test files."""
from __future__ import annotations

import uuid
from unittest import mock

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from apps.games.models import JigsawPuzzle, Mission, Quiz
from apps.games.services import generate_apod_mission
from apps.progress.models import Constellation, PlayerStar, SkillStar

from .factories import make_apod, make_mission, make_planet, make_player


class PlanetDetailViewTests(TestCase):
    def setUp(self) -> None:
        cache.clear()
        self.planet = make_planet(slug="view-planet")

    def test_returns_missions_sorted_by_created_at(self):
        """Missions should be ordered newest first."""
        m1 = make_mission(slug="old-mission", planet=self.planet, title="Old")
        m2 = make_mission(slug="new-mission", planet=self.planet, title="New")
        resp = self.client.get(reverse("planet-detail", args=["view-planet"]))
        self.assertEqual(resp.status_code, 200)
        slugs = [m["slug"] for m in resp.json()["missions"]]
        # Newer mission should appear first (ordered by -created_at)
        self.assertEqual(slugs[0], "new-mission")


class MissionDetailViewCacheTests(TestCase):
    def setUp(self) -> None:
        cache.clear()
        self.entry = make_apod()
        self.mission = generate_apod_mission(self.entry)

    def test_caching_returns_hit_header(self):
        url = reverse("mission-detail", args=[self.mission.slug])
        r1 = self.client.get(url)
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r1["X-Cache"], "MISS")

        r2 = self.client.get(url)
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(r2["X-Cache"], "HIT")

    def test_cache_contains_correct_data(self):
        url = reverse("mission-detail", args=[self.mission.slug])
        self.client.get(url)
        # Second call from cache should return identical data
        r = self.client.get(url)
        self.assertEqual(r.json()["slug"], self.mission.slug)


class AttemptViewEdgeCaseTests(TestCase):
    def setUp(self) -> None:
        cache.clear()
        self.entry = make_apod()
        self.mission = generate_apod_mission(self.entry)

    @mock.patch("apps.progress.leaderboard.add_xp")
    def test_empty_answers_list_returns_zero_xp_for_quiz_portion(self, _):
        """Posting with empty quiz_answers and no jigsaw gives 0 XP."""
        resp = self.client.post(
            reverse("mission-attempt", args=[self.mission.slug]),
            data={"quiz_answers": [], "jigsaw_completed": False},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["xp_earned"], 0)
        self.assertEqual(body["results"], [])

    @mock.patch("apps.progress.leaderboard.add_xp")
    def test_jigsaw_only_completion_gives_partial_xp(self, _):
        """Completing jigsaw without answering quizzes gives 40% XP."""
        resp = self.client.post(
            reverse("mission-attempt", args=[self.mission.slug]),
            data={"quiz_answers": [], "jigsaw_completed": True},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        # XP = mission.xp_reward * (0.6 * 0/1 + 0.4 * 1) = 50 * 0.4 = 20
        self.assertEqual(body["xp_earned"], 20)

    @mock.patch("apps.progress.leaderboard.add_xp")
    def test_null_quiz_answers_treated_as_empty(self, _):
        """Sending null quiz_answers should not error."""
        resp = self.client.post(
            reverse("mission-attempt", args=[self.mission.slug]),
            data={"quiz_answers": None, "jigsaw_completed": False},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["xp_earned"], 0)


@mock.patch("apps.progress.leaderboard.get_planet_top")
class LeaderboardPlanetViewTests(TestCase):
    def setUp(self) -> None:
        cache.clear()

    def test_returns_planet_specific_data(self, mock_top):
        player = make_player(username="planet-lb-player")
        mock_top.return_value = [
            {"player_id": player.id, "score": 150, "rank": 1},
        ]
        resp = self.client.get(reverse("leaderboard-planet", args=["earth"]))
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["planet"], "earth")
        self.assertEqual(body["period"], "weekly")
        self.assertEqual(len(body["entries"]), 1)
        mock_top.assert_called_once_with("earth", n=50)

    def test_empty_leaderboard(self, mock_top):
        mock_top.return_value = []
        resp = self.client.get(reverse("leaderboard-planet", args=["mars"]))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["entries"], [])


@mock.patch("apps.progress.leaderboard.add_xp")
class ConstellationListViewTests(TestCase):
    def setUp(self) -> None:
        cache.clear()
        self.constellation = Constellation.objects.create(
            slug="test-const", name="Test Constellation", topic="astronomy",
        )
        self.star = SkillStar.objects.create(
            constellation=self.constellation,
            slug="test-star",
            name="Test Star",
            xp_value=25,
        )

    def test_authenticated_player_sees_earned_stars(self, _):
        player = make_player(username="const-player")
        PlayerStar.objects.create(player=player, star=self.star)
        self.client.force_login(player)

        resp = self.client.get(reverse("constellation-list"))
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body[0]["earned_count"], 1)
        self.assertTrue(body[0]["stars"][0]["earned"])

    def test_anonymous_sees_no_earned_stars(self, _):
        resp = self.client.get(reverse("constellation-list"))
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body[0]["earned_count"], 0)
        self.assertFalse(body[0]["stars"][0]["earned"])


class DDAStateViewTests(TestCase):
    def setUp(self) -> None:
        cache.clear()

    def test_returns_config_with_quiz_and_jigsaw(self):
        player = make_player(username="dda-player")
        self.client.force_login(player)
        resp = self.client.get(reverse("dda-state"))
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIn("config", body)
        self.assertIn("quiz", body["config"])
        self.assertIn("jigsaw", body["config"])
        self.assertIn("level", body)
        self.assertIn("accuracy", body)
        self.assertIn("topic_levels", body)

    def test_requires_auth(self):
        resp = self.client.get(reverse("dda-state"))
        self.assertEqual(resp.status_code, 401)


class ExperimentAssignmentViewTests(TestCase):
    def setUp(self) -> None:
        cache.clear()

    def test_requires_auth(self):
        resp = self.client.get(reverse("experiments"))
        self.assertEqual(resp.status_code, 401)

    def test_authenticated_returns_200(self):
        player = make_player(username="exp-player")
        self.client.force_login(player)
        resp = self.client.get(reverse("experiments"))
        self.assertEqual(resp.status_code, 200)


class ProgressViewTests(TestCase):
    def setUp(self) -> None:
        cache.clear()

    def test_requires_auth(self):
        resp = self.client.get(reverse("progress-me"))
        self.assertEqual(resp.status_code, 401)

    @mock.patch("apps.progress.leaderboard.get_player_rank", return_value=None)
    @mock.patch("apps.progress.leaderboard.add_xp")
    def test_authenticated_returns_progress(self, _add, _rank):
        player = make_player(username="prog-player")
        self.client.force_login(player)
        resp = self.client.get(reverse("progress-me"))
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIn("total_xp", body)
        self.assertIn("rank", body)
        self.assertIn("dda_level", body)


class EventIngestViewExtendedTests(TestCase):
    def setUp(self) -> None:
        cache.clear()

    @mock.patch("apps.analytics.stream.push")
    def test_handles_empty_events_list(self, mock_push):
        resp = self.client.post(
            reverse("analytics-events"),
            data={"events": []},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 202)
        self.assertEqual(resp.json()["accepted"], 0)
        mock_push.assert_not_called()

    @mock.patch("apps.analytics.stream.push")
    def test_respects_max_batch_limit(self, mock_push):
        """Only the first MAX_BATCH (50) events should be processed."""
        from apps.analytics.views import MAX_BATCH
        session_id = str(uuid.uuid4())
        events = [
            {
                "event_type": "session.started",
                "session_id": session_id,
                "payload": {"device_type": "tablet"},
            }
            for _ in range(MAX_BATCH + 20)
        ]
        resp = self.client.post(
            reverse("analytics-events"),
            data={"events": events},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 202)
        # At most MAX_BATCH events should be accepted
        self.assertLessEqual(resp.json()["accepted"], MAX_BATCH)
        self.assertLessEqual(mock_push.call_count, MAX_BATCH)

    @mock.patch("apps.analytics.stream.push")
    def test_invalid_events_are_silently_dropped(self, mock_push):
        """Events with unknown types or missing session_id are dropped."""
        events = [
            {"event_type": "unknown.type", "session_id": str(uuid.uuid4()), "payload": {}},
            {"event_type": "session.started", "session_id": "not-a-uuid", "payload": {}},
        ]
        resp = self.client.post(
            reverse("analytics-events"),
            data={"events": events},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 202)
        self.assertEqual(resp.json()["accepted"], 0)
        mock_push.assert_not_called()
