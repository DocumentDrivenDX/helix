#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path


@dataclass
class RequireEdge:
    path: str | None
    edge_type: str | None
    line: int


@dataclass
class ArtifactMeta:
    artifact_id: str
    slug: str
    creation_order: Decimal
    meta_path: Path
    requires: list[RequireEdge]


def normalize_scalar(value: str) -> str:
    normalized = value.strip()
    if normalized and normalized[0] not in {"'", '"'} and " #" in normalized:
        normalized = normalized.split(" #", 1)[0].rstrip()
    if len(normalized) >= 2 and normalized[0] == normalized[-1] and normalized[0] in {"'", '"'}:
        normalized = normalized[1:-1]
    return normalized


def split_key_value(line: str, meta_path: Path, line_number: int) -> tuple[str, str]:
    if ":" not in line:
        raise ValueError(f"{meta_path}:{line_number}: expected key:value pair, got {line!r}")
    key, value = line.split(":", 1)
    return key.strip(), normalize_scalar(value)


def parse_meta(meta_path: Path) -> ArtifactMeta:
    artifact_id: str | None = None
    creation_order: Decimal | None = None
    requires: list[RequireEdge] = []

    section: str | None = None
    subsection: str | None = None
    current_require: dict[str, str | int] | None = None

    lines = meta_path.read_text(encoding="utf-8").splitlines()
    for line_number, raw_line in enumerate(lines, start=1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))

        if indent == 0:
            if current_require is not None:
                requires.append(
                    RequireEdge(
                        path=current_require.get("path"),  # type: ignore[arg-type]
                        edge_type=current_require.get("type"),  # type: ignore[arg-type]
                        line=int(current_require["line"]),
                    )
                )
                current_require = None

            section = stripped[:-1] if stripped.endswith(":") else None
            subsection = None
            continue

        if section == "artifact" and indent == 2 and stripped.startswith("id:"):
            _, value = split_key_value(stripped, meta_path, line_number)
            artifact_id = value
            continue

        if section == "workflow" and indent == 2 and stripped.startswith("creation_order:"):
            _, value = split_key_value(stripped, meta_path, line_number)
            try:
                creation_order = Decimal(value)
            except InvalidOperation as exc:
                raise ValueError(
                    f"{meta_path}:{line_number}: workflow.creation_order must be numeric, got {value!r}"
                ) from exc
            continue

        if section != "dependencies":
            continue

        if indent == 2 and stripped == "requires:":
            subsection = "requires"
            continue

        if indent == 2 and stripped.endswith(":") and stripped != "requires:":
            if current_require is not None:
                requires.append(
                    RequireEdge(
                        path=current_require.get("path"),  # type: ignore[arg-type]
                        edge_type=current_require.get("type"),  # type: ignore[arg-type]
                        line=int(current_require["line"]),
                    )
                )
                current_require = None
            subsection = None
            continue

        if subsection != "requires":
            continue

        if indent == 4 and stripped.startswith("- "):
            if current_require is not None:
                requires.append(
                    RequireEdge(
                        path=current_require.get("path"),  # type: ignore[arg-type]
                        edge_type=current_require.get("type"),  # type: ignore[arg-type]
                        line=int(current_require["line"]),
                    )
                )
            current_require = {"line": line_number}
            inline_mapping = stripped[2:].strip()
            if inline_mapping:
                key, value = split_key_value(inline_mapping, meta_path, line_number)
                current_require[key] = value
            continue

        if indent >= 6 and current_require is not None and ":" in stripped:
            key, value = split_key_value(stripped, meta_path, line_number)
            current_require[key] = value
            continue

        if indent <= 4 and current_require is not None:
            requires.append(
                RequireEdge(
                    path=current_require.get("path"),  # type: ignore[arg-type]
                    edge_type=current_require.get("type"),  # type: ignore[arg-type]
                    line=int(current_require["line"]),
                )
            )
            current_require = None

    if current_require is not None:
        requires.append(
            RequireEdge(
                path=current_require.get("path"),  # type: ignore[arg-type]
                edge_type=current_require.get("type"),  # type: ignore[arg-type]
                line=int(current_require["line"]),
            )
        )

    if artifact_id is None:
        raise ValueError(f"{meta_path}: missing artifact.id")
    if creation_order is None:
        raise ValueError(f"{meta_path}: missing workflow.creation_order")

    return ArtifactMeta(
        artifact_id=artifact_id,
        slug=meta_path.parent.name,
        creation_order=creation_order,
        meta_path=meta_path,
        requires=requires,
    )


def load_artifacts(artifacts_dir: Path) -> list[ArtifactMeta]:
    if not artifacts_dir.is_dir():
        raise ValueError(f"{artifacts_dir}: artifacts directory does not exist")

    artifacts: list[ArtifactMeta] = []
    for meta_path in sorted(artifacts_dir.glob("*/meta.yml")):
        artifacts.append(parse_meta(meta_path))

    if not artifacts:
        raise ValueError(f"{artifacts_dir}: no deploy artifact metadata found")

    return artifacts


def find_cycle(adjacency: dict[str, set[str]]) -> list[str] | None:
    state: dict[str, int] = {node: 0 for node in adjacency}
    stack: list[str] = []

    def visit(node: str) -> list[str] | None:
        state[node] = 1
        stack.append(node)

        for neighbor in sorted(adjacency[node]):
            if state[neighbor] == 0:
                cycle = visit(neighbor)
                if cycle is not None:
                    return cycle
            elif state[neighbor] == 1:
                start = stack.index(neighbor)
                return stack[start:] + [neighbor]

        stack.pop()
        state[node] = 2
        return None

    for node in sorted(adjacency):
        if state[node] == 0:
            cycle = visit(node)
            if cycle is not None:
                return cycle
    return None


def validate_artifacts(artifacts: list[ArtifactMeta]) -> list[str]:
    errors: list[str] = []
    artifact_by_key: dict[str, ArtifactMeta] = {}

    for artifact in artifacts:
        for key in (artifact.artifact_id, artifact.slug):
            existing = artifact_by_key.get(key)
            if existing is not None and existing.meta_path != artifact.meta_path:
                errors.append(
                    f"{artifact.meta_path}: duplicate deploy artifact key {key!r} already defined by {existing.meta_path}"
                )
            artifact_by_key[key] = artifact

    adjacency: dict[str, set[str]] = {artifact.artifact_id: set() for artifact in artifacts}
    checked_edges = 0

    for artifact in artifacts:
        for require in artifact.requires:
            if require.path is None:
                continue
            if require.edge_type not in {None, "", "artifact"}:
                continue

            target = artifact_by_key.get(require.path)
            if target is None:
                continue

            checked_edges += 1
            adjacency[artifact.artifact_id].add(target.artifact_id)

            if target.creation_order > artifact.creation_order:
                errors.append(
                    f"{artifact.meta_path}:{require.line}: {artifact.artifact_id} requires later deploy artifact "
                    f"{target.artifact_id} (order {artifact.creation_order} -> {target.creation_order})"
                )

    cycle = find_cycle(adjacency)
    if cycle is not None:
        errors.append(
            "deploy artifact dependency cycle detected: " + " -> ".join(cycle)
        )

    if not errors:
        print(
            f"validated deploy artifact graph: {len(artifacts)} artifacts, {checked_edges} intra-phase requires edges"
        )

    return errors


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[1]
    default_artifacts_dir = repo_root / "workflows" / "phases" / "05-deploy" / "artifacts"

    parser = argparse.ArgumentParser(
        description="Validate 05-deploy artifact creation-order consistency and dependency cycles."
    )
    parser.add_argument(
        "--artifacts-dir",
        type=Path,
        default=default_artifacts_dir,
        help="Path to the 05-deploy artifacts directory (defaults to the repo deploy artifacts).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        artifacts = load_artifacts(args.artifacts_dir)
        errors = validate_artifacts(artifacts)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
