"""Validate .env.example has all required variables."""
import unittest
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class EnvExampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        env_path = os.path.join(PROJECT_ROOT, ".env.example")
        cls.vars = {}
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    cls.vars[key.strip()] = val.strip()

    def test_required_vars_present(self):
        required = [
            "NASA_API_KEY",
            "DJANGO_SECRET_KEY",
            "DJANGO_DEBUG",
            "POSTGRES_DB",
            "POSTGRES_USER",
            "POSTGRES_PASSWORD",
            "POSTGRES_HOST",
            "POSTGRES_PORT",
            "REDIS_URL",
            "NEXT_PUBLIC_API_BASE",
        ]
        for var in required:
            self.assertIn(var, self.vars, f"Missing env var: {var}")

    def test_no_production_secrets(self):
        for key, val in self.vars.items():
            self.assertNotIn("sk_live", val, f"{key} contains production secret")
            self.assertNotIn("prod", val.lower(), f"{key} may reference production")

    def test_django_debug_is_on(self):
        self.assertEqual(self.vars.get("DJANGO_DEBUG"), "1")

    def test_postgres_port_is_numeric(self):
        port = self.vars.get("POSTGRES_PORT", "")
        self.assertTrue(port.isdigit(), f"POSTGRES_PORT should be numeric: {port}")


if __name__ == "__main__":
    unittest.main()
