"""Catalog contract checks; these do not prove consumer runtime behavior.

Requirement authority: FEAT-008 FR-6; FEAT-010 FR-6/8/9; FEAT-016 FR-2.
"""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text()


def prose(path):
    return " ".join(read(path).split())


class VerificationContractTests(unittest.TestCase):
    def test_build_keeps_execution_gate_and_removes_shared_file_check(self):
        # FEAT-010 FR-8: observed runtime proof, without a storage surrogate.
        gate = yaml.safe_load(read('workflows/activities/04-build/GATE.yaml'))
        checks = gate['exit_requirements']['automated']
        self.assertIn('tests_passing', [item['check'] for item in checks])
        for item in checks:
            self.assertNotIn('verification-evidence', item.get('path', ''))
        # Semantic coverage remains manual; no imaginary new executable check.
        self.assertEqual({item['check'] for item in checks}, {
            'tests_passing', 'security_scan_clean',
            'lint_clean', 'file_exists', 'dir_not_empty', 'grep_absent',
        })
        review = '\n'.join(gate['exit_requirements']['manual'])
        for term in ('acceptance mappings', 'test-source citations',
                     'meaningful assertions', 'observed passing results',
                     'verification/practices.md', 'guard/negative branch',
                     'RUNNING system', 'Downstream-consumer', 'pulled the change'):
            self.assertIn(term, review)

    def test_existing_reports_suffice_and_only_proof_gaps_need_supplements(self):
        # FEAT-008 FR-6: avoid a second AC matrix or mandatory extra file.
        policy = prose('workflows/concerns/verification/practices.md')
        for term in ('Acceptance Criteria Test Mapping', 'test-source', '@covers',
                     'no supplemental record is needed',
                     'normal reporting cannot capture the required proof',
                     'A real-client integration report',
                     'existing mapping\'s Notes/Executable Proof',
                     'no `verification-evidence.md`', 'second per-criterion matrix'):
            self.assertIn(term, policy)
        for path in (ROOT / 'workflows').rglob('*'):
            if path.suffix not in ('.md', '.yaml', '.yml'):
                continue
            for line in path.read_text().splitlines():
                if 'verification-evidence.md' in line:
                    self.assertIn('requires no', line, str(path))

    def test_completion_requires_current_accessible_observed_results(self):
        # FEAT-016 FR-2: tags, green totals and stale links cannot prove claims.
        policy = prose('workflows/concerns/verification/practices.md')
        for term in ('mapped test exists', 'asserts its actual outcome',
                     'ran successfully at the required', 'tested revision',
                     'command and exit status', 'environment/data state',
                     'executed tests and outcomes', 'dirty checkout',
                     'identify the tested diff', 'Otherwise rerun',
                     'skipped, deselected or unreported', 'retention period',
                     'expired results are unknown', 'unknown until recovered or rerun'):
            self.assertIn(term, policy)
        for name in ('fresh-eyes-review', 'reconcile-alignment'):
            policy = prose(f'workflows/actions/{name}.md')
            for term in ('test-source citations', 'assertions', 'observed',
                         'verification completion contract', 'verification/practices.md'):
                self.assertIn(term, policy)

    def test_names_describe_conditions_and_keep_legacy_citations_valid(self):
        # FEAT-008 FR-6 and FEAT-010 FR-9: names aid discovery, IDs aid linking.
        policy = read('workflows/concerns/testing/practices.md')
        for term in ('TestClaim_RejectsAlreadyLeasedBead',
                     'test_route_resolution_timeout_releases_lease',
                     '@covers US-001-AC2', 'Parameterized cases',
                     'multiple criteria', 'each with its own `@covers`',
                     'Existing valid', 'bodies, names or doc comments',
                     'no bulk rename', 'meaningful assertions'):
            self.assertIn(term, policy)
        template = prose('workflows/activities/03-test/artifacts/story-test-plan/template.md')
        self.assertIn('test body, name, or doc comment', template)
        self.assertIn('passing results are required only for completion claims', template)
        self.assertNotIn('| Run Result |', template)
        self.assertIn('No new table,', template)

    def test_exceptions_and_surface_proof_survive_storage_change(self):
        # FEAT-010 FR-6/8: proof outside reporting still needs review.
        policy = prose('workflows/concerns/verification/practices.md')
        for term in ('guard/negative branch', 'running system',
                     'consumer pulled the change', 'library / docs-only',
                     'scope, owner', 'reviewer/decision', 'review/removal',
                     'strongest observable evidence', 'never asserted', 'selected concerns and slots',
                     'browser E2E', 'HTTP+HTML', 'aria-current',
                     'real client handshake/login', 'updating `concerns.md`'):
            self.assertIn(term, policy)
        metering = prose('workflows/concerns/usage-metering/practices.md')
        for term in ('real billable flow', 'idempotency guard branch',
                     'reconciliation', 'tested revision', 'verification/practices.md'):
            self.assertIn(term, metering)
        ux = prose('workflows/references/ux-evidence.md')
        for term in ('appropriate real-surface harness', 'verification/practices.md',
                     'No screenshot-only semantic proof'):
            self.assertIn(term, ux)


if __name__ == '__main__':
    unittest.main()
