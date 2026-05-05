"""Tests for Celery ingestion tasks (nasa_ingest + progress)."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from django.core.cache import cache
from django.test import TestCase

from apps.nasa_ingest.circuit import CircuitOpenError
from apps.nasa_ingest.clients.base import QuotaExhaustedError


class IngestAPODTaskTests(TestCase):
    """Tests for apps.nasa_ingest.tasks.ingest_apod."""

    def setUp(self) -> None:
        cache.clear()

    @patch("apps.nasa_ingest.tasks._acquire_lock", return_value=None)
    def test_skips_when_lock_not_acquired(self, mock_lock):
        from apps.nasa_ingest.tasks import ingest_apod
        result = ingest_apod()
        self.assertEqual(result, {"skipped": True})

    @patch("apps.nasa_ingest.tasks._acquire_lock")
    def test_handles_circuit_open_error(self, mock_lock):
        mock_lock.return_value = MagicMock()
        with patch("apps.nasa_ingest.tasks.ingest_apod.__wrapped__", side_effect=None):
            # Patch the client inside the task
            with patch("apps.nasa_ingest.clients.apod.APODClient") as MockClient:
                MockClient.return_value.fetch_today.side_effect = CircuitOpenError("open")
                from apps.nasa_ingest.tasks import ingest_apod
                result = ingest_apod()
                self.assertTrue(result.get("skipped"))
                self.assertIn("reason", result)

    @patch("apps.nasa_ingest.tasks._acquire_lock")
    def test_handles_quota_exhausted_error(self, mock_lock):
        mock_lock.return_value = MagicMock()
        with patch("apps.nasa_ingest.clients.apod.APODClient") as MockClient:
            MockClient.return_value.fetch_today.side_effect = QuotaExhaustedError("quota")
            from apps.nasa_ingest.tasks import ingest_apod
            result = ingest_apod()
            self.assertTrue(result.get("skipped"))
            self.assertIn("reason", result)

    @patch("apps.nasa_ingest.tasks._acquire_lock")
    @patch("apps.nasa_ingest.tasks._safe_release")
    def test_success_path_creates_mission_and_warms_cache(self, mock_release, mock_lock):
        mock_lock.return_value = MagicMock()

        fake_raw = {
            "date": "2026-04-13",
            "title": "Fake Nebula",
            "explanation": "A test explanation.",
            "media_type": "image",
            "url": "https://example.com/apod.jpg",
        }

        with patch("apps.nasa_ingest.clients.apod.APODClient") as MockClient, \
             patch("apps.nasa_ingest.transformers.apod.APODTransformer") as MockTransformer, \
             patch("apps.games.services.generate_apod_mission") as mock_gen:

            from tests.factories import make_apod
            entry = make_apod()
            MockClient.return_value.fetch_today.return_value = fake_raw
            MockTransformer.return_value.to_model.return_value = entry
            mock_gen.return_value = MagicMock(slug="apod-2026-04-13")

            from apps.nasa_ingest.tasks import ingest_apod
            result = ingest_apod()

            self.assertTrue(result.get("ok"))
            self.assertEqual(result["date"], "2026-04-13")
            mock_gen.assert_called_once_with(entry)
            # Cache should be warmed
            cached = cache.get("nasa:today")
            self.assertIsNotNone(cached)
            mock_release.assert_called_once()


class IngestMarsTaskTests(TestCase):
    """Tests for apps.nasa_ingest.tasks.ingest_mars."""

    def setUp(self) -> None:
        cache.clear()

    @patch("apps.nasa_ingest.tasks._acquire_lock", return_value=None)
    def test_skips_when_locked(self, mock_lock):
        from apps.nasa_ingest.tasks import ingest_mars
        result = ingest_mars()
        self.assertEqual(result, {"skipped": True})

    @patch("apps.nasa_ingest.tasks._acquire_lock")
    @patch("apps.nasa_ingest.tasks._safe_release")
    def test_success_path(self, mock_release, mock_lock):
        mock_lock.return_value = MagicMock()

        with patch("apps.nasa_ingest.clients.mars.MarsRoverClient") as MockClient, \
             patch("apps.nasa_ingest.transformers.mars.MarsPhotoTransformer") as MockTransformer, \
             patch("apps.games.services.generate_mars_missions") as mock_gen:

            MockClient.return_value.fetch_latest.return_value = [{"id": 1}]
            from tests.factories import make_mars_photo
            photos = [make_mars_photo(nasa_id=99)]
            MockTransformer.return_value.to_models.return_value = photos
            mock_gen.return_value = []

            from apps.nasa_ingest.tasks import ingest_mars
            result = ingest_mars()

            self.assertTrue(result.get("ok"))
            self.assertEqual(result["count"], 1)
            mock_gen.assert_called_once_with(photos)
            mock_release.assert_called_once()

    @patch("apps.nasa_ingest.tasks._acquire_lock")
    def test_skip_on_circuit_open(self, mock_lock):
        mock_lock.return_value = MagicMock()
        with patch("apps.nasa_ingest.clients.mars.MarsRoverClient") as MockClient:
            MockClient.return_value.fetch_latest.side_effect = CircuitOpenError("open")
            from apps.nasa_ingest.tasks import ingest_mars
            result = ingest_mars()
            self.assertTrue(result.get("skipped"))


class IngestNeoWsTaskTests(TestCase):
    """Tests for apps.nasa_ingest.tasks.ingest_neows."""

    def setUp(self) -> None:
        cache.clear()

    @patch("apps.nasa_ingest.tasks._acquire_lock", return_value=None)
    def test_skips_when_locked(self, mock_lock):
        from apps.nasa_ingest.tasks import ingest_neows
        result = ingest_neows()
        self.assertEqual(result, {"skipped": True})

    @patch("apps.nasa_ingest.tasks._acquire_lock")
    @patch("apps.nasa_ingest.tasks._safe_release")
    def test_success_sets_neo_count_cache(self, mock_release, mock_lock):
        mock_lock.return_value = MagicMock()

        with patch("apps.nasa_ingest.clients.neows.NeoWsClient") as MockClient, \
             patch("apps.nasa_ingest.transformers.neows.NeoWsTransformer") as MockTransformer, \
             patch("apps.games.services.generate_neo_missions") as mock_gen:

            MockClient.return_value.fetch_today.return_value = {"element_count": 3}
            from tests.factories import make_neo
            neos = [make_neo(neo_id="100"), make_neo(neo_id="101")]
            MockTransformer.return_value.to_models.return_value = neos
            mock_gen.return_value = []

            from apps.nasa_ingest.tasks import ingest_neows
            result = ingest_neows()

            self.assertTrue(result.get("ok"))
            self.assertEqual(result["count"], 2)
            # Cache key set to count of neos
            self.assertEqual(cache.get("neo:approaching_count"), 2)
            mock_release.assert_called_once()


class IngestEPICTaskTests(TestCase):
    """Tests for apps.nasa_ingest.tasks.ingest_epic."""

    def setUp(self) -> None:
        cache.clear()

    @patch("apps.nasa_ingest.tasks._acquire_lock", return_value=None)
    def test_skips_when_locked(self, mock_lock):
        from apps.nasa_ingest.tasks import ingest_epic
        result = ingest_epic()
        self.assertEqual(result, {"skipped": True})

    @patch("apps.nasa_ingest.tasks._acquire_lock")
    @patch("apps.nasa_ingest.tasks._safe_release")
    def test_success_path(self, mock_release, mock_lock):
        mock_lock.return_value = MagicMock()

        with patch("apps.nasa_ingest.clients.epic.EPICClient") as MockClient, \
             patch("apps.nasa_ingest.transformers.epic.EPICTransformer") as MockTransformer, \
             patch("apps.games.services.generate_epic_missions") as mock_gen:

            MockClient.return_value.fetch_recent.return_value = [{"id": "e1"}]
            from tests.factories import make_epic
            images = [make_epic(identifier="epic_task_1")]
            MockTransformer.return_value.to_models.return_value = images
            mock_gen.return_value = []

            from apps.nasa_ingest.tasks import ingest_epic
            result = ingest_epic()

            self.assertTrue(result.get("ok"))
            self.assertEqual(result["count"], 1)
            mock_gen.assert_called_once_with(images)
            mock_release.assert_called_once()


class IngestExoplanetsTaskTests(TestCase):
    """Tests for apps.nasa_ingest.tasks.ingest_exoplanets."""

    def setUp(self) -> None:
        cache.clear()

    @patch("apps.nasa_ingest.tasks._acquire_lock", return_value=None)
    def test_skips_when_locked(self, mock_lock):
        from apps.nasa_ingest.tasks import ingest_exoplanets
        result = ingest_exoplanets()
        self.assertEqual(result, {"skipped": True})

    @patch("apps.nasa_ingest.tasks._acquire_lock")
    @patch("apps.nasa_ingest.tasks._safe_release")
    def test_success_path(self, mock_release, mock_lock):
        mock_lock.return_value = MagicMock()

        with patch("apps.nasa_ingest.clients.exoplanet.ExoplanetClient") as MockClient, \
             patch("apps.nasa_ingest.transformers.exoplanet.ExoplanetTransformer") as MockTransformer, \
             patch("apps.games.services.generate_exoplanet_missions") as mock_gen:

            MockClient.return_value.fetch_confirmed.return_value = [{"name": "Test"}]
            from tests.factories import make_exoplanet
            exos = [make_exoplanet(name="Task-Exo-1")]
            MockTransformer.return_value.to_models.return_value = exos
            mock_gen.return_value = []

            from apps.nasa_ingest.tasks import ingest_exoplanets
            result = ingest_exoplanets()

            self.assertTrue(result.get("ok"))
            self.assertEqual(result["count"], 1)
            mock_gen.assert_called_once_with(exos)
            mock_release.assert_called_once()


class ResetWeeklyLeaderboardTaskTests(TestCase):
    """Tests for apps.progress.tasks.reset_weekly_leaderboard."""

    @patch("apps.progress.leaderboard.reset_weekly", return_value=10)
    def test_calls_reset_and_returns_count(self, mock_reset):
        from apps.progress.tasks import reset_weekly_leaderboard
        result = reset_weekly_leaderboard()
        self.assertTrue(result["reset"])
        self.assertEqual(result["entries_archived"], 10)
        mock_reset.assert_called_once()


class GenerateCrossAPIMissionsTaskTests(TestCase):
    """Tests for apps.progress.tasks.generate_cross_api_missions."""

    @patch("apps.games.services.generate_cross_api_missions")
    def test_calls_service_and_returns_count(self, mock_gen):
        mock_gen.return_value = [MagicMock(), MagicMock()]
        from apps.progress.tasks import generate_cross_api_missions
        result = generate_cross_api_missions()
        self.assertTrue(result["ok"])
        self.assertEqual(result["count"], 2)
        mock_gen.assert_called_once()
