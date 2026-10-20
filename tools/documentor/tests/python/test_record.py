"""The record: local diagram publication must preserve bytes, links, and source boundaries."""
from pathlib import Path
import tempfile
import unittest

from documentor import record as publisher


def opts(root, prefix="artifacts"):
    notes = dict(publisher.DEFAULT_NOTES)
    return {"prefix": prefix, "blob": "", "notes": notes, "repo_root": root, "helix_rel": "docs/helix", "title": "Record"}


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
            self.assertEqual(publisher.publish(source, dest, 'Example', opts(root)), 0)
            output = dest / 'media/02-design/diagrams/overview.svg'
            self.assertEqual(output.read_bytes(), diagram.read_bytes())
            page = (dest / 'overview.md').read_text()
            self.assertIn('![Map](/artifacts/media/02-design/diagrams/overview.svg)', page)
            self.assertIn('[Editable](/artifacts/media/02-design/diagrams/overview.svg#title)', page)
            first = page
            publisher.publish(source, dest, 'Example', opts(root))
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
            self.assertEqual(publisher.publish_images(records, source, dest, 'artifacts'), {})
            self.assertEqual(list(dest.iterdir()), [])


if __name__ == '__main__':
    unittest.main()


class RecordOptionsTests(unittest.TestCase):
    def test_the_record_follows_the_publish_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs/helix/01-frame").mkdir(parents=True)
            (root / "docs/helix/01-frame/prd.md").write_text("# PRD\n\nSee [the repo](../../../README.md).\n")
            (root / "README.md").write_text("# Readme\n")
            config = {"flows": [{"id": "helix", "root": "docs/helix/"}],
                      "publish": {"site": {"title": "Example", "repo_url": "https://git.example/org/ex",
                                           "record_dir": "record"}}}
            source, dest, project, o = publisher.options(root, config, str(root / "out"))
            self.assertEqual(publisher.publish(source, dest, project, o), 0)
            page = (root / "out/prd.md").read_text()
            self.assertIn("From the governed record", page)
            self.assertIn("(https://git.example/org/ex/blob/main/README.md)", page)
            self.assertIn("(/record/prd/)", (root / "out/_index.md").read_text())
