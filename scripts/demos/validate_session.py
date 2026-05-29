#!/usr/bin/env python3
"""Validate a HELIX demo session.jsonl against the session-record contract.

Schema is intentionally lightweight (no jsonschema dependency). The
renderer in scripts/demos/render_session.py is the executable contract;
this validator catches mistakes before render time.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

EVENT_KEYS = {
    "meta",
    "narration",
    "shell",
    "output",
    "prompt",
    "assistant",
    "tool_call",
    "tool_result",
    "pause",
}

REQUIRED_META_FIELDS = {"title", "scenario"}

ALLOWED_SCENARIO_KEYS = {
    "adopt",
    "brief",
    "align",
    "plan",
    "evolve",
    "concerns",
    "review",
    "execute",
    "install",
    "smoke",
}


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        raw_lines = [
            l for l in path.read_text(encoding="utf-8").splitlines() if l.strip()
        ]
    except OSError as e:
        return [f"{path}: cannot read: {e}"]

    if not raw_lines:
        return [f"{path}: empty file"]

    for idx, raw in enumerate(raw_lines, start=1):
        try:
            event = json.loads(raw)
        except json.JSONDecodeError as e:
            errors.append(f"{path}:{idx}: invalid JSON: {e.msg}")
            continue

        if not isinstance(event, dict):
            errors.append(f"{path}:{idx}: event must be an object")
            continue

        keys = set(event.keys())
        # An event has exactly one primary content key plus optional
        # presentation fields like pause_s / pace_ms / lines.
        primary = keys & EVENT_KEYS
        if not primary:
            errors.append(
                f"{path}:{idx}: no recognized event key (expected one of {sorted(EVENT_KEYS)})"
            )
        elif len(primary) > 1:
            errors.append(
                f"{path}:{idx}: multiple primary event keys: {sorted(primary)}"
            )

        if idx == 1 and "meta" not in event:
            errors.append(f"{path}:1: first event must be a `meta` block")

        if "meta" in event:
            meta = event["meta"]
            if not isinstance(meta, dict):
                errors.append(f"{path}:{idx}: meta must be an object")
            else:
                missing = REQUIRED_META_FIELDS - meta.keys()
                if missing:
                    errors.append(
                        f"{path}:{idx}: meta missing required fields: {sorted(missing)}"
                    )
                scenario = meta.get("scenario")
                if scenario is not None and scenario not in ALLOWED_SCENARIO_KEYS:
                    errors.append(
                        f"{path}:{idx}: meta scenario '{scenario}' not in "
                        f"allowed keys {sorted(ALLOWED_SCENARIO_KEYS)}"
                    )

        if "assistant" in event:
            if not isinstance(event["assistant"], str):
                errors.append(f"{path}:{idx}: assistant text must be a string")
            pace = event.get("pace_ms")
            if pace is not None and not isinstance(pace, (int, float)):
                errors.append(f"{path}:{idx}: pace_ms must be numeric")

        if "tool_call" in event:
            tc = event["tool_call"]
            if not isinstance(tc, dict) or "name" not in tc:
                errors.append(f"{path}:{idx}: tool_call requires a 'name' field")

        if "pause" in event:
            if not isinstance(event["pause"], (int, float)):
                errors.append(f"{path}:{idx}: pause must be numeric")

    return errors


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("session", type=Path, nargs="+", help="session.jsonl paths")
    args = parser.parse_args(argv)

    all_errors: list[str] = []
    for p in args.session:
        all_errors.extend(validate(p))

    if all_errors:
        for e in all_errors:
            print(e, file=sys.stderr)
        return 1

    print(f"validated {len(args.session)} demo session(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
