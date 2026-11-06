"""The build report: how each page was made, and which HELIX artifacts would improve the guide."""
import unittest

from documentor import report
from documentor.lib import PagePlan


def page(audience, pid, gaps=(), state="current"):
    entry = {"state": state, "detail": ""}
    if gaps:
        entry["gaps"] = list(gaps)
    return PagePlan(audience, pid, pid.title(), "explanation", "written", f"docs/guide/{audience}/{pid}.md", entry=entry)


class GapTests(unittest.TestCase):
    def test_the_artifact_that_would_improve_most_pages_comes_first(self):
        pages = [page("developer", "index", ["artifact:architecture"]),
                 page("developer", "walkthrough", ["artifact:architecture", "artifact:contract"]),
                 page("user", "about", ["artifact:feature-specification"]),
                 page("user", "using")]
        self.assertEqual(report.gaps(pages), [
            ("architecture", ["developer/index", "developer/walkthrough"]),
            ("contract", ["developer/walkthrough"]),
            ("feature-specification", ["user/about"]),
        ])
        lines = report.gap_lines(pages)
        self.assertIn("Artifacts that would improve the guide", lines[1])
        self.assertTrue(lines[2].strip().startswith("architecture") and "2 pages" in lines[2])

    def test_no_gaps_no_lines(self):
        self.assertEqual(report.gap_lines([page("user", "using")]), [])


if __name__ == "__main__":
    unittest.main()
