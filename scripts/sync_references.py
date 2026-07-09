#!/usr/bin/env python3
"""sync_references — materialize the generated skill-adjacent catalog floor.

Source checkouts keep the methodology catalog under `workflows/`. Installed
skill packages need the same catalog adjacent to SKILL.md so §Catalog Resolution
can always bind a graph/template in consumer repos. This script materializes
that generated package floor.

This script copies the catalog the skill binds at authoring time into a
package-local `references/` directory:

    workflows/graph.yml    -> references/graph.yml
    workflows/activities/  -> references/activities/   (templates/prompts/examples)
    workflows/voice.yml    -> references/voice.yml
    workflows/concerns/    -> references/concerns/

Single source of truth: edit under `workflows/`, regenerate graph.yml
(scripts/generate_graph.py), then build/validate the plugin package. Drift
between generated references and `workflows/` is a validation failure.

Usage:
    python3 scripts/sync_references.py [OUTPUT_DIR]

OUTPUT_DIR defaults to dist/plugin-package/helix/skills/helix/references.
validate-skills.sh passes a temp dir and diffs the generated package floor
against that expected output.
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
]
TREES = [
    ("workflows/activities", "activities"),
    ("workflows/concerns", "concerns"),
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


def main(argv: list[str]) -> int:
    out_dir = Path(argv[1]).resolve() if len(argv) > 1 else DEFAULT_OUT
    return sync(out_dir)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
