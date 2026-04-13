from django.contrib import admin
from .models import (
    Achievement, Attempt, Constellation, PlayerAchievement,
    PlayerStar, PlayerStreak, SkillStar,
)


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "player", "mission", "quiz_correct", "quiz_total",
                    "jigsaw_completed", "xp_earned", "difficulty_level", "created_at")
    list_filter = ("jigsaw_completed", "mission__mission_type", "difficulty_level")
    readonly_fields = ("created_at",)


# --------------------------------------------------------------------------- #
# Knowledge Constellation
# --------------------------------------------------------------------------- #

class SkillStarInline(admin.TabularInline):
    model = SkillStar
    extra = 0
    fields = ("slug", "name", "mission_types", "xp_value", "display_x", "display_y")


@admin.register(Constellation)
class ConstellationAdmin(admin.ModelAdmin):
    list_display = ("name", "topic", "slug", "display_order")
    list_filter = ("topic",)
    inlines = [SkillStarInline]


@admin.register(SkillStar)
class SkillStarAdmin(admin.ModelAdmin):
    list_display = ("name", "constellation", "slug", "xp_value")
    list_filter = ("constellation",)
    filter_horizontal = ("prerequisites",)


@admin.register(PlayerStar)
class PlayerStarAdmin(admin.ModelAdmin):
    list_display = ("player", "star", "earned_at")
    list_filter = ("star__constellation",)
    readonly_fields = ("earned_at",)


# --------------------------------------------------------------------------- #
# Achievements
# --------------------------------------------------------------------------- #

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "xp_bonus")
    search_fields = ("name",)


@admin.register(PlayerAchievement)
class PlayerAchievementAdmin(admin.ModelAdmin):
    list_display = ("player", "achievement", "earned_at")
    readonly_fields = ("earned_at",)


# --------------------------------------------------------------------------- #
# Streaks
# --------------------------------------------------------------------------- #

@admin.register(PlayerStreak)
class PlayerStreakAdmin(admin.ModelAdmin):
    list_display = ("player", "current_streak", "longest_streak", "last_play_date")
    readonly_fields = ("last_play_date",)
