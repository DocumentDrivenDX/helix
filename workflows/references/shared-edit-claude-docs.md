# Shared edit: the Claude Docs adapter

Adapter for `workflows/modes/shared-edit.md` when the runtime has the Claude Docs connector. Load it only then. It records what was observed in three round trips of a technology brief, an assessment, and a position paper; test anything outside those before relying on it.

## Open

Create one doc per document from the body (front matter removed), titled with the document id. Record the doc id and its revision in the pull request. The connector adds a byline and takes the title from the doc name, so the doc has blocks the file does not.

## Read what changed

Call the docs `read` tool with `{"kind":"view","sinceRev":<recorded revision>}`.

- An edited block comes back whole and untruncated as text runs with bold kept, and the text is raw: `[1]`, `[[wiki-links]]` and underscores arrive as typed, so nothing is unescaped.
- Unchanged blocks are never returned; they fold into `<gap blocks='N'/>`. In a table only the changed row and cell come back; the gap counts before them give the row and column index. A changed list item comes back alone.
- A deleted block or row is `<gone id='...' was='first 30 characters'/>`. An inserted paragraph or appended row comes back in full with a new id; its neighbours and gaps place it.
- Block ids are stable across edits, and one read from the opening revision returns all later edits together.
- Not returned: the old text of a changed block (take it from the file at the base), who edited, and comment positions (use `query`).

Count blocks in the source with `draftsync.py blocks`, skip the doc's own title and byline blocks, and add the gap counts to find each changed block's index. The doc and the file agree on order but not on the title block, so check old text against the source before applying.

## Fallback: export

Use an export only when the changed-blocks read cannot be used. It reaches only the calling agent, as base64. It joins hard-wrapped lines, rewrites `|---|` to `| --- |`, adds a byline, and escapes `[1]` to `\[1\]`, `[[x]]` to `\[\[x\]\]` and `pg_cron` to `pg\_cron`. Normalize those, diff against the base by paragraph, and write the differences as `EDITS.json`; never copy the export over the file. Draftsync does not normalize exports.

## Not yet tested

Inline code and links, nested lists, a concurrent edit by another person, and edits made in the Docs UI instead of through the tools. Say so in the handoff when a draft involves them.
