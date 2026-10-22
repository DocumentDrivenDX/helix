#!/usr/bin/env python3
"""Compose an estate view from the architecture models of several repositories
(HELIX workflows/references/architecture-model.md, "The estate").

    documentor estate check  --config estate.toml [--fetch]
    documentor estate render --config estate.toml --out PAGE.md [--fetch]
    documentor estate write  --config estate.toml --out PAGE.md [--fetch] [--agent CMD] [--model M] [--reviewer-model M] [--dry-run]

The config names each system in the estate, its repository, and where its model is. A model is
read from a local checkout (`path`) or, with --fetch, from the repository's default branch through
`gh api`. Every element and relation in a model cites that repository's code; the estate cites the
models, each at the commit it was read from.

`check` reports:
  missing-model    a system's model cannot be read                                    (blocking)
  no-system        a model names no [system], or its id is not the config's            (blocking)
  one-sided        A's model says A and B are connected and B's model does not say so  (blocking)
  unresolved       a model names a system the estate does not include                  (warning)

`render` writes a Markdown page: the landscape as Mermaid, the systems with their commits, and
each connection as both sides state it. `write` writes the explained estate: an agent writes, from a
digest of every model, where each system sits, what it does, a reason for every connection, the
journeys that cross systems, and the open questions; a second model checks the page against the same
digest; the page keeps the landscape and the generated tables as its evidence. Standard library only (Python 3.11 or later for tomllib; `tomli` on older ones).
Exit codes: 0 = no blocking findings, 1 = blocking findings, 2 = usage error.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    import tomllib
except ImportError:  # Python 3.10 and older
    import tomli as tomllib  # type: ignore[no-redef]

DEFAULT_MODEL = "docs/helix/02-design/architecture-model.toml"


@dataclass
class Claim:
    """One system's statement that it is connected to another, from its own model."""
    source: str
    target: str
    label: str
    status: str
    evidence: tuple[str, ...]


@dataclass
class System:
    id: str
    repo: str
    name: str = ""
    detail: str = ""
    status: str = ""
    commit: str = ""
    elements: int = 0
    claims: list[Claim] = field(default_factory=list)
    references: set[str] = field(default_factory=set)


@dataclass
class Findings:
    items: list[tuple[str, str, str]] = field(default_factory=list)  # (severity, check, message)

    def add(self, severity: str, check: str, message: str) -> None:
        self.items.append((severity, check, message))

    @property
    def blocking(self) -> int:
        return sum(1 for severity, _, _ in self.items if severity == "blocking")


# --- reading models ---------------------------------------------------------------------------

def gh(host: str, endpoint: str) -> dict:
    env = {"GH_HOST": host} if host else {}
    result = subprocess.run(["gh", "api", endpoint], capture_output=True, text=True, check=True,
                            env={**os.environ, **env})
    return json.loads(result.stdout)


def read_model(entry: dict, host: str, fetch: bool, cache: Path) -> tuple[str, str] | None:
    """(model text, commit) for one system, or None when it cannot be read."""
    model = entry.get("model", DEFAULT_MODEL)
    if entry.get("path") and not fetch:
        root = Path(entry["path"]).expanduser()
        file = root / model
        if not file.is_file():
            return None
        commit = subprocess.run(["git", "-C", str(root), "rev-parse", "--short", "HEAD"],
                                capture_output=True, text=True).stdout.strip() or "worktree"
        return file.read_text(encoding="utf-8"), commit
    branch = entry.get("branch", "main")
    try:
        commit = gh(host, f"repos/{entry['repo']}/commits/{branch}")["sha"][:8]
        content = gh(host, f"repos/{entry['repo']}/contents/{model}?ref={commit}")
    except (subprocess.CalledProcessError, KeyError):
        return None
    text = base64.b64decode(content["content"]).decode("utf-8")
    (cache / entry["id"]).mkdir(parents=True, exist_ok=True)
    (cache / entry["id"] / "architecture-model.toml").write_text(text, encoding="utf-8")
    return text, commit


def load_system(entry: dict, text: str, commit: str, findings: Findings) -> System:
    system = System(entry["id"], entry["repo"], commit=commit)
    raw = tomllib.loads(text)
    declared = (raw.get("system") or {}).get("id")
    if declared != system.id:
        findings.add("blocking", "no-system",
                     f"{system.repo}: the model's [system] id is {declared!r}, the estate's is {system.id!r}")
    elements = {e["id"]: e for e in raw.get("element", [])}
    system.elements = len(elements)
    own = [e for e in elements.values() if e.get("kind") == "system"]
    if own:
        system.name, system.detail, system.status = own[0].get("name", system.id), own[0].get("detail", ""), own[0].get("status", "")
    else:
        findings.add("blocking", "no-system", f"{system.repo}: the model has no element of kind \"system\"")
    system.references = {e["system"] for e in elements.values() if e.get("system")}
    for relation in raw.get("relation", []):
        source, target = elements.get(relation["from"], {}), elements.get(relation["to"], {})
        other = source.get("system") or target.get("system")
        if not other:
            continue
        evidence = tuple(e["path"] for e in relation.get("evidence", []))
        if target.get("system"):
            system.claims.append(Claim(system.id, target["system"], relation.get("label", ""), relation.get("status", ""), evidence))
        else:
            system.claims.append(Claim(source["system"], system.id, relation.get("label", ""), relation.get("status", ""), evidence))
    return system


def load_estate(config: dict, fetch: bool, cache: Path, findings: Findings) -> dict[str, System]:
    host = config.get("host", "")
    systems: dict[str, System] = {}
    for entry in config.get("system", []):
        read = read_model(entry, host, fetch, cache)
        if read is None:
            findings.add("blocking", "missing-model", f"{entry['repo']}: {entry.get('model', DEFAULT_MODEL)} could not be read")
            systems[entry["id"]] = System(entry["id"], entry["repo"])
            continue
        systems[entry["id"]] = load_system(entry, *read, findings)
    return systems


# --- the check --------------------------------------------------------------------------------

def check_claims(systems: dict[str, System], findings: Findings) -> list[tuple[Claim, Claim | None]]:
    """Each claim paired with the other side's matching claim; a missing pair is one-sided."""
    paired: list[tuple[Claim, Claim | None]] = []
    for system in systems.values():
        for other in sorted(system.references - set(systems)):
            findings.add("warning", "unresolved", f"{system.id} names the system {other!r}, which the estate does not include")
        for claim in system.claims:
            other_id = claim.target if claim.source == system.id else claim.source
            other = systems.get(other_id)
            if other is None:
                continue
            match = next((c for c in other.claims if (c.source, c.target) == (claim.source, claim.target)), None)
            if match is None:
                findings.add("blocking", "one-sided",
                             f"{system.id}'s model says {claim.source} -> {claim.target} ({claim.label}); "
                             f"{other_id}'s model ({other.repo}) does not")
            if claim.source == system.id or match is None:
                paired.append((claim, match))
    return paired


# --- rendering --------------------------------------------------------------------------------

def mermaid(systems: dict[str, System], pairs: list[tuple[Claim, Claim | None]]) -> str:
    lines = ["flowchart LR"]
    for system in systems.values():
        label = f"{system.name or system.id}<br/><small>{system.repo}</small>"
        lines.append(f'  {system.id}["{label}"]')
    for claim, match in pairs:
        arrow = "-->" if claim.status == "built" and match else "-.->"
        lines.append(f'  {claim.source} {arrow}|"{claim.label}"| {claim.target}')
    unbuilt = [s.id for s in systems.values() if s.status and s.status != "built"]
    if unbuilt:
        lines.append("  classDef unbuilt stroke-dasharray: 5 5")
        lines.append(f"  class {','.join(unbuilt)} unbuilt")
    return "\n".join(lines)


def render(config: dict, systems: dict[str, System], pairs: list[tuple[Claim, Claim | None]], findings: Findings) -> str:
    models = ", ".join(f"{s.repo}@{s.commit or '?'}" for s in systems.values())
    out = [f"<!-- architecture-estate: generated from the architecture models of {models}; edit a model, then rerun documentor estate render -->",
           f"# {config.get('title', 'Architecture estate')}", ""]
    if config.get("takeaway"):
        out += [config["takeaway"], ""]
    out += ["```mermaid", mermaid(systems, pairs), "```", "",
            "## Systems", "", "| System | Repository | Model at | Elements | Status |", "|---|---|---|---|---|"]
    for s in systems.values():
        out.append(f"| {s.name or s.id}{' (' + s.detail + ')' if s.detail else ''} | `{s.repo}` | `{s.commit or '?'}` | {s.elements} | {s.status or '?'} |")
    out += ["", "## Connections", "", "Each connection as the two models state it; the check fails when only one side does.", "",
            "| From | To | The caller's model says | The callee's model says | Evidence |", "|---|---|---|---|---|"]
    for claim, match in pairs:
        other = match.label if match else "nothing"
        evidence = ", ".join(f"`{claim.source}: {p}`" for p in claim.evidence) + (", " + ", ".join(f"`{claim.target}: {p}`" for p in match.evidence) if match and match.evidence else "")
        out.append(f"| {claim.source} | {claim.target} | {claim.label} | {other} | {evidence} |")
    warnings = [m for sev, _, m in findings.items if sev == "warning"]
    if warnings:
        out += ["", "## Outside the estate", ""] + [f"- {w}" for w in warnings]
    return "\n".join(out) + "\n"


# --- the explained estate ----------------------------------------------------------------------

def digest(config: dict, fetch: bool, cache: Path) -> str:
    """Everything the explained estate may say, from the models: each system's parts, each
    connection with its reason, and each journey; nothing else."""
    host = config.get("host", "")
    out = []
    for entry in config.get("system", []):
        read = read_model(entry, host, fetch, cache)
        if read is None:
            out.append(f"## {entry['id']} ({entry['repo']}): model not readable")
            continue
        raw = tomllib.loads(read[0])
        elements = {e["id"]: e for e in raw.get("element", [])}
        out.append(f"## {entry['id']} ({entry['repo']} at {read[1]})")
        for e in elements.values():
            where = f", zone {e['zone']}" if e.get("zone") else ""
            other = f", belongs to system {e['system']}" if e.get("system") else ""
            out.append(f"- part {e['id']}: {e.get('name', e['id'])} [{e.get('kind')}, {e.get('status')}{where}{other}]"
                       + (f": {e['detail']}" if e.get("detail") else "") + (f"; job: {e['job']}" if e.get("job") else ""))
        for r in raw.get("relation", []):
            why = r.get("why") or r.get("note") or ""
            out.append(f"- connection {r['from']} -> {r['to']}: {r.get('label', '')} [{r.get('status', '')}]" + (f"; why: {why}" if why else ""))
        for j in raw.get("journey", []):
            steps = "; ".join(f"{s.get('from')} -> {s.get('to')}: {s.get('label', '')}" for s in j.get("step", []))
            out.append(f"- journey {j.get('id')}: {j.get('title', '')}. {j.get('takeaway', '')} Steps: {steps}")
    return "\n".join(out)


SECTIONS = ("Where things sit", "What each system does", "How they connect", "Journeys across systems", "Open questions")


def writer_prompt(config: dict, facts: str, generated: str, findings: Findings) -> str:
    from documentor.write import _writing_pass

    problems = "\n".join(f"- {m}" for _, _, m in findings.items) or "- none"
    return "\n".join([
        "You are writing the explained estate: one page that tells a newcomer how several systems fit together.",
        "Answer with the page body only, starting at the first H2. Do not write files.",
        "",
        "## Sections, as H2 headings in this order",
        *[f"- {s}" for s in SECTIONS],
        "",
        "Where things sit: the zones and who owns what. What each system does: one short paragraph each.",
        "How they connect: every connection between systems, each with the reason the models give; a connection without a reason is an open question.",
        "Journeys across systems: each journey the models hold, step by step. Open questions: what the models leave unknown, every finding below, every part whose status is not built.",
        "",
        "## Rules",
        "- Every fact comes from the digest or the generated page below. Do not invent systems, parts, connections, or reasons.",
        "- Name parts and systems as the digest names them. Keep statuses: a decided or placeholder part is not built.",
        *_writing_pass(),
        "",
        f"## The estate: {config.get('title', 'Architecture estate')}",
        config.get("takeaway", ""),
        "",
        "## Findings from the check",
        problems,
        "",
        "## The digest of the models",
        facts,
        "",
        "## The generated page (landscape and tables)",
        generated,
    ])


def reviewer_prompt(page: str, facts: str) -> str:
    return "\n".join([
        "You are checking one page against the facts it must come from. Do not edit anything.",
        "Fail the page for any claim the digest does not support, any connection between systems the page leaves out,",
        "or any unknown the page states as settled. Answer with a first line `VERDICT: pass` or `VERDICT: fail`,",
        "then one line per problem, each starting with `- `.",
        "",
        "## The digest", facts, "", "## The page", page,
    ])


def review_page(args, config: dict) -> int:
    """Evaluate the page as it stands (after a person's edits) against the digest, and record a pass."""
    import re
    from datetime import date

    from documentor.write import AgentError, VERDICT, call, settings

    if not args.out.is_file():
        print(f"documentor estate write --review: {args.out} does not exist; write it first", file=sys.stderr)
        return 2
    page = args.out.read_text(encoding="utf-8")
    start = page.find("\n## ")
    end = page.rfind("\n<details>\n<summary>The models behind this page</summary>")
    body = page[start:end if end > 0 else None].strip()
    cache = args.cache or args.config.parent / ".helix" / "estate"
    _, _, reviewer = settings({}, args.agent or "", args.model or "", args.reviewer_model or "")
    command = settings({}, args.agent or "")[0]
    try:
        answer = call(command, reviewer, reviewer_prompt(body, digest(config, args.fetch, cache)), args.config.parent.resolve())
    except AgentError as error:
        print(f"documentor estate write --review: {error}", file=sys.stderr)
        return 1
    verdict = VERDICT.search(answer)
    if not (verdict and verdict.group(1).lower() == "pass"):
        print(f"FAILED {args.out}:", file=sys.stderr)
        for line in answer.splitlines():
            if line.startswith("- "):
                print(f"  {line[2:].strip()}", file=sys.stderr)
        return 1
    page = re.sub(r"reviewed=\S+;", f"reviewed={date.today().isoformat()}/agent-{reviewer};", page, count=1)
    args.out.write_text(page, encoding="utf-8")
    print(f"{args.out}: passed by {reviewer}")
    return 0


def write_page(args, config: dict, systems: dict[str, System], pairs, findings: Findings) -> int:
    from datetime import date

    from documentor.write import AgentError, VERDICT, call, settings

    cache = args.cache or args.config.parent / ".helix" / "estate"
    facts = digest(config, args.fetch, cache)
    generated = render(config, systems, pairs, findings)
    command, writer, reviewer = settings({}, args.agent or "", args.model or "", args.reviewer_model or "")
    if writer == reviewer:
        print(f"documentor estate write: the writer and the evaluator must be different models (both {writer})", file=sys.stderr)
        return 2
    prompt = writer_prompt(config, facts, generated, findings)
    if args.dry_run:
        print(prompt)
        return 0
    root = args.config.parent.resolve()
    notes: list[str] = []
    for attempt in range(2):
        try:
            body = call(command, writer, prompt + ("\n\n## Feedback to resolve\n" + "\n".join(f"- {n}" for n in notes) if notes else ""), root)
            body = body[body.find("## "):] if "## " in body else body
            answer = call(command, reviewer, reviewer_prompt(body, facts), root)
        except AgentError as error:
            print(f"documentor estate write: {error}", file=sys.stderr)
            return 1
        verdict = VERDICT.search(answer)
        notes = [line[2:].strip() for line in answer.splitlines() if line.startswith("- ")]
        passed = bool(verdict and verdict.group(1).lower() == "pass")
        if passed:
            break
    models = ", ".join(f"{s.repo}@{s.commit or '?'}" for s in systems.values())
    reviewed = f"{date.today().isoformat()}/agent-{reviewer}" if passed else "-"
    header = (f"<!-- architecture-estate: explained from the architecture models of {models}; written=agent-{writer} "
              f"reviewed={reviewed}; rerun documentor estate write after a model changes -->")
    landscape = generated[generated.index("```mermaid"):generated.index("```", generated.index("```mermaid") + 3) + 3]
    tables = generated[generated.index("## Systems"):].replace("## ", "### ")
    page = "\n".join([header, f"# {config.get('title', 'Architecture estate')}", "",
                       *( [config["takeaway"], ""] if config.get("takeaway") else []),
                       landscape, "", body.strip(), "",
                       "<details>", "<summary>The models behind this page</summary>", "", tables.strip(), "", "</details>", ""])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(page, encoding="utf-8")
    if passed:
        print(f"wrote {args.out} (written by {writer}, passed by {reviewer})")
        return 0
    print(f"LEFT {args.out}: written, unreviewed; the evaluator failed it twice. Resolve these, then review it:", file=sys.stderr)
    for note in notes[:8]:
        print(f"  {note}", file=sys.stderr)
    return 1


# --- commands ---------------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="documentor estate", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("check", "render", "write"))
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--out", type=Path, help="render: the page to write")
    parser.add_argument("--fetch", action="store_true", help="read each model from its repository with gh, not a local path")
    parser.add_argument("--cache", type=Path, help="where fetched models are kept (default: .helix/estate beside the config)")
    parser.add_argument("--agent", help="write: the agent command ({model} becomes the model); default as `documentor write`")
    parser.add_argument("--model", help="write: the writer model")
    parser.add_argument("--reviewer-model", help="write: the evaluator model (must differ)")
    parser.add_argument("--dry-run", action="store_true", help="write: print the writer's prompt; call no agent")
    parser.add_argument("--review", action="store_true", help="write: evaluate the page as it stands (after edits) and record a pass")
    args = parser.parse_args(argv)
    if args.command in ("render", "write") and not args.out and not args.dry_run:
        parser.error(f"{args.command} needs --out")
    config = tomllib.loads(args.config.read_text(encoding="utf-8"))
    cache = args.cache or args.config.parent / ".helix" / "estate"
    findings = Findings()
    systems = load_estate(config, args.fetch, cache, findings)
    pairs = check_claims(systems, findings)
    for severity, check, message in findings.items:
        print(f"{severity.upper():9} {check:14} {message}")
    if args.command == "write":
        if findings.blocking and not args.dry_run:
            print("documentor estate write: fix the blocking findings first; the page explains a checked estate", file=sys.stderr)
            return 1
        return review_page(args, config) if args.review else write_page(args, config, systems, pairs, findings)
    if args.command == "render":
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(render(config, systems, pairs, findings), encoding="utf-8")
        print(f"wrote {args.out} ({len(systems)} systems, {len(pairs)} connections)")
    print(f"{'FAIL' if findings.blocking else 'OK'}: {len(systems)} systems, {findings.blocking} blocking, "
          f"{len(findings.items) - findings.blocking} warnings")
    return 1 if findings.blocking else 0


if __name__ == "__main__":
    sys.exit(main())
