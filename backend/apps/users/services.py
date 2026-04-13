"""Business logic for COPPA consent, parental verification, and moderation.

PLAN §21.3 (verification flow), §22 (display-name moderation).
"""
from __future__ import annotations

import logging
from typing import Any

from django.utils import timezone

from .models import (
    AuditLog, ConsentRecord, DisplayNameAudit, ParentAccount, Player,
    check_display_name,
)

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Parent registration + verification
# --------------------------------------------------------------------------- #

def register_parent(*, email: str, full_name: str, method: str = "stripe") -> ParentAccount:
    parent, created = ParentAccount.objects.get_or_create(
        email=email,
        defaults={"full_name": full_name, "verification_method": method},
    )
    if not created:
        # Re-registration — update name, keep existing verification state
        parent.full_name = full_name
        parent.save(update_fields=["full_name"])
    return parent


def verify_parent_stripe(parent: ParentAccount, *, stripe_customer_id: str) -> ParentAccount:
    """Mark the parent as verified after a successful Stripe micro-charge.

    The actual Stripe interaction (create customer, charge $0.01, refund) lives
    in the view layer or a dedicated Stripe integration module. This function
    records the outcome.
    """
    parent.stripe_customer_id = stripe_customer_id
    parent.verification_status = "verified"
    parent.verified_at = timezone.now()
    parent.save(update_fields=["stripe_customer_id", "verification_status", "verified_at"])
    return parent


# --------------------------------------------------------------------------- #
# Consent grant / revoke
# --------------------------------------------------------------------------- #

def grant_consent(
    parent: ParentAccount,
    player: Player,
    *,
    ip_address: str | None = None,
    user_agent: str = "",
) -> ConsentRecord:
    """Record verifiable consent from a verified parent for a child player."""
    if not parent.is_verified:
        raise ValueError("Parent account must be verified before granting consent")

    player.parent = parent
    player.coppa_consent_given = True
    player.coppa_consent_at = timezone.now()
    player.save(update_fields=["parent", "coppa_consent_given", "coppa_consent_at"])

    record = ConsentRecord.objects.create(
        parent=parent,
        player=player,
        action="granted",
        ip_address=ip_address,
        user_agent=user_agent,
    )
    AuditLog.objects.create(
        event_type="consent_grant",
        actor=player,
        target_player=player,
        detail={"parent_id": str(parent.id), "method": parent.verification_method},
        ip_address=ip_address,
    )
    return record


def revoke_consent(
    parent: ParentAccount,
    player: Player,
    *,
    ip_address: str | None = None,
    user_agent: str = "",
) -> ConsentRecord:
    """Revoke consent — stops data collection for the child."""
    player.coppa_consent_given = False
    player.save(update_fields=["coppa_consent_given"])

    record = ConsentRecord.objects.create(
        parent=parent,
        player=player,
        action="revoked",
        ip_address=ip_address,
        user_agent=user_agent,
    )
    AuditLog.objects.create(
        event_type="consent_revoke",
        actor=player,
        target_player=player,
        ip_address=ip_address,
    )
    return record


def request_data_deletion(
    parent: ParentAccount,
    player: Player,
    *,
    ip_address: str | None = None,
) -> ConsentRecord:
    """Parent requests deletion of all child data. PLAN §21.5."""
    player.data_deletion_requested_at = timezone.now()
    player.save(update_fields=["data_deletion_requested_at"])

    record = ConsentRecord.objects.create(
        parent=parent,
        player=player,
        action="data_deletion",
        ip_address=ip_address,
    )
    AuditLog.objects.create(
        event_type="data_delete",
        actor=player,
        target_player=player,
        ip_address=ip_address,
    )
    # Actual deletion is handled by a Celery task (not automated here — requires
    # human review within 72 hours per GDPR).
    return record


# --------------------------------------------------------------------------- #
# Display name moderation
# --------------------------------------------------------------------------- #

def request_name_change(player: Player, proposed_name: str) -> DisplayNameAudit:
    """Submit a display name for moderation. Auto-filter first, then queue."""
    ok, reason = check_display_name(proposed_name)
    audit = DisplayNameAudit.objects.create(
        player=player,
        proposed_name=proposed_name.strip(),
        auto_filter_ok=ok,
        auto_filter_reason=reason,
    )

    if ok:
        # Auto-approve names that pass the filter for verified players (parent
        # consented + under-13 cleared). Others still need human review.
        if not player.is_under_13 or player.coppa_consent_given:
            audit.moderator_decision = "approved"
            audit.reviewed_at = timezone.now()
            audit.save(update_fields=["moderator_decision", "reviewed_at"])
            player.display_name = proposed_name.strip()
            player.display_name_status = "approved"
            player.save(update_fields=["display_name", "display_name_status"])
        else:
            # Under-13 without consent: name is pending manual review
            player.display_name = proposed_name.strip()
            player.display_name_status = "pending"
            player.save(update_fields=["display_name", "display_name_status"])
    else:
        # Auto-rejected — reason returned to user
        audit.moderator_decision = "rejected"
        audit.reviewed_at = timezone.now()
        audit.save(update_fields=["moderator_decision", "reviewed_at"])
        player.display_name_status = "rejected"
        player.save(update_fields=["display_name_status"])

    AuditLog.objects.create(
        event_type="name_change",
        actor=player,
        target_player=player,
        detail={"proposed": proposed_name, "auto_ok": ok, "reason": reason},
    )
    return audit
