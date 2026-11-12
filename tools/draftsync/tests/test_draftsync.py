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
