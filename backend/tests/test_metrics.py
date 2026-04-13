"""Tests for config.metrics — Prometheus business metrics endpoint."""
from unittest.mock import patch, MagicMock

import pytest
from django.test import RequestFactory


class TestMetricsView:
    @patch("config.metrics.circuit_state", return_value="closed")
    @patch("config.metrics.nasa_quota_used", return_value=42)
    @patch("config.metrics.redis_hit_rate", return_value=0.95)
    @patch("config.metrics.current_dau", return_value=150)
    def test_returns_prometheus_metrics(self, mock_dau, mock_hit, mock_quota, mock_circuit):
        from config.metrics import metrics_view

        rf = RequestFactory()
        response = metrics_view(rf.get("/metrics"))
        assert response.status_code == 200
        content = response.content.decode()
        assert "nse_dau" in content
        assert "nse_redis_hit_rate" in content
        assert "nse_nasa_quota_used" in content
        assert "nse_nasa_circuit_open" in content

    @patch("config.metrics.circuit_state", return_value="open")
    @patch("config.metrics.nasa_quota_used", return_value=0)
    @patch("config.metrics.redis_hit_rate", return_value=1.0)
    @patch("config.metrics.current_dau", return_value=0)
    def test_circuit_open_value(self, mock_dau, mock_hit, mock_quota, mock_circuit):
        from config.metrics import metrics_view

        rf = RequestFactory()
        response = metrics_view(rf.get("/metrics"))
        content = response.content.decode()
        # When circuit is open, gauge should be 1
        assert "nse_nasa_circuit_open 1.0" in content
