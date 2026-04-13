"""Validate GitHub Actions workflow files are well-formed."""
import os
import unittest
import yaml

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOWS_DIR = os.path.join(PROJECT_ROOT, ".github", "workflows")


class CIWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(WORKFLOWS_DIR, "ci.yml")) as f:
            cls.ci = yaml.safe_load(f)

    def test_valid_yaml(self):
        self.assertIsInstance(self.ci, dict)

    def test_has_name(self):
        self.assertIn("name", self.ci)

    def test_has_on_trigger(self):
        self.assertIn("on", self.ci)

    def test_triggers_on_pull_request(self):
        triggers = self.ci["on"]
        self.assertTrue(
            "pull_request" in triggers or
            isinstance(triggers, list) and "pull_request" in triggers
        )

    def test_has_backend_job(self):
        self.assertIn("backend", self.ci["jobs"])

    def test_has_frontend_job(self):
        self.assertIn("frontend", self.ci["jobs"])

    def test_has_terraform_job(self):
        self.assertIn("terraform-plan", self.ci["jobs"])

    def test_backend_uses_postgres_service(self):
        backend = self.ci["jobs"]["backend"]
        services = backend.get("services", {})
        self.assertIn("postgres", services)

    def test_backend_uses_redis_service(self):
        backend = self.ci["jobs"]["backend"]
        services = backend.get("services", {})
        self.assertIn("redis", services)

    def test_backend_runs_pytest(self):
        backend = self.ci["jobs"]["backend"]
        steps = backend.get("steps", [])
        has_pytest = any("pytest" in str(s.get("run", "")) for s in steps)
        self.assertTrue(has_pytest, "Backend job should run pytest")

    def test_frontend_runs_lint(self):
        frontend = self.ci["jobs"]["frontend"]
        steps = frontend.get("steps", [])
        has_lint = any("lint" in str(s.get("run", "")) for s in steps)
        self.assertTrue(has_lint, "Frontend job should run lint")

    def test_terraform_validates(self):
        tf = self.ci["jobs"]["terraform-plan"]
        steps = tf.get("steps", [])
        has_validate = any("terraform" in str(s.get("run", "")).lower() for s in steps)
        self.assertTrue(has_validate)


class DeployWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(WORKFLOWS_DIR, "deploy.yml")) as f:
            cls.deploy = yaml.safe_load(f)

    def test_valid_yaml(self):
        self.assertIsInstance(self.deploy, dict)

    def test_has_name(self):
        self.assertIn("name", self.deploy)

    def test_has_jobs(self):
        self.assertIn("jobs", self.deploy)
        self.assertTrue(len(self.deploy["jobs"]) > 0)

    def test_deploy_has_health_check(self):
        """Deploy workflow should include a health check / integration test."""
        content = yaml.dump(self.deploy)
        self.assertTrue(
            "health" in content.lower() or "curl" in content.lower(),
            "Deploy workflow should include health check"
        )


if __name__ == "__main__":
    unittest.main()
