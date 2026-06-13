#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

python3 - <<'PY'
from __future__ import annotations

import pathlib
import re
import shlex
import sys

STRICT_ROOTS = [
    pathlib.Path("docs/website/content/_index.md"),
    pathlib.Path("docs/website/content/artifact-types/_index.md"),
    pathlib.Path("docs/website/content/install"),
    pathlib.Path("docs/website/content/platforms"),
    pathlib.Path("docs/website/content/reference"),
    pathlib.Path("docs/website/content/skills"),
    pathlib.Path("docs/website/content/use"),
    pathlib.Path("docs/website/content/why"),
    pathlib.Path("docs/demos"),
]

LEGACY_PATTERNS = [
    (re.compile(r"/helix-(?:input|frame|align|plan|evolve|review|implement|worker|backfill)\b"), "legacy slash command", "use `/helix <mode>` or name the HELIX skill"),
    (re.compile(r"\balignment[-/ ]and[-/ ]planning skill\b", re.I), "alignment-and-planning skill", "say `HELIX skill` and name the workflow mode when needed"),
    (re.compile(r"\balignment skill\b", re.I), "alignment skill", "say `HELIX skill` and name the workflow mode when needed"),
    (re.compile(r"\bHELIX_(?:FLOW|METHODOLOGY)\b"), "HELIX env-var routing", "describe flow scope in project artifacts; do not use environment variables"),
    (re.compile(r"\bhelix-(?:infra|data|web)\b"), "public sibling flow", "describe domain lanes or flow scopes; do not name retired public skills"),
    (re.compile(r"\bHELIX build mode\b"), "HELIX build mode", "say `build workflow mode` or `HELIX skill build mode` with context"),
    (re.compile(r"\bFZO\b"), "Fizeau shorthand in public demos", "spell out the runtime or remove internal shorthand"),
    (re.compile(r"built-in tracker is HELIX's execution layer", re.I), "HELIX-owned tracker wording", "say the runtime owns tracker and execution behavior"),
    (re.compile(r"\bauthority\s+order\b", re.I), "authority-order wording", "say `artifact authority hierarchy`"),
]

FORBIDDEN = [
    (re.compile(r"\badopter doctrine\b", re.I), "public-copy-forbidden", "say `adoption guidance`, `current user guidance`, or remove the phrase"),
    (re.compile(r"\bsource traceability\b", re.I), "public-copy-forbidden", "say `source path` or explain the source document plainly"),
    (re.compile(r"\bgenerated area\b", re.I), "public-copy-forbidden", "say `generated examples from HELIX's own docs`"),
    (re.compile(r"\bdogfood corpus\b", re.I), "public-copy-forbidden", "say `HELIX's own example docs`"),
    (re.compile(r"\bdogfood artifacts?\b", re.I), "public-copy-forbidden", "say `HELIX's own example docs`"),
    (re.compile(r"\bdogfood(?:ing)?\b", re.I), "public-copy-forbidden", "say `HELIX's own example docs` unless a maintainer reference defines dogfooding"),
    (re.compile(r"\bthe reusable catalog\b|\breusable catalog\b", re.I), "public-copy-forbidden", "say `artifact-type catalog` or `reusable catalog of HELIX document patterns`"),
    (re.compile(r"\bartifact catalog\b", re.I), "public-copy-forbidden", "say `artifact-type catalog` for `/artifact-types/` or `HELIX example docs` for `/artifacts/`"),
]

CONTEXT_GATES = [
    (
        re.compile(r"\brouting skill\b", re.I),
        "routing-skill-context",
        re.compile(r"\bHELIX skill\b|\bportable [`']?helix[`']? skill\b|\bsingle skill\b|\bone [`']?helix[`']? skill\b", re.I),
        "define it nearby as the HELIX skill, not a runtime or queue runner",
    ),
    (
        re.compile(r"\bruntime-neutral\b", re.I),
        "runtime-neutral-context",
        re.compile(r"\bportable across tools\b|\bnot tied to\b|\bany runtime\b|\bruntime boundary\b|\btool doing the work\b", re.I),
        "say which runtime boundary the copy is protecting, or use `portable across tools`",
    ),
    (
        re.compile(r"\bartifact discipline\b", re.I),
        "artifact-discipline-context",
        re.compile(r"\bdocument pattern\b|\bauthority\b|\bgoverning artifact\b|\bMarkdown\b|\bartifact rule\b", re.I),
        "name the document pattern, rule, or authority relationship instead",
    ),
    (
        re.compile(r"\bbeads?\b", re.I),
        "bead-context",
        re.compile(r"\bDDx\b|\bruntime work item\b|\breference runtime\b", re.I),
        "define bead as a DDx work item or say `runtime work item`",
    ),
    (
        re.compile(r"\bcontext digests?\b", re.I),
        "context-digest-context",
        re.compile(r"\bruntime work context\b|\bDDx\b|\breference runtime\b", re.I),
        "define context digest as runtime work context or avoid the internal term",
    ),
]

GEN_ROOT = pathlib.Path("docs/website/content/artifacts/_index.md")
GEN_ARTIFACT_ROOT = pathlib.Path("docs/website/content/artifacts")


def split_frontmatter(text: str) -> tuple[str, str, int]:
    if not text.startswith("---\n"):
        return "", text, 1
    end = text.find("\n---\n", 4)
    if end == -1:
        return "", text, 1
    frontmatter = text[4:end]
    body = text[end + 5 :]
    body_start = text.count("\n", 0, end + 5) + 1
    return frontmatter, body, body_start


def strip_code_fences(text: str) -> str:
    lines = text.splitlines()
    in_fence = False
    stripped: list[str] = []
    for line in lines:
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            stripped.append("")
        elif in_fence:
            stripped.append("")
        else:
            stripped.append(line)
    return "\n".join(stripped)


def line_number(text: str, offset: int, base: int = 1) -> int:
    return base + text.count("\n", 0, offset)


def paragraph_around(text: str, offset: int) -> str:
    start = text.rfind("\n\n", 0, offset)
    end = text.find("\n\n", offset)
    if start == -1:
        start = 0
    else:
        start += 2
    if end == -1:
        end = len(text)
    return text[start:end]


def is_artifact_body(path: pathlib.Path) -> bool:
    parts = path.parts
    return len(parts) >= 4 and parts[:4] == ("docs", "website", "content", "artifacts")


def is_research(path: pathlib.Path) -> bool:
    parts = path.parts
    return len(parts) >= 4 and parts[:4] == ("docs", "website", "content", "research")


def is_demo_fixture(path: pathlib.Path) -> bool:
    parts = path.parts
    return len(parts) >= 2 and parts[:2] == ("docs", "demos") and (
        "fixture" in parts or "agent-dictionary" in parts or ".ddx" in parts
    )


def strict_files() -> list[pathlib.Path]:
    files: set[pathlib.Path] = set()
    for root in STRICT_ROOTS:
        if root.is_file():
            files.add(root)
        elif root.is_dir():
            for suffix in ("*.md", "*.jsonl", "*.yml", "*.yaml"):
                files.update(root.rglob(suffix))
    return sorted(
        p
        for p in files
        if not is_artifact_body(p) and not is_research(p) and not is_demo_fixture(p)
    )


def public_card_files() -> list[pathlib.Path]:
    content_root = pathlib.Path("docs/website/content")
    return sorted(
        p
        for p in content_root.rglob("*.md")
        if not is_artifact_body(p) and not is_research(p)
    )


def iter_cards(text: str, base_line: int = 1):
    for match in re.finditer(r"\{\{<\s+card\s+([^>]*)>\}\}", text):
        attrs: dict[str, str] = {}
        try:
            tokens = shlex.split(match.group(1))
        except ValueError:
            tokens = []
        for token in tokens:
            if "=" not in token:
                continue
            key, value = token.split("=", 1)
            attrs[key] = value
        yield match, attrs, line_number(text, match.start(), base_line)


errors: list[str] = []


def fail(path: pathlib.Path, line: int, rule: str, found: str, replacement: str) -> None:
    errors.append(f"{path}:{line}: {rule}: found {found!r}; replacement: {replacement}")


def scan_legacy_and_public_terms(path: pathlib.Path) -> None:
    text = path.read_text(encoding="utf-8")
    frontmatter, body, body_start = split_frontmatter(text)
    scan = strip_code_fences(body)
    del frontmatter

    for pattern, label, replacement in LEGACY_PATTERNS:
        for match in pattern.finditer(scan):
            line_start = scan.rfind("\n", 0, match.start()) + 1
            line_end = scan.find("\n", match.end())
            if line_end == -1:
                line_end = len(scan)
            line = scan[line_start:line_end]
            if label == "legacy slash command" and (
                "docs/demos/" in line or "/demos/helix-" in line
            ):
                continue
            if (
                label == "public sibling flow"
                and path == pathlib.Path("docs/website/content/use/multiple-flows.md")
                and "not separate public" in paragraph_around(scan, match.start())
            ):
                continue
            fail(path, line_number(scan, match.start(), body_start), label, match.group(0), replacement)

    for pattern, rule, replacement in FORBIDDEN:
        for match in pattern.finditer(scan):
            line_start = scan.rfind("\n", 0, match.start()) + 1
            line_end = scan.find("\n", match.end())
            if line_end == -1:
                line_end = len(scan)
            line = scan[line_start:line_end]
            if line.lstrip().startswith("#"):
                continue
            fail(path, line_number(scan, match.start(), body_start), rule, match.group(0), replacement)

    for pattern, rule, required_context, replacement in CONTEXT_GATES:
        for match in pattern.finditer(scan):
            line_start = scan.rfind("\n", 0, match.start()) + 1
            line_end = scan.find("\n", match.end())
            if line_end == -1:
                line_end = len(scan)
            line = scan[line_start:line_end]
            if line.lstrip().startswith("#"):
                continue
            para = paragraph_around(scan, match.start())
            if not required_context.search(para):
                fail(path, line_number(scan, match.start(), body_start), rule, match.group(0), replacement)


def scan_cards(path: pathlib.Path) -> None:
    text = path.read_text(encoding="utf-8")
    _, body, body_start = split_frontmatter(text)
    for match, attrs, line in iter_cards(body, body_start):
        title = attrs.get("title", "").strip()
        subtitle = attrs.get("subtitle", "").strip()
        link = attrs.get("link", "").strip()
        card_text = f"{title} {subtitle}"
        if not title:
            fail(path, line, "card-standalone-copy", match.group(0), "add a concrete title")
        if not subtitle:
            fail(path, line, "card-standalone-copy", title or match.group(0), "add a subtitle that explains what the reader gets")
        if subtitle.lower() in {"learn more", "read more", "details", "see details"}:
            fail(path, line, "card-standalone-copy", subtitle, "explain the click target in the subtitle")
        if title and subtitle and subtitle.lower().strip(".") == title.lower().strip("."):
            fail(path, line, "card-standalone-copy", subtitle, "make the subtitle add context beyond the title")
        for pattern, rule, replacement in FORBIDDEN:
            if pattern.search(card_text):
                fail(path, line, rule, card_text, replacement)
        for pattern, rule, required_context, replacement in CONTEXT_GATES:
            if pattern.search(card_text) and not required_context.search(card_text):
                fail(path, line, rule, card_text, replacement)
        if "artifact-types" in link and not re.search(r"artifact|catalog|template|prompt|document pattern|document shape|quality|PRD|ADR|test plan|runbook", card_text, re.I):
            fail(path, line, "card-standalone-copy", card_text, "artifact-type links must say they open HELIX document patterns or templates")
        if re.search(r"(^|/|\.\.)artifacts", link) and not re.search(r"example|HELIX's own|project documents|source files|generated", card_text, re.I):
            fail(path, line, "card-standalone-copy", card_text, "artifacts links must say they open examples from HELIX's own project documents")


def assert_contains(path: pathlib.Path, needle: str, rule: str) -> None:
    text = path.read_text(encoding="utf-8")
    if needle not in text:
        fail(path, 1, rule, "<missing required copy>", f"include {needle!r}")


def wrapper(path: pathlib.Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8")
    frontmatter, body, _ = split_frontmatter(text)
    if path == GEN_ROOT:
        body = body.split("\n## ", 1)[0]
    elif path.name == "_index.md":
        body = body.split("\n- ", 1)[0]
    else:
        source_heading = re.search(r"\n#\s+", body)
        if source_heading:
            body = body[: source_heading.start()]
        else:
            body = "\n".join(body.splitlines()[:35])
    return frontmatter, body


def validate_generated_wrappers() -> int:
    checked = 0
    artifact_files = sorted(GEN_ARTIFACT_ROOT.rglob("*.md"))
    for path in artifact_files:
        frontmatter, intro = wrapper(path)
        checked += 1
        if "generated: true" not in frontmatter:
            fail(path, 1, "generated-artifact-wrapper", "<missing generated: true>", "generated artifact pages must declare generated: true")
        if path == GEN_ROOT:
            for needle in [
                "Generated examples from the HELIX project's own HELIX documents.",
                "start with the [artifact-type catalog](/artifact-types/)",
                "edits should be made in the source, not here",
            ]:
                if needle not in intro:
                    fail(path, 1, "generated-artifact-wrapper", "<missing root intro copy>", f"include {needle!r}")
        elif path.name == "_index.md":
            for needle in [
                "Examples from HELIX's own docs.",
                "docs/helix/",
                "[artifact-type catalog](/artifact-types/)",
            ]:
                if needle not in intro:
                    fail(path, 1, "generated-artifact-wrapper", "<missing collection intro copy>", f"include {needle!r}")
        else:
            for needle in [
                "Example from HELIX's own docs.",
                "docs/helix/",
                "[artifact-type catalog](/artifact-types/)",
                "Historical plans and reports may describe retired architecture.",
            ]:
                if needle not in intro:
                    fail(path, 1, "generated-artifact-wrapper", "<missing leaf intro copy>", f"include {needle!r}")
            if "source:" not in frontmatter:
                fail(path, 1, "generated-artifact-wrapper", "<missing source frontmatter>", "include the docs/helix source path")
    return checked


for file_path in strict_files():
    scan_legacy_and_public_terms(file_path)

for file_path in public_card_files():
    scan_cards(file_path)

assert_contains(
    pathlib.Path("docs/website/content/_index.md"),
    "skill reads your project documents",
    "positive-public-contract",
)
assert_contains(
    pathlib.Path("docs/website/content/use/_index.md"),
    "are reusable HELIX document patterns",
    "positive-public-contract",
)
assert_contains(
    pathlib.Path("docs/website/content/use/getting-started.md"),
    "Start with documents, not tooling",
    "positive-public-contract",
)
assert_contains(
    pathlib.Path("docs/website/content/artifact-types/_index.md"),
    "is the artifact-type catalog: HELIX document shapes, prompts, and quality rules.",
    "positive-public-contract",
)
assert_contains(
    GEN_ROOT,
    "Generated examples from the HELIX project's own HELIX documents.",
    "positive-public-contract",
)

generated_count = validate_generated_wrappers()

if errors:
    print("microsite voice validation failed:", file=sys.stderr)
    for err in errors:
        print(f"  {err}", file=sys.stderr)
    raise SystemExit(1)

print(
    f"OK: checked {len(strict_files())} strict files, "
    f"{len(public_card_files())} public card files, and {generated_count} generated artifact wrappers"
)
PY
