"""Player, ParentAccount, consent, moderation, and audit models. PLAN §8.2, §21, §22.

COPPA requires verifiable parental consent for children under 13 before collecting
personal information. GDPR-K extends similar protections to EU children. Our model:

- Children play without an account (anonymous, localStorage identity, Phase 1+2).
- When a child wants to save progress to the server, a parent registers and provides
  consent. The parent's verified account is the legal data controller.
- Display names go through a moderation queue before becoming visible.
"""
from __future__ import annotations

import re
import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


# --------------------------------------------------------------------------- #
# Display-name blocklist (Phase 3 basic filter; Phase 5 can use ML scoring)
# --------------------------------------------------------------------------- #

# Words that auto-reject a display name. Keep this list small and unambiguous;
# Phase 5 adds fuzzy/ML matching. The moderation queue catches what the filter misses.
_BLOCKED_FRAGMENTS: list[str] = [
    # slurs, profanity, PII patterns — intentionally abbreviated here; a real
    # deployment loads from a managed data file outside version control.
    "admin", "moderator", "nasa_official",
]

_PII_PATTERNS = [
    re.compile(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"),  # US phone
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),  # email
]


def check_display_name(name: str) -> tuple[bool, str]:
    """Return (ok, reason). Fast, synchronous, no DB hit."""
    lower = name.lower().strip()
    if len(lower) < 2:
        return False, "Too short"
    if len(lower) > 30:
        return False, "Too long (max 30 characters)"
    for frag in _BLOCKED_FRAGMENTS:
        if frag in lower:
            return False, "Contains a reserved or blocked word"
    for pat in _PII_PATTERNS:
        if pat.search(name):
            return False, "Looks like personal information — please pick a fun space name!"
    return True, ""


# --------------------------------------------------------------------------- #
# Core models
# --------------------------------------------------------------------------- #

class Player(AbstractUser):
    AGE_GROUPS = [("6-8", "6-8"), ("9-11", "9-11"), ("12-14", "12-14"), ("adult", "adult")]
    NAME_STATUS_CHOICES = [
        ("pending", "Pending review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    display_name = models.CharField(max_length=50, blank=True)
    display_name_status = models.CharField(
        max_length=10, choices=NAME_STATUS_CHOICES, default="pending",
    )
    age_group = models.CharField(max_length=8, choices=AGE_GROUPS, default="9-11")
    avatar_config = models.JSONField(default=dict, blank=True)
    parent = models.ForeignKey(
        "ParentAccount", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="children",
    )
    coppa_consent_given = models.BooleanField(default=False)
    coppa_consent_at = models.DateTimeField(null=True, blank=True)
    is_under_13 = models.BooleanField(default=True)
    data_deletion_requested_at = models.DateTimeField(null=True, blank=True)

    class Meta(AbstractUser.Meta):
        pass

    def __str__(self) -> str:
        return self.display_name or self.username

    @property
    def safe_display_name(self) -> str:
        """Return the display name only if approved; otherwise a fallback."""
        if self.display_name_status == "approved":
            return self.display_name
        return f"Explorer-{self.pk or '?'}"

    @property
    def needs_parental_consent(self) -> bool:
        return self.is_under_13 and not self.coppa_consent_given


class ParentAccount(models.Model):
    """The adult who provides verifiable consent. PLAN §21.3.

    Stripe charges $0.01 (refunded) to verify the parent controls a real payment
    method — an FTC-accepted verification mechanism. Alternatively we accept
    a signed consent form uploaded and reviewed by a moderator.
    """
    VERIFICATION_METHODS = [
        ("stripe", "Credit card micro-charge via Stripe"),
        ("form", "Signed consent form reviewed by moderator"),
    ]
    VERIFICATION_STATUSES = [
        ("pending", "Pending"),
        ("verified", "Verified"),
        ("rejected", "Rejected"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=200)
    verification_method = models.CharField(max_length=10, choices=VERIFICATION_METHODS, default="stripe")
    verification_status = models.CharField(max_length=10, choices=VERIFICATION_STATUSES, default="pending")
    verified_at = models.DateTimeField(null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Parent account"

    def __str__(self) -> str:
        return f"{self.full_name} <{self.email}>"

    @property
    def is_verified(self) -> bool:
        return self.verification_status == "verified"


class ConsentRecord(models.Model):
    """Immutable audit trail of consent events. PLAN §21.4.

    Every grant or revocation of consent is recorded. GDPR requires evidence
    of consent with timestamp, scope, and mechanism.
    """
    ACTION_CHOICES = [
        ("granted", "Consent granted"),
        ("revoked", "Consent revoked"),
        ("data_deletion", "Data deletion requested"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey(ParentAccount, on_delete=models.PROTECT, related_name="consent_records")
    player = models.ForeignKey(Player, on_delete=models.PROTECT, related_name="consent_records")
    action = models.CharField(max_length=16, choices=ACTION_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("-timestamp",)
        indexes = [models.Index(fields=["parent", "-timestamp"])]

    def __str__(self) -> str:
        return f"{self.action} by {self.parent_id} for player {self.player_id} @ {self.timestamp}"


class DisplayNameAudit(models.Model):
    """Tracks every display-name change and its moderation outcome. PLAN §22."""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="name_audits")
    proposed_name = models.CharField(max_length=50)
    auto_filter_ok = models.BooleanField()
    auto_filter_reason = models.CharField(max_length=200, blank=True)
    moderator_decision = models.CharField(
        max_length=10, choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")],
        default="pending",
    )
    moderator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="moderation_decisions",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"'{self.proposed_name}' for player {self.player_id} ({self.moderator_decision})"


class AuditLog(models.Model):
    """General-purpose audit log for compliance-relevant events. PLAN §21.5."""
    EVENT_TYPES = [
        ("login", "Login"),
        ("consent_grant", "Consent granted"),
        ("consent_revoke", "Consent revoked"),
        ("data_export", "Data export requested"),
        ("data_delete", "Data deletion requested"),
        ("name_change", "Display name change"),
        ("admin_action", "Admin action"),
    ]
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+",
    )
    target_player = models.ForeignKey(
        Player, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="audit_events",
    )
    detail = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ("-timestamp",)

    def __str__(self) -> str:
        return f"{self.event_type} @ {self.timestamp}"
