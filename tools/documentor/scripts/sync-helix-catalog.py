#!/usr/bin/env python3
"""Refresh the HELIX catalog data this package carries from the HELIX repository it lives in.

Usage:
    sync-helix-catalog.py                          copy from the HELIX repository this package lives in
    sync-helix-catalog.py --check                  fail when the packaged copy differs from it

documentor lives in the HELIX repository (`tools/documentor/`). HELIX owns the audiences (`workflows/publish/audiences/*.yml`) and the voice profiles
(`workflows/voice.yml`); documentor reads them from `src/documentor/catalog/helix/` and records
which HELIX version they came from in `HELIX_VERSION`. Everything else in the catalog is documentor's. The copy is packaged so a
git-subdirectory install carries it; `--check` (run by the tests) keeps it equal to the source.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
TARGET = HERE / "src" / "documentor" / "catalog" / "helix"
REPO = "https://github.com/DocumentDrivenDX/helix.git"


def copy_from(checkout: Path, label: str) -> None:
    audiences = checkout / "workflows" / "publish" / "audiences"
    if not audiences.is_dir():
        audiences = checkout / "workflows" / "publish" / "flows"  # HELIX before the rename
    if not audiences.is_dir() or not (checkout / "workflows" / "voice.yml").is_file():
        sys.exit(f"{checkout}: no workflows/publish/audiences (or flows) and workflows/voice.yml")
    shutil.rmtree(TARGET / "audiences", ignore_errors=True)
    shutil.copytree(audiences, TARGET / "audiences")
    shutil.copy2(checkout / "workflows" / "voice.yml", TARGET / "voice.yml")
    (TARGET / "HELIX_VERSION").write_text(label + "\n", encoding="utf-8")
    print(f"synced {len(list((TARGET / 'audiences').glob('*.yml')))} audiences and voice.yml from HELIX {label}")


def same(checkout: Path) -> list[str]:
    """The packaged files that differ from the HELIX repository's."""
    import filecmp

    src = checkout / "workflows" / "publish" / "audiences"
    differ = [f"audiences/{f.name}" for f in sorted(src.glob("*.yml"))
              if not (TARGET / "audiences" / f.name).is_file() or not filecmp.cmp(f, TARGET / "audiences" / f.name, shallow=False)]
    differ += [f"audiences/{f.name} (extra)" for f in sorted((TARGET / "audiences").glob("*.yml")) if not (src / f.name).is_file()]
    if not filecmp.cmp(checkout / "workflows" / "voice.yml", TARGET / "voice.yml", shallow=False):
        differ.append("voice.yml")
    return differ


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    checkout = HERE.parent.parent
    if not (checkout / "workflows" / "voice.yml").is_file():
        sys.exit(f"{checkout}: not a HELIX checkout (no workflows/voice.yml)")
    if args.check:
        differ = same(checkout)
        for d in differ:
            print(f"stale: src/documentor/catalog/helix/{d}; run scripts/sync-helix-catalog.py", file=sys.stderr)
        if not differ:
            print("the packaged HELIX catalog matches workflows/")
        return 1 if differ else 0
    copy_from(checkout, "in-repo")
    return 0


if __name__ == "__main__":
    sys.exit(main())
