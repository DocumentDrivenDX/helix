#!/usr/bin/env python3
"""sync_references — materialize the generated skill-adjacent catalog floor.

Source checkouts keep the methodology catalog under `workflows/`. Installed
skill packages need the same catalog adjacent to SKILL.md so §Catalog Resolution
can always bind a graph/template in consumer repos. This script materializes
that generated package floor.

This script copies the catalog the skill binds at authoring time into a
package-local `references/` directory:

    workflows/graph.yml    -> references/graph.yml
    workflows/voice.yml    -> references/voice.yml
    workflows/stop-triggers.yml -> references/stop-triggers.yml (stop_at floor)
    workflows/principles.md -> references/principles.md (default principles)
    workflows/activities/  -> references/activities/   (templates/prompts/examples)
    workflows/concerns/    -> references/concerns/
    workflows/modes/       -> references/modes/       (mode contracts)
    workflows/actions/     -> references/actions/     (action procedures)
    workflows/templates/   -> references/templates/   (report templates)
    workflows/deliverables/-> references/deliverables/ (theme, slide patterns, mappings)
    workflows/references/  -> references/references/   (shared references the actions cite)
    workflows/publish/     -> references/publish/      (the guide's audiences)

Single source of truth: edit under `workflows/`, regenerate graph.yml
(scripts/generate_graph.py), then build/validate the plugin package. Drift
between generated references and `workflows/` is a validation failure.

Usage:
    python3 scripts/sync_references.py [OUTPUT_DIR]
    python3 scripts/sync_references.py --subset documentor [--check] [OUTPUT_DIR]

OUTPUT_DIR defaults to dist/plugin-package/helix/skills/helix/references.
validate-skills.sh passes a temp dir and diffs the generated package floor
against that expected output.

`--subset documentor` writes the part of the catalog the documentation tool reads, in the same
layout as `workflows/` (publish/, voice.yml, deliverables/, the two references the guide and the
writing pass live in), to tools/documentor/src/documentor/catalog/helix by default. The copy carries no version of its
own: documentor is released with HELIX at the same version. `--check` writes nothing and fails when that copy differs from `workflows/`.
One script defines every packaged floor, so the skill's and the tool's cannot drift apart.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO_ROOT / "dist" / "plugin-package" / "helix" / "skills" / "helix" / "references"

# (source relative to repo root, destination name under the floor)
FILES = [
    ("workflows/graph.yml", "graph.yml"),
    ("workflows/voice.yml", "voice.yml"),
    ("workflows/stop-triggers.yml", "stop-triggers.yml"),
    ("workflows/principles.md", "principles.md"),
]
TREES = [
    ("workflows/activities", "activities"),
    ("workflows/concerns", "concerns"),
    ("workflows/modes", "modes"),
    ("workflows/actions", "actions"),
    ("workflows/templates", "templates"),
    ("workflows/deliverables", "deliverables"),
    ("workflows/references", "references"),
    ("workflows/publish", "publish"),
]


def sync(out_dir: Path) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)

    for src_rel, dst_name in FILES:
        src = REPO_ROOT / src_rel
        if not src.is_file():
            print(f"error: {src_rel} not found", file=sys.stderr)
            return 1
        shutil.copy2(src, out_dir / dst_name)

    for src_rel, dst_name in TREES:
        src = REPO_ROOT / src_rel
        if not src.is_dir():
            print(f"error: {src_rel} not found", file=sys.stderr)
            return 1
        dst = out_dir / dst_name
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)

    rel = out_dir.relative_to(REPO_ROOT) if out_dir.is_relative_to(REPO_ROOT) else out_dir
    print(f"synced catalog floor -> {rel}: "
          f"{len(FILES)} files, {len(TREES)} trees")
    return 0


DOCUMENTOR_OUT = REPO_ROOT / "tools" / "documentor" / "src" / "documentor" / "catalog" / "helix"
DOCUMENTOR_FILES = [
    ("workflows/voice.yml", "voice.yml"),
    ("workflows/references/publishing.md", "references/publishing.md"),
    ("workflows/references/writing-pass.md", "references/writing-pass.md"),
    ("workflows/references/architecture-model.md", "references/architecture-model.md"),
    ("workflows/references/umf-schemas.md", "references/umf-schemas.md"),
]
DOCUMENTOR_TREES = [
    ("workflows/publish", "publish"),
    ("workflows/deliverables", "deliverables"),
]


def _documentor_expected() -> dict[str, bytes]:
    """Every file the documentor floor holds, by its path in the floor, with its bytes."""
    found: dict[str, bytes] = {}
    for src_rel, dst in DOCUMENTOR_FILES:
        found[dst] = (REPO_ROOT / src_rel).read_bytes()
    for src_rel, dst in DOCUMENTOR_TREES:
        for path in sorted((REPO_ROOT / src_rel).rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                found[f"{dst}/{path.relative_to(REPO_ROOT / src_rel).as_posix()}"] = path.read_bytes()
    return found


def sync_documentor(out_dir: Path, check: bool) -> int:
    expected = _documentor_expected()
    if check:
        present = {p.relative_to(out_dir).as_posix(): p.read_bytes() for p in out_dir.rglob("*")
                   if p.is_file() and "__pycache__" not in p.parts} if out_dir.is_dir() else {}
        stale = sorted(k for k in expected if present.get(k) != expected[k])
        extra = sorted(k for k in present if k not in expected)
        for k in stale:
            print(f"stale: {k}", file=sys.stderr)
        for k in extra:
            print(f"extra: {k}", file=sys.stderr)
        if stale or extra:
            print("the documentor floor differs from workflows/; run scripts/sync_references.py --subset documentor",
                  file=sys.stderr)
            return 1
        print(f"documentor floor matches workflows/: {len(expected)} files")
        return 0
    if out_dir.exists():
        shutil.rmtree(out_dir)
    for rel, data in expected.items():
        target = out_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    print(f"synced documentor floor -> {out_dir.relative_to(REPO_ROOT)}: {len(expected)} files")
    return 0


def main(argv: list[str]) -> int:
    args = argv[1:]
    if args[:2] == ["--subset", "documentor"]:
        rest = args[2:]
        check = "--check" in rest
        rest = [a for a in rest if a != "--check"]
        return sync_documentor(Path(rest[0]).resolve() if rest else DOCUMENTOR_OUT, check)
    out_dir = Path(args[0]).resolve() if args else DEFAULT_OUT
    return sync(out_dir)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
