"""Publishing into the organization marketplace, DocumentDrivenDX/plugins."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('publish_plugin', ROOT / 'scripts/publish-plugin.py')
publish = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publish)


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


class PublishPluginTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.checkout = Path(temp.name) / 'plugins-repo'
        self.package = Path(temp.name) / 'package'
        self.marketplace(source='./plugins/helix')
        write(self.checkout / 'plugins/other/keep.txt', 'other plugin')
        self.build('1.0.0', 'first')
        write(self.package / '.claude-plugin/marketplace.json', '{}')

    def marketplace(self, source, name='documentdrivendx'):
        write(self.checkout / '.claude-plugin/marketplace.json',
              json.dumps({'name': name, 'plugins': [{'name': 'helix', 'source': source}]}))

    def build(self, version, skill, commit='abc'):
        write(self.package / '.claude-plugin/plugin.json', json.dumps({'version': version}))
        write(self.package / 'skills/helix/SKILL.md', skill)
        write(self.package / 'PACKAGE-SOURCE.json', commit)

    def publish(self):
        return publish.publish_into(self.checkout, self.package)

    def published(self, name):
        return self.checkout / 'plugins/helix' / name

    def test_writes_only_the_helix_plugin(self):
        manifest = (self.checkout / '.claude-plugin/marketplace.json').read_text()
        self.assertEqual(self.publish(), ('1.0.0', True))
        self.assertEqual(self.published('skills/helix/SKILL.md').read_text(), 'first')
        self.assertEqual(self.published('PACKAGE-SOURCE.json').read_text(), 'abc')
        self.assertFalse(self.published('.claude-plugin/marketplace.json').exists())
        self.assertEqual((self.checkout / 'plugins/other/keep.txt').read_text(), 'other plugin')
        self.assertEqual((self.checkout / '.claude-plugin/marketplace.json').read_text(), manifest)

    def test_a_new_commit_alone_changes_nothing(self):
        self.publish()
        self.build('1.0.0', 'first', commit='def')
        self.assertEqual(self.publish(), ('1.0.0', False))
        self.assertEqual(self.published('PACKAGE-SOURCE.json').read_text(), 'abc')

    def test_refuses_new_content_under_a_published_version(self):
        self.publish()
        self.build('1.0.0', 'second')
        with self.assertRaisesRegex(ValueError, 'already published'):
            self.publish()
        self.assertEqual(self.published('skills/helix/SKILL.md').read_text(), 'first')

    def test_a_new_version_replaces_the_old_tree(self):
        self.publish()
        write(self.published('stale.txt'), 'removed by the next release')
        self.build('1.1.0', 'second')
        self.assertEqual(self.publish(), ('1.1.0', True))
        self.assertEqual(self.published('skills/helix/SKILL.md').read_text(), 'second')
        self.assertFalse(self.published('stale.txt').exists())

    def test_refuses_to_roll_back_to_an_older_version(self):
        self.build('1.10.0', 'newer')
        self.publish()
        self.build('1.9.0', 'older')
        with self.assertRaisesRegex(ValueError, 'older'):
            self.publish()
        self.assertEqual(self.published('skills/helix/SKILL.md').read_text(), 'newer')

    def test_refuses_a_checkout_that_does_not_list_helix(self):
        for source, name in [('./elsewhere', 'documentdrivendx'), ('./plugins/helix', 'helix')]:
            with self.subTest(source=source, name=name):
                self.marketplace(source, name)
                with self.assertRaisesRegex(ValueError, 'must be named'):
                    self.publish()
                self.assertFalse((self.checkout / 'plugins/helix').exists())


if __name__ == '__main__':
    unittest.main()
