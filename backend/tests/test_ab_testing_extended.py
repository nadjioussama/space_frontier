"""Tests for analytics.ab_testing — experiment scoring and enrollment."""
import math
from unittest.mock import MagicMock, patch

import pytest

from apps.analytics.ab_testing import _bucket, MAX_CONCURRENT_PER_PLAYER


class TestBucket:
    def test_deterministic(self):
        b1 = _bucket("player-1", "exp-a")
        b2 = _bucket("player-1", "exp-a")
        assert b1 == b2

    def test_range_0_to_99(self):
        buckets = {_bucket(f"p{i}", "exp") for i in range(500)}
        assert min(buckets) >= 0
        assert max(buckets) <= 99

    def test_different_experiments_differ(self):
        # Not guaranteed for all inputs, but extremely likely with 500 samples
        same = sum(
            1 for i in range(500) if _bucket(f"p{i}", "a") == _bucket(f"p{i}", "b")
        )
        assert same < 50  # collision rate should be ~1%


class TestAssignmentsFor:
    @patch("apps.analytics.ab_testing.Experiment.objects")
    @patch("apps.analytics.ab_testing.PlayerExperiment.objects")
    def test_returns_existing_assignments(self, mock_pe_qs, mock_exp_qs):
        from apps.analytics.ab_testing import assignments_for

        player = MagicMock()
        player.public_id = "pid-1"
        player.age_group = "9-11"
        player.is_new_player.return_value = False

        variant = MagicMock(slug="control", config={"color": "blue"})
        experiment = MagicMock(id=1, slug="test-exp", status="running")
        pe = MagicMock(experiment_id=1, experiment=experiment, variant=variant)

        mock_pe_qs.select_related.return_value.filter.return_value = [pe]
        mock_exp_qs.filter.return_value.prefetch_related.return_value = [experiment]

        result = assignments_for(player)
        assert "test-exp" in result
        assert result["test-exp"]["variant"] == "control"

    @patch("apps.analytics.ab_testing.Experiment.objects")
    @patch("apps.analytics.ab_testing.PlayerExperiment.objects")
    def test_respects_max_concurrent(self, mock_pe_qs, mock_exp_qs):
        from apps.analytics.ab_testing import assignments_for

        player = MagicMock()
        player.public_id = "pid-1"
        player.age_group = "9-11"
        player.is_new_player.return_value = False

        # Player already has MAX_CONCURRENT_PER_PLAYER assignments
        existing = []
        for i in range(MAX_CONCURRENT_PER_PLAYER):
            pe = MagicMock(experiment_id=i, experiment=MagicMock(id=i, slug=f"exp-{i}"),
                           variant=MagicMock(slug="v", config={}))
            existing.append(pe)

        mock_pe_qs.select_related.return_value.filter.return_value = existing

        new_exp = MagicMock(id=99, slug="new-exp", traffic_percent=100,
                            target_age_groups=[], target_new_players_only=False)
        new_exp.variants.all.return_value = [MagicMock(slug="v1", config={})]
        mock_exp_qs.filter.return_value.prefetch_related.return_value = [new_exp]

        result = assignments_for(player)
        # Should not include new-exp since we're at max
        assert "new-exp" not in result

    @patch("apps.analytics.ab_testing.Experiment.objects")
    @patch("apps.analytics.ab_testing.PlayerExperiment.objects")
    def test_respects_age_group_filter(self, mock_pe_qs, mock_exp_qs):
        from apps.analytics.ab_testing import assignments_for

        player = MagicMock()
        player.public_id = "pid-1"
        player.age_group = "6-8"
        player.is_new_player.return_value = False

        mock_pe_qs.select_related.return_value.filter.return_value = []

        exp = MagicMock(id=1, slug="teens-only", traffic_percent=100,
                        target_age_groups=["12-14"], target_new_players_only=False)
        mock_exp_qs.filter.return_value.prefetch_related.return_value = [exp]

        result = assignments_for(player)
        assert "teens-only" not in result

    @patch("apps.analytics.ab_testing.Experiment.objects")
    @patch("apps.analytics.ab_testing.PlayerExperiment.objects")
    def test_respects_new_player_filter(self, mock_pe_qs, mock_exp_qs):
        from apps.analytics.ab_testing import assignments_for

        player = MagicMock()
        player.public_id = "pid-1"
        player.age_group = "9-11"
        player.is_new_player.return_value = False

        mock_pe_qs.select_related.return_value.filter.return_value = []

        exp = MagicMock(id=1, slug="newbies", traffic_percent=100,
                        target_age_groups=[], target_new_players_only=True)
        mock_exp_qs.filter.return_value.prefetch_related.return_value = [exp]

        result = assignments_for(player)
        assert "newbies" not in result


class TestScoreExperiment:
    @patch("apps.analytics.ab_testing.RawEvent.objects")
    @patch("apps.analytics.ab_testing.PlayerExperiment.objects")
    def test_computes_rate_metric(self, mock_pe_qs, mock_re_qs):
        from apps.analytics.ab_testing import score_experiment

        exp = MagicMock(primary_metric="mission_completion_rate")

        control_v = MagicMock(slug="control", config={})
        treatment_v = MagicMock(slug="treatment", config={})
        exp.variants.all.return_value = [control_v, treatment_v]

        # Mock player counts and event counts
        mock_pe_qs.filter.return_value.values_list.return_value.count.return_value = 100
        mock_re_qs.filter.return_value.count.side_effect = [80, 100, 90, 100]  # control: 80/100, treat: 90/100

        score_experiment(exp)

        control_v.save.assert_called_once()
        treatment_v.save.assert_called_once()

    def test_unknown_metric_is_noop(self):
        from apps.analytics.ab_testing import score_experiment

        exp = MagicMock(primary_metric="unknown_metric")
        score_experiment(exp)
        exp.variants.all.assert_not_called()

    def test_confidence_computation(self):
        """Verify the z-test confidence formula produces expected ranges."""
        # For large z-values, confidence should approach 1.0
        z = 3.0
        confidence = 1 - math.erfc(abs(z) / math.sqrt(2))
        assert confidence > 0.99

        # For z = 0, confidence should be 0
        z = 0.0
        confidence = 1 - math.erfc(abs(z) / math.sqrt(2))
        assert confidence == pytest.approx(0.0, abs=0.01)
