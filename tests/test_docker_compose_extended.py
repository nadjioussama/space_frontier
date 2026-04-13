"""Extended docker-compose validation — volumes, build contexts, networking."""
import os
import unittest
import yaml

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class DockerComposeExtendedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(PROJECT_ROOT, "docker-compose.yml")) as f:
            cls.config = yaml.safe_load(f)
        cls.services = cls.config.get("services", {})

    # --- Volume tests ---

    def test_pgdata_volume_defined(self):
        volumes = self.config.get("volumes", {})
        self.assertIn("pgdata", volumes)

    def test_media_volume_defined(self):
        volumes = self.config.get("volumes", {})
        self.assertIn("media", volumes)

    def test_db_uses_pgdata_volume(self):
        db = self.services["db"]
        vol_strs = [str(v) for v in db.get("volumes", [])]
        has_pgdata = any("pgdata" in v for v in vol_strs)
        self.assertTrue(has_pgdata, "DB should mount pgdata volume")

    def test_web_mounts_media_volume(self):
        web = self.services["web"]
        vol_strs = [str(v) for v in web.get("volumes", [])]
        has_media = any("media" in v for v in vol_strs)
        self.assertTrue(has_media, "Web should mount media volume")

    def test_worker_shares_media_with_web(self):
        worker = self.services["worker"]
        vol_strs = [str(v) for v in worker.get("volumes", [])]
        has_media = any("media" in v for v in vol_strs)
        self.assertTrue(has_media, "Worker should share media volume with web")

    # --- Build context tests ---

    def test_web_builds_from_backend(self):
        web = self.services["web"]
        build = web.get("build", "")
        self.assertIn("backend", str(build))

    def test_frontend_builds_from_frontend_dir(self):
        frontend = self.services["frontend"]
        build = frontend.get("build", "")
        self.assertIn("frontend", str(build))

    def test_worker_builds_from_backend(self):
        worker = self.services["worker"]
        build = worker.get("build", "")
        self.assertIn("backend", str(build))

    # --- Command tests ---

    def test_worker_runs_celery(self):
        worker = self.services["worker"]
        cmd = worker.get("command", "")
        self.assertIn("celery", str(cmd))

    def test_beat_runs_celery_beat(self):
        beat = self.services["beat"]
        cmd = beat.get("command", "")
        self.assertIn("celery", str(cmd))
        self.assertIn("beat", str(cmd))

    def test_frontend_runs_npm(self):
        frontend = self.services["frontend"]
        cmd = frontend.get("command", "")
        self.assertIn("npm", str(cmd))

    # --- Healthcheck dependency conditions ---

    def test_web_waits_for_healthy_db(self):
        web = self.services["web"]
        deps = web.get("depends_on", {})
        if isinstance(deps, dict):
            db_dep = deps.get("db", {})
            self.assertEqual(db_dep.get("condition"), "service_healthy")

    def test_web_waits_for_healthy_redis(self):
        web = self.services["web"]
        deps = web.get("depends_on", {})
        if isinstance(deps, dict):
            redis_dep = deps.get("redis", {})
            self.assertEqual(redis_dep.get("condition"), "service_healthy")

    # --- Environment tests ---

    def test_frontend_overrides_api_base(self):
        frontend = self.services["frontend"]
        env = frontend.get("environment", {})
        if isinstance(env, dict):
            self.assertIn("NEXT_PUBLIC_API_BASE", env)
        elif isinstance(env, list):
            has_api_base = any("NEXT_PUBLIC_API_BASE" in str(e) for e in env)
            self.assertTrue(has_api_base)

    # --- No duplicate port bindings ---

    def test_no_duplicate_host_ports(self):
        all_ports = []
        for name, svc in self.services.items():
            for p in svc.get("ports", []):
                host_port = str(p).split(":")[0]
                all_ports.append((host_port, name))
        host_ports = [hp for hp, _ in all_ports]
        self.assertEqual(len(host_ports), len(set(host_ports)),
                         f"Duplicate host ports: {all_ports}")


if __name__ == "__main__":
    unittest.main()
