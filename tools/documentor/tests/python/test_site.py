"""The site's Linker: a page's relative links become site URLs, repository URLs, or copied assets."""
from pathlib import Path
import tempfile
import unittest

from documentor.site import Linker


class LinkerTests(unittest.TestCase):
    def test_image_inside_a_link_rewrites_both_targets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            page = root / "docs/guide/developer/architecture.md"
            svg = root / "docs/guide/views/deployment.svg"
            svg.parent.mkdir(parents=True)
            page.parent.mkdir(parents=True)
            svg.write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
            content = root / "content/guide"
            linker = Linker(root, content, {}, "", "main", "/guide")
            body = linker.rewrite(page, "[![Where it runs](../views/deployment.svg)](../views/deployment.svg)\n")
            url = "/guide/files/docs/guide/views/deployment.svg"
            self.assertEqual(body, f"[![Where it runs]({url})]({url})\n")
            self.assertTrue((content / "files/docs/guide/views/deployment.svg").is_file())


class LinkSectionsTests(unittest.TestCase):
    def test_a_generated_section_joins_a_scaffolded_sites_navigation_before_the_report(self):
        import yaml

        from documentor.site import link_sections

        with tempfile.TemporaryDirectory() as tmp:
            site = Path(tmp)
            (site / "content" / "estate").mkdir(parents=True)
            (site / "hugo.yaml").write_text(yaml.safe_dump({"params": {"sections": [
                {"id": "developer", "url": "/developer/"}, {"id": "about", "url": "/about/"}]}}))
            config = {"publish": {"site": {"sections": [
                {"id": "estate", "title": "The estate", "generated": {"command": "true"}},
                {"id": "absent", "title": "Absent", "generated": {"command": "true"}}]}}}
            link_sections(config, site)
            ids = [s["id"] for s in yaml.safe_load((site / "hugo.yaml").read_text())["params"]["sections"]]
            self.assertEqual(ids, ["developer", "estate", "about"], "a section that wrote nothing is not linked")

if __name__ == "__main__":
    unittest.main()
