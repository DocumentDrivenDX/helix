#!/usr/bin/env python3
"""Slot Registry Integrity check for the HELIX concern library.

Validates `workflows/concerns/slots.yml` against each concern's own
`## Slot` section. Slot membership is derived (a concern fills slot X iff its
`concern.md` `## Slot` names X), so the registry may only reference concerns
whose declared slot matches. Rules:

  1. No duplicate keys anywhere in slots.yml (YAML keeps the last silently).
  2. Every concern `## Slot` names a declared slot.
  3. `defaults:` keys are declared exclusive slots; each value is a library
     concern whose `## Slot` is that key.
  4. Each profile is keyed by its trigger concern; `when` names exactly one
     declared slot whose filler is that concern, and the concern's `## Slot`
     matches.
  5. A profile's `defaults` follow rule 3 and never name its own `when` slot.
  6. A profile's `compose` entries are library concerns with no `## Slot`.
  7. No two profiles share a trigger (at most one profile matches a project).

Usage: check_concern_slots.py [--concerns workflows/concerns]
Exit codes: 0 = consistent, 1 = integrity findings, 2 = unreadable registry.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml


class UniqueKeyLoader(yaml.SafeLoader):
    """SafeLoader that records duplicate mapping keys instead of dropping them."""

    duplicates: list[str]


def _construct_mapping(loader: UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False):
    seen: set[object] = set()
    for key_node, _ in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in seen:
            loader.duplicates.append(f"line {key_node.start_mark.line + 1}: duplicate key {key!r}")
        seen.add(key)
    return yaml.SafeLoader.construct_mapping(loader, node, deep=deep)


UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)


def load_registry(path: Path) -> tuple[dict, list[str]]:
    loader = UniqueKeyLoader(path.read_text(encoding="utf-8"))
    loader.duplicates = []
    try:
        data = loader.get_single_data() or {}
    finally:
        loader.dispose()
    return data, loader.duplicates


SLOT_HEADING = re.compile(r"^## Slot\s*$")


def concern_slots(concerns_dir: Path) -> dict[str, str | None]:
    """Map each library concern to the slot its `## Slot` names (None if composable)."""
    result: dict[str, str | None] = {}
    for concern_md in sorted(concerns_dir.glob("*/concern.md")):
        slot = None
        lines = concern_md.read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines):
            if SLOT_HEADING.match(line):
                for following in lines[i + 1 :]:
                    if following.strip():
                        slot = following.strip().strip("`")
                        break
                break
        result[concern_md.parent.name] = slot
    return result


def check(concerns_dir: Path) -> list[str]:
    registry_path = concerns_dir / "slots.yml"
    registry, findings = load_registry(registry_path)
    slots = registry.get("slots") or {}
    exclusive = {name for name, spec in slots.items() if (spec or {}).get("exclusive")}
    members = concern_slots(concerns_dir)

    for concern, slot in members.items():
        if slot is not None and slot not in slots:
            findings.append(f"concern {concern}: `## Slot` names undeclared slot {slot!r}")

    def check_defaults(where: str, defaults: dict) -> None:
        for slot, filler in (defaults or {}).items():
            if slot not in exclusive:
                findings.append(f"{where}: {slot!r} is not a declared exclusive slot")
            elif filler not in members:
                findings.append(f"{where}: {slot} -> {filler!r} is not a library concern")
            elif members[filler] != slot:
                findings.append(
                    f"{where}: {slot} -> {filler} but {filler}'s `## Slot` is {members[filler]!r}"
                )

    check_defaults("defaults", registry.get("defaults"))

    triggers: dict[tuple[str, str], str] = {}
    for name, profile in (registry.get("profiles") or {}).items():
        where = f"profile {name}"
        when = (profile or {}).get("when") or {}
        if len(when) != 1:
            findings.append(f"{where}: `when` must name exactly one slot, found {len(when)}")
            continue
        (when_slot, trigger), = when.items()
        if trigger != name:
            findings.append(f"{where}: keyed by {name!r} but triggered by {trigger!r}")
        check_defaults(f"{where} when", when)
        key = (when_slot, trigger)
        if key in triggers:
            findings.append(f"{where}: same trigger {when_slot}={trigger} as profile {triggers[key]}")
        triggers[key] = name
        defaults = profile.get("defaults") or {}
        if when_slot in defaults:
            findings.append(f"{where}: defaults its own trigger slot {when_slot!r}")
        check_defaults(f"{where} defaults", defaults)
        for concern in profile.get("compose") or []:
            if concern not in members:
                findings.append(f"{where} compose: {concern!r} is not a library concern")
            elif members[concern] is not None:
                findings.append(
                    f"{where} compose: {concern} fills slot {members[concern]!r}; put it under defaults"
                )
    return findings


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--concerns", type=Path, default=repo_root / "workflows" / "concerns")
    args = parser.parse_args()
    try:
        findings = check(args.concerns)
    except (OSError, yaml.YAMLError) as exc:
        print(f"error: cannot read slot registry: {exc}", file=sys.stderr)
        return 2
    for finding in findings:
        print(f"SLOT REGISTRY: {finding}", file=sys.stderr)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
