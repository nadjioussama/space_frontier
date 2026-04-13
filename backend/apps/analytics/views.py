"""Event ingest + experiment-assignment endpoints."""
from __future__ import annotations

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from . import stream
from .ab_testing import assignments_for
from .events import validate

MAX_BATCH = 50


class EventIngestView(APIView):
    """POST /api/v1/events/ — accepts a batch of client events.

    Anonymous allowed (children play without accounts in Phase 1-2). The
    server supplies player_id/age_group from the auth token when present and
    ignores any client-supplied identity.
    """

    permission_classes = [permissions.AllowAny]
    authentication_classes = []  # don't 401 anonymous kids; auth is optional via header

    def post(self, request):
        events = request.data.get("events")
        if not isinstance(events, list):
            return Response({"detail": "events[] required"}, status=status.HTTP_400_BAD_REQUEST)

        player = getattr(request, "user", None)
        player_id = getattr(player, "id", None) if player and getattr(player, "is_authenticated", False) else None
        age_group = getattr(player, "age_group", None) if player_id else None

        accepted = 0
        for raw in events[:MAX_BATCH]:
            ev = validate(raw, player_id=player_id, age_group=age_group)
            if ev is None:
                continue
            stream.push(ev.to_record())
            accepted += 1

        return Response({"accepted": accepted}, status=status.HTTP_202_ACCEPTED)


class ExperimentAssignmentView(APIView):
    """GET /api/v1/experiments/ — variant config for the current player."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        player = request.user
        return Response(assignments_for(player))
