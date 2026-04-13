"""Create the partitioned raw-event table + materialized rollup views, plus the
managed A/B-testing tables. PLAN §24.3."""
from django.contrib.postgres.fields import ArrayField
from django.db import migrations, models
import django.db.models.deletion

RAW_EVENT_SQL = """
CREATE TABLE analytics_rawevent (
    id          bigserial,
    event_type  varchar(64)  NOT NULL,
    player_id   uuid         NOT NULL,
    session_id  uuid         NOT NULL,
    age_group   varchar(8)   NOT NULL,
    "timestamp" timestamptz  NOT NULL,
    payload     jsonb        NOT NULL,
    PRIMARY KEY (id, "timestamp")
) PARTITION BY RANGE ("timestamp");

CREATE INDEX analytics_rawevent_type_ts ON analytics_rawevent (event_type, "timestamp");
CREATE INDEX analytics_rawevent_age_type_ts ON analytics_rawevent (age_group, event_type, "timestamp");
CREATE INDEX analytics_rawevent_player ON analytics_rawevent (player_id);
"""

ROLLUP_SQL = """
CREATE MATERIALIZED VIEW analytics_daily_engagement AS
SELECT
    row_number() OVER ()                                  AS id,
    date_trunc('day', "timestamp")::date                  AS date,
    age_group,
    COUNT(DISTINCT player_id)                             AS dau,
    COUNT(DISTINCT session_id)                            AS sessions,
    COALESCE(AVG((payload->>'duration_seconds')::float)
             FILTER (WHERE event_type = 'session.ended'), 0)        AS avg_session_seconds,
    COUNT(*) FILTER (WHERE event_type = 'mission.started')          AS missions_started,
    COUNT(*) FILTER (WHERE event_type = 'mission.completed')        AS missions_completed,
    COUNT(*) FILTER (WHERE event_type = 'quiz.answered')            AS quizzes_answered,
    COUNT(*) FILTER (WHERE event_type = 'quiz.answered'
                     AND (payload->>'is_correct')::boolean)         AS quizzes_correct,
    COUNT(DISTINCT player_id) FILTER (WHERE event_type = 'session.started'
                     AND NOT (payload->>'is_returning')::boolean)   AS new_players,
    COUNT(DISTINCT player_id) FILTER (WHERE event_type = 'session.started'
                     AND (payload->>'is_returning')::boolean)       AS returning_players
FROM analytics_rawevent
GROUP BY 2, 3;
CREATE UNIQUE INDEX ON analytics_daily_engagement (date, age_group);

CREATE MATERIALIZED VIEW analytics_mission_rollup AS
SELECT
    row_number() OVER ()                                  AS id,
    date_trunc('day', "timestamp")::date                  AS date,
    (payload->>'mission_id')::int                         AS mission_id,
    age_group,
    COUNT(*) FILTER (WHERE event_type = 'mission.started')                              AS starts,
    COUNT(*) FILTER (WHERE event_type = 'mission.completed')                            AS completions,
    COUNT(*) FILTER (WHERE event_type = 'mission.abandoned')                            AS abandons,
    AVG((payload->>'score')::float)        FILTER (WHERE event_type = 'mission.completed') AS avg_score,
    AVG((payload->>'time_seconds')::float) FILTER (WHERE event_type = 'mission.completed') AS avg_time_seconds,
    AVG((payload->>'attempts')::float)     FILTER (WHERE event_type = 'mission.completed') AS avg_attempts,
    AVG((payload->>'hints_used')::float)   FILTER (WHERE event_type = 'mission.completed') AS avg_hints_used,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY (payload->>'time_seconds')::float)
        FILTER (WHERE event_type = 'mission.completed')                                 AS p50_time_seconds,
    percentile_cont(0.9) WITHIN GROUP (ORDER BY (payload->>'time_seconds')::float)
        FILTER (WHERE event_type = 'mission.completed')                                 AS p90_time_seconds
FROM analytics_rawevent
WHERE event_type IN ('mission.started', 'mission.completed', 'mission.abandoned')
GROUP BY 2, 3, 4;
CREATE UNIQUE INDEX ON analytics_mission_rollup (date, mission_id, age_group);

CREATE MATERIALIZED VIEW analytics_quiz_rollup AS
SELECT
    row_number() OVER ()                                  AS id,
    date_trunc('day', "timestamp")::date                  AS date,
    (payload->>'quiz_id')::int                            AS quiz_id,
    age_group,
    COUNT(*)                                              AS attempts,
    COUNT(*) FILTER (WHERE (payload->>'is_correct')::boolean)                  AS correct_count,
    AVG((payload->>'time_to_answer_ms')::float)                                AS avg_time_to_answer_ms,
    AVG(CASE WHEN COALESCE((payload->>'hint_tier_used')::int, 0) > 0
             THEN 1.0 ELSE 0.0 END)                                            AS hint_usage_rate
FROM analytics_rawevent
WHERE event_type = 'quiz.answered'
GROUP BY 2, 3, 4;
CREATE UNIQUE INDEX ON analytics_quiz_rollup (date, quiz_id, age_group);
"""


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.RunSQL(RAW_EVENT_SQL, reverse_sql="DROP TABLE IF EXISTS analytics_rawevent CASCADE;"),
        migrations.RunSQL(
            ROLLUP_SQL,
            reverse_sql=(
                "DROP MATERIALIZED VIEW IF EXISTS analytics_quiz_rollup;"
                "DROP MATERIALIZED VIEW IF EXISTS analytics_mission_rollup;"
                "DROP MATERIALIZED VIEW IF EXISTS analytics_daily_engagement;"
            ),
        ),
        migrations.CreateModel(
            name="Experiment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("slug", models.SlugField(unique=True)),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("traffic_percent", models.PositiveSmallIntegerField(default=10)),
                ("target_age_groups", ArrayField(base_field=models.CharField(max_length=8), default=list, blank=True, size=None)),
                ("target_new_players_only", models.BooleanField(default=False)),
                ("status", models.CharField(max_length=16, choices=[("draft", "draft"), ("running", "running"), ("concluded", "concluded")], default="draft")),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("concluded_at", models.DateTimeField(blank=True, null=True)),
                ("winner_variant", models.CharField(blank=True, max_length=64)),
                ("primary_metric", models.CharField(max_length=64)),
                ("minimum_sample", models.PositiveIntegerField(default=500)),
            ],
        ),
        migrations.CreateModel(
            name="ExperimentVariant",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("slug", models.SlugField()),
                ("config", models.JSONField(default=dict)),
                ("sample_size", models.PositiveIntegerField(default=0)),
                ("metric_value", models.FloatField(blank=True, null=True)),
                ("confidence", models.FloatField(blank=True, null=True)),
                ("experiment", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="variants", to="analytics.experiment")),
            ],
            options={"unique_together": {("experiment", "slug")}},
        ),
        migrations.CreateModel(
            name="PlayerExperiment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("player_id", models.UUIDField()),
                ("assigned_at", models.DateTimeField(auto_now_add=True)),
                ("experiment", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="analytics.experiment")),
                ("variant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="analytics.experimentvariant")),
            ],
            options={
                "unique_together": {("player_id", "experiment")},
                "indexes": [models.Index(fields=["player_id"], name="analytics_pe_player_idx")],
            },
        ),
    ]
