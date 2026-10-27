"""The project's visuals as `umf.visual` documents, drawn by `@ux-builder/visuals`.

With `publish.visuals` in `.helix.yml`, documentor projects each view of the architecture model
into a `umf.visual` 1.0 document (DocumentDrivenDX/umf CONTRACT-083) and has ux-builder's renderer
draw it in the project's theme (HELIX workflows/references/visuals.md):

| Model view | Visual |
|---|---|
| `flowchart` | `flow/network` (`flow/pipeline` when the view says `form = "pipeline"`), with its numbered steps |
| `deployment` | `flow/zoned`; walked by its `journey` when the view is `present = true` |
| `field-guide` | `flow/lanes`, with the numbered steps and what the view leaves out |
| `journey` | `sequence/lifelines` |
| `stack` | `structure/stack` |
| `cast` | none: what each piece does is a table |

    publish:
      visuals: ux-builder                # or {renderer: ux-builder, command: "node …/cli.mjs"}

`documentor visuals [--root DIR] [--check]` writes each document to `<publish.out>/visuals/<id>.visual.json`
and draws it beside: `<id>.svg` (colors as the theme's CSS variables, so an inline copy follows the
page's theme and the reader's light or dark setting), `<id>.mmd` (Mermaid, for the Markdown record),
and, where they apply, `<id>.plate.html` and `<id>.presentation.html`. `--check` writes nothing and
fails when a document no longer matches the model. A page shows a visual with a fenced block,
```` ```visual id=<id> ````; the site documentor builds draws it inline.

The renderer is `@ux-builder/visuals`: `publish.visuals.command` (or `DOCUMENTOR_VISUALS`) names its
command; otherwise documentor installs the pinned release into its cache, as it does for Eraser.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import tomllib
from pathlib import Path

from documentor.lib import config_of, find_root, publish_out

VOCABULARY = "1.0.0"
UMF = "0.10.0"
RENDERER = ("@ux-builder/visuals", "0.1.0")  # the release documentor is tested against

# A view's question when it names none: the reader's question its form answers (visuals.md).
QUESTIONS = {
    "network": "What are the parts, and what connects them?",
    "pipeline": "What stages does this go through, in order?",
    "zoned": "Where does each part run, and what travels between them?",
    "lanes": "What is a newcomer's first map of the system?",
    "lifelines": "What happens, step by step?",
    "stack": "Where does each piece sit?",
}


def settings(config: dict) -> dict:
    """`publish.visuals` as a mapping; empty when the project has not turned visuals on."""
    raw = (config.get("publish") or {}).get("visuals")
    if not raw:
        return {}
    return {"renderer": raw} if isinstance(raw, str) else dict(raw)


def enabled(config: dict) -> bool:
    return bool(settings(config))


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _clean(value):
    if isinstance(value, dict):
        return {k: _clean(v) for k, v in value.items() if v not in (None, [], {}, "")}
    if isinstance(value, list):
        return [_clean(v) for v in value]
    return value


def _sentence(text: str) -> str:
    return text[:1].upper() + text[1:] if text else text


class Projection:
    """One architecture model, projected view by view."""

    def __init__(self, root: Path, path: Path):
        self.root, self.path = root, path
        self.text = path.read_text(encoding="utf-8")
        self.data = tomllib.loads(self.text)
        self.system = (self.data.get("system") or {}).get("id", "system")
        self.elements = {e["id"]: e for e in self.data.get("element", [])}
        self.relations = self.data.get("relation", [])
        self.views = {v["id"]: v for v in self.data.get("view", [])}
        self.journeys = {j["id"]: j for j in self.data.get("journey", [])}
        self.zone_captions = {z["name"]: z.get("caption") for z in self.data.get("zone", [])}
        self.prefix = slug(self.system)

    # --- parts -----------------------------------------------------------------------------------

    def source(self, view: str) -> dict:
        return {"path": self.path.relative_to(self.root).as_posix(), "view": view,
                "digest": "sha256:" + hashlib.sha256(self.text.encode("utf-8")).hexdigest()}

    def role(self, element: dict) -> str:
        kind, owner = element["kind"], element.get("owner")
        if kind == "person" or owner == "person":
            return "actor"
        if kind == "store":
            return "store"
        if owner == "platform":
            return "platform"
        if kind in ("system", "container") and owner in (None, self.system):
            return "own"
        return "external" if kind == "external" else "platform"

    def node(self, ident: str, **extra) -> dict:
        e = self.elements[ident]
        node = {"id": ident, "label": e["name"], "detail": e.get("detail"), "role": self.role(e),
                "status": e.get("status"), **extra,
                "evidence": [{"path": x["path"], "contains": x["contains"]} for x in e.get("evidence", [])]}
        return _clean(node)

    def edges(self, ids: list[str]) -> list[dict]:
        out, seen = [], set()
        for r in self.relations:
            if r["from"] in ids and r["to"] in ids:
                ident = f"{r['from']}--{r['to']}"
                while ident in seen:
                    ident += "-2"
                seen.add(ident)
                edge = {"id": ident, "from": r["from"], "to": r["to"], "label": r.get("label"), "why": r.get("why"),
                        "status": r.get("status"),
                        "kind": "return" if r.get("dashed") or r.get("kind") == "return" else None,
                        "evidence": [{"path": x["path"], "contains": x["contains"]} for x in r.get("evidence", [])]}
                out.append(_clean(edge))
        return out

    def relation_steps(self, edges: list[dict]) -> list[dict]:
        by_pair = {(e["from"], e["to"]): e["id"] for e in edges}
        numbered = sorted((r for r in self.relations if "step" in r and (r["from"], r["to"]) in by_pair),
                          key=lambda r: r["step"])
        steps = [{"id": f"s{r['step']}", "title": _sentence(r["label"]), "caption": r.get("note"),
                  "focus": [by_pair[(r["from"], r["to"])]]} for r in numbered]
        steps += [{"id": f"throughout-{slug(r['label'])}", "title": _sentence(r["label"]), "caption": r.get("note"),
                   "focus": [by_pair[(r["from"], r["to"])]], "when": "throughout"}
                  for r in self.relations if r.get("throughout") and (r["from"], r["to"]) in by_pair]
        return [_clean(s) for s in steps]

    def left_out(self, ids: list[str]) -> list[str]:
        left: dict[str, list[str]] = {}
        for e in self.elements.values():
            if e["id"] not in ids:
                left.setdefault(e.get("layer") or "elsewhere", []).append(e["name"])
        text = "This is a conceptual map, not a deployment topology."
        if left:
            text += " Left out on purpose, by layer: " + "; ".join(f"{k} ({', '.join(v)})" for k, v in left.items()) + "."
        unreal = [f"{e['name']} ({e['status']})" for e in self.elements.values() if e.get("status", "built") != "built"]
        if unreal:
            text += f" Not real yet: {', '.join(unreal)}."
        return [text]

    def base(self, view: dict, kind: str, form: str, ident: str | None = None) -> dict:
        return {"id": ident or f"{self.prefix}-{slug(view['id'])}", "kind": kind, "form": form, "title": view.get("title"),
                "question": view.get("question") or QUESTIONS[form], "takeaway": view.get("takeaway"),
                "audience": "developer", "source": self.source(view["id"])}

    # --- views -----------------------------------------------------------------------------------

    def network(self, view: dict, form: str) -> dict:
        ids = list(view["elements"])
        groups, member = [], {}
        for g in view.get("group", []):
            groups.append({"id": g["id"], "label": g["label"], "role": "lane" if form == "lanes" else "boundary"})
            member.update({e: g["id"] for e in g["elements"]})
        edges = self.edges(ids)
        visual = {**self.base(view, "flow", form), "groups": groups,
                  "nodes": [self.node(i, **({"group": member[i]} if i in member else {})) for i in ids], "edges": edges}
        visual["steps"] = self.relation_steps(edges)  # numbered relations, when the view has them
        if form == "lanes":
            visual["omissions"] = self.left_out(ids)
        return visual

    def zoned(self, view: dict) -> dict:
        ids = list(view["elements"])
        tiers: dict[str, int] = {}
        for i in ids:
            e = self.elements[i]
            tiers[e["zone"]] = min(tiers.get(e["zone"], 99), e.get("tier", 1))
        groups = [{"id": "zone-" + slug(z), "label": z, "detail": self.zone_captions.get(z), "role": "zone", "tier": t}
                  for z, t in tiers.items()]
        edges = self.edges(ids)
        visual = {**self.base(view, "flow", "zoned"), "groups": groups,
                  "nodes": [self.node(i, group="zone-" + slug(self.elements[i]["zone"])) for i in ids], "edges": edges}
        journey = self.journeys.get(view.get("journey", "")) if view.get("present") else None
        if journey:
            by_pair = {(e["from"], e["to"]): e["id"] for e in edges}
            visual["steps"] = [{"id": f"s{n}", "title": _sentence(s["label"]),
                                "focus": [by_pair.get((s["from"], s["to"])) or by_pair.get((s["to"], s["from"])) or s["to"]]}
                               for n, s in enumerate(journey["step"], 1)]
        return visual

    def sequence(self, view: dict) -> dict | None:
        journey = self.journeys.get(view.get("journey") or view["id"])
        if not journey:
            return None
        order: list[str] = []
        for s in journey["step"]:
            for end in (s["from"], s["to"]):
                if end not in order:
                    order.append(end)
        participants = [{k: v for k, v in self.node(i).items() if k not in ("evidence", "group")} for i in order]
        messages = [{"id": f"m{n}", "from": s["from"], "to": s["to"], "label": s["label"],
                     "kind": "return" if order.index(s["to"]) < order.index(s["from"]) else "call"}
                    for n, s in enumerate(journey["step"], 1)]
        named = {"id": view["id"], "title": view.get("title") or journey.get("title"),
                 "takeaway": view.get("takeaway") or journey.get("takeaway"), "question": view.get("question")}
        return {**self.base(named, "sequence", "lifelines"),
                "sequence": {"participants": participants, "messages": messages},
                "steps": [{"id": f"s{n}", "title": _sentence(m["label"]), "focus": [m["id"]]}
                          for n, m in enumerate(messages, 1)]}

    def stack(self, view: dict) -> dict:
        ids = list(view["elements"])
        layers: list[str] = []
        for e in self.data.get("element", []):
            if e["id"] in ids and e.get("layer") and e["layer"] not in layers:
                layers.append(e["layer"])
        nodes = [self.node(i, layer="layer-" + slug(self.elements[i].get("layer") or "other")) for i in ids]
        return {**self.base(view, "structure", "stack"), "nodes": nodes,
                "structure": {"layers": [{"id": "layer-" + slug(l), "label": l} for l in layers]}}

    def visual(self, view: dict) -> dict | None:
        kind = view.get("type", "flowchart")
        if kind == "flowchart":
            form = view.get("form", "network")  # a view that is a sequence of stages names `form = "pipeline"`
            return self.network(view, form if form in ("network", "pipeline") else "network")
        if kind == "deployment":
            return self.zoned(view)
        if kind == "field-guide":
            return self.network(view, "lanes")
        if kind == "journey":
            return self.sequence(view)
        if kind == "stack":
            return self.stack(view)
        return None  # cast and anything else: a table, not a picture


def documents(root: Path, config: dict) -> dict[str, dict]:
    """Every visual the project's sources draw, as umf.visual documents keyed by id."""
    from documentor.architecture.model import default_model

    out: dict[str, dict] = {}
    path = default_model(root)
    if not path.is_file():
        return out
    projection = Projection(root, path)
    for view in projection.views.values():
        visual = projection.visual(view)
        if visual:
            visual = _clean(visual)
            out[visual["id"]] = {"umf": UMF, "id": "visual:" + visual["id"],
                                 "vocabularies": {"umf.visual": {"version": VOCABULARY}},
                                 "extensions": {"umf.visual": visual}, "modules": []}
    return out


def directory(root: Path, config: dict) -> Path:
    return root / publish_out(config) / "visuals"


def serialize(document: dict) -> str:
    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


# --- drawing --------------------------------------------------------------------------------------

def renderer_command(config: dict) -> list[str]:
    """The renderer's command: the project's, the environment's, or the pinned release from the cache."""
    named = os.environ.get("DOCUMENTOR_VISUALS") or settings(config).get("command")
    if named:
        return shlex.split(named)
    from documentor.deliverable import npm_modules

    modules = npm_modules(*RENDERER)
    return ["node", str(modules / RENDERER[0] / "cli.mjs")]


def draw(root: Path, config: dict, files: list[Path], out: Path) -> tuple[int, list[str]]:
    """Draw the documents into `out`; (exit status, problems: refusals and layout findings)."""
    from documentor import theme as project_theme

    chosen = project_theme.load(root, config)
    appearance = "both" if chosen.dark else "light"
    try:
        command = renderer_command(config)
    except (RuntimeError, OSError) as error:
        return 3, [f"the visuals renderer is not available: {error}"]
    argv = [*command, "render", *map(str, files), "--theme", chosen.name, "--appearance", appearance,
            "--output", "all", "--check", "--out", str(out)]
    # The renderer reads the theme by name from its own @ux-builder/tokens.
    done = subprocess.run(argv, cwd=root, capture_output=True, text=True, check=False)
    try:
        summary = json.loads(done.stdout)
    except json.JSONDecodeError:
        return 3, [f"the visuals renderer failed: {(done.stderr or done.stdout).strip()[:400]}"]
    problems = [f"{r.get('id') or r['file']}: {r['code']}: {r['message']}" for r in summary.get("refused", [])]
    for rendered in summary.get("rendered", []):
        problems += [f"{rendered['id']}: {f.get('code', f.get('rule', 'finding'))}: {f.get('message', f)}"
                     for f in rendered.get("findings", [])]
    return (1 if problems else 0), problems


def write(root: Path, config: dict, render: bool = True) -> tuple[int, list[str]]:
    """Write every document, remove ones no source draws any more, and draw them."""
    docs = documents(root, config)
    out = directory(root, config)
    out.mkdir(parents=True, exist_ok=True)
    for stale in out.glob("*.visual.json"):
        if stale.name.removesuffix(".visual.json") not in docs:
            for path in out.glob(stale.name.removesuffix(".visual.json") + ".*"):
                path.unlink()
    files = []
    for ident, document in docs.items():
        path = out / f"{ident}.visual.json"
        path.write_text(serialize(document), encoding="utf-8")
        files.append(path)
    if not render or not files:
        return 0, []
    return draw(root, config, files, out)


def check(root: Path, config: dict) -> list[str]:
    """The documents that no longer match their sources (or are missing, or are left over)."""
    docs = documents(root, config)
    out = directory(root, config)
    problems = []
    for ident, document in docs.items():
        path = out / f"{ident}.visual.json"
        if not path.is_file():
            problems.append(f"visual {ident} is missing; run `documentor visuals`")
        elif path.read_text(encoding="utf-8") != serialize(document):
            problems.append(f"visual {ident} is stale: its source changed; run `documentor visuals`")
        elif not (out / f"{ident}.svg").is_file():
            problems.append(f"visual {ident} is not drawn; run `documentor visuals`")
    for left in out.glob("*.visual.json") if out.is_dir() else []:
        if left.name.removesuffix(".visual.json") not in docs:
            problems.append(f"visual {left.name.removesuffix('.visual.json')} has no source any more; run `documentor visuals`")
    return problems


# --- embedding --------------------------------------------------------------------------------------

VISUAL_BLOCK = re.compile(r"^```visual\b[^\n]*\bid=([a-z0-9-]+)[^\n]*\n.*?^```[ \t]*$", re.M | re.S)


def text_equivalent(document: dict) -> str:
    """The visual's content as a list, for a reader who cannot see it."""
    v = document["extensions"]["umf.visual"]
    names = {n["id"]: n["label"] for n in v.get("nodes", [])}
    if v.get("sequence"):
        names.update({p["id"]: p["label"] for p in v["sequence"]["participants"]})
        lines = [f"{n}. {names.get(m['from'], m['from'])} → {names.get(m['to'], m['to'])}: {m['label']}"
                 for n, m in enumerate(v["sequence"]["messages"], 1)]
        return "\n".join(lines)
    lines = [f"- {n['label']}" + (f": {n['detail']}" if n.get("detail") else "") for n in v.get("nodes", [])]
    lines += [f"- {names.get(e['from'], e['from'])} → {names.get(e['to'], e['to'])}" + (f": {e['label']}" if e.get("label") else "")
              for e in v.get("edges", [])]
    return "\n".join(lines)


def figure(out: Path, ident: str) -> str | None:
    """The inline figure for a site: the SVG, the takeaway as its caption, the text equivalent."""
    svg, doc = out / f"{ident}.svg", out / f"{ident}.visual.json"
    if not (svg.is_file() and doc.is_file()):
        return None
    document = json.loads(doc.read_text(encoding="utf-8"))
    visual = document["extensions"]["umf.visual"]
    caption = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", visual.get("takeaway") or visual.get("title") or "")
    import html

    return (f'<figure class="visual" id="visual-{ident}">\n{svg.read_text(encoding="utf-8").strip()}\n'
            + (f"<figcaption>{html.escape(caption)}</figcaption>\n" if caption else "")
            + f'<details class="visual-text"><summary>The picture in words</summary>\n\n{text_equivalent(document)}\n\n</details>\n'
            + "</figure>")


VIEW_MARKERS = re.compile(r"<!-- architecture-view: (\S+) -->.*?<!-- /architecture-view -->", re.S)


def by_view(out: Path) -> dict[str, str]:
    """Each drawn visual's id, by the model view it was drawn from."""
    found = {}
    for path in out.glob("*.visual.json") if out.is_dir() else []:
        visual = json.loads(path.read_text(encoding="utf-8"))["extensions"]["umf.visual"]
        view = (visual.get("source") or {}).get("view")
        if view:
            found[view] = visual["id"]
    return found


def embed(body: str, out: Path) -> str:
    """For a site: each fenced ```visual id=…``` block, and each generated architecture view between its
    markers, becomes the drawn visual inline. The Markdown keeps its Mermaid for readers without the site."""
    body = VISUAL_BLOCK.sub(lambda m: figure(out, m.group(1)) or m.group(0), body)
    views = by_view(out)
    return VIEW_MARKERS.sub(lambda m: (figure(out, views[m.group(1)]) if m.group(1) in views else None) or m.group(0), body)


# --- the command --------------------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="documentor visuals", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--check", action="store_true", help="write nothing; fail when a visual no longer matches its source")
    parser.add_argument("--no-draw", action="store_true", help="write the documents but do not draw them")
    args = parser.parse_args(argv)
    root = find_root(args.root or Path.cwd())
    config = config_of(root)
    if args.check:
        problems = check(root, config)
        for p in problems:
            print(f"BLOCKING  {p}")
        print(f"{'FAIL' if problems else 'OK'}: {len(documents(root, config))} visuals")
        return 1 if problems else 0
    status, problems = write(root, config, render=not args.no_draw)
    for p in problems:
        print(p, file=sys.stderr)
    print(f"wrote {len(documents(root, config))} visuals to {directory(root, config).relative_to(root)}"
          + ("" if status == 0 else f" ({len(problems)} problems)"))
    return status
