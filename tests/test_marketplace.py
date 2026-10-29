"""Marketplace validation must support independent entries and arbitrary ordering."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('marketplace', ROOT / 'scripts/validate-marketplace.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class MarketplaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / '.claude-plugin').mkdir()
        self.catalog = json.loads((ROOT / '.claude-plugin/marketplace.json').read_text())

    def validate(self):
        (self.root / '.claude-plugin/marketplace.json').write_text(json.dumps(self.catalog))
        return MODULE.validate(self.root)

    def test_entries_are_independent_of_order(self):
        self.catalog['plugins'].reverse()
        result = self.validate()
        self.assertEqual({entry['name'] for entry in result['plugins']}, {'helix', 'ux-builder'})

    def test_install_consistency_selects_helix_by_name(self):
        self.catalog['plugins'].reverse()
        self.validate()
        for path in ROOT.iterdir():
            if path.name != '.claude-plugin':
                (self.root / path.name).symlink_to(path, target_is_directory=path.is_dir())
        (self.root / '.claude-plugin/plugin.json').symlink_to(ROOT / '.claude-plugin/plugin.json')
        result = subprocess.run(['bash', str(ROOT / 'tests/validate-install-consistency.sh'), str(self.root)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_duplicate_and_missing_names_are_rejected(self):
        self.catalog['plugins'].append(copy.deepcopy(self.catalog['plugins'][0]))
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            self.validate()
        self.catalog['plugins'] = [entry for entry in self.catalog['plugins'] if entry['name'] != 'helix']
        with self.assertRaisesRegex(ValueError, 'exactly one helix'):
            self.validate()

    def test_external_plugin_requires_full_commit_pin(self):
        entry = next(entry for entry in self.catalog['plugins'] if entry['name'] == 'ux-builder')
        entry['source'].pop('sha')
        with self.assertRaisesRegex(ValueError, 'pin a tested commit'):
            self.validate()
        entry['source']['sha'] = 'shortsha'
        with self.assertRaisesRegex(ValueError, 'full Git commit'):
            self.validate()

    def test_external_plugin_cannot_escape_its_checkout(self):
        entry = next(entry for entry in self.catalog['plugins'] if entry['name'] == 'ux-builder')
        entry['source']['path'] = './../outside'
        with self.assertRaisesRegex(ValueError, 'contained'):
            self.validate()


if __name__ == '__main__':
    unittest.main()
