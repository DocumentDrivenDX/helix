#!/usr/bin/env python3
"""Land edits from a shared editing surface onto a governed Markdown file as a patch.

Usage:
    draftsync.py blocks FILE                       list the file's addressable blocks
    draftsync.py edits FILE --old OLD.xml --delta DELTA.xml
                                                   turn a Claude Docs changed-blocks read into EDITS.json
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
current file with `git merge-file`; a conflict stops with exit 1 and writes nothing. Unless
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
    return "".join(ch for ch in text.lower() if ch.isalnum())


class OldDoc:
    """The doc at the opening revision, as a tree of ids, with the file's block index of each unit."""

    def __init__(self, xml: str, blocks: list[Block], lines: list[str]):
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
        self.words: list[str] = []             # per unit, the doc's words reduced to letters and digits
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

        def walk(elem, parent: str) -> None:
            ident = elem.get("id")
            self.kids[parent].append(ident)
            self.tag[ident] = elem.tag
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


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout


def merge_three_way(current: str, base: str, patched: str) -> tuple[str, int]:
    with tempfile.TemporaryDirectory() as d:
        paths = []
        for name, content in (("current", current), ("base", base), ("patched", patched)):
            p = Path(d) / name
            p.write_text(content, encoding="utf-8")
            paths.append(str(p))
        r = subprocess.run(["git", "merge-file", "-p", *paths], capture_output=True, text=True)
        if r.returncode < 0 or r.returncode > 127:
            raise Refused(f"git merge-file failed: {r.stderr.strip()}")
        return r.stdout, r.returncode


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
    a = sub.add_parser("apply")
    a.add_argument("file", type=Path)
    a.add_argument("--edits", type=Path, required=True)
    a.add_argument("--base-commit")
    a.add_argument("--write", action="store_true")
    a.add_argument("--no-table-guard", action="store_true")
    a.add_argument("--assessment-tables", type=Path)
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="backslashreplace")

    def base_text(current: str) -> str:
        if not args.base_commit:
            return current
        if args.base_commit.startswith("-"):
            raise Refused("--base-commit must be a commit, not an option")
        root = Path(git(args.file.resolve().parent, "rev-parse", "--show-toplevel").strip())
        rel = args.file.resolve().relative_to(root.resolve())
        return git(root, "show", f"{args.base_commit}:{rel.as_posix()}")

    try:
        current = read(args.file)
        if "\r" in current:
            raise Refused("the file has CRLF line endings; convert it to LF or edit it in the repository")
        if args.cmd == "blocks":
            lines, blocks = parse(split_front_matter(current)[1])
            for n, blk in enumerate(blocks):
                print(f"{n}\t{blk.kind}\t{lines[blk.start][:70]}")
            return 0

        if args.cmd == "edits":
            ops = edits_from_read(read(args.old), read(args.delta), base_text(current))
            print(json.dumps({"ops": ops}, indent=2))
            return 0

        ops = json.loads(read(args.edits))["ops"]
        base = base_text(current)
        result = apply_text(base, ops)
        if base != current:
            result, conflicts = merge_three_way(current, base, result)
            if conflicts:
                raise Refused(f"the file changed since the base commit and {conflicts} edit(s) conflict; "
                              "ask the reviewer which text wins")
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
