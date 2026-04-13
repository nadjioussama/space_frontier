from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from .models import (
    AuditLog, ConsentRecord, DisplayNameAudit, ParentAccount, Player,
)


# --------------------------------------------------------------------------- #
# Player
# --------------------------------------------------------------------------- #

@admin.register(Player)
class PlayerAdmin(UserAdmin):
    list_display = ("username", "display_name", "display_name_status", "age_group",
                    "coppa_consent_given", "is_under_13", "is_staff")
    list_filter = ("display_name_status", "age_group", "is_under_13", "coppa_consent_given")
    search_fields = ("username", "display_name")
    fieldsets = UserAdmin.fieldsets + (
        ("Player profile", {"fields": (
            "display_name", "display_name_status", "age_group", "avatar_config",
        )}),
        ("COPPA / Privacy", {"fields": (
            "parent", "is_under_13", "coppa_consent_given", "coppa_consent_at",
            "data_deletion_requested_at",
        )}),
    )
    readonly_fields = ("coppa_consent_at", "data_deletion_requested_at")


# --------------------------------------------------------------------------- #
# Parent account
# --------------------------------------------------------------------------- #

@admin.register(ParentAccount)
class ParentAccountAdmin(admin.ModelAdmin):
    list_display = ("email", "full_name", "verification_status", "verification_method", "created_at")
    list_filter = ("verification_status", "verification_method")
    search_fields = ("email", "full_name")
    readonly_fields = ("id", "created_at", "verified_at", "stripe_customer_id")


# --------------------------------------------------------------------------- #
# Display name moderation queue
# --------------------------------------------------------------------------- #

@admin.register(DisplayNameAudit)
class DisplayNameAuditAdmin(admin.ModelAdmin):
    list_display = ("proposed_name", "player", "auto_filter_ok", "moderator_decision",
                    "moderator", "created_at")
    list_filter = ("moderator_decision", "auto_filter_ok")
    search_fields = ("proposed_name",)
    readonly_fields = ("player", "proposed_name", "auto_filter_ok", "auto_filter_reason",
                       "created_at")
    actions = ["approve_names", "reject_names"]

    @admin.action(description="Approve selected display names")
    def approve_names(self, request, queryset):
        for audit in queryset.filter(moderator_decision="pending"):
            audit.moderator_decision = "approved"
            audit.moderator = request.user
            audit.reviewed_at = timezone.now()
            audit.save()
            audit.player.display_name = audit.proposed_name
            audit.player.display_name_status = "approved"
            audit.player.save(update_fields=["display_name", "display_name_status"])
        self.message_user(request, f"Approved {queryset.count()} name(s).")

    @admin.action(description="Reject selected display names")
    def reject_names(self, request, queryset):
        for audit in queryset.filter(moderator_decision="pending"):
            audit.moderator_decision = "rejected"
            audit.moderator = request.user
            audit.reviewed_at = timezone.now()
            audit.save()
            audit.player.display_name_status = "rejected"
            audit.player.save(update_fields=["display_name_status"])
        self.message_user(request, f"Rejected {queryset.count()} name(s).")


# --------------------------------------------------------------------------- #
# Consent + audit logs (read-only in admin)
# --------------------------------------------------------------------------- #

@admin.register(ConsentRecord)
class ConsentRecordAdmin(admin.ModelAdmin):
    list_display = ("action", "parent", "player", "timestamp")
    list_filter = ("action",)
    readonly_fields = ("id", "parent", "player", "action", "ip_address",
                       "user_agent", "timestamp", "notes")

    def has_add_permission(self, *args, **kwargs):
        return False

    def has_change_permission(self, *args, **kwargs):
        return False

    def has_delete_permission(self, *args, **kwargs):
        return False


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("event_type", "actor", "target_player", "timestamp")
    list_filter = ("event_type",)
    readonly_fields = ("event_type", "actor", "target_player", "detail",
                       "ip_address", "timestamp")

    def has_add_permission(self, *args, **kwargs):
        return False

    def has_change_permission(self, *args, **kwargs):
        return False

    def has_delete_permission(self, *args, **kwargs):
        return False
