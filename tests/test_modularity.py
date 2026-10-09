"""Boundary policy and real instance-validator negative controls."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / 'skills/helix/scripts/validate-instance.py'


class ModularityTests(unittest.TestCase):
    def validate(self, body):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'architecture.md'
            path.write_text(body)
            result = subprocess.run([sys.executable, str(VALIDATOR), str(path), '--catalog', str(ROOT / 'workflows'), '--type', 'architecture', '--format', 'json'], capture_output=True, text=True)
            return result.returncode, json.loads(result.stdout)

    def example(self):
        return (ROOT / 'workflows/activities/02-design/artifacts/architecture/example.md').read_text()

    def test_complete_example_passes(self):
        self.assertEqual(self.validate(self.example())[0], 0)

    def test_legacy_missing_boundary_map_stays_valid(self):
        body = self.example()
        start = body.find('## Module Boundaries')
        if start >= 0:
            end = body.find('\n## ', start + 3)
            body = body[:start] + (body[end:] if end >= 0 else '')
        code, report = self.validate(body)
        self.assertEqual(code, 0)


    def test_empty_boundary_map_blocks(self):
        body = self.example()
        start = body.find('## Module Boundaries')
        end = body.find('\n## ', start + 3)
        body = body[:start] + '## Module Boundaries\n\n' + body[end:]
        code, report = self.validate(body)
        self.assertEqual(code, 1)
        self.assertTrue(any(f['check'] == 'module_boundaries' for f in report['findings']))

    def test_noncanonical_empty_headings_also_block(self):
        original = self.example()
        start = original.index('## Module Boundaries')
        end = original.index('\n## ', start + 3)
        for heading in ('## Module boundaries', '##  Module Boundaries', '## Module Boundaries ##'):
            with self.subTest(heading=heading):
                altered = original[:start] + heading + '\n\n' + original[end:]
                self.assertEqual(self.validate(altered)[0], 1)

    def test_duplicate_boundary_sections_block(self):
        self.assertEqual(self.validate(self.example() + '\n## Module Boundaries\n')[0], 1)

    def test_baseline_covers_all_autonomy_and_libraries(self):
        reference = (ROOT / 'workflows/references/concern-resolution.md').read_text()
        self.assertTrue('## Source-code baseline (all autonomy levels)' in reference)
        baseline = reference.split('## Source-code baseline (all autonomy levels)', 1)[1].split('\n## ', 1)[0]
        for term in ('low', 'medium', 'high', 'libraries', 'source-free', 'existing', 'blocking'):
            self.assertIn(term, baseline)

    def test_workflow_propagation(self):
        for name in ('frame', 'genesis', 'design', 'polish', 'check', 'runtime-handoff', 'review', 'align'):
            with self.subTest(mode=name):
                self.assertTrue('modularity-and-encapsulation' in (ROOT / f'workflows/modes/{name}.md').read_text())


    def test_boundary_missing_evidence_blocks(self):
        body = self.example()
        self.assertIn('## Module Boundaries', body)
        for label in ('Source Applicability', 'Integration Owners', 'Construction Policy', 'Boundary Check'):
            with self.subTest(label=label):
                altered = '\n'.join(line for line in body.splitlines() if not line.startswith(f'**{label}**:'))
                self.assertEqual(self.validate(altered)[0], 1)

    def test_blank_labels_do_not_capture_following_prose(self):
        body = self.example()
        for label in ('Integration Owners', 'Construction Policy', 'Boundary Check'):
            with self.subTest(label=label):
                altered = '\n'.join(f'**{label}**:\n\nUnrelated text' if line.startswith(f'**{label}**:') else line for line in body.splitlines())
                self.assertEqual(self.validate(altered)[0], 1)

    def test_blank_boundary_cell_blocks(self):
        body = self.example().replace('Owns matching invariants and core value types', '')
        self.assertNotEqual(body, self.example())
        self.assertEqual(self.validate(body)[0], 1)

    def test_source_free_requires_reason(self):
        original = self.example()
        start = original.index('## Module Boundaries')
        end = original.index('\n## ', start + 3)
        section = '## Module Boundaries\n\n**Source Applicability**: source-free; Documentation catalog with no handwritten source.\n'
        self.assertEqual(self.validate(original[:start] + section + original[end:])[0], 0)
        section = '## Module Boundaries\n\n**Source Applicability**: source-free\n'
        self.assertEqual(self.validate(original[:start] + section + original[end:])[0], 1)

    def test_tiny_classic_layered_is_valid(self):
        original = self.example()
        start = original.index('## Module Boundaries')
        end = original.index('\n## ', start + 3)
        section = """## Module Boundaries

**Source Applicability**: source; One-file local tool with handwritten Python.

| Module | Responsibility / Owned Types | Public API | Allowed Dependencies | Forbidden Dependencies |
|---|---|---|---|---|
| app.py | Local operations and private state | main | stdlib, concrete DAL under classic-layered | UI framework, vendor SDK |

**Integration Owners**: None; no external integration.
**Construction Policy**: app.py owns local construction; classic-layered does not require DI.
**Boundary Check**: python3 tests/check_imports.py
"""
        self.assertEqual(self.validate(original[:start] + section + original[end:])[0], 0)


    def test_real_project_checker_negative_controls(self):
        fixture = ROOT / 'tests/fixtures/modularity-python'
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / 'project'
            shutil.copytree(fixture, project)
            command = [sys.executable, str(project / 'check_boundaries.py')]
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
            domain = project / 'src/domain.py'
            original = domain.read_text()
            for import_text in ('import vendor_sdk', 'from adapter import store', 'import service'):
                with self.subTest(import_text=import_text):
                    domain.write_text(original + '\n' + import_text + '\n')
                    result = subprocess.run(command, capture_output=True, text=True)
                    self.assertEqual(result.returncode, 1)
                    self.assertIn('forbidden domain import', result.stdout)


if __name__ == '__main__':
    unittest.main()
