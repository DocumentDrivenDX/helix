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
refused. A numbered item cannot be inserted or deleted unless it is last in its list (the rest would
need renumbering).

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
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

ITEM = re.compile(r"^(\s*)([-*+]|\d+[.)])(\s+)")
HEADING = re.compile(r"^#{1,6}\s")
SEPARATOR = re.compile(r"^\s*\|?[\s:|-]+\|?\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")


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
        end = text.find("\n---\n", 4)
        if end >= 0:
            return text[: end + 5], text[end + 5:]
    return "", text


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
                if not (SEPARATOR.match(lines[i]) and "-" in lines[i]):
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


def patch_words(old: str, new: str) -> str:
    """Return `old` with only the words that differ from `new` replaced; spacing of kept words is original."""
    pieces = re.findall(r"(\s*)(\S+)", old)
    seps = [p[0] for p in pieces]
    old_words = [p[1] for p in pieces]
    new_words = new.split()
    if old_words == new_words:
        return old
    out: list[str] = []

    def emit(sep: str, word: str) -> None:
        out.append((sep if out else "") + word)

    for tag, a1, a2, b1, b2 in difflib.SequenceMatcher(None, old_words, new_words, autojunk=False).get_opcodes():
        if tag == "equal":
            for k in range(a1, a2):
                emit(seps[k], old_words[k])
        elif tag in ("replace", "insert"):
            for k in range(b1, b2):
                emit(" ", new_words[k])
    tail = re.search(r"\s*$", old).group(0)
    return "".join(out) + tail


def _numbered(block: Block) -> bool:
    return bool(re.match(r"\s*\d", block.prefix))


def _last_in_list(blocks: list[Block], k: int) -> bool:
    return not (k + 1 < len(blocks) and blocks[k + 1].kind == "item" and blocks[k + 1].start <= blocks[k].end + 1)


def split_cells(line: str) -> list[str]:
    inner = line.strip()
    inner = inner[1:] if inner.startswith("|") else inner
    inner = inner[:-1] if inner.endswith("|") and not inner.endswith("\\|") else inner
    return re.split(r"(?<!\\)\|", inner)


def apply_ops(body: str, ops: list[dict]) -> str:
    lines, blocks = parse(body)
    seen: set[tuple[str, int]] = set()
    plan: list[tuple[int, int, list[str]]] = []   # (start line, end line, replacement lines)

    def block(n) -> Block:
        if not isinstance(n, int) or not 0 <= n < len(blocks):
            raise Refused(f"block {n} does not exist (the file has {len(blocks)} blocks, 0 to {len(blocks) - 1})")
        return blocks[n]

    for op in ops:
        kind = op.get("op")
        if kind in ("replace", "delete"):
            n = op.get("block")
            b = block(n)
            if (kind, n) in seen or ("replace", n) in seen or ("delete", n) in seen:
                raise Refused(f"block {n} is edited twice")
            seen.add((kind, n))
            if b.kind == "other":
                raise Refused(f"block {n} is code, a quote or HTML; edit it in the repository")
            if kind == "delete":
                if b.kind == "item" and _numbered(b) and not _last_in_list(blocks, n):
                    raise Refused(f"block {n} is a numbered item that is not last; deleting it would renumber the list")
                end = b.end + 1 if b.kind in ("paragraph", "heading") and b.end < len(lines) and not lines[b.end].strip() else b.end
                plan.append((b.start, end, []))
            elif b.kind == "row":
                row = lines[b.start]
                cells = split_cells(row)
                c = op.get("cell")
                if not isinstance(c, int) or not 0 <= c < len(cells):
                    raise Refused(f"block {n} is a table row with {len(cells)} cells; `cell` is required")
                lead = re.match(r"\s*", cells[c]).group(0)
                trail = re.search(r"\s*$", cells[c]).group(0)
                cells[c] = lead + patch_words(cells[c].strip(), op["text"]) + (trail if trail else "")
                indent = re.match(r"\s*", row).group(0)
                plan.append((b.start, b.end, [indent + "|" + "|".join(cells) + "|"]))
            else:
                first = lines[b.start][len(b.prefix):]
                old = "\n".join([first] + lines[b.start + 1:b.end])
                new = patch_words(old, op["text"])
                plan.append((b.start, b.end, (b.prefix + new).split("\n")))
        elif kind == "insert":
            after = op.get("after")
            b = block(after)
            what = op.get("kind", "paragraph")
            if what == "row":
                if b.kind != "row":
                    raise Refused(f"cannot insert a row after block {after}: it is not a table row")
                text = "| " + " | ".join(op["cells"]) + " |"
                plan.append((b.end, b.end, [text]))
            elif what == "item":
                like = block(op["like"]) if "like" in op else b
                if like.kind != "item":
                    raise Refused(f"cannot insert an item after block {after}: it is not a list item")
                if _numbered(like):
                    if not _last_in_list(blocks, after):
                        raise Refused(f"cannot insert after numbered item {after}: later items would need renumbering")
                    num = int(re.search(r"\d+", like.prefix).group(0)) + 1
                    prefix = re.sub(r"\d+", str(num), like.prefix, count=1)
                else:
                    prefix = like.prefix
                plan.append((b.end, b.end, [prefix + op["text"]]))
            elif what == "paragraph":
                plan.append((b.end, b.end, ["", op["text"]]))
            elif what == "heading":
                plan.append((b.end, b.end, ["", "#" * int(op.get("level", 2)) + " " + op["text"]]))
            else:
                raise Refused(f"unknown insert kind {what!r}")
        else:
            raise Refused(f"unknown op {kind!r}")
    merged: list[tuple[int, int, list[str]]] = []
    for start, end, repl in plan:      # inserts at one spot keep the order they were given in
        if start == end and merged and merged[-1][0] == merged[-1][1] == start:
            merged[-1] = (start, end, merged[-1][2] + repl)
        else:
            merged.append((start, end, repl))
    for start, end, repl in sorted(merged, key=lambda p: (p[0], p[1]), reverse=True):
        lines[start:end] = repl
    return "\n".join(lines)


def apply_text(text: str, ops: list[dict]) -> str:
    front, body = split_front_matter(text)
    return front + apply_ops(body, ops)


# ---- Claude Docs changed-blocks read -> EDITS.json -------------------------------------------------

MARKS = {"bold": "**", "italic": "*", "code": "`", "strike": "~~"}


def runs_to_markdown(node) -> str:
    out = node.text or ""
    for c in node:
        if c.tag == "text":
            out += runs_to_markdown(c)
        elif c.tag in MARKS:
            out += MARKS[c.tag] + runs_to_markdown(c) + MARKS[c.tag]
        elif c.tag == "link":
            out += f"[{runs_to_markdown(c)}]({c.get('href', '')})"
        else:
            raise Refused(f"the doc has <{c.tag}> inside a paragraph, which has no Markdown form here")
        out += c.tail or ""
    return out


def full_ids(root) -> None:
    """A read prints a session's first id in full and later ones short (`.90`); make them all full."""
    prefix = ""
    for e in root.iter():
        ident = e.get("id")
        if not ident:
            continue
        if ident.startswith("."):
            e.set("id", prefix + ident)
        else:
            prefix = ident.split(".")[0]


class OldDoc:
    """The doc at the opening revision, as a tree of ids, with the file's block index of each unit."""

    def __init__(self, xml: str, blocks: list[Block], lines: list[str]):
        import xml.etree.ElementTree as ET
        root = ET.fromstring(xml)
        full_ids(root)
        self.kids: dict[str, list[str]] = {"root": []}
        self.tag: dict[str, str] = {}
        self.src: dict[str, int] = {}          # unit id -> block index
        self.last: dict[str, int] = {}         # any block id -> last block index in its subtree
        self.first: dict[str, int] = {}        # ... and the first
        kinds: list[str] = []

        def unit(elem, kind: str, ident: str) -> None:
            self.src[ident] = len(kinds)
            kinds.append(kind)

        def walk(elem, parent: str) -> None:
            ident = elem.get("id")
            self.kids[parent].append(ident)
            self.tag[ident] = elem.tag
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


def edits_from_read(old_xml: str, delta_xml: str, text: str) -> list[dict]:
    import xml.etree.ElementTree as ET
    lines, blocks = parse(split_front_matter(text)[1])
    old = OldDoc(old_xml, blocks, lines)
    delta = ET.fromstring(delta_xml)
    full_ids(delta)
    if delta.get("since") == "unavailable":
        raise Refused("the read is the whole doc (since='unavailable'), not a delta; compare the doc with the file by hand")
    ops: list[dict] = []

    def para_text(p) -> str:
        return runs_to_markdown(p)

    def insert_after(prev_id: str | None, make: dict) -> None:
        if prev_id is None:
            raise Refused("a new block at the start of its container has nothing to anchor to; add it in the repository")
        ops.append({"op": "insert", "after": old.last[prev_id], **make})

    def container(elem, old_id: str) -> None:
        olds = old.kids[old_id]
        ptr = 0
        for c in elem:
            if c.tag == "gap":
                ptr += int(c.get("blocks"))
            elif c.tag == "gone":
                ident = c.get("id")
                if ident not in olds:
                    raise Refused(f"deleted block {ident} is not where the opening doc had it")
                ptr = olds.index(ident) + 1
                for i in range(old.first[ident], old.last[ident] + 1):
                    ops.append({"op": "delete", "block": i})
            else:
                ident = c.get("id")
                if ident in olds:
                    ptr = olds.index(ident) + 1
                    changed(c, ident, old_id)
                else:
                    prev = olds[ptr - 1] if ptr else None
                    inserted(c, old_id, prev)

    def changed(c, ident: str, parent: str) -> None:
        tag = c.tag
        if tag == "paragraph":
            if parent == "root":
                if (blocks[old.src[ident]].kind == "heading") != bool(c.get("heading")):
                    raise Refused(f"block {old.src[ident]} changed between heading and paragraph; change it in the repository")
                ops.append({"op": "replace", "block": old.src[ident], "text": para_text(c)})
            else:                                                  # the paragraph of a list item
                ops.append({"op": "replace", "block": old.src[parent], "text": para_text(c)})
        elif tag in ("list", "table", "listItem", "row"):
            container(c, ident)
        elif tag == "cell":
            row = parent
            col = old.kids[row].index(ident)
            ps = c.findall("paragraph")
            if len(ps) != 1:
                raise Refused(f"cell {ident} has {len(ps)} paragraphs; edit it in the repository")
            ops.append({"op": "replace", "block": old.src[row], "cell": col, "text": para_text(ps[0])})
        else:
            raise Refused(f"block {ident} is a <{tag}>; edit it in the repository")

    def inserted(c, parent: str, prev: str | None) -> None:
        tag = c.tag
        if tag == "paragraph" and parent == "root":
            lvl = c.get("heading")
            if lvl:
                insert_after(prev, {"kind": "heading", "level": int(lvl), "text": para_text(c)})
            else:
                insert_after(prev, {"kind": "paragraph", "text": para_text(c)})
        elif tag == "row":
            cells = []
            for cell in c.findall("cell"):
                ps = cell.findall("paragraph")
                cells.append(" ".join(para_text(p) for p in ps))
            insert_after(prev, {"kind": "row", "cells": cells})
        elif tag == "listItem":
            if c.find("list") is not None or len(c.findall("paragraph")) != 1:
                raise Refused("a new list item with nested items or several paragraphs is not supported; add it in the repository")
            insert_after(prev, {"kind": "item", "like": old.src[prev] if prev in old.src else None, "text": para_text(c.find("paragraph"))})
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
    probe = path.with_name(path.stem + ".draftsync-probe" + path.suffix)
    try:
        probe.write_text(text, encoding="utf-8")
        r = subprocess.run([sys.executable, str(script), str(probe)], capture_output=True, text=True)
        return not r.stdout.lstrip().startswith("FAIL")
    finally:
        probe.unlink(missing_ok=True)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Land edits from a shared editing surface as a patch.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("blocks")
    b.add_argument("file", type=Path)
    e = sub.add_parser("edits")
    e.add_argument("file", type=Path)
    e.add_argument("--old", type=Path, required=True)
    e.add_argument("--delta", type=Path, required=True)
    a = sub.add_parser("apply")
    a.add_argument("file", type=Path)
    a.add_argument("--edits", type=Path, required=True)
    a.add_argument("--base-commit")
    a.add_argument("--write", action="store_true")
    a.add_argument("--no-table-guard", action="store_true")
    a.add_argument("--assessment-tables", type=Path)
    args = ap.parse_args(argv)

    current = args.file.read_text(encoding="utf-8")
    if args.cmd == "blocks":
        lines, blocks = parse(split_front_matter(current)[1])
        for n, blk in enumerate(blocks):
            print(f"{n}\t{blk.kind}\t{lines[blk.start][:70]}")
        return 0

    if args.cmd == "edits":
        try:
            ops = edits_from_read(args.old.read_text(encoding="utf-8"), args.delta.read_text(encoding="utf-8"), current)
        except Refused as err:
            print(f"refused: {err}", file=sys.stderr)
            return 1
        print(json.dumps({"ops": ops}, indent=2))
        return 0

    try:
        ops = json.loads(args.edits.read_text(encoding="utf-8"))["ops"]
        if args.base_commit:
            root = Path(git(args.file.resolve().parent, "rev-parse", "--show-toplevel").strip())
            rel = args.file.resolve().relative_to(root.resolve())
            base = git(root, "show", f"{args.base_commit}:{rel.as_posix()}")
        else:
            base = current
        patched_base = apply_text(base, ops)
        result = patched_base
        if base != current:
            result, conflicts = merge_three_way(current, base, patched_base)
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
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 2

    sys.stdout.writelines(difflib.unified_diff(current.splitlines(True), result.splitlines(True), "current", "patched"))
    print(f"sha256 before {sha(current)}\nsha256 after  {sha(result)}\nfile hash {'changed' if result != current else 'unchanged'}")
    if args.write and result != current:
        args.file.write_text(result, encoding="utf-8")
        print(f"wrote {args.file}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
