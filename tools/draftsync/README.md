# draftsync

The deterministic half of the `shared-edit` mode (`workflows/modes/shared-edit.md`): land edits from a shared editing surface onto a governed Markdown file as a patch against a pinned base. Python 3.11, PyYAML, no network, no agent. The header of `draftsync.py` has the usage and the edit format.

```sh
python3 tools/draftsync/draftsync.py blocks FILE
python3 tools/draftsync/draftsync.py apply FILE --edits EDITS.json --base-commit BASE [--write]
```

It keeps untouched text byte-identical (a changed paragraph keeps each unchanged word's spacing and line breaks), leaves front matter alone, merges into a file that moved since the base with `git merge-file`, and refuses an edit that makes a generated table differ from its front matter. It does not call a surface, normalize an export, scan for names, or know any review state; the agent and the consuming repository own those.

Tests: `just test-draftsync`. The binding, status, hook, merge and draft write-back commands are described in the header of `draftsync.py` and in ADR-020.

## Known limits

- An edit that only adds or removes Markdown emphasis on words the file wrote with backslash escapes (`\*foo\*` to italic) is read as no change.
- Numbered lists are grouped by adjacency, so inserting after or deleting the last item of a numbered list nested inside another list is refused even when it would be safe.
- Deleting a table or a loose-list item can leave one extra blank line.
- A data row whose cells are only dashes (`| - | - |`) reads as a table separator.
- Only the changed-blocks read of the Claude Docs surface has a translator; a full export is not normalized.
- The draft write-back (`doc-ops`) writes only plain-word changes. It reports and leaves to a person: anything in or next to formatting (bold, code, links), blocks with odd spacing, code, quotes and HTML, a new list, table or list item, a block inserted between list items or table rows, a list item deleted with nested items, and blocks that repeat identically.
- `merge3` is quadratic in the length of a changed region: a paragraph of tens of thousands of words on one line is slow; wrapped text is fast.
- `find_base` reads one version per commit of the file (`git log --follow`); a base hundreds of commits back is slow. `rebind` shortens that.
- The hook is silent without PyYAML and does not fire for edits made through a shell command.
