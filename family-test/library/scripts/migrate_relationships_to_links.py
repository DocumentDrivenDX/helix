#!/usr/bin/env python3
"""migrate_relationships_to_links.py — legacy frontmatter → ddx.links migrator.

Translates legacy instance-frontmatter keys into the new `ddx.links:` shape:

  relationships:
    informs: [FEAT-001, FEAT-002]
    depends_on: [PRD-001]
    referenced_by: [TEST-001]           # dropped — inverse view, not authoritative
  depends_on: [PRD-002]                  # top-level legacy

becomes

  ddx:
    links:
      - { kind: informs,  to: FEAT-001 }
      - { kind: informs,  to: FEAT-002 }
      - { kind: requires, to: PRD-001 }
      - { kind: requires, to: PRD-002 }

Behaviour:
  * `--dry-run` (default) — print proposed edits, write nothing.
  * `--apply`            — write edits in-place, preserving key order and unknown keys.
  * `--require-clean`    — CI gate: dry-run + non-zero exit if any edits would be proposed.

Preservation:
  * Top-level frontmatter key order preserved via insertion-ordered dict + sort_keys=False.
  * Unknown top-level keys (vendor x-*, custom blocks) pass through untouched.
  * Body content (everything after the closing `---`) is byte-preserved.
  * If the file already has `ddx.links:`, new entries are appended (no duplicates by
    (kind, to)); existing entries are not reordered.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

# Mapping from legacy relationship key → ddx.links kind.
# Design §5.4 + §6.1.1: depends_on → requires, informs → informs.
# referenced_by is the inverse view of informs; the new model has no inverse
# edges (design §6.1 removed `referenced_by` from the layer). We DROP it.
LEGACY_REL_TO_KIND = {
    "informs": "informs",
    "depends_on": "requires",
    "requires": "requires",
}
LEGACY_REL_DROP = {"referenced_by"}


_FRONTMATTER_RE = re.compile(r"^(---\s*\n)(.*?)(\n---\s*\n)", re.DOTALL)


@dataclass
class FileEdit:
    path: Path
    proposed_links: list[dict[str, str]] = field(default_factory=list)
    removed_top_keys: list[str] = field(default_factory=list)
    removed_rel_subkeys: list[str] = field(default_factory=list)
    dropped_subkeys: list[str] = field(default_factory=list)  # referenced_by etc.
    new_frontmatter_yaml: str = ""
    original_frontmatter_yaml: str = ""

    @property
    def has_changes(self) -> bool:
        return bool(self.proposed_links or self.removed_top_keys
                    or self.removed_rel_subkeys or self.dropped_subkeys)


def _ordered_load(yaml_text: str) -> dict:
    """Load YAML preserving key order (PyYAML safe_load already preserves insertion
    order in Python 3.7+ since dicts are insertion-ordered)."""
    return yaml.safe_load(yaml_text) or {}


def _dump_yaml(data: dict) -> str:
    """Dump YAML preserving key order; no aliases; block style."""
    return yaml.safe_dump(
        data,
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=True,
    )


def _normalize_link_list(items: Any) -> list[str]:
    """Normalize a legacy list field (informs/depends_on) to list[str].

    Accepts None, str, list[str], list[dict]. Each entry must yield an id-ish
    string; dicts are inspected for an `id:` or `to:` key.
    """
    if items is None:
        return []
    if isinstance(items, str):
        return [items.strip()]
    out: list[str] = []
    if isinstance(items, list):
        for it in items:
            if isinstance(it, str):
                if it.strip():
                    out.append(it.strip())
            elif isinstance(it, dict):
                # legacy dict form: {id: FOO, kind: ...} — pull the id-ish field
                v = it.get("id") or it.get("to") or it.get("ref")
                if isinstance(v, str) and v.strip():
                    out.append(v.strip())
    return out


def plan_edit(path: Path) -> FileEdit | None:
    """Inspect one markdown file. Return a FileEdit if changes are proposed, else None."""
    try:
        text = path.read_text()
    except Exception:
        return None
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return None
    fm_text = m.group(2)
    try:
        fm = _ordered_load(fm_text)
    except yaml.YAMLError:
        return None
    if not isinstance(fm, dict):
        return None

    edit = FileEdit(path=path, original_frontmatter_yaml=fm_text)

    # Gather legacy entries
    proposed: list[tuple[str, str]] = []  # (kind, to)

    rel = fm.get("relationships")
    rel_removed_subkeys: list[str] = []
    rel_dropped_subkeys: list[str] = []
    if isinstance(rel, dict):
        for subkey, value in list(rel.items()):
            if subkey in LEGACY_REL_DROP:
                rel_dropped_subkeys.append(subkey)
                continue
            if subkey in LEGACY_REL_TO_KIND:
                kind = LEGACY_REL_TO_KIND[subkey]
                for tgt in _normalize_link_list(value):
                    proposed.append((kind, tgt))
                rel_removed_subkeys.append(subkey)
            else:
                # Unknown subkey under relationships — leave it (don't drop silently).
                pass

    # Top-level legacy depends_on
    removed_top: list[str] = []
    if "depends_on" in fm:
        for tgt in _normalize_link_list(fm.get("depends_on")):
            proposed.append(("requires", tgt))
        removed_top.append("depends_on")

    if not proposed and not rel_dropped_subkeys and not removed_top and not rel_removed_subkeys:
        return None

    # Merge into ddx.links (deduplicate by (kind, to))
    ddx = fm.get("ddx")
    if not isinstance(ddx, dict):
        ddx = {}
    existing_links = ddx.get("links")
    if not isinstance(existing_links, list):
        existing_links = []
    seen: set[tuple[str, str]] = set()
    final_links: list[dict[str, str]] = []
    # Preserve existing first
    for entry in existing_links:
        if isinstance(entry, dict):
            k = entry.get("kind")
            t = entry.get("to")
            if isinstance(k, str) and isinstance(t, str):
                seen.add((k, t))
            final_links.append(entry)
    # Append new
    new_entries: list[dict[str, str]] = []
    for kind, tgt in proposed:
        key = (kind, tgt)
        if key in seen:
            continue
        seen.add(key)
        entry = {"kind": kind, "to": tgt}
        final_links.append(entry)
        new_entries.append(entry)

    if not new_entries and not rel_dropped_subkeys and not removed_top and not rel_removed_subkeys:
        # Nothing actually changes (all legacy values were already in ddx.links).
        # Still strip the legacy keys though.
        pass

    # Build the new frontmatter dict, preserving top-level key order.
    new_fm: dict = {}
    for k, v in fm.items():
        if k == "relationships":
            # Keep only unknown subkeys (not migrated, not dropped).
            if isinstance(v, dict):
                surviving = {
                    sk: sv for sk, sv in v.items()
                    if sk not in LEGACY_REL_TO_KIND and sk not in LEGACY_REL_DROP
                }
                if surviving:
                    new_fm["relationships"] = surviving
            # else: scalar/list — leave behavior alone (drop, since it's malformed)
            continue
        if k == "depends_on":
            # Migrated to ddx.links — drop top-level.
            continue
        if k == "ddx":
            # Will be rewritten below to include links.
            continue
        new_fm[k] = v

    # Place ddx (with links) in the original position if it existed; else append.
    new_ddx: dict = {}
    if isinstance(ddx, dict):
        for k, v in ddx.items():
            if k == "links":
                continue
            new_ddx[k] = v
    if final_links:
        new_ddx["links"] = final_links
    if new_ddx:
        # Find original ddx position
        if "ddx" in fm:
            # Reconstruct preserving original ddx slot
            ordered: dict = {}
            for k, v in fm.items():
                if k == "ddx":
                    ordered["ddx"] = new_ddx
                elif k in ("relationships", "depends_on"):
                    continue
                else:
                    ordered[k] = v
            new_fm = ordered
        else:
            new_fm["ddx"] = new_ddx

    edit.proposed_links = new_entries
    edit.removed_top_keys = removed_top
    edit.removed_rel_subkeys = rel_removed_subkeys
    edit.dropped_subkeys = rel_dropped_subkeys
    edit.new_frontmatter_yaml = _dump_yaml(new_fm)

    if not edit.has_changes:
        return None
    return edit


def apply_edit(path: Path, edit: FileEdit) -> None:
    text = path.read_text()
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return
    new_text = m.group(1) + edit.new_frontmatter_yaml + m.group(3) + text[m.end():]
    path.write_text(new_text)


def render_dry_run(edit: FileEdit) -> str:
    out: list[str] = []
    out.append(f"--- {edit.path}")
    if edit.removed_top_keys:
        out.append(f"  - remove top-level keys: {', '.join(edit.removed_top_keys)}")
    if edit.removed_rel_subkeys:
        out.append(f"  - remove relationships.{{{', '.join(edit.removed_rel_subkeys)}}}")
    if edit.dropped_subkeys:
        out.append(f"  - drop (no equivalent): relationships.{{{', '.join(edit.dropped_subkeys)}}}")
    if edit.proposed_links:
        out.append(f"  + add ddx.links entries:")
        for e in edit.proposed_links:
            out.append(f"      - {{ kind: {e['kind']:<8s} to: {e['to']} }}")
    return "\n".join(out)


def walk_targets(roots: list[Path]) -> list[Path]:
    paths: list[Path] = []
    for root in roots:
        if root.is_file() and root.suffix == ".md":
            paths.append(root)
        elif root.is_dir():
            paths.extend(sorted(root.rglob("*.md")))
    return paths


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="migrate_relationships_to_links.py")
    parser.add_argument("paths", nargs="+", type=Path, help="file or directory roots to scan")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true",
                      help="print proposed edits without writing (default)")
    mode.add_argument("--apply", action="store_true",
                      help="write edits in-place")
    mode.add_argument("--require-clean", action="store_true",
                      help="CI mode: dry-run + non-zero exit if any edits would be proposed")
    parser.add_argument("--quiet", action="store_true", help="suppress per-file output")
    args = parser.parse_args(argv)

    # Default = dry-run
    if not args.apply and not args.require_clean:
        args.dry_run = True

    targets = walk_targets(args.paths)
    edits: list[FileEdit] = []
    for p in targets:
        e = plan_edit(p)
        if e is not None:
            edits.append(e)

    if args.apply:
        for e in edits:
            apply_edit(e.path, e)
            if not args.quiet:
                print(f"APPLIED {e.path}")
        print(f"\nsummary: applied={len(edits)} scanned={len(targets)}")
        return 0

    # dry-run / require-clean both render edits without writing
    if not args.quiet:
        for e in edits:
            print(render_dry_run(e))
            print()
    print(f"summary: would-edit={len(edits)} scanned={len(targets)}")

    if args.require_clean and edits:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
