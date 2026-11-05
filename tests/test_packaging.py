from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PackagingMetadataTests(unittest.TestCase):
    def test_pyproject_exposes_stdlib_cli(self):
        text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('name = "memory-applicability-guard"', text)
        self.assertIn('version = "1.0.0"', text)
        self.assertIn('requires-python = ">=3.10"', text)
        self.assertIn('memory-applicability-guard = "memory_applicability_guard:main"', text)
        self.assertIn('where = ["src"]', text)
        self.assertNotIn("jsonschema", text)
        self.assertNotIn("requests", text)

    def test_wrapper_loads_skill_helper(self):
        src = str(ROOT / "src")
        if src not in sys.path:
            sys.path.insert(0, src)
        import memory_applicability_guard as mag

        from test_guard_decision import case

        self.assertEqual(mag.__version__, "1.0.0")
        self.assertEqual(mag.decide(case())["reason_code"], "DIRECT")


if __name__ == "__main__":
    unittest.main()
