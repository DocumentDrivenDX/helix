#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

TRACKER_TERMS = ("status", "label", "tracker", "field", "notes")
VAGUE_PATTERN = re.compile(r"\b(?:works?|correct(?:ly)?|complete(?:ly)?|aligned?)\b", re.IGNORECASE)
COMMAND_PATTERN = re.compile(
    r"\b(?:bash|biome|bun|cargo|ddx|git|go(?:\s+test|\s+vet)?|helix|just|"
    r"lefthook|node|npm|pnpm|pytest|python3?|ruff|uv(?:\s+run)?|yarn)\b",
    re.IGNORECASE,
)
CHECK_PATTERN = re.compile(
    r"\b(?:pass(?:es|ed)?|fail(?:s|ed)?|return(?:s|ed)?|contain(?:s|ed)?|"
    r"match(?:es|ed)?|exist(?:s|ed)?|print(?:s|ed)?|show(?:s|ed)?|"
    r"create(?:s|d)?|update(?:s|d)?|record(?:s|ed)?|close(?:s|d)?|"
    r"promot(?:e|es|ed)|flag(?:s|ged)?|reject(?:s|ed)?|include(?:s|d)?|"
    r"document(?:s|ed)?|write(?:s|n)?|mark(?:s|ed)?)\b",
    re.IGNORECASE,
)
CODE_PATTERN = re.compile(r"`[^`]+`")
PATH_PATTERN = re.compile(r"(?:^|[\s`])(?:[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.-]+")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate that execution-ready HELIX beads have measurable acceptance criteria."
    )
    parser.add_argument(
        "tracker",
        nargs="?",
        default=".ddx/beads.jsonl",
        help="Path to a tracker JSONL file. Defaults to .ddx/beads.jsonl",
    )
    return parser.parse_args()


def load_beads(tracker_path: Path) -> list[tuple[int, dict[str, object]]]:
    beads: list[tuple[int, dict[str, object]]] = []
    for line_number, raw_line in enumerate(tracker_path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = raw_line.strip()
        if not stripped:
            continue
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{tracker_path}:{line_number}: invalid JSON: {exc}") from exc
        if not isinstance(payload, dict):
            raise ValueError(f"{tracker_path}:{line_number}: expected JSON object")
        beads.append((line_number, payload))
    return beads


def has_closed_dependencies_only(bead: dict[str, object], statuses_by_id: dict[str, str]) -> bool:
    dependencies = bead.get("dependencies")
    if not isinstance(dependencies, list):
        return True

    for dependency in dependencies:
        if not isinstance(dependency, dict):
            continue
        depends_on_id = dependency.get("depends_on_id")
        if not isinstance(depends_on_id, str) or not depends_on_id:
            continue
        if statuses_by_id.get(depends_on_id) != "closed":
            return False
    return True


def is_execution_ready_bead(bead: dict[str, object], statuses_by_id: dict[str, str]) -> bool:
    if bead.get("status") != "open":
        return False
    if not has_closed_dependencies_only(bead, statuses_by_id):
        return False
    if bead.get("execution-eligible") is False:
        return False
    superseded_by = bead.get("superseded-by")
    if isinstance(superseded_by, str) and superseded_by.strip():
        return False
    return True


def execution_ready_beads(beads: list[tuple[int, dict[str, object]]]) -> list[tuple[int, dict[str, object]]]:
    statuses_by_id = {
        str(bead_id): str(status)
        for _, bead in beads
        if (bead_id := bead.get("id")) is not None and (status := bead.get("status")) is not None
    }
    return [
        (line_number, bead)
        for line_number, bead in beads
        if is_execution_ready_bead(bead, statuses_by_id)
    ]


def validate_beads(beads: list[tuple[int, dict[str, object]]], tracker_path: Path) -> list[str]:
    errors: list[str] = []
    ready_beads = execution_ready_beads(beads)

    for line_number, bead in ready_beads:
        bead_id = str(bead.get("id", "<missing-id>"))
        acceptance = bead.get("acceptance")
        if not isinstance(acceptance, str) or not is_measurable_acceptance(acceptance):
            errors.append(
                f"{tracker_path}:{line_number}: bead {bead_id} has non-measurable execution-ready acceptance: "
                f"{acceptance!r}"
            )

    if not errors:
        print(f"validated measurable acceptance on {len(ready_beads)} execution-ready bead(s)")
    return errors


def is_measurable_acceptance(acceptance: str) -> bool:
    if not acceptance.strip():
        return False

    has_command = COMMAND_PATTERN.search(acceptance) is not None
    has_check = CHECK_PATTERN.search(acceptance) is not None
    has_named_target = (
        CODE_PATTERN.search(acceptance) is not None
        or PATH_PATTERN.search(acceptance) is not None
        or any(term in acceptance.lower() for term in TRACKER_TERMS)
    )
    has_vague_language = VAGUE_PATTERN.search(acceptance) is not None

    if has_command and has_check:
        return True
    if has_named_target and has_check:
        return True
    if has_vague_language:
        return False
    return has_command or (has_named_target and has_check)


def main() -> int:
    args = parse_args()
    tracker_path = Path(args.tracker)
    if not tracker_path.is_file():
        print(f"{tracker_path}: tracker file does not exist", file=sys.stderr)
        return 1

    try:
        beads = load_beads(tracker_path)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    errors = validate_beads(beads, tracker_path)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
