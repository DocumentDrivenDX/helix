"""Tests for draftsync: parsing, word-level patching, three-way landing, and the generated-table guard."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SRC = str(Path(__file__).resolve().parents[1] / "src")
sys.path.insert(0, SRC)
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
    return subprocess.run([sys.executable, "-m", "draftsync", *args], capture_output=True, text=True, cwd=cwd, env={**os.environ, "PYTHONPATH": SRC})


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
    assert notes["text"] == "Configure `app.yaml` and see [the guide](https://example.com/guide) and [[tech-spike]] for pg\\_cron configuration."


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


# ---- regressions from the independent review ---------------------------------------------------------------

def ap(text, *ops):
    return ds.apply_text(text, list(ops))


def test_a_word_added_at_the_start_keeps_its_space():
    assert ds.patch_words("text here", "New text here") == "New text here"
    assert ap("- item text\n", {"op": "replace", "block": 0, "text": "New item text"}) == "- New item text\n"
    assert ap("## Title here\n", {"op": "replace", "block": 0, "text": "The Title here"}) == "## The Title here\n"
    assert ds.patch_words("   indented para text", "indented para text now") == "   indented para text now"


def test_guard_fails_closed_when_the_table_check_cannot_run(tmp_path, monkeypatch):
    f = tmp_path / "PP.md"
    f.write_text((FIX / "pp-with-notes.md").read_text())
    script = tmp_path / "broken.py"
    script.write_text("import sys\nsys.stderr.write('PyYAML is required')\nsys.exit(2)\n")
    with pytest.raises(ds.Refused, match="could not run"):
        ds.tables_ok(script, f, f.read_text())


def test_row_inserted_after_the_header_lands_after_the_separator():
    t = "| H1 | H2 |\n|----|----|\n| a | b |\n"
    assert ap(t, {"op": "insert", "after": 0, "kind": "row", "cells": ["x", "y"]}) == "| H1 | H2 |\n|----|----|\n| x | y |\n| a | b |\n"


def test_pipes_are_escaped_and_escapes_survive_edits():
    t = "| a \\| b c | z |\n"
    assert ap(t, {"op": "replace", "block": 0, "cell": 0, "text": "a | b d"}) == "| a \\| b d | z |\n"
    assert ap("| a | b |\n", {"op": "insert", "after": 0, "kind": "row", "cells": ["x|y", "z"]}) == "| a | b |\n| x\\|y | z |\n"
    para = "Use \\*args and 2 \\* 3 here.\n"
    assert ap(para, {"op": "replace", "block": 0, "text": "Use *args and 2 * 3 there."}) == "Use \\*args and 2 \\* 3 there.\n"
    with pytest.raises(ds.Refused):
        ap("plain\n", {"op": "replace", "block": 0, "text": "# now heading"})
    with pytest.raises(ds.Refused):
        ap("plain\n", {"op": "insert", "after": 0, "kind": "paragraph", "text": "- a list now"})


def test_deleting_a_table_takes_its_separator_and_a_lone_header_is_refused():
    t = "intro\n\n| H1 | H2 |\n|----|----|\n| a | b |\n"
    out = ap(t, {"op": "delete", "block": 1}, {"op": "delete", "block": 2})
    assert "|" not in out
    with pytest.raises(ds.Refused, match="header row"):
        ap(t, {"op": "delete", "block": 1})


def test_a_short_id_with_no_full_id_before_it_is_refused():
    old = (FIX / "old.xml").read_text()
    with pytest.raises(ds.Refused, match="short"):
        ds.edits_from_read(old, "<doc rev='3' sinceRev='1'><gap blocks='1'/><paragraph id='.1'>x</paragraph></doc>",
                           (FIX / "pp-with-notes.md").read_text())


def test_an_inserted_paragraph_is_followed_by_a_blank_line():
    assert ap("## H\ntext here\n", {"op": "insert", "after": 0, "kind": "paragraph", "text": "NEW"}) == "## H\n\nNEW\n\ntext here\n"
    assert ap("Intro:\n- a\n", {"op": "insert", "after": 0, "kind": "paragraph", "text": "NEW"}) == "Intro:\n\nNEW\n\n- a\n"


def test_two_cells_of_one_row_can_be_edited():
    t = "| a b | c d |\n"
    out = ap(t, {"op": "replace", "block": 0, "cell": 0, "text": "a x"}, {"op": "replace", "block": 0, "cell": 1, "text": "c y"})
    assert out == "| a x | c y |\n"
    with pytest.raises(ds.Refused):
        ap(t, {"op": "replace", "block": 0, "cell": 0, "text": "a x"}, {"op": "replace", "block": 0, "cell": 0, "text": "a z"})


def test_bad_input_is_a_refusal_or_error_not_a_traceback(tmp_path):
    f = tmp_path / "d.md"
    f.write_text(DOC)
    for payload in ('[1]', '{"ops": [{"op": "replace", "block": 1, "text": 5}]}', '{"ops": [{"op": "insert", "after": 1, "kind": "row", "cells": null}]}',
                    '{"ops": [{"op": "delete", "block": true}]}'):
        e = tmp_path / "e.json"
        e.write_text(payload)
        r = run("apply", str(f), "--edits", str(e), "--no-table-guard")
        assert r.returncode in (1, 2) and "Traceback" not in r.stderr, (payload, r.stderr)
    r = run("apply", str(tmp_path / "missing.md"), "--edits", str(e))
    assert r.returncode == 2 and "Traceback" not in r.stderr
    old = tmp_path / "o.xml"
    old.write_text("<doc")
    r = run("edits", str(f), "--old", str(old), "--delta", str(old))
    assert r.returncode == 2 and "Traceback" not in r.stderr


def test_translator_refuses_a_deleted_cell_a_big_gap_and_a_moved_block():
    old, text = (FIX / "old.xml").read_text(), (FIX / "pp-with-notes.md").read_text()
    with pytest.raises(ds.Refused):
        ds.edits_from_read(old, "<doc rev='3' sinceRev='1'><gap blocks='9'/><gone id='m9gc498ep5e.722'/></doc>", text)
    with pytest.raises(ds.Refused):
        ds.edits_from_read(old, "<doc rev='3' sinceRev='1'><gap blocks='99'/><paragraph id='m9gc498ep5e.9999'>x</paragraph></doc>", text)
    with pytest.raises(ds.Refused, match="not where"):
        ds.edits_from_read(old, "<doc rev='3' sinceRev='1'><gap blocks='2'/><paragraph id='m9gc498ep5e.259'><text id='.1'>x</text></paragraph></doc>", text)


def test_crlf_is_refused_and_empty_front_matter_is_recognised(tmp_path):
    f = tmp_path / "d.md"
    f.write_bytes(b"---\r\nddx:\r\n---\r\ntext here\r\n")
    r = run("apply", str(f), "--edits", str(f), "--no-table-guard")
    assert r.returncode == 1 and "CRLF" in r.stderr
    front, body = ds.split_front_matter("---\n---\nbody\n\n---\n\nmore\n")
    assert front == "---\n---\n" and body.startswith("body")


def test_a_hash_report_matches_the_bytes_on_disk(tmp_path):
    f = tmp_path / "d.md"
    f.write_text(DOC)
    e = tmp_path / "e.json"
    e.write_text(json.dumps({"ops": [{"op": "replace", "block": 0, "text": "New title"}]}))
    import hashlib
    r = run("apply", str(f), "--edits", str(e), "--no-table-guard")
    assert hashlib.sha256(f.read_bytes()).hexdigest() in r.stdout


def test_heading_level_change_and_a_stale_draft_are_refused():
    old, text = (FIX / "old.xml").read_text(), (FIX / "pp-with-notes.md").read_text()
    with pytest.raises(ds.Refused, match="heading level"):
        ds.edits_from_read(old, "<doc rev='3' sinceRev='1'><gap blocks='1'/><paragraph id='m9gc498ep5e.56' heading='3'><text id='.57'>Thesis</text></paragraph></doc>", text)
    stale = text.replace("Maintainers choosing", "Reviewers choosing")
    with pytest.raises(ds.Refused, match="different text"):
        ds.edits_from_read(old, (FIX / "delta.xml").read_text(), stale)


def test_numbered_inserts_count_up_and_deleted_neighbours_block_them():
    t = "1. one\n2. two\n"
    out = ap(t, {"op": "insert", "after": 1, "kind": "item", "like": 1, "text": "three"}, {"op": "insert", "after": 1, "kind": "item", "like": 1, "text": "four"})
    assert out == "1. one\n2. two\n3. three\n4. four\n"
    with pytest.raises(ds.Refused):
        ap(t, {"op": "delete", "block": 1}, {"op": "insert", "after": 1, "kind": "item", "like": 1, "text": "deux"})
    assert ap(t, {"op": "delete", "block": 0}, {"op": "delete", "block": 1}).strip() == ""


def test_small_things_row_pipes_checkboxes_bold_runs_and_ordering():
    assert ap("| a | b\n", {"op": "replace", "block": 0, "cell": 0, "text": "z"}) == "| z | b\n"
    assert ap("- [ ] do thing\n", {"op": "replace", "block": 0, "text": "do the thing"}) == "- [ ] do the thing\n"
    import xml.etree.ElementTree as ET
    p = ET.fromstring("<paragraph><text><bold>Intro </bold></text><text>para</text><text><bold>graph.</bold></text></paragraph>")
    assert ds.runs_to_markdown(p) == "**Intro** para**graph.**"
    t = "a\n\nb\n"
    out = ap(t, {"op": "insert", "after": 0, "kind": "paragraph", "text": "X"}, {"op": "replace", "block": 1, "text": "bee"},
             {"op": "insert", "after": 0, "kind": "paragraph", "text": "Y"})
    assert out.index("X") < out.index("Y") < out.index("bee")
    with pytest.raises(ds.Refused):
        ap(t, {"op": "delete", "block": True})


# ---- regressions from the second review -------------------------------------------------------------------

def test_adjacent_tables_are_separate_for_deletes():
    t = "| a |\n|---|\n| 1 |\n\n| b |\n|---|\n| 2 |\n\nend\n"
    out = ap(t, {"op": "delete", "block": 2}, {"op": "delete", "block": 3})
    assert "| b |" not in out and out.count("|---|") == 1
    with pytest.raises(ds.Refused, match="header row"):
        ap(t, {"op": "delete", "block": 2})
    assert "| a |" not in ap(t, {"op": "delete", "block": 0}, {"op": "delete", "block": 1})


def test_attribute_changes_and_empty_blocks_are_refused_not_dropped():
    old, text = (FIX / "old.xml").read_text(), (FIX / "pp-with-notes.md").read_text()
    with pytest.raises(ds.Refused, match="kind"):
        ds.edits_from_read(old, "<doc rev='3' sinceRev='1'><gap blocks='6'/><list id='m9gc498ep5e.410' kind='bullet'><gap blocks='3'/></list></doc>", text)
    with pytest.raises(ds.Refused, match="empty"):
        ds.edits_from_read(old, "<doc rev='3' sinceRev='1'><gap blocks='4'/><paragraph id='m9gc498ep5e.259'></paragraph></doc>", text)
    with pytest.raises(ds.Refused, match="same doc"):
        ds.edits_from_read(old, "<doc node='other' rev='3' sinceRev='1'></doc>", text)
    with pytest.raises(ds.Refused, match="negative"):
        ds.edits_from_read(old, "<doc rev='3' sinceRev='1'><gap blocks='-1'/></doc>", text)


def test_equivalent_spellings_of_untouched_words_stay_as_written():
    assert ds.patch_words("an _old_ word here", "an *old* word there") == "an _old_ word there"
    assert ds.patch_words("see <http://x.y> now", "see [http://x.y](http://x.y) later") == "see <http://x.y> later"
    assert ds.patch_words("foo\\\nbar baz", "foo bar bazz") == "foo\\\nbar bazz"


def test_literal_markdown_in_the_doc_is_escaped_and_code_is_not():
    import xml.etree.ElementTree as ET
    p = ET.fromstring("<paragraph><text>A *lit* _x_ &lt;b&gt; pg_cron </text><text><code>a_b</code></text></paragraph>")
    assert ds.runs_to_markdown(p) == "A \\*lit\\* \\_x\\_ \\<b> pg\\_cron `a_b`"


def test_row_inserts_are_checked_and_new_tasks_start_unchecked():
    with pytest.raises(ds.Refused):
        ap("| a | b |\n", {"op": "insert", "after": 0, "kind": "row", "cells": ["x\ny", "z"]})
    with pytest.raises(ds.Refused, match="2 cells"):
        ap("| a | b |\n", {"op": "insert", "after": 0, "kind": "row", "cells": ["x"]})
    assert ap("- [ ] a\n- [x] b\n", {"op": "insert", "after": 1, "kind": "item", "like": 1, "text": "new"}) == "- [ ] a\n- [x] b\n- [ ] new\n"


def test_empty_text_and_block_lookalikes_are_refused():
    for op in ({"op": "replace", "block": 0, "text": "  "}, {"op": "replace", "block": 0, "text": "---"},
               {"op": "insert", "after": 0, "kind": "heading", "level": 0, "text": "x"},
               {"op": "insert", "after": 0, "kind": "paragraph", "text": ""}):
        with pytest.raises(ds.Refused):
            ap("plain\n", op)
    with pytest.raises(ds.Refused):
        ap("- a\n", {"op": "replace", "block": 0, "text": "- nested"})
    with pytest.raises(ds.Refused, match="not a table row"):
        ap("plain\n", {"op": "replace", "block": 0, "cell": 1, "text": "x"})


def test_deleting_the_last_paragraph_keeps_the_trailing_newline_and_eof_front_matter_is_found():
    assert ap("# H\nB\n", {"op": "delete", "block": 1}) == "# H\n"
    assert ds.split_front_matter("---\na: 1\n---") == ("---\na: 1\n---", "")


def test_a_cell_with_only_spaces_gets_normal_padding():
    assert ap("|   | b |\n", {"op": "replace", "block": 0, "cell": 0, "text": "x"}) == "| x | b |\n"


def test_base_commit_cannot_be_an_option(tmp_path):
    f = tmp_path / "d.md"
    f.write_text(DOC)
    e = tmp_path / "e.json"
    e.write_text('{"ops": []}')
    r = run("apply", str(f), "--edits", str(e), "--base-commit=--output=zz", "--no-table-guard")
    assert r.returncode == 1 and "not an option" in r.stderr and not list(tmp_path.glob("zz*"))


# ---- a read recorded after edits in the Docs UI by three editors, two of them at the same time -----------

def test_ui_edits_by_several_editors_translate_and_land():
    text = (FIX / "pp-with-notes.md").read_text()
    ops = ds.edits_from_read((FIX / "ui-old.xml").read_text(), (FIX / "ui-delta.xml").read_text(), text)
    assert {"op": "delete", "block": 12} in ops
    assert {"op": "insert", "after": 26, "kind": "item", "like": 26, "indent": 4, "text": "A new subitem."} in ops
    assert any(o.get("text", "").startswith("Maintainers choosing a runtime for a new tooling script. A THIRD runtime") for o in ops)
    out = ds.apply_text(text, ops)
    assert "A THIRD runtime in\na repository adds installation and upkeep for every contributors." in out
    assert "- Outer item two\n    - A new subitem.\n    - New Bullet\n" in out
    assert "Distribution of a single script" not in out
    assert out.count("\n") == text.count("\n") - 1 + 2          # one row gone, two items added


def test_blocks_born_and_deleted_after_the_draft_opened_are_ignored():
    old, text = (FIX / "old.xml").read_text(), (FIX / "pp-with-notes.md").read_text()
    delta = "<doc rev='9' sinceRev='1'><gap blocks='9'/><gone id='zz.1' rev='3'/><gone id='.2' rev='4' was='x'/></doc>"
    assert ds.edits_from_read(old, delta, text) == []


# ---- the word-level three-way merge ------------------------------------------------------------------------

def test_merge3_applies_both_sides_changes_on_different_words_of_one_line():
    base = "the quick brown fox\njumps over the lazy dog\n"
    ours = "the quick red fox\njumps over the lazy dog\n"          # git changed brown
    theirs = "the quick brown fox\njumps over the sleepy dog\n"    # the draft changed lazy
    out, lost = ds.merge3(base, ours, theirs)
    assert out == "the quick red fox\njumps over the sleepy dog\n" and lost == []


def test_merge3_identical_changes_are_not_a_conflict_and_keep_wrapping():
    base = "a b c\nd e f\n"
    both = "a b X\nd e f\n"
    assert ds.merge3(base, both, both) == (both, [])
    out, _ = ds.merge3(base, both, "a b c\nd e f\n")
    assert out == both


def test_merge3_conflict_stops_or_follows_the_record():
    base = "one two three\n"
    ours = "one 2 three\n"
    theirs = "one deux three\n"
    with pytest.raises(ds.Conflict) as err:
        ds.merge3(base, ours, theirs)
    assert err.value.conflicts[0]["ours"] == "2" and err.value.conflicts[0]["theirs"] == "deux"
    out, lost = ds.merge3(base, ours, theirs, prefer="ours")
    assert out == "one 2 three\n" and lost[0]["kept"] == "ours"
    out, lost = ds.merge3(base, ours, theirs, prefer="theirs")
    assert out == "one deux three\n"


def test_merge3_adjacent_edits_merge_and_two_insertions_at_one_spot_conflict():
    base = "a b c d\n"
    assert ds.merge3(base, "a B c d\n", "a b C d\n")[0] == "a B C d\n"
    with pytest.raises(ds.Conflict):
        ds.merge3(base, "a b X c d\n", "a b Y c d\n")
    assert ds.merge3(base, "a b X c d\n", "a b X c d\n")[0] == "a b X c d\n"


def test_merge3_a_deletion_against_an_edit_in_it_is_a_conflict():
    base = "keep\n| a | b |\n| c | d |\nend\n"
    ours = "keep\n| a | b |\nend\n"                      # git deleted the last row
    theirs = "keep\n| a | b |\n| c | D |\nend\n"           # the draft edited it
    with pytest.raises(ds.Conflict):
        ds.merge3(base, ours, theirs)
    assert ds.merge3(base, ours, theirs, prefer="ours")[0] == ours


def test_apply_with_a_moved_base_merges_by_word_and_honours_prefer(tmp_path):
    git(tmp_path, "init", "-q")
    f = tmp_path / "d.md"
    f.write_text("# Title\n\nalpha beta gamma delta\nepsilon zeta\n")
    git(tmp_path, "add", "d.md")
    git(tmp_path, "commit", "-qm", "base")
    base = subprocess.run(["git", "-C", str(tmp_path), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    f.write_text("# Title\n\nalpha BETA gamma delta\nepsilon zeta\n")             # git moved: one word
    e = tmp_path / "e.json"
    e.write_text(json.dumps({"ops": [{"op": "replace", "block": 1, "text": "alpha beta gamma delta epsilon ZETA"}]}))   # draft: another word
    r = run("apply", str(f), "--edits", str(e), "--base-commit", base, "--no-table-guard", "--write")
    assert r.returncode == 0, r.stderr
    assert "alpha BETA gamma delta\nepsilon ZETA" in f.read_text()
    f.write_text("# Title\n\nalpha beta gamma delta\nepsilon zeta\n")
    e.write_text(json.dumps({"ops": [{"op": "replace", "block": 1, "text": "alpha beta gamma delta epsilon ZETA"}, {"op": "replace", "block": 0, "text": "Draft title"}]}))
    f.write_text("# Git title\n\nalpha beta gamma delta\nepsilon zeta\n")
    r = run("apply", str(f), "--edits", str(e), "--base-commit", base, "--no-table-guard", "--write")
    assert r.returncode == 1 and "--prefer" in r.stderr
    r = run("apply", str(f), "--edits", str(e), "--base-commit", base, "--no-table-guard", "--write", "--prefer", "git")
    assert r.returncode == 0 and "# Git title" in f.read_text() and "ZETA" in f.read_text() and "conflict resolved for git" in r.stderr


# ---- the binding: sidecar, attribute, status, hook, base from history ------------------------------------

def bound_repo(tmp_path, front="---\nddx:\n  id: X-1\n---\n"):
    git(tmp_path, "init", "-q")
    f = tmp_path / "d.md"
    f.write_text(front + "# Title\n\nalpha beta gamma delta\nepsilon zeta\n")
    git(tmp_path, "add", "d.md")
    git(tmp_path, "commit", "-qm", "base")
    r = run("bind", str(f), "--tool", "claude-docs", "--origin", "https://example.com/doc", "--synced-rev", "7")
    assert r.returncode == 0, r.stderr
    return f


def test_bind_writes_the_sidecar_and_the_attribute_and_status_reads_them(tmp_path):
    f = bound_repo(tmp_path)
    assert "d.md claude-docs-bind" in (tmp_path / ".gitattributes").read_text()
    assert "synced_rev: '7'" in (tmp_path / ".helix-bindings.yml").read_text()
    st = json.loads(run("status", str(f)).stdout)
    assert st["bound"] and st["tool"] == "claude-docs" and st["record"] == "git" and st["file_changed_since_base"] is False
    f.write_text(f.read_text().replace("beta", "BETA"))
    assert json.loads(run("status", str(f)).stdout)["file_changed_since_base"] is True
    other = tmp_path / "o.md"
    other.write_text("x\n")
    assert json.loads(run("status", str(other)).stdout)["bound"] is False


def test_front_matter_edits_do_not_count_as_changes_since_the_base(tmp_path):
    f = bound_repo(tmp_path)
    f.write_text(f.read_text().replace("id: X-1", "id: X-1\n  tags: [a]"))
    assert json.loads(run("status", str(f)).stdout)["file_changed_since_base"] is False


def test_the_record_follows_authoring_home(tmp_path):
    f = bound_repo(tmp_path, "---\nddx:\n  id: X-1\n  authoring:\n    home: external-tool\n---\n")
    assert json.loads(run("status", str(f)).stdout)["record"] == "doc"


def hook_run(tmp_path, f, payload=None):
    data = payload or {"tool_name": "Edit", "tool_input": {"file_path": str(f)}, "cwd": str(tmp_path)}
    return subprocess.run([sys.executable, "-m", "draftsync", "hook"], input=json.dumps(data),
                          capture_output=True, text=True, cwd=tmp_path, env={**os.environ, "PYTHONPATH": SRC})


def test_hook_is_silent_for_unbound_or_unchanged_files_and_tells_the_agent_otherwise(tmp_path):
    f = bound_repo(tmp_path)
    assert hook_run(tmp_path, f).stdout == ""                       # bound, unchanged
    other = tmp_path / "o.md"
    other.write_text("x\n")
    assert hook_run(tmp_path, other).stdout == ""                   # unbound
    assert hook_run(tmp_path, f, {"tool_input": {}}).stdout == ""   # not a file edit
    assert hook_run(tmp_path, f, {"tool_input": {"file_path": "missing.md"}, "cwd": str(tmp_path)}).returncode == 0
    f.write_text(f.read_text().replace("beta", "BETA"))
    r = hook_run(tmp_path, f)
    out = json.loads(r.stdout)["hookSpecificOutput"]
    assert r.returncode == 0 and out["hookEventName"] == "PostToolUse"
    assert "git is its system of record" in out["additionalContext"]
    assert list((tmp_path / ".git/draftsync-pending").glob("*.json"))


def test_hook_warns_that_the_draft_wins_when_it_is_the_record(tmp_path):
    f = bound_repo(tmp_path, "---\nddx:\n  id: X-1\n  authoring:\n    home: external-tool\n---\n")
    f.write_text(f.read_text().replace("beta", "BETA"))
    assert "draft is its system of record" in json.loads(hook_run(tmp_path, f).stdout)["hookSpecificOutput"]["additionalContext"]


def test_hook_never_fails_on_garbage(tmp_path):
    r = subprocess.run([sys.executable, "-m", "draftsync", "hook"], input="not json", capture_output=True, text=True, cwd=tmp_path, env={**os.environ, "PYTHONPATH": SRC})
    assert r.returncode == 0 and r.stdout == ""


def test_apply_from_binding_finds_the_base_in_history_and_follows_the_record(tmp_path):
    f = bound_repo(tmp_path)
    text = f.read_text()
    f.write_text(text.replace("alpha beta", "alpha BETA"))                     # git moves on, committed
    git(tmp_path, "commit", "-qam", "git change")
    e = tmp_path / "e.json"
    e.write_text(json.dumps({"ops": [{"op": "replace", "block": 1, "text": "alpha beta gamma delta epsilon ZETA"}]}))
    r = run("apply", str(f), "--edits", str(e), "--from-binding", "--no-table-guard", "--write")
    assert r.returncode == 0, r.stderr
    assert "alpha BETA gamma delta\nepsilon ZETA" in f.read_text()
    f.write_text(f.read_text().replace("# Title", "# Git title"))
    e.write_text(json.dumps({"ops": [{"op": "replace", "block": 0, "text": "Draft title"}]}))
    r = run("apply", str(f), "--edits", str(e), "--from-binding", "--no-table-guard", "--write")
    assert r.returncode == 0 and "# Git title" in f.read_text() and "conflict resolved for git" in r.stderr


def test_apply_from_binding_lets_the_draft_win_when_it_is_the_record(tmp_path):
    f = bound_repo(tmp_path, "---\nddx:\n  id: X-1\n  authoring:\n    home: external-tool\n---\n")
    f.write_text(f.read_text().replace("# Title", "# Git title"))
    e = tmp_path / "e.json"
    e.write_text(json.dumps({"ops": [{"op": "replace", "block": 0, "text": "Draft title"}]}))
    r = run("apply", str(f), "--edits", str(e), "--from-binding", "--no-table-guard", "--write")
    assert r.returncode == 0 and "# Draft title" in f.read_text() and "conflict resolved for doc" in r.stderr


def test_a_missing_base_or_binding_is_a_refusal(tmp_path):
    f = bound_repo(tmp_path)
    side = tmp_path / ".helix-bindings.yml"
    side.write_text(side.read_text().replace(side.read_text().split("base_sha256: ")[1].split("\n")[0], "'" + "0" * 64 + "'"))
    e = tmp_path / "e.json"
    e.write_text('{"ops": []}')
    r = run("apply", str(f), "--edits", str(e), "--from-binding", "--no-table-guard")
    assert r.returncode == 1 and "rebind" in r.stderr
    side.unlink()
    r = run("apply", str(f), "--edits", str(e), "--from-binding", "--no-table-guard")
    assert r.returncode == 1 and "no entry" in r.stderr


def test_rebind_needs_the_draft_to_equal_a_committed_file(tmp_path):
    f = bound_repo(tmp_path)
    old = tmp_path / "old.xml"
    old.write_text("<doc node='n' rev='9'><paragraph id='s.0' heading='1'><text id='.1'>Title</text></paragraph>"
                   "<paragraph id='.2'><text id='.3'>alpha beta gamma delta epsilon zeta</text></paragraph></doc>")
    f.write_text(f.read_text().replace("beta", "BETA"))
    r = run("rebind", str(f), "--synced-rev", "9", "--old", str(old))
    assert r.returncode == 1 and "commit it first" in r.stderr
    git(tmp_path, "commit", "-qam", "git change")
    r = run("rebind", str(f), "--synced-rev", "9", "--old", str(old))
    assert r.returncode == 1 and "different text" in r.stderr
    f.write_text(f.read_text().replace("BETA", "beta"))
    git(tmp_path, "commit", "-qam", "back")
    r = run("rebind", str(f), "--synced-rev", "5", "--old", str(old))
    assert r.returncode == 1 and "not the revision" in r.stderr
    r = run("rebind", str(f), "--synced-rev", "9", "--old", str(old))
    assert r.returncode == 0, r.stderr
    assert json.loads(run("status", str(f)).stdout)["synced_rev"] == "9"



# ---- git -> draft: doc ops ---------------------------------------------------------------------------------

def writer(file_text, now_xml=None, record="git"):
    base = (FIX / "pp-with-notes.md").read_text()
    return ds.doc_ops(base, file_text, (FIX / "old.xml").read_text(), now_xml or (FIX / "old.xml").read_text(), record)


def test_writer_carries_a_git_word_change_into_an_untouched_draft():
    text = (FIX / "pp-with-notes.md").read_text().replace("hard to say", "hard to say")
    text = text.replace("less to install", "far less to install")
    out = writer(text)
    assert out["report"] == []
    assert len(out["ops"]) == 1
    op = out["ops"][0]
    assert op["op"] == "replace" and op["with"]["as"] == "text"
    assert op["with"]["from"]["content"] == op["target"]["text"].replace("has less", "has far less")


def test_writer_merges_with_the_drafts_own_edit_in_the_same_paragraph_and_reports_conflicts():
    now = (FIX / "old.xml").read_text().replace("adds installation and upkeep for every contributor", "adds installation and maintenance for every contributor")
    text = (FIX / "pp-with-notes.md").read_text().replace("A second runtime", "A third runtime")
    out = writer(text, now)
    assert out["report"] == [] and len(out["ops"]) == 1
    assert "second" in out["ops"][0]["target"]["text"] and "third" in out["ops"][0]["with"]["from"]["content"]
    clash = (FIX / "pp-with-notes.md").read_text().replace("upkeep", "care")
    out = writer(clash, now, record="git")
    assert any("conflict" in r and "resolved for git" in r for r in out["report"])
    assert out["ops"] and "care" in out["ops"][0]["with"]["from"]["content"]
    out = writer(clash, now, record="doc")
    assert any("resolved for doc" in r for r in out["report"]) and out["ops"] == []


def test_writer_deletes_blocks_the_file_deleted_and_inserts_new_ones_after_their_neighbour():
    base = (FIX / "pp-with-notes.md").read_text()
    text = base.replace("| Distribution of a single script may differ | The assessment has no finding on distribution; the thesis does not rely on it | TA-001, Contradictions and Gaps |\n", "")
    text = text.replace("## Limits of the Position\n", "## Limits of the Position\n\nA new paragraph from git.\n")
    out = writer(text)
    kinds = [o["op"] for o in out["ops"]]
    assert kinds.count("delete") == 1 and kinds.count("insert") == 1
    d = next(o for o in out["ops"] if o["op"] == "delete")
    assert d["target"]["ids"] == ["m9gc498ep5e.913"] and d["ifHash"] == "d9e9ecc8"
    ins = next(o for o in out["ops"] if o["op"] == "insert")
    assert ins["target"]["ids"] == ["m9gc498ep5e.1288"] and ins["source"]["from"]["content"] == "A new paragraph from git."


def test_writer_edits_a_cell_with_a_within_target_and_leaves_markup_changes_to_a_person():
    base = (FIX / "pp-with-notes.md").read_text()
    out = writer(base.replace("Familiarity favors", "Familiarity favours"))
    t = out["ops"][0]["target"]
    assert t["within"] == {"kind": "cell", "table": "m9gc498ep5e.720", "row": 1, "col": 1} and "favors" in t["text"]
    out = writer(base.replace("upkeep", "**upkeep**"))
    assert out["ops"] == [] and any("formatting" in r for r in out["report"])


def test_writer_has_nothing_to_do_when_the_file_has_not_changed_and_cli_runs(tmp_path):
    base = (FIX / "pp-with-notes.md").read_text()
    assert writer(base) == {"ops": [], "report": []}
    f = tmp_path / "PP.md"
    f.write_text(base.replace("less to install", "far less to install"))
    git(tmp_path, "init", "-q")
    r = run("doc-ops", str(f), "--old", str(FIX / "old.xml"), "--now", str(FIX / "old.xml"), "--base-commit=--x")
    assert r.returncode == 1 and "not an option" in r.stderr


def test_writer_on_reads_recorded_from_a_live_draft_with_merged_and_conflicting_edits():
    """The draft had two edits of its own; git changed the same paragraph, one of the same words, a row and a heading's neighbour."""
    base = (FIX / "pp-with-notes.md").read_text()
    text = (base.replace("A second runtime", "A third runtime").replace("Familiarity favors", "Familiarity prefers")
            .replace("has less to install", "has far less to install")
            .replace("| Distribution of a single script may differ | The assessment has no finding on distribution; the thesis does not rely on it | TA-001, Contradictions and Gaps |\n", "")
            .replace("## Limits of the Position\n", "## Limits of the Position\n\nA new paragraph from git.\n"))
    out = ds.doc_ops(base, text, (FIX / "wr-old.xml").read_text(), (FIX / "wr-now.xml").read_text(), "git")
    summary = [(o["op"], o["target"].get("text") or o["target"]["ids"][0]) for o in out["ops"]]
    assert summary == [("replace", "favours"), ("replace", "runtime has less"), ("replace", "second"),
                       ("delete", "mmgx2r82dhj.913"), ("insert", "mmgx2r82dhj.1288")]
    assert out["ops"][0]["target"]["within"] == {"kind": "cell", "table": "mmgx2r82dhj.720", "row": 1, "col": 1}
    assert all(o["target"]["nth"] >= 1 for o in out["ops"] if o["op"] == "replace")      # replacements run from the end of the draft to its start
    assert out["ops"][3]["ifHash"] == "c677e51c" and out["ops"][3]["ifRev"] == 3
    assert out["report"] == ["conflict in mmgx2r82dhj.788 resolved for git: git 'prefers' / draft 'favours'"]
    out = ds.doc_ops(base, text, (FIX / "wr-old.xml").read_text(), (FIX / "wr-now.xml").read_text(), "doc")
    assert all("within" not in o["target"] for o in out["ops"] if o["op"] == "replace")     # the draft's word stays
    assert any("resolved for doc" in r for r in out["report"])


def test_bind_handles_odd_file_names_and_existing_attributes(tmp_path):
    git(tmp_path, "init", "-q")
    (tmp_path / ".gitattributes").write_text("*.png binary")                    # no trailing newline
    for name in ("my file.md", "[draft].md", "a: b.md", "#x.md"):
        f = tmp_path / name
        f.write_text("# T\n\ntext here\n")
        git(tmp_path, "add", "-A")
        git(tmp_path, "commit", "-qm", name)
        r = run("bind", str(f), "--tool", "claude-docs", "--origin", "u", "--synced-rev", "1")
        assert r.returncode == 0, (name, r.stderr)
        assert json.loads(run("status", str(f)).stdout)["bound"] is True, name
        run("bind", str(f), "--tool", "claude-docs", "--origin", "u", "--synced-rev", "1")      # twice adds no second line
    text = (tmp_path / ".gitattributes").read_text()
    assert text.startswith("*.png binary\n") and text.count("claude-docs-bind") == 4
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "my file.md").write_text("x\n")
    assert json.loads(run("status", str(sub / "my file.md")).stdout)["bound"] is False   # anchored: same name below is not bound


def test_bind_needs_a_committed_body_and_bindings_file_errors_are_clean(tmp_path):
    git(tmp_path, "init", "-q")
    f = tmp_path / "d.md"
    f.write_text("# T\n\nwords here\n")
    r = run("bind", str(f), "--tool", "claude-docs", "--origin", "u", "--synced-rev", "1")
    assert r.returncode == 1 and "commit it first" in r.stderr
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-qm", "x")
    assert run("bind", str(f), "--tool", "claude-docs", "--origin", "u", "--synced-rev", "1").returncode == 0
    side = tmp_path / ".helix-bindings.yml"
    for bad in ("bindings: [", "bindings:\n  - tool: x\n"):
        side.write_text(bad)
        r = run("status", str(f))
        assert r.returncode == 1 and "Traceback" not in r.stderr, bad
    side.write_text("bindings:\n  - path: d.md\n    tool: claude-docs\n    synced_rev: 010\n    base_sha256: 0000\n")
    assert json.loads(run("status", str(f)).stdout)["synced_rev"] == "010"


# ---- regressions from the third review: merge3 whitespace, write-back targeting ---------------------------

def test_merge3_keeps_structure_around_changes_at_the_edges_of_text_and_blocks():
    assert ds.merge3("B b", "New B b", "B b")[0] == "New B b"
    assert ds.merge3("Old text\n", "# New\n\nOld text\n", "Old text\n")[0] == "# New\n\nOld text\n"
    assert ds.merge3("A.\n\nB b.\n", "A.\n\nNew B b.\n", "A.\n\nB b.\n")[0] == "A.\n\nNew B b.\n"
    assert ds.merge3("A.\n\nB b c.\n", "A.\n\nb c.\n", "A.\n\nB b c.\n")[0] == "A.\n\nb c.\n"
    assert ds.merge3("A.\n\nB b c.\n", "A.\n\nB b c.\n", "A.\n\nB b.\n")[0] == "A.\n\nB b.\n"
    assert ds.merge3("Intro\n\n| a | b |\n| a | d |\n", "Intro\n\n| a | d |\n", "Intro\n\n| a | b |\n| a | d |\n")[0] == "Intro\n\n| a | d |\n"


def test_merge3_keeps_whitespace_only_changes_and_rewraps():
    assert ds.merge3("a b c d\n", "a b\n\nc d\n", "a b c D\n")[0] == "a b\n\nc D\n"
    assert ds.merge3("- a\n- b\n", "- a\n  - b\n", "- a\n- b\n")[0] == "- a\n  - b\n"
    assert ds.merge3("one two three four\n", "one two\nthree four\n", "one two three FOUR\n")[0] == "one two\nthree FOUR\n"


def test_merge3_a_change_next_to_one_already_on_both_sides_is_not_a_conflict():
    assert ds.merge3("a X Z b", "a Y Z b", "a Y W b", "ours") == ("a Y W b", [])


def draft_xml(paragraphs):
    out = []
    for i, text in enumerate(paragraphs):
        out.append(f"<paragraph id='{'s.%d' % (i * 10) if i == 0 else '.%d' % (i * 10)}'><text id='.{i * 10 + 1}'>{text}</text></paragraph>")
    return "<doc node='n' rev='1'>" + "".join(out) + "</doc>"


def simulate(ops, blocks):
    """Apply write-back replace ops to plain paragraphs, nth counted over the whole draft in order."""
    blocks = list(blocks)
    for op in ops:
        assert op["op"] == "replace", op
        text, nth = op["target"]["text"], op["target"]["nth"]
        seen = 0
        for i, b in enumerate(blocks):
            at = b.find(text)
            while at >= 0:
                seen += 1
                if seen == nth:
                    assert op["with"]["from"]["content"], op            # an empty replacement is refused by Docs
                    blocks[i] = b[:at] + op["with"]["from"]["content"] + b[at + len(text):]
                    break
                at = b.find(text, at + 1)
            if seen >= nth:
                break
        else:
            raise AssertionError(f"find {text!r} nth {nth} matches nothing in {blocks}")
    return blocks


def test_writer_edits_land_exactly_on_random_drafts_with_repeated_words():
    import random
    rnd = random.Random(7)
    vocab = ["cat", "dog", "the", "a", "very", "TBD", "is", "ship"]
    for _ in range(400):
        base = [" ".join(rnd.choice(vocab) for _ in range(rnd.randint(2, 9))) for _ in range(rnd.randint(1, 4))]
        new = []
        for para in base:
            w = para.split()
            for _ in range(rnd.choice([0, 0, 1, 2])):
                k = rnd.randrange(len(w) + 1)
                kind = rnd.choice(["sub", "ins", "del"])
                if kind == "sub" and w:
                    w[min(k, len(w) - 1)] = rnd.choice(vocab + ["NEW"])
                elif kind == "ins":
                    w.insert(k, rnd.choice(vocab + ["NEW"]))
                elif kind == "del" and len(w) > 1:
                    del w[min(k, len(w) - 1)]
            new.append(" ".join(w))
        base_md = "\n\n".join(base) + "\n"
        file_md = "\n\n".join(new) + "\n"
        xml = draft_xml(base)
        out = ds.doc_ops(base_md, file_md, xml, xml, "git")
        assert out["report"] == [], (base, new, out)
        assert simulate(out["ops"], base) == new, (base, new, out["ops"])


def test_writer_leaves_formatting_odd_spacing_and_unsafe_cases_to_a_person():
    base = "Intro para here.\n\nSecond para here.\n"
    xml = draft_xml(["Intro para here.", "Second  para here."])
    out = ds.doc_ops(base, "Intro para here.\n\nSecond para there.\n", xml, xml, "git")
    assert out["ops"] == [] and any("odd spacing" in r for r in out["report"])
    out = ds.doc_ops("Intro para here.\n\n```\ncode\n```\n", "Intro para here.\n", draft_xml(["Intro para here."]).replace("</doc>", "<codeBlock id='.90'><text id='.91'>code</text></codeBlock></doc>"),
                     draft_xml(["Intro para here."]).replace("</doc>", "<codeBlock id='.90'><text id='.91'>code</text></codeBlock></doc>"), "git")
    assert out["ops"] == [] and any("code, a quote or HTML" in r for r in out["report"])
    xml = draft_xml(["Intro para here."])
    out = ds.doc_ops("Intro para here.\n", "Intro para _really_ here.\n", xml, xml, "git")
    assert out["ops"] == [] and any("formatting" in r for r in out["report"])


def test_writer_inserts_new_blocks_in_file_order_and_not_between_list_items():
    base = "Alpha one.\n\nBeta two.\n"
    xml = draft_xml(["Alpha one.", "Beta two."])
    out = ds.doc_ops(base, "Alpha one.\n\nFirst new.\n\nSecond new.\n\nBeta two.\n", xml, xml, "git")
    contents = [o["source"]["from"]["content"] for o in out["ops"] if o["op"] == "insert"]
    assert contents == ["Second new.", "First new."]                         # applied in order: First ends up above Second
    base = "- a\n- b\n"
    xml = "<doc node='n' rev='1'><list id='s.0' kind='bullet'><listItem id='.1'><paragraph id='.2'><text id='.3'>a</text></paragraph></listItem><listItem id='.4'><paragraph id='.5'><text id='.6'>b</text></paragraph></listItem></list></doc>"
    out = ds.doc_ops(base, "- a\n\nBetween.\n\n- b\n", xml, xml, "git")
    assert out["ops"] == []


def test_writer_will_not_delete_what_it_cannot_delete_cleanly():
    xml = "<doc node='n' rev='1'><list id='s.0' kind='bullet'><listItem id='.1'><paragraph id='.2'><text id='.3'>parent</text></paragraph><list id='.4' kind='bullet'><listItem id='.5'><paragraph id='.6'><text id='.7'>child one</text></paragraph></listItem></list></listItem></list></doc>"
    out = ds.doc_ops("- parent\n  - child one\n", "- child one\n", xml, xml, "git")
    assert [o for o in out["ops"] if o["op"] == "delete"] == [] and any("nested" in r for r in out["report"])
    xml = "<doc node='n' rev='1'><table id='s.0'><row id='.1'><cell id='.2'><paragraph id='.3'><text id='.4'>x</text></paragraph></cell></row><row id='.5'><cell id='.6'><paragraph id='.7'><text id='.8'>same</text></paragraph></cell></row><row id='.9'><cell id='.10'><paragraph id='.11'><text id='.12'>same</text></paragraph></cell></row></table></doc>"
    out = ds.doc_ops("| x |\n|---|\n| same |\n| same |\n", "| x |\n|---|\n| same |\n", xml, xml, "git")
    assert [o for o in out["ops"] if o["op"] == "delete"] == [] and any("repeated identical" in r for r in out["report"])


# ---- regressions from the fourth review: merge3 and the write-back's block pairing ------------------------

def test_merge3_reviewer_cases():
    assert ds.merge3("one\ntwo three\n", "one two\nthree\n", "one\nthree\n")[0] == "one\nthree\n"
    assert ds.merge3("S0 w0\n\nS1\n\n", "S0 S1\n\n", "S0 w0 S1\n\n")[0] == "S0 S1\n\n"
    out = ds.merge3("S0\nw0\n\nw1 S1\n", "S0\nw0\nw1 S1\n", "S0 T0\nw1 T2 T3\n")[0]
    assert out.split() == ["S0", "T0", "w1", "T2", "T3"]
    assert ds.merge3("w0\nw1", "w0\n\nw1", "w0\nX1")[0] == "w0\n\nX1"
    assert ds.merge3("a b c d", "a b X d", "a b Y c d", "ours")[0].split() == ["a", "b", "Y", "X", "d"]
    out = ds.merge3("S0 w0\n\nw1 w2 S1\n\n", "S0 w1 w2 S1\n\n", "S0 w0\n\nw1 w2 T3 S1\n\n")[0]
    assert out.split() == ["S0", "w1", "w2", "T3", "S1"] and "\n\n" in out


def test_merge3_fuzz_keeps_every_word_and_never_glues_or_duplicates():
    import random
    rnd = random.Random(11)
    gaps = [" ", " ", "\n", "\n\n", "  "]
    for _ in range(3000):
        n = rnd.randint(4, 14)
        words = [f"w{i}" for i in range(n)]
        bgaps = [rnd.choice(gaps) for _ in range(n)]
        spots = list(range(0, n, 2))
        rnd.shuffle(spots)
        edits = {"ours": {}, "theirs": {}}
        for k, i in enumerate(spots[: rnd.randint(0, 4)]):
            edits[rnd.choice(["ours", "theirs"])][i] = rnd.choice(["sub", "ins", "del"])

        def render(side):
            ws, gs = [], []
            for i, w in enumerate(words):
                kind = edits[side].get(i)
                g = bgaps[i]
                if kind == "ins":
                    ws.append(f"{side[0]}{i}new")
                    gs.append(g)
                    g = rnd.choice(gaps) if False else g
                if kind == "del":
                    continue
                ws.append(f"{side[0]}{i}sub" if kind == "sub" else w)
                gs.append(g)
            out = "".join(g + w for g, w in zip(gs, ws)).lstrip() + "\n"
            return out

        base = "".join(g + w for g, w in zip(bgaps, words)).lstrip() + "\n"
        ours, theirs = render("ours"), render("theirs")
        expect = []
        for i, w in enumerate(words):
            for side in ("ours", "theirs"):
                if edits[side].get(i) == "ins":
                    expect.append(f"{side[0]}{i}new")
            kinds = [edits[s].get(i) for s in ("ours", "theirs") if edits[s].get(i)]
            if "del" in kinds:
                continue
            expect.append(next((f"{s[0]}{i}sub" for s in ("ours", "theirs") if edits[s].get(i) == "sub"), w))
        out, lost = ds.merge3(base, ours, theirs)
        assert lost == []
        assert out.split() == expect, (base, ours, theirs, out, expect)
        out2, _ = ds.merge3(base, theirs, ours)
        assert out2.split() == expect


def test_writer_pairs_blocks_by_content_not_position():
    base = "Alpha one two.\n\nBeta three four.\n\nGamma five six.\n"
    xml = draft_xml(["Alpha one two.", "Beta three four.", "Gamma five six."])
    now = draft_xml(["Alpha one two.", "Beta three FOUR.", "Gamma five six."])
    out = ds.doc_ops(base, "Beta three four.\n\nGamma five six.\n\nDelta seven eight nine.\n", xml, now, "git")
    assert out["report"] == []
    assert [o["op"] for o in out["ops"]] == ["delete", "insert"]


def test_writer_pairs_an_edited_short_block_when_the_block_count_changes():
    base = "Intro stays.\n\nDue TBD\n\nTail stays.\n"
    xml = draft_xml(["Intro stays.", "Due TBD", "Tail stays."])
    out = ds.doc_ops(base, "Intro stays.\n\nDue Friday\n\nTail stays.\n\nExtra.\n", xml, xml, "git")
    assert [o["op"] for o in out["ops"]] == ["replace", "insert"]
    assert out["ops"][0]["with"]["from"]["content"].endswith("Friday") or "Friday" in out["ops"][0]["with"]["from"]["content"]
    now = draft_xml(["Intro stays.", "Tail stays."])                     # the draft deleted that block
    out = ds.doc_ops(base, "Intro stays.\n\nDue Friday\n\nTail stays.\n\nExtra.\n", xml, now, "git")
    assert all(o["op"] != "insert" or o["source"]["from"]["content"] == "Extra." for o in out["ops"])


def test_writer_reports_prefix_only_changes_and_does_not_delete_unanchored_blocks():
    xml = "<doc node='n' rev='1'><paragraph id='s.0' heading='2'><text id='.1'>Title</text></paragraph><paragraph id='.2'><text id='.3'>Body here.</text></paragraph></doc>"
    out = ds.doc_ops("## Title\n\nBody here.\n", "### Title\n\nBody here.\n", xml, xml, "git")
    assert out["ops"] == [] and any("heading level" in r or "prefix" in r for r in out["report"])
    xml = "<doc node='n' rev='1'><list id='s.0' kind='bullet'><listItem id='.1'><paragraph id='.2'><text id='.3'>task one</text></paragraph></listItem></list></doc>"
    out = ds.doc_ops("- [ ] task one\n", "- [x] task one\n", xml, xml, "git")
    assert out["ops"] == [] and out["report"]
    xml = "<doc node='n' rev='1'><paragraph id='s.0' heading='1'><text id='.1'>Scope</text></paragraph><paragraph id='.2'><text id='.3'>Body here.</text></paragraph></doc>"
    out = ds.doc_ops("# Scope\n\nBody here.\n", "# Goals\n\nNew para.\n\nBody here.\n", xml, xml, "git")
    assert all(o["op"] != "delete" for o in out["ops"])


def test_writer_deletes_a_whole_table_with_one_op_and_checks_row_widths():
    xml = "<doc node='n' rev='1'><paragraph id='s.0'><text id='.1'>Intro here.</text></paragraph><table id='.2' h='tt'><row id='.3'><cell id='.4'><paragraph id='.5'><text id='.6'>a</text></paragraph></cell></row><row id='.7'><cell id='.8'><paragraph id='.9'><text id='.10'>b</text></paragraph></cell></row></table></doc>"
    out = ds.doc_ops("Intro here.\n\n| a |\n|---|\n| b |\n", "Intro here.\n", xml, xml, "git")
    dels = [o for o in out["ops"] if o["op"] == "delete"]
    assert len(dels) == 1 and dels[0]["target"]["ids"] == [".2"] or dels[0]["target"]["ids"] == ["s.2"]
    out = ds.doc_ops("Intro here.\n\n| a |\n|---|\n| b |\n", "Intro here.\n\n| a |\n|---|\n| b |\n| c | d |\n", xml, xml, "git")
    assert [o for o in out["ops"] if o["op"] == "insert"] == [] and any("by hand" in r for r in out["report"])


# ---- packaging: a uv tool released with HELIX --------------------------------------------------------------

def test_the_vendored_table_check_equals_the_skills_copy_and_the_version_follows_the_plugin():
    for name in ("assessment-tables.py", "structured_blocks.py"):
        assert (Path(SRC) / "draftsync/vendor" / name).read_bytes() == (REPO / "skills/helix/scripts" / name).read_bytes(), \
            f"run: cp skills/helix/scripts/{name} tools/draftsync/src/draftsync/vendor/"
    plugin = json.loads((REPO / ".claude-plugin/plugin.json").read_text())["version"]
    assert ds.__version__ == plugin
    assert f'version = "{plugin}"' in (REPO / "tools/draftsync/pyproject.toml").read_text()


def test_the_table_guard_uses_the_vendored_check_outside_a_helix_checkout(tmp_path):
    f = tmp_path / "PP.md"
    f.write_text((FIX / "pp-with-notes.md").read_text())
    shutil.copy(REPO / "workflows/activities/00-discover/artifacts/criteria.yml", tmp_path)
    assert ds.find_tables_script(f).parent.name == "vendor" or "skills" in ds.find_tables_script(f).parts
    vendored = Path(SRC) / "draftsync/vendor/assessment-tables.py"
    e = tmp_path / "e.json"
    e.write_text(json.dumps({"ops": [{"op": "replace", "block": 15, "cell": 1, "text": "Recommended"}]}))
    r = run("apply", str(f), "--edits", str(e), "--assessment-tables", str(vendored))
    assert r.returncode == 1 and "generated table" in r.stderr
