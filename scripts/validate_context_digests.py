#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


DIGEST_PATTERN = re.compile(r"<context-digest>\s*.*?</context-digest>", re.DOTALL)
OMISSION_RATIONALE_PATTERN = re.compile(
    r"^\s*Explicit omission rationale:\s*\S.*\Z", re.DOTALL
)
AUTHORIZED_OMISSION_LABEL = "digest:omission-authorized"


def review_finding_missing_area(labels: list[str]) -> bool:
    return "review-finding" in labels and not any(
        label.startswith("area:") for label in labels
    )


def has_digest(description: str) -> bool:
    return bool(DIGEST_PATTERN.search(description))


def has_authorized_omission_rationale(description: str, labels: list[str]) -> bool:
    return AUTHORIZED_OMISSION_LABEL in labels and bool(
        OMISSION_RATIONALE_PATTERN.match(description)
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate that open HELIX beads carry a context digest or an "
            "explicit omission rationale from a workflow-authorized omission path."
        )
    )
    parser.add_argument(
        "--tracker",
        default=".ddx/beads.jsonl",
        help="Tracker JSONL path (default: .ddx/beads.jsonl).",
    )
    parser.add_argument(
        "--status",
        action="append",
        default=[],
        help="Status to validate (repeatable, default: open).",
    )
    args = parser.parse_args()

    tracker_path = Path(args.tracker)
    statuses = set(args.status or ["open"])
    missing_context: list[tuple[int, str, str]] = []
    unauthorized_omission: list[tuple[int, str, str]] = []
    missing_review_area: list[tuple[int, str, str]] = []

    for line_number, raw_line in enumerate(
        tracker_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not raw_line.strip():
            continue
        bead = json.loads(raw_line)
        if bead.get("status") not in statuses:
            continue
        labels = bead.get("labels", [])
        if "helix" not in labels:
            continue
        if review_finding_missing_area(labels):
            missing_review_area.append(
                (line_number, bead.get("id", "<unknown>"), bead.get("title", ""))
            )
        description = bead.get("description") or ""
        if has_digest(description):
            continue
        if OMISSION_RATIONALE_PATTERN.match(description):
            if has_authorized_omission_rationale(description, labels):
                continue
            unauthorized_omission.append(
                (line_number, bead.get("id", "<unknown>"), bead.get("title", ""))
            )
            continue
        missing_context.append(
            (line_number, bead.get("id", "<unknown>"), bead.get("title", ""))
        )

    if missing_context or unauthorized_omission or missing_review_area:
        for line_number, bead_id, title in missing_context:
            print(
                f"{tracker_path}:{line_number}: bead {bead_id} is missing "
                f"<context-digest> or workflow-authorized explicit omission rationale: {title}",
                file=sys.stderr,
            )
        for line_number, bead_id, title in unauthorized_omission:
            print(
                f"{tracker_path}:{line_number}: bead {bead_id} uses an explicit omission rationale "
                f"without {AUTHORIZED_OMISSION_LABEL}: {title}",
                file=sys.stderr,
            )
        for line_number, bead_id, title in missing_review_area:
            print(
                f"{tracker_path}:{line_number}: review-finding bead {bead_id} is missing area:* label(s): {title}",
                file=sys.stderr,
            )
        print(
            "validated context digests / workflow-authorized omission rationales on 0 bead(s): "
            f"{len(missing_context)} missing digest-or-rationale entry(ies), "
            f"{len(unauthorized_omission)} unauthorized omission rationale entry(ies), "
            f"{len(missing_review_area)} review-finding bead(s) missing area labels",
            file=sys.stderr,
        )
        return 1

    print(
        "validated context digests / workflow-authorized omission rationales on open HELIX bead(s) "
        f"in {tracker_path}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
