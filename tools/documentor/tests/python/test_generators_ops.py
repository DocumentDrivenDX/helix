"""The generators for what a repository runs: CI workflows, tasks, the migrated database, compose services."""
from pathlib import Path
import subprocess
import tempfile
import unittest

from documentor.generate import GENERATORS

FILES = {
    ".helix.yml": "flows:\n  - id: helix\n    root: docs/helix/\n",
    ".github/workflows/ci.yml": "name: CI\non:\n  push:\n    branches: [main]\n  pull_request:\njobs:\n"
                                "  lint:\n    runs-on: ubuntu-latest\n  test:\n    needs: lint\n    runs-on: ubuntu-latest\n",
    "justfile": "# List the recipes. Run with no arguments.\ndefault:\n    just --list\n\n# Run the tests.\ntest *ARGS:\n    pytest {{ARGS}}\n",
    "web/package.json": '{"name": "web", "scripts": {"build": "vite build"}}',
    "app/migrations/versions/0001.py": 'op.execute("""\nCREATE TABLE accounts (\n    id uuid PRIMARY KEY,\n'
                                       '    email text NOT NULL,  -- the login\n    created_at timestamptz\n);\n'
                                       'CREATE TABLE orders (\n    id uuid PRIMARY KEY,\n'
                                       '    account_id uuid NOT NULL REFERENCES accounts (id),\n    CHECK (true)\n);\n""")\n',
    "app/migrations/versions/0002.py": 'op.execute("ALTER TABLE orders ADD COLUMN total numeric(10,2)")\n',
    "notebooks/demo.sql": "CREATE TABLE demo (\n    x int\n);\n",
    "compose.yaml": "services:\n  api:\n    build: .\n    ports: ['8000:8000']\n    depends_on: [db]\n  db:\n    image: postgres:16\n",
}


class OpsGeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name).resolve()
        for path, text in FILES.items():
            (cls.root / path).parent.mkdir(parents=True, exist_ok=True)
            (cls.root / path).write_text(text)
        subprocess.run(["git", "init", "-q"], cwd=cls.root, check=True)
        subprocess.run(["git", "add", "-A"], cwd=cls.root, check=True)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_generator(self, name):
        return GENERATORS[name](self.root, {})

    def test_ci_pipelines_list_triggers_jobs_and_what_each_waits_for(self):
        body, sources = self.run_generator("ci-pipelines")
        self.assertIn("runs on push on `main`; pull_request", body)
        self.assertIn("| `test` |  | ubuntu-latest | `lint` |", body)
        self.assertIn("lint[lint] --> test[test]", body)
        self.assertIn(".github/workflows/*.yml", sources)

    def test_tasks_list_recipes_with_the_first_sentence_of_their_comment(self):
        body, sources = self.run_generator("tasks")
        self.assertIn("| `default` | List the recipes. |", body)
        self.assertIn("| `test` | Run the tests. |", body)
        self.assertIn("| `build` | `vite build` |", body)
        self.assertEqual(sources, ["justfile", "web/package.json"])

    def test_the_schema_follows_migrations_in_order_and_draws_the_references(self):
        body, sources = self.run_generator("database-schema")
        self.assertIn("2 tables", body)
        self.assertIn("accounts ||--o{ orders : account_id", body)
        self.assertIn("| `email` | `text` | required | the login |", body)
        self.assertIn("| `account_id` | `uuid` | FK accounts, required | — |", body)
        self.assertIn("| `total` | `numeric(10,2)` | — | — |", body)
        self.assertNotIn("demo", body, "SQL outside the migrations is not the schema")
        self.assertEqual(sources, ["app/migrations/versions/0001.py", "app/migrations/versions/0002.py"])

    def test_compose_services_show_images_ports_and_start_order(self):
        body, sources = self.run_generator("compose-services")
        self.assertIn("| `api` | built from `.` | `8000:8000` | `db` |", body)
        self.assertIn("| `db` | postgres:16 | — | — |", body)
        self.assertIn("api[api] --> db[db]", body)
        self.assertEqual(sources, ["compose.yaml"])


if __name__ == "__main__":
    unittest.main()
