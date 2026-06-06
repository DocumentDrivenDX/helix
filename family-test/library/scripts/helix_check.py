#!/usr/bin/env python3
"""helix_check.py — vertical-slice validator for the helix family.

Implements the four subcommands from design §4: marker, graph, instance, type.
Scope: enough to prove the design's contracts; production version is
stdlib-only, this slice uses PyYAML for ergonomics.

Exit code classes (design §4.3):
  0 = clean
  1 = I (instance violation)
  2 = G (graph violation)
  3 = T (type violation)
  4 = M (marker violation)
  5 = R (resolver / install)
  64 = U (usage)

Highest violation wins. Run is exhaustive — every violation is collected,
not just the first.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

EXIT_CLEAN, EXIT_I, EXIT_G, EXIT_T, EXIT_M, EXIT_R, EXIT_U = 0, 1, 2, 3, 4, 5, 64

# ─────────────────────────────────────────────────────────────────────────────
# Per-process caches. Cheap memoization so a marker walk over N instances is
# O(N) instead of O(N^2). Keyed on resolved path string. Mutable so tests
# can reset between runs if needed.

_INSTANCE_INDEX_CACHE: dict[str, dict[str, str]] = {}
_META_CACHE: dict[str, dict] = {}
_GRAPH_CACHE: dict[str, dict] = {}
_DOCS_SCANNED = {"count": 0}
_CEILING_S: float | None = None
_START_T: float = 0.0


def _ceiling_check() -> None:
    """Raise SystemExit(5) with stderr message if wall-clock budget exhausted."""
    if _CEILING_S is None:
        return
    if (time.monotonic() - _START_T) > _CEILING_S:
        sys.stderr.write(
            f"ceiling: >{_CEILING_S}s wall-clock exceeded "
            f"(docs scanned so far: {_DOCS_SCANNED['count']})\n"
        )
        sys.exit(EXIT_R)

# Code → severity (E = error / contributes to exit; W = warning, only at --strict)
ERROR_CODES = {
    "M001","M002","M003","M004","M006","M030",
    "G103","G104","G105","G201","G202","G203",
    "T002","T003","T004",
    "I101","I104","I130","I200",
    "R010",
    "A001","A002",
}
WARNING_CODES = {
    "M005","M010","M020",
    "G133","G140",
    "I010","I103","I120","I121","I131",
    "W003","W004","W005",
}


@dataclass
class Finding:
    code: str
    msg: str
    file: str | None = None
    line: int | None = None

    def is_error(self, strict: bool = False) -> bool:
        if self.code in ERROR_CODES:
            return True
        if strict and self.code in WARNING_CODES:
            return True
        return False


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)

    def add(self, f: Finding) -> None:
        self.findings.append(f)

    def add_code(self, code: str, msg: str, **kw) -> None:
        self.findings.append(Finding(code=code, msg=msg, **kw))

    def has_class(self, prefix: str) -> bool:
        return any(f.code.startswith(prefix) for f in self.findings)

    def exit_code(self, strict: bool = False) -> int:
        # Pick the highest-class error present. Class order: M > T > G > I (highest exit code wins; but design has I=1, G=2, T=3, M=4, R=5)
        rank = {"M": EXIT_M, "T": EXIT_T, "G": EXIT_G, "I": EXIT_I, "R": EXIT_R, "W": EXIT_I, "A": EXIT_I}
        # Soft-escalation overrides: codes whose --strict escalation should NOT bump
        # the exit code to the full marker (M) class. M020 is an advisory rename
        # alias, not a structural marker violation; under --strict it should
        # behave like a W (exit 1), not like M001/M002.
        soft_escalate = {"M020": EXIT_I}
        ec = EXIT_CLEAN
        for f in self.findings:
            if f.is_error(strict):
                if f.code in soft_escalate:
                    cls_exit = soft_escalate[f.code]
                else:
                    cls = f.code[0]
                    cls_exit = rank.get(cls, 0)
                if cls_exit > ec:
                    ec = cls_exit
        return ec

    def render(self, strict: bool = False) -> str:
        lines = []
        for f in self.findings:
            tag = "ERROR" if f.is_error(strict) else "warn "
            loc = f" ({f.file}{':' + str(f.line) if f.line else ''})" if f.file else ""
            lines.append(f"{tag} {f.code}: {f.msg}{loc}")
        e_count = sum(1 for f in self.findings if f.is_error(strict))
        w_count = sum(1 for f in self.findings if not f.is_error(strict) and f.code in WARNING_CODES)
        lines.append(f"\nsummary: E={e_count} W={w_count} exit={self.exit_code(strict)}")
        return "\n".join(lines) if lines else "clean (no findings)"

    def to_json(self, strict: bool = False) -> dict:
        return {
            "findings": [
                {"code": f.code, "msg": f.msg, "file": f.file, "line": f.line,
                 "severity": "error" if f.is_error(strict) else "warning"}
                for f in self.findings
            ],
            "exit_code": self.exit_code(strict),
            "docs_scanned": _DOCS_SCANNED["count"],
        }


# ─────────────────────────────────────────────────────────────────────────────
# Helpers

def load_yaml(path: Path, report: Report, code: str) -> Any | None:
    try:
        return yaml.safe_load(path.read_text())
    except FileNotFoundError:
        report.add_code(code, f"file not found: {path}", file=str(path))
        return None
    except yaml.YAMLError as e:
        report.add_code(code, f"YAML parse error: {e}", file=str(path))
        return None


_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def extract_frontmatter(path: Path, report: Report) -> dict | None:
    text = path.read_text()
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return None
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        report.add_code("I200", f"frontmatter YAML parse error: {e}", file=str(path))
        return None


def slugify_h2(line: str) -> str:
    """## Foo Bar → foo_bar (matches design's section-id rules)."""
    stripped = re.sub(r"^##\s+", "", line.strip())
    return re.sub(r"[^a-z0-9]+", "_", stripped.lower()).strip("_")


# ─────────────────────────────────────────────────────────────────────────────
# Subcommand: type

def cmd_type(types_root: Path, report: Report) -> None:
    """Verify every library type's meta.yml has NO relationships block (design §2.1)."""
    if not types_root.is_dir():
        report.add_code("R010", f"types root not a directory: {types_root}")
        return
    for meta_path in sorted(types_root.glob("*/meta.yml")):
        meta = load_yaml(meta_path, report, "T003")
        if meta is None:
            continue
        if "relationships" in meta:
            report.add_code(
                "T003",
                f"library type meta.yml carries forbidden `relationships:` block "
                f"(design §2.1 invariant — library is shape only)",
                file=str(meta_path),
            )
        # Confirm required keys
        for key in ("id", "required_sections", "version"):
            if key not in meta:
                report.add_code("T002", f"missing required key `{key}:`", file=str(meta_path))
        # Required sections vs template H2s (honoring section_aliases)
        tmpl = meta_path.parent / "template.md"
        if tmpl.exists():
            h2_slugs = {slugify_h2(ln) for ln in tmpl.read_text().splitlines() if ln.startswith("## ")}
            aliases_map = meta.get("section_aliases") or {}
            for sec in meta.get("required_sections", []) or []:
                # Canonical match, or any alias matches an H2 slug
                if sec in h2_slugs:
                    continue
                if any(h.startswith(sec + "_") for h in h2_slugs):
                    continue
                aliases = aliases_map.get(sec, []) or []
                alias_slugs = {re.sub(r"[^a-z0-9]+", "_", a.lower()).strip("_") for a in aliases}
                if h2_slugs & alias_slugs:
                    continue
                if any(h.startswith(a + "_") for a in alias_slugs for h in h2_slugs):
                    continue
                report.add_code(
                    "T004",
                    f"required_section `{sec}` not found as H2 in template.md",
                    file=str(meta_path),
                )


# ─────────────────────────────────────────────────────────────────────────────
# Subcommand: example --adversarial-coverage
#
# Walks <example_root>/fixtures/*.yml and asserts each fixture's `id:` token
# (F1, F2, ...) appears as a word-bounded reference in at least one artifact
# markdown body under <example_root>/docs/. Empty fixtures dir is an error
# (A002 — coverage gate with nothing to gate is a no-op trap).

_FIXTURE_TOKEN_RE_CACHE: dict[str, re.Pattern] = {}


def _fixture_token_re(token: str) -> re.Pattern:
    """Word-bounded regex for a fixture token (e.g. 'F1' matches F1 but not F11)."""
    cached = _FIXTURE_TOKEN_RE_CACHE.get(token)
    if cached is not None:
        return cached
    # \b at end keeps F1 from matching F10/F11; re.escape handles future tokens
    pat = re.compile(rf"(?<![A-Za-z0-9]){re.escape(token)}(?![A-Za-z0-9])")
    _FIXTURE_TOKEN_RE_CACHE[token] = pat
    return pat


def cmd_example_adversarial_coverage(example_root: Path, report: Report) -> None:
    """Verify every fixture ID under <example_root>/fixtures/ is referenced
    by at least one artifact under <example_root>/docs/.
    """
    if not example_root.is_dir():
        report.add_code("A002", f"example root not a directory: {example_root}")
        return
    fixtures_dir = example_root / "fixtures"
    docs_dir = example_root / "docs"
    if not fixtures_dir.is_dir():
        report.add_code("A002", f"fixtures dir missing: {fixtures_dir}")
        return
    if not docs_dir.is_dir():
        report.add_code("A002", f"docs dir missing: {docs_dir}")
        return

    fixture_ids: list[str] = []
    for fx_path in sorted(fixtures_dir.glob("*.yml")):
        try:
            fx = yaml.safe_load(fx_path.read_text()) or {}
        except yaml.YAMLError as e:
            report.add_code("A002", f"fixture YAML parse error: {e}", file=str(fx_path))
            continue
        fid = fx.get("id")
        if not fid:
            report.add_code("A002", f"fixture missing `id:` key", file=str(fx_path))
            continue
        fixture_ids.append(str(fid))

    if not fixture_ids:
        report.add_code("A002", f"no fixtures found under {fixtures_dir} — coverage gate is vacuous")
        return

    # Build artifact bodies (frontmatter stripped, since fixture refs in
    # frontmatter would be a code smell — fixtures are narrative, not links).
    artifact_bodies: list[tuple[Path, str]] = []
    for md in sorted(docs_dir.rglob("*.md")):
        try:
            text = md.read_text()
        except Exception:
            continue
        body = _FRONTMATTER_RE.sub("", text, count=1)
        artifact_bodies.append((md, body))

    if not artifact_bodies:
        report.add_code("A002", f"no markdown artifacts found under {docs_dir}")
        return

    for fid in fixture_ids:
        pat = _fixture_token_re(fid)
        refs = [str(p) for p, b in artifact_bodies if pat.search(b)]
        if not refs:
            report.add_code(
                "A001",
                f"adversarial fixture `{fid}` not referenced by any artifact under {docs_dir}",
            )

    # Track docs_scanned for symmetry with other modes
    _DOCS_SCANNED["count"] += len(artifact_bodies)


# ─────────────────────────────────────────────────────────────────────────────
# Subcommand: graph

def cmd_graph(graph_path: Path, library_types_root: Path | None, report: Report) -> dict | None:
    """Validate a flow graph.yml. Returns parsed graph or None on hard failure."""
    g = load_yaml(graph_path, report, "G201")
    if g is None:
        return None

    nodes = {n["id"]: n for n in g.get("nodes", []) or []}
    edges = g.get("edges", []) or []
    activities = g.get("activities", []) or []
    allowed_cycles = g.get("allowed_cycles", []) or []
    external_edges = g.get("external_edges", []) or []
    walked_kinds = {"requires", "contains"}

    # Type resolution
    lib_types = set()
    if library_types_root and library_types_root.is_dir():
        lib_types = {p.parent.name for p in library_types_root.glob("*/meta.yml")}
    for node_id, node in nodes.items():
        t = node.get("type", "")
        if t.startswith("library:"):
            slug = t.split(":", 1)[1]
            if library_types_root and slug not in lib_types:
                report.add_code(
                    "G202",
                    f"node `{node_id}` references unknown library type `{slug}`",
                    file=str(graph_path),
                )
        elif t.startswith("local:"):
            pass  # OK for slice
        else:
            report.add_code(
                "G203",
                f"node `{node_id}` type `{t}` missing library: or local: prefix",
                file=str(graph_path),
            )

    # Edge endpoint resolution + walked-kind self-loops
    for e in edges:
        if e["from"] not in nodes:
            report.add_code("G201", f"edge from `{e['from']}` to `{e['to']}`: source not declared", file=str(graph_path))
        if e["to"] not in nodes:
            report.add_code("G201", f"edge from `{e['from']}` to `{e['to']}`: target not declared", file=str(graph_path))
        kind = e.get("kind")
        # G103: walked-kind self-loop requires allowed_cycles entry
        if e["from"] == e["to"] and kind in walked_kinds:
            triple = (e["from"], e["to"], kind)
            if not any(
                (ac.get("from_type"), ac.get("to_type"), ac.get("kind")) == triple
                for ac in allowed_cycles
            ):
                report.add_code(
                    "G103",
                    f"self-loop on walked kind `{kind}` for `{e['from']}` requires an allowed_cycles entry",
                    file=str(graph_path),
                )

    # external_edges hard-fails (G104, G105)
    for ext in external_edges:
        if ext.get("required") is True:
            report.add_code(
                "G104",
                f"external_edges entry to `{ext.get('to_flow') or ext.get('to_methodology')}:{ext.get('to_type')}` "
                f"has `required: true` — forbidden (cross-flow edges are advisory)",
                file=str(graph_path),
            )
        if ext.get("kind") not in ("informs", "informed_by") and not str(ext.get("kind", "")).startswith("x-"):
            report.add_code(
                "G105",
                f"external_edges kind `{ext.get('kind')}` must be `informs`, `informed_by`, or `x-*` "
                f"(cross-flow `requires`/`contains`/`supersedes` forbidden in v1)",
                file=str(graph_path),
            )

    # Exit-gate role check
    for a in activities:
        gate = a.get("exit_gate")
        if gate and gate not in nodes:
            report.add_code(
                "G201",
                f"activity `{a.get('id')}` declares exit_gate `{gate}` not in nodes",
                file=str(graph_path),
            )
        elif gate and nodes.get(gate, {}).get("role") != "exit-gate":
            report.add_code(
                "G201",
                f"activity `{a.get('id')}` exit_gate `{gate}` exists but lacks `role: exit-gate`",
                file=str(graph_path),
            )

    return g


# ─────────────────────────────────────────────────────────────────────────────
# Subcommand: instance

def build_instance_index(scope_root: Path) -> dict[str, Path]:
    key = str(scope_root)
    cached = _INSTANCE_INDEX_CACHE.get(key)
    if cached is not None:
        # Convert back to Paths
        return {k: Path(v) for k, v in cached.items()}
    index: dict[str, Path] = {}
    if not scope_root.is_dir():
        _INSTANCE_INDEX_CACHE[key] = {}
        return index
    for md in scope_root.rglob("*.md"):
        try:
            text = md.read_text()
        except Exception:
            continue
        m = _FRONTMATTER_RE.match(text)
        if not m:
            continue
        try:
            fm = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            continue
        ddx = fm.get("ddx") or {}
        if "id" in ddx:
            index[ddx["id"]] = md
    _INSTANCE_INDEX_CACHE[key] = {k: str(v) for k, v in index.items()}
    return index


def _parse_major(v: Any) -> int | None:
    if v is None:
        return None
    try:
        s = str(v).strip()
        return int(s.split(".", 1)[0])
    except (ValueError, AttributeError):
        return None


def _check_instance_sections(
    doc_path: Path,
    ddx: dict,
    library_types_root: Path | None,
    report: Report,
    fm_raw: dict,
) -> None:
    """B1: check instance H2s against library required_sections.

    Honors library_type_version pin: if pin major < library major, missing
    newly-introduced sections fire as I010 (warn). Without pin, missing
    sections fire as T004 (error).
    """
    if library_types_root is None or not library_types_root.is_dir():
        return
    inst_type = ddx.get("type")
    if not inst_type:
        return
    meta_path = library_types_root / inst_type / "meta.yml"
    if not meta_path.exists():
        return
    meta_key = str(meta_path)
    if meta_key in _META_CACHE:
        meta = _META_CACHE[meta_key]
    else:
        try:
            meta = yaml.safe_load(meta_path.read_text()) or {}
        except yaml.YAMLError:
            return
        _META_CACHE[meta_key] = meta
    required = meta.get("required_sections", []) or []
    if not required:
        return
    aliases_map = meta.get("section_aliases") or {}
    lib_major = _parse_major(meta.get("version"))
    pin_major = _parse_major(ddx.get("library_type_version"))

    # Extract instance heading slugs (H2 always; H3 too if the type opts in
    # via `match_scope: any-heading` — backfill-plan style where required
    # sections live under per-scenario H2 partitions).
    text = doc_path.read_text()
    body = _FRONTMATTER_RE.sub("", text, count=1)
    h2_slugs = {slugify_h2(ln) for ln in body.splitlines() if ln.startswith("## ")}
    if meta.get("match_scope") == "any-heading":
        # slugify_h2 strips "## " specifically; for "### " do an inline version.
        for ln in body.splitlines():
            if ln.startswith("### "):
                stripped = re.sub(r"^#+\s+", "", ln.strip())
                h2_slugs.add(re.sub(r"[^a-z0-9]+", "_", stripped.lower()).strip("_"))

    # For each required section, check canonical or alias.
    # An alias matches if any H2 slug equals it OR starts with `<alias>_`
    # (so "Consumer" aliases match "Consumer 1 — Analytics" etc).
    for sec in required:
        if sec in h2_slugs:
            continue
        if any(h.startswith(sec + "_") for h in h2_slugs):
            continue
        aliases = aliases_map.get(sec, []) or []
        alias_slugs = {re.sub(r"[^a-z0-9]+", "_", a.lower()).strip("_") for a in aliases}
        if h2_slugs & alias_slugs:
            continue
        if any(h.startswith(a + "_") for a in alias_slugs for h in h2_slugs):
            continue
        # Missing. Choose severity:
        # If a pin exists and pin_major < lib_major → I010 deprecation warn.
        # Otherwise → T004 error.
        if pin_major is not None and lib_major is not None and pin_major < lib_major:
            report.add_code(
                "I010",
                f"required_section `{sec}` missing — instance pins "
                f"library_type_version {ddx.get('library_type_version')} < current {meta.get('version')}; "
                f"deprecation grace (re-pin or add section)",
                file=str(doc_path),
            )
        else:
            report.add_code(
                "T004",
                f"required_section `{sec}` not present in instance",
                file=str(doc_path),
            )


def cmd_instance(
    doc_path: Path,
    marker: dict,
    marker_dir: Path,
    flow_resolver: dict[str, Path],
    report: Report,
    cross_flow_edges_mode: str = "warn",
    library_types_root: Path | None = None,
) -> None:
    """Validate one instance document against the active flow graph(s)."""
    fm = extract_frontmatter(doc_path, report)
    if fm is None:
        # No frontmatter — design says deprecation cycle warning W004
        report.add_code("W004", f"instance has no ddx frontmatter", file=str(doc_path))
        return

    # W005: legacy `relationships:` block alongside ddx.links
    if "relationships" in fm and ((fm.get("ddx") or {}).get("links") is not None):
        report.add_code(
            "W005",
            f"instance carries both legacy `relationships:` block and new `ddx.links:` — drop the legacy block",
            file=str(doc_path),
        )

    ddx = fm.get("ddx") or {}
    # Accept v2 (`ddx.flow:`) and v1 (`ddx.methodology:`) interchangeably.
    # The v1 key is the legacy alias; M020 governs the marker-level rename.
    inst_flow = ddx.get("flow") or ddx.get("methodology")
    if not inst_flow:
        report.add_code("I200", f"missing `ddx.flow:` (or legacy `ddx.methodology:`)", file=str(doc_path))
        return

    # Section-presence check against library shape (B1 / B6).
    _check_instance_sections(doc_path, ddx, library_types_root, report, fm)

    # Resolve the flow's graph
    flow_root = flow_resolver.get(inst_flow)
    if not flow_root:
        report.add_code("I120" if inst_flow in marker.get("_installed", []) else "I121",
                        f"link to flow `{inst_flow}` not in resolver", file=str(doc_path))
        return

    graph_path = flow_root / "workflows/graph.yml"
    graph_key = str(graph_path)
    if graph_key in _GRAPH_CACHE:
        graph = _GRAPH_CACHE[graph_key]
    else:
        graph = load_yaml(graph_path, report, "I200")
        if graph is None:
            return
        _GRAPH_CACHE[graph_key] = graph

    # Build node map keyed by type
    nodes_by_type_id: dict[str, dict] = {}  # type_id → node dict
    nodes_by_node_id: dict[str, dict] = {}  # node id → node dict
    for n in graph.get("nodes", []) or []:
        nodes_by_node_id[n["id"]] = n
        nodes_by_type_id[n.get("id")] = n  # primary key for resolution
    # Edge table keyed by (from_type_id, to_type_id, kind)
    edges = {
        (e["from"], e["to"], e.get("kind")): e
        for e in graph.get("edges", []) or []
    }
    external_edges_by_kv = {}
    for ext in graph.get("external_edges", []) or []:
        # v2 graphs use `to_flow:`; v1 use `to_methodology:` — accept both.
        key = (
            ext.get("from_type"),
            ext.get("to_flow") or ext.get("to_methodology"),
            ext.get("to_type"),
            ext.get("kind"),
        )
        external_edges_by_kv[key] = ext

    # Build instance index for this flow (consumer's scope under marker)
    flow_entry = next(
        (m for m in marker.get("methodologies", []) or [] if m.get("id") == inst_flow),
        None,
    )
    if not flow_entry:
        report.add_code("I200", f"instance flow `{inst_flow}` not in marker", file=str(doc_path))
        return
    scope_root = (marker_dir / flow_entry["root"]).resolve()
    instance_index = build_instance_index(scope_root)

    # Determine source node id from the instance's `ddx.type`
    inst_type = ddx.get("type")
    source_node_id = ddx.get("type")  # convention for slice: node id == type id when only one node per type
    # Actually use the FIRST node with matching type
    source_node = None
    for n in graph.get("nodes", []) or []:
        node_type = n.get("type", "")
        if node_type.startswith("library:") and node_type.split(":", 1)[1] == inst_type:
            source_node = n
            break
        elif node_type.startswith("local:") and node_type.split(":", 1)[1] == inst_type:
            source_node = n
            break
    if not source_node:
        report.add_code("I200",
                        f"instance type `{inst_type}` does not map to any node in {inst_flow}'s graph",
                        file=str(doc_path))
        return

    source_node_id = source_node["id"]

    # Now walk ddx.links[]
    for i, link in enumerate(ddx.get("links", []) or []):
        kind = link.get("kind")
        target = link.get("to")
        status = link.get("status", "present")
        scope = link.get("scope")
        cross = link.get("cross_flow", False) or link.get("cross_methodology", False)

        # Intra-document edges (FR-N, US-N-ACm) — not resolved against external index
        if scope == "intra-document":
            continue

        # Cross-instance (§13.4 case A): target shape is "flow.instance:id" or link
        # carries `cross_instance: true`. Handled BEFORE plain cross-flow so
        # the dotted-flow.instance form doesn't get mis-parsed.
        cross_instance = link.get("cross_instance", False)
        is_dotted_target = isinstance(target, str) and ":" in target and "." in target.split(":", 1)[0]
        if cross_instance or is_dotted_target:
            if ":" in (target or ""):
                qual, target_id = target.split(":", 1)
            else:
                qual, target_id = "", target
            if "." in qual:
                target_flow, target_instance = qual.split(".", 1)
            else:
                target_flow, target_instance = qual, "default"

            # I130: target (flow, instance) not in marker
            marker_pairs = {(m["id"], m.get("instance", "default"))
                            for m in marker.get("methodologies", []) or []}
            if (target_flow, target_instance) not in marker_pairs:
                report.add_code("I130",
                    f"edge {i}: cross-instance target `{target_flow}.{target_instance}:{target_id}` "
                    f"references unknown (flow, instance) pair (not in marker)",
                    file=str(doc_path))
                continue

            # I131: target instance present in marker but the source flow's
            # external_edges doesn't authorise the cross-instance kind.
            ext_match = None
            for key, ext in external_edges_by_kv.items():
                # external_edges entries for cross-instance use `to_flow:` and may
                # optionally carry `to_instance:`. Loose match on (source, to_flow, kind).
                if key[0] == source_node_id and key[1] == target_flow and key[3] == kind:
                    ext_match = ext
                    break
            if not ext_match:
                report.add_code("I131",
                    f"edge {i}: cross-instance `{kind}` from `{source_node_id}` "
                    f"to `{target_flow}.{target_instance}:{target_id}` not authorised in external_edges",
                    file=str(doc_path))
                continue

            # Stale-target check (§13.4 case A): target (flow, instance) authorised
            # AND in marker, but the target document is missing OR carries
            # `status: superseded` / `status: deprecated` in its frontmatter.
            # Locate the target instance's scope via marker entries and resolve.
            target_entry = next(
                (m for m in marker.get("methodologies", []) or []
                 if m.get("id") == target_flow and m.get("instance", "default") == target_instance),
                None,
            )
            if target_entry is not None:
                target_scope = (marker_dir / target_entry["root"]).resolve()
                target_index = build_instance_index(target_scope)
                target_doc = target_index.get(target_id)
                if target_doc is None:
                    report.add_code("I131",
                        f"edge {i}: cross-instance target `{target_flow}.{target_instance}:{target_id}` "
                        f"not found under scope `{target_scope}` (stale target — instance superseded or renamed)",
                        file=str(doc_path))
                else:
                    target_fm = extract_frontmatter(target_doc, Report()) or {}
                    tstatus = ((target_fm.get("ddx") or {}).get("status")
                               or target_fm.get("status"))
                    if tstatus in ("superseded", "deprecated"):
                        report.add_code("I131",
                            f"edge {i}: cross-instance target `{target_flow}.{target_instance}:{target_id}` "
                            f"is `status: {tstatus}` (stale target — update link to the successor)",
                            file=str(doc_path))
            continue

        # Cross-flow
        if cross or (isinstance(target, str) and ":" in target and not target.startswith("@")):
            # Parse qualified target
            if ":" in (target or ""):
                target_flow, target_id = target.split(":", 1)
            else:
                target_flow, target_id = "?", target

            # Look up in external_edges
            ext_key = (source_node_id, target_flow, None, kind)
            # Loose match: we look for source_node_id, target_flow, kind, ignoring to_type
            ext_match = None
            for key, ext in external_edges_by_kv.items():
                if key[0] == source_node_id and key[1] == target_flow and key[3] == kind:
                    ext_match = ext
                    break
            if not ext_match:
                report.add_code(
                    "I101",
                    f"edge {i}: cross-flow `{kind}` from `{source_node_id}` "
                    f"to `{target_flow}:{target_id}` not authorized in external_edges",
                    file=str(doc_path),
                )
                continue

            # Is target flow in active marker?
            if target_flow not in [m["id"] for m in marker.get("methodologies", []) or []]:
                code = "I121" if target_flow not in marker.get("_installed", []) else "I120"
                if cross_flow_edges_mode == "deny":
                    report.add_code("I101",
                        f"edge {i}: cross-flow target `{target_flow}` not active "
                        f"(deny mode)", file=str(doc_path))
                else:
                    report.add_code(code,
                        f"edge {i}: cross-flow target `{target_flow}` not in marker",
                        file=str(doc_path))
            continue

        # Local edge — resolve target via instance index
        # First, figure out target node id by looking at target instance's ddx.type
        target_path = instance_index.get(target)
        if not target_path:
            if status == "planned":
                report.add_code("I103",
                    f"edge {i}: forward reference to `{target}` (status: planned) — unresolved (will re-check at exit gate)",
                    file=str(doc_path))
            else:
                # Nearest-id hint
                hint = ""
                if instance_index:
                    sample = sorted(instance_index.keys())[:3]
                    hint = f" — known ids include: {', '.join(sample)}; if planned, set status: planned"
                report.add_code("I101",
                    f"edge {i}: target `{target}` not found in scope `{scope_root}`{hint}",
                    file=str(doc_path))
            continue

        if status == "planned":
            # Target resolved but author left status: planned — I104
            report.add_code("I104",
                f"edge {i}: target `{target}` resolved but status is `planned` — change to `present`",
                file=str(doc_path))
            # don't return; still check kind validity below

        # Read target's type
        target_fm = extract_frontmatter(target_path, report) or {}
        target_type = (target_fm.get("ddx") or {}).get("type")
        target_node = None
        for n in graph.get("nodes", []) or []:
            nt = n.get("type", "")
            if nt.startswith("library:") and nt.split(":", 1)[1] == target_type:
                target_node = n; break
            elif nt.startswith("local:") and nt.split(":", 1)[1] == target_type:
                target_node = n; break
        if not target_node:
            report.add_code("I200",
                f"edge {i}: target `{target}` has type `{target_type}` not declared in `{inst_flow}`'s graph",
                file=str(doc_path))
            continue

        target_node_id = target_node["id"]

        # Look up the type-pair edge
        edge_key = (source_node_id, target_node_id, kind)
        if edge_key not in edges:
            allowed_kinds = [
                k for (f, t, k), _ in edges.items()
                if f == source_node_id and t == target_node_id
            ]
            hint = f" allowed kinds: {allowed_kinds}" if allowed_kinds else " no edges declared between these nodes"
            report.add_code("I101",
                f"edge {i}: `{source_node_id}` --[{kind}]--> `{target_node_id}` not declared in graph.{hint}",
                file=str(doc_path))


# ─────────────────────────────────────────────────────────────────────────────
# Subcommand: marker

def validate_marker_schema(marker: dict, marker_path: Path, marker_dir: Path, report: Report) -> bool:
    """M001-M006/M030 hard-fail rules from design §1.4 + §13.7.

    Schema v2 (helix_version: 2) accepts `flows:` with optional `instance:` per entry.
    Schema v1 (`methodologies:`) is accepted with M020 deprecation warn (alias on the
    legacy key). After validation, marker["methodologies"] holds the normalized entry
    list (the internal cache key is preserved for one cycle of back-compat) where each
    entry has an injected `instance` field (defaulting to "default"). Uniqueness key is
    (id, instance) — duplicates fire M030.

    Returns True if marker survives.
    """
    if not isinstance(marker, dict):
        report.add_code("M001", "marker must be a mapping", file=str(marker_path))
        return False

    # Schema-version detection: accept either `flows:` (v2) or `methodologies:` (v1).
    has_flows = "flows" in marker
    has_methods = "methodologies" in marker
    if has_flows and has_methods:
        report.add_code("M001",
                        "marker carries BOTH `flows:` and `methodologies:` — pick one (use `flows:` for v2)",
                        file=str(marker_path))
        return False
    if not has_flows and not has_methods:
        report.add_code("M001", "marker missing required `flows:` (v2) or `methodologies:` (v1) list",
                        file=str(marker_path))
        return False

    if has_flows:
        raw_entries = marker.get("flows")
        list_key = "flows"
    else:
        raw_entries = marker.get("methodologies")
        list_key = "methodologies"
        # M020: legacy-key deprecation alias (one cycle). Fires on every v1-shape
        # marker that still uses `methodologies:`. v2-shape (`flows:`) markers are
        # silent. Escalated to error when helix_version: 2 is explicitly declared
        # (the author opted into v2 but kept the old key).
        if str(marker.get("helix_version", "")).strip() == "2":
            report.add_code("M020",
                            "marker declares `helix_version: 2` but uses legacy `methodologies:` key — rename to `flows:`",
                            file=str(marker_path))
        else:
            report.add_code("M020",
                            "`methodologies:` is the legacy key; rename to `flows:` before v2 lands",
                            file=str(marker_path))

    if not isinstance(raw_entries, list) or not raw_entries:
        report.add_code("M001", f"`{list_key}:` must be a non-empty list", file=str(marker_path))
        return False

    pairs_seen: set[tuple[str, str]] = set()
    ids_seen_for_default: set[str] = set()
    survived = True
    normalized: list[dict] = []
    for i, entry in enumerate(raw_entries):
        if not isinstance(entry, dict):
            report.add_code("M001", f"{list_key}[{i}] must be a mapping", file=str(marker_path))
            survived = False; continue
        mid = entry.get("id")
        if not mid:
            report.add_code("M001", f"{list_key}[{i}] missing `id:`", file=str(marker_path))
            survived = False; continue

        # instance: optional, default "default". Empty string → M001 (per §13.7 M031 note,
        # rolled into M001 covers empty values).
        if "instance" in entry:
            inst = entry.get("instance")
            if not isinstance(inst, str) or not inst.strip():
                report.add_code("M001",
                                f"{list_key}[{i}] (`{mid}`) `instance:` must be a non-empty string",
                                file=str(marker_path))
                survived = False; continue
            inst = inst.strip()
        else:
            inst = "default"
        entry["instance"] = inst

        pair = (mid, inst)
        # M030: duplicate (id, instance) → hard fail.
        # M003 retained for backwards-compat: when same id appears twice and BOTH
        # would map to instance "default" (i.e. v1-style duplicate), prefer M003.
        if pair in pairs_seen:
            if inst == "default" and mid in ids_seen_for_default:
                report.add_code("M003", f"duplicate flow id `{mid}` (instance `{inst}`)",
                                file=str(marker_path))
            else:
                report.add_code("M030",
                                f"duplicate (id, instance) pair (`{mid}`, `{inst}`)",
                                file=str(marker_path))
            survived = False
        pairs_seen.add(pair)
        if inst == "default":
            ids_seen_for_default.add(mid)

        root = entry.get("root")
        if not root:
            report.add_code("M001", f"{list_key}[{i}] (`{mid}`) missing `root:`", file=str(marker_path))
            survived = False; continue
        try:
            root_resolved = (marker_dir / root).resolve()
            marker_dir_resolved = marker_dir.resolve()
            # M002: root must stay inside repo
            try:
                root_resolved.relative_to(marker_dir_resolved)
            except ValueError:
                report.add_code("M002", f"`{mid}` root `{root}` escapes repo root", file=str(marker_path))
                survived = False; continue
        except Exception as e:
            report.add_code("M001", f"`{mid}` root path invalid: {e}", file=str(marker_path))
            survived = False; continue
        normalized.append(entry)

    # Normalize: regardless of v1/v2 input shape, downstream code reads
    # marker["methodologies"]. The internal cache key keeps the legacy spelling
    # for one cycle so the rename stays additive — downstream consumers see a
    # stable shape while authors migrate to `flows:`.
    marker["methodologies"] = normalized

    # M004: defaults.flow (v2) / defaults.methodology (v1 legacy) must be in the
    # flows list (by id, or by qualified `flow.instance` for v2).
    defaults = marker.get("defaults") or {}
    dm = defaults.get("flow") or defaults.get("methodology")
    if dm:
        if "." in dm:
            df, di = dm.split(".", 1)
            if not any(e["id"] == df and e["instance"] == di for e in normalized):
                report.add_code("M004",
                    f"defaults.{'flow' if 'flow' in defaults else 'methodology'} `{dm}` "
                    f"not in {list_key} list", file=str(marker_path))
                survived = False
        else:
            if dm not in {e["id"] for e in normalized}:
                report.add_code("M004",
                    f"defaults.{'flow' if 'flow' in defaults else 'methodology'} `{dm}` "
                    f"not in {list_key} list", file=str(marker_path))
                survived = False

    return survived


# ─────────────────────────────────────────────────────────────────────────────
# resolve_cwd_to_instance — design §13.6b
#
# Path-component-aware matching (NOT string prefix). Equal-depth ties at the
# SAME or SIBLING level return AMBIGUOUS — never silent alphabetical selection.

def _path_components(p: Path) -> tuple[str, ...]:
    """Absolute path → tuple of components, with empty trailing component removed."""
    s = str(p)
    parts = [x for x in s.split(os.sep) if x != ""]
    return tuple(parts)


def _is_path_prefix(a: Path, b: Path) -> bool:
    """True iff components(a) is a prefix of components(b). Component-aware:
    "/a/bc" is NOT a path prefix of "/a/bcd"."""
    ca = _path_components(a)
    cb = _path_components(b)
    if len(ca) > len(cb):
        return False
    return cb[: len(ca)] == ca


def resolve_cwd_to_instance(
    marker: dict,
    cwd: Path,
    repo_root: Path,
    env_flow: str | None = None,
) -> tuple[str, str, str] | tuple[str, list[tuple[str, str]]]:
    """Resolve a current working directory to a (flow, instance) pair per §13.6b.

    Inputs:
      marker     — already-validated marker dict (post `validate_marker_schema`)
      cwd        — absolute cwd path
      repo_root  — absolute repo root (the directory containing .helix.yml)
      env_flow   — optional value of HELIX_FLOW env (or legacy HELIX_METHODOLOGY)

    Returns either:
      ("resolved",   flow_id, instance) — single (flow, instance) result
      ("no_match",   [])                — no scope contains cwd; caller falls through
      ("ambiguous",  [(flow_id, instance), ...]) — multiple equal-depth candidates
                                                   AND env/defaults could not break tie

    Algorithm (§13.6b):
      1. abs_root_k = repo_root / entry["root"] for each entry
      2. K = { entries whose abs_root is a path-prefix of cwd OR equal to cwd }
      3. |K|==0 → no_match
      4. |K|==1 → resolved(that entry)
      5. |K|>1  → pick deepest (longest components). Single deepest → resolved.
                  Multiple deepest (siblings at equal depth, or identical roots):
                  i. env_flow names one of K_max → resolved(that one)
                  ii. defaults.{flow,methodology} names one of K_max → resolved
                  iii. else ambiguous(K_max)
    """
    cwd = Path(cwd).resolve()
    repo_root = Path(repo_root).resolve()

    entries = marker.get("methodologies") or []
    # Each entry already has injected `instance:` from validate_marker_schema.

    # Step 1-2: build candidate set K
    K: list[dict] = []
    for entry in entries:
        abs_root = (repo_root / entry["root"]).resolve()
        if _is_path_prefix(abs_root, cwd):
            K.append(entry)

    # Step 3: no match
    if not K:
        return ("no_match", [])

    # Step 4: single match
    if len(K) == 1:
        e = K[0]
        return ("resolved", e["id"], e["instance"])

    # Step 5: nested / overlapping — pick deepest
    def depth(e: dict) -> int:
        return len(_path_components((repo_root / e["root"]).resolve()))

    max_depth = max(depth(e) for e in K)
    K_max = [e for e in K if depth(e) == max_depth]

    # 5a: single deepest wins
    if len(K_max) == 1:
        e = K_max[0]
        return ("resolved", e["id"], e["instance"])

    # 5b: genuine sibling tie. Disambiguation chain.
    # i. env_flow (HELIX_FLOW / legacy HELIX_METHODOLOGY). Accepts either bare flow id
    # (matches if exactly one entry in K_max has that id) or qualified "flow.instance".
    if env_flow:
        ef = env_flow.strip()
        if "." in ef:
            ef_flow, ef_instance = ef.split(".", 1)
            for e in K_max:
                if e["id"] == ef_flow and e["instance"] == ef_instance:
                    return ("resolved", e["id"], e["instance"])
        else:
            matching = [e for e in K_max if e["id"] == ef]
            if len(matching) == 1:
                e = matching[0]
                return ("resolved", e["id"], e["instance"])

    # ii. defaults.{flow,methodology}
    defaults = marker.get("defaults") or {}
    dm = defaults.get("flow") or defaults.get("methodology")
    if dm:
        if "." in dm:
            dm_flow, dm_instance = dm.split(".", 1)
            for e in K_max:
                if e["id"] == dm_flow and e["instance"] == dm_instance:
                    return ("resolved", e["id"], e["instance"])
        else:
            matching = [e for e in K_max if e["id"] == dm]
            if len(matching) == 1:
                e = matching[0]
                return ("resolved", e["id"], e["instance"])

    # iii. ambiguous. Caller (skill / runner) emits the disambiguation banner.
    return ("ambiguous", [(e["id"], e["instance"]) for e in K_max])


def _load_disk_cache(marker_dir: Path) -> dict:
    p = marker_dir / ".helix" / "index.json"
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text())
    except Exception:
        return {}


def _save_disk_cache(marker_dir: Path, data: dict) -> None:
    d = marker_dir / ".helix"
    d.mkdir(exist_ok=True)
    try:
        (d / "index.json").write_text(json.dumps(data))
    except Exception:
        pass


def cmd_marker(
    marker_path: Path,
    flow_resolver: dict[str, Path],
    library_types_root: Path | None,
    report: Report,
    no_instance: bool = False,
    cross_flow_edges_mode: str = "warn",
    allow_empty_scope: bool = False,
    use_cache: bool = False,
) -> None:
    marker = load_yaml(marker_path, report, "M001")
    if marker is None:
        return
    marker_dir = marker_path.parent.resolve()

    if not validate_marker_schema(marker, marker_path, marker_dir, report):
        return

    # M005: warn on unknown flows; proceed with known ones
    # M006: root resolves to nonexistent directory → hard stop unless --allow-empty-scope
    for entry in marker["methodologies"]:
        mid = entry["id"]
        if mid not in flow_resolver:
            report.add_code("M005", f"unknown flow `{mid}` — no plugin found, entry ignored",
                            file=str(marker_path))
            continue
        scope = (marker_dir / entry["root"]).resolve()
        if not scope.is_dir():
            if allow_empty_scope:
                report.add_code("W003", f"`{mid}` root `{entry['root']}` does not exist (allow-empty-scope)",
                                file=str(marker_path))
            else:
                report.add_code("M006", f"`{mid}` root `{entry['root']}` does not resolve to a directory",
                                file=str(marker_path))

    # Track installed flows for I120/I121 discrimination
    marker.setdefault("_installed", list(flow_resolver.keys()))

    # Dispatch graph mode for each known flow
    for entry in marker["methodologies"]:
        mid = entry["id"]
        if mid not in flow_resolver:
            continue
        graph_path = flow_resolver[mid] / "workflows/graph.yml"
        if graph_path.exists():
            cmd_graph(graph_path, library_types_root, report)

    if no_instance:
        return

    # Cache-correctness invalidation matrix (design F4):
    #   - marker mtime change → full re-walk (no entries survive)
    #   - graph.yml mtime change → invalidate all instances of that flow
    #   - library type meta.yml mtime → invalidate all instances of that type
    #   - per-instance mtime unchanged → skip re-validation
    disk_cache = _load_disk_cache(marker_dir) if use_cache else {}
    prev_entries = disk_cache.get("entries", {}) if use_cache else {}
    prev_marker_mtime = disk_cache.get("marker_mtime")
    prev_graph_mtimes = disk_cache.get("graph_mtimes", {})
    prev_type_mtimes = disk_cache.get("type_mtimes", {})

    cur_marker_mtime = marker_path.stat().st_mtime
    marker_changed = (prev_marker_mtime != cur_marker_mtime)

    cur_graph_mtimes = {}
    invalidated_flows = set()
    for entry in marker["methodologies"]:
        mid = entry["id"]
        if mid not in flow_resolver:
            continue
        gp = flow_resolver[mid] / "workflows/graph.yml"
        if gp.exists():
            cur_graph_mtimes[mid] = gp.stat().st_mtime
            if prev_graph_mtimes.get(mid) != cur_graph_mtimes[mid]:
                invalidated_flows.add(mid)

    cur_type_mtimes = {}
    invalidated_types = set()
    if library_types_root and library_types_root.is_dir():
        for meta_path in library_types_root.glob("*/meta.yml"):
            tid = meta_path.parent.name
            cur_type_mtimes[tid] = meta_path.stat().st_mtime
            if prev_type_mtimes.get(tid) != cur_type_mtimes[tid]:
                invalidated_types.add(tid)

    new_entries: dict[str, dict] = {}

    for entry in marker["methodologies"]:
        mid = entry["id"]
        if mid not in flow_resolver:
            continue
        scope = (marker_dir / entry["root"]).resolve()
        if not scope.is_dir():
            continue
        for md in sorted(scope.rglob("*.md")):
            md_key = str(md)
            cur_mtime = md.stat().st_mtime
            prev_entry = prev_entries.get(md_key)

            # Skip when cache hit AND nothing higher invalidates this entry
            can_skip = (
                use_cache
                and not marker_changed
                and mid not in invalidated_flows
                and prev_entry is not None
                and prev_entry.get("mtime") == cur_mtime
                and prev_entry.get("flow") == mid
                and prev_entry.get("type") not in invalidated_types
            )
            if can_skip:
                # Replay stashed findings (none for clean docs)
                for f in prev_entry.get("findings", []) or []:
                    report.add(Finding(**f))
                new_entries[md_key] = prev_entry
            else:
                before = len(report.findings)
                cmd_instance(md, marker, marker_dir, flow_resolver, report,
                             cross_flow_edges_mode=cross_flow_edges_mode,
                             library_types_root=library_types_root)
                new_findings = report.findings[before:]
                # Snapshot the doc's type (best-effort, for type-invalidation matrix)
                doc_type = None
                fm = extract_frontmatter(md, Report())
                if fm:
                    doc_type = (fm.get("ddx") or {}).get("type")
                new_entries[md_key] = {
                    "mtime": cur_mtime,
                    "flow": mid,
                    "type": doc_type,
                    "findings": [
                        {"code": f.code, "msg": f.msg, "file": f.file, "line": f.line}
                        for f in new_findings
                    ],
                }
            _DOCS_SCANNED["count"] += 1
            _ceiling_check()

    if use_cache:
        _save_disk_cache(marker_dir, {
            "marker_mtime": cur_marker_mtime,
            "graph_mtimes": cur_graph_mtimes,
            "type_mtimes": cur_type_mtimes,
            "entries": new_entries,
        })


# ─────────────────────────────────────────────────────────────────────────────
# CLI

def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="helix_check.py")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_marker = sub.add_parser("marker")
    p_marker.add_argument("marker_path", type=Path)
    # v2 flag name is `--flow`; `--methodology` retained as deprecated alias for one cycle.
    p_marker.add_argument("--flow", "--methodology", action="append", default=[], dest="flow",
                          help="<id>=<path-to-flow-root>, repeatable")
    p_marker.add_argument("--library-types", type=Path)
    p_marker.add_argument("--strict", action="store_true")
    p_marker.add_argument("--json", action="store_true")
    p_marker.add_argument("--no-instance", action="store_true")
    p_marker.add_argument("--cross-flow-edges", "--cross-methodology-edges",
                          dest="cross_flow_edges",
                          choices=["allow", "warn", "deny"], default="warn")
    p_marker.add_argument("--allow-empty-scope", action="store_true")
    p_marker.add_argument("--ceiling-s", type=float, default=None,
                          help="abort with exit=5 if wall-clock exceeds N seconds")
    p_marker.add_argument("--use-cache", action="store_true",
                          help="enable on-disk .helix/index.json incremental cache (F4)")

    p_graph = sub.add_parser("graph")
    p_graph.add_argument("flow_root", type=Path)
    p_graph.add_argument("--library-types", type=Path)
    p_graph.add_argument("--strict", action="store_true")
    p_graph.add_argument("--json", action="store_true")

    p_inst = sub.add_parser("instance")
    p_inst.add_argument("doc", type=Path)
    p_inst.add_argument("--marker", type=Path, required=True)
    p_inst.add_argument("--flow", "--methodology", action="append", default=[], dest="flow")
    p_inst.add_argument("--library-types", type=Path)
    p_inst.add_argument("--strict", action="store_true")
    p_inst.add_argument("--json", action="store_true")
    p_inst.add_argument("--cross-flow-edges", "--cross-methodology-edges",
                        dest="cross_flow_edges",
                        choices=["allow", "warn", "deny"], default="warn")

    p_type = sub.add_parser("type")
    p_type.add_argument("types_root", type=Path)
    p_type.add_argument("--strict", action="store_true")
    p_type.add_argument("--json", action="store_true")

    p_example = sub.add_parser("example")
    p_example.add_argument("example_root", type=Path, nargs="?", default=None,
                           help="path to worked example root (contains fixtures/ and docs/)")
    p_example.add_argument("--adversarial-coverage", action="store_true",
                           help="assert every fixture under <root>/fixtures/ is referenced by >=1 artifact")
    p_example.add_argument("--strict", action="store_true")
    p_example.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    report = Report()

    def parse_flows(items: list[str]) -> dict[str, Path]:
        out = {}
        for it in items:
            if "=" not in it:
                report.add_code("R010", f"--flow requires <id>=<path>, got `{it}`")
                continue
            mid, path = it.split("=", 1)
            out[mid] = Path(path)
        return out

    if args.cmd == "marker":
        global _CEILING_S, _START_T
        _CEILING_S = args.ceiling_s
        _START_T = time.monotonic()
        _DOCS_SCANNED["count"] = 0
        resolver = parse_flows(args.flow)
        cmd_marker(args.marker_path, resolver, args.library_types, report,
                   no_instance=args.no_instance,
                   cross_flow_edges_mode=args.cross_flow_edges,
                   allow_empty_scope=args.allow_empty_scope,
                   use_cache=args.use_cache)
    elif args.cmd == "graph":
        graph_path = args.flow_root / "workflows/graph.yml"
        cmd_graph(graph_path, args.library_types, report)
    elif args.cmd == "instance":
        # Need the marker context
        marker = load_yaml(args.marker, report, "M001")
        if marker is not None and validate_marker_schema(marker, args.marker, args.marker.parent.resolve(), report):
            resolver = parse_flows(args.flow)
            marker.setdefault("_installed", list(resolver.keys()))
            cmd_instance(args.doc, marker, args.marker.parent.resolve(), resolver, report,
                         cross_flow_edges_mode=args.cross_flow_edges,
                         library_types_root=args.library_types)
    elif args.cmd == "type":
        cmd_type(args.types_root, report)
    elif args.cmd == "example":
        if args.example_root is None:
            report.add_code("R010", "example subcommand requires <example_root> positional arg")
        elif args.adversarial_coverage:
            cmd_example_adversarial_coverage(args.example_root, report)
        else:
            report.add_code("R010", "example subcommand requires --adversarial-coverage flag (no other mode implemented)")
    else:
        return EXIT_U

    if args.json:
        print(json.dumps(report.to_json(args.strict), indent=2))
    else:
        print(report.render(args.strict))

    return report.exit_code(args.strict)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
