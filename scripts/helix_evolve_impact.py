#!/usr/bin/env python3
"""Compute HELIX Evolve impact sets from instance frontmatter links.

Evolve is primarily a skill workflow, not a standalone CLI. This helper provides
the deterministic graph-discovery core used by tests and release evidence:
canonical ``ddx.links`` is preferred, with explicit read-only fallback for the
legacy fields supported by the skill contract.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - exercised by shell validators.
    raise SystemExit("PyYAML is required for HELIX frontmatter parsing") from exc


UPSTREAM_KINDS = {"depends_on", "requires", "informed_by", "references"}
DOWNSTREAM_KINDS = {"informs", "contains", "enables", "referenced_by"}


@dataclass(frozen=True)
class Artifact:
    id: str
    path: Path
    frontmatter: dict[str, Any]


@dataclass(frozen=True)
class Edge:
    source: str
    target: str
    field: str
    direction: str
    kind: str


def read_frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    data = yaml.safe_load(text[4:end]) or {}
    return data if isinstance(data, dict) else {}


def artifact_id(frontmatter: dict[str, Any]) -> str | None:
    ddx = frontmatter.get("ddx")
    if isinstance(ddx, dict) and isinstance(ddx.get("id"), str):
        return ddx["id"]
    value = frontmatter.get("id")
    return value if isinstance(value, str) else None


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def target_from_link(value: Any) -> tuple[str | None, str]:
    if isinstance(value, str):
        return value, "depends_on"
    if isinstance(value, dict):
        target = value.get("to") or value.get("target") or value.get("id")
        kind = value.get("kind") or "depends_on"
        if isinstance(target, str):
            return target, str(kind)
    return None, "depends_on"


def collect_artifacts(docs_root: Path) -> dict[str, Artifact]:
    artifacts: dict[str, Artifact] = {}
    for path in sorted(docs_root.rglob("*.md")):
        frontmatter = read_frontmatter(path)
        ident = artifact_id(frontmatter)
        if ident:
            artifacts[ident] = Artifact(ident, path, frontmatter)
    return artifacts


def add_edge(
    edges: list[Edge],
    source: str,
    target: str,
    field: str,
    direction: str,
    kind: str,
) -> None:
    if target:
        edges.append(Edge(source, target, field, direction, kind))


def collect_edges(artifacts: dict[str, Artifact]) -> tuple[list[Edge], dict[str, list[str]]]:
    edges: list[Edge] = []
    warnings: dict[str, list[str]] = defaultdict(list)

    for artifact in artifacts.values():
        fm = artifact.frontmatter
        ddx = fm.get("ddx") if isinstance(fm.get("ddx"), dict) else {}
        canonical_present = "links" in ddx

        if canonical_present:
            legacy_fields = [
                name
                for name, present in (
                    ("ddx.depends_on", "depends_on" in ddx),
                    ("depends_on", "depends_on" in fm),
                    ("relationships", "relationships" in fm),
                )
                if present
            ]
            if legacy_fields:
                warnings[artifact.id].append(
                    "canonical ddx.links present; ignored legacy fields: "
                    + ", ".join(legacy_fields)
                )

            for item in as_list(ddx.get("links")):
                target, kind = target_from_link(item)
                if not target:
                    continue
                direction = "downstream" if kind in DOWNSTREAM_KINDS else "upstream"
                add_edge(edges, artifact.id, target, "ddx.links", direction, kind)
            continue

        for target in as_list(ddx.get("depends_on")):
            if isinstance(target, str):
                add_edge(edges, artifact.id, target, "ddx.depends_on", "upstream", "depends_on")

        for target in as_list(fm.get("depends_on")):
            if isinstance(target, str):
                add_edge(edges, artifact.id, target, "depends_on", "upstream", "depends_on")

        relationships = fm.get("relationships")
        if isinstance(relationships, dict):
            for target in as_list(relationships.get("depends_on")):
                if isinstance(target, str):
                    add_edge(
                        edges,
                        artifact.id,
                        target,
                        "relationships.depends_on",
                        "upstream",
                        "depends_on",
                    )
            for key in ("informs", "referenced_by"):
                for target in as_list(relationships.get(key)):
                    if isinstance(target, str):
                        add_edge(edges, artifact.id, target, f"relationships.{key}", "downstream", key)

    return edges, dict(warnings)


def build_adjacency(edges: list[Edge]) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    upstream: dict[str, set[str]] = defaultdict(set)
    downstream: dict[str, set[str]] = defaultdict(set)
    for edge in edges:
        if edge.direction == "downstream":
            downstream[edge.source].add(edge.target)
            upstream[edge.target].add(edge.source)
        else:
            upstream[edge.source].add(edge.target)
            downstream[edge.target].add(edge.source)
    return upstream, downstream


def reachable(start: str, graph: dict[str, set[str]], known_ids: set[str]) -> list[str]:
    seen: set[str] = set()
    stack = sorted(graph.get(start, set()))
    while stack:
        current = stack.pop()
        if current in seen:
            continue
        seen.add(current)
        for nxt in sorted(graph.get(current, set()), reverse=True):
            if nxt not in seen:
                stack.append(nxt)
    return sorted(item for item in seen if item in known_ids)


def compute(docs_root: Path, entry: str) -> dict[str, Any]:
    artifacts = collect_artifacts(docs_root)
    if entry not in artifacts:
        raise SystemExit(f"entry artifact not found: {entry}")
    edges, warnings = collect_edges(artifacts)
    upstream_graph, downstream_graph = build_adjacency(edges)
    known_ids = set(artifacts)
    used_fields = sorted({edge.field for edge in edges})
    entry_edges = [
        edge
        for edge in edges
        if edge.source == entry or edge.target == entry
    ]

    return {
        "entry": entry,
        "docs_root": str(docs_root),
        "artifact_count": len(artifacts),
        "edge_count": len(edges),
        "edge_fields": used_fields,
        "upstream": reachable(entry, upstream_graph, known_ids),
        "downstream": reachable(entry, downstream_graph, known_ids),
        "entry_edges": [edge.__dict__ for edge in entry_edges],
        "compatibility_warnings": warnings,
        "reviewed_by": "scripts/helix_evolve_impact.py",
    }


def render_markdown(result: dict[str, Any]) -> str:
    def bullets(items: list[str]) -> str:
        return "\n".join(f"- {item}" for item in items) if items else "- none"

    return "\n".join(
        [
            "# HELIX Evolve Impact Set",
            "",
            f"- entry: `{result['entry']}`",
            f"- artifacts reviewed: {result['artifact_count']}",
            f"- graph edges reviewed: {result['edge_count']}",
            f"- edge fields: {', '.join(result['edge_fields']) or 'none'}",
            f"- reviewed by: `{result['reviewed_by']}`",
            "",
            "## Upstream Impact",
            "",
            bullets(result["upstream"]),
            "",
            "## Downstream Impact",
            "",
            bullets(result["downstream"]),
            "",
        ]
    )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--docs-root", required=True, type=Path)
    parser.add_argument("--entry", required=True)
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--require-upstream", action="store_true")
    parser.add_argument("--require-downstream", action="store_true")
    parser.add_argument("--expect-edge-field", action="append", default=[])
    args = parser.parse_args(argv)

    result = compute(args.docs_root.resolve(), args.entry)
    fields = set(result["edge_fields"])
    missing_fields = [field for field in args.expect_edge_field if field not in fields]
    if missing_fields:
        raise SystemExit(f"expected edge field(s) not used: {', '.join(missing_fields)}")
    if args.require_upstream and not result["upstream"]:
        raise SystemExit("expected non-empty upstream impact set")
    if args.require_downstream and not result["downstream"]:
        raise SystemExit("expected non-empty downstream impact set")

    if args.format == "markdown":
        print(render_markdown(result), end="")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
