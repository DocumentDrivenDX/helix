#!/usr/bin/env python3
"""Land edits from a shared editing surface onto a governed Markdown file as a patch.

Usage:
    draftsync.py blocks FILE                       list the file's addressable blocks
    draftsync.py edits FILE --old OLD.xml --delta DELTA.xml
                                                   turn a Claude Docs changed-blocks read into EDITS.json
    draftsync.py doc-ops FILE --old OLD.xml --now NOW.xml [--from-binding]
                                                   the draft edits that carry the file's changes into the draft
    draftsync.py bind FILE --tool T --origin URL --synced-rev N     record the binding in .helix/bindings.yml
    draftsync.py status FILE                       the binding, and whether the file changed since it
    draftsync.py rebind FILE --synced-rev N --old OLD.xml           move the binding to a draft revision that equals the file
    draftsync.py hook                              a Claude Code PostToolUse hook: notice edits to bound files
    draftsync.py apply FILE --edits EDITS.json [--base-commit REV] [--write] [--no-table-guard]
                                                   [--assessment-tables PATH]

The surface returns what changed; the runtime adapter turns that into EDITS.json, a runtime-neutral list
of operations addressed by block index in the file as it was at the pinned base (`blocks` prints the
index):

    {"ops": [
      {"op": "replace", "block": 4, "text": "new paragraph, heading or item text"},
      {"op": "replace", "block": 9, "cell": 1, "text": "new cell text"},
      {"op": "delete",  "block": 6},
      {"op": "insert",  "after": 4, "kind": "paragraph", "text": "a new paragraph"},
      {"op": "insert",  "after": 4, "kind": "heading", "level": 2, "text": "A new heading"},
      {"op": "insert",  "after": 8, "kind": "item", "like": 7, "text": "a new list item"},
      {"op": "insert",  "after": 9, "kind": "row", "cells": ["a", "b"]}
    ]}

Blocks, in file order after the front matter: heading, paragraph, item (one list item), row (one table
row; the separator row has no index), other (fenced code, quote, HTML). Front matter is never patched.
A replaced block keeps every word that did not change with its original spacing and line breaks, so
untouched text stays byte-identical and the patch shows only the real edit. Blocks of kind `other` are
refused. A numbered item cannot be inserted or deleted unless the items after it are also deleted
(the rest would need renumbering); a table's header row can only go with the whole table. Text is
compared with backslash escapes ignored, so an untouched `\\*` or `\\|` stays as written, and a `|` in new
cell text is escaped. New paragraph text that would read as a heading, list, table or quote is refused.
Files with CRLF line endings are refused.

With --base-commit the edits are applied to the file as it was at that commit and merged into the
current file word by word (merge3); a conflict, meaning both sides changed the same words, stops with
exit 1 and writes nothing unless --prefer git (the file wins) or --prefer doc (the draft wins) is given,
in which case each conflict is reported on stderr. Unless
--no-table-guard is given, the patched file is checked with HELIX's assessment-tables.py: a document
whose generated tables matched their front matter before the patch must still match after it, so an
edit to a generated table is refused and belongs in the `assessment:` or `recommendations:` block.
Without --write nothing is written; the result is printed as a unified diff. The report names the
whole-file sha256 before and after, which is what seals and reviews key on.

`edits` is the Claude Docs adapter's translator: OLD.xml is the doc read at the opening revision
(`{"kind":"view","atRev":N}`) and DELTA.xml the read since it (`{"kind":"view","sinceRev":N}`). It checks that
the old doc and the file have the same sequence of headings, paragraphs, list items and table rows, so a
mismatch stops before anything is applied, and prints EDITS.json. A new list, table or code block, and
formatting it cannot write as Markdown, are refused.

The binding (ADR-020) is one entry per file in `.helix/bindings.yml` (`path`, `tool`, `origin`, `connector`,
`synced_rev`, `base_sha256`) and a `<tool>-bind` attribute in `.gitattributes`. `synced_rev` is a draft
revision whose text equals the file body whose SHA-256 is `base_sha256`; `apply --from-binding` finds that
body in git history as the base, and a conflict is resolved toward the file's system of record
(`ddx.authoring.home`: `repo` or absent means git, `external-tool` means the draft).

Exit codes: 0 ok, 1 refused or conflicted, 2 usage error.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

ITEM = re.compile(r"^(\s*)([-*+]|\d+[.)])(\s+)(\[[ xX]\]\s+)?")
HEADING = re.compile(r"^#{1,6}\s")
SEPARATOR = re.compile(r"^\s*\|?[\s:|-]+\|?\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")
ESCAPED = re.compile(r"\\([!-/:-@\[-`{-~])")


class Refused(Exception):
    pass


@dataclass
class Block:
    kind: str       # heading | paragraph | item | row | other
    start: int      # first line index in the body
    end: int        # one past the last line
    prefix: str     # heading hashes or list marker with indent; empty otherwise


def split_front_matter(text: str) -> tuple[str, str]:
    if text.startswith("---\n"):
        end = text.find("\n---\n", 3)
        if end >= 0:
            return text[: end + 5], text[end + 5:]
        if text.endswith("\n---"):
            return text, ""
    return "", text


def _is_separator(line: str) -> bool:
    return bool(SEPARATOR.match(line)) and "-" in line


def _starts_block(line: str) -> bool:
    return (not line.strip()) or bool(HEADING.match(line) or ITEM.match(line) or FENCE.match(line)
                                      or line.lstrip().startswith(("|", ">", "<")))


def parse(body: str) -> tuple[list[str], list[Block]]:
    lines = body.split("\n")
    blocks: list[Block] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
        elif FENCE.match(line):
            fence = FENCE.match(line).group(1)
            j = i + 1
            while j < len(lines) and not lines[j].lstrip().startswith(fence):
                j += 1
            blocks.append(Block("other", i, min(j + 1, len(lines)), ""))
            i = j + 1
        elif HEADING.match(line):
            blocks.append(Block("heading", i, i + 1, HEADING.match(line).group(0)))
            i += 1
        elif line.lstrip().startswith("|"):
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                if not _is_separator(lines[i]):
                    blocks.append(Block("row", i, i + 1, ""))
                i += 1
        elif line.lstrip().startswith((">", "<")):
            j = i + 1
            while j < len(lines) and lines[j].strip():
                j += 1
            blocks.append(Block("other", i, j, ""))
            i = j
        elif ITEM.match(line):
            m = ITEM.match(line)
            j = i + 1
            while j < len(lines) and lines[j].strip() and not _starts_block(lines[j]):
                j += 1
            blocks.append(Block("item", i, j, m.group(0)))
            i = j
        else:
            j = i + 1
            while j < len(lines) and not _starts_block(lines[j]):
                j += 1
            blocks.append(Block("paragraph", i, j, ""))
            i = j
    return lines, blocks


def norm_word(word: str) -> str:
    """A word with escapes, emphasis style (`_x_` and `*x*`), autolinks and a hard-break backslash made alike."""
    word = ESCAPED.sub(r"\1", word)
    word = re.sub(r"^<(https?://[^>\s]+)>$", r"[\1](\1)", word)
    word = re.sub(r"^_+|_+$", lambda m: "*" * len(m.group(0)), word)
    return word[:-1] if word.endswith("\\") and len(word) > 1 else word


def patch_words(old: str, new: str) -> str:
    """Return `old` with only the words that differ from `new` replaced.

    Kept words keep their original spacing and line breaks, and a backslash escape in a kept word
    stays; the leading whitespace of `old` is kept too. New words join with one space."""
    pieces = re.findall(r"(\s*)(\S+)", old)
    seps = [p[0] for p in pieces]
    old_words = [p[1] for p in pieces]
    new_words = new.split()
    if [norm_word(w) for w in old_words] == [norm_word(w) for w in new_words]:
        return old
    lead = seps[0] if seps else ""
    out: list[str] = []

    def emit(sep: str, word: str) -> None:
        out.append((lead if not out else sep) + word)

    for tag, a1, a2, b1, b2 in difflib.SequenceMatcher(
            None, [norm_word(w) for w in old_words], [norm_word(w) for w in new_words], autojunk=False).get_opcodes():
        if tag == "equal":
            for k in range(a1, a2):
                emit(seps[k] if k else " ", old_words[k])
        elif tag in ("replace", "insert"):
            for k in range(b1, b2):
                emit(" ", new_words[k])
    tail = re.search(r"\s*$", old).group(0)
    return "".join(out) + tail


def _numbered(block: Block) -> bool:
    return bool(re.match(r"\s*\d", block.prefix))


def _list_group(blocks: list[Block], k: int) -> list[int]:
    """Indexes of the list items around item k that belong to one list (adjacent, blank lines allowed)."""
    lo = hi = k
    while lo > 0 and blocks[lo - 1].kind == "item" and blocks[lo].start <= blocks[lo - 1].end + 1:
        lo -= 1
    while hi + 1 < len(blocks) and blocks[hi + 1].kind == "item" and blocks[hi + 1].start <= blocks[hi].end + 1:
        hi += 1
    return list(range(lo, hi + 1))


def split_cells(line: str) -> tuple[str, list[str], bool, str]:
    """(indent, cells, had a trailing pipe, trailing whitespace) of a table row."""
    indent = re.match(r"\s*", line).group(0)
    trail = re.search(r"\s*$", line).group(0)
    inner = line.strip()[1:]
    closed = inner.endswith("|") and not inner.endswith("\\|")
    inner = inner[:-1] if closed else inner
    return indent, re.split(r"(?<!\\)\|", inner), closed, trail


def escape_cell(text: str) -> str:
    return re.sub(r"(?<!\\)\|", r"\\|", text)


def _plain_check(text, what: str, empty_ok: bool = False) -> str:
    if not isinstance(text, str):
        raise Refused(f"{what} needs `text` as a string")
    if "\n" in text:
        raise Refused(f"{what}: `text` is one paragraph and has no line breaks")
    if not text.strip() and not empty_ok:
        raise Refused(f"{what}: the new text is empty; delete the block instead")
    return text


THEMATIC = re.compile(r"^\s*(([-*_])\s*){3,}$|^\s*(=+|-+)\s*$")


def _would_start_a_block(text: str) -> bool:
    return bool(HEADING.match(text) or ITEM.match(text) or FENCE.match(text) or THEMATIC.match(text)
                or text.lstrip().startswith(("|", ">", "<")))


def validate_ops(ops) -> None:
    if not isinstance(ops, list) or not all(isinstance(o, dict) for o in ops):
        raise Refused("`ops` must be a list of operations")
    for o in ops:
        for key in ("block", "after", "cell", "like", "level"):
            if key in o and (isinstance(o[key], bool) or not isinstance(o[key], int)):
                raise Refused(f"`{key}` must be an integer in {o}")
        if "level" in o and not 1 <= o["level"] <= 6:
            raise Refused(f"`level` must be 1 to 6 in {o}")
        if "cells" in o and not (isinstance(o["cells"], list) and all(isinstance(c, str) for c in o["cells"])):
            raise Refused(f"`cells` must be a list of strings in {o}")


def apply_ops(body: str, ops: list[dict]) -> str:
    validate_ops(ops)
    lines, blocks = parse(body)
    plan: list[tuple[int, int, list[str]]] = []          # replacements and deletions: (start, end, lines)
    inserts: dict[int, list[str]] = {}                   # pure inserts by line, in op order
    seen: set = set()
    cell_edits: dict[int, dict[int, str]] = {}
    deleted = {o["block"] for o in ops if o.get("op") == "delete" and isinstance(o.get("block"), int)}
    numbered_adds: dict[int, int] = {}

    def block(n) -> Block:
        if not isinstance(n, int) or not 0 <= n < len(blocks):
            raise Refused(f"block {n} does not exist (the file has {len(blocks)} blocks, 0 to {len(blocks) - 1})")
        return blocks[n]

    def table_rows(n: int) -> list[int]:
        lo = hi = n
        def joined(a: int, b2: int) -> bool:           # rows a and b2 are lines of one table
            gap = blocks[b2].start - blocks[a].end
            return gap == 0 or (gap == 1 and _is_separator(lines[blocks[a].end]))
        while lo > 0 and blocks[lo - 1].kind == "row" and joined(lo - 1, lo):
            lo -= 1
        while hi + 1 < len(blocks) and blocks[hi + 1].kind == "row" and joined(hi, hi + 1):
            hi += 1
        return list(range(lo, hi + 1))

    for op in ops:
        kind = op.get("op")
        if kind in ("replace", "delete"):
            n = op.get("block")
            b = block(n)
            key = (n, op.get("cell")) if kind == "replace" and b.kind == "row" else (n, None)
            if key in seen or (kind == "delete" and any(k[0] == n for k in seen)) or (kind == "replace" and (n, None) in seen and key != (n, None)):
                raise Refused(f"block {n} is edited twice")
            seen.add(key)
            if b.kind == "other":
                raise Refused(f"block {n} is code, a quote or HTML; edit it in the repository")
            if "cell" in op and b.kind != "row":
                raise Refused(f"block {n} is not a table row, so `cell` does not apply")
            if kind == "delete":
                end = b.end
                if b.kind == "item" and _numbered(b):
                    group = _list_group(blocks, n)
                    if any(k not in deleted for k in group if k > n):
                        raise Refused(f"block {n} is a numbered item that is not last; deleting it would renumber the list")
                if b.kind == "row":
                    rows = table_rows(n)
                    if n == rows[0]:
                        if any(k not in deleted for k in rows):
                            raise Refused(f"block {n} is the header row of a table that keeps other rows; edit it in the repository")
                        if end < len(lines) and _is_separator(lines[end]):
                            end += 1                         # the separator goes with a whole table
                if b.kind in ("paragraph", "heading") and end < len(lines) - 1 and not lines[end].strip():
                    end += 1
                plan.append((b.start, end, []))
            elif b.kind == "row":
                c = op.get("cell")
                _, cells, _, _ = split_cells(lines[b.start])
                if not isinstance(c, int) or not 0 <= c < len(cells):
                    raise Refused(f"block {n} is a table row with {len(cells)} cells; `cell` is required")
                cell_edits.setdefault(n, {})[c] = _plain_check(op.get("text"), f"block {n}", empty_ok=True)
            else:
                text = _plain_check(op.get("text"), f"block {n}")
                first = lines[b.start][len(b.prefix):]
                old = "\n".join([first] + lines[b.start + 1:b.end])
                new = patch_words(old, text)
                if b.kind in ("paragraph", "item") and new != old and _would_start_a_block(new.lstrip().split("\n")[0]) \
                        and not _would_start_a_block(first):
                    raise Refused(f"the new text of block {n} would read as a heading, list, table or quote")
                plan.append((b.start, b.end, (b.prefix + new).split("\n")))
        elif kind == "insert":
            after = op.get("after")
            b = block(after)
            what = op.get("kind", "paragraph")
            if what == "row":
                if b.kind != "row":
                    raise Refused(f"cannot insert a row after block {after}: it is not a table row")
                if "cells" not in op:
                    raise Refused("a row insert needs `cells`")
                for cell_text in op["cells"]:
                    _plain_check(cell_text, "a new row's cell", empty_ok=True)
                if len(op["cells"]) != len(split_cells(lines[b.start])[1]):
                    raise Refused(f"a new row needs {len(split_cells(lines[b.start])[1])} cells like its table, not {len(op['cells'])}")
                at = b.end + 1 if b.end < len(lines) and _is_separator(lines[b.end]) else b.end
                inserts.setdefault(at, []).append("| " + " | ".join(escape_cell(c) for c in op["cells"]) + " |")
            elif what == "item":
                like = block(op["like"]) if "like" in op else b
                if like.kind != "item":
                    raise Refused(f"cannot insert an item after block {after}: it is not a list item")
                text = _plain_check(op.get("text"), "an inserted item")
                if _would_start_a_block(text):
                    raise Refused("the new item text would read as a heading, list, table or quote")
                if "indent" in op:
                    prefix = re.match(r"\s*", like.prefix).group(0) + " " * op["indent"] + "- "
                    inserts.setdefault(b.end, []).append(prefix + text)
                    continue
                if _numbered(like):
                    lk = op["like"] if "like" in op else after
                    group = _list_group(blocks, lk)
                    if lk != group[-1] or any(k in deleted for k in group):
                        raise Refused(f"cannot insert after numbered item {lk}: later items or deleted items would need renumbering")
                    numbered_adds[lk] = numbered_adds.get(lk, 0) + 1
                    num = int(re.search(r"\d+", like.prefix).group(0)) + numbered_adds[lk]
                    prefix = re.sub(r"\d+", str(num), like.prefix, count=1)
                else:
                    prefix = like.prefix
                prefix = re.sub(r"\[[xX]\]", "[ ]", prefix)         # a new task is not done
                inserts.setdefault(b.end, []).append(prefix + text)
            elif what in ("paragraph", "heading"):
                text = _plain_check(op.get("text"), "an inserted block")
                if what == "paragraph" and _would_start_a_block(text):
                    raise Refused("the new paragraph would read as a heading, list, table or quote")
                line = ("#" * int(op.get("level", 2)) + " " + text) if what == "heading" else text
                lead = ["", line] + ([""] if b.end < len(lines) and lines[b.end].strip() else [])
                inserts.setdefault(b.end, []).extend(lead)
            else:
                raise Refused(f"unknown insert kind {what!r}")
        else:
            raise Refused(f"unknown op {kind!r}")
    for n, edits in cell_edits.items():
        b = blocks[n]
        indent, cells, closed, trail = split_cells(lines[b.start])
        for c, text in edits.items():
            lead = re.match(r"\s*", cells[c]).group(0)
            tail = re.search(r"\s*$", cells[c]).group(0)
            if not cells[c].strip():
                lead, tail = " ", " "
            old = cells[c].strip().replace("\\|", "|")
            cells[c] = lead + escape_cell(patch_words(old, text)) + tail
        plan.append((b.start, b.end, [indent + "|" + "|".join(cells) + ("|" if closed else "") + trail.rstrip("\n")]))
    entries = plan + [(at, at, repl) for at, repl in inserts.items()]
    for start, end, repl in sorted(entries, key=lambda p: (p[0], p[1]), reverse=True):
        lines[start:end] = repl
    return "\n".join(lines)


def apply_text(text: str, ops: list[dict]) -> str:
    if "\r" in text:
        raise Refused("the file has CRLF line endings; convert it to LF or edit it in the repository")
    front, body = split_front_matter(text)
    return front + apply_ops(body, ops)


# ---- Claude Docs changed-blocks read -> EDITS.json -------------------------------------------------

MARKS = {"bold": "**", "italic": "*", "code": "`", "strike": "~~"}


def literal(text: str) -> str:
    """Escape the characters that would start emphasis, code or HTML in text the doc holds literally."""
    return re.sub(r"([*_`<\\])", r"\\\1", text)


def runs_to_markdown(node) -> str:
    out = literal(node.text or "")
    for c in node:
        if c.tag == "text":
            out += runs_to_markdown(c)
        elif c.tag == "code":
            raw = "".join(c.itertext())
            fence = "``" if "`" in raw else "`"
            out += fence + raw + fence
        elif c.tag in MARKS:
            inner = runs_to_markdown(c)
            lead, core, trail = re.match(r"(\s*)(.*?)(\s*)$", inner, re.S).groups()
            out += lead + (MARKS[c.tag] + core + MARKS[c.tag] if core else "") + trail
        elif c.tag == "link":
            out += f"[{runs_to_markdown(c)}]({c.get('href', '')})"
        else:
            raise Refused(f"the doc has <{c.tag}> inside a paragraph, which has no Markdown form here")
        out += literal(c.tail or "")
    return out


def full_ids(root) -> None:
    """A read prints a session's first id in full and later ones short (`.90`); make them all full."""
    prefix = ""
    for e in root.iter():
        ident = e.get("id")
        if not ident:
            continue
        if ident.startswith("."):
            if not prefix:
                raise Refused(f"id {ident} is short and no full id came before it, so its session is unknown")
            e.set("id", prefix + ident)
        else:
            prefix = ident.split(".")[0]


def alnum(text: str) -> str:
    return "".join(ch for ch in text if ch.isalnum())


class OldDoc:
    """The doc at the opening revision, as a tree of ids, with the file's block index of each unit."""

    def __init__(self, xml: str, blocks: list[Block] | None = None, lines: list[str] | None = None):
        root = ET.fromstring(xml)
        full_ids(root)
        self.kids: dict[str, list[str]] = {"root": []}
        self.tag: dict[str, str] = {}
        self.src: dict[str, int] = {}          # unit id -> block index
        self.last: dict[str, int] = {}         # any block id -> last block index in its subtree
        self.first: dict[str, int] = {}        # ... and the first
        self.rev = root.get("rev")
        self.node = root.get("node")
        self.attrs: dict[str, dict] = {}
        self.words: list[str] = []
        self.md: dict[str, str] = {}                      # unit id -> its text as Markdown (rows: see cells)
        self.plain: dict[str, str] = {}                   # ... and as plain text, as the doc stores it
        self.cells: dict[str, list[tuple[str, str, str]]] = {}   # row id -> [(cell id, Markdown, plain)]
        self.h: dict[str, str] = {}
        self.top: dict[str, str] = {}                     # unit id -> id of its top-level block
        self.table_of: dict[str, str] = {}
        self.order: list[str] = []                        # unit ids in document order             # per unit, the doc's words reduced to letters and digits
        kinds: list[str] = []

        def unit(elem, kind: str, ident: str) -> None:
            self.src[ident] = len(kinds)
            kinds.append(kind)
            if kind == "row":
                text = " ".join(runs_to_markdown(p) for p in elem.iter("paragraph"))
            elif kind == "other":
                text = ""
            else:
                para = elem if elem.tag == "paragraph" else elem.find("paragraph")
                text = runs_to_markdown(para) if para is not None else ""
            self.words.append(alnum(text))
            self.h[ident] = elem.get("h") or ""
            self.order.append(ident)
            if kind == "row":
                self.cells[ident] = [(c.get("id"), ESCAPED.sub(r"\1", " ".join(runs_to_markdown(q) for q in c.findall("paragraph"))),
                                      " ".join("".join(q.itertext()) for q in c.findall("paragraph"))) for c in elem.findall("cell")]
            else:
                para = elem if elem.tag == "paragraph" else elem.find("paragraph")
                self.md[ident] = ESCAPED.sub(r"\1", text)
                self.plain[ident] = "".join(para.itertext()) if para is not None else ""

        def walk(elem, parent: str) -> None:
            ident = elem.get("id")
            self.kids[parent].append(ident)
            self.tag[ident] = elem.tag
            self.top[ident] = ident if parent == "root" else self.top.get(parent, ident)
            if elem.tag == "row":
                self.table_of[ident] = parent
            self.attrs[ident] = {k: v for k, v in elem.attrib.items() if k not in ("id", "rev", "h")}
            self.kids[ident] = []
            before = len(kinds)
            if elem.tag == "paragraph":
                unit(elem, "heading" if elem.get("heading") else "paragraph", ident)
            elif elem.tag == "list":
                for li in elem.findall("listItem"):
                    walk(li, ident)
            elif elem.tag == "listItem":
                paras = elem.findall("paragraph")
                unit(elem, "item", ident)
                for c in elem:
                    if c.tag == "paragraph":
                        self.kids[ident].append(c.get("id"))
                        self.tag[c.get("id")] = "paragraph"
                        self.kids[c.get("id")] = []
                    elif c.tag == "list":
                        walk(c, ident)
                if len(paras) != 1:
                    kinds[self.src[ident]] = "other"
            elif elem.tag == "table":
                for r in elem.findall("row"):
                    walk(r, ident)
            elif elem.tag == "row":
                unit(elem, "row", ident)
                for cell in elem.findall("cell"):
                    cid = cell.get("id")
                    self.kids[ident].append(cid)
                    self.tag[cid] = "cell"
                    self.kids[cid] = []
            else:
                unit(elem, "other", ident)
            if len(kinds) > before:
                self.first[ident], self.last[ident] = before, len(kinds) - 1

        for elem in root:
            walk(elem, "root")
        for ident, tag in list(self.tag.items()):          # containers take their last descendant's index
            if ident not in self.last:
                desc = [self.last[k] for k in self.kids.get(ident, []) if k in self.last]
                if desc:
                    self.last[ident] = max(desc)
        if blocks is None:
            return
        want = [b.kind for b in blocks]
        if kinds != want:
            at = next((i for i, (a, b) in enumerate(zip(kinds, want)) if a != b), min(len(kinds), len(want)))
            raise Refused(f"the doc at the opening revision and the file do not line up: block {at} is "
                          f"{kinds[at] if at < len(kinds) else 'missing'} in the doc and "
                          f"{want[at] if at < len(want) else 'missing'} in the file")
        for i, (blk, words) in enumerate(zip(blocks, self.words)):
            if blk.kind != "other" and kinds[i] == blk.kind and alnum(" ".join([lines[blk.start][len(blk.prefix):]] + lines[blk.start + 1:blk.end])) != words:
                raise Refused(f"block {i} has different text in the doc at the opening revision and in the file "
                              "(was the draft made from another version of the file?)")


def edits_from_read(old_xml: str, delta_xml: str, text: str) -> list[dict]:
    lines, blocks = parse(split_front_matter(text)[1])
    old = OldDoc(old_xml, blocks, lines)
    delta = ET.fromstring(delta_xml)
    full_ids(delta)
    if delta.get("since") == "unavailable":
        raise Refused("the read is the whole doc (since='unavailable'), not a delta; compare the doc with the file by hand")
    if (delta.get("node") and old.node and delta.get("node") != old.node) or \
            (delta.get("sinceRev") and old.rev and delta.get("sinceRev") != old.rev):
        raise Refused("the read since the opening revision and the read at it are not of the same doc and revision")
    ops: list[dict] = []

    def para_text(p) -> str:
        return runs_to_markdown(p)

    def block_text(p) -> str:
        text = runs_to_markdown(p)
        if not text.strip():
            raise Refused("a paragraph is empty in the doc; delete the block in the repository instead")
        return text

    def insert_after(prev_id: str | None, make: dict) -> None:
        if prev_id is None or prev_id not in old.last:
            raise Refused("a new block with nothing before it to anchor to; add it in the repository")
        ops.append({"op": "insert", "after": old.last[prev_id], **make})

    def container(elem, old_id: str) -> None:
        olds = old.kids[old_id]
        ptr = 0
        for c in elem:
            if c.tag == "gap":
                n = int(c.get("blocks"))
                if n < 0:
                    raise Refused("the read has a negative gap")
                ptr += n
            elif c.tag == "gone":
                ident = c.get("id")
                if ident not in old.tag:
                    continue                      # born and deleted after the draft was opened: no change
                if ident not in olds or olds.index(ident) != ptr:
                    raise Refused(f"deleted block {ident} is not where the opening doc had it")
                if ident not in old.first:
                    raise Refused(f"deleted block {ident} is a cell or a paragraph inside another block; edit it in the repository")
                ptr += 1
                for i in range(old.first[ident], old.last[ident] + 1):
                    ops.append({"op": "delete", "block": i})
            else:
                ident = c.get("id")
                if ident in olds:
                    if olds.index(ident) != ptr:
                        raise Refused(f"block {ident} is not where the opening doc had it (moved, or the gaps do not add up)")
                    ptr += 1
                    changed(c, ident, old_id)
                else:
                    if ptr > len(olds):
                        raise Refused("the read's gaps are longer than the opening doc")
                    prev = olds[ptr - 1] if ptr else None
                    inserted(c, old_id, prev)

    def changed(c, ident: str, parent: str) -> None:
        tag = c.tag
        now = {k: v for k, v in c.attrib.items() if k not in ("id", "rev", "h")}
        for k in set(now) | set(old.attrs.get(ident, {})):
            if k != "heading" and now.get(k) != old.attrs.get(ident, {}).get(k):
                raise Refused(f"{tag} {ident} changed its `{k}` ({old.attrs.get(ident, {}).get(k)!r} to {now.get(k)!r}); change it in the repository")
        if tag == "paragraph":
            if parent == "root":
                if (blocks[old.src[ident]].kind == "heading") != bool(c.get("heading")):
                    raise Refused(f"block {old.src[ident]} changed between heading and paragraph; change it in the repository")
                if c.get("heading") and int(c.get("heading")) != len(blocks[old.src[ident]].prefix.strip()):
                    raise Refused(f"block {old.src[ident]} changed heading level; change it in the repository")
                ops.append({"op": "replace", "block": old.src[ident], "text": block_text(c)})
            else:                                                  # the paragraph of a list item
                ops.append({"op": "replace", "block": old.src[parent], "text": block_text(c)})
        elif tag in ("list", "table", "listItem", "row"):
            container(c, ident)
        elif tag == "cell":
            row = parent
            col = old.kids[row].index(ident)
            ps = c.findall("paragraph")
            if len(ps) != 1 or len(list(c)) != 1:
                raise Refused(f"cell {ident} has more than one paragraph or other content; edit it in the repository")
            ops.append({"op": "replace", "block": old.src[row], "cell": col, "text": para_text(ps[0])})
        else:
            raise Refused(f"block {ident} is a <{tag}>; edit it in the repository")

    def inserted(c, parent: str, prev: str | None) -> None:
        tag = c.tag
        if tag == "paragraph" and parent == "root":
            lvl = c.get("heading")
            if lvl:
                insert_after(prev, {"kind": "heading", "level": int(lvl), "text": block_text(c)})
            else:
                insert_after(prev, {"kind": "paragraph", "text": block_text(c)})
        elif tag == "row":
            cells = []
            for cell in c.findall("cell"):
                if len(list(cell)) != len(cell.findall("paragraph")):
                    raise Refused("a new row has a cell with a list or other content; add it in the repository")
                cells.append(" ".join(para_text(p) for p in cell.findall("paragraph")))
            insert_after(prev, {"kind": "row", "cells": cells})
        elif tag == "list" and old.tag.get(parent) == "listItem":
            if c.get("kind") != "bullet" or old.kids[parent] and any(old.tag.get(k) == "list" for k in old.kids[parent]):
                raise Refused("a new nested list must be a bullet list under an item with no nested list; add it in the repository")
            for li in c.findall("listItem"):
                if li.find("list") is not None or len(li.findall("paragraph")) != 1:
                    raise Refused("a new nested item with its own nested items or several paragraphs is not supported")
                ops.append({"op": "insert", "after": old.last[parent], "kind": "item", "like": old.src[parent], "indent": 4,
                            "text": block_text(li.find("paragraph"))})
        elif tag == "listItem":
            if c.find("list") is not None or len(c.findall("paragraph")) != 1:
                raise Refused("a new list item with nested items or several paragraphs is not supported; add it in the repository")
            insert_after(prev, {"kind": "item", "like": old.src[prev] if prev in old.src else None, "text": block_text(c.find("paragraph"))})
        else:
            raise Refused(f"a new <{tag}> is not supported; add it in the repository")

    container(delta, "root")
    for op in ops:
        if op.get("like", 0) is None:
            del op["like"]
    return ops


# ---- git -> draft: the doc edits that carry the file's changes into the draft ----------------------------------

MARKUP = re.compile(r"[*`\[\]\\<>]")


def block_texts(lines: list[str], b: Block):
    """A block's text as the doc holds it: unwrapped words; a row's cells as a list."""
    if b.kind == "row":
        return [c.strip().replace("\\|", "|") for c in split_cells(lines[b.start])[1]]
    first = lines[b.start][len(b.prefix):]
    return " ".join(("\n".join([first] + lines[b.start + 1:b.end])).split())


def align_blocks(lb, bb, lm, bm) -> tuple[dict[int, int], list[int]]:
    """Map base block index -> file block index for blocks that survive; and the file blocks that are new."""
    def sig(lines, b):
        t = block_texts(lines, b)
        return (b.kind, alnum(" ".join(t) if isinstance(t, list) else t))
    sb, sm = [sig(lb, b) for b in bb], [sig(lm, b) for b in bm]
    mapping: dict[int, int] = {}
    matched: set[int] = set()
    for tag, a1, a2, b1, b2 in difflib.SequenceMatcher(None, sb, sm, autojunk=False).get_opcodes():
        if tag == "equal":
            for k in range(a2 - a1):
                mapping[a1 + k] = b1 + k
                matched.add(b1 + k)
        elif tag == "replace":                  # pair edited blocks in order by how much text they share
            at = b1
            for i in range(a1, a2):
                best, best_r = None, 0.5
                for j in range(at, b2):
                    if sb[i][0] == sm[j][0]:
                        r = difflib.SequenceMatcher(None, sb[i][1], sm[j][1], autojunk=False).ratio()
                        if r > best_r:
                            best, best_r = j, r
                if best is not None:
                    mapping[i] = best
                    matched.add(best)
                    at = best + 1
    return mapping, [i for i in range(len(bm)) if i not in matched]


def _span_ops(cur: str, merged: str, occurrences) -> list[dict] | str:
    """Doc `replace` ops turning `cur` into `merged`, one per changed span; or a reason string. Both are the
    draft's text as Markdown with escapes removed; a span that touches markup is left to a person."""
    cw, mw = cur.split(), merged.split()
    ops = []
    for tag, a1, a2, b1, b2 in difflib.SequenceMatcher(None, cw, mw, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        old, new = cw[a1:a2], mw[b1:b2]
        if any(MARKUP.search(w) for w in old + new):
            return "the change involves formatting or markup the doc cannot take as plain words; make it in the draft"
        lo, hi = a1, a2
        if not old:                      # a pure insertion needs an anchor word
            if lo == 0 and not cw:
                return "the unit is empty in the draft"
            lo = max(lo - 1, 0)
            hi = lo + 1 if cw else lo
        ctx = 0
        while True:
            text = " ".join(cw[max(lo - ctx, 0):min(hi + ctx, len(cw))])
            edge_lo, edge_hi = max(lo - ctx - 1, 0), min(hi + ctx + 1, len(cw))
            blocked = (lo - ctx - 1 >= 0 and MARKUP.search(cw[lo - ctx - 1])) or (hi + ctx < len(cw) and MARKUP.search(cw[hi + ctx]))
            if occurrences(text) <= 1 or blocked or (max(lo - ctx, 0) == 0 and min(hi + ctx, len(cw)) == len(cw)):
                break
            ctx += 1
        start, end = max(lo - ctx, 0), min(hi + ctx, len(cw))
        find_text = " ".join(cw[start:end])
        pre = " ".join(cw[start:a1]) if a1 > start else ""
        post = " ".join(cw[a2:end]) if a2 < end else ""
        repl = " ".join(x for x in (pre, " ".join(new), post) if x)
        if not old:
            # insertion: keep the anchor word and add after it
            repl = " ".join(cw[start:lo + 1] + new + cw[lo + 1:end]) if cw else " ".join(new)
        ops.append({"find": find_text, "with": repl, "nth": None})
    return ops


def doc_ops(base_text: str, file_text: str, old_xml: str, now_xml: str, record: str) -> dict:
    """The doc `update` ops that bring the file's changes since the base into the draft as it is now.

    `old_xml` is the draft at the synced revision (equal to the base), `now_xml` the draft now. Where the file
    and the draft changed the same words, `record` ("git" or "doc") decides. Returns {"ops": [...], "report": [...]}."""
    lb, bb = parse(split_front_matter(base_text)[1])
    lm, bm = parse(split_front_matter(file_text)[1])
    old = OldDoc(old_xml, bb, lb)
    now = OldDoc(now_xml)
    mapping, new_blocks = align_blocks(lb, bb, lm, bm)
    ids = {old.src[i]: i for i in old.src}
    prefer = "ours" if record == "git" else "theirs"
    ops: list[dict] = []
    report: list[str] = []
    all_plain = [(k, now.plain[k]) for k in now.order if k in now.plain] + \
                [(c[0], c[2]) for k in now.order for c in now.cells.get(k, [])]

    def occurrences_of(text: str) -> int:
        return sum(t.count(text) for _, t in all_plain)

    def nth_of(unit_key: str, text: str) -> int | None:
        total = occurrences_of(text)
        if total <= 1:
            return None
        before = 0
        for k, t in all_plain:
            if k == unit_key:
                break
            before += t.count(text)
        return before + 1

    def replace_in(unit_key: str, cur_plain: str, base_md: str, target_md: str, cur_md: str, within: dict | None) -> None:
        try:
            merged, lost = merge3(base_md, target_md, cur_md, prefer)
        except Conflict as err:                               # cannot happen with a prefer, but stay safe
            report.append(f"conflict in {unit_key}: {err}")
            return
        for c in lost:
            report.append(f"conflict in {unit_key} resolved for {record}: git {c['ours']!r} / draft {c['theirs']!r}")
        if merged.split() == cur_md.split():
            return
        spans = _span_ops(cur_md, merged,
                          lambda t: occurrences_of(t) if within is None else cur_plain.count(t))
        if isinstance(spans, str):
            report.append(f"{unit_key}: {spans}")
            return
        for sp in spans:
            target = {"kind": "find", "text": sp["find"]}
            if within is not None:
                target["within"] = within
            else:
                n = nth_of(unit_key, sp["find"])
                if n:
                    target["nth"] = n
            ops.append({"op": "replace", "target": target, "with": {"from": {"kind": "inline", "content": sp["with"]}, "as": "text"}})

    for b_idx in sorted(ids):
        uid = ids[b_idx]
        m_idx = mapping.get(b_idx)
        if uid not in now.order:
            if m_idx is not None and block_texts(lb, bb[b_idx]) != block_texts(lm, bm[m_idx]):
                report.append(f"block {b_idx}: deleted in the draft and changed in the file; left deleted")
            continue
        if m_idx is None:                                      # the file deleted this block
            unchanged = (now.cells.get(uid) == old.cells.get(uid)) if bb[b_idx].kind == "row" else now.md.get(uid) == old.md.get(uid)
            if unchanged or record == "git":
                ops.append({"op": "delete", "target": {"kind": "blocks", "ids": [uid]}, "ifHash": now.h[uid], "ifRev": int(now.rev or 0)})
                if not unchanged:
                    report.append(f"block {b_idx}: deleted in the file but edited in the draft; the file wins")
            else:
                report.append(f"block {b_idx}: deleted in the file but edited in the draft; the draft wins")
            continue
        target = block_texts(lm, bm[m_idx])
        if bb[b_idx].kind == "row":
            oc, nc = old.cells[uid], now.cells[uid]
            if len(target) != len(oc) or len(nc) != len(oc):
                report.append(f"block {b_idx}: the row's cells differ in number; edit it by hand")
                continue
            tbl = now.table_of.get(uid)
            row_pos = now.kids[tbl].index(uid) if tbl else 0
            for col, ((cid, base_md, _), (_, cur_md, cur_pl)) in enumerate(zip(oc, nc)):
                replace_in(cid, cur_pl, base_md, target[col], cur_md, {"kind": "cell", "table": tbl, "row": row_pos, "col": col})
        else:
            replace_in(uid, now.plain[uid], old.md[uid], target, now.md[uid], None)

    anchor_of_m = {m: ids[b] for b, m in mapping.items() if b in ids and ids[b] in now.order}
    for m_idx in new_blocks:
        prev = next((anchor_of_m[k] for k in range(m_idx - 1, -1, -1) if k in anchor_of_m), None)
        b = bm[m_idx]
        if prev is None:
            report.append(f"file block {m_idx}: new, with nothing before it in the draft to anchor to; add it by hand")
            continue
        if b.kind in ("paragraph", "heading"):
            text = block_texts(lm, b)
            content = ("#" * len(b.prefix.strip()) + " " + text) if b.kind == "heading" else text
            ops.append({"op": "insert", "target": {"kind": "blocks", "ids": [now.top.get(prev, prev)]}, "side": "after",
                        "source": {"as": "markdown", "from": {"kind": "inline", "content": content}}})
        elif b.kind == "row" and now.tag.get(prev) == "row":
            cells = block_texts(lm, b)
            ops.append({"op": "insert", "target": {"kind": "blocks", "ids": [prev]}, "side": "after",
                        "source": {"as": "blocks", "from": {"kind": "inline", "content": [{"type": "row", "content": [
                            {"type": "cell", "content": [{"type": "paragraph", "content": [{"type": "text", "text": c}]}]} for c in cells]}]}}})
        else:
            report.append(f"file block {m_idx} ({b.kind}): new in the file; add it to the draft by hand")
    return {"ops": ops, "report": report}


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout


class Conflict(Exception):
    def __init__(self, conflicts):
        super().__init__(f"{len(conflicts)} conflict(s)")
        self.conflicts = conflicts


def _tokens(text: str) -> tuple[list[tuple[str, str]], str]:
    toks = re.findall(r"(\s*)(\S+)", text)
    return toks, re.search(r"\s*$", text).group(0)


def _hunks(base_words: list[str], other_words: list[str]) -> list[tuple[int, int, int, int]]:
    sm = difflib.SequenceMatcher(None, base_words, other_words, autojunk=False)
    return [(b1, b2, o1, o2) for tag, b1, b2, o1, o2 in sm.get_opcodes() if tag != "equal"]


def merge3(base: str, ours: str, theirs: str, prefer: str | None = None) -> tuple[str, list[dict]]:
    """Three-way merge at the level of words. `prefer` is "ours" or "theirs" (the side that wins a conflict).

    Both sides' changes apply. A conflict is a place where both changed the same words differently (two
    insertions at one spot count). Without `prefer` a conflict raises Conflict; with it the preferred side's
    words are kept and the conflict is reported."""
    bt, btail = _tokens(base)
    ot, otail = _tokens(ours)
    tt, ttail = _tokens(theirs)
    bw = [w for _, w in bt]
    sides = {"ours": (ot, _hunks(bw, [w for _, w in ot])), "theirs": (tt, _hunks(bw, [w for _, w in tt]))}
    hunks = sorted(((h[0], h[1], name, h) for name, (_, hs) in sides.items() for h in hs), key=lambda x: (x[0], x[1], x[2]))
    groups: list[list] = []
    for h in hunks:
        if groups:
            g = groups[-1]
            gend = max(x[1] for x in g)
            gstart = min(x[0] for x in g)
            if h[0] < gend or (h[0] == gend and gend == gstart):
                g.append(h)
                continue
        groups.append([h])
    out: list[tuple[str, str]] = []
    conflicts: list[dict] = []
    pos = 0

    def side_tokens(name: str, gs: int, ge: int) -> list[tuple[str, str]]:
        toks, hs = sides[name]
        res, at = [], gs
        for b1, b2, o1, o2 in sorted(h[3] for h in (x for x in groups_cur if x[2] == name)):
            res += bt[at:b1] + toks[o1:o2]
            at = b2
        return res + bt[at:ge]

    for groups_cur in groups:
        gs = min(x[0] for x in groups_cur)
        ge = max(x[1] for x in groups_cur)
        out += bt[pos:gs]
        names = {x[2] for x in groups_cur}
        if len(names) == 1:
            out += side_tokens(names.pop(), gs, ge)
        else:
            mine, theirs_ = side_tokens("ours", gs, ge), side_tokens("theirs", gs, ge)
            if [w for _, w in mine] == [w for _, w in theirs_]:
                out += mine
            else:
                kept = prefer
                conflicts.append({"base": " ".join(w for _, w in bt[gs:ge]), "ours": " ".join(w for _, w in mine),
                                  "theirs": " ".join(w for _, w in theirs_), "kept": kept})
                out += mine if prefer == "ours" else theirs_ if prefer == "theirs" else mine
        pos = ge
    out += bt[pos:]
    if conflicts and prefer is None:
        raise Conflict(conflicts)
    tail = otail if otail != btail else ttail
    return "".join((sep if i else sep) + w for i, (sep, w) in enumerate(out)) + tail, conflicts


# ---- the binding: sidecar, git attribute, status, hook -----------------------------------------------------

BINDINGS = Path(".helix") / "bindings.yml"


def _yaml():
    try:
        import yaml
    except ImportError:
        raise Refused("PyYAML is required for bindings (python3 -m pip install pyyaml)")
    return yaml


def repo_root(path: Path) -> Path:
    return Path(git(path.resolve().parent, "rev-parse", "--show-toplevel").strip())


def load_bindings(root: Path) -> list[dict]:
    f = root / BINDINGS
    if not f.is_file():
        return []
    data = _yaml().safe_load(f.read_text(encoding="utf-8")) or {}
    entries = list(data.get("bindings") or [])
    for e in entries:
        for key in ("base_sha256", "synced_rev"):         # a digits-only hash or a revision can load as a number
            if key in e:
                e[key] = str(e[key])
    return entries


def save_bindings(root: Path, entries: list[dict]) -> None:
    f = root / BINDINGS
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text("# File bindings to shared drafts (ADR-020). Edit with `draftsync.py bind` and `rebind`.\n"
                 + _yaml().safe_dump({"bindings": sorted(entries, key=lambda e: e["path"])}, sort_keys=False), encoding="utf-8")


def body_sha(text: str) -> str:
    return sha(split_front_matter(text)[1])


def bound_tool(root: Path, rel: str) -> str | None:
    """The surface a path is bound to by a `<tool>-bind` git attribute, or None."""
    r = subprocess.run(["git", "-C", str(root), "check-attr", "-a", "--", rel], capture_output=True, text=True)
    for line in r.stdout.splitlines():
        _, attr, value = (part.strip() for part in line.split(":", 2))
        if attr.endswith("-bind") and value not in ("unspecified", "unset"):
            return attr[: -len("-bind")]
    return None


def record_of(text: str) -> str:
    """The system of record from `ddx.authoring.home`: `git` for repo or absent, `doc` for external-tool."""
    front = split_front_matter(text)[0]
    if not front:
        return "git"
    try:
        home = ((_yaml().safe_load(front[4:front.rindex("---")]) or {}).get("ddx") or {}).get("authoring", {}).get("home")
    except Exception:
        return "git"
    return "doc" if home == "external-tool" else "git"


def find_base(root: Path, rel: str, base_sha256: str) -> str:
    for commit in git(root, "log", "--format=%H", "--", rel).split():
        text = git(root, "show", f"{commit}:{rel}")
        if body_sha(text) == base_sha256:
            return text
    raise Refused(f"no version of {rel} in git history has the body {base_sha256[:12]}; rebind it")


def entry_for(root: Path, rel: str) -> dict:
    for e in load_bindings(root):
        if e["path"] == rel:
            return e
    raise Refused(f"{rel} has no entry in {BINDINGS}")


def status_of(file: Path) -> dict:
    root = repo_root(file)
    rel = file.resolve().relative_to(root.resolve()).as_posix()
    tool = bound_tool(root, rel)
    entry = next((e for e in load_bindings(root) if e["path"] == rel), None)
    out = {"path": rel, "bound": bool(tool and entry), "attribute": tool}
    if out["bound"]:
        text = read(file)
        out.update(tool=entry.get("tool"), origin=entry.get("origin"), connector=entry.get("connector"),
                   synced_rev=entry.get("synced_rev"), record=record_of(text),
                   file_changed_since_base=body_sha(text) != entry.get("base_sha256"))
    return out


def hook() -> int:
    """PostToolUse hook: tell the agent when a bound file was edited. Silent and exit 0 for anything else."""
    try:
        data = json.loads(sys.stdin.read() or "{}")
        target = (data.get("tool_input") or {}).get("file_path")
        if not target:
            return 0
        path = Path(target) if Path(target).is_absolute() else Path(data.get("cwd") or ".") / target
        if not path.is_file():
            return 0
        st = status_of(path)
        if not st["bound"] or not st["file_changed_since_base"]:
            return 0
        root = repo_root(path)
        pending = Path(git(root, "rev-parse", "--absolute-git-dir").strip()) / "draftsync-pending"
        pending.mkdir(exist_ok=True)
        (pending / (hashlib.sha1(st["path"].encode()).hexdigest() + ".json")).write_text(json.dumps(st))
        if st["record"] == "doc":
            note = (f"{st['path']} is bound to a {st['tool']} draft ({st['origin']}) and the draft is its system of record. "
                    "This edit is a conflict in waiting: where the draft changed the same words, the draft wins and the edit "
                    "is overwritten. Prefer editing the draft, or tell the user before syncing.")
        else:
            note = (f"{st['path']} is bound to a {st['tool']} draft ({st['origin']}) and git is its system of record. "
                    "This edit is not yet in the draft. When it is committed or merged, run the shared-edit sync "
                    "(workflows/modes/shared-edit.md) to merge it with the draft's changes and write it back.")
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": note}}))
    except Exception:                      # a hook must never get in the way of an edit
        return 0
    return 0


def find_tables_script(start: Path) -> Path | None:
    for parent in [start.resolve(), *start.resolve().parents, *Path(__file__).resolve().parents]:
        c = parent / "skills" / "helix" / "scripts" / "assessment-tables.py"
        if c.is_file():
            return c
    return None


def tables_ok(script: Path, path: Path, text: str) -> bool:
    """True when the document's generated tables match its front matter (or it has none)."""
    probe = path.with_name(f"{path.stem}.draftsync-probe-{os.getpid()}{path.suffix}")
    try:
        with open(probe, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        r = subprocess.run([sys.executable, str(script), str(probe)], capture_output=True, text=True)
        first = r.stdout.lstrip().split(" ", 1)[0]
        if r.returncode not in (0, 1) or first not in ("ok", "skip", "FAIL", "wrote"):
            raise Refused("the generated-table check could not run (is PyYAML installed for this Python?): "
                          + (r.stderr.strip() or r.stdout.strip() or f"exit {r.returncode}"))
        return first != "FAIL"
    finally:
        probe.unlink(missing_ok=True)


def read(path: Path) -> str:
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Land edits from a shared editing surface as a patch.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("blocks")
    b.add_argument("file", type=Path)
    e = sub.add_parser("edits")
    e.add_argument("file", type=Path)
    e.add_argument("--old", type=Path, required=True)
    e.add_argument("--delta", type=Path, required=True)
    e.add_argument("--base-commit")
    e.add_argument("--from-binding", action="store_true")
    bd = sub.add_parser("bind")
    bd.add_argument("file", type=Path)
    bd.add_argument("--tool", required=True)
    bd.add_argument("--origin", required=True)
    bd.add_argument("--connector")
    bd.add_argument("--synced-rev", required=True)
    bd.add_argument("--base-sha256")
    st_ = sub.add_parser("status")
    st_.add_argument("file", type=Path)
    rb = sub.add_parser("rebind")
    rb.add_argument("file", type=Path)
    rb.add_argument("--synced-rev", required=True)
    rb.add_argument("--old", type=Path, required=True)
    dp = sub.add_parser("doc-ops")
    dp.add_argument("file", type=Path)
    dp.add_argument("--old", type=Path, required=True, help="the draft at the synced revision")
    dp.add_argument("--now", type=Path, required=True, help="the draft now, in full")
    dp.add_argument("--base-commit")
    dp.add_argument("--from-binding", action="store_true")
    dp.add_argument("--prefer", choices=("git", "doc"))
    sub.add_parser("hook")
    a = sub.add_parser("apply")
    a.add_argument("file", type=Path)
    a.add_argument("--edits", type=Path, required=True)
    a.add_argument("--base-commit")
    a.add_argument("--from-binding", action="store_true", help="take the base from the binding and the winner from the record")
    a.add_argument("--write", action="store_true")
    a.add_argument("--prefer", choices=("git", "doc"), help="the system of record, which wins a conflict")
    a.add_argument("--no-table-guard", action="store_true")
    a.add_argument("--assessment-tables", type=Path)
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="backslashreplace")

    def base_text(current: str) -> str:
        if getattr(args, "from_binding", False):
            root = repo_root(args.file)
            rel = args.file.resolve().relative_to(root.resolve()).as_posix()
            return find_base(root, rel, entry_for(root, rel)["base_sha256"])
        if not args.base_commit:
            return current
        if args.base_commit.startswith("-"):
            raise Refused("--base-commit must be a commit, not an option")
        root = Path(git(args.file.resolve().parent, "rev-parse", "--show-toplevel").strip())
        rel = args.file.resolve().relative_to(root.resolve())
        return git(root, "show", f"{args.base_commit}:{rel.as_posix()}")

    if args.cmd == "hook":
        return hook()
    try:
        current = read(args.file)
        if "\r" in current:
            raise Refused("the file has CRLF line endings; convert it to LF or edit it in the repository")
        if args.cmd == "blocks":
            lines, blocks = parse(split_front_matter(current)[1])
            for n, blk in enumerate(blocks):
                print(f"{n}\t{blk.kind}\t{lines[blk.start][:70]}")
            return 0

        if args.cmd == "status":
            print(json.dumps(status_of(args.file), indent=2))
            return 0

        if args.cmd == "bind":
            root = repo_root(args.file)
            rel = args.file.resolve().relative_to(root.resolve()).as_posix()
            entries = [e for e in load_bindings(root) if e["path"] != rel]
            entry = {"path": rel, "tool": args.tool, "origin": args.origin, "synced_rev": args.synced_rev,
                     "base_sha256": args.base_sha256 or body_sha(current)}
            if args.connector:
                entry["connector"] = args.connector
            save_bindings(root, entries + [entry])
            if bound_tool(root, rel) != args.tool:
                with open(root / ".gitattributes", "a", encoding="utf-8") as f:
                    f.write(f"{rel} {args.tool}-bind\n")
            print(f"bound {rel} to {args.tool} at revision {args.synced_rev}")
            return 0

        if args.cmd == "rebind":
            root = repo_root(args.file)
            rel = args.file.resolve().relative_to(root.resolve()).as_posix()
            entry = entry_for(root, rel)
            lines, blocks = parse(split_front_matter(current)[1])
            OldDoc(read(args.old), blocks, lines)          # refuses unless the draft at that revision equals the file
            entry.update(synced_rev=args.synced_rev, base_sha256=body_sha(current))
            save_bindings(root, [e for e in load_bindings(root) if e["path"] != rel] + [entry])
            print(f"rebound {rel} to revision {args.synced_rev}")
            return 0

        if args.cmd == "doc-ops":
            out = doc_ops(base_text(current), current, read(args.old), read(args.now), args.prefer or record_of(current))
            print(json.dumps(out, indent=2))
            return 0

        if args.cmd == "edits":
            ops = edits_from_read(read(args.old), read(args.delta), base_text(current))
            print(json.dumps({"ops": ops}, indent=2))
            return 0

        ops = json.loads(read(args.edits))["ops"]
        base = base_text(current)
        result = apply_text(base, ops)
        if base != current:
            prefer = args.prefer or (record_of(current) if args.from_binding else None)
            try:
                result, lost = merge3(base, current, result, {"git": "ours", "doc": "theirs"}.get(prefer))
            except Conflict as err:
                shown = "; ".join(f"git: {c['ours']!r} / draft: {c['theirs']!r}" for c in err.conflicts[:3])
                raise Refused(f"the file changed since the base and {len(err.conflicts)} change(s) conflict "
                              f"({shown}); pass --prefer git or --prefer doc, or ask the reviewer which text wins")
            for c in lost:
                print(f"conflict resolved for {prefer}: git {c['ours']!r} / draft {c['theirs']!r}", file=sys.stderr)
        if not args.no_table_guard:
            script = args.assessment_tables or find_tables_script(args.file)
            if script is None:
                raise Refused("assessment-tables.py not found; pass --assessment-tables PATH or --no-table-guard")
            if tables_ok(script, args.file, current) and not tables_ok(script, args.file, result):
                raise Refused("an edit changed a generated table; make the edit in the `assessment:` or "
                              "`recommendations:` block instead")
    except Refused as err:
        print(f"refused: {err}", file=sys.stderr)
        return 1
    except (OSError, ValueError, KeyError, TypeError, AttributeError, IndexError, ET.ParseError,
            subprocess.CalledProcessError) as err:
        print(f"error: {type(err).__name__}: {err}", file=sys.stderr)
        return 2

    sys.stdout.writelines(difflib.unified_diff(current.splitlines(True), result.splitlines(True), "current", "patched"))
    print(f"sha256 before {sha(current)}\nsha256 after  {sha(result)}\nfile hash {'changed' if result != current else 'unchanged'}")
    if args.write and result != current:
        with open(args.file, "w", encoding="utf-8", newline="") as f:
            f.write(result)
        print(f"wrote {args.file}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
