"""Real artifact-validator and concern-propagation positive/negative controls."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import refresh_context_digests as digests

VALIDATOR = ROOT / 'skills/helix/scripts/validate-instance.py'
STP = ROOT / 'workflows/activities/03-test/artifacts/story-test-plan/example.md'
PATTERNS = ('navigation', 'keyboard-overlays', 'async-actions', 'forms', 'data-states', 'destructive-actions')


class UXGovernanceTests(unittest.TestCase):
    def validate(self, body, kind='story-test-plan'):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'instance.md'
            path.write_text(body)
            result = subprocess.run([sys.executable, str(VALIDATOR), str(path), '--catalog', str(ROOT / 'workflows'), '--type', kind, '--format', 'json'], capture_output=True, text=True)
            self.assertTrue(result.stdout.strip(), result.stderr)
        return result.returncode, json.loads(result.stdout)

    def body(self, covered=True):
        # Reuse the catalog example's real AC table, without inventing another matrix.
        original = STP.read_text()
        ac_rows = [line for line in original.splitlines() if line.startswith('| US-')]
        self.assertTrue(ac_rows)
        ac = ac_rows[0].split('|')[1].strip()
        coverage = '\n## UX Coverage\n\n| Pattern | Disposition | AC IDs or Reason |\n|---|---|---|\n'
        for pattern in PATTERNS:
            if covered and pattern in ('navigation', 'keyboard-overlays'):
                coverage += f'| {pattern} | covered | {ac} |\n'
            else:
                coverage += f'| {pattern} | not-applicable | No {pattern} in this slice |\n'
        return original + coverage

    def assert_ux_failure(self, body):
        code, report = self.validate(body)
        self.assertEqual(code, 1, report)
        self.assertTrue(any(f['check'] == 'ux_coverage' and f['severity'] == 'blocking' for f in report['findings']), report)

    def test_legacy_omission_stays_structurally_valid(self):
        self.assertEqual(self.validate(STP.read_text())[0], 0)

    def test_covered_and_no_ui_dispositions_pass(self):
        for covered in (True, False):
            for legacy_header in (True, False):
                with self.subTest(covered=covered, legacy_header=legacy_header):
                    body = self.body(covered)
                    if legacy_header:
                        body = body.replace('New or Existing Test(s) to Create or Run',
                                            'Failing Test(s) to Create or Run')
                    code, report = self.validate(body)
                    self.assertEqual(code, 0, report)

    def test_missing_each_pattern_fails(self):
        for pattern in PATTERNS:
            with self.subTest(pattern=pattern):
                self.assert_ux_failure('\n'.join(line for line in self.body().splitlines() if not line.startswith(f'| {pattern} |')))

    def test_duplicate_section_and_rows_fail(self):
        body = self.body()
        self.assert_ux_failure(body + '\n## UX Coverage\n')
        self.assert_ux_failure(body + '| forms | not-applicable | No form here |\n')

    def test_unknown_disposition_and_pattern_fail(self):
        self.assert_ux_failure(self.body().replace('| navigation | covered |', '| navigation | passed |'))
        self.assert_ux_failure(self.body().replace('| navigation | covered |', '| invented | covered |'))

    def test_empty_exclusion_reason_fails(self):
        for value in ('', 'N/A', '-'):
            self.assert_ux_failure(self.body(False).replace('No forms in this slice', value))

    def test_absent_ac_and_invalid_ids_fail(self):
        for value in ('US-999-AC99', 'some test', ''):
            body = self.body()
            row = next(line for line in body.splitlines() if line.startswith('| navigation |'))
            altered = '| navigation | covered | ' + value + ' |'
            self.assert_ux_failure(body.replace(row, altered))

    def test_mapped_test_assertion_and_command_cannot_be_blank(self):
        body = self.body()
        row = next(line for line in body.splitlines() if line.startswith('| US-'))
        cells = row.split('|')
        for index in (3, 4, 7):
            with self.subTest(column=index):
                altered = cells.copy()
                altered[index] = ' '
                self.assert_ux_failure(body.replace(row, '|'.join(altered)))

    def test_formatting_only_mapped_cells_fail(self):
        body = self.body()
        row = next(line for line in body.splitlines() if line.startswith('| US-'))
        for index in (3, 4, 7):
            for value in ('   ', '``', '`  `'):
                with self.subTest(column=index, value=value):
                    altered = row.split('|')
                    altered[index] = value
                    self.assert_ux_failure(body.replace(row, '|'.join(altered)))

    def test_design_without_page_navigation_needs_reason(self):
        body = (ROOT / 'workflows/activities/02-design/artifacts/design-system/example-packaged.md').read_text()
        body = body.replace('aria-current', 'current-state')
        code, report = self.validate(body, 'design-system')
        self.assertEqual(code, 1, report)
        code, report = self.validate(body + '\nPage navigation: not-applicable; Embedded single-surface view has no routes\n', 'design-system')
        self.assertEqual(code, 0, report)

    def test_duplicate_mapping_ids_fail(self):
        body = self.body()
        row = next(line for line in body.splitlines() if line.startswith('| US-'))
        self.assert_ux_failure(body.replace(row, row + '\n' + row))

    def test_multiple_existing_ac_ids_pass(self):
        body = self.body()
        ids = [line.split('|')[1].strip() for line in body.splitlines() if line.startswith('| US-')]
        self.assertGreater(len(ids), 1)
        row = next(line for line in body.splitlines() if line.startswith('| navigation |'))
        code, report = self.validate(body.replace(row, '| navigation | covered | ' + ', '.join(ids[:2]) + ' |'))
        self.assertEqual(code, 0, report)

    def test_local_and_packaged_design_examples_pass(self):
        for name in ('example.md', 'example-packaged.md'):
            code, report = self.validate((ROOT / 'workflows/activities/02-design/artifacts/design-system' / name).read_text(), 'design-system')
            self.assertEqual(code, 0, report)

    def digest(self, selected, area='ui'):
        library = digests.build_concern_library(ROOT, selected, {})
        body, _ = digests.build_digest({'title': 'Bounded UX change', 'description': 'Test authority', 'acceptance': 'Exercise behavior', 'labels': [f'area:{area}']}, principles=[], library=library, root=ROOT)
        return body, library

    def test_existing_and_packaged_adapters_compose_baseline_without_other_kit(self):
        for selected in ('ux-radix', 'packaged-design-system', 'databricks-appkit-ui'):
            with self.subTest(selected=selected):
                body, library = self.digest([selected])
                self.assertIn('ux-interaction-patterns', library)
                self.assertIn('ux-interaction-patterns', body)
                self.assertIn('STP UX Coverage', body)
                self.assertIn('running system', body)
                if selected == 'packaged-design-system':
                    self.assertNotIn('ux-radix', library)
                    self.assertIn('installed-version documentation', body)
                    self.assertIn('quality checks', body)
                api, _ = self.digest([selected], 'api')
                self.assertNotIn('<concerns>', api)
        body, library = self.digest([])
        self.assertNotIn('ux-interaction-patterns', library)

    def test_realistic_packaged_selection_survives_compact_digest(self):
        selected = ['typescript-bun', 'react-nextjs', 'a11y-wcag-aa', 'testing', 'verification', 'packaged-design-system']
        for explicit_baseline in (False, True):
            with self.subTest(explicit_baseline=explicit_baseline):
                names = selected + (['ux-interaction-patterns'] if explicit_baseline else [])
                library = digests.build_concern_library(ROOT, names, {'packaged-design-system': ['Scope Records route; reviewed audit exception expires after packaged design system upgrade']})
                body, _ = digests.build_digest({'title': 'Packaged records view', 'description': 'Design authority', 'acceptance': 'Exercise behavior', 'labels': ['area:frontend']}, principles=[], library=library, root=ROOT)
                self.assertIn('ux-interaction-patterns | packaged-design-system', body)
                self.assertIn('installed-version documentation', body)
                self.assertIn('quality checks', body)
                self.assertIn('Scope Records route', body)

    def test_catalog_floor_packages_both_concerns_and_evidence_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'references'
            subprocess.run([sys.executable, str(ROOT / 'scripts/sync_references.py'), str(target)], check=True, capture_output=True, text=True)
            for name in ('ux-interaction-patterns', 'packaged-design-system'):
                self.assertTrue((target / 'concerns' / name / 'practices.md').is_file())
            self.assertTrue((target / 'references/ux-evidence.md').is_file())


if __name__ == '__main__':
    unittest.main()
