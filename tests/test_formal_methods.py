"""Real concern propagation and executable finite-model negative controls."""
import importlib.util
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import refresh_context_digests as digests

MODEL = ROOT / "workflows/references/formal-methods/lease_model.py"
spec = importlib.util.spec_from_file_location("lease_model", MODEL)
model = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = model
spec.loader.exec_module(model)


class FormalMethodsTests(unittest.TestCase):
    def command(self, variant="safe", source=MODEL):
        result = subprocess.run([sys.executable, str(source), "--variant", variant],
                                capture_output=True, text=True)
        return result.returncode, json.loads(result.stdout)

    def digest(self, area, selected=True, override=""):
        selection = "## Active Concerns\n" + ("- formal-methods\n" if selected else "")
        selection += "\n## Project Overrides\n### formal-methods\n"
        if override:
            selection += f"- {override}\n"
        library = digests.build_concern_library(
            ROOT, digests.parse_active_concerns(selection), digests.parse_overrides(selection))
        body, _ = digests.build_digest(
            {"title": "Change a bounded slice", "description": "Design authority",
             "acceptance": "Record scope disposition", "labels": [f"area:{area}"]},
            principles=[], library=library, root=ROOT)
        return body

    def test_selection_reaches_all_work_areas_without_automatic_analysis(self):
        for area in ("cli", "ui", "data", "api", "infra", "testing"):
            with self.subTest(area=area):
                body = self.digest(area)
                self.assertIn("<concerns>formal-methods</concerns>", body)
                self.assertIn("only to recorded affected slices", body)
                self.assertIn("non-applicability disposition", body)
        self.assertNotIn("formal-methods", self.digest("cli", selected=False))

    def test_scope_rigor_and_unaffected_disposition_survive_existing_overrides(self):
        scope = "Scope lease lifecycle; executable analysis; authority Design lease-1"
        self.assertIn(scope, self.digest("cli", override=scope))
        excluded = "CSV display is unaffected: no mapped guards change; no analyzer/proof run"
        body = self.digest("ui", override=excluded)
        self.assertIn("<concerns>formal-methods</concerns>", body)
        self.assertIn(excluded, body)
        self.assertIn("only to recorded affected slices", body)

    def test_safe_complete_exploration_has_replayed_success_and_ordered_race(self):
        code, report = self.command()
        self.assertEqual(code, 0)
        self.assertEqual(report["outcome"], "PASS_BOUNDED")
        self.assertTrue(report["complete"])
        self.assertEqual(report["states_discovered"], report["states_checked"])
        self.assertGreater(report["transitions_explored"], report["states_checked"])
        self.assertEqual(report["violations"], [])
        self.assertEqual(report["liveness"], "NOT_CHECKED")
        self.assertEqual(report["correspondence"], "UNMAPPED")
        self.assertEqual(report["model_sha256"], hashlib.sha256(MODEL.read_bytes()).hexdigest())
        for name, witness in report["witnesses"].items():
            final = model.replay(witness["actions"], "safe")[-1]
            self.assertIn(name, model.witness_names(final))
            self.assertTrue(witness["replayed"])
        actions = report["witnesses"]["expire_reclaim_late_return"]["actions"]
        order = [actions.index(a) for a in ("claim(0)", "expire(0)", "claim(1)", "return(0)")]
        self.assertEqual(order, sorted(order))
        final = model.replay(actions, "safe")[-1]
        self.assertEqual(final.tokens, (1, 2))
        self.assertEqual(final.valid, (False, True))

    def test_mutants_report_targeted_violations_with_replayed_shortest_traces(self):
        for variant, target, length in (("unfenced", "stale_landing_rejected", 5),
                                        ("lock-held", "no_lock_across_wait", 2)):
            with self.subTest(variant=variant):
                code, report = self.command(variant)
                self.assertEqual(code, 1)
                self.assertEqual(report["outcome"], "VIOLATION")
                self.assertFalse(report["complete"])
                self.assertEqual(report["violations"], [target])
                trace = report["counterexample"]
                self.assertTrue(trace["replayed"])
                self.assertEqual(len(trace["actions"]), length)
                states = model.replay(trace["actions"], variant)
                self.assertEqual(trace["states"], json.loads(json.dumps([asdict(s) for s in states])))
                self.assertEqual(model.violations(states[-1]), [target])
                self.assertTrue(all(not model.violations(s) for s in states[:-1]))

    def test_late_return_rejected_while_new_owner_remains_valid(self):
        actions = ["claim(0)", "start_wait(0)", "expire(0)", "claim(1)",
                   "start_wait(1)", "return(0)", "land(0)"]
        state = model.replay(actions, "safe")[-1]
        self.assertEqual(state.phases, ("rejected", "running"))
        self.assertEqual(state.valid, (False, True))
        self.assertFalse(state.landed)
        bad = model.replay(actions, "unfenced")[-1]
        self.assertIn("stale_landing_rejected", model.violations(bad))

    def test_unreachable_success_is_error_not_vacuous_pass(self):
        with patch.object(model, "witness_names", return_value=[]):
            with self.assertRaisesRegex(ValueError, "Incomplete behavioral coverage"):
                model.explore()

    def test_checker_error_has_distinct_exit_and_outcome(self):
        with patch.object(model, "explore", side_effect=RuntimeError("checker failed")), \
                patch.object(sys, "argv", [str(MODEL)]), patch("builtins.print") as output:
            self.assertEqual(model.main(), 2)
            report = json.loads(output.call_args.args[0])
            self.assertEqual(report["outcome"], "ERROR")
            self.assertFalse(report["complete"])

    def test_catalog_floor_carries_runnable_model_and_concern(self):
        with tempfile.TemporaryDirectory() as directory:
            floor = Path(directory) / "references"
            subprocess.run([sys.executable, str(ROOT / "scripts/sync_references.py"), str(floor)],
                           check=True, capture_output=True, text=True)
            self.assertTrue((floor / "concerns/formal-methods/concern.md").exists())
            bundled = floor / "references/formal-methods/lease_model.py"
            self.assertEqual(bundled.read_bytes(), MODEL.read_bytes())
            code, report = self.command(source=bundled)
            self.assertEqual(code, 0)
            self.assertEqual(report["outcome"], "PASS_BOUNDED")


if __name__ == "__main__":
    unittest.main()
