---
ddx:
  id: ADR-019
  authoring:
    home: repo
  status: proposed
  depends_on:
    - ADR-015
    - ADR-018
---
# ADR-019: A shared editing surface is a HELIX capability

| Date | Status | Deciders | Related | Confidence |
|------|--------|----------|---------|------------|
| 2026-11-11 | Proposed | HELIX maintainers | `ddx.authoring.home`, CONTRACT-003, `assessment-tables.py`, documentor | Medium |

## Problem

HELIX exists to make human and agent work on governed documents go well, and the best place for a person and an agent to work on a document is one they can both edit and comment on at once. A consuming repository (Atlas is the case at hand) wants reviewers and Claude to edit a draft copy of each document in Claude Docs, with git staying the record. A sync step lands the draft as a pull request and must leave untouched text byte-identical, because review state keys on the file hash.

Five spikes tested the mechanics. Export-and-diff works but the export joins hard-wrapped lines, rewrites table separators, adds a byline, and escapes `[1]` and `[[wiki-links]]`, so it needs a normalizer. Reading only the blocks changed since a revision returns raw, unescaped, untruncated text and places table edits by row and column, which removes most of the normalizer. A fourth spike edited a position paper live through the docs tools (inline code, links, a nested list, table row delete and append, a new paragraph) and the changed-blocks read, with the opening revision read for comparison, translated exactly into edits that landed with only those changes in the diff. A fifth spike had three people edit a position paper in the Docs UI, two at the same time (a paragraph edited by two at once, a table row deleted, a cell retyped, a nested bullet list added); the changed-blocks read showed the merged result and it landed with only those changes. Should HELIX own this, and when?

## Decision

We will make a shared editing surface a HELIX capability: a runtime-neutral mode, a host tool for the deterministic part, and one adapter reference per runtime surface. The maintainers chose to ship it now, ahead of the earlier plan to incubate it in the consuming repository, and to state the untested cases where the mode and the adapter use them. Specifically:

1. **HELIX owns the contract.** A capability-gated mode: open a draft copy of a repo-authored document at a pinned base, take the edits the surface returns, and land them as a patch against that base so every untouched byte is identical. A runtime that offers a shared editing surface implements it; a runtime that does not is unaffected and edits the repository files directly. This sits beyond the minimal runtime contract, as CONTRACT-003 draws that boundary: HELIX portable behaviour ends there, and a runtime adapts HELIX content for its own surfaces.
2. **The adapter is the runtime's, not the skill body's.** Claude Docs is the first adapter. The skill body names the capability, never the connector, so the portability target (zero runtime-specific commands in the skill body) holds.
3. **Authoring home does not change.** A document edited through a draft copy stays `authoring.home: repo`. `external-tool` means the tool is the write surface and the repository holds a checked-in copy; this is the opposite relationship. The draft's document id, revision, and base are operational state, which the schema keeps out of `authoring` and leaves to the pull request or tracker. No field is added.
4. **HELIX owns the checks that come from its own semantics.** Landing a patch refuses an edit to a generated table (an assessment's Criteria and Comparison tables, a position paper's Recommendations table) and points to the `assessment:` or `recommendations:` block, using `skills/helix/scripts/assessment-tables.py` as the check and never `--write` to hide a mismatch. It never edits frontmatter as text. It reports a moved base, and it reports which documents' file hashes the patch changes, so a consumer can stale its seals and reviews.
5. **Ship the mode, the adapter, and the tool together.** `workflows/modes/shared-edit.md` is the mode, `workflows/references/shared-edit-claude-docs.md` is the Claude Docs adapter, and `tools/draftsync/` is the host tool (parse, word-level patch, three-way merge onto a moved base, generated-table guard, hash report). The skill routes to the mode and names no connector.
6. **Say what is untested.** The adapter lists what was tested and what the tool refuses, and the mode's handoff reports when a draft goes beyond them. The export-and-diff fallback is documented in the adapter but draftsync does not normalize exports.
7. **Review state stays the consumer's policy.** The hash-keyed review ledger, the attestation a named person types at a terminal, seals, and the scan for client names are consumer choices. HELIX's living-document principle (`workflows/principles.md`) says review stamps gate nothing, and `ddx.review` is legacy metadata. The contract needs only item 4's report of changed hashes.

## Packaging

HELIX allows one public skill (`tests/validate-skills.sh` requires `skills/helix/SKILL.md` as the single entrypoint and forbids separate `helix-*` skills) and keeps host vocabulary out of its body. The capability therefore adds no skill and no Claude-only plugin:

| Piece | Home |
|---|---|
| The workflow: open a draft at a pinned base, land edits as a patch, refuse generated tables, report changed hashes | `workflows/modes/shared-edit.md`, routed by the one skill |
| The Claude Docs specifics: connector calls, the changed-blocks read, the export fallback | `workflows/references/shared-edit-claude-docs.md`, loaded only when the runtime has the connector; other runtimes ignore it |
| The deterministic part: block parser, word-level patcher, merge, table guard | `tools/draftsync/`, tested by `just test-draftsync` |
| Review ledger, attestation, seals, scan for client names | The consuming repository |

## Why We Chose This

### Over keeping it in the consumer for good
This was the first version of this decision, and it undersold HELIX's stake. HELIX already treats external editing as part of its model: `authoring.home: external-tool` has a checked-out and checked-in lifecycle, an origin URL, a connector field, and an export digest (`workflows/artifact-schema.md`). The checks that make a sync safe, generated tables, pinned sources, frontmatter that is never prose, are HELIX's own semantics, and a consumer that reimplements them will drift from them. A feature that improves how people and agents edit together is core to what HELIX is for.

### Over incubating in the consumer first
The earlier version of this decision incubated the mapper and patcher in the consuming repository and promoted on evidence. The maintainers chose to ship now. The risk named then still stands: the contract is written from one adapter and one read path proven on one document type, edited by tool. The mitigation is that the tool is small and deterministic, is tested against the whole of this repository's Markdown and the consumer's `knowledge/` (replacing every paragraph, heading and item with its own unwrapped text changes no byte), refuses what it cannot do safely, and that the adapter says which cases are untested.

### Over a separate standalone sync tool or MCP server
A server cannot call the connector. The deterministic parts (map, patch, check, open the PR) fit the host-tool pattern ADR-015 already accepted, and that is where item 6 puts them.

### Over moving the review ledger into HELIX
The ledger is keyed by whole-file hash, and it sits outside the file because a review written into the file changes the hash and stales itself. HELIX's documentor avoids the same circularity another way: its `reviewed` stamp sits in a page header the body digest excludes (`tools/documentor/src/documentor/cli.py`). That suits generated pages whose header HELIX controls, not a governed document whose whole-file hash is the seal key, so merging the two would force each to carry the other's constraints.

## Consequences

**Good**: HELIX gets a defined path to bidirectional editing without committing the skill to one vendor. The consumer builds against a stable HELIX (structured blocks, generated tables, pinned sources) and gets table safety from an existing check. The abstraction is extracted from working code.

**Trade-offs**: The untested spike cases ship as stated limits. The ledger and attestation have no HELIX validation. HELIX now maintains a tool whose only runtime today is one connector, and it has no version of its own, so it is not in the release version sync that documentor has.

**Drift signals to watch**: Docs-specific string handling (`\[`, a byline) in HELIX scripts or mode files; the skill body naming a connector; HELIX gaining a field for a document id or revision; a consumer editing a generated table with `--write` to make a sync pass; an attestation written by an agent; review state in a document's frontmatter in a consumer that keys seals on the file hash; the adapter's untested list growing without anyone running the cases.

## Assumptions

- A runtime-neutral contract can sit above one adapter: a second surface whose edits arrive as whole documents, not changed blocks, would show the contract too narrow.
- The changed-blocks read can replace export-and-diff for text edits, shrinking the normalizer to a block-to-source mapper plus a word-level patcher, with export-and-diff as the fallback. The spike supports this; the untested cases could show it false.
- A skill plus scripts is enough orchestration: if the sync only runs reliably as a standing service, it belongs in a tool, not a mode.

## Validation

**Result**: tested on four documents (a brief, an assessment, two position papers), through the tools and in the Docs UI, including a concurrent edit
**Evidence**: Three spikes recorded in the consumer's design doc. The first two round-tripped a brief and an assessment through export and did not exercise stale-base merge. The third read changes since a revision from a position paper and found:

- Edited blocks come back whole, untruncated, with bold kept and text raw: `[1]`, `[[wiki-links]]` and underscores arrive as typed, so no unescaping is needed.
- Unchanged blocks are never returned; they fold into a gap count. In a table only the changed row and cell appear, and the gap counts give the row and column index.
- A deleted block or row appears with its id and the first 30 characters. An inserted block or row appears in full with a new id.
- Block ids are stable across edits, and a second read from the same revision returns all edits together.
- Not given: the old text of a changed block (it comes from the file at the base commit), who edited, and comment positions (a separate query returns those).

The fourth spike also showed that the opening revision is readable (`atRev`), so inserted blocks are the ids that revision lacked, and deleted blocks arrive in the place they had. The fifth spike covered concurrent edits and Docs UI edits. Not yet tested: a whole new table or numbered nested list in the doc, which the tool refuses, and a second surface.

## Concern Impact

- **No concern impact**: the decision adds nothing to HELIX yet and selects and overrides no concern.

## What would change this decision

| Trigger | Move |
|---|---|
| A case outside what was tested (a new table, a numbered nested list, another surface) fails in use | Add it to draftsync, or make the export fallback the supported path with an export normalizer |
| A second editing surface is wanted | Write a CONTRACT from the two adapters and move the shared edit format out of the script header |
| Landing a patch to a generated table becomes wanted | Add a table-to-block write-back to `assessment-tables.py`; until then, refuse |
| A consumer other than Atlas needs hash-keyed review state | Reopen the ledger question as its own ADR; check it against the living-document principle first |

## First step

Use it on a real review in the consuming repository and send each input it gets wrong back as a failing test; build the export normalizer only if the changed-blocks read fails on a real draft.
