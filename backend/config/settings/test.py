"""Test settings. Isolates Redis to DB 1 and disables migrations so the test
runner builds the schema directly from models (most apps have no committed
migrations — see README quick-start step 3)."""
import os

# Default to localhost so `pytest` works outside docker-compose too.
os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/1")

from .base import *  # noqa: E402,F401,F403

DEBUG = False

# --- DB: build schema from models, skip migrations -----------------------
class _DisableMigrations:
    def __contains__(self, item): return True
    def __getitem__(self, item): return None


MIGRATION_MODULES = _DisableMigrations()

# --- Redis: separate logical DB so tests don't clobber dev data ----------
_TEST_REDIS = os.environ.get("REDIS_URL", "redis://localhost:6379/1")
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": _TEST_REDIS,
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
}
REDIS_URL = _TEST_REDIS

# --- Celery: never hit a broker in tests --------------------------------
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Faster password hashing for user fixtures
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
