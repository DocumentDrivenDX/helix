"""Release version regression tests, including the v0.20.0 publication race."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('release_version', ROOT / 'scripts/release-version.py')
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class ReleaseVersionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ['.claude-plugin/plugin.json', '.codex-plugin/plugin.json',
                     '.claude-plugin/marketplace.json', 'tools/documentor/pyproject.toml',
                     'tools/documentor/src/documentor/__init__.py', 'tools/documentor/uv.lock']:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)

    def test_bump_checks_all_shipped_versions(self):
        release.synchronize(self.root, 'v1.2.3', write=True)
        self.assertEqual(release.synchronize(self.root, 'v1.2.3'), [])
        self.assertEqual(json.loads((self.root / '.codex-plugin/plugin.json').read_text())['version'], '1.2.3')
        self.assertIn('__version__ = "1.2.3"', (self.root / 'tools/documentor/src/documentor/__init__.py').read_text())

    def test_rejects_each_stale_surface_without_writing(self):
        release.synchronize(self.root, 'v1.2.3', write=True)
        for path in list(self.root.rglob('*')):
            if path.is_file():
                with self.subTest(path=str(path)):
                    original = path.read_text()
                    path.write_text(original.replace('1.2.3', '0.19.1'))
                    with self.assertRaisesRegex(ValueError, 'release version mismatch'):
                        release.synchronize(self.root, 'v1.2.3')
                    self.assertIn('0.19.1', path.read_text())
                    path.write_text(original)

    def test_version_bump_refreshes_only_current_source_evidence(self):
        import hashlib
        source = self.root / 'tools/documentor/pyproject.toml'
        normalized = "\n".join(line.rstrip() for line in source.read_text().strip().splitlines())
        old = hashlib.sha256(normalized.encode()).hexdigest()[:16]
        page = self.root / 'tools/documentor/docs/guide/developer/architecture.md'
        page.parent.mkdir(parents=True)
        page.write_text(f'<!-- helix:source pyproject.toml sha256:{old} -->\n# Unchanged body\n')
        stale = page.with_name('embedding.md')
        stale.write_text('<!-- helix:source pyproject.toml sha256:deadbeef -->\n# Stale body\n')
        release.synchronize(self.root, 'v1.2.3', write=True)
        self.assertNotIn(old, page.read_text())
        self.assertTrue(page.read_text().endswith('# Unchanged body\n'))
        self.assertIn('deadbeef', stale.read_text())

    def test_rejects_invalid_tags_before_writing(self):
        for tag in ['main', 'v1.2', 'v1.2.3; echo bad', 'v1.2.3-rc1']:
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                release.synchronize(self.root, tag, write=True)

    def test_publisher_validates_before_build_and_upload(self):
        workflow = (ROOT / '.github/workflows/release-genie-bundle.yml').read_text()
        check = workflow.index('run: python3 scripts/release-version.py')
        self.assertLess(check, workflow.index('run: bash scripts/build-genie-bundle.sh'))
        self.assertLess(check, workflow.index('uses: softprops/action-gh-release'))
        self.assertNotIn('continue-on-error:', workflow)
        self.assertIn('target_commitish: ${{ github.sha }}', workflow)

    def test_guard_checks_selected_tag_and_quarantines_ui_release(self):
        workflow = (ROOT / '.github/workflows/release-version-guard.yml').read_text()
        self.assertIn('ref: ${{ inputs.tag || github.event.release.tag_name || github.ref }}', workflow)
        self.assertIn('types: [published]', workflow)
        self.assertIn('--draft=true', workflow)
        self.assertNotIn('release delete', workflow)
        self.assertNotIn('|| true', workflow)

    def test_ui_release_opens_version_pr_and_runs_ci(self):
        workflow = (ROOT / '.github/workflows/release-ui.yml').read_text()
        self.assertIn('types: [published]', workflow)
        self.assertLess(workflow.index('--draft=true'), workflow.index('gh pr create'))
        self.assertIn('python3 scripts/release-version.py "$TAG" --write', workflow)
        self.assertIn('git rev-parse origin/main', workflow)
        self.assertIn('gh workflow run test.yml', workflow)

    def test_existing_tag_requires_draft_and_version_only_diff(self):
        workflow = (ROOT / '.github/workflows/release-tag.yml').read_text()
        self.assertIn('--json isDraft --jq .isDraft)', workflow)
        self.assertIn('changed and changed <= allowed | guide_pages', workflow)
        self.assertIn('--force-with-lease="refs/tags/$TAG:$OLD"', workflow)
        self.assertIn('git merge-base --is-ancestor', workflow)


if __name__ == '__main__':
    unittest.main()
