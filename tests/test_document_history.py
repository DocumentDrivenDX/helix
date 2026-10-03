"""Document history guard: citations fail; technical language remains valid."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_instance", ROOT / "skills/helix/scripts/validate-instance.py"
)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class DocumentHistoryTests(unittest.TestCase):
    def findings(self, body):
        report = validator.Report()
        validator.check_delivery_history(body, 1, report)
        return report.findings

    def test_repository_citations_fail(self):
        for citation in (
            "Implemented in PR #42", "See PR42", "pull request 42",
            "https://github.com/org/repo/pull/42",
            "https://github.com/org/repo/commit/abc1234",
            "commit `abc1234`", "revision abc1234", "commit SHA abc1234",
            "---\nddx:\n  commit: abc1234\n---\n# Intent",
        ):
            with self.subTest(citation=citation):
                self.assertEqual(self.findings(citation)[0]["severity"], "blocking")

    def test_technical_semantics_and_non_git_identifiers_pass(self):
        self.assertEqual(self.findings(
            "Transactions commit atomically. Release v0.14.1 uses ADR-003.\n"
            "Run tests before committing. Session `2f92aad5` has 18 prompts.\n"
            "The export SHA256 is " + "a" * 64
        ), [])

    def test_findings_have_source_lines(self):
        self.assertEqual(self.findings("Requirement.\nSee PR #42.")[0]["line"], 2)

    def test_active_corpus_has_no_repository_citations(self):
        paths = list((ROOT / "docs/helix").rglob("*.md"))
        paths.append(ROOT / "skills/helix/SKILL.md")
        paths.extend((ROOT / "workflows").rglob("*.md"))
        paths.extend((ROOT / "workflows").rglob("*.yml"))
        for path in paths:
            if "archive" in path.relative_to(ROOT).parts:
                continue
            with self.subTest(path=str(path.relative_to(ROOT))):
                self.assertEqual(self.findings(path.read_text()), [])


if __name__ == "__main__":
    unittest.main()
