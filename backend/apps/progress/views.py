"""API views for Phase 5 progress, leaderboard, constellation, and DDA. PLAN §3.4, §8.4, §25."""
from __future__ import annotations

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import Player
from . import dda, leaderboard
from .models import Constellation, PlayerStar, SkillStar
from .services import get_player_progress


class ProgressView(APIView):
    """GET /api/v1/progress/me/ — full progress snapshot."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(get_player_progress(request.user))


class DDAStateView(APIView):
    """GET /api/v1/progress/dda/ — current DDA difficulty and content config."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        state = dda.get_state(request.user.id)
        return Response({
            "level": state.current_level,
            "accuracy": round(state.accuracy, 2),
            "topic_levels": state.topic_levels,
            "config": {
                "quiz": dda.get_content_config("quiz", state.current_level),
                "jigsaw": dda.get_content_config("jigsaw", state.current_level),
            },
        })


class LeaderboardWeeklyView(APIView):
    """GET /api/v1/leaderboard/weekly/ — top players this week."""
    permission_classes = [AllowAny]

    def get(self, request):
        top = leaderboard.get_weekly_top(n=50)
        # Attach safe display names (pseudonyms only)
        player_ids = [e["player_id"] for e in top]
        names = {
            p.id: p.safe_display_name
            for p in Player.objects.filter(id__in=player_ids)
        }
        for entry in top:
            entry["display_name"] = names.get(entry["player_id"], f"Explorer-{entry['player_id']}")
        return Response({"period": "weekly", "entries": top})


class LeaderboardPlanetView(APIView):
    """GET /api/v1/leaderboard/planet/<slug>/ — per-planet top players."""
    permission_classes = [AllowAny]

    def get(self, request, slug: str):
        top = leaderboard.get_planet_top(slug, n=50)
        player_ids = [e["player_id"] for e in top]
        names = {
            p.id: p.safe_display_name
            for p in Player.objects.filter(id__in=player_ids)
        }
        for entry in top:
            entry["display_name"] = names.get(entry["player_id"], f"Explorer-{entry['player_id']}")
        return Response({"period": "weekly", "planet": slug, "entries": top})


class ConstellationListView(APIView):
    """GET /api/v1/progress/constellations/ — skill tree for the current player."""
    permission_classes = [AllowAny]

    def get(self, request):
        constellations = Constellation.objects.prefetch_related("stars", "stars__prerequisites").all()
        earned_ids = set()
        if request.user.is_authenticated:
            earned_ids = set(
                PlayerStar.objects.filter(player=request.user).values_list("star_id", flat=True)
            )

        data = []
        for c in constellations:
            stars = []
            for s in c.stars.all():
                stars.append({
                    "id": s.id,
                    "slug": s.slug,
                    "name": s.name,
                    "description": s.description,
                    "xp_value": s.xp_value,
                    "x": s.display_x,
                    "y": s.display_y,
                    "earned": s.id in earned_ids,
                    "prerequisites": [p.slug for p in s.prerequisites.all()],
                })
            data.append({
                "slug": c.slug,
                "name": c.name,
                "topic": c.topic,
                "description": c.description,
                "icon": c.icon,
                "stars": stars,
                "earned_count": sum(1 for s in stars if s["earned"]),
                "total_count": len(stars),
            })
        return Response(data)
