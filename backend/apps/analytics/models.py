"""Analytics storage. Raw events live in a day-partitioned table; dashboards
read materialized views. Both are `managed = False` — created via raw SQL in
migration 0001 so we control partitioning. PLAN §24.3."""
from __future__ import annotations

from django.contrib.postgres.fields import ArrayField
from django.db import models


class RawEvent(models.Model):
    id = models.BigAutoField(primary_key=True)
    event_type = models.CharField(max_length=64)
    player_id = models.UUIDField()
    session_id = models.UUIDField()
    age_group = models.CharField(max_length=8)
    timestamp = models.DateTimeField()
    payload = models.JSONField()

    class Meta:
        managed = False
        db_table = "analytics_rawevent"


class DailyEngagementRollup(models.Model):
    date = models.DateField()
    age_group = models.CharField(max_length=8)
    dau = models.IntegerField()
    sessions = models.IntegerField()
    avg_session_seconds = models.FloatField()
    missions_started = models.IntegerField()
    missions_completed = models.IntegerField()
    quizzes_answered = models.IntegerField()
    quizzes_correct = models.IntegerField()
    new_players = models.IntegerField()
    returning_players = models.IntegerField()

    class Meta:
        managed = False
        db_table = "analytics_daily_engagement"
        unique_together = ("date", "age_group")


class MissionRollup(models.Model):
    date = models.DateField()
    mission_id = models.IntegerField()
    age_group = models.CharField(max_length=8)
    starts = models.IntegerField()
    completions = models.IntegerField()
    abandons = models.IntegerField()
    avg_score = models.FloatField()
    avg_time_seconds = models.FloatField()
    avg_attempts = models.FloatField()
    avg_hints_used = models.FloatField()
    p50_time_seconds = models.FloatField()
    p90_time_seconds = models.FloatField()

    class Meta:
        managed = False
        db_table = "analytics_mission_rollup"
        unique_together = ("date", "mission_id", "age_group")


class QuizQuestionRollup(models.Model):
    date = models.DateField()
    quiz_id = models.IntegerField()
    age_group = models.CharField(max_length=8)
    attempts = models.IntegerField()
    correct_count = models.IntegerField()
    avg_time_to_answer_ms = models.FloatField()
    hint_usage_rate = models.FloatField()

    class Meta:
        managed = False
        db_table = "analytics_quiz_rollup"
        unique_together = ("date", "quiz_id", "age_group")


# --- A/B testing (managed normally — small tables) ----------------------

class Experiment(models.Model):
    STATUS = [("draft", "draft"), ("running", "running"), ("concluded", "concluded")]

    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    traffic_percent = models.PositiveSmallIntegerField(default=10)
    target_age_groups = ArrayField(models.CharField(max_length=8), default=list, blank=True)
    target_new_players_only = models.BooleanField(default=False)
    status = models.CharField(max_length=16, choices=STATUS, default="draft")
    started_at = models.DateTimeField(null=True, blank=True)
    concluded_at = models.DateTimeField(null=True, blank=True)
    winner_variant = models.CharField(max_length=64, blank=True)
    primary_metric = models.CharField(max_length=64)
    minimum_sample = models.PositiveIntegerField(default=500)

    def __str__(self) -> str:
        return self.slug


class ExperimentVariant(models.Model):
    experiment = models.ForeignKey(Experiment, related_name="variants", on_delete=models.CASCADE)
    slug = models.SlugField()
    config = models.JSONField(default=dict)
    sample_size = models.PositiveIntegerField(default=0)
    metric_value = models.FloatField(null=True, blank=True)
    confidence = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ("experiment", "slug")

    def __str__(self) -> str:
        return f"{self.experiment.slug}:{self.slug}"


class PlayerExperiment(models.Model):
    player_id = models.UUIDField()
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    variant = models.ForeignKey(ExperimentVariant, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("player_id", "experiment")
        indexes = [models.Index(fields=["player_id"])]
