"""Celery app + Beat schedule. Matches PLAN §7.3 (APOD only in walking skeleton)."""
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

app = Celery("nse")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    # Phase 1
    "apod-daily": {
        "task": "apps.nasa_ingest.tasks.ingest_apod",
        "schedule": crontab(hour=5, minute=0),       # 05:00 UTC
    },
    # Phase 4
    "mars-daily": {
        "task": "apps.nasa_ingest.tasks.ingest_mars",
        "schedule": crontab(hour=6, minute=0),       # 06:00 UTC
    },
    "neows-hourly": {
        "task": "apps.nasa_ingest.tasks.ingest_neows",
        "schedule": crontab(minute=0),               # top of every hour
    },
    "epic-6hourly": {
        "task": "apps.nasa_ingest.tasks.ingest_epic",
        "schedule": crontab(hour="*/6", minute=15),  # every 6h at :15
    },
    "exoplanet-weekly": {
        "task": "apps.nasa_ingest.tasks.ingest_exoplanets",
        "schedule": crontab(day_of_week=1, hour=3),  # Monday 03:00 UTC
    },
    # Phase 5
    "leaderboard-weekly-reset": {
        "task": "apps.progress.tasks.reset_weekly_leaderboard",
        "schedule": crontab(day_of_week=1, hour=0, minute=0),  # Monday 00:00 UTC
    },
    "cross-api-missions-weekly": {
        "task": "apps.progress.tasks.generate_cross_api_missions",
        "schedule": crontab(day_of_week=1, hour=4, minute=0),  # Monday 04:00 UTC
    },
    # Phase 7 — ops
    "warm-caches": {
        "task": "apps.analytics.tasks.warm_caches",
        "schedule": crontab(minute="*/30"),
    },
    # Phase 8 — analytics pipeline
    "analytics-drain": {
        "task": "apps.analytics.tasks.drain_event_stream",
        "schedule": crontab(minute="*"),               # every minute
        "options": {"queue": "analytics"},
    },
    "analytics-rollups": {
        "task": "apps.analytics.tasks.refresh_rollups",
        "schedule": crontab(minute="*/15"),
        "options": {"queue": "analytics"},
    },
    "analytics-partitions": {
        "task": "apps.analytics.tasks.manage_partitions",
        "schedule": crontab(hour=1, minute=0),         # nightly
        "options": {"queue": "analytics"},
    },
    "analytics-anomaly": {
        "task": "apps.analytics.tasks.run_anomaly_checks",
        "schedule": crontab(minute="5,20,35,50"),      # offset from rollup refresh
        "options": {"queue": "analytics"},
    },
    "analytics-score-experiments": {
        "task": "apps.analytics.tasks.score_running_experiments",
        "schedule": crontab(hour=2, minute=0),         # nightly
        "options": {"queue": "analytics"},
    },
}

app.conf.task_routes = {"apps.analytics.tasks.*": {"queue": "analytics"}}
