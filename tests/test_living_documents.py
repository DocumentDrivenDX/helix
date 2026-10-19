"""Working intent remains usable through light drift; material checks still fail."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills/helix/scripts/validate-instance.py'
SPEC = importlib.util.spec_from_file_location('validate_instance', SCRIPT)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)

CATALOG_SPEC = importlib.util.spec_from_file_location(
    'validate_catalog', ROOT / 'scripts/helix_validate_artifact_meta.py')
catalog_validator = importlib.util.module_from_spec(CATALOG_SPEC)
CATALOG_SPEC.loader.exec_module(catalog_validator)


class LivingDocumentTests(unittest.TestCase):
    def validate(self, text):
        with tempfile.TemporaryDirectory() as directory:
            instance = Path(directory) / 'ADR-001-choice.md'
            instance.write_text(text)
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(instance), '--catalog',
                 str(ROOT / 'workflows'), '--format', 'json'],
                text=True, capture_output=True,
            )
        self.assertIn(result.returncode, (0, 1), result.stderr)
        return result.returncode, json.loads(result.stdout)

    def test_light_metadata_drift_does_not_change_content_validation(self):
        text = (ROOT / 'workflows/activities/02-design/artifacts/adr/example.md').read_text()
        fm, body, _ = validator.split_frontmatter(text)
        code, baseline = self.validate(text)
        self.assertEqual(code, 0)
        for status in (None, 'draft', 'review', 'approved', 'deprecated', 'superseded'):
            with self.subTest(status=status):
                metadata = yaml.safe_load(yaml.safe_dump(fm))
                metadata['ddx']['depends_on'] = ['missing.upstream']
                metadata['ddx']['links'] = []
                metadata['ddx']['review'] = {'self_hash': 'stale', 'deps': {}}
                if status:
                    metadata['ddx']['status'] = status
                else:
                    metadata['ddx'].pop('status', None)
                code, report = self.validate('---\n' + yaml.safe_dump(metadata) + '---\n' + body)
                self.assertEqual(code, 0, report)
                self.assertEqual(report['findings'], baseline['findings'])

    def test_unaddressable_prose_does_not_produce_housekeeping_findings(self):
        for metadata in (None, {}, {'title': 'Working intent'}):
            report = validator.Report()
            validator.check_frontmatter(metadata, report)
            self.assertEqual(report.findings, [])

    def test_legacy_admin_sections_do_not_hide_missing_substantive_content(self):
        report = validator.Report()
        validator.check_required_sections(
            ['document_status', 'document_approvals', 'trace_links',
             'requirements', 'compliance_status', 'approvals'],
            Path('/nonexistent/template.md'), '', True, report,
        )
        self.assertEqual({f['check'] for f in report.findings}, {
            'required_sections.requirements', 'required_sections.compliance_status',
            'required_sections.approvals',
        })
        self.assertTrue(all(f['severity'] == 'blocking' for f in report.findings))

    def test_approved_label_does_not_hide_broken_requirements(self):
        text = (ROOT / 'tests/fixtures/validate-instance/broken-prd.md').read_text()
        fm, body, _ = validator.split_frontmatter(text)
        fm['ddx']['status'] = 'approved'
        code, report = self.validate('---\n' + yaml.safe_dump(fm) + '---\n' + body)
        self.assertEqual(code, 1)
        checks = {f['check'] for f in report['findings'] if f['severity'] == 'blocking'}
        self.assertIn('required_sections.success_criteria', checks)
        self.assertIn('placeholder', checks)

    def test_invalid_explicit_authoring_home_still_blocks(self):
        report = validator.Report()
        validator.check_frontmatter({'ddx': {'id': 'ADR-001', 'authoring': {'home': 'unknown'}}}, report)
        self.assertEqual(report.findings[0]['check'], 'frontmatter.authoring_home')
        self.assertEqual(report.findings[0]['severity'], 'blocking')

    def test_catalog_guard_distinguishes_domain_authorization(self):
        check = catalog_validator.check_lifecycle_defaults
        self.assertTrue(check('workflow:\n  approval_required: true\n', ''))
        self.assertTrue(check('', '---\nddx:\n  status: draft\n---\n'))
        self.assertTrue(check('', '**Status**: [Draft | Review | Approved]'))
        self.assertTrue(check('', '**Status:** Draft'))
        self.assertEqual(check('operations:\n  approval_required: true\n',
                               'Production go/no-go decision approved\n```yaml\n  status: draft\n```'), [])

    def test_catalog_does_not_reintroduce_generic_approval_lifecycle(self):
        for path in (ROOT / 'workflows/activities').glob('*/artifacts/*/meta.yml'):
            with self.subTest(path=path):
                meta = yaml.safe_load(path.read_text())
                self.assertNotIn('approval_required', meta.get('workflow', {}))
                self.assertNotIn('approvers', meta.get('workflow', {}))
                self.assertNotIn('status_values', meta.get('tracking', {}))
        for path in (ROOT / 'workflows/activities').glob('*/artifacts/*/template.md'):
            with self.subTest(path=path):
                self.assertNotRegex(path.read_text(), r'(?m)^  status: (draft|approved|review|deprecated|superseded)$')
        # Actual operational constraints and test evidence are still substantive.
        self.assertIn('Production go/no-go decision approved',
                      (ROOT / 'workflows/activities/05-deploy/GATE.yaml').read_text())
        self.assertIn('require manual approval',
                      (ROOT / 'workflows/activities/03-test/artifacts/data-quality-expectations/template.md').read_text())


if __name__ == '__main__':
    unittest.main()
