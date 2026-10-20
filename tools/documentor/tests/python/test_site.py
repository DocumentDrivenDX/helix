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


if __name__ == "__main__":
    unittest.main()
