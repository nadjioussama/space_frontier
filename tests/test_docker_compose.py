"""Validate docker-compose.yml structure and consistency."""
import unittest
import yaml
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class DockerComposeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(PROJECT_ROOT, "docker-compose.yml")) as f:
            cls.config = yaml.safe_load(f)

    def test_required_services_exist(self):
        services = set(self.config.get("services", {}).keys())
        for name in ("db", "redis", "web", "worker", "beat", "frontend"):
            self.assertIn(name, services, f"Missing service: {name}")

    def test_db_uses_postgres(self):
        db = self.config["services"]["db"]
        self.assertIn("postgres", db.get("image", ""))

    def test_redis_service(self):
        redis = self.config["services"]["redis"]
        self.assertIn("redis", redis.get("image", ""))

    def test_web_depends_on_db_and_redis(self):
        web = self.config["services"]["web"]
        deps = web.get("depends_on", {})
        if isinstance(deps, list):
            dep_names = deps
        else:
            dep_names = list(deps.keys())
        self.assertIn("db", dep_names)
        self.assertIn("redis", dep_names)

    def test_worker_depends_on_db_and_redis(self):
        worker = self.config["services"]["worker"]
        deps = worker.get("depends_on", {})
        if isinstance(deps, list):
            dep_names = deps
        else:
            dep_names = list(deps.keys())
        self.assertIn("db", dep_names)
        self.assertIn("redis", dep_names)

    def test_frontend_depends_on_web(self):
        frontend = self.config["services"]["frontend"]
        deps = frontend.get("depends_on", {})
        if isinstance(deps, list):
            dep_names = deps
        else:
            dep_names = list(deps.keys())
        self.assertIn("web", dep_names)

    def test_env_file_or_environment_set(self):
        for name, svc in self.config["services"].items():
            has_env = "env_file" in svc or "environment" in svc
            if name not in ("db", "redis"):
                self.assertTrue(has_env, f"Service {name} missing env config")

    def test_db_has_healthcheck(self):
        db = self.config["services"]["db"]
        self.assertIn("healthcheck", db)

    def test_redis_has_healthcheck(self):
        redis = self.config["services"]["redis"]
        self.assertIn("healthcheck", redis)

    def test_web_port_8000(self):
        web = self.config["services"]["web"]
        ports = web.get("ports", [])
        has_8000 = any("8000" in str(p) for p in ports)
        cmd = web.get("command", "")
        has_8000_in_cmd = "8000" in str(cmd)
        self.assertTrue(has_8000 or has_8000_in_cmd,
                        "Web service should expose or use port 8000")

    def test_frontend_port_3000(self):
        frontend = self.config["services"]["frontend"]
        ports = frontend.get("ports", [])
        has_3000 = any("3000" in str(p) for p in ports)
        cmd = frontend.get("command", "")
        has_3000_in_cmd = "3000" in str(cmd)
        self.assertTrue(has_3000 or has_3000_in_cmd,
                        "Frontend service should expose or use port 3000")

    def test_no_privileged_containers(self):
        for name, svc in self.config["services"].items():
            self.assertFalse(svc.get("privileged", False),
                             f"Service {name} should not be privileged")

    def test_volumes_defined(self):
        self.assertIn("volumes", self.config)


if __name__ == "__main__":
    unittest.main()
