"""Contract regression checks for plan execution and explicit tracker opt-in."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]

def read(path):
    return (ROOT / path).read_text()

class PlanExecutionTests(unittest.TestCase):
    def test_ordinary_intake_does_not_select_installed_tracker(self):
        policy = read('workflows/references/work-item-first.md')
        self.assertIn('Installed binaries, metadata,', policy)
        self.assertIn('Do not search for or invoke a tracker binary', policy)
        self.assertIn('intake alone does not authorize implementation', read('workflows/actions/input.md'))

    def test_implementation_continues_and_recovers_with_evidence(self):
        policy = read('workflows/references/work-item-first.md')
        self.assertIn('context-window boundary is not a stopping condition', policy)
        self.assertIn('Reconcile it against the actual diff and tests on resume', policy)
        self.assertIn('Do not widen acceptance criteria', policy)
        self.assertIn('Planning readiness does not authorize execution', read('workflows/modes/runtime-handoff.md'))

    def test_tracking_preserves_audit_and_avoids_per_step_items(self):
        policy = read('workflows/references/work-item-first.md')
        self.assertIn('claim, audit, and closure rules', policy)
        self.assertIn('independent', policy)
        self.assertIn('Do not turn every step or finding into an item', policy)

    def test_catalog_accepts_direct_execution(self):
        base = 'workflows/activities/04-build/artifacts/implementation-plan/'
        meta = yaml.safe_load(read(base + 'meta.yml'))
        sections = meta['validation']['required_sections']
        self.assertNotIn('issue_decomposition', sections)
        for section in ['execution_contract', 'continuation_evidence', 'exit_criteria']:
            self.assertIn(section, sections)
        for name in ['template.md', 'example.md']:
            self.assertIn('## Execution Contract', read(base + name))
            self.assertIn('## Continuation Evidence', read(base + name))

    def test_portable_prompts_do_not_point_to_tracker_adapter(self):
        for directory in ['actions', 'modes', 'references']:
            for path in (ROOT / 'workflows' / directory).glob('*.md'):
                self.assertNotIn('docs/install/ddx.md', path.read_text(), str(path))

if __name__ == '__main__':
    unittest.main()
