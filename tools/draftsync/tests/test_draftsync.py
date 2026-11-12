"""Tests for draftsync: parsing, word-level patching, three-way landing, and the generated-table guard."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import draftsync as ds  # noqa: E402

REPO = Path(__file__).resolve().parents[3]

DOC = """---
ddx:
  id: X-1
---
# Title

A paragraph that is hard wrapped at about
sixty columns, with a citation [1] and a
link [[tech-spike]] and pg_cron.

| a | b |
|---|---|
| one | two words |
| three | four |

- first item that
  continues here
- second item

1. Source one
2. Source two

```
code stays
```
"""


def kinds(text=DOC):
    lines, blocks = ds.parse(ds.split_front_matter(text)[1])
    return [(b.kind, lines[b.start]) for b in blocks]


def test_parse_kinds_and_indices():
    got = [k for k, _ in kinds()]
    assert got == ["heading", "paragraph", "row", "row", "row", "item", "item", "item", "item", "other"]


def test_front_matter_is_never_patched():
    out = ds.apply_text(DOC, [{"op": "replace", "block": 0, "text": "New title"}])
    assert out.startswith(DOC.split("# Title")[0])
    assert "# New title" in out


def test_replace_keeps_untouched_wrapping_byte_identical():
    out = ds.apply_text(DOC, [{"op": "replace", "block": 1, "text":
        "A paragraph that is hard wrapped at about sixty columns, with a citation [2] and a link [[tech-spike]] and pg_cron."}])
    assert out == DOC.replace("citation [1]", "citation [2]")


def test_replace_inserted_words_join_with_single_spaces():
    out = ds.apply_text(DOC, [{"op": "replace", "block": 1, "text":
        "A paragraph that is hard wrapped at about sixty columns, with a very short citation [1] and a link [[tech-spike]] and pg_cron."}])
    assert "with a very short citation [1] and a" in out
    assert out.count("\n") == DOC.count("\n")


def test_identical_text_is_a_no_op():
    text = "A paragraph that is hard wrapped at about sixty columns, with a citation [1] and a link [[tech-spike]] and pg_cron."
    assert ds.apply_text(DOC, [{"op": "replace", "block": 1, "text": text}]) == DOC


def test_table_cell_replace_and_row_insert_and_delete():
    out = ds.apply_text(DOC, [{"op": "replace", "block": 3, "cell": 1, "text": "two"},
                              {"op": "insert", "after": 3, "kind": "row", "cells": ["x", "y"]},
                              {"op": "delete", "block": 4}])
    assert "| one | two |" in out and "| x | y |" in out and "| three | four |" not in out
    assert "|---|---|" in out


def test_row_replace_needs_a_cell():
    with pytest.raises(ds.Refused):
        ds.apply_text(DOC, [{"op": "replace", "block": 2, "text": "x"}])


def test_item_replace_keeps_marker_and_continuation_indent():
    out = ds.apply_text(DOC, [{"op": "replace", "block": 5, "text": "first item that continues right here"}])
    assert "- first item that\n  continues right here\n- second item" in out


def test_insert_paragraph_after_block():
    out = ds.apply_text(DOC, [{"op": "insert", "after": 1, "kind": "paragraph", "text": "Added."}])
    assert "pg_cron.\n\nAdded.\n\n| a | b |" in out


def test_numbered_list_refuses_renumbering_edits():
    with pytest.raises(ds.Refused):
        ds.apply_text(DOC, [{"op": "delete", "block": 7}])
    with pytest.raises(ds.Refused):
        ds.apply_text(DOC, [{"op": "insert", "after": 7, "kind": "item", "text": "x"}])
    out = ds.apply_text(DOC, [{"op": "insert", "after": 8, "kind": "item", "text": "Source three"}])
    assert "2. Source two\n3. Source three\n" in out


def test_other_blocks_and_bad_indices_are_refused():
    with pytest.raises(ds.Refused):
        ds.apply_text(DOC, [{"op": "replace", "block": 9, "text": "x"}])
    with pytest.raises(ds.Refused):
        ds.apply_text(DOC, [{"op": "replace", "block": 99, "text": "x"}])
    with pytest.raises(ds.Refused):
        ds.apply_text(DOC, [{"op": "delete", "block": 1}, {"op": "replace", "block": 1, "text": "x"}])


def test_delete_paragraph_removes_one_blank_line():
    out = ds.apply_text(DOC, [{"op": "delete", "block": 1}])
    assert "# Title\n\n| a | b |" in out


def corpus():
    roots = [REPO / "docs", REPO / "workflows"]
    return sorted(p for r in roots for p in r.rglob("*.md") if "website/content" not in p.as_posix())


def test_corpus_no_op_replace_is_byte_identical():
    """Replacing every paragraph, heading and item with its own unwrapped text changes no byte, across the repo's own Markdown."""
    files = corpus()
    assert len(files) > 100
    for path in files:
        text = path.read_text(encoding="utf-8")
        front, body = ds.split_front_matter(text)
        lines, blocks = ds.parse(body)
        ops = []
        for n, b in enumerate(blocks):
            if b.kind in ("paragraph", "heading", "item"):
                first = lines[b.start][len(b.prefix):]
                ops.append({"op": "replace", "block": n, "text": " ".join(("\n".join([first] + lines[b.start + 1:b.end])).split())})
        assert ds.apply_text(text, ops) == text, path


def test_corpus_one_word_edit_touches_only_that_block():
    for path in corpus()[:150]:
        text = path.read_text(encoding="utf-8")
        front, body = ds.split_front_matter(text)
        lines, blocks = ds.parse(body)
        for n, b in enumerate(blocks):
            if b.kind == "paragraph" and len(lines[b.start]) > 20:
                first = lines[b.start]
                words = " ".join(("\n".join(lines[b.start:b.end])).split()).split(" ")
                words[0] = words[0] + "X"
                out = ds.apply_text(text, [{"op": "replace", "block": n, "text": " ".join(words)}])
                changed = [i for i, (x, y) in enumerate(zip(text.split("\n"), out.split("\n"))) if x != y]
                assert len(text.split("\n")) == len(out.split("\n"))
                assert changed == [front.count("\n") + b.start], path
                break


def run(*args, cwd=None):
    return subprocess.run([sys.executable, str(REPO / "tools/draftsync/draftsync.py"), *args], capture_output=True, text=True, cwd=cwd)


def git(repo, *args):
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.com", *args], check=True, capture_output=True)


def test_cli_reports_hashes_and_writes(tmp_path):
    f = tmp_path / "d.md"
    f.write_text(DOC)
    e = tmp_path / "e.json"
    e.write_text(json.dumps({"ops": [{"op": "replace", "block": 0, "text": "New title"}]}))
    r = run("apply", str(f), "--edits", str(e), "--no-table-guard")
    assert r.returncode == 0 and "file hash changed" in r.stdout and f.read_text() == DOC
    r = run("apply", str(f), "--edits", str(e), "--no-table-guard", "--write")
    assert r.returncode == 0 and "# New title" in f.read_text()


def test_stale_base_merges_when_clean_and_stops_on_conflict(tmp_path):
    git(tmp_path, "init", "-q")
    f = tmp_path / "d.md"
    f.write_text(DOC)
    git(tmp_path, "add", "d.md")
    git(tmp_path, "commit", "-qm", "base")
    base = subprocess.run(["git", "-C", str(tmp_path), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    f.write_text(DOC.replace("Source two", "Source 2"))          # main moved elsewhere
    e = tmp_path / "e.json"
    e.write_text(json.dumps({"ops": [{"op": "replace", "block": 0, "text": "New title"}]}))
    r = run("apply", str(f), "--edits", str(e), "--base-commit", base, "--no-table-guard", "--write")
    assert r.returncode == 0, r.stderr
    out = f.read_text()
    assert "# New title" in out and "Source 2" in out
    f.write_text(DOC.replace("# Title", "# Other"))              # main moved the same line
    r = run("apply", str(f), "--edits", str(e), "--base-commit", base, "--no-table-guard", "--write")
    assert r.returncode == 1 and "conflict" in r.stderr and "# Other" in f.read_text()


@pytest.fixture
def assessment(tmp_path):
    shutil.copy(REPO / "workflows/activities/00-discover/artifacts/criteria.yml", tmp_path)
    f = tmp_path / "TA.md"
    shutil.copy(REPO / "workflows/activities/00-discover/artifacts/technology-assessment/example.md", f)
    return f


def test_generated_table_edit_is_refused_and_prose_edit_is_not(assessment):
    lines, blocks = ds.parse(ds.split_front_matter(assessment.read_text())[1])
    rows = [n for n, b in enumerate(blocks) if b.kind == "row" and "Script distribution" in lines[b.start]]
    assert rows
    e = assessment.parent / "e.json"
    e.write_text(json.dumps({"ops": [{"op": "replace", "block": rows[0], "cell": 1, "text": "Fine"}]}))
    r = run("apply", str(assessment), "--edits", str(e))
    assert r.returncode == 1 and "generated table" in r.stderr
    para = next(n for n, b in enumerate(blocks) if b.kind == "paragraph")
    first = " ".join("\n".join(lines[blocks[para].start:blocks[para].end]).split())
    e.write_text(json.dumps({"ops": [{"op": "replace", "block": para, "text": first + " Reviewed."}]}))
    r = run("apply", str(assessment), "--edits", str(e))
    assert r.returncode == 0, r.stderr


# ---- the Claude Docs changed-blocks translator, on reads recorded from a live doc ----------------------

FIX = Path(__file__).resolve().parent / "fixtures"


def fixture_ops():
    return ds.edits_from_read((FIX / "old.xml").read_text(), (FIX / "delta.xml").read_text(),
                              (FIX / "pp-with-notes.md").read_text())


def test_translates_a_recorded_read_into_ops():
    ops = fixture_ops()
    assert {"op": "replace", "block": 11, "cell": 1, "text": "Familiarity favours Node.js for that team; the thesis assumes the repository's existing runtime is Python"} in ops
    assert {"op": "delete", "block": 12} in ops
    assert {"op": "insert", "after": 20, "kind": "row", "cells": ["TA-002", "Technology assessment", "draft", "Objections"]} in ops
    assert {"op": "insert", "after": 16, "kind": "paragraph", "text": "A new paragraph about **scope** and `code` between the sections."} in ops
    assert {"op": "replace", "block": 25, "text": "Nested item b (edited)"} in ops
    notes = next(o for o in ops if o.get("block") == 22)
    assert notes["text"] == "Configure `app.yaml` and see [the guide](https://example.com/guide) and [[tech-spike]] for pg_cron configuration."


def test_recorded_read_lands_with_only_the_edits_in_the_diff():
    text = (FIX / "pp-with-notes.md").read_text()
    ops = [o for o in fixture_ops() if not (o["op"] == "replace" and o.get("block") == 15)]   # a generated table
    out = ds.apply_text(text, ops)
    before, after = text.split("\n"), out.split("\n")
    assert "a repository adds installation and maintenance for every contributor." in out
    assert "| TA-002 | Technology assessment | draft | Objections |" in out
    assert "Distribution of a single script" not in out
    untouched = [l for l in before if l in after]
    assert len(untouched) > len(before) - 12
    assert "|-----------|--------|----------|" in out and "Argument step 1 |" in out


def test_doc_and_file_that_do_not_line_up_are_refused():
    text = (FIX / "pp-with-notes.md").read_text().replace("\n## Notes\n", "\n## Notes\n\nExtra paragraph.\n")
    with pytest.raises(ds.Refused, match="do not line up"):
        ds.edits_from_read((FIX / "old.xml").read_text(), (FIX / "delta.xml").read_text(), text)


def test_a_whole_doc_read_is_refused():
    with pytest.raises(ds.Refused, match="whole doc"):
        ds.edits_from_read((FIX / "old.xml").read_text(),
                           "<doc node='n' rev='3' since='unavailable'></doc>", (FIX / "pp-with-notes.md").read_text())


def test_new_blocks_that_cannot_be_written_as_markdown_are_refused():
    old = (FIX / "old.xml").read_text()
    text = (FIX / "pp-with-notes.md").read_text()
    table = "<doc rev='3' sinceRev='1'><gap blocks='3'/><table id='m9gc498ep5e.9999'><row id='.9998'><cell id='.9997'><paragraph id='.9996'><text id='.9995'>x</text></paragraph></cell></row></table></doc>"
    with pytest.raises(ds.Refused, match="new <table>"):
        ds.edits_from_read(old, table, text)
    mention = "<doc rev='3' sinceRev='1'><gap blocks='4'/><paragraph id='m9gc498ep5e.259'><text id='.1'>a</text><mention id='.2' user='u'/></paragraph></doc>"
    with pytest.raises(ds.Refused, match="mention"):
        ds.edits_from_read(old, mention, text)


def test_two_inserts_at_one_spot_keep_their_order_and_headings_and_items_insert():
    out = ds.apply_text(DOC, [{"op": "insert", "after": 1, "kind": "paragraph", "text": "First."},
                              {"op": "insert", "after": 1, "kind": "heading", "level": 2, "text": "Second"},
                              {"op": "insert", "after": 6, "kind": "item", "like": 5, "text": "inserted item"}])
    assert "pg_cron.\n\nFirst.\n\n## Second\n\n| a | b |" in out
    assert "- second item\n- inserted item\n" in out


def test_cli_edits_prints_json(tmp_path):
    f = tmp_path / "pp.md"
    f.write_text((FIX / "pp-with-notes.md").read_text())
    r = run("edits", str(f), "--old", str(FIX / "old.xml"), "--delta", str(FIX / "delta.xml"))
    assert r.returncode == 0 and json.loads(r.stdout)["ops"]


def test_a_live_edit_to_a_generated_table_is_refused_end_to_end(tmp_path):
    f = tmp_path / "PP.md"
    f.write_text((FIX / "pp-with-notes.md").read_text())
    shutil.copy(REPO / "workflows/activities/00-discover/artifacts/criteria.yml", tmp_path)
    e = tmp_path / "e.json"
    e.write_text(json.dumps({"ops": fixture_ops()}))
    r = run("apply", str(f), "--edits", str(e))
    assert r.returncode == 1 and "generated table" in r.stderr
    e.write_text(json.dumps({"ops": [o for o in fixture_ops() if o.get("block") != 15]}))
    r = run("apply", str(f), "--edits", str(e))
    assert r.returncode == 0, r.stderr
