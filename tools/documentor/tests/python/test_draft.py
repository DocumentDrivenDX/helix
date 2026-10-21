"""A first architecture model is drafted from what the repository's files declare, and passes the
model's own check as written."""
from pathlib import Path
import subprocess
import tempfile
import unittest

from documentor.architecture import draft
from documentor.architecture import model as am

FILES = {
    ".helix.yml": "flows:\n  - id: helix\n    root: docs/helix/\n",
    "compose.yaml": "services:\n  api:\n    build: .\n    ports: ['8000:8000']\n    depends_on: [db]\n"
                    "  db:\n    image: postgres:16\n",
    "pyproject.toml": '[project]\nname = "shop"\ndependencies = [\n  "fastapi>=0.110",\n]\n',
    "web/package.json": '{"name": "shop-web", "dependencies": {"react": "^19.0.0"}}',
    "web/src/api.ts": 'export const orders = () => fetch("/api/orders");\n',
    "alembic.ini": "[alembic]\nscript_location = migrations\n",
    "databricks.yml": "bundle:\n  name: shop\ninclude:\n  - resources/*.yml\n",
    "resources/nightly.yml": "resources:\n  jobs:\n    nightly_refresh:\n      name: nightly\n",
    "examples/demo/package.json": '{"name": "demo", "dependencies": {"vue": "3"}}',
}


def repository(root: Path) -> None:
    for path, text in FILES.items():
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_text(text)
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)


class DraftTests(unittest.TestCase):
    def test_the_draft_names_each_declared_part_with_its_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            repository(root)
            drafted = draft.draft_model(root)
            parts = {e.id: (e.kind, e.detail) for e in drafted.elements.values()}
            self.assertEqual(parts["db"], ("store", "postgres"))
            self.assertEqual(parts["web"], ("container", "React frontend"))
            self.assertEqual(parts["shop"][1], "FastAPI API")
            self.assertEqual(parts["nightly-refresh"], ("container", "Databricks job"))
            self.assertEqual(parts["database"][0], "store")
            self.assertEqual(parts["user"][0], "person")
            self.assertNotIn("demo", parts, "an example is not part of the system")
            edges = {(r.source, r.target, r.label) for r in drafted.relations}
            self.assertIn(("api", "db", "depends on"), edges)
            self.assertIn(("web", "shop", "calls the API"), edges)
            self.assertIn(("nightly-refresh", "databricks", "runs on"), edges)
            self.assertIn(("user", "web", "uses"), edges)

    def test_the_written_draft_passes_the_model_check_and_init_proposes_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            repository(root)
            self.assertEqual(draft.main(["--root", str(root), "--write"]), 0)
            path = am.default_model(root)
            model = am.load(path)
            self.assertEqual(am.model_problems(model, root), [])
            self.assertEqual(model.views["deployment"].type, "deployment")
            self.assertEqual(draft.main(["--root", str(root), "--write"]), 2, "an existing model is not replaced")

    def test_a_bundle_with_many_jobs_draws_them_as_one_part(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            jobs = "".join(f"    job_{n}:\n      name: j{n}\n" for n in range(draft.COLLAPSE + 2))
            FILES_MANY = {".helix.yml": FILES[".helix.yml"], "databricks.yml": FILES["databricks.yml"],
                          "resources/jobs.yml": "resources:\n  jobs:\n" + jobs}
            for path, text in FILES_MANY.items():
                (root / path).parent.mkdir(parents=True, exist_ok=True)
                (root / path).write_text(text)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "add", "-A"], cwd=root, check=True)
            drafted = draft.draft_model(root)
            jobs_part = drafted.elements["shop-jobs"]
            self.assertEqual((jobs_part.detail, jobs_part.contains), (f"{draft.COLLAPSE + 2} jobs", "- resources/*.yml"))


if __name__ == "__main__":
    unittest.main()
