"""Progress tracking. PLAN §8.2.

Phase 1 stores the bare minimum — per-player XP + per-mission attempt rows.
Phase 5 adds: Knowledge Constellation (skill tree), achievements, streaks,
DDA difficulty persistence, and leaderboard snapshots.

Anonymous play is first-class (no login wall, PLAN §3.2). We still need a
place to persist per-mission results; the frontend holds the identity in
IndexedDB and passes nothing to the backend in Phase 1+2 — so we use a
synthetic anon_id when the player is not authenticated.
"""
from django.conf import settings
from django.db import models

from apps.games.models import Mission


class Attempt(models.Model):
    player = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=True, blank=True, related_name="attempts",
    )
    anon_id = models.CharField(max_length=64, blank=True, db_index=True)
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name="attempts")
    quiz_correct = models.IntegerField(default=0)
    quiz_total = models.IntegerField(default=0)
    jigsaw_completed = models.BooleanField(default=False)
    xp_earned = models.IntegerField(default=0)
    difficulty_level = models.IntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["player", "-created_at"]),
            models.Index(fields=["anon_id", "-created_at"]),
        ]


# --------------------------------------------------------------------------- #
# Knowledge Constellation — skill tree (Phase 5, PLAN §3.4)
# --------------------------------------------------------------------------- #

TOPIC_CHOICES = [
    ("astronomy", "Astronomy"),
    ("physics", "Physics"),
    ("geology", "Geology"),
    ("biology", "Astrobiology"),
    ("engineering", "Space Engineering"),
    ("earth_science", "Earth Science"),
    ("planetary_defense", "Planetary Defense"),
    ("exoplanets", "Exoplanets"),
]


class Constellation(models.Model):
    """A topic cluster in the skill tree. Each constellation groups related SkillStars."""
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    topic = models.CharField(max_length=32, choices=TOPIC_CHOICES)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=32, default="star")
    display_order = models.IntegerField(default=0)

    class Meta:
        ordering = ("display_order", "name")

    def __str__(self) -> str:
        return self.name


class SkillStar(models.Model):
    """A single concept node inside a constellation. Earning it means the
    player demonstrated understanding of one specific concept."""
    constellation = models.ForeignKey(Constellation, on_delete=models.CASCADE, related_name="stars")
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    # Connections to other stars (visual lines in the constellation map)
    prerequisites = models.ManyToManyField("self", symmetrical=False, blank=True, related_name="unlocks")
    # Which mission types can earn this star
    mission_types = models.JSONField(default=list, blank=True)
    xp_value = models.IntegerField(default=25)
    display_x = models.FloatField(default=50.0)
    display_y = models.FloatField(default=50.0)

    class Meta:
        ordering = ("constellation", "name")

    def __str__(self) -> str:
        return f"{self.constellation.name} > {self.name}"


class PlayerStar(models.Model):
    """Tracks which stars a player has earned."""
    player = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="earned_stars",
    )
    star = models.ForeignKey(SkillStar, on_delete=models.CASCADE, related_name="earners")
    earned_at = models.DateTimeField(auto_now_add=True)
    earned_in_attempt = models.ForeignKey(
        Attempt, on_delete=models.SET_NULL, null=True, blank=True,
    )

    class Meta:
        unique_together = [("player", "star")]
        ordering = ("-earned_at",)


# --------------------------------------------------------------------------- #
# Achievements / badges (Phase 5, PLAN §3.4)
# --------------------------------------------------------------------------- #

class Achievement(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=64, default="badge")
    # Criteria encoded as JSON — evaluated by the achievement checker service
    criteria = models.JSONField(default=dict)
    xp_bonus = models.IntegerField(default=50)

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class PlayerAchievement(models.Model):
    player = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="achievements",
    )
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name="earners")
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("player", "achievement")]
        ordering = ("-earned_at",)


# --------------------------------------------------------------------------- #
# Streak tracking (Phase 5, PLAN §3.3)
# --------------------------------------------------------------------------- #

class PlayerStreak(models.Model):
    """Tracks daily play streaks for engagement. PLAN §3.3 fixed interval."""
    player = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="streak",
    )
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_play_date = models.DateField(null=True, blank=True)

    def __str__(self) -> str:
        return f"Player {self.player_id}: {self.current_streak}d streak"
