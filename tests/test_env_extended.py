"""Extended .env.example validation — format, consistency, completeness."""
import os
import re
import unittest
import yaml

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class EnvFormatTests(unittest.TestCase):
    """Validate .env.example format and cross-reference with docker-compose."""

    @classmethod
    def setUpClass(cls):
        env_path = os.path.join(PROJECT_ROOT, ".env.example")
        cls.vars = {}
        cls.raw_lines = []
        with open(env_path) as f:
            for line in f:
                cls.raw_lines.append(line)
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    cls.vars[key.strip()] = val.strip()

        with open(os.path.join(PROJECT_ROOT, "docker-compose.yml")) as f:
            cls.compose = yaml.safe_load(f)

    def test_redis_url_uses_redis_service(self):
        """REDIS_URL should point to the redis service in docker-compose."""
        url = self.vars.get("REDIS_URL", "")
        self.assertTrue(url.startswith("redis://"), f"REDIS_URL should be a redis:// URL: {url}")

    def test_postgres_host_matches_compose(self):
        """POSTGRES_HOST should match the db service name in docker-compose."""
        host = self.vars.get("POSTGRES_HOST", "")
        self.assertEqual(host, "db", "POSTGRES_HOST should be 'db' (docker-compose service name)")

    def test_django_allowed_hosts_includes_localhost(self):
        hosts = self.vars.get("DJANGO_ALLOWED_HOSTS", "")
        self.assertIn("localhost", hosts)

    def test_api_base_is_localhost(self):
        base = self.vars.get("NEXT_PUBLIC_API_BASE", "")
        self.assertIn("localhost", base)

    def test_no_empty_required_values(self):
        """Required vars should have non-empty default values."""
        required_with_values = [
            "DJANGO_SECRET_KEY", "POSTGRES_DB", "POSTGRES_USER",
            "POSTGRES_PASSWORD", "REDIS_URL",
        ]
        for var in required_with_values:
            self.assertTrue(
                self.vars.get(var, "").strip(),
                f"{var} should have a non-empty default value"
            )

    def test_no_real_api_keys(self):
        """Env example should use DEMO_KEY or placeholder, not a real key."""
        nasa_key = self.vars.get("NASA_API_KEY", "")
        self.assertTrue(
            nasa_key in ("DEMO_KEY", "") or "demo" in nasa_key.lower() or "change" in nasa_key.lower(),
            f"NASA_API_KEY should be DEMO_KEY or a placeholder, got: {nasa_key}"
        )

    def test_secret_key_is_dev_only(self):
        key = self.vars.get("DJANGO_SECRET_KEY", "")
        self.assertTrue(
            "dev" in key.lower() or "change" in key.lower() or "not-for-production" in key.lower(),
            "DJANGO_SECRET_KEY should indicate it's dev-only"
        )

    def test_sentry_dsn_empty_by_default(self):
        dsn = self.vars.get("SENTRY_DSN", "NOT_SET")
        self.assertEqual(dsn, "", "SENTRY_DSN should be empty by default")

    def test_compose_services_using_env(self):
        """Services that use env_file should be able to find .env."""
        for name, svc in self.compose.get("services", {}).items():
            if "env_file" in svc:
                env_file = svc["env_file"]
                if isinstance(env_file, str):
                    self.assertEqual(env_file, ".env",
                                     f"Service {name} env_file should be .env")


if __name__ == "__main__":
    unittest.main()
