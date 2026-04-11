import tempfile
import unittest
from pathlib import Path

import scripts.refresh_context_digests as refresh_context_digests


class RefreshContextDigestsTest(unittest.TestCase):
    def test_build_digest_keeps_library_practices_and_overrides(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            concern_dir = root / "workflows" / "concerns" / "demo-concern"
            concern_dir.mkdir(parents=True)
            (concern_dir / "concern.md").write_text("## Areas\nall\n", encoding="utf-8")
            (concern_dir / "practices.md").write_text(
                "- Library practice A\n- Library practice B\n- Library practice C\n",
                encoding="utf-8",
            )

            library = refresh_context_digests.build_concern_library(
                root,
                active_concerns=["demo-concern"],
                overrides={"demo-concern": ["Override practice A", "Override practice B"]},
            )
            description, _ = refresh_context_digests.build_digest(
                {
                    "title": "Demo bead",
                    "description": "Review finding.",
                    "acceptance": "Digest includes merged practices.",
                    "labels": ["area:workflow"],
                    "spec-id": "docs/spec.md",
                },
                principles=["Make Intent Explicit"],
                library=library,
                root=root,
            )

        self.assertIn("<practices>Library practice A", description)
        self.assertIn("Override practice A", description)
        self.assertLess(
            description.index("Library practice A"),
            description.index("Override practice A"),
        )

    def test_select_digest_practices_falls_back_to_library_practices(self) -> None:
        selected = refresh_context_digests.select_digest_practices(
            ["Library practice A", "Library practice B", "Library practice C"],
            [],
            limit=2,
        )
        self.assertEqual(selected, ["Library practice A", "Library practice B"])

    def test_select_digest_practices_keeps_unique_override_when_first_matches_library(self) -> None:
        selected = refresh_context_digests.select_digest_practices(
            ["Library practice A", "Library practice B"],
            ["Library practice A", "Override practice C"],
            limit=2,
        )
        self.assertEqual(selected, ["Library practice A", "Override practice C"])

    def test_select_digest_practices_keeps_unique_override_when_early_override_matches_later_library(self) -> None:
        selected = refresh_context_digests.select_digest_practices(
            ["Library practice A", "Library practice B"],
            ["Library practice B", "Override practice C"],
            limit=2,
        )
        self.assertEqual(selected, ["Library practice A", "Override practice C"])

    def test_build_digest_adds_adrs_and_governing_clause_from_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            concern_dir = root / "workflows" / "concerns" / "demo-concern"
            concern_dir.mkdir(parents=True)
            (concern_dir / "concern.md").write_text(
                "# Concern: Demo Concern\n\n## Areas\nworkflow\n\n## ADR References\n- ADR-777\n",
                encoding="utf-8",
            )
            (concern_dir / "practices.md").write_text("- Use deterministic tests\n", encoding="utf-8")

            adr_dir = root / "docs" / "helix" / "02-design" / "adr"
            adr_dir.mkdir(parents=True)
            (adr_dir / "ADR-777-demo-decision.md").write_text(
                "---\n"
                "dun:\n"
                "  id: ADR-777\n"
                "---\n"
                "# ADR-777: Digest Assembly Helper\n\n"
                "| Date | Status | Deciders | Related | Confidence |\n"
                "|------|--------|----------|---------|------------|\n"
                "| 2026-04-10 | Proposed | HELIX maintainers | FEAT-999 | High |\n\n"
                "## Context\n\n"
                "| Aspect | Description |\n"
                "|--------|-------------|\n"
                "| Requirements | Digest refresh must summarize ADR decisions directly in the bead context. |\n\n"
                "## Decision\n\n"
                "The helper resolves ADR references from matched concerns before rebuilding the digest.\n",
                encoding="utf-8",
            )

            spec_dir = root / "docs" / "helix" / "01-frame" / "features"
            spec_dir.mkdir(parents=True)
            (spec_dir / "FEAT-999-demo.md").write_text(
                "---\n"
                "dun:\n"
                "  id: FEAT-999\n"
                "---\n"
                "# Feature Specification: FEAT-999 — Demo\n\n"
                "## Requirements\n\n"
                "- Digest assembly must load ADR references from matched concerns.\n"
                "- Governing context must come from the referenced artifact.\n",
                encoding="utf-8",
            )

            library = refresh_context_digests.build_concern_library(
                root,
                active_concerns=["demo-concern"],
                overrides={},
            )
            description, _ = refresh_context_digests.build_digest(
                {
                    "title": "Digest helper honors ADR refs",
                    "description": "Review finding for the digest helper.",
                    "acceptance": "The helper now includes ADR summaries and governing clauses.",
                    "labels": ["area:workflow"],
                    "spec-id": "FEAT-999",
                },
                principles=["Make Intent Explicit"],
                library=library,
                root=root,
            )

        self.assertIn("<adrs>ADR-777", description)
        self.assertIn("resolves ADR references from matched concerns", description)
        self.assertIn("<governing>FEAT-999", description)
        self.assertIn("Digest assembly must load ADR references from matched concerns.", description)
        self.assertNotIn("The helper now includes ADR summaries and governing clauses.", description)

    def test_build_digest_adds_adrs_from_secondary_matching(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            concern_dir = root / "workflows" / "concerns" / "demo-concern"
            concern_dir.mkdir(parents=True)
            (concern_dir / "concern.md").write_text(
                "# Concern: Demo Concern\n\n## Areas\nworkflow\n",
                encoding="utf-8",
            )
            (concern_dir / "practices.md").write_text("- Use deterministic tests\n", encoding="utf-8")

            adr_dir = root / "docs" / "helix" / "02-design" / "adr"
            adr_dir.mkdir(parents=True)
            (adr_dir / "ADR-888-secondary-match.md").write_text(
                "---\n"
                "dun:\n"
                "  id: ADR-888\n"
                "---\n"
                "# ADR-888: Secondary Match Digest Assembly\n\n"
                "| Date | Status | Deciders | Related | Confidence |\n"
                "|------|--------|----------|---------|------------|\n"
                "| 2026-04-10 | Proposed | HELIX maintainers | FEAT-999 | High |\n\n"
                "## Context\n\n"
                "| Aspect | Description |\n"
                "|--------|-------------|\n"
                "| Requirements | Workflow digest rebuilds must summarize ADRs discovered from the fallback scan. |\n\n"
                "## Decision\n\n"
                "Workflow ADRs discovered outside concern metadata still contribute summaries to the bead digest.\n",
                encoding="utf-8",
            )

            spec_dir = root / "docs" / "helix" / "01-frame" / "features"
            spec_dir.mkdir(parents=True)
            (spec_dir / "FEAT-999-demo.md").write_text(
                "---\n"
                "dun:\n"
                "  id: FEAT-999\n"
                "---\n"
                "# Feature Specification: FEAT-999 — Demo\n\n"
                "## Requirements\n\n"
                "- Digest assembly must summarize secondary ADR matches.\n",
                encoding="utf-8",
            )

            library = refresh_context_digests.build_concern_library(
                root,
                active_concerns=["demo-concern"],
                overrides={},
            )
            description, _ = refresh_context_digests.build_digest(
                {
                    "title": "Digest helper honors secondary ADR refs",
                    "description": "Review finding for the digest helper.",
                    "acceptance": "The helper now includes ADR summaries discovered by fallback matching.",
                    "labels": ["area:workflow"],
                    "spec-id": "FEAT-999",
                },
                principles=["Make Intent Explicit"],
                library=library,
                root=root,
            )

        self.assertIn("<adrs>ADR-888", description)
        self.assertIn("Workflow ADRs discovered outside concern metadata still contribute summaries", description)

    def test_build_digest_supports_project_local_concern_when_library_root_differs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            root = workspace / "project"
            library_root = workspace / "library"
            root.mkdir()
            library_root.mkdir()

            custom_concern_dir = root / "workflows" / "concerns" / "custom-cli"
            custom_concern_dir.mkdir(parents=True)
            (custom_concern_dir / "concern.md").write_text(
                "# Concern: Custom CLI\n\n## Areas\ncli\n\n## ADR References\n- ADR-321\n",
                encoding="utf-8",
            )
            (custom_concern_dir / "practices.md").write_text(
                "- Use project-local custom concern practices\n",
                encoding="utf-8",
            )

            concerns_path = root / "docs" / "helix" / "01-frame"
            concerns_path.mkdir(parents=True)
            (concerns_path / "concerns.md").write_text(
                "# Project Concerns\n\n## Active Concerns\n- custom-cli\n",
                encoding="utf-8",
            )

            adr_dir = root / "docs" / "helix" / "02-design" / "adr"
            adr_dir.mkdir(parents=True)
            (adr_dir / "ADR-321-project-local-custom-cli.md").write_text(
                "---\n"
                "dun:\n"
                "  id: ADR-321\n"
                "---\n"
                "# ADR-321: Project-local custom CLI concern\n\n"
                "## Decision\n\n"
                "Project-local custom concerns remain valid when the HELIX library root differs.\n",
                encoding="utf-8",
            )

            library = refresh_context_digests.build_concern_library(
                root,
                active_concerns=["custom-cli"],
                overrides={},
                library_root=library_root,
            )
            description, _ = refresh_context_digests.build_digest(
                {
                    "title": "Digest refresh honors project-local custom concern",
                    "description": "Review finding for split-root concern handling.",
                    "acceptance": "The digest includes custom concern practices and ADR refs.",
                    "labels": ["area:cli"],
                    "spec-id": "scripts/refresh_context_digests.py",
                },
                principles=["Make Intent Explicit"],
                library=library,
                root=root,
                library_root=library_root,
            )

        self.assertIn("<concerns>custom-cli</concerns>", description)
        self.assertIn("Use project-local custom concern practices", description)
        self.assertIn("<adrs>ADR-321", description)
        self.assertIn("Project-local custom concerns remain valid", description)


if __name__ == "__main__":
    unittest.main()
