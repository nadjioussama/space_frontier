"""Users: display-name moderation + COPPA consent flow. PLAN §21, §22."""
from __future__ import annotations

from django.test import SimpleTestCase, TestCase

from apps.users.models import (
    AuditLog, ConsentRecord, check_display_name,
)
from apps.users.services import (
    grant_consent, register_parent, request_data_deletion,
    request_name_change, revoke_consent, verify_parent_stripe,
)

from .factories import make_parent, make_player


# --------------------------------------------------------------------------- #
# Display-name auto-filter
# --------------------------------------------------------------------------- #

class DisplayNameFilterTests(SimpleTestCase):
    def test_ok(self):
        ok, reason = check_display_name("StarCommander42")
        self.assertTrue(ok)
        self.assertEqual(reason, "")

    def test_too_short(self):
        ok, reason = check_display_name("a")
        self.assertFalse(ok)

    def test_too_long(self):
        ok, _ = check_display_name("x" * 31)
        self.assertFalse(ok)

    def test_blocked_fragment(self):
        ok, _ = check_display_name("nasa_official_kid")
        self.assertFalse(ok)
        ok, _ = check_display_name("AdminBob")
        self.assertFalse(ok)

    def test_pii_email(self):
        ok, _ = check_display_name("kid@example.com")
        self.assertFalse(ok)

    def test_pii_phone(self):
        ok, _ = check_display_name("call-555-123-4567")
        self.assertFalse(ok)


class SafeDisplayNameTests(TestCase):
    def test_pending_uses_fallback(self):
        p = make_player()
        p.display_name = "RocketKid"
        p.display_name_status = "pending"
        self.assertEqual(p.safe_display_name, f"Explorer-{p.pk}")

    def test_approved_uses_real_name(self):
        p = make_player(username="kid2")
        p.display_name = "RocketKid"
        p.display_name_status = "approved"
        self.assertEqual(p.safe_display_name, "RocketKid")


# --------------------------------------------------------------------------- #
# Name change moderation
# --------------------------------------------------------------------------- #

class NameChangeTests(TestCase):
    def test_auto_approved_for_consented_under_13(self):
        p = make_player()
        p.coppa_consent_given = True
        p.save()
        audit = request_name_change(p, "RocketKid")
        self.assertEqual(audit.moderator_decision, "approved")
        p.refresh_from_db()
        self.assertEqual(p.display_name, "RocketKid")
        self.assertEqual(p.display_name_status, "approved")

    def test_queued_for_unconsented_under_13(self):
        p = make_player(username="kid2")
        audit = request_name_change(p, "RocketKid")
        self.assertEqual(audit.moderator_decision, "pending")
        p.refresh_from_db()
        self.assertEqual(p.display_name_status, "pending")

    def test_auto_rejected_blocked_name(self):
        p = make_player(username="kid3")
        audit = request_name_change(p, "moderator_kid")
        self.assertEqual(audit.moderator_decision, "rejected")
        p.refresh_from_db()
        self.assertEqual(p.display_name_status, "rejected")

    def test_audit_log_written(self):
        p = make_player(username="kid4")
        request_name_change(p, "RocketKid")
        self.assertTrue(
            AuditLog.objects.filter(event_type="name_change", target_player=p).exists()
        )


# --------------------------------------------------------------------------- #
# Parent registration + verification
# --------------------------------------------------------------------------- #

class ParentTests(TestCase):
    def test_register_idempotent_on_email(self):
        a = register_parent(email="p@x.com", full_name="A")
        b = register_parent(email="p@x.com", full_name="B")
        self.assertEqual(a.pk, b.pk)
        b.refresh_from_db()
        self.assertEqual(b.full_name, "B")

    def test_verify_stripe(self):
        parent = register_parent(email="p@x.com", full_name="A")
        self.assertFalse(parent.is_verified)
        verify_parent_stripe(parent, stripe_customer_id="cus_x")
        self.assertTrue(parent.is_verified)
        self.assertIsNotNone(parent.verified_at)


# --------------------------------------------------------------------------- #
# Consent grant / revoke / delete
# --------------------------------------------------------------------------- #

class ConsentTests(TestCase):
    def test_grant_requires_verified_parent(self):
        parent = make_parent(verified=False)
        player = make_player()
        with self.assertRaises(ValueError):
            grant_consent(parent, player)

    def test_grant_records_and_links(self):
        parent = make_parent()
        player = make_player()
        self.assertTrue(player.needs_parental_consent)
        rec = grant_consent(parent, player, ip_address="1.2.3.4", user_agent="ua")
        player.refresh_from_db()
        self.assertTrue(player.coppa_consent_given)
        self.assertEqual(player.parent_id, parent.id)
        self.assertFalse(player.needs_parental_consent)
        self.assertEqual(rec.action, "granted")
        self.assertTrue(
            AuditLog.objects.filter(event_type="consent_grant", target_player=player).exists()
        )

    def test_revoke(self):
        parent = make_parent()
        player = make_player(username="kid2")
        grant_consent(parent, player)
        revoke_consent(parent, player)
        player.refresh_from_db()
        self.assertFalse(player.coppa_consent_given)
        self.assertEqual(
            ConsentRecord.objects.filter(player=player, action="revoked").count(), 1,
        )

    def test_data_deletion(self):
        parent = make_parent()
        player = make_player(username="kid3")
        grant_consent(parent, player)
        request_data_deletion(parent, player)
        player.refresh_from_db()
        self.assertIsNotNone(player.data_deletion_requested_at)
        self.assertTrue(
            AuditLog.objects.filter(event_type="data_delete", target_player=player).exists()
        )
