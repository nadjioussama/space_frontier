"""NASA HTTP client: quota tracking + key injection. PLAN §6.3, §9.7."""
from __future__ import annotations

from unittest import mock

from django.conf import settings
from django.core.cache import cache
from django.test import SimpleTestCase

from apps.nasa_ingest.clients.base import NASAClient, QuotaExhaustedError


class QuotaTests(SimpleTestCase):
    def setUp(self) -> None:
        self.client = NASAClient()
        cache.delete(self.client._quota_key())

    def tearDown(self) -> None:
        cache.delete(self.client._quota_key())

    def test_hard_stop_raises_before_calling_nasa(self):
        cache.set(self.client._quota_key(), settings.NASA_QUOTA_HARD_STOP_AT, timeout=3600)
        with self.assertRaises(QuotaExhaustedError):
            self.client._check_quota()

    def test_warn_threshold_does_not_raise(self):
        cache.set(self.client._quota_key(), settings.NASA_QUOTA_WARN_AT, timeout=3600)
        # Should log a warning but return the count
        self.assertEqual(self.client._check_quota(), settings.NASA_QUOTA_WARN_AT)

    def test_increment_from_empty(self):
        self.assertEqual(self.client._increment_quota(), 1)
        self.assertEqual(self.client._increment_quota(), 2)
        self.assertEqual(cache.get(self.client._quota_key()), 2)


class RequestTests(SimpleTestCase):
    def setUp(self) -> None:
        self.client = NASAClient()
        cache.delete(self.client._quota_key())
        # Make sure the breaker is closed so .get() reaches _do_get
        from apps.nasa_ingest import circuit
        cache.delete_many([circuit._STATE_KEY, circuit._FAIL_KEY, circuit._OPENED_AT_KEY])

    @mock.patch("apps.nasa_ingest.clients.base.requests.get")
    def test_api_key_injected_and_quota_incremented(self, mock_get):
        mock_get.return_value = mock.Mock(
            status_code=200, json=lambda: {"ok": True}, raise_for_status=lambda: None,
        )
        out = self.client.get("https://api.nasa.gov/planetary/apod", {"date": "2026-04-13"})
        self.assertEqual(out, {"ok": True})
        _, kwargs = mock_get.call_args
        self.assertEqual(kwargs["params"]["api_key"], settings.NASA_API_KEY)
        self.assertEqual(kwargs["params"]["date"], "2026-04-13")
        self.assertEqual(cache.get(self.client._quota_key()), 1)

    @mock.patch("apps.nasa_ingest.clients.base.requests.get")
    def test_quota_exhausted_prevents_network_call(self, mock_get):
        cache.set(self.client._quota_key(), settings.NASA_QUOTA_HARD_STOP_AT, timeout=3600)
        with self.assertRaises(QuotaExhaustedError):
            self.client._do_get("https://api.nasa.gov/x")
        mock_get.assert_not_called()
