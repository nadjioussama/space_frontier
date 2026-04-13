"""Production settings — ECS Fargate behind ALB/CloudFront/Cloudflare. PLAN §11."""
import os
from .base import *  # noqa: F401,F403

DEBUG = False

# Behind ALB + 2 CDN tiers — trust X-Forwarded-* from the LB only.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# --- Database: primary via PgBouncer sidecar, replica direct for analytics ---
DATABASES["default"]["CONN_MAX_AGE"] = 0  # noqa: F405 — PgBouncer transaction mode
_replica = os.environ.get("POSTGRES_REPLICA_HOST")
if _replica:
    DATABASES["replica"] = {  # noqa: F405
        **DATABASES["default"],  # noqa: F405
        "HOST": _replica,
        "PORT": "5432",  # replica is hit directly (analytics only), not via PgBouncer
    }
    DATABASE_ROUTERS = ["config.db_router.AnalyticsReplicaRouter"]

# --- Static/media on S3 via django-storages -----------------------------
INSTALLED_APPS += ["storages"]  # noqa: F405
AWS_STORAGE_BUCKET_NAME = os.environ.get("MEDIA_BUCKET")
AWS_S3_REGION_NAME = os.environ.get("AWS_REGION", "us-east-1")
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "public, max-age=31536000, immutable"}
AWS_QUERYSTRING_AUTH = False
STORAGES = {
    "default": {"BACKEND": "storages.backends.s3.S3Storage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

# --- CORS: same-origin in prod (CDN fronts everything) ------------------
CORS_ALLOWED_ORIGINS = [f"https://{h}" for h in ALLOWED_HOSTS if h not in ("*",)]  # noqa: F405

# --- Logging: JSON to stdout -> CloudWatch ------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "format": '{"ts":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","msg":"%(message)s"}',
        },
    },
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "json"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}

# Analytics tuning
ANALYTICS_STREAM_KEY = "nse:analytics:events"
ANALYTICS_RAW_RETENTION_DAYS = 90
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "")
