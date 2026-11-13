# draftsync

The deterministic half of the `shared-edit` mode (`workflows/modes/shared-edit.md`): land edits from a shared editing surface onto a governed Markdown file as a patch against a pinned base, merge them with the file's own changes word by word, and carry the file's changes back into the draft. Python 3.11 and PyYAML, no network, no agent. It is released with HELIX like documentor.

```sh
uv tool install "git+https://github.com/DocumentDrivenDX/helix@<tag>#subdirectory=tools/draftsync"
draftsync --help
```

In a HELIX checkout, `uv run --project tools/draftsync draftsync ...` runs it without installing. The header of `src/draftsync/__init__.py` has every command and the edit format; ADR-019 and ADR-020 give the design.

It keeps untouched text byte-identical (a changed paragraph keeps each unchanged word's spacing and line breaks), leaves front matter alone, merges into a file that moved since the base (`merge3`, a word-level three-way merge), and refuses an edit that makes a generated table differ from its front matter. It does not call a surface, normalize an export, scan for names, or know any review state; the agent and the consuming repository own those.

`src/draftsync/vendor/` holds copies of `assessment-tables.py` and `structured_blocks.py` from `skills/helix/scripts/` so the generated-table check works without a HELIX checkout; a test fails if they drift (`cp skills/helix/scripts/<name> tools/draftsync/src/draftsync/vendor/`).

Tests: `just test-draftsync`.

## Known limits

- An edit that only adds or removes Markdown emphasis on words the file wrote with backslash escapes (`\*foo\*` to italic) is read as no change.
- Numbered lists are grouped by adjacency, so inserting after or deleting the last item of a numbered list nested inside another list is refused even when it would be safe.
- Deleting a table or a loose-list item can leave one extra blank line.
- A data row whose cells are only dashes (`| - | - |`) reads as a table separator.
- Only the changed-blocks read of the Claude Docs surface has a translator; a full export is not normalized.
- The draft write-back (`doc-ops`) writes only plain-word changes. It reports and leaves to a person: anything in or next to formatting (bold, code, links), blocks with odd spacing, code, quotes and HTML, a new list, table or list item, a block inserted between list items or table rows, a list item deleted with nested items, and blocks that repeat identically.
- `merge3` is quadratic in the length of a changed region; wrapped text is fast.
- `find_base` reads one version per commit of the file (`git log --follow`); a base hundreds of commits back is slow. `rebind` shortens that.
- The hook does not fire for edits made through a shell command.
