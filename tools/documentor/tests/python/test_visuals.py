"""The model's views as umf.visual documents: the mapping, the check, the drawing, and the site."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest

from documentor import visuals

MODEL = textwrap.dedent('''
    [system]
    id = "shop"

    [[element]]
    id = "buyer"
    name = "Buyer"
    kind = "person"
    status = "built"
    tier = 1
    zone = "People"
    layer = "People"
    evidence = [{ path = "app.py", contains = "def main" }]

    [[element]]
    id = "api"
    name = "API"
    detail = "FastAPI"
    kind = "container"
    status = "built"
    tier = 2
    zone = "Apps"
    layer = "Shop"
    evidence = [{ path = "app.py", contains = "def main" }]

    [[element]]
    id = "db"
    name = "Database"
    kind = "store"
    status = "decided"
    tier = 3
    zone = "Data"
    layer = "Data"
    evidence = [{ path = "app.py", contains = "def main" }]

    [[relation]]
    from = "buyer"
    to = "api"
    label = "places an order"
    status = "built"
    step = 1
    evidence = [{ path = "app.py", contains = "def main" }]

    [[relation]]
    from = "api"
    to = "db"
    label = "stores it"
    why = "orders outlive a request"
    status = "decided"
    step = 2
    evidence = [{ path = "app.py", contains = "def main" }]

    [[journey]]
    id = "order"
    title = "An order"
    [[journey.step]]
    from = "buyer"
    to = "api"
    label = "places an order"
    [[journey.step]]
    from = "api"
    to = "db"
    label = "stores it"

    [[view]]
    id = "context"
    title = "The shop"
    question = "Who uses the shop, and what does it keep?"
    elements = ["buyer", "api", "db"]

    [[view]]
    id = "deployment"
    type = "deployment"
    elements = ["buyer", "api", "db"]
    journey = "order"
    present = true

    [[view]]
    id = "order"
    type = "journey"
    journey = "order"
    elements = []

    [[view]]
    id = "stack"
    type = "stack"
    elements = ["buyer", "api", "db"]

    [[view]]
    id = "cast"
    type = "cast"
    elements = ["buyer", "api", "db"]
''')

# A stand-in for `ux-builder-visuals render`: writes an SVG per document and prints the summary.
RENDERER = textwrap.dedent('''
    import json, pathlib, sys
    args = sys.argv[2:]
    out = pathlib.Path(args[args.index("--out") + 1])
    files = [a for a in args if a.endswith(".visual.json")]
    rendered = []
    for f in files:
        ident = json.load(open(f))["extensions"]["umf.visual"]["id"]
        (out / f"{ident}.svg").write_text(f'<svg xmlns="http://www.w3.org/2000/svg" data-visual="{ident}"><title>{ident}</title></svg>')
        rendered.append({"file": f, "id": ident, "files": [], "warnings": [], "findings": []})
    print(json.dumps({"rendered": rendered, "refused": [], "theme": args[args.index("--theme") + 1]}))
''')


def project(root: Path, visuals_setting: str | None = None) -> None:
    (root / "app.py").write_text("def main():\n    pass\n")
    model = root / "docs/helix/02-design/architecture-model.toml"
    model.parent.mkdir(parents=True)
    model.write_text(MODEL)
    (root / "renderer.py").write_text(RENDERER)
    command = f"{sys.executable} {root / 'renderer.py'}"
    publish = f"publish:\n  out: docs/guide\n  visuals: {{renderer: ux-builder, command: \"{command}\"}}\n"
    (root / ".helix.yml").write_text("flows:\n  - id: helix\n    root: docs/helix/\n" + publish)
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)


def config(root: Path) -> dict:
    from documentor.lib import config_of

    return config_of(root)


class ProjectionTests(unittest.TestCase):
    def test_each_view_becomes_its_kind_and_form_and_cast_stays_a_table(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            project(root)
            docs = visuals.documents(root, config(root))
            forms = {i: (d["extensions"]["umf.visual"]["kind"], d["extensions"]["umf.visual"]["form"]) for i, d in docs.items()}
            self.assertEqual(forms, {"shop-context": ("flow", "network"), "shop-deployment": ("flow", "zoned"),
                                     "shop-order": ("sequence", "lifelines"), "shop-stack": ("structure", "stack")})
            context = docs["shop-context"]["extensions"]["umf.visual"]
            self.assertEqual(context["question"], "Who uses the shop, and what does it keep?")
            roles = {n["id"]: (n["role"], n["status"]) for n in context["nodes"]}
            self.assertEqual(roles, {"buyer": ("actor", "built"), "api": ("own", "built"), "db": ("store", "decided")})
            self.assertEqual([s["focus"] for s in context["steps"]], [["buyer--api"], ["api--db"]])
            self.assertEqual(context["edges"][1]["why"], "orders outlive a request")
            self.assertEqual(context["source"]["path"], "docs/helix/02-design/architecture-model.toml")
            self.assertTrue(context["source"]["digest"].startswith("sha256:"))
            deployment = docs["shop-deployment"]["extensions"]["umf.visual"]
            self.assertEqual([(g["label"], g["tier"]) for g in deployment["groups"]], [("People", 1), ("Apps", 2), ("Data", 3)])
            self.assertEqual(len(deployment["steps"]), 2, "a presented deployment view is walked by its journey")
            order = docs["shop-order"]["extensions"]["umf.visual"]["sequence"]
            self.assertEqual([m["kind"] for m in order["messages"]], ["call", "call"])
            self.assertEqual(docs["shop-order"]["vocabularies"], {"umf.visual": {"version": "1.0.0"}})


class WriteCheckEmbedTests(unittest.TestCase):
    def test_documents_are_written_drawn_checked_and_embedded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            project(root)
            cfg = config(root)
            self.assertEqual(visuals.check(root, cfg)[0], "visual shop-context is missing; run `documentor visuals`")
            status, problems = visuals.write(root, cfg)
            self.assertEqual((status, problems), (0, []))
            out = root / "docs/guide/visuals"
            self.assertTrue((out / "shop-deployment.svg").is_file())
            self.assertEqual(visuals.check(root, cfg), [])
            model = root / "docs/helix/02-design/architecture-model.toml"
            model.write_text(model.read_text().replace('label = "stores it"\nwhy', 'label = "keeps it"\nwhy'))
            self.assertIn("shop-context is stale", " ".join(visuals.check(root, cfg)))
            body = ("Text.\n\n```visual id=shop-stack\nsource: architecture-model.toml#stack\n```\n\n"
                    "<!-- architecture-view: deployment -->\n```mermaid\nflowchart LR\n```\n<!-- /architecture-view -->\n"
                    "\n```visual id=absent\nsource: x\n```\n")
            shown = visuals.embed(body, out)
            self.assertIn('<figure class="visual" id="visual-shop-stack">', shown)
            self.assertIn('<figure class="visual" id="visual-shop-deployment">', shown)
            self.assertNotIn("```mermaid", shown, "a generated view is drawn, not left as Mermaid, on the site")
            self.assertIn("```visual id=absent", shown, "a visual with nothing drawn is left as it was")
            self.assertIn("<summary>The picture in words</summary>", shown)
            self.assertIn("- Buyer → API: places an order", shown)

    def test_without_the_setting_nothing_changes(self):
        self.assertFalse(visuals.enabled({"publish": {}}))
        self.assertEqual(visuals.settings({"publish": {"visuals": "ux-builder"}}), {"renderer": "ux-builder"})


if __name__ == "__main__":
    unittest.main()
