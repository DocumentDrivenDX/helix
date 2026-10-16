"""Local diagram publication must preserve bytes, links, and source boundaries."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('publish_artifacts', Path(__file__).resolve().parents[1] / 'scripts/publish-artifacts.py')
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)


class PublishDiagramTests(unittest.TestCase):
    def test_publish_local_diagrams_and_rewrite_download_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'docs/helix'
            design = source / '02-design'
            diagram = design / 'diagrams/overview.svg'
            diagram.parent.mkdir(parents=True)
            diagram.write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
            (design / 'overview.md').write_text('# Overview\n\n![Map](diagrams/overview.svg)\n[Editable](diagrams/overview.svg#title)\n')
            dest = root / 'published'
            self.assertEqual(publisher.publish(source, dest, 'Example'), 0)
            output = dest / 'media/02-design/diagrams/overview.svg'
            self.assertEqual(output.read_bytes(), diagram.read_bytes())
            page = (dest / 'overview.md').read_text()
            self.assertIn('![Map](/artifacts/media/02-design/diagrams/overview.svg)', page)
            self.assertIn('[Editable](/artifacts/media/02-design/diagrams/overview.svg#title)', page)
            first = page
            publisher.publish(source, dest, 'Example')
            self.assertEqual((dest / 'overview.md').read_text(), first)

    def test_outside_root_and_remote_images_are_not_copied(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'docs/helix'
            design = source / '02-design'
            design.mkdir(parents=True)
            (root / 'private.svg').write_text('<svg/>')
            (design / 'escape.svg').symlink_to(root / 'private.svg')
            page = design / 'overview.md'
            page.write_text('# Overview\n![Outside](../../../private.svg)\n![Symlink](escape.svg)\n![Remote](https://example.org/image.png)\n![Missing](missing.png)\n')
            records = publisher.collect_artifacts(source)
            dest = root / 'published'
            dest.mkdir()
            self.assertEqual(publisher.publish_images(records, source, dest), {})
            self.assertEqual(list(dest.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
