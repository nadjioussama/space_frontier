"""Tests for management commands."""
from __future__ import annotations

from io import StringIO
from unittest.mock import patch, MagicMock

from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase

from apps.progress.models import Constellation, SkillStar


class IngestAPODCommandTests(TestCase):
    def setUp(self) -> None:
        cache.clear()

    @patch("apps.nasa_ingest.tasks.ingest_apod")
    def test_calls_ingest_apod_task(self, mock_task):
        mock_task.return_value = {"ok": True, "date": "2026-04-13"}
        out = StringIO()
        call_command("ingest_apod", stdout=out)
        mock_task.assert_called_once()
        self.assertIn("ingest_apod", out.getvalue())


class IngestMarsCommandTests(TestCase):
    def setUp(self) -> None:
        cache.clear()

    @patch("apps.nasa_ingest.tasks.ingest_mars")
    def test_calls_ingest_mars_task(self, mock_task):
        mock_task.return_value = {"ok": True, "count": 5}
        out = StringIO()
        call_command("ingest_mars", stdout=out)
        mock_task.assert_called_once()
        self.assertIn("ingest_mars", out.getvalue())


class IngestNeoWsCommandTests(TestCase):
    def setUp(self) -> None:
        cache.clear()

    @patch("apps.nasa_ingest.tasks.ingest_neows")
    def test_calls_ingest_neows_task(self, mock_task):
        mock_task.return_value = {"ok": True, "count": 3}
        out = StringIO()
        call_command("ingest_neows", stdout=out)
        mock_task.assert_called_once()
        self.assertIn("ingest_neows", out.getvalue())


class IngestEPICCommandTests(TestCase):
    def setUp(self) -> None:
        cache.clear()

    @patch("apps.nasa_ingest.tasks.ingest_epic")
    def test_calls_ingest_epic_task(self, mock_task):
        mock_task.return_value = {"ok": True, "count": 2}
        out = StringIO()
        call_command("ingest_epic", stdout=out)
        mock_task.assert_called_once()
        self.assertIn("ingest_epic", out.getvalue())


class IngestExoplanetsCommandTests(TestCase):
    def setUp(self) -> None:
        cache.clear()

    @patch("apps.nasa_ingest.tasks.ingest_exoplanets")
    def test_calls_ingest_exoplanets_task(self, mock_task):
        mock_task.return_value = {"ok": True, "count": 10}
        out = StringIO()
        call_command("ingest_exoplanets", stdout=out)
        mock_task.assert_called_once()
        self.assertIn("ingest_exoplanets", out.getvalue())


class SeedConstellationsCommandTests(TestCase):
    def setUp(self) -> None:
        cache.clear()

    def test_creates_constellations_and_stars(self):
        out = StringIO()
        call_command("seed_constellations", stdout=out)

        # Should have created all 5 constellations
        self.assertEqual(Constellation.objects.count(), 5)
        # Should have created stars across constellations
        self.assertGreater(SkillStar.objects.count(), 0)

    def test_idempotent_run(self):
        """Running twice should not duplicate data."""
        call_command("seed_constellations", stdout=StringIO())
        first_count = SkillStar.objects.count()
        call_command("seed_constellations", stdout=StringIO())
        second_count = SkillStar.objects.count()
        self.assertEqual(first_count, second_count)

    def test_prerequisites_wired(self):
        call_command("seed_constellations", stdout=StringIO())
        # "outer-planets" should have "inner-planets" as prerequisite
        outer = SkillStar.objects.get(slug="outer-planets")
        prereq_slugs = list(outer.prerequisites.values_list("slug", flat=True))
        self.assertIn("inner-planets", prereq_slugs)


class GenerateCrossAPICommandTests(TestCase):
    def setUp(self) -> None:
        cache.clear()

    @patch("apps.games.services.generate_cross_api_missions")
    def test_calls_generate_cross_api_missions(self, mock_gen):
        m1 = MagicMock(slug="cross-1", title="Mission 1")
        m2 = MagicMock(slug="cross-2", title="Mission 2")
        mock_gen.return_value = [m1, m2]
        out = StringIO()
        call_command("generate_cross_api", stdout=out)
        mock_gen.assert_called_once()
        self.assertIn("2 cross-API missions", out.getvalue())
