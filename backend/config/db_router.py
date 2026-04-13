"""Route read-only analytics queries to the RDS read replica. PLAN §11.6."""


class AnalyticsReplicaRouter:
    analytics_apps = {"analytics"}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.analytics_apps:
            return "replica"
        return None

    def db_for_write(self, model, **hints):
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # All migrations run on primary only.
        return db == "default"
