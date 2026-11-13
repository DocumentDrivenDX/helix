# Shared edit: the Claude Docs adapter

Adapter for `workflows/modes/shared-edit.md` when the runtime has the Claude Docs connector. Load it only then. It records what was observed in five round trips (a technology brief, an assessment, and three position papers, two of them edited live, one through the docs tools and one in the Docs UI by several people); test anything outside those before relying on it.

## Open

Create one doc per document from the body (front matter removed), titled with the document id, with the file's own `# ` heading as the doc's first block so the doc and the file have the same blocks. Record the doc id and the revision after creation (`rev` in the create acknowledgement) in the pull request. Do not add a byline or other blocks the file lacks: the translator refuses a doc that does not line up with the file.

## Read what changed

Make two reads of the doc body and save each result's `xml` to a file:

- `{"kind":"view","atRev":<recorded revision>}`: the doc as it was at the opening revision (`OLD.xml`).
- `{"kind":"view","sinceRev":<recorded revision>}`: only what changed since (`DELTA.xml`).

Then run `draftsync edits FILE --old OLD.xml --delta DELTA.xml` and pass its output to `apply` as in the mode. The translator does the block counting below for you and stops if the old doc and the file do not have the same sequence of headings, paragraphs, list items and table rows. What the read returns:

- An edited block comes back whole and untruncated as text runs, and the text is raw: `[1]`, `[[wiki-links]]` and underscores arrive as typed, so nothing is unescaped. Inline formatting arrives as `<bold>`, `<italic>`, `<code>` and `<link href=...>` inside the runs; the translator writes them back as `**`, `*`, backticks and `[text](href)`.
- Unchanged blocks are never returned; they fold into `<gap blocks='N'/>`. In a table only the changed row and cell come back; the gap counts before them give the row and column index. A changed list item comes back alone.
- A deleted block or row is `<gone id='...' was='first 30 characters'/>`, in the place it had. An inserted paragraph or row comes back in full with an id the opening doc did not have; its neighbours and gaps place it.
- Ids print in full once and short (`.90`) after that; the translator expands them.
- Block ids are stable across edits, and one read from the opening revision returns all later edits together.
- Not returned: the old text of a changed block (take it from the file at the base), who edited, and comment positions (use `query`).

The translator handles changed paragraphs, headings, list items and table cells, deleted blocks, rows and list items, and new paragraphs, headings, table rows and single-paragraph list items. It refuses a new list, table or code block, a paragraph that gained or lost heading status, and anything with an element that has no Markdown form (a mention, say); make those changes in the repository. Edits that land in a generated table are refused later, by `apply`. It also refuses a draft whose text, at the opening revision, differs from the file (the draft was made from another version), a block that moved, and a heading level change. `apply` needs PyYAML for its generated-table check and refuses to continue if the check cannot run.

## Fallback: export

Use an export only when the changed-blocks read cannot be used. It reaches only the calling agent, as base64. It joins hard-wrapped lines, rewrites `|---|` to `| --- |`, adds a byline, and escapes `[1]` to `\[1\]`, `[[x]]` to `\[\[x\]\]` and `pg_cron` to `pg\_cron`. Normalize those, diff against the base by paragraph, and write the differences as `EDITS.json`; never copy the export over the file. Draftsync does not normalize exports.

## Not yet tested

Nothing in the cases the tool covers; say in the handoff when a draft goes beyond them.

Tested in the Docs UI by three editors, two of them at the same time (a paragraph edited by two at once, a table row deleted, a table cell retyped, a new nested bullet list): the read shows the merged result, and it lands with only those changes in the diff. A block that was added and deleted after the draft opened comes back as a `<gone>` with an id the opening doc lacks; it is ignored. A new bullet list nested under an existing item is supported; a new numbered or doubly nested one is not.

Tested through the tools on a position paper: inline code, links, a wiki link in running text, a nested list edit, a table row delete and append, a new paragraph, and an edit to a generated table (refused).

## Write into the draft

`draftsync doc-ops` produces the `update` payload ops that carry the file's changes into the draft (see the mode, "Keeping a file bound to its draft"). What it emits for the Claude Docs surface, and what was observed when it ran against a live draft:

- A changed word or phrase is a `replace` with a `find` target and `"as":"text"`, which re-words in place and keeps links, code and comment anchors. The quoted text is widened with neighbouring words until it is unique, and `nth` is added when it still repeats. A table cell change adds `within` with the table id and the cell's row and column.
- A block the file deleted is a `delete` with `ifHash` and `ifRev` taken from the current read; a stale guard refuses and the sync reads again.
- A new paragraph or heading is an `insert` after the previous surviving block, as Markdown; a new table row is an `insert` of a row after the previous row. A new list item, list or table is left to a person and named in the report.
- A change that touches formatting (bold, code, a link) is left to a person; so is a block the draft deleted and the file changed.
