#!/usr/bin/env python3
"""Validate artifact-type schemas.

Checks:
- required_sections must match template H2s.
- artifact voice profile references must exist in workflows/voice.yml.

For every artifact under workflows/activities/<phase>/artifacts/<slug>/, read
meta.yml and extract validation.required_sections (list of section IDs). Then
read template.md, extract its H2 headings, slugify each (lowercase, replace
runs of non-alphanumeric with single underscore, strip leading/trailing
underscores). Assert every required_section appears as an H2 slug. Also read
the artifact's top-level `voice` declaration, when present, and assert all
profile references exist in the canonical voice registry.

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
VOICE_REGISTRY = REPO_ROOT / "workflows" / "voice.yml"


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


def strip_yaml_scalar(value: str) -> str:
    value = value.strip()
    if "#" in value:
        value = value.split("#", 1)[0].strip()
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        value = value[1:-1]
    return value


def load_voice_registry(path: Path) -> tuple[str, set[str], list[str]]:
    """Extract default_profile and profiles from workflows/voice.yml."""
    failures: list[str] = []
    if not path.exists():
        return "", set(), [f"missing voice registry: {path.relative_to(REPO_ROOT)}"]

    default_profile = ""
    profiles: set[str] = set()
    in_profiles = False

    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^default_profile\s*:\s*(.+?)\s*$", line)
        if m:
            default_profile = strip_yaml_scalar(m.group(1))
            continue

        if re.match(r"^profiles\s*:\s*$", line):
            in_profiles = True
            continue

        if in_profiles:
            if line and not line.startswith((" ", "\t")) and ":" in line:
                in_profiles = False
                continue
            m = re.match(r"^\s{2}([a-z0-9][a-z0-9-]*)\s*:\s*$", line)
            if m:
                profiles.add(m.group(1))

    if not default_profile:
        failures.append("workflows/voice.yml: missing default_profile")
    if not profiles:
        failures.append("workflows/voice.yml: no profiles declared")
    if default_profile and profiles and default_profile not in profiles:
        failures.append(
            f"workflows/voice.yml: default_profile '{default_profile}' "
            "is not declared under profiles"
        )

    return default_profile, profiles, failures


def extract_voice_references(meta_path: Path, default_profile: str) -> list[str]:
    """Extract profile references from top-level `voice`."""
    lines = meta_path.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        m = re.match(r"^voice\s*:\s*(.*?)\s*$", line)
        if not m:
            continue

        inline = strip_yaml_scalar(m.group(1))
        if inline:
            return [inline]

        refs: list[str] = []
        in_overrides = False
        for child in lines[i + 1 :]:
            if child and not child.startswith((" ", "\t")) and ":" in child:
                break
            profile = re.match(r"^\s+profile\s*:\s*(.+?)\s*$", child)
            if profile:
                refs.append(strip_yaml_scalar(profile.group(1)))
                in_overrides = False
                continue
            if re.match(r"^\s+overrides\s*:\s*$", child):
                in_overrides = True
                continue
            if in_overrides:
                override = re.match(r"^\s+[a-zA-Z0-9_-]+\s*:\s*(.+?)\s*$", child)
                if override:
                    refs.append(strip_yaml_scalar(override.group(1)))
        return refs or [default_profile]

    return [default_profile]


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


def validate(art_dir: Path, default_voice_profile: str, voice_profiles: set[str]) -> list[str]:
    """Return a list of failure messages for this artifact (empty if clean)."""
    meta_path = art_dir / "meta.yml"
    template_path = art_dir / "template.md"
    failures: list[str] = []

    for voice_ref in extract_voice_references(meta_path, default_voice_profile):
        if voice_ref not in voice_profiles:
            failures.append(
                f"{art_dir.relative_to(REPO_ROOT)}: voice profile '{voice_ref}' "
                "is not declared in workflows/voice.yml"
            )

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
    default_voice_profile, voice_profiles, registry_failures = load_voice_registry(VOICE_REGISTRY)
    all_failures.extend(registry_failures)
    for art_dir in art_dirs:
        all_failures.extend(validate(art_dir, default_voice_profile, voice_profiles))

    if all_failures:
        for msg in all_failures:
            print(f"FAIL: {msg}")
        print(f"\nFAIL: {len(all_failures)} drift(s) across {len(art_dirs)} artifact type(s)")
        return 1

    print(
        f"OK: {len(art_dirs)} artifact type(s) validated "
        "(required_sections <-> template H2s, voice profiles)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
