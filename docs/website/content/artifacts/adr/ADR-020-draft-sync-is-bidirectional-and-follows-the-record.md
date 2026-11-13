---
title: "ADR-020: Draft sync is bidirectional and follows the system of record"
slug: ADR-020-draft-sync-is-bidirectional-and-follows-the-record
weight: 380
activity: "Design"
source: "02-design/adr/ADR-020-draft-sync-is-bidirectional-and-follows-the-record.md"
generated: true
collection: adr
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

> **Source identity** (from `02-design/adr/ADR-020-draft-sync-is-bidirectional-and-follows-the-record.md`):

```yaml
ddx:
  id: ADR-020
  authoring:
    home: repo
  status: proposed
  depends_on:
    - ADR-019
```

# ADR-020: Draft sync is bidirectional and follows the system of record

| Date | Status | Deciders | Related | Confidence |
|------|--------|----------|---------|------------|
| 2026-11-12 | Proposed | HELIX maintainers | ADR-019, `ddx.authoring.home`, `tools/draftsync/` | Medium |

## Problem

ADR-019 lands a draft's edits in git as a patch. It leaves four things open. Nothing records which draft a file is bound to, so only whoever opened the draft can sync it. Changes made in git after the draft opened can only stop the sync or be merged by whole lines, never carried back into the draft. When both sides changed the same words, nothing says which side wins. And nothing notices a local edit to a bound file.

`ddx.authoring.home` already answers who wins. `repo` means the file is the document and `external-tool` means the tool is; a conflict between the file and its copy resolves toward `home`. The first version of that field served surfaces with no programmatic interface (a slide deck in a hosted editor). A surface that can report what changed since a revision and accept guarded edits can be synced in both directions.

## Decision

We will sync a bound document in both directions, merge the two sides' changes, and resolve conflicts toward the system of record. Specifically:

1. **Direction is `home`.** A conflict resolves to git when `authoring.home` is `repo` (or absent) and to the tool when it is `external-tool`. No new field is added and `home` stays fixed for the life of the document; changing it is a deliberate migration. The side that loses a conflict is listed in the sync's report, so nothing is overwritten silently.
2. **The binding lives in a sidecar, marked by a git attribute.** `.helix-bindings.yml` holds one entry per bound file: `path`, `tool`, `origin`, `connector`, a draft revision (`synced_rev`), and the SHA-256 of the file body that revision equals (`base_sha256`, body only, because a hash cannot sit in the file it hashes). The pair is the base of the three-way merge: the body is found in git history by its hash, and the draft's own text at that revision is read from the draft. `.gitattributes` marks bound paths with an attribute named for the surface, for example `knowledge/**/*.md claude-docs-bind`, so a hook or script asks `git check-attr` whether a file is bound without reading anything. Document front matter and its hash are untouched by binding.
3. **The merge is three-way and word-level.** The sides are the file at the last sync (the base), the file now, and the draft now. Both sides' changes apply; a conflict exists only where both changed the same words differently, and it resolves toward the record. Identical changes on both sides merge cleanly, which is what lets the binding stay put after a write-back (item 4).
4. **The cycle follows the pull request.** Git is the record only once a change is merged, so:
   - Draft changes land as a pull request carrying the merged text. The PR lists what lost any conflict. The binding is not touched by it.
   - After the merge, changes that exist only in git are written back into the draft as guarded edits that replace only the changed words, so comment anchors survive. A draft edit that lost a conflict to git is replaced, and the report says which.
   - The binding stays where it is. The next sync reads the draft's changes since `synced_rev` against the same base; the changes already merged appear on both sides as identical and merge cleanly, so only newer edits count.
   - The binding moves (`rebind`) only to a draft revision whose text equals a committed file body, checked against the draft, which shortens later reads. It is a change to the sidecar alone.
   - A sync that changes nothing writes nothing.
5. **Surfaces have capability tiers.** Check-in only (the surface can be exported, as with a hosted slide editor): the repository takes a copy and the tool is the record. Read-changes (the surface reports changes since a revision): draft to git, as in ADR-019. Read-and-write (the surface also accepts guarded edits): the full cycle. The Claude Docs adapter is read-and-write.
6. **A local edit to a bound file is noticed by a hook, and acted on by the agent.** A runtime that supports hooks runs `draftsync.py hook` after a file edit. The command checks the attribute and the sidecar and does nothing for an unbound file. For a bound file whose body no longer matches `base_sha256` it records a pending marker in the git directory and tells the agent. The hook cannot call the surface; the agent does the sync. The repository that has bound files registers the hook in its own Claude Code settings, so it runs only where it can matter; the plugin's `hooks/hooks.json`, which Codex also reads and which applies to every user, stays empty until a shared registration is confirmed safe for both runtimes. An edit made through a shell command does not trigger an edit hook, so the agent also checks `draftsync.py status` when it starts a sync. Under `repo` the agent pushes after a commit or merge, not on each edit. Under `external-tool` it warns that the draft wins and the edit may be overwritten.
7. **Automation is agent-run.** The merge, the patch and the checks can run in CI. The surface's reads and writes can only be made by an agent, so a scheduled or triggered agent run does the whole cycle, and CI validates the resulting pull request.

## Why We Chose This

### Over a stored direction field
`home` already says where the document is authored, and a second statement of the same fact could disagree with it. The cost is that direction cannot flip on a live document without a migration, which the schema already treats as deliberate.

### Over binding fields in front matter
A front-matter binding makes every sync, and any later binding change, an edit to the file, and seals and reviews key on the whole-file hash. The cycle already avoids a post-merge commit (item 4), so front matter would mostly work, but a sidecar costs nothing against that rule and keeps document hashes a function of document content. It uses the field names of the existing `external-tool` metadata (`tool`, `origin`, `connector`), so a document can move to the front-matter form later without translation.

### Over a sidecar under `.helix/`
HELIX repositories conventionally ignore `.helix/` for local tracker data, and the repository this was first used in does too, so a binding written there would never be committed. The sidecar is a flat file beside the `.helix.yml` marker.

### Over per-file values in `.gitattributes`
The synced revision changes on every sync, which would make the attributes file a merge-conflict magnet. The attribute carries only the marker.

### Over line-level merging
Documents are hard-wrapped, so two edits to different words of one paragraph can fall on adjacent lines and conflict line by line. Word-level merging conflicts only on words both sides changed.

### Over syncing on every local edit
An uncommitted edit is not the record, and a draft is shared with other people. Pushing it on each keystroke would show them work in progress and cause conflicts that a commit boundary avoids.

## Consequences

**Good**: A bound file can be synced by anyone with access to the draft. Both directions work for surfaces that allow it. Conflicts resolve by a rule the schema already states, and the losing text is reported. Document hashes change only when document content does.

**Trade-offs**: The write-back is deliberately narrow: it writes plain-word changes and names everything else in its report for a person (formatting, new lists and tables, blocks that repeat). The binding is a second file to keep consistent with the documents. A conflict silently resolving toward the record can discard an editor's work, so the report must be read. The write-back needs the draft's current structure and can fail on guards when people are editing; it retries from a fresh read. A hook in the shared plugin runs for every user of the plugin, so it must be inert for repositories with no bound files.

**Drift signals to watch**: A binding field in document front matter; a second direction setting that disagrees with `home`; a conflict resolved without a report; a sync commit that changes a document with no content change; the hook doing work for an unbound file; the write-back replacing whole blocks and detaching comment anchors.

## Assumptions

- The draft's current text is readable in full and edits can be guarded by revision (true of the Claude Docs adapter in the spikes). A surface without that is check-in only.
- Merged changes appearing on both sides as identical is stable enough that the binding need not advance after a merge. A surface that reformats text on write would break this. A block that the file changed and the draft deleted is left deleted and reported, not restored.
- A repository that uses the hook is one that has bound files, so the hook's cost for others is a single attribute lookup.

## Validation

**Result**: tested on one position paper
**Evidence**: The patch and the draft-to-git direction were validated for ADR-019. This decision's word-level merge, binding, hook and write-back have unit tests, and the write-back ran against a live draft: the draft held two edits of its own and the file changed the same paragraph, one of the same words, a table row and a new paragraph. Applying the write-back's edits left the draft equal to the merged text, the conflicting word taken from git as the record, the draft's own edit kept, and the report naming the conflict. Not tested: a draft edited while the write-back runs (the revision guards refuse and a retry is needed), a list item or table the file added, and the hook inside a live Claude Code session.

## Concern Impact

- **No concern impact**: the decision adds no concern and overrides none.

## What would change this decision

| Trigger | Move |
|---|---|
| Direction must differ from `home` for a live document | Add an explicit direction field and make `home` advisory |
| The binding drifts from the documents in practice | Move it into front matter and accept a hash change on each sync |
| A surface reformats text on write | Advance the binding after each write-back |
| The hook proves noisy or unsupported on a runtime | Drop it; the agent checks status when it starts a sync |
