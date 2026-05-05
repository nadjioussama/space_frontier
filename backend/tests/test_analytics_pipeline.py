"""Tests for analytics.tasks — Celery tasks for the analytics pipeline."""
from datetime import date, datetime, timedelta, timezone
from unittest.mock import MagicMock, patch



class TestPartitionName:
    def test_format(self):
        from apps.analytics.tasks import _partition_name

        assert _partition_name(date(2026, 4, 13)) == "analytics_rawevent_20260413"

    def test_different_dates(self):
        from apps.analytics.tasks import _partition_name

        assert _partition_name(date(2026, 1, 1)) == "analytics_rawevent_20260101"
        assert _partition_name(date(2026, 12, 31)) == "analytics_rawevent_20261231"


class TestEnsurePartition:
    def test_creates_partition_sql(self):
        from apps.analytics.tasks import _ensure_partition

        cur = MagicMock()
        _ensure_partition(cur, date(2026, 4, 13))
        sql = cur.execute.call_args[0][0]
        assert "analytics_rawevent_20260413" in sql
        assert "2026-04-13" in sql
        assert "2026-04-14" in sql
        assert "CREATE TABLE IF NOT EXISTS" in sql


class TestDrainEventStream:
    @patch("apps.analytics.tasks.stream")
    @patch("apps.analytics.tasks.connection")
    def test_processes_batch(self, mock_conn, mock_stream):
        from apps.analytics.tasks import drain_event_stream

        record = {
            "event_type": "session.started",
            "player_id": "abc-123",
            "session_id": "sess-1",
            "age_group": "9-11",
            "timestamp": "2026-04-13T10:00:00+00:00",
            "payload": {"device_type": "tablet"},
        }
        mock_stream.read_batch.side_effect = [
            [(b"1-0", record)],
            [],  # second call returns empty → stop
        ]
        cur = MagicMock()
        mock_conn.cursor.return_value.__enter__ = lambda s: cur
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

        result = drain_event_stream(max_batches=5)
        assert result["written"] == 1
        mock_stream.ack.assert_called_once_with([b"1-0"])

    @patch("apps.analytics.tasks.stream")
    @patch("apps.analytics.tasks.connection")
    def test_empty_stream_returns_zero(self, mock_conn, mock_stream):
        from apps.analytics.tasks import drain_event_stream

        mock_stream.read_batch.return_value = []
        cur = MagicMock()
        mock_conn.cursor.return_value.__enter__ = lambda s: cur
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

        result = drain_event_stream()
        assert result["written"] == 0


class TestRefreshRollups:
    @patch("apps.analytics.tasks.connection")
    def test_refreshes_all_materialized_views(self, mock_conn):
        from apps.analytics.tasks import refresh_rollups

        cur = MagicMock()
        mock_conn.cursor.return_value.__enter__ = lambda s: cur
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

        refresh_rollups()
        calls = [c[0][0] for c in cur.execute.call_args_list]
        assert any("analytics_daily_engagement" in c for c in calls)
        assert any("analytics_mission_rollup" in c for c in calls)
        assert any("analytics_quiz_rollup" in c for c in calls)


class TestManagePartitions:
    @patch("apps.analytics.tasks.connection")
    def test_creates_today_and_tomorrow_partitions(self, mock_conn):
        from apps.analytics.tasks import manage_partitions

        cur = MagicMock()
        cur.fetchall.return_value = []
        mock_conn.cursor.return_value.__enter__ = lambda s: cur
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

        result = manage_partitions()
        # Should have at least 2 CREATE calls (today + tomorrow)
        create_calls = [c for c in cur.execute.call_args_list if "CREATE" in str(c)]
        assert len(create_calls) >= 2
        assert result["dropped"] == []

    @patch("apps.analytics.tasks.connection")
    def test_drops_old_partitions(self, mock_conn):
        from apps.analytics.tasks import manage_partitions, RETENTION_DAYS

        old_date = (datetime.now(timezone.utc).date() - timedelta(days=RETENTION_DAYS + 1))
        old_name = f"analytics_rawevent_{old_date:%Y%m%d}"

        cur = MagicMock()
        cur.fetchall.return_value = [(old_name,)]
        mock_conn.cursor.return_value.__enter__ = lambda s: cur
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

        result = manage_partitions()
        assert old_name in result["dropped"]


class TestScoreRunningExperiments:
    @patch("apps.analytics.tasks.score_experiment")
    @patch("apps.analytics.tasks.Experiment.objects")
    def test_scores_running_experiments(self, mock_qs, mock_score):
        from apps.analytics.tasks import score_running_experiments

        exp1 = MagicMock()
        exp2 = MagicMock()
        mock_qs.filter.return_value = [exp1, exp2]

        result = score_running_experiments()
        assert result["scored"] == 2
        mock_score.assert_any_call(exp1)
        mock_score.assert_any_call(exp2)


class TestWarmCaches:
    @patch("apps.analytics.tasks.RequestFactory")
    @patch("apps.analytics.tasks.PlanetListView")
    @patch("apps.analytics.tasks.TodayView")
    def test_warms_views(self, mock_today, mock_planets, mock_rf):
        # Import will fail in test env without proper Django app, so we patch
        from apps.analytics.tasks import warm_caches

        mock_today.as_view.return_value = MagicMock()
        mock_planets.as_view.return_value = MagicMock()

        result = warm_caches()
        assert result["warmed"] == 2


class TestRunAnomalyChecks:
    @patch("apps.analytics.tasks.run_alert_rules")
    def test_delegates_to_alert_rules(self, mock_rules):
        from apps.analytics.tasks import run_anomaly_checks

        mock_rules.return_value = ["dau_drop"]
        result = run_anomaly_checks()
        assert result == {"alerts": ["dau_drop"]}
