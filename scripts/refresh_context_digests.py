#!/usr/bin/env python3

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
from collections import OrderedDict, defaultdict
from functools import lru_cache
from pathlib import Path


STANDARD_TAGS = ("principles", "concerns", "practices", "adrs", "governing")
STOPWORDS = {
    "a",
    "all",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "if",
    "in",
    "into",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "this",
    "to",
    "use",
    "with",
}
AREA_TOPIC_ALIASES = {
    "site": {"site", "microsite", "hugo", "frontend", "ui"},
    "ui": {"ui", "frontend", "site", "accessibility"},
    "frontend": {"ui", "frontend", "site", "accessibility"},
    "api": {"api", "backend", "service"},
    "backend": {"api", "backend", "service"},
    "data": {"data", "database", "storage"},
    "demo": {"demo", "recording", "asciinema"},
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_section(markdown: str, heading: str) -> str:
    pattern = re.compile(
        rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL
    )
    match = pattern.search(markdown)
    return match.group(1).strip() if match else ""


def strip_markdown(text: str) -> str:
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = text.replace("**", "")
    text = re.sub(r"\s+", " ", text)
    return text.strip(" -")


def strip_frontmatter(markdown: str) -> str:
    if not markdown.startswith("---\n"):
        return markdown
    _, _, remainder = markdown.partition("\n---\n")
    return remainder or markdown


def parse_principles(root: Path, library_root: Path | None = None) -> list[str]:
    library_root = library_root or root
    project = root / "docs/helix/01-frame/principles.md"
    source = (
        project
        if project.exists() and project.stat().st_size
        else library_root / "workflows/principles.md"
    )
    principles = []
    for line in read_text(source).splitlines():
        if line.startswith("### "):
            principles.append(strip_markdown(line[4:]))
    return principles


def parse_active_concerns(markdown: str) -> list[str]:
    names = []
    section = extract_section(markdown, "Active Concerns")
    for line in section.splitlines():
        line = line.strip()
        if not line.startswith("- "):
            continue
        body = line[2:].strip()
        body = body.split(" — ", 1)[0]
        body = body.split(" (", 1)[0]
        body = body.strip("[]")
        if body and not body.startswith("<!--"):
            names.append(strip_markdown(body))
    return names


def parse_overrides(markdown: str) -> dict[str, list[str]]:
    overrides: dict[str, list[str]] = defaultdict(list)
    section = extract_section(markdown, "Project Overrides")
    current = ""
    for raw_line in section.splitlines():
        line = raw_line.rstrip()
        if line.startswith("### "):
            current = strip_markdown(line[4:])
            continue
        if current and line.strip().startswith("- "):
            overrides[current].append(strip_markdown(line.strip()[2:]))
    return overrides


def parse_area_taxonomy(markdown: str) -> list[str]:
    section = extract_section(markdown, "Area Labels")
    areas: list[str] = []
    for line in section.splitlines():
        if "area:" not in line:
            continue
        match = re.search(r"`area:([^`]+)`", line)
        if match:
            areas.append(match.group(1))
    return areas


def parse_concern_areas(path: Path) -> list[str]:
    section = extract_section(read_text(path), "Areas")
    values = []
    for raw in section.splitlines():
        line = raw.strip()
        if not line or line.startswith("## "):
            continue
        values.extend([part.strip() for part in line.split(",") if part.strip()])
    return values


def parse_practice_bullets(path: Path) -> list[str]:
    bullets = []
    for raw in read_text(path).splitlines():
        line = raw.strip()
        if line.startswith("- "):
            bullets.append(strip_markdown(line[2:]))
    return bullets


def resolve_concern_dir(root: Path, name: str, library_root: Path | None = None) -> Path | None:
    library_root = library_root or root
    for candidate in (
        root / "workflows" / "concerns" / name,
        library_root / "workflows" / "concerns" / name,
    ):
        if candidate.exists():
            return candidate
    return None


def build_concern_library(
    root: Path,
    active_concerns: list[str],
    overrides: dict[str, list[str]],
    library_root: Path | None = None,
) -> dict[str, dict[str, list[str]]]:
    library_root = library_root or root
    library: dict[str, dict[str, list[str]]] = {}
    for name in active_concerns:
        concern_dir = resolve_concern_dir(root, name, library_root)
        concern_md = concern_dir / "concern.md" if concern_dir else None
        practices_md = concern_dir / "practices.md" if concern_dir else None
        areas = parse_concern_areas(concern_md) if concern_md and concern_md.exists() else []
        library[name] = {
            "areas": areas,
            "library_practices": parse_practice_bullets(practices_md)[:5]
            if practices_md and practices_md.exists()
            else [],
            "override_practices": overrides.get(name, []),
            "override_lines": overrides.get(name, []),
        }
    return library


@lru_cache(maxsize=None)
def list_markdown_paths(root: Path, library_root: Path | None = None) -> tuple[Path, ...]:
    library_root = library_root or root
    paths: list[Path] = []
    seen: set[Path] = set()
    for directory in (
        root / "docs",
        root / "workflows",
        library_root / "workflows",
    ):
        if directory in seen:
            continue
        seen.add(directory)
        if directory.exists():
            paths.extend(sorted(directory.rglob("*.md")))
    return tuple(paths)


@lru_cache(maxsize=None)
def list_adr_paths(root: Path) -> tuple[Path, ...]:
    adr_dir = root / "docs/helix/02-design/adr"
    if not adr_dir.exists():
        return ()
    return tuple(sorted(adr_dir.glob("ADR-*.md")))


def tokenize(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) > 2 and token not in STOPWORDS
    }


def extract_doc_id(markdown: str) -> str:
    patterns = (
        r"^\s*id:\s*([A-Za-z0-9._-]+)\s*$",
        r"^\*\*[^*]+ID\*\*:\s*`?([A-Za-z0-9._-]+)`?\s*$",
        r"^# [^\n]*\b([A-Z]{2,}-\d{3,}|helix\.[A-Za-z0-9._-]+)\b",
    )
    for pattern in patterns:
        match = re.search(pattern, markdown, re.MULTILINE)
        if match:
            return match.group(1)
    return ""


def extract_markdown_links(markdown: str) -> list[str]:
    return [match.rstrip(".,:;") for match in re.findall(r"\[[^\]]+\]\(([^)]+)\)", markdown)]


def resolve_artifact_path(root: Path, spec: str, library_root: Path | None = None) -> Path | None:
    library_root = library_root or root
    normalized = strip_markdown(spec)
    if not normalized:
        return None
    for direct in (root / normalized, library_root / normalized):
        if direct.exists():
            return direct
    for path in list_markdown_paths(root, library_root):
        text = read_text(path)
        doc_id = extract_doc_id(text)
        if doc_id == normalized:
            return path
        if normalized == path.stem:
            return path
    return None


def iter_markdown_clauses(markdown: str) -> list[str]:
    clauses: list[str] = []
    paragraph: list[str] = []
    in_code = False
    for raw in strip_frontmatter(markdown).splitlines():
        stripped = raw.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            if paragraph:
                clauses.append(strip_markdown(" ".join(paragraph)))
                paragraph = []
            continue
        if in_code:
            continue
        if not stripped:
            if paragraph:
                clauses.append(strip_markdown(" ".join(paragraph)))
                paragraph = []
            continue
        if stripped.startswith("#") or stripped.startswith("|"):
            if paragraph:
                clauses.append(strip_markdown(" ".join(paragraph)))
                paragraph = []
            continue
        bullet = re.match(r"^(?:[-*]|\d+\.)\s+(.*)$", stripped)
        if bullet:
            if paragraph:
                clauses.append(strip_markdown(" ".join(paragraph)))
                paragraph = []
            clauses.append(strip_markdown(bullet.group(1)))
            continue
        paragraph.append(stripped)
    if paragraph:
        clauses.append(strip_markdown(" ".join(paragraph)))
    return [clause for clause in clauses if clause]


def choose_best_clause(candidates: list[str], query: str) -> str:
    if not candidates:
        return ""
    query_tokens = tokenize(query)
    ranked: list[tuple[int, int, str]] = []
    for index, candidate in enumerate(candidates):
        overlap = len(query_tokens & tokenize(candidate))
        boost = 2 if "must" in candidate.lower() or "required" in candidate.lower() else 0
        ranked.append((overlap + boost, -index, candidate))
    ranked.sort(reverse=True)
    if ranked[0][0] == 0:
        return candidates[0]
    return ranked[0][2]


def parse_concern_adr_refs(path: Path) -> list[str]:
    markdown = read_text(path)
    section = extract_section(markdown, "ADR References")
    refs = []
    refs.extend(re.findall(r"\bADR-\d+\b", section))
    refs.extend(extract_markdown_links(section))
    return compact(refs, 6)


def parse_override_adr_refs(lines: list[str]) -> list[str]:
    refs = []
    for line in lines:
        refs.extend(re.findall(r"\bADR-\d+\b", line))
        refs.extend(extract_markdown_links(line))
    return compact(refs, 6)


def extract_adr_rationale(markdown: str) -> str:
    requirements_row = re.search(r"^\|\s*Requirements\s*\|\s*(.*?)\s*\|$", markdown, re.MULTILINE)
    if requirements_row:
        return strip_markdown(requirements_row.group(1))
    problem_row = re.search(r"^\|\s*Problem\s*\|\s*(.*?)\s*\|$", markdown, re.MULTILINE)
    if problem_row:
        return strip_markdown(problem_row.group(1))
    context = extract_section(markdown, "Context")
    return choose_best_clause(iter_markdown_clauses(context), "requirements constraints rationale")


def summarize_adr(root: Path, ref: str, library_root: Path | None = None) -> str:
    path = resolve_artifact_path(root, ref, library_root)
    if path is None or not path.exists():
        return ""
    markdown = read_text(path)
    adr_id = extract_doc_id(markdown) or strip_markdown(ref)
    title_match = re.search(r"^#\s+(.*)$", markdown, re.MULTILINE)
    title = strip_markdown(title_match.group(1)) if title_match else adr_id
    title = re.sub(rf"^{re.escape(adr_id)}:\s*", "", title)
    decision = choose_best_clause(
        iter_markdown_clauses(extract_section(markdown, "Decision")),
        "decision selected approach",
    )
    rationale = extract_adr_rationale(markdown)
    summary = f"{adr_id} {title}"
    if decision:
        summary += f" — {decision}"
    if rationale:
        summary += f" Why: {rationale}"
    return summary


def secondary_adr_matches(root: Path, item: dict, labels: list[str]) -> list[str]:
    spec = strip_markdown(str(item.get("spec-id", "")))
    areas = {label.removeprefix("area:") for label in labels if label.startswith("area:")}
    matches = []
    for path in list_adr_paths(root):
        markdown = read_text(path)
        lowered = markdown.lower()
        if spec and spec in markdown:
            matches.append(path.relative_to(root).as_posix())
            continue
        for area in areas:
            aliases = AREA_TOPIC_ALIASES.get(area, {area})
            if any(alias in lowered for alias in aliases):
                matches.append(path.relative_to(root).as_posix())
                break
    return compact(matches, 6)


def build_adrs(
    root: Path,
    item: dict,
    labels: list[str],
    matched: list[str],
    library: dict[str, dict[str, list[str]]],
    library_root: Path | None = None,
) -> list[str]:
    library_root = library_root or root
    refs: list[str] = []
    for name in matched:
        concern_dir = resolve_concern_dir(root, name, library_root)
        concern_path = concern_dir / "concern.md" if concern_dir else None
        if concern_path and concern_path.exists():
            refs.extend(parse_concern_adr_refs(concern_path))
        refs.extend(parse_override_adr_refs(library[name].get("override_lines", [])))
    refs.extend(secondary_adr_matches(root, item, labels))
    summaries = []
    for ref in OrderedDict.fromkeys(refs):
        summary = summarize_adr(root, ref, library_root)
        if summary:
            summaries.append(summary)
    return compact(summaries, 3)


def select_digest_practices(
    library_practices: list[str], override_practices: list[str], limit: int
) -> list[str]:
    prioritized: list[str] = []
    library_set = set(library_practices)
    if library_practices:
        prioritized.append(library_practices[0])

    chosen_override = ""
    for practice in override_practices:
        if practice not in library_set:
            chosen_override = practice
            break
    if not chosen_override and override_practices:
        chosen_override = override_practices[0]
    if chosen_override:
        prioritized.append(chosen_override)

    prioritized.extend(library_practices[1:])
    prioritized.extend(practice for practice in override_practices if practice != chosen_override)
    return compact(prioritized, limit)


def bead_paths(item: dict) -> list[str]:
    paths = set()
    _, description_body = split_digest(item.get("description", ""))
    haystacks = [item.get("title", ""), description_body, item.get("acceptance", ""), item.get("spec-id", "")]
    patterns = [
        re.compile(r"(?:docs|tests|workflows|website|\.ddx)/[A-Za-z0-9_./:-]+\.[A-Za-z0-9-]+"),
        re.compile(r"(?:scripts|bin)/helix\b"),
    ]
    for text in haystacks:
        for pattern in patterns:
            for match in pattern.findall(text):
                paths.add(match.rstrip(".,:;"))
    return sorted(paths)


def infer_area_labels(item: dict) -> list[str]:
    labels = set(label for label in item.get("labels", []) if label.startswith("area:"))
    title = item.get("title", "").lower()
    for path in bead_paths(item):
        normalized = path.lower()
        if normalized.startswith("website/"):
            labels.add("area:site")
        if normalized.startswith("docs/demos/"):
            labels.add("area:demo")
        if normalized.startswith("docs/"):
            labels.add("area:docs")
        if normalized.startswith("tests/"):
            labels.add("area:testing")
        if normalized.startswith("scripts/") or normalized.startswith("bin/"):
            labels.add("area:cli")
        if normalized.startswith("workflows/") or normalized.startswith(".ddx/"):
            labels.add("area:workflow")
        if "/artifacts/" in normalized:
            labels.add("area:artifacts")
    if "playwright coverage" in title or "deterministic coverage" in title or "deterministic verification" in title:
        labels.add("area:testing")
    if "helix-cli.sh hang" in title:
        labels.add("area:testing")
    if "deleted artifact type" in title or "artifact order consistency" in title:
        labels.add("area:artifacts")
    return sorted(labels)


def concern_matches(bead_areas: set[str], concern_areas: list[str]) -> bool:
    if "all" in concern_areas:
        return True
    aliases = {
        "ui": {"ui", "frontend", "site"},
        "frontend": {"ui", "frontend", "site"},
        "api": {"api", "backend"},
        "backend": {"api", "backend"},
        "site": {"site"},
    }
    expanded = set(bead_areas)
    for area in list(bead_areas):
        expanded |= aliases.get(area, set())
    for concern_area in concern_areas:
        if concern_area in expanded:
            return True
        if aliases.get(concern_area, set()) & bead_areas:
            return True
    return False


def split_digest(description: str) -> tuple[str, str]:
    match = re.match(r"\s*<context-digest>\s*(.*?)\s*</context-digest>\s*(.*)\Z", description, re.DOTALL)
    if not match:
        return "", description.strip()
    return match.group(1), match.group(2).strip()


def extract_extra_tags(digest_inner: str) -> list[str]:
    extras = []
    for match in re.finditer(r"<([a-z-]+)>(.*?)</\1>", digest_inner, re.DOTALL):
        tag = match.group(1)
        if tag not in STANDARD_TAGS:
            extras.append(match.group(0).strip())
    return extras


def compact(items: list[str], limit: int) -> list[str]:
    ordered = list(OrderedDict.fromkeys(item for item in items if item))
    return ordered[:limit]


def build_governing(root: Path, item: dict, library_root: Path | None = None) -> str:
    library_root = library_root or root
    spec = strip_markdown(str(item.get("spec-id", "")))
    if not spec:
        return strip_markdown(str(item.get("acceptance", "")))
    path = resolve_artifact_path(root, spec, library_root)
    if path is None or not path.exists():
        return spec

    markdown = read_text(path)
    artifact_id = extract_doc_id(markdown) or spec
    query = " ".join(
        [
            item.get("title", ""),
            item.get("description", ""),
            item.get("acceptance", ""),
            spec,
        ]
    )
    candidates = []
    for heading in ("Requirements", "Acceptance Criteria", "Constraints", "Problem Statement", "Overview"):
        candidates.extend(iter_markdown_clauses(extract_section(markdown, heading)))
    if not candidates:
        candidates = iter_markdown_clauses(markdown)
    clause = choose_best_clause(candidates, query)
    if clause:
        return f"{artifact_id} — {clause}"
    return artifact_id


def build_digest(
    item: dict,
    principles: list[str],
    library: dict[str, dict[str, list[str]]],
    root: Path,
    library_root: Path | None = None,
) -> tuple[str, list[str]]:
    library_root = library_root or root
    existing_digest, body = split_digest(item.get("description", ""))
    labels = infer_area_labels(item)
    bead_areas = {label.removeprefix("area:") for label in labels}
    matched = [
        name
        for name, data in library.items()
        if concern_matches(bead_areas, data["areas"])
    ]
    adrs = build_adrs(root, item, labels, matched, library, library_root)
    practices = []
    for name in matched:
        practices.extend(
            select_digest_practices(
                library[name]["library_practices"],
                library[name]["override_practices"],
                limit=2,
            )
        )
    extra_tags = extract_extra_tags(existing_digest)

    digest_lines = ["<context-digest>"]
    if principles:
        digest_lines.append(
            f"<principles>{html.escape(' · '.join(principles), quote=False)}</principles>"
        )
    if matched:
        digest_lines.append(
            f"<concerns>{html.escape(' | '.join(compact(matched, 5)), quote=False)}</concerns>"
        )
    if practices:
        digest_lines.append(
            f"<practices>{html.escape(' · '.join(compact(practices, 6)), quote=False)}</practices>"
        )
    if adrs:
        digest_lines.append(f"<adrs>{html.escape(' · '.join(adrs), quote=False)}</adrs>")
    governing = build_governing(root, item, library_root)
    if governing:
        digest_lines.append(f"<governing>{html.escape(governing, quote=False)}</governing>")
    digest_lines.extend(extra_tags)
    digest_lines.append("</context-digest>")

    rebuilt_description = "\n".join(digest_lines)
    if body:
        rebuilt_description += "\n\n" + body
    return rebuilt_description, labels


def run_update(bead_id: str, description: str, labels: list[str]) -> None:
    subprocess.run(
        [
            "ddx",
            "bead",
            "update",
            bead_id,
            "--description",
            description,
            "--labels",
            ",".join(labels),
        ],
        check=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh HELIX bead context digests and area labels.")
    parser.add_argument("--apply", action="store_true", help="Write updates back to the tracker.")
    parser.add_argument("--bead", action="append", default=[], help="Restrict updates to specific bead IDs.")
    parser.add_argument("--root", help="Project root containing the target tracker and docs.")
    parser.add_argument(
        "--library-root",
        help="HELIX library root containing workflows/ and scripts/ resources.",
    )
    parser.add_argument("--tracker", help="Explicit tracker path. Defaults to <root>/.ddx/beads.jsonl.")
    parser.add_argument("--status", default="open", help="Tracker status to target (default: open).")
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    library_root = (
        Path(args.library_root).resolve()
        if args.library_root
        else Path(__file__).resolve().parents[1]
    )
    tracker = Path(args.tracker).resolve() if args.tracker else root / ".ddx/beads.jsonl"
    concerns_path = root / "docs/helix/01-frame/concerns.md"
    concerns_doc = read_text(concerns_path) if concerns_path.exists() else ""
    active_concerns = parse_active_concerns(concerns_doc)
    overrides = parse_overrides(concerns_doc)
    principles = parse_principles(root, library_root)
    library = build_concern_library(root, active_concerns, overrides, library_root)

    targeted = set(args.bead)
    changed = 0
    for line in read_text(tracker).splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        if item.get("status") != args.status:
            continue
        if targeted and item.get("id") not in targeted:
            continue
        new_description, new_labels = build_digest(
            item,
            principles,
            library,
            root,
            library_root,
        )
        old_labels = [label for label in item.get("labels", []) if label.startswith("area:")]
        if new_description == item.get("description", "") and sorted(old_labels) == new_labels:
            continue
        changed += 1
        print(f"{item['id']}: {','.join(old_labels) or '-'} -> {','.join(new_labels) or '-'}")
        if args.apply:
            merged_labels = [label for label in item.get("labels", []) if not label.startswith("area:")] + new_labels
            run_update(item["id"], new_description, merged_labels)
    if not changed:
        print("No bead updates required.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
