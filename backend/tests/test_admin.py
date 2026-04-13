"""Tests for Django admin registration and custom actions across all apps."""
from unittest.mock import MagicMock, patch
from datetime import date

import pytest
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory

from tests.factories import make_player, make_parent


# --------------------------------------------------------------------------- #
# Users admin
# --------------------------------------------------------------------------- #

@pytest.mark.django_db
class TestUsersAdmin:
    def test_player_admin_registered(self):
        from django.contrib import admin
        from apps.users.models import Player
        assert Player in admin.site._registry

    def test_parent_account_admin_registered(self):
        from django.contrib import admin
        from apps.users.models import ParentAccount
        assert ParentAccount in admin.site._registry

    def test_consent_record_admin_readonly(self):
        from apps.users.admin import ConsentRecordAdmin
        admin_cls = ConsentRecordAdmin(MagicMock(), AdminSite())
        assert admin_cls.has_add_permission(MagicMock()) is False
        assert admin_cls.has_change_permission(MagicMock()) is False
        assert admin_cls.has_delete_permission(MagicMock()) is False

    def test_audit_log_admin_readonly(self):
        from apps.users.admin import AuditLogAdmin
        admin_cls = AuditLogAdmin(MagicMock(), AdminSite())
        assert admin_cls.has_add_permission(MagicMock()) is False
        assert admin_cls.has_change_permission(MagicMock()) is False
        assert admin_cls.has_delete_permission(MagicMock()) is False

    def test_approve_names_action(self):
        from apps.users.admin import DisplayNameAuditAdmin
        from apps.users.models import DisplayNameAudit

        player = make_player(username="approvetester")
        moderator = make_player(username="mod1", is_staff=True)

        audit = DisplayNameAudit.objects.create(
            player=player, proposed_name="SpaceCadet",
            auto_filter_ok=True, moderator_decision="pending",
        )
        admin_cls = DisplayNameAuditAdmin(DisplayNameAudit, AdminSite())
        request = RequestFactory().get("/")
        request.user = moderator

        admin_cls.approve_names(request, DisplayNameAudit.objects.filter(pk=audit.pk))

        audit.refresh_from_db()
        player.refresh_from_db()
        assert audit.moderator_decision == "approved"
        assert player.display_name == "SpaceCadet"
        assert player.display_name_status == "approved"

    def test_reject_names_action(self):
        from apps.users.admin import DisplayNameAuditAdmin
        from apps.users.models import DisplayNameAudit

        player = make_player(username="rejecttester")
        moderator = make_player(username="mod2", is_staff=True)

        audit = DisplayNameAudit.objects.create(
            player=player, proposed_name="BadName",
            auto_filter_ok=False, moderator_decision="pending",
        )
        admin_cls = DisplayNameAuditAdmin(DisplayNameAudit, AdminSite())
        request = RequestFactory().get("/")
        request.user = moderator

        admin_cls.reject_names(request, DisplayNameAudit.objects.filter(pk=audit.pk))

        audit.refresh_from_db()
        player.refresh_from_db()
        assert audit.moderator_decision == "rejected"
        assert player.display_name_status == "rejected"


# --------------------------------------------------------------------------- #
# Games admin
# --------------------------------------------------------------------------- #

class TestGamesAdmin:
    def test_planet_admin_registered(self):
        from django.contrib import admin
        from apps.games.models import Planet
        assert Planet in admin.site._registry

    def test_mission_admin_registered(self):
        from django.contrib import admin
        from apps.games.models import Mission
        assert Mission in admin.site._registry

    def test_mission_admin_has_inlines(self):
        from apps.games.admin import MissionAdmin
        admin_cls = MissionAdmin(MagicMock(), AdminSite())
        inline_models = [i.model for i in admin_cls.inlines]
        from apps.games.models import Quiz, JigsawPuzzle
        assert Quiz in inline_models
        assert JigsawPuzzle in inline_models


# --------------------------------------------------------------------------- #
# Progress admin
# --------------------------------------------------------------------------- #

class TestProgressAdmin:
    def test_attempt_admin_registered(self):
        from django.contrib import admin
        from apps.progress.models import Attempt
        assert Attempt in admin.site._registry

    def test_constellation_admin_registered(self):
        from django.contrib import admin
        from apps.progress.models import Constellation
        assert Constellation in admin.site._registry

    def test_achievement_admin_registered(self):
        from django.contrib import admin
        from apps.progress.models import Achievement
        assert Achievement in admin.site._registry

    def test_player_streak_admin_registered(self):
        from django.contrib import admin
        from apps.progress.models import PlayerStreak
        assert PlayerStreak in admin.site._registry

    def test_constellation_admin_has_inline(self):
        from apps.progress.admin import ConstellationAdmin
        admin_cls = ConstellationAdmin(MagicMock(), AdminSite())
        inline_models = [i.model for i in admin_cls.inlines]
        from apps.progress.models import SkillStar
        assert SkillStar in inline_models


# --------------------------------------------------------------------------- #
# NASA Ingest admin
# --------------------------------------------------------------------------- #

class TestNASAIngestAdmin:
    def test_apod_admin_registered(self):
        from django.contrib import admin
        from apps.nasa_ingest.models import APODEntry
        assert APODEntry in admin.site._registry

    def test_mars_photo_admin_registered(self):
        from django.contrib import admin
        from apps.nasa_ingest.models import MarsPhoto
        assert MarsPhoto in admin.site._registry

    def test_neo_object_admin_registered(self):
        from django.contrib import admin
        from apps.nasa_ingest.models import NEOObject
        assert NEOObject in admin.site._registry

    def test_epic_image_admin_registered(self):
        from django.contrib import admin
        from apps.nasa_ingest.models import EPICImage
        assert EPICImage in admin.site._registry

    def test_exoplanet_admin_registered(self):
        from django.contrib import admin
        from apps.nasa_ingest.models import Exoplanet
        assert Exoplanet in admin.site._registry

    def test_neo_admin_has_approach_inline(self):
        from apps.nasa_ingest.admin import NEOObjectAdmin
        admin_cls = NEOObjectAdmin(MagicMock(), AdminSite())
        inline_models = [i.model for i in admin_cls.inlines]
        from apps.nasa_ingest.models import NEOApproach
        assert NEOApproach in inline_models


# --------------------------------------------------------------------------- #
# Analytics admin
# --------------------------------------------------------------------------- #

class TestAnalyticsAdmin:
    def test_experiment_admin_registered(self):
        from django.contrib import admin
        from apps.analytics.models import Experiment
        assert Experiment in admin.site._registry

    def test_rollup_admins_readonly(self):
        from apps.analytics.admin import (
            DailyEngagementAdmin, MissionRollupAdmin, QuizRollupAdmin,
        )
        for admin_cls_type in (DailyEngagementAdmin, MissionRollupAdmin, QuizRollupAdmin):
            admin_cls = admin_cls_type(MagicMock(), AdminSite())
            assert admin_cls.has_add_permission(MagicMock()) is False
            assert admin_cls.has_change_permission() is False
            assert admin_cls.has_delete_permission() is False

    def test_experiment_admin_has_variant_inline(self):
        from apps.analytics.admin import ExperimentAdmin
        admin_cls = ExperimentAdmin(MagicMock(), AdminSite())
        inline_models = [i.model for i in admin_cls.inlines]
        from apps.analytics.models import ExperimentVariant
        assert ExperimentVariant in inline_models

    @patch("apps.analytics.ab_testing.score_experiment")
    def test_score_now_action(self, mock_score):
        from apps.analytics.admin import ExperimentAdmin
        from apps.analytics.models import Experiment

        admin_cls = ExperimentAdmin(Experiment, AdminSite())
        exp = MagicMock()
        admin_cls.score_now(MagicMock(), [exp])
        mock_score.assert_called_once_with(exp)
