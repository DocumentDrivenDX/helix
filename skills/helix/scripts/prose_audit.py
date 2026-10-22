"""prose_audit — measure an instance's prose against its voice profile.

Used by validate-instance.py. Reads the rules from `workflows/voice.yml`: each profile's `limits`
(words per sentence, sentences per paragraph or list item, words per table cell) and the shared
`prose` phrase lists. A type's `meta.yml` may add `prose.budget_words`, a word budget for the whole
instance. The procedure that resolves the findings is `workflows/references/writing-pass.md`.

What is read: paragraphs, list items, table cells, and block quotes. What is not: frontmatter,
headings, fenced code, HTML comments, and generated blocks between
`<!-- <name>: ... -->` and `<!-- /<name> -->` markers. A collapsed `<details>` block is read but
does not count toward the budget. A type's `meta.yml` may list `prose.skip_lines`, regular
expressions for lines that hold machine-read fields (a slide's `**Visual**:` spec), which are not
prose and are not read. Standard library only.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+")
TABLE_RULE = re.compile(r"^\|[\s:|-]+\|?$")
LINK = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")
TAG = re.compile(r"<[^>]+>")
EMPHASIS = re.compile(r"(?<!\w)([*_])(\S(?:.*?\S)?)\1(?!\w)")
MENTION = re.compile(r'"[^"]*"|“[^”]*”|`[^`]*`')
GENERATED_OPEN = re.compile(r"^<!-- ([\w-]+): [^>]*-->$")
ABBREVIATIONS = ("e.g.", "i.e.", "etc.", "vs.")
SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-Za-z0-9`\"(\[*_])")
SNIPPET_WORDS = 8


@dataclass(frozen=True)
class Unit:
    line: int
    text: str
    kind: str  # paragraph or cell
    counted: bool  # counts toward a word budget


@dataclass(frozen=True)
class Limits:
    sentence_words: int
    paragraph_sentences: int
    cell_words: int
    budget_words: int = 0


def plain(text: str) -> str:
    text = TAG.sub(" ", LINK.sub(r"\1", text)).replace("**", "").replace("__", "")
    return " ".join(EMPHASIS.sub(r"\2", text).split())


def sentences(text: str) -> list[str]:
    guarded = text
    for abbreviation in ABBREVIATIONS:
        guarded = guarded.replace(abbreviation, abbreviation.replace(".", "\0"))
    return [s.replace("\0", ".") for s in SENTENCE_END.split(guarded) if s.strip()]


def words(text: str) -> int:
    return len(text.split())


class _Scanner:
    """Walks body lines and yields the prose units, tracking what to skip."""

    def __init__(self, closers: set[str], skip: list[re.Pattern[str]]) -> None:
        self.closers = closers  # generated-block names whose closing marker exists
        self.skip = skip  # lines that hold machine-read fields, not prose
        self.fence = False
        self.comment = False
        self.generated: str | None = None
        self.details = False
        self.units: list[Unit] = []
        self.current: list[str] = []
        self.start = 0

    def close(self) -> None:
        if self.current:
            text = plain(" ".join(self.current))
            self.units.append(Unit(self.start, text, "paragraph", not self.details))
            self.current = []

    def skipped(self, stripped: str) -> bool:
        if stripped.startswith("```"):
            self.fence = not self.fence
            return True
        if self.fence:
            return True
        if self.generated:
            if stripped.startswith(f"<!-- /{self.generated}"):
                self.generated = None
            return True
        opened = GENERATED_OPEN.match(stripped)
        if opened and opened[1] in self.closers:
            self.generated = opened[1]
            return True
        if stripped.startswith("<!--") or self.comment:
            self.comment = "-->" not in stripped
            return True
        if any(pattern.search(stripped) for pattern in self.skip):
            return True
        if stripped.startswith("<details"):
            self.details = True
        elif stripped.startswith("</details"):
            self.details = False
        return stripped.startswith(("<details", "</details", "<summary"))

    def take(self, number: int, line: str) -> None:
        stripped = line.strip()
        if self.skipped(stripped):
            self.close()
            return
        if not stripped or stripped.startswith(("#", ">", "|")):
            self.close()
            if stripped.startswith("|") and not TABLE_RULE.match(stripped):
                cells = [plain(c) for c in stripped.strip("|").split("|")]
                self.units += [Unit(number, c, "cell", not self.details) for c in cells if c]
            elif stripped.startswith(">"):
                self.units.append(Unit(number, plain(stripped.lstrip("> ")), "paragraph", False))
            return
        if LIST_ITEM.match(line) or not self.current:
            self.close()
            self.start = number
        self.current.append(LIST_ITEM.sub("", stripped))


def units(body: str, base: int, skip_lines: list[str] | None = None) -> list[Unit]:
    """The prose units of a body whose first line is line `base` of the file."""
    skip = [re.compile(pattern) for pattern in skip_lines or []]
    scanner = _Scanner(set(re.findall(r"<!-- /([\w-]+)", body)), skip)
    for offset, line in enumerate(body.splitlines()):
        scanner.take(base + offset, line)
    scanner.close()
    return scanner.units


def _snippet(text: str) -> str:
    head = text.split()[:SNIPPET_WORDS]
    return " ".join(head) + (" ..." if words(text) > SNIPPET_WORDS else "")


def phrases(voice: dict) -> dict[str, str]:
    """Every phrase a profile avoids, mapped to what to write instead."""
    prose = voice.get("prose") or {}
    found: dict[str, str] = {}
    for group in ("avoid_phrases", "information_only", "pronouns"):
        found.update({str(k): str(v) for k, v in (prose.get(group) or {}).items()})
    return found


def limits_for(voice: dict, profile: str, budget_words: int = 0) -> Limits | None:
    entry = ((voice.get("profiles") or {}).get(profile) or {}).get("limits")
    if not entry:
        return None
    return Limits(
        int(entry["sentence_words"]),
        int(entry["paragraph_sentences"]),
        int(entry["cell_words"]),
        int(budget_words or 0),
    )


def audit(
    body: str, base: int, limits: Limits, avoid: dict[str, str], skip_lines: list[str] | None = None
) -> list[tuple[str, str, int]]:
    """Each breach as (check, message, line)."""
    found: list[tuple[str, str, int]] = []
    counted = 0
    for unit in units(body, base, skip_lines):
        counted += words(unit.text) if unit.counted else 0
        if unit.kind == "cell" and words(unit.text) > limits.cell_words:
            found.append(("prose.cell", f"{words(unit.text)} words, limit {limits.cell_words}: {_snippet(unit.text)}", unit.line))
        if unit.kind == "paragraph":
            parts = sentences(unit.text)
            found += [
                ("prose.sentence", f"{words(s)} words, limit {limits.sentence_words}: {_snippet(s)}", unit.line)
                for s in parts
                if words(s) > limits.sentence_words
            ]
            if len(parts) > limits.paragraph_sentences:
                found.append(("prose.paragraph", f"{len(parts)} sentences, limit {limits.paragraph_sentences}: {_snippet(unit.text)}", unit.line))
        used = MENTION.sub(" ", unit.text)
        found += [
            ("prose.avoid", f'"{phrase}": {instead}', unit.line)
            for phrase, instead in avoid.items()
            if re.search(rf"(?<![\w-]){re.escape(phrase)}(?![\w-])", used, re.IGNORECASE)
        ]
    if limits.budget_words and counted > limits.budget_words:
        found.insert(0, ("prose.budget", f"{counted} words, budget {limits.budget_words}", base))
    return found
