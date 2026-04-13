"""Tests for individual NASA API client classes."""
from datetime import date
from unittest.mock import patch, MagicMock

import pytest

from apps.nasa_ingest.clients.base import NASAClient, QuotaExhaustedError


class TestAPODClient:
    @patch("apps.nasa_ingest.clients.apod.NASAClient.get")
    def test_fetch_today(self, mock_get):
        from apps.nasa_ingest.clients.apod import APODClient

        mock_get.return_value = {"title": "Nebula", "date": "2026-04-13"}
        client = APODClient()
        result = client.fetch_today()
        assert result["title"] == "Nebula"
        mock_get.assert_called_once()

    @patch("apps.nasa_ingest.clients.apod.NASAClient.get")
    def test_fetch_date(self, mock_get):
        from apps.nasa_ingest.clients.apod import APODClient

        client = APODClient()
        client.fetch_date("2026-01-01")
        call_args = mock_get.call_args
        assert call_args[0][1] == {"date": "2026-01-01"}


class TestMarsRoverClient:
    @patch("apps.nasa_ingest.clients.mars.NASAClient.get")
    def test_fetch_latest(self, mock_get):
        from apps.nasa_ingest.clients.mars import MarsRoverClient

        mock_get.return_value = {"latest_photos": [{"id": 1}]}
        client = MarsRoverClient()
        result = client.fetch_latest()
        assert len(result) == 1

    @patch("apps.nasa_ingest.clients.mars.NASAClient.get")
    def test_fetch_latest_with_camera(self, mock_get):
        from apps.nasa_ingest.clients.mars import MarsRoverClient

        mock_get.return_value = {"latest_photos": []}
        client = MarsRoverClient()
        client.fetch_latest(camera="navcam")
        call_args = mock_get.call_args
        assert "navcam" in str(call_args)

    @patch("apps.nasa_ingest.clients.mars.NASAClient.get")
    def test_fetch_sol(self, mock_get):
        from apps.nasa_ingest.clients.mars import MarsRoverClient

        mock_get.return_value = {"photos": [{"id": 99}]}
        client = MarsRoverClient()
        result = client.fetch_sol("perseverance", 1000)
        assert len(result) == 1


class TestNeoWsClient:
    @patch("apps.nasa_ingest.clients.neows.NASAClient.get")
    def test_fetch_today(self, mock_get):
        from apps.nasa_ingest.clients.neows import NeoWsClient

        mock_get.return_value = {"element_count": 5}
        client = NeoWsClient()
        result = client.fetch_today()
        assert result["element_count"] == 5

    @patch("apps.nasa_ingest.clients.neows.NASAClient.get")
    def test_fetch_week(self, mock_get):
        from apps.nasa_ingest.clients.neows import NeoWsClient

        mock_get.return_value = {"element_count": 20}
        client = NeoWsClient()
        result = client.fetch_week(start=date(2026, 4, 13))
        call_args = mock_get.call_args
        params = call_args[0][1]
        assert params["start_date"] == "2026-04-13"
        assert params["end_date"] == "2026-04-20"


class TestEPICClient:
    @patch("apps.nasa_ingest.clients.epic.NASAClient.get")
    def test_fetch_recent(self, mock_get):
        from apps.nasa_ingest.clients.epic import EPICClient

        mock_get.return_value = [{"image": "epic_1"}]
        client = EPICClient()
        result = client.fetch_recent()
        assert len(result) == 1

    def test_image_url_format(self):
        from apps.nasa_ingest.clients.epic import EPICClient

        client = EPICClient()
        url = client.image_url("epic_test", "2026-04-13")
        assert url == "https://epic.gsfc.nasa.gov/archive/natural/2026/04/13/png/epic_test.png"

    def test_image_url_enhanced_collection(self):
        from apps.nasa_ingest.clients.epic import EPICClient

        client = EPICClient()
        url = client.image_url("img", "2026-01-01", collection="enhanced")
        assert "/enhanced/" in url


class TestExoplanetClient:
    @patch("apps.nasa_ingest.clients.exoplanet.requests.get")
    def test_fetch_confirmed(self, mock_get):
        from apps.nasa_ingest.clients.exoplanet import ExoplanetClient

        mock_resp = MagicMock()
        mock_resp.json.return_value = [{"pl_name": "Kepler-442 b"}]
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        client = ExoplanetClient()
        result = client.fetch_confirmed(limit=10)
        assert result[0]["pl_name"] == "Kepler-442 b"

    @patch("apps.nasa_ingest.clients.exoplanet.requests.get")
    def test_fetch_confirmed_sends_tap_query(self, mock_get):
        from apps.nasa_ingest.clients.exoplanet import ExoplanetClient

        mock_resp = MagicMock()
        mock_resp.json.return_value = []
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        client = ExoplanetClient()
        client.fetch_confirmed(limit=50)
        call_kwargs = mock_get.call_args
        params = call_kwargs.kwargs.get("params") or call_kwargs[1].get("params", {})
        assert "LIMIT 50" in params.get("query", "")
        assert params.get("format") == "json"


class TestQuotaExhaustedError:
    def test_is_runtime_error(self):
        err = QuotaExhaustedError("test")
        assert isinstance(err, RuntimeError)
