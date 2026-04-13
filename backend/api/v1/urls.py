from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.games.views import (
    AttemptView, MissionDetailView, PlanetDetailView, PlanetListView, TodayView,
)
from apps.progress.views import (
    ConstellationListView, DDAStateView, LeaderboardPlanetView,
    LeaderboardWeeklyView, ProgressView,
)
from apps.analytics.views import EventIngestView, ExperimentAssignmentView
from apps.users.views import (
    GrantConsentView, NameChangeView, PlayerProfileView,
    RegisterParentView, VerifyParentView,
)

urlpatterns = [
    # --- Game content (Phase 1+2) ----------------------------------------
    path("nasa/today/", TodayView.as_view(), name="nasa-today"),
    path("planets/", PlanetListView.as_view(), name="planet-list"),
    path("planets/<slug:slug>/", PlanetDetailView.as_view(), name="planet-detail"),
    path("missions/<slug:slug>/", MissionDetailView.as_view(), name="mission-detail"),
    path("missions/<slug:slug>/attempt/", AttemptView.as_view(), name="mission-attempt"),

    # --- Auth (Phase 3) --------------------------------------------------
    path("auth/token/", TokenObtainPairView.as_view(), name="token-obtain"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),

    # --- Users + COPPA (Phase 3) -----------------------------------------
    path("users/me/", PlayerProfileView.as_view(), name="player-profile"),
    path("users/name/", NameChangeView.as_view(), name="name-change"),
    path("users/parent/register/", RegisterParentView.as_view(), name="parent-register"),
    path("users/parent/verify/", VerifyParentView.as_view(), name="parent-verify"),
    path("users/consent/grant/", GrantConsentView.as_view(), name="consent-grant"),

    # --- Progress, DDA, Leaderboard, Constellation (Phase 5) -------------
    path("progress/me/", ProgressView.as_view(), name="progress-me"),
    path("progress/dda/", DDAStateView.as_view(), name="dda-state"),
    path("progress/constellations/", ConstellationListView.as_view(), name="constellation-list"),
    path("leaderboard/weekly/", LeaderboardWeeklyView.as_view(), name="leaderboard-weekly"),
    path("leaderboard/planet/<slug:slug>/", LeaderboardPlanetView.as_view(), name="leaderboard-planet"),

    # --- Analytics + experiments (Phase 8) -------------------------------
    path("events/", EventIngestView.as_view(), name="analytics-events"),
    path("experiments/", ExperimentAssignmentView.as_view(), name="experiments"),
]
