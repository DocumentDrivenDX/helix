#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

CANONICAL_ARTIFACTS = (
    "deployment-checklist",
    "monitoring-setup",
    "runbook",
    "release-notes",
)


@dataclass(frozen=True)
class SurfaceSpec:
    label: str
    path: Path
    required_fragment: str


def normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


def build_surface_specs(args: argparse.Namespace) -> list[SurfaceSpec]:
    return [
        SurfaceSpec(
            label="deploy README",
            path=args.deploy_readme,
            required_fragment=(
                "Deploy artifacts are project-specific, but current HELIX still "
                "treats four deploy surfaces as first-class in the live contract: "
                "`deployment-checklist`, `monitoring-setup`, `runbook`, and "
                "`release-notes`."
            ),
        ),
        SurfaceSpec(
            label="deploy enforcer",
            path=args.deploy_enforcer,
            required_fragment=(
                "Deploy artifacts are project-specific, but HELIX treats four "
                "deploy outputs as the live contract under "
                "`docs/helix/05-deploy/`:"
            ),
        ),
        SurfaceSpec(
            label="artifacts glossary",
            path=args.glossary,
            required_fragment=(
                "Deploy artifacts cover four first-class surfaces in the current "
                "HELIX contract: `deployment-checklist`, `monitoring-setup`, "
                "`runbook`, and `release-notes`."
            ),
        ),
    ]


def validate_surface(spec: SurfaceSpec) -> list[str]:
    errors: list[str] = []
    if not spec.path.is_file():
        return [f"{spec.label}: expected file {spec.path} to exist"]

    text = spec.path.read_text(encoding="utf-8")
    normalized = normalize_whitespace(text)

    if normalize_whitespace(spec.required_fragment) not in normalized:
        errors.append(
            f"{spec.label}: missing canonical four-artifact contract wording in {spec.path}"
        )

    missing_artifacts = [artifact for artifact in CANONICAL_ARTIFACTS if f"`{artifact}`" not in text]
    if missing_artifacts:
        errors.append(
            f"{spec.label}: missing deploy artifact reference(s) {', '.join(missing_artifacts)} in {spec.path}"
        )

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate deploy contract documentation stays aligned to the canonical four-artifact surface."
    )
    parser.add_argument(
        "--deploy-readme",
        type=Path,
        default=Path("workflows/phases/05-deploy/README.md"),
        help="Path to the deploy phase README surface.",
    )
    parser.add_argument(
        "--deploy-enforcer",
        type=Path,
        default=Path("workflows/phases/05-deploy/enforcer.md"),
        help="Path to the deploy phase enforcer surface.",
    )
    parser.add_argument(
        "--glossary",
        type=Path,
        default=Path("website/content/docs/glossary/artifacts.md"),
        help="Path to the shipped artifacts glossary surface.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    errors: list[str] = []
    for spec in build_surface_specs(args):
        errors.extend(validate_surface(spec))

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("validated deploy contract docs: 3 surfaces")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
