from django.contrib import admin

from .models import (
    DailyEngagementRollup, Experiment, ExperimentVariant, MissionRollup,
    PlayerExperiment, QuizQuestionRollup,
)


class VariantInline(admin.TabularInline):
    model = ExperimentVariant
    extra = 1
    readonly_fields = ("sample_size", "metric_value", "confidence")


@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    list_display = ("slug", "status", "primary_metric", "traffic_percent", "started_at", "winner_variant")
    list_filter = ("status",)
    inlines = [VariantInline]
    actions = ["score_now"]

    @admin.action(description="Recompute variant metrics")
    def score_now(self, request, queryset):
        from .ab_testing import score_experiment
        for exp in queryset:
            score_experiment(exp)


@admin.register(PlayerExperiment)
class PlayerExperimentAdmin(admin.ModelAdmin):
    list_display = ("player_id", "experiment", "variant", "assigned_at")
    list_filter = ("experiment",)


@admin.register(DailyEngagementRollup)
class DailyEngagementAdmin(admin.ModelAdmin):
    list_display = ("date", "age_group", "dau", "sessions", "avg_session_seconds",
                    "missions_started", "missions_completed")
    list_filter = ("age_group",)
    date_hierarchy = "date"

    def has_add_permission(self, request):    return False
    def has_change_permission(self, *a, **k): return False
    def has_delete_permission(self, *a, **k): return False


@admin.register(MissionRollup)
class MissionRollupAdmin(admin.ModelAdmin):
    list_display = ("date", "mission_id", "age_group", "starts", "completions",
                    "abandons", "avg_score", "p50_time_seconds")
    list_filter = ("age_group",)
    date_hierarchy = "date"

    def has_add_permission(self, request):    return False
    def has_change_permission(self, *a, **k): return False
    def has_delete_permission(self, *a, **k): return False


@admin.register(QuizQuestionRollup)
class QuizRollupAdmin(admin.ModelAdmin):
    list_display = ("date", "quiz_id", "age_group", "attempts", "correct_count",
                    "avg_time_to_answer_ms", "hint_usage_rate")
    list_filter = ("age_group",)
    date_hierarchy = "date"

    def has_add_permission(self, request):    return False
    def has_change_permission(self, *a, **k): return False
    def has_delete_permission(self, *a, **k): return False
