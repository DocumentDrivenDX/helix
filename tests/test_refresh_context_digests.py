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


if __name__ == "__main__":
    unittest.main()
