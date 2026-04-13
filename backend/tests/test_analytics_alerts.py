"""Tests for analytics.alerts — anomaly detection rules."""
from datetime import date
from unittest.mock import MagicMock, patch

import pytest


class TestDauDrop:
    @patch("apps.analytics.alerts.rollups")
    def test_fires_when_dau_drops_20_percent(self, mock_rollups):
        from apps.analytics.alerts import _dau_drop

        mock_rollups.dau_on.side_effect = lambda d: 35 if d == date.today() else 50
        result = _dau_drop()
        assert result is not None
        assert "35" in result

    @patch("apps.analytics.alerts.rollups")
    def test_no_fire_when_dau_is_stable(self, mock_rollups):
        from apps.analytics.alerts import _dau_drop

        mock_rollups.dau_on.return_value = 100
        assert _dau_drop() is None

    @patch("apps.analytics.alerts.rollups")
    def test_no_fire_when_previous_dau_below_threshold(self, mock_rollups):
        from apps.analytics.alerts import _dau_drop

        mock_rollups.dau_on.return_value = 10
        assert _dau_drop() is None


class TestMissionCompletionCrash:
    @patch("apps.analytics.alerts.MissionRollup.objects")
    @patch("apps.analytics.alerts.rollups")
    def test_fires_on_completion_rate_crash(self, mock_rollups, mock_qs):
        from apps.analytics.alerts import _mission_completion_crash

        mock_qs.filter.return_value.values_list.return_value.distinct.return_value = [1]
        mock_rollups.mission_completion_rate.side_effect = lambda mid, d: (
            0.20 if d == date.today() else 0.80
        )
        result = _mission_completion_crash()
        assert result is not None
        assert "mission 1" in result

    @patch("apps.analytics.alerts.MissionRollup.objects")
    @patch("apps.analytics.alerts.rollups")
    def test_no_fire_when_stable(self, mock_rollups, mock_qs):
        from apps.analytics.alerts import _mission_completion_crash

        mock_qs.filter.return_value.values_list.return_value.distinct.return_value = [1]
        mock_rollups.mission_completion_rate.return_value = 0.80
        assert _mission_completion_crash() is None


class TestQuizBroken:
    @patch("apps.analytics.alerts.rollups")
    def test_fires_with_broken_quiz_ids(self, mock_rollups):
        from apps.analytics.alerts import _quiz_broken

        mock_rollups.broken_quizzes.return_value = [5, 12]
        result = _quiz_broken()
        assert result is not None
        assert "5" in result and "12" in result

    @patch("apps.analytics.alerts.rollups")
    def test_no_fire_when_all_ok(self, mock_rollups):
        from apps.analytics.alerts import _quiz_broken

        mock_rollups.broken_quizzes.return_value = []
        assert _quiz_broken() is None


class TestOnboardingDropout:
    @patch("apps.analytics.alerts.rollups")
    def test_fires_on_low_completion_steps(self, mock_rollups):
        from apps.analytics.alerts import _onboarding_dropout

        mock_rollups.onboarding_funnel.return_value = {1: 1.0, 2: 0.80, 3: 0.50}
        result = _onboarding_dropout()
        assert result is not None
        assert "3" in result

    @patch("apps.analytics.alerts.rollups")
    def test_no_fire_when_funnel_healthy(self, mock_rollups):
        from apps.analytics.alerts import _onboarding_dropout

        mock_rollups.onboarding_funnel.return_value = {1: 1.0, 2: 0.90}
        assert _onboarding_dropout() is None


class TestSessionLengthAnomaly:
    @patch("apps.analytics.alerts.rollups")
    def test_fires_on_large_deviation(self, mock_rollups):
        from apps.analytics.alerts import _session_length_anomaly

        mock_rollups.avg_session_seconds.return_value = 500.0
        mock_rollups.rolling_avg.return_value = 300.0
        result = _session_length_anomaly()
        assert result is not None
        assert "500" in result

    @patch("apps.analytics.alerts.rollups")
    def test_no_fire_within_threshold(self, mock_rollups):
        from apps.analytics.alerts import _session_length_anomaly

        mock_rollups.avg_session_seconds.return_value = 310.0
        mock_rollups.rolling_avg.return_value = 300.0
        assert _session_length_anomaly() is None

    @patch("apps.analytics.alerts.rollups")
    def test_no_fire_when_no_baseline(self, mock_rollups):
        from apps.analytics.alerts import _session_length_anomaly

        mock_rollups.avg_session_seconds.return_value = 100.0
        mock_rollups.rolling_avg.return_value = 0
        assert _session_length_anomaly() is None


class TestPostSlack:
    @patch("apps.analytics.alerts.requests.post")
    def test_posts_to_webhook(self, mock_post):
        from apps.analytics.alerts import _post_slack

        with patch("apps.analytics.alerts.settings") as s:
            s.SLACK_WEBHOOK_URL = "https://hooks.slack.com/test"
            _post_slack("#general", "test message")
        mock_post.assert_called_once()

    @patch("apps.analytics.alerts.requests.post")
    def test_skips_when_no_url(self, mock_post):
        from apps.analytics.alerts import _post_slack

        with patch("apps.analytics.alerts.settings") as s:
            s.SLACK_WEBHOOK_URL = ""
            _post_slack("#general", "test")
        mock_post.assert_not_called()


class TestRunAlertRules:
    @patch("apps.analytics.alerts.cache")
    @patch("apps.analytics.alerts._post_slack")
    @patch("apps.analytics.alerts.ALERT_RULES")
    def test_deduplicates_alerts(self, mock_rules, mock_slack, mock_cache):
        from apps.analytics.alerts import run_alert_rules, Rule

        mock_rules.__iter__ = lambda _: iter([
            Rule("test_rule", "high", "#ch", lambda: "problem found"),
        ])
        mock_cache.get.return_value = 1  # already fired
        result = run_alert_rules()
        assert result == []
        mock_slack.assert_not_called()

    @patch("apps.analytics.alerts.cache")
    @patch("apps.analytics.alerts._post_slack")
    @patch("apps.analytics.alerts.ALERT_RULES")
    def test_fires_and_caches(self, mock_rules, mock_slack, mock_cache):
        from apps.analytics.alerts import run_alert_rules, Rule

        mock_rules.__iter__ = lambda _: iter([
            Rule("new_rule", "high", "#ch", lambda: "alert!"),
        ])
        mock_cache.get.return_value = None
        result = run_alert_rules()
        assert "new_rule" in result
        mock_slack.assert_called_once()
        mock_cache.set.assert_called_once()

    @patch("apps.analytics.alerts.cache")
    @patch("apps.analytics.alerts._post_slack")
    @patch("apps.analytics.alerts.ALERT_RULES")
    def test_handles_check_exceptions(self, mock_rules, mock_slack, mock_cache):
        from apps.analytics.alerts import run_alert_rules, Rule

        mock_rules.__iter__ = lambda _: iter([
            Rule("broken", "high", "#ch", lambda: (_ for _ in ()).throw(RuntimeError("boom"))),
        ])
        result = run_alert_rules()
        assert result == []
