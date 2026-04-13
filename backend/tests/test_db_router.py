"""Tests for the database router in config/db_router.py."""
from __future__ import annotations

from django.test import SimpleTestCase

from config.db_router import AnalyticsReplicaRouter


class _FakeMeta:
    def __init__(self, app_label: str):
        self.app_label = app_label


class _FakeModel:
    def __init__(self, app_label: str):
        self._meta = _FakeMeta(app_label)


class AnalyticsReplicaRouterTests(SimpleTestCase):
    def setUp(self) -> None:
        self.router = AnalyticsReplicaRouter()

    # --- db_for_read ---------------------------------------------------------

    def test_reads_go_to_replica_for_analytics_models(self):
        model = _FakeModel("analytics")
        self.assertEqual(self.router.db_for_read(model), "replica")

    def test_reads_return_none_for_non_analytics_models(self):
        model = _FakeModel("games")
        self.assertIsNone(self.router.db_for_read(model))

    def test_reads_return_none_for_nasa_ingest(self):
        model = _FakeModel("nasa_ingest")
        self.assertIsNone(self.router.db_for_read(model))

    # --- db_for_write --------------------------------------------------------

    def test_writes_always_go_to_default(self):
        for label in ("analytics", "games", "nasa_ingest", "progress", "users"):
            model = _FakeModel(label)
            self.assertEqual(
                self.router.db_for_write(model), "default",
                f"Expected 'default' for {label}"
            )

    # --- allow_relation ------------------------------------------------------

    def test_relations_allowed(self):
        obj1 = _FakeModel("analytics")
        obj2 = _FakeModel("games")
        self.assertTrue(self.router.allow_relation(obj1, obj2))

    def test_relations_allowed_same_app(self):
        obj1 = _FakeModel("analytics")
        obj2 = _FakeModel("analytics")
        self.assertTrue(self.router.allow_relation(obj1, obj2))

    # --- allow_migrate -------------------------------------------------------

    def test_migrations_allowed_only_on_default(self):
        self.assertTrue(self.router.allow_migrate("default", "analytics"))
        self.assertFalse(self.router.allow_migrate("replica", "analytics"))

    def test_migrations_on_default_for_other_apps(self):
        self.assertTrue(self.router.allow_migrate("default", "games"))
        self.assertFalse(self.router.allow_migrate("replica", "games"))
