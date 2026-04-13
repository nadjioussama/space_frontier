"""Tests for analytics.rollups — metric read helpers."""
from datetime import date, timedelta
from unittest.mock import MagicMock, patch, PropertyMock

import pytest


@pytest.fixture
def mock_redis():
    with patch("apps.analytics.rollups._redis") as r:
        yield r


class TestCurrentDau:
    @patch("apps.analytics.rollups.DailyEngagementRollup.objects")
    def test_sums_all_age_groups(self, mock_qs):
        from apps.analytics.rollups import current_dau

        mock_qs.filter.return_value.values_list.return_value = [50, 30, 20]
        assert current_dau() == 100


class TestDauOn:
    @patch("apps.analytics.rollups.DailyEngagementRollup.objects")
    def test_returns_dau_for_date(self, mock_qs):
        from apps.analytics.rollups import dau_on

        mock_qs.filter.return_value.values_list.return_value = [42]
        assert dau_on(date(2026, 4, 13)) == 42

    @patch("apps.analytics.rollups.DailyEngagementRollup.objects")
    def test_returns_zero_for_no_data(self, mock_qs):
        from apps.analytics.rollups import dau_on

        mock_qs.filter.return_value.values_list.return_value = []
        assert dau_on(date(2026, 1, 1)) == 0


class TestAvgSessionSeconds:
    @patch("apps.analytics.rollups.DailyEngagementRollup.objects")
    def test_averages_across_rows(self, mock_qs):
        from apps.analytics.rollups import avg_session_seconds

        row1 = MagicMock(avg_session_seconds=100.0, sessions=5)
        row2 = MagicMock(avg_session_seconds=200.0, sessions=3)
        mock_qs.filter.return_value = [row1, row2]
        assert avg_session_seconds(date(2026, 4, 13)) == 150.0

    @patch("apps.analytics.rollups.DailyEngagementRollup.objects")
    def test_returns_zero_for_no_sessions(self, mock_qs):
        from apps.analytics.rollups import avg_session_seconds

        row = MagicMock(sessions=0)
        mock_qs.filter.return_value = [row]
        assert avg_session_seconds(date(2026, 4, 13)) == 0.0


class TestMissionCompletionRate:
    @patch("apps.analytics.rollups.MissionRollup.objects")
    def test_computes_rate(self, mock_qs):
        from apps.analytics.rollups import mission_completion_rate

        row = MagicMock(starts=100, completions=75)
        mock_qs.filter.return_value = [row]
        assert mission_completion_rate(1, date(2026, 4, 13)) == 0.75

    @patch("apps.analytics.rollups.MissionRollup.objects")
    def test_returns_none_for_zero_starts(self, mock_qs):
        from apps.analytics.rollups import mission_completion_rate

        row = MagicMock(starts=0, completions=0)
        mock_qs.filter.return_value = [row]
        assert mission_completion_rate(1, date(2026, 4, 13)) is None


class TestBrokenQuizzes:
    @patch("apps.analytics.rollups.QuizQuestionRollup.objects")
    def test_identifies_low_accuracy_quizzes(self, mock_qs):
        from apps.analytics.rollups import broken_quizzes

        good = MagicMock(quiz_id=1, attempts=100, correct_count=50)
        bad = MagicMock(quiz_id=2, attempts=100, correct_count=5)
        mock_qs.filter.return_value = [good, bad]
        result = broken_quizzes(date(2026, 4, 13), accuracy_max=0.10, min_attempts=50)
        assert result == [2]


class TestRedisHitRate:
    def test_computes_hit_rate(self, mock_redis):
        from apps.analytics.rollups import redis_hit_rate

        mock_redis.info.return_value = {"keyspace_hits": 90, "keyspace_misses": 10}
        assert redis_hit_rate() == 0.9

    def test_returns_one_when_no_traffic(self, mock_redis):
        from apps.analytics.rollups import redis_hit_rate

        mock_redis.info.return_value = {"keyspace_hits": 0, "keyspace_misses": 0}
        assert redis_hit_rate() == 1.0


class TestNasaQuotaUsed:
    @patch("apps.analytics.rollups.cache")
    def test_reads_from_cache(self, mock_cache):
        from apps.analytics.rollups import nasa_quota_used

        mock_cache.get.return_value = 42
        assert nasa_quota_used() == 42

    @patch("apps.analytics.rollups.cache")
    def test_returns_zero_when_missing(self, mock_cache):
        from apps.analytics.rollups import nasa_quota_used

        mock_cache.get.return_value = None
        assert nasa_quota_used() == 0


class TestRollingAvg:
    def test_averages_over_days(self):
        from apps.analytics.rollups import rolling_avg

        values = {1: 10.0, 2: 20.0, 3: 30.0}
        fn = lambda d: values.get((date.today() - d).days, 0.0)
        # rolling_avg calls fn(today - timedelta(days=i)) for i in 1..days
        # We need a simpler mock
        call_count = [0]

        def metric_fn(d):
            call_count[0] += 1
            return 10.0 * call_count[0]

        result = rolling_avg(metric_fn, days=3)
        assert result == 20.0  # (10 + 20 + 30) / 3
