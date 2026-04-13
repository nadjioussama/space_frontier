"""Validate Dockerfile best practices and structure."""
import os
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class BackendDockerfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = os.path.join(PROJECT_ROOT, "backend", "Dockerfile")
        with open(path) as f:
            cls.content = f.read()
            cls.lines = cls.content.strip().splitlines()

    def test_starts_with_from(self):
        self.assertTrue(self.lines[0].startswith("FROM"))

    def test_uses_python_image(self):
        self.assertIn("python", self.lines[0].lower())

    def test_sets_workdir(self):
        self.assertIn("WORKDIR", self.content)

    def test_copies_requirements_before_code(self):
        """Requirements should be copied before the full app for layer caching."""
        req_idx = next(
            (i for i, l in enumerate(self.lines) if "requirements.txt" in l and "COPY" in l),
            None,
        )
        app_idx = next(
            (i for i, l in enumerate(self.lines) if l.strip() == "COPY . ."),
            None,
        )
        self.assertIsNotNone(req_idx, "Should COPY requirements.txt")
        self.assertIsNotNone(app_idx, "Should COPY . .")
        self.assertLess(req_idx, app_idx, "requirements.txt should be copied before app code")

    def test_exposes_port_8000(self):
        self.assertIn("EXPOSE 8000", self.content)

    def test_has_cmd(self):
        self.assertTrue(any("CMD" in l for l in self.lines))

    def test_disables_bytecode(self):
        self.assertIn("PYTHONDONTWRITEBYTECODE", self.content)

    def test_unbuffered_output(self):
        self.assertIn("PYTHONUNBUFFERED", self.content)

    def test_no_pip_cache(self):
        self.assertIn("PIP_NO_CACHE_DIR", self.content)

    def test_apt_lists_cleaned(self):
        self.assertIn("rm -rf /var/lib/apt/lists", self.content)


class FrontendDockerfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = os.path.join(PROJECT_ROOT, "frontend", "Dockerfile")
        with open(path) as f:
            cls.content = f.read()
            cls.lines = cls.content.strip().splitlines()

    def test_starts_with_from(self):
        self.assertTrue(self.lines[0].startswith("FROM"))

    def test_uses_node_image(self):
        self.assertIn("node", self.lines[0].lower())

    def test_sets_workdir(self):
        self.assertIn("WORKDIR", self.content)

    def test_copies_package_json_before_code(self):
        pkg_idx = next(
            (i for i, l in enumerate(self.lines) if "package.json" in l and "COPY" in l),
            None,
        )
        app_idx = next(
            (i for i, l in enumerate(self.lines) if l.strip() == "COPY . ."),
            None,
        )
        self.assertIsNotNone(pkg_idx)
        self.assertIsNotNone(app_idx)
        self.assertLess(pkg_idx, app_idx)

    def test_exposes_port_3000(self):
        self.assertIn("EXPOSE 3000", self.content)

    def test_has_cmd(self):
        self.assertTrue(any("CMD" in l for l in self.lines))


if __name__ == "__main__":
    unittest.main()
