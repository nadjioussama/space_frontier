"""DRF views for Phase 1 endpoints. PLAN §7.4."""
from __future__ import annotations

import logging

from django.core.cache import cache
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.nasa_ingest.models import APODEntry
from .models import Mission, Planet, Quiz
from .serializers import (
    MissionDetailSerializer,
    PlanetSerializer,
    TodayPayloadSerializer,
)

logger = logging.getLogger(__name__)


class TodayView(APIView):
    """GET /api/v1/nasa/today/  — APOD + live context. Redis-first."""

    def get(self, request):
        cached = cache.get("nasa:today")
        if cached:
            return Response(cached, headers={"X-Cache": "HIT"})
        entry = APODEntry.objects.filter(is_published=True).order_by("-date").first()
        if not entry:
            return Response(
                {"detail": "No APOD available yet. Run `python manage.py ingest_apod`."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        payload = TodayPayloadSerializer.build(entry)
        cache.set("nasa:today", payload, timeout=3600)
        return Response(payload, headers={"X-Cache": "MISS"})


class PlanetListView(APIView):
    """GET /api/v1/planets/  — Space Map nodes."""

    def get(self, request):
        cached = cache.get("planets:list")
        if cached:
            return Response(cached, headers={"X-Cache": "HIT"})
        data = PlanetSerializer(Planet.objects.all(), many=True).data
        cache.set("planets:list", data, timeout=6 * 3600)
        return Response(data, headers={"X-Cache": "MISS"})


class PlanetDetailView(APIView):
    """GET /api/v1/planets/<slug>/  — planet + its published missions."""

    def get(self, request, slug: str):
        planet = get_object_or_404(Planet, slug=slug)
        missions = planet.missions.filter(is_published=True).order_by("-created_at")[:10]
        return Response({
            "planet": PlanetSerializer(planet).data,
            "missions": [
                {"slug": m.slug, "title": m.title, "mission_type": m.mission_type,
                 "xp_reward": m.xp_reward, "difficulty": m.difficulty}
                for m in missions
            ],
        })


class MissionDetailView(APIView):
    """GET /api/v1/missions/<slug>/  — everything the game viewport needs."""

    def get(self, request, slug: str):
        key = f"mission:{slug}"
        cached = cache.get(key)
        if cached:
            return Response(cached, headers={"X-Cache": "HIT"})
        mission = get_object_or_404(
            Mission.objects.select_related("apod", "jigsaw")
                           .prefetch_related("quizzes"),
            slug=slug, is_published=True,
        )
        data = MissionDetailSerializer(mission).data
        cache.set(key, data, timeout=24 * 3600)
        return Response(data, headers={"X-Cache": "MISS"})


class AttemptView(APIView):
    """POST /api/v1/missions/<slug>/attempt/
    Body: { "quiz_answers": [{"quiz_id": 1, "answer": "..."}], "jigsaw_completed": true }
    Returns per-answer correctness + XP earned.
    """

    def post(self, request, slug: str):
        mission = get_object_or_404(Mission, slug=slug, is_published=True)
        answers = request.data.get("quiz_answers", []) or []
        jigsaw_completed = bool(request.data.get("jigsaw_completed"))

        if not isinstance(answers, list):
            return Response({"detail": "quiz_answers must be a list"}, status=400)

        results = []
        correct_count = 0
        quiz_ids = [a.get("quiz_id") for a in answers if isinstance(a, dict)]
        quizzes = {q.id: q for q in Quiz.objects.filter(id__in=quiz_ids, mission=mission)}
        for a in answers:
            if not isinstance(a, dict):
                continue
            qid = a.get("quiz_id")
            submitted = (a.get("answer") or "").strip()
            quiz = quizzes.get(qid)
            if not quiz:
                results.append({"quiz_id": qid, "correct": False, "reason": "unknown quiz"})
                continue
            is_correct = submitted == quiz.correct_answer
            if is_correct:
                correct_count += 1
            results.append({
                "quiz_id": qid,
                "correct": is_correct,
                "correct_answer": quiz.correct_answer,
                "explanation": quiz.explanation,
            })

        # XP: proportional to quiz performance + bonus for jigsaw completion.
        total_quizzes = max(len(quizzes), 1)
        quiz_fraction = correct_count / total_quizzes
        xp = int(round(mission.xp_reward * (0.6 * quiz_fraction + 0.4 * (1 if jigsaw_completed else 0))))

        from apps.progress.services import record_attempt
        progress_snapshot = record_attempt(
            request.user if request.user.is_authenticated else None,
            mission, xp=xp, quiz_correct=correct_count, quiz_total=total_quizzes,
            jigsaw_completed=jigsaw_completed,
        )

        return Response({
            "mission_slug": mission.slug,
            "results": results,
            "xp_earned": xp,
            "progress": progress_snapshot,
        })
