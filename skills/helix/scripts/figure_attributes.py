"""Figure attributes: the provenance of a figure, written as an MDITA-style attribute list.

A figure (a price, a limit, a date, a support window) may end with `{basis=... accessed=... source=...}`,
in a table cell, at the end of a list item, or at the end of a paragraph:

    | Support window | five years per major | {basis=published accessed=2026-11-06 source="postgresql.org/support/versioning"} |

`basis` is `published` (the maker states it), `third-party` (someone else estimated it), or
`not-published` (searched and absent). Unless the basis is `not-published`, `source` and `accessed`
are required, and `accessed` is a YYYY-MM-DD date. This turns the vocabulary in a brief's "How to
Read This Profile" table into a rule.

Reading rules. The check is opt-in by presence: an attribute list that names `basis`, `source` or
`accessed` is held to the rule, and other lists (`{keys=pg role=evaluates}`) are ignored. Names are
case-insensitive and may have spaces around `=`; a value is a bare word or a double-quoted string
(which may contain braces); a list may run over several lines; an attribute written twice is an
error. Code (fenced with backticks or tildes, or inline with any number of backticks), HTML
comments, and link destinations and titles are not read, so the syntax can be documented.
"""
from __future__ import annotations

import datetime
import re

BASES = ("published", "third-party", "not-published")
OURS = {"basis", "source", "accessed"}
MAX_LIST = 600  # characters; a longer run is prose, not an attribute list

FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})[^\n]*$")
INLINE_CODE = re.compile(r"(`+)(?!`)(.+?)(?<!`)\1(?!`)", re.S)
HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)
LINK_TARGET = re.compile(r"\]\([^)\n]*\)")
PAIR = re.compile(r'\s*([A-Za-z][\w-]*)\s*=\s*("[^"]*"|[^\s"]+)')


def _blank(match: re.Match) -> str:
    """The match as spaces, keeping newlines, so offsets and line numbers stay valid."""
    return re.sub(r"[^\n]", " ", match.group(0))


def _blank_fences(text: str) -> str:
    out, fence = [], None
    for line in text.split("\n"):
        opened = FENCE.match(line)
        if opened and opened.group(1)[0] == "`" and "`" in line.strip()[len(opened.group(1)):]:
            opened = None  # a backtick fence's info string has no backtick: this is inline code
        if fence is None and opened:
            fence = opened.group(1)
            out.append(" " * len(line))
        elif fence is not None:
            closes = opened and opened.group(1)[0] == fence[0] and len(opened.group(1)) >= len(fence) \
                and not line.strip().strip(fence[0])
            if closes:
                fence = None
            out.append(" " * len(line))
        else:
            out.append(line)
    return "\n".join(out)


def readable(body: str) -> str:
    """body with everything a figure attribute list cannot be in blanked out, same length."""
    text = _blank_fences(body)
    for pattern in (HTML_COMMENT, INLINE_CODE, LINK_TARGET):
        text = pattern.sub(_blank, text)
    return text


def _lists(text: str):
    """Yield (offset, inner text) of each `{...}` attribute list; braces inside quotes do not count."""
    i, n = 0, len(text)
    while i < n:
        if text[i] != "{":
            i += 1
            continue
        j, quoted = i + 1, False
        while j < n and j - i < MAX_LIST:
            c = text[j]
            if c == '"':
                quoted = not quoted
            elif not quoted and c == "}":
                yield i, text[i + 1:j]
                break
            elif not quoted and c == "{":
                break
            j += 1
        i += 1


def _bad_date(value: str) -> bool:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return True
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        return True
    return False


def find(body: str) -> list[tuple[int, str, str]]:
    """(offset, check, message) for each malformed figure attribute list in body."""
    out = []
    for offset, inner in _lists(readable(body)):
        pairs = [(k.lower(), v) for k, v in PAIR.findall(inner)]
        if not OURS & {k for k, _ in pairs}:
            continue
        names = [k for k, _ in pairs]
        repeated = sorted({k for k in names if names.count(k) > 1})
        if repeated:
            out.append((offset, "figure.duplicate", f"attribute {', '.join(repeated)} is written more than once"))
            continue
        attrs = {k: v.strip('"') for k, v in pairs}
        basis = attrs.get("basis")
        if basis not in BASES:
            hint = ", without punctuation" if basis and basis.rstrip(",;.") in BASES else ""
            out.append((offset, "figure.basis", f"figure attributes need basis={'|'.join(BASES)}"
                        f"{'' if basis is None else f', not {basis!r}'}{hint}"))
            continue
        if basis == "not-published":
            continue
        for need in ("source", "accessed"):
            if not attrs.get(need):
                out.append((offset, f"figure.{need}", f"a {basis} figure needs {need}= (only not-published may omit it)"))
        accessed = attrs.get("accessed")
        if accessed and _bad_date(accessed):
            out.append((offset, "figure.accessed", f"accessed={accessed!r} is not a YYYY-MM-DD date"))
    return out
