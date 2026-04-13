"""API views for Phase 3 user management. PLAN §21, §22."""
from __future__ import annotations

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ParentAccount, Player
from .serializers import (
    ConsentGrantSerializer, NameChangeSerializer,
    ParentRegistrationSerializer, PlayerProfileSerializer,
)
from .services import grant_consent, register_parent, request_name_change


class PlayerProfileView(APIView):
    """GET /api/v1/users/me/ — current player profile with consent status."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(PlayerProfileSerializer(request.user).data)


class RegisterParentView(APIView):
    """POST /api/v1/users/parent/register/
    Begins the parental verification flow. Returns a parent_id for subsequent
    steps (Stripe verification, consent grant).

    In production this endpoint also triggers a verification email via SES/SendGrid.
    Walking skeleton skips the actual email and auto-returns the parent_id.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        ser = ParentRegistrationSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        parent = register_parent(
            email=ser.validated_data["email"],
            full_name=ser.validated_data["full_name"],
        )
        return Response({
            "parent_id": str(parent.id),
            "verification_status": parent.verification_status,
            "next_step": "verify_payment" if parent.verification_method == "stripe" else "upload_form",
        }, status=status.HTTP_201_CREATED)


class VerifyParentView(APIView):
    """POST /api/v1/users/parent/verify/
    In production, this endpoint processes a Stripe PaymentIntent confirmation.
    Walking skeleton accepts a mock token and marks the parent as verified.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        parent_id = request.data.get("parent_id")
        parent = get_object_or_404(ParentAccount, id=parent_id)

        # Production: validate Stripe PaymentIntent, refund $0.01.
        # Walking skeleton: auto-verify with a mock customer ID.
        from .services import verify_parent_stripe
        verify_parent_stripe(parent, stripe_customer_id=f"mock_{parent.id}")

        return Response({
            "parent_id": str(parent.id),
            "verification_status": "verified",
        })


class GrantConsentView(APIView):
    """POST /api/v1/users/consent/grant/
    A verified parent grants consent for a specific child player.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        ser = ConsentGrantSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        parent = get_object_or_404(
            ParentAccount, email=ser.validated_data["parent_email"],
        )
        player = get_object_or_404(Player, id=ser.validated_data["player_id"])

        if not parent.is_verified:
            return Response(
                {"detail": "Parent account must be verified first."},
                status=status.HTTP_403_FORBIDDEN,
            )

        ip = request.META.get("REMOTE_ADDR")
        ua = request.META.get("HTTP_USER_AGENT", "")
        record = grant_consent(parent, player, ip_address=ip, user_agent=ua)
        return Response({
            "consent_id": str(record.id),
            "action": record.action,
            "player_id": player.id,
            "coppa_consent_given": player.coppa_consent_given,
        })


class NameChangeView(APIView):
    """POST /api/v1/users/name/
    Submit a display-name change request. Runs through the auto-filter;
    may be auto-approved, auto-rejected, or queued for moderation.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = NameChangeSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        audit = request_name_change(request.user, ser.validated_data["display_name"])
        return Response({
            "proposed_name": audit.proposed_name,
            "decision": audit.moderator_decision,
            "auto_filter_ok": audit.auto_filter_ok,
            "auto_filter_reason": audit.auto_filter_reason,
            "display_name_status": request.user.display_name_status,
        })
