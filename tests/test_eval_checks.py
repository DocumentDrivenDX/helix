"""Regression tests for deterministic evaluation output checks."""
import importlib.util
from pathlib import Path
import unittest

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


if __name__ == "__main__":
    unittest.main()
