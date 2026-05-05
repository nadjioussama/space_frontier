"""HTTP-level API tests beyond the walking-skeleton smoke test."""
from __future__ import annotations

import uuid
from unittest import mock

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from apps.games.models import Quiz
from apps.games.services import generate_apod_mission
from apps.progress.models import Constellation, SkillStar

from .factories import make_apod, make_parent, make_player


class HealthTests(TestCase):
    def test_health(self):
        resp = self.client.get(reverse("health"))
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["status"], "ok")
        self.assertIn(body["nasa_circuit"], {"CLOSED", "OPEN", "HALF_OPEN"})


class GameEndpointTests(TestCase):
    def setUp(self) -> None:
        cache.clear()
        self.entry = make_apod()
        self.mission = generate_apod_mission(self.entry)

    def test_today_503_when_empty(self):
        cache.clear()
        from apps.nasa_ingest.models import APODEntry
        APODEntry.objects.all().delete()
        resp = self.client.get(reverse("nasa-today"))
        self.assertEqual(resp.status_code, 503)

    def test_today_caches(self):
        r1 = self.client.get(reverse("nasa-today"))
        self.assertEqual(r1["X-Cache"], "MISS")
        r2 = self.client.get(reverse("nasa-today"))
        self.assertEqual(r2["X-Cache"], "HIT")

    def test_planet_list_and_detail(self):
        resp = self.client.get(reverse("planet-list"))
        self.assertEqual(resp.status_code, 200)
        slugs = {p["slug"] for p in resp.json()}
        self.assertIn("earth", slugs)

        resp = self.client.get(reverse("planet-detail", args=["earth"]))
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["planet"]["slug"], "earth")
        self.assertGreaterEqual(len(body["missions"]), 1)

    def test_planet_detail_404(self):
        resp = self.client.get(reverse("planet-detail", args=["pluto"]))
        self.assertEqual(resp.status_code, 404)

    def test_mission_detail_options_contain_correct_answer(self):
        resp = self.client.get(reverse("mission-detail", args=[self.mission.slug]))
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        for q in body["quizzes"]:
            stored = Quiz.objects.get(id=q["id"])
            self.assertIn(stored.correct_answer, q["options"])
            # Correct answer must not leak as a separate field
            self.assertNotIn("correct_answer", q)

    def test_mission_detail_404(self):
        resp = self.client.get(reverse("mission-detail", args=["nope"]))
        self.assertEqual(resp.status_code, 404)

    def test_attempt_rejects_non_list(self):
        resp = self.client.post(
            reverse("mission-attempt", args=[self.mission.slug]),
            data={"quiz_answers": "not-a-list"},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_attempt_partial_credit(self):
        quizzes = list(Quiz.objects.filter(mission=self.mission))
        answers = [
            {"quiz_id": quizzes[0].id, "answer": quizzes[0].correct_answer},
            {"quiz_id": quizzes[1].id, "answer": "wrong"},
        ]
        resp = self.client.post(
            reverse("mission-attempt", args=[self.mission.slug]),
            data={"quiz_answers": answers, "jigsaw_completed": False},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        results = {r["quiz_id"]: r["correct"] for r in body["results"]}
        self.assertTrue(results[quizzes[0].id])
        self.assertFalse(results[quizzes[1].id])
        # 1 of 2 correct, no jigsaw -> 50 * 0.6 * 0.5 = 15
        self.assertEqual(body["xp_earned"], 15)

    def test_attempt_unknown_quiz_id(self):
        resp = self.client.post(
            reverse("mission-attempt", args=[self.mission.slug]),
            data={"quiz_answers": [{"quiz_id": 99999, "answer": "x"}]},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.json()["results"][0]["correct"])


class UserEndpointTests(TestCase):
    def test_profile_requires_auth(self):
        resp = self.client.get(reverse("player-profile"))
        self.assertEqual(resp.status_code, 401)

    def test_profile_returns_player(self):
        p = make_player()
        self.client.force_login(p)
        resp = self.client.get(reverse("player-profile"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["username"], "kid1")
        self.assertTrue(resp.json()["needs_parental_consent"])

    def test_full_coppa_flow(self):
        # 1. register parent
        resp = self.client.post(reverse("parent-register"),
                                {"email": "p@x.com", "full_name": "Pat"},
                                content_type="application/json")
        self.assertEqual(resp.status_code, 201)
        parent_id = resp.json()["parent_id"]
        # 2. verify
        resp = self.client.post(reverse("parent-verify"),
                                {"parent_id": parent_id},
                                content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        # 3. grant consent for a player
        player = make_player()
        resp = self.client.post(reverse("consent-grant"),
                                {"parent_email": "p@x.com", "player_id": player.id},
                                content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()["coppa_consent_given"])

    def test_consent_blocked_for_unverified_parent(self):
        make_parent(email="p@x.com", verified=False)
        player = make_player()
        resp = self.client.post(reverse("consent-grant"),
                                {"parent_email": "p@x.com", "player_id": player.id},
                                content_type="application/json")
        self.assertEqual(resp.status_code, 403)

    def test_name_change_endpoint(self):
        p = make_player()
        self.client.force_login(p)
        resp = self.client.post(reverse("name-change"),
                                {"display_name": "RocketKid"},
                                content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["decision"], "pending")  # under-13, no consent

    def test_name_change_rejected(self):
        p = make_player()
        self.client.force_login(p)
        resp = self.client.post(reverse("name-change"),
                                {"display_name": "admin"},
                                content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["decision"], "rejected")


@mock.patch("apps.progress.leaderboard.add_xp")
class ProgressEndpointTests(TestCase):
    def setUp(self) -> None:
        cache.clear()
        self.player = make_player()
        self.client.force_login(self.player)

    def test_dda_state(self, _):
        resp = self.client.get(reverse("dda-state"))
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["level"], 3)
        self.assertIn("piece_count", body["config"]["jigsaw"])

    @mock.patch("apps.progress.leaderboard.get_player_rank", return_value=None)
    def test_progress_me(self, _rank, _lb):
        resp = self.client.get(reverse("progress-me"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["rank"], "Cadet")

    def test_constellation_list(self, _):
        c = Constellation.objects.create(slug="solar", name="Solar", topic="astronomy")
        SkillStar.objects.create(constellation=c, slug="s1", name="Inner Planets")
        resp = self.client.get(reverse("constellation-list"))
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body[0]["slug"], "solar")
        self.assertEqual(body[0]["earned_count"], 0)
        self.assertEqual(body[0]["total_count"], 1)


@mock.patch("apps.progress.leaderboard.get_weekly_top")
class LeaderboardEndpointTests(TestCase):
    def test_weekly_attaches_safe_names(self, mock_top):
        p1 = make_player(username="kid1")
        p1.display_name = "RocketKid"
        p1.display_name_status = "approved"
        p1.save()
        p2 = make_player(username="kid2")  # pending name -> fallback
        mock_top.return_value = [
            {"player_id": p1.id, "score": 200, "rank": 1},
            {"player_id": p2.id, "score": 100, "rank": 2},
        ]
        resp = self.client.get(reverse("leaderboard-weekly"))
        self.assertEqual(resp.status_code, 200)
        entries = resp.json()["entries"]
        self.assertEqual(entries[0]["display_name"], "RocketKid")
        self.assertEqual(entries[1]["display_name"], f"Explorer-{p2.id}")


class AnalyticsEndpointTests(TestCase):
    @mock.patch("apps.analytics.stream.push")
    def test_batch_ingest_validates_and_counts(self, mock_push):
        good = {
            "event_type": "mission.started",
            "session_id": str(uuid.uuid4()),
            "payload": {"mission_id": 1, "planet_id": 1, "game_type": "quiz",
                        "difficulty_level": 3},
        }
        bad = {"event_type": "nope", "session_id": "x", "payload": {}}
        resp = self.client.post(reverse("analytics-events"),
                                {"events": [good, bad]},
                                content_type="application/json")
        self.assertEqual(resp.status_code, 202)
        self.assertEqual(resp.json()["accepted"], 1)
        self.assertEqual(mock_push.call_count, 1)

    def test_rejects_non_list(self):
        resp = self.client.post(reverse("analytics-events"),
                                {"events": "x"},
                                content_type="application/json")
        self.assertEqual(resp.status_code, 400)
