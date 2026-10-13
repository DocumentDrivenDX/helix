"""Regression tests for deterministic evaluation output checks."""
import importlib.util
from pathlib import Path
import unittest
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("run_eval", ROOT / "scripts/run-eval.py")
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


class OutputChecksTests(unittest.TestCase):
    def check(self, forbidden, output):
        brief = {"checks": [{"kind": "output_not_contains", "values": [forbidden]}]}
        return runner.run_checks(brief, ROOT, {}, {}, output, {})[0]

    def test_yaml_report_headers_are_rejected(self):
        for output in (
            "helix_report:\n  mode: review\n",
            "```yaml\nhelix_report:\n  mode: review\n```",
            "HELIX_REPORT: {}",
            "helix_report:",
        ):
            with self.subTest(output=output):
                self.assertFalse(self.check("helix_report:", output)["ok"])

    def test_conversational_output_passes(self):
        self.assertTrue(self.check("helix_report:", "No findings.")["ok"])

    def test_word_checks_keep_token_boundaries(self):
        self.assertFalse(self.check("bead", "Create a bead.")["ok"])
        self.assertTrue(self.check("bead", "A beaded bracelet.")["ok"])


class SessionChecksTests(unittest.TestCase):
    def test_file_contains_requires_file_and_every_value(self):
        with tempfile.TemporaryDirectory() as td:
            ws = Path(td)
            brief = {"checks": [{"kind": "file_contains", "path": "proof.md", "values": ["120", "reject"]}]}
            check = lambda: runner.run_checks(brief, ws, {}, {}, "", {})[0]["ok"]
            self.assertFalse(check())
            (ws / "proof.md").write_text("120")
            self.assertFalse(check())
            (ws / "proof.md").write_text("reject 120")
            self.assertTrue(check())

    def test_overlay_preserves_low_autonomy_marker(self):
        with tempfile.TemporaryDirectory() as td, patch.object(runner.subprocess, "run"):
            ws = runner.make_workspace("session-low-autonomy", Path(td))
            self.assertIn("level: low", (ws / ".helix.yml").read_text())
            self.assertTrue((ws / "docs/helix/01-frame/prd.md").is_file())

    def test_unknown_overlay_and_traversal_are_rejected(self):
        for fixture in ("session-missing", "session-../../outside"):
            with self.subTest(fixture=fixture), tempfile.TemporaryDirectory() as td:
                with self.assertRaises(SystemExit):
                    runner.make_workspace(fixture, Path(td))

if __name__ == "__main__":
    unittest.main()
