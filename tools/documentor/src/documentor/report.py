"""How a guide was made, and what would make it better.

`build_report` is the site's "How this guide was made" page, generated at every site build: what
detection found in the repository and the evidence for each trait, every page with its kind, how it
was made, who wrote and evaluated it, and how many sources it cites, the architecture views, the
site's other sections, and the HELIX artifacts that would improve the guide.

`gaps` is that last list on its own (also in `documentor status`): a written page records each
HELIX artifact it had to be written without (`<!-- helix:gap artifact:<type> -->`), and the list
groups them by artifact, so the artifact that would improve the most pages comes first.

`shots` photographs a built site: each page on a desktop, in dark, and at phone width, with an
index page to look through them.
"""

from __future__ import annotations

import html
import subprocess
from pathlib import Path

from documentor import check
from documentor.lib import PagePlan, incidental, load_traits, repository_files


def gaps(pages: list[PagePlan]) -> list[tuple[str, list[str]]]:
    """(the artifact, the pages written without it), the artifact that would improve most pages first."""
    by_artifact: dict[str, list[str]] = {}
    for page in pages:
        for gap in page.entry.get("gaps") or []:
            by_artifact.setdefault(gap.removeprefix("artifact:"), []).append(page.key)
    return sorted(by_artifact.items(), key=lambda kv: (-len(kv[1]), kv[0]))


def gap_lines(pages: list[PagePlan]) -> list[str]:
    found = gaps(pages)
    if not found:
        return []
    lines = ["", "Artifacts that would improve the guide (ask HELIX for each; the pages listed are then rewritten from it):"]
    lines += [f"  {artifact:24} {len(keys)} page{'s' if len(keys) != 1 else ''}: {', '.join(keys)}" for artifact, keys in found]
    return lines


def _cell(text: str) -> str:
    return str(text).replace("|", "\\|")


def build_report(root: Path, config: dict, pages: list[PagePlan], sections: list[dict]) -> str:
    """The body of "How this guide was made" (Markdown, without its title)."""
    from documentor import detect

    lines = ["Every page of this site was made from the repository by documentor, and is rebuilt when the "
             "repository changes. This page says how each one was made.", "", "## What the repository is", ""]
    files = [f for f in repository_files(root) if not incidental(f)]
    chosen = set((config.get("publish") or {}).get("traits") or [])
    scores = [s for s in (detect.score(root, files, t) for t in load_traits(config, root)) if s.matches]
    lines += ["| Trait | Chosen | Confidence | Evidence |", "|---|---|---:|---|"]
    for s in sorted(scores, key=lambda s: -s.confidence):
        evidence = "; ".join(f"`{m.signal}`" for m in s.matches)
        lines.append(f"| {s.trait.get('title', s.trait['id'])} | {'yes' if s.trait['id'] in chosen else 'no'} | "
                     f"{s.confidence:.2f} | {_cell(evidence)} |")
    lines += ["", "## The pages", "", "| Reader | Page | Kind | Made by | Evaluated by | Sources | State |",
              "|---|---|---|---|---|---:|---|"]
    for page in pages:
        made = {"generated": f"generator `{page.generator or page.command}`", "delegated": page.tool or "its tool",
                "existing": "a person (adopted)", "written": "an agent"}.get(page.work, page.work)
        evaluated, count = "—", "—"
        path = root / page.path
        if path.is_file() and page.work != "delegated":
            parsed = check.parse_page(path)
            if parsed is not None:
                count = str(len(parsed.sources))
                if parsed.meta.get("written"):
                    made = parsed.meta["written"]
                reviewed = parsed.meta.get("reviewed", "")
                evaluated = reviewed.split("/")[1] if reviewed.count("/") >= 2 else ("—" if page.work == "generated" else "not yet")
        lines.append(f"| {page.audience} | {_cell(page.title)} | {page.kind} | {_cell(made)} | {evaluated} | {count} | "
                     f"{page.entry.get('state', '?')} |")
    from documentor.architecture.model import default_model, load

    model_path = default_model(root)
    if model_path.is_file():
        model = load(model_path)
        lines += ["", "## The architecture views", "",
                  f"Drawn from `{model_path.relative_to(root).as_posix()}`: {len(model.elements)} parts and "
                  f"{len(model.relations)} connections, each citing the file that shows it.", "",
                  "| View | Type | Parts |", "|---|---|---:|"]
        lines += [f"| {_cell(v.title or v.id)} | {v.type}{' (presented)' if v.present else ''} | {len(v.elements)} |"
                  for v in model.views.values()]
    extra = [s for s in sections if s.get("id") not in {p.audience for p in pages}]
    if extra:
        lines += ["", "## The other sections", ""] + [f"- {s['title']}: {s.get('reader', '')}" for s in extra]
    found = gaps(pages)
    if found:
        lines += ["", "## What would improve this guide", "",
                  "These pages were written without a HELIX artifact that would hold what they explain. "
                  "Writing the artifact (ask HELIX for it) lets the pages be rewritten from it.", "",
                  "| Artifact | Pages written without it |", "|---|---|"]
        lines += [f"| `{a}` | {', '.join(keys)} |" for a, keys in found]
    return "\n".join(lines) + "\n"


VIEWS = ("desktop", "dark", "phone")


def shots(public: Path, out: Path, limit: int = 40) -> int:
    """Screenshots of the built pages (desktop, dark, phone at 390px) under `out`, with
    `out/index.html`, and a report of any page wider than its screen. Rendered by `js/shots.mjs`
    through playwright-core, which installs into the documentor cache with Eraser."""
    import shutil

    from documentor.deliverable import eraser_env

    if not (shutil.which("node") and shutil.which("npm")):
        print("documentor site --shots: needs node and npm")
        return 3
    try:
        env = eraser_env()
    except (RuntimeError, OSError) as error:
        print(f"documentor site --shots: {error}")
        return 3
    pages = sorted(p for p in public.rglob("index.html") if "presentations" not in p.parts)[:limit]
    out.mkdir(parents=True, exist_ok=True)
    script = Path(__file__).parent / "js" / "shots.mjs"
    done = subprocess.run(["node", str(script), str(out), str(public), *map(str, pages)], env=env,
                          capture_output=True, text=True, check=False)
    if done.returncode:
        print(f"documentor site --shots: {done.stderr.strip()[:400]}")
        return 1
    overflow = [line for line in done.stdout.splitlines() if line.startswith("overflow ")]
    rows = []
    for page in pages:
        name = page.parent.relative_to(public).as_posix().replace("/", "-") or "home"
        cells = "".join(f'<figure><a href="{name}.{v}.png"><img src="{name}.{v}.png" loading="lazy" alt="{html.escape(name)}, {v}"></a>'
                        f"<figcaption>{v}</figcaption></figure>" for v in VIEWS)
        rows.append(f"<section><h2>{html.escape(name)}</h2><div class=row>{cells}</div></section>")
    (out / "index.html").write_text(
        "<!doctype html><meta charset=utf-8><title>Site screenshots</title><style>body{font:15px system-ui;margin:24px}"
        ".row{display:flex;gap:16px;align-items:flex-start;flex-wrap:wrap}figure{margin:0}img{max-height:340px;border:1px solid #ccc}"
        "</style><h1>Site screenshots</h1>" + "".join(f"<p>{html.escape(o)}</p>" for o in overflow) + "".join(rows), encoding="utf-8")
    print(f"took {len(pages) * len(VIEWS)} screenshots of {len(pages)} pages into {out}")
    for line in overflow:
        print(f"  {line}")
    return 1 if overflow else 0
