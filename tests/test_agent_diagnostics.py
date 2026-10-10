"""Exercise selected OTel concern injection and the shipped bounded query."""
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import refresh_context_digests as digests


class AgentDiagnosticsTests(unittest.TestCase):
    def test_monitoring_action_uses_contract_mapping_and_conditional_context(self):
        prompt = (ROOT / 'workflows/activities/05-deploy/actions/configure-monitoring/prompt.md').read_text()
        self.assertIn("governing Contract's OpenTelemetry mapping", prompt)
        self.assertIn('only when valid context exists', prompt)
        self.assertIn('run/attempt correlation independent', prompt)
        self.assertNotIn('timestamp, level, service, trace_id, message', prompt)

    def digest(self, area, selected=True, overrides=None):
        library = digests.build_concern_library(
            ROOT, ['o11y-otel'] if selected else [], overrides or {}
        )
        body, _ = digests.build_digest(
            {'title': 'Investigate failed command', 'description': 'Safe run evidence',
             'acceptance': 'Correlate the failed attempt', 'labels': [f'area:{area}']},
            principles=[], library=library, root=ROOT,
        )
        return body

    def test_selected_concern_reaches_cli_data_ui_infra_without_service_only_digest(self):
        for area in ('cli', 'data', 'ui', 'infra', 'backend', 'testing'):
            with self.subTest(area=area):
                body = self.digest(area)
                self.assertIn('<concerns>o11y-otel</concerns>', body)
                self.assertIn('OpenTelemetry governs diagnostics', body)
                self.assertIn('quiet consoles', body)
                self.assertIn('agent-diagnostics.md', body)
                self.assertNotIn('All services must define SLOs', body)
                self.assertNotIn('Every HTTP handler', body)

    def test_no_selection_does_not_auto_inject_or_replace_project_override(self):
        self.assertNotIn('o11y-otel', self.digest('cli', selected=False))
        body = self.digest('cli', overrides={'o11y-otel': ['Retain local runs for 3 days']})
        self.assertIn('OpenTelemetry governs diagnostics', body)
        self.assertIn('Retain local runs for 3 days', body)

    def queries(self):
        files = (
            ROOT / 'workflows/references/agent-diagnostics.md',
            ROOT / 'workflows/activities/05-deploy/artifacts/runbook/example.md',
        )
        for path in files:
            blocks = re.findall(r'```bash\n(.*?)\n```', path.read_text(), re.S)
            queries = [block for block in blocks if block.startswith('jq -cs')]
            self.assertEqual(len(queries), 1, path)
            yield path, queries[0]

    def test_published_queries_filter_bound_output_and_preserve_source_lines(self):
        for path, command in self.queries():
            with self.subTest(path=path), tempfile.TemporaryDirectory() as directory:
                logs = Path(directory) / 'logs'
                logs.mkdir()
                records = [
                    {'severity_number': 17, 'attributes': {'example.run.id': 'other'}},
                    {'severity_number': 9, 'attributes': {'example.run.id': 'run-42'}},
                ] + [
                    {'severity_number': 13, 'body': f'warning-{i}',
                     'attributes': {'example.run.id': 'run-42'}}
                    for i in range(55)
                ]
                source = logs / 'worker-1.jsonl'
                source.write_text(''.join(json.dumps(record) + '\n' for record in records))
                result = subprocess.run(['bash', '-c', command], cwd=directory,
                                        capture_output=True, text=True, check=True)
                report = json.loads(result.stdout)
                self.assertEqual(report['matched'], 55)
                self.assertTrue(report['truncated'])
                self.assertEqual(len(report['records']), 50)
                self.assertEqual(report['records'][0]['line'], 3)
                self.assertEqual(report['records'][0]['source'], 'logs/worker-1.jsonl')
                self.assertTrue(all(row['record']['severity_number'] >= 13
                                    for row in report['records']))

    def test_published_queries_distinguish_zero_matches_from_malformed_input(self):
        for path, command in self.queries():
            with self.subTest(path=path), tempfile.TemporaryDirectory() as directory:
                logs = Path(directory) / 'logs'
                logs.mkdir()
                source = logs / 'worker-1.jsonl'
                source.write_text('{"severity_number":9,"attributes":{"example.run.id":"other"}}\n')
                result = subprocess.run(['bash', '-c', command], cwd=directory,
                                        capture_output=True, text=True, check=True)
                report = json.loads(result.stdout)
                self.assertEqual(report, {'matched': 0, 'truncated': False, 'records': []})
                source.write_text('not valid JSON\n')
                result = subprocess.run(['bash', '-c', command], cwd=directory,
                                        capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue(result.stderr)


if __name__ == '__main__':
    unittest.main()
