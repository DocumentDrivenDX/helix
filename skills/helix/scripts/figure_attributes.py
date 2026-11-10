"""Figure attributes: the provenance of a figure, written as an MDITA-style attribute list.

A figure (a price, a limit, a date, a support window) may end with `{basis=... accessed=... source=...}`,
in a table cell, at the end of a list item, or at the end of a paragraph:

    | Support window | five years per major | {basis=published accessed=2026-11-06 source="postgresql.org/support/versioning"} |

`basis` is `published` (the maker states it), `third-party` (someone else estimated it), or
`not-published` (searched and absent). Unless the basis is `not-published`, `source` and `accessed`
are required, and `accessed` is a YYYY-MM-DD date. This turns the vocabulary in a brief's "How to
Read This Profile" table into a rule. The check is opt-in by presence: a list that names `basis`,
`source` or `accessed` is held to the rule, and other attribute lists are ignored. Fenced and
inline code are skipped, so the syntax can be documented.
"""
from __future__ import annotations

import datetime
import re

BASES = ("published", "third-party", "not-published")
ATTR_LIST = re.compile(r"\{([^{}\n]*)\}")
PAIR = re.compile(r'([A-Za-z][\w-]*)=("[^"\n]*"|\S+)')
INLINE_CODE = re.compile(r"`[^`\n]*`")
OURS = {"basis", "source", "accessed"}


def _blank_code(scan: str) -> str:
    """scan with inline code replaced by spaces, so offsets stay valid."""
    return INLINE_CODE.sub(lambda m: " " * len(m.group(0)), scan)


def _bad_date(value: str) -> bool:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return True
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        return True
    return False


def find(scan: str) -> list[tuple[int, str, str]]:
    """(offset, check, message) for each malformed figure attribute list in scan.

    scan is the body with fenced code already blanked (validate-instance.strip_fences)."""
    out = []
    for m in ATTR_LIST.finditer(_blank_code(scan)):
        attrs = {k: v.strip('"') for k, v in PAIR.findall(m.group(1))}
        if not OURS & attrs.keys():
            continue
        basis = attrs.get("basis")
        if basis not in BASES:
            out.append((m.start(), "figure.basis", f"figure attributes need basis={'|'.join(BASES)}"
                        f"{'' if basis is None else f', not {basis!r}'}"))
            continue
        if basis == "not-published":
            continue
        for need in ("source", "accessed"):
            if not attrs.get(need):
                out.append((m.start(), f"figure.{need}", f"a {basis} figure needs {need}= (only not-published may omit it)"))
        accessed = attrs.get("accessed")
        if accessed and _bad_date(accessed):
            out.append((m.start(), "figure.accessed", f"accessed={accessed!r} is not a YYYY-MM-DD date"))
    return out
