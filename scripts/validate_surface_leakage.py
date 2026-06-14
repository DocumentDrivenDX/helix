#!/usr/bin/env python3
"""Detect exact interface-surface leakage outside Contract artifacts.

HELIX Frame artifacts may name a product capability, feature behavior, user
journey, or high-level dependency on an API/CLI/event/schema. They must not
define the normative shared surface itself. Exact commands, flags, endpoints,
payloads, status codes, config keys, telemetry fields, event schemas, and
adapter signatures belong in Contract artifacts.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class PatternRule:
    name: str
    regex: re.Pattern[str]
    description: str


@dataclass
class Finding:
    path: Path
    line: int
    section: str
    rule: str
    text: str
    destination: str = "02-design/contracts/"

    def to_dict(self) -> dict[str, object]:
        return {
            "class": "SURFACE_LEAK",
            "path": str(self.path),
            "line": self.line,
            "section": self.section,
            "rule": self.rule,
            "text": self.text,
            "suggested_destination": self.destination,
        }


@dataclass(frozen=True)
class RetiredSurfaceRule:
    name: str
    regex: re.Pattern[str]
    description: str
    replacement: str


@dataclass
class RetiredSurfaceFinding:
    path: Path
    line: int
    rule: str
    text: str
    replacement: str

    def to_dict(self) -> dict[str, object]:
        return {
            "class": "RETIRED_PUBLIC_SURFACE",
            "path": str(self.path),
            "line": self.line,
            "rule": self.rule,
            "text": self.text,
            "replacement": self.replacement,
        }


RULES: tuple[PatternRule, ...] = (
    PatternRule(
        "cli_flag",
        re.compile(r"(?<![\w-])--[a-zA-Z][\w-]+"),
        "CLI flag or option",
    ),
    PatternRule(
        "http_method_path",
        re.compile(r"\b(?:GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+/[A-Za-z0-9_./{}:$?&=%-]+"),
        "HTTP method and path",
    ),
    PatternRule(
        "api_path",
        re.compile(r"(?<![\w-])/(?:api|v\d+|graphql|rpc)/[A-Za-z0-9_./{}:$?&=%-]+"),
        "concrete API path",
    ),
    PatternRule(
        "json_fence",
        re.compile(r"^```(?:json|jsonc|schema)\s*$", re.IGNORECASE),
        "JSON payload or schema block",
    ),
    PatternRule(
        "exit_or_status_code",
        re.compile(r"\b(?:exit\s+(?:code|status)|status\s+code|HTTP\s+status)\s*[:=]?\s*[1-9]\d{0,2}\b", re.IGNORECASE),
        "exit/status code",
    ),
    PatternRule(
        "schema_table",
        re.compile(r"^\|.*\b(?:field|property|config\s+key|metric|event|message|endpoint|command)\b.*\b(?:type|shape|required|unit|enum|code)\b.*\|$", re.IGNORECASE),
        "field/schema/config/telemetry/event table",
    ),
    PatternRule(
        "adapter_signature",
        re.compile(r"\b[a-zA-Z_]\w+\([^)]*\)\s*(?:->|:)\s*[A-Za-z_][\w.\[\]<>|, ?]*"),
        "adapter or method signature",
    ),
)


RETIRED_SURFACE_RULES: tuple[RetiredSurfaceRule, ...] = (
    RetiredSurfaceRule(
        "helix_env_routing",
        re.compile(r"\bHELIX_(?:FLOW|METHODOLOGY)\b"),
        "Retired environment-variable routing surface",
        "Put flow scope in marker files and artifacts; do not route HELIX with env vars.",
    ),
    RetiredSurfaceRule(
        "public_sibling_skill",
        re.compile(
            r"\b(?:helix-(?:data|infra|web))\b[^\n]{0,80}\b(?:skill|plugin|methodolog(?:y|ies)|flow)\b"
            r"|\b(?:skill|plugin|methodolog(?:y|ies)|flow)\b[^\n]{0,80}\b(?:helix-(?:data|infra|web))\b",
            re.IGNORECASE,
        ),
        "Retired public sibling HELIX skill/flow claim",
        "Describe one public `helix` skill with internal flows or domain lanes.",
    ),
    RetiredSurfaceRule(
        "helix_scope_selector",
        re.compile(r"(?<![:\w/])\/helix:[A-Za-z0-9_.-]+\b"),
        "Retired public /helix:<scope> selector",
        "Use `/helix <mode>` and describe scope in project artifacts.",
    ),
    RetiredSurfaceRule(
        "missing_checkout_script",
        re.compile(r"(?<![\w/])scripts/helix(?:\b|[./-])"),
        "Retired checkout script reference",
        "HELIX ships documents, templates, and one skill; runtime CLIs own execution.",
    ),
    RetiredSurfaceRule(
        "spec_tracks_implementation_status",
        re.compile(
            r"\b(?:spec|specification|artifact)s?\b[^\n]{0,100}\bimplementation status\b"
            r"|\bimplementation status\b[^\n]{0,100}\b(?:spec|specification|artifact)s?\b",
            re.IGNORECASE,
        ),
        "Specification-as-implementation-status wording",
        "Specifications capture intent; gaps and implementation state belong in plans, beads, reports, or evaluations.",
    ),
)


SCAN_SECTIONS: dict[str, set[str]] = {
    "prd": {"functional requirements"},
    "feature-specification": {
        "requirements",
        "edge cases and error handling",
        "dependencies",
    },
    "user-stories": {
        "acceptance criteria",
        "dependencies",
    },
    "technical-design": {
        "api/interface design",
        "integration points",
    },
}


def normalize_heading(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def iter_markdown_paths(paths: list[Path]) -> list[Path]:
    found: list[Path] = []
    for path in paths:
        if path.is_dir():
            found.extend(sorted(p for p in path.rglob("*.md") if p.is_file()))
        elif path.is_file() and path.suffix.lower() in {".md", ".mdx"}:
            found.append(path)
    return found


def iter_text_paths(paths: list[Path]) -> list[Path]:
    suffixes = {".md", ".mdx", ".yml", ".yaml", ".jsonl", ".txt"}
    found: list[Path] = []
    for path in paths:
        if path.is_dir():
            found.extend(sorted(p for p in path.rglob("*") if p.is_file() and p.suffix.lower() in suffixes))
        elif path.is_file() and path.suffix.lower() in suffixes:
            found.append(path)
    return found


def artifact_type(path: Path, text: str) -> str | None:
    normalized_parts = {part.lower() for part in path.parts}
    path_text = str(path).lower()

    if "contracts" in normalized_parts or "/contract/" in path_text:
        return "contract"

    frontmatter_id = re.search(r"^\s*id:\s*([A-Za-z0-9_.-]+)\s*$", text, re.MULTILINE)
    artifact_id = frontmatter_id.group(1).lower() if frontmatter_id else ""

    if "technical-design" in normalized_parts or "technical-designs" in normalized_parts:
        return "technical-design"
    if artifact_id.startswith("td-"):
        return "technical-design"
    if "user-stories" in normalized_parts or artifact_id.startswith("us-"):
        return "user-stories"
    if "feature-specification" in normalized_parts or "features" in normalized_parts:
        return "feature-specification"
    if artifact_id.startswith("feat-"):
        return "feature-specification"
    if path.name.lower() == "prd.md" or artifact_id == "prd":
        return "prd"
    if artifact_id.startswith(("contract-", "api-")):
        return "contract"
    return None


def current_sections(lines: list[str]) -> list[str]:
    sections: list[str] = []
    active: str | None = None
    for line in lines:
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if match:
            active = normalize_heading(match.group(1))
        sections.append(active or "")
    return sections


def should_scan(artifact: str | None, section: str) -> bool:
    if artifact == "contract":
        return False
    if artifact not in SCAN_SECTIONS:
        return False
    return section in SCAN_SECTIONS[artifact]


def is_contract_reference(line: str) -> bool:
    return bool(re.search(r"\b(?:CONTRACT|API)-\d{3}\b", line))


def validate_file(path: Path) -> list[Finding]:
    text = path.read_text(encoding="utf-8")
    artifact = artifact_type(path, text)
    lines = text.splitlines()
    sections = current_sections(lines)
    findings: list[Finding] = []

    for index, line in enumerate(lines, start=1):
        section = sections[index - 1]
        if not should_scan(artifact, section):
            continue
        if is_contract_reference(line):
            continue
        for rule in RULES:
            if rule.regex.search(line):
                findings.append(
                    Finding(
                        path=path,
                        line=index,
                        section=section,
                        rule=rule.name,
                        text=line.strip(),
                    )
                )
                break
    return findings


def is_inline_retired_allowlisted(lines: list[str], index: int) -> bool:
    start = max(0, index - 3)
    window = "\n".join(lines[start : index + 1]).lower()
    return "retired-public-surface: allow" in window


def is_path_allowlisted(path: Path, patterns: list[str]) -> bool:
    rel = str(path)
    try:
        rel = str(path.relative_to(REPO_ROOT))
    except ValueError:
        pass
    return any(fnmatch.fnmatch(rel, pattern) for pattern in patterns)


def validate_retired_public_surfaces(
    path: Path,
    path_allowlist: list[str],
) -> list[RetiredSurfaceFinding]:
    if is_path_allowlisted(path, path_allowlist):
        return []

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    findings: list[RetiredSurfaceFinding] = []

    for index, line in enumerate(lines, start=1):
        if is_inline_retired_allowlisted(lines, index - 1):
            continue
        for rule in RETIRED_SURFACE_RULES:
            if rule.regex.search(line):
                findings.append(
                    RetiredSurfaceFinding(
                        path=path,
                        line=index,
                        rule=rule.name,
                        text=line.strip(),
                        replacement=rule.replacement,
                    )
                )
                break
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="Markdown files or directories to scan")
    parser.add_argument("--json", action="store_true", help="Emit findings as JSON")
    parser.add_argument(
        "--retired-public-surfaces",
        action="store_true",
        help="Scan for retired HELIX public surfaces instead of Contract surface leakage",
    )
    parser.add_argument(
        "--retired-allow-glob",
        action="append",
        default=[],
        help="Glob, relative to repo root, allowed to contain retired public-surface text",
    )
    args = parser.parse_args()

    if args.retired_public_surfaces:
        retired_findings: list[RetiredSurfaceFinding] = []
        for path in iter_text_paths(args.paths):
            retired_findings.extend(
                validate_retired_public_surfaces(path, args.retired_allow_glob)
            )

        if args.json:
            print(json.dumps([finding.to_dict() for finding in retired_findings], indent=2))
        elif retired_findings:
            for finding in retired_findings:
                rel = finding.path
                try:
                    rel = finding.path.relative_to(REPO_ROOT)
                except ValueError:
                    pass
                print(
                    f"RETIRED_PUBLIC_SURFACE {rel}:{finding.line} "
                    f"rule={finding.rule} -> {finding.replacement}: {finding.text}"
                )
        else:
            print("OK: no retired public HELIX surfaces detected")

        return 1 if retired_findings else 0

    findings: list[Finding] = []
    for path in iter_markdown_paths(args.paths):
        findings.extend(validate_file(path))

    if args.json:
        print(json.dumps([finding.to_dict() for finding in findings], indent=2))
    elif findings:
        for finding in findings:
            rel = finding.path
            try:
                rel = finding.path.relative_to(REPO_ROOT)
            except ValueError:
                pass
            print(
                f"SURFACE_LEAK {rel}:{finding.line} "
                f"section={finding.section!r} rule={finding.rule} "
                f"-> {finding.destination}: {finding.text}"
            )
    else:
        print("OK: no surface leakage detected")

    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
