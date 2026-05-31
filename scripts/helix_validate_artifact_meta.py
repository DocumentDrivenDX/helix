#!/usr/bin/env python3
"""Validate artifact-type schemas: required_sections must match template H2s.

For every artifact under workflows/activities/<phase>/artifacts/<slug>/, read
meta.yml and extract validation.required_sections (list of section IDs). Then
read template.md, extract its H2 headings, slugify each (lowercase, replace
runs of non-alphanumeric with single underscore, strip leading/trailing
underscores). Assert every required_section appears as an H2 slug.

Stdlib-only: meta.yml is parsed by a small purpose-built reader that handles
the limited shape used by HELIX artifact meta files (mapping keys, list of
strings). This keeps the script runnable as `python3 scripts/...` with no
third-party dependency.

Exit codes: 0 = all clean; 1 = drift detected.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
ACTIVITIES_ROOT = REPO_ROOT / "workflows" / "activities"


def slugify(heading: str) -> str:
    """Lowercase, collapse non-alphanumerics to underscores, trim underscores."""
    slug = re.sub(r"[^a-z0-9]+", "_", heading.lower())
    return slug.strip("_")


def extract_h2_slugs(template_path: Path) -> list[str]:
    slugs: list[str] = []
    for line in template_path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^##\s+(?!#)(.+?)\s*$", line)
        if m:
            slugs.append(slugify(m.group(1)))
    return slugs


def extract_output_format(meta_path: Path) -> str | None:
    """Extract `output.format` from a HELIX meta.yml, or None if absent.

    The validator's H2-vs-required_sections check only applies to markdown
    artifacts. YAML artifacts (metric-definition, etc.) declare their schema
    by YAML keys, not template H2s, so they are skipped.
    """
    text = meta_path.read_text(encoding="utf-8").splitlines()
    in_output = False
    for line in text:
        if re.match(r"^output\s*:\s*$", line):
            in_output = True
            continue
        if in_output:
            if line and not line.startswith((" ", "\t")) and ":" in line:
                return None
            m = re.match(r"^\s+format\s*:\s*(.+?)\s*$", line)
            if m:
                value = m.group(1).strip()
                if (value.startswith('"') and value.endswith('"')) or (
                    value.startswith("'") and value.endswith("'")
                ):
                    value = value[1:-1]
                return value
    return None


def extract_required_sections(meta_path: Path) -> list[str] | None:
    """Parse out validation.required_sections from a HELIX meta.yml.

    Returns the list of section IDs (possibly empty), or None if no
    `validation.required_sections` key is declared at all. We deliberately
    keep this narrow: locate the `validation:` block, then within it the
    `required_sections:` list, then read subsequent `- item` lines until the
    indentation drops back out of the list. This matches every HELIX meta
    file shape we care about without pulling in PyYAML.
    """
    text = meta_path.read_text(encoding="utf-8").splitlines()

    # Find top-level `validation:` (column 0).
    validation_line = None
    for i, line in enumerate(text):
        if re.match(r"^validation\s*:\s*$", line):
            validation_line = i
            break
    if validation_line is None:
        return None

    # Within the validation block, find `required_sections:` (any indent > 0).
    required_line = None
    for i in range(validation_line + 1, len(text)):
        line = text[i]
        # Block ends when we hit another top-level key.
        if line and not line.startswith((" ", "\t")) and ":" in line:
            break
        m = re.match(r"^(\s+)required_sections\s*:\s*(.*)$", line)
        if m:
            required_line = i
            break
    if required_line is None:
        return None

    # Collect list items (lines like `    - foo`) immediately following.
    items: list[str] = []
    base_indent = None
    for i in range(required_line + 1, len(text)):
        line = text[i]
        if not line.strip():
            continue
        # Stop when we leave the list (a key at lower indent than items, or
        # we hit a non-list line at the same indent that's not a `-` item).
        stripped = line.lstrip(" \t")
        indent = len(line) - len(stripped)
        if not stripped.startswith("- "):
            # Could be the next sibling key inside `validation:` — stop.
            if base_indent is None or indent <= base_indent - 2:
                break
            # Or a continuation we don't model — stop conservatively.
            break
        if base_indent is None:
            base_indent = indent
        elif indent != base_indent:
            break
        value = stripped[2:].strip()
        # Strip quotes if present.
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        items.append(value)

    return items


def iter_artifact_dirs() -> list[Path]:
    dirs: list[Path] = []
    if not ACTIVITIES_ROOT.is_dir():
        return dirs
    for phase in sorted(ACTIVITIES_ROOT.iterdir()):
        artifacts_dir = phase / "artifacts"
        if not artifacts_dir.is_dir():
            continue
        for art_dir in sorted(artifacts_dir.iterdir()):
            if art_dir.is_dir() and (art_dir / "meta.yml").exists():
                dirs.append(art_dir)
    return dirs


def validate(art_dir: Path) -> list[str]:
    """Return a list of failure messages for this artifact (empty if clean)."""
    meta_path = art_dir / "meta.yml"
    template_path = art_dir / "template.md"
    failures: list[str] = []

    # Skip non-markdown artifacts: their schema lives in YAML keys, not H2s.
    fmt = extract_output_format(meta_path)
    if fmt and fmt.lower() != "markdown":
        return failures

    required = extract_required_sections(meta_path)
    if not required:
        return failures  # no required_sections declared, nothing to check

    if not template_path.exists():
        failures.append(
            f"{art_dir.relative_to(REPO_ROOT)}: meta.yml declares required_sections "
            f"but template.md is missing"
        )
        return failures

    h2_slugs = set(extract_h2_slugs(template_path))
    for section_id in required:
        if section_id not in h2_slugs:
            failures.append(
                f"{art_dir.relative_to(REPO_ROOT)}: required_section '{section_id}' "
                f"not found as H2 in template.md (have: {sorted(h2_slugs)})"
            )
    return failures


def main() -> int:
    art_dirs = iter_artifact_dirs()
    all_failures: list[str] = []
    for art_dir in art_dirs:
        all_failures.extend(validate(art_dir))

    if all_failures:
        for msg in all_failures:
            print(f"FAIL: {msg}")
        print(f"\nFAIL: {len(all_failures)} drift(s) across {len(art_dirs)} artifact type(s)")
        return 1

    print(f"OK: {len(art_dirs)} artifact type(s) validated (required_sections <-> template H2s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
