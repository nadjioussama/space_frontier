"""Smoke tests exercising the walking-skeleton happy path without touching NASA.

These assume a Postgres + Redis already provisioned (docker compose up). Run:
    docker compose exec web python manage.py test tests
"""
from datetime import date

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from apps.games.services import generate_apod_mission
from apps.nasa_ingest.models import APODEntry


def _seed_apod() -> APODEntry:
    return APODEntry.objects.create(
        source_api="apod", source_id="2026-04-13",
        date=date(2026, 4, 13),
        title="Test Nebula",
        explanation="A beautiful cloud of gas and dust photographed by Hubble.",
        media_type="image",
        image_url="https://example.com/test.jpg",
        proxied_url="/media/apod/test.jpg",
        is_published=True,
    )


class WalkingSkeletonTests(TestCase):
    def setUp(self) -> None:
        cache.clear()
        self.entry = _seed_apod()
        self.mission = generate_apod_mission(self.entry)

    def test_today_endpoint_returns_payload(self):
        resp = self.client.get(reverse("nasa-today"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["apod"]["title"], "Test Nebula")
        self.assertEqual(resp.json()["mission_slug"], self.mission.slug)

    def test_mission_detail_has_jigsaw_and_quizzes(self):
        resp = self.client.get(reverse("mission-detail", args=[self.mission.slug]))
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIn("jigsaw", body)
        self.assertEqual(body["jigsaw"]["piece_count"], 12)
        self.assertEqual(len(body["quizzes"]), 3)

    def test_attempt_scores_and_returns_xp(self):
        detail = self.client.get(reverse("mission-detail", args=[self.mission.slug])).json()
        # Answer every quiz correctly using the stored correct_answer
        from apps.games.models import Quiz
        answers = [
            {"quiz_id": q.id, "answer": q.correct_answer}
            for q in Quiz.objects.filter(mission=self.mission)
        ]
        resp = self.client.post(
            reverse("mission-attempt", args=[self.mission.slug]),
            data={"quiz_answers": answers, "jigsaw_completed": True},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertGreater(body["xp_earned"], 0)
        self.assertTrue(all(r["correct"] for r in body["results"]))
        self.assertIsNotNone(detail)
