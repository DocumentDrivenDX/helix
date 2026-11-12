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
# ADR-019: A shared editing surface is a HELIX capability, incubated in the consuming repository

| Date | Status | Deciders | Related | Confidence |
|------|--------|----------|---------|------------|
| 2026-11-11 | Proposed | HELIX maintainers | `ddx.authoring.home`, CONTRACT-003, `assessment-tables.py`, documentor | Medium |

## Problem

HELIX exists to make human and agent work on governed documents go well, and the best place for a person and an agent to work on a document is one they can both edit and comment on at once. A consuming repository (Atlas is the case at hand) wants reviewers and Claude to edit a draft copy of each document in Claude Docs, with git staying the record. A sync step lands the draft as a pull request and must leave untouched text byte-identical, because review state keys on the file hash.

Three spikes tested the mechanics. Export-and-diff works but the export joins hard-wrapped lines, rewrites table separators, adds a byline, and escapes `[1]` and `[[wiki-links]]`, so it needs a normalizer. Reading only the blocks changed since a revision returns raw, unescaped, untruncated text and places table edits by row and column, which removes most of the normalizer. That result is one position paper edited by tool; inline code and links, nested lists, a concurrent edit, and edits made in the Docs UI are untested. Should HELIX own this, and when?

## Decision

We will make a shared editing surface a HELIX capability, specified by HELIX and implemented per runtime, and incubate the first implementation in the consuming repository until the untested cases pass. Specifically:

1. **HELIX owns the contract.** A capability-gated mode: open a draft copy of a repo-authored document at a pinned base, take the edits the surface returns, and land them as a patch against that base so every untouched byte is identical. A runtime that offers a shared editing surface implements it; a runtime that does not is unaffected and edits the repository files directly. This sits beyond the minimal runtime contract, as CONTRACT-003 draws that boundary: HELIX portable behaviour ends there, and a runtime adapts HELIX content for its own surfaces.
2. **The adapter is the runtime's, not the skill body's.** Claude Docs is the first adapter. The skill body names the capability, never the connector, so the portability target (zero runtime-specific commands in the skill body) holds.
3. **Authoring home does not change.** A document edited through a draft copy stays `authoring.home: repo`. `external-tool` means the tool is the write surface and the repository holds a checked-in copy; this is the opposite relationship. The draft's document id, revision, and base are operational state, which the schema keeps out of `authoring` and leaves to the pull request or tracker. No field is added.
4. **HELIX owns the checks that come from its own semantics.** Landing a patch refuses an edit to a generated table (an assessment's Criteria and Comparison tables, a position paper's Recommendations table) and points to the `assessment:` or `recommendations:` block, using `skills/helix/scripts/assessment-tables.py` as the check and never `--write` to hide a mismatch. It never edits frontmatter as text. It reports a moved base, and it reports which documents' file hashes the patch changes, so a consumer can stale its seals and reviews.
5. **Incubate in the consumer first.** The mapper from changed blocks to source lines, the word-level patcher, and the orchestration skill are built and tested in the consuming repository against its whole corpus, written to the contract above so they can be lifted unchanged. HELIX adds no mode, validator, or schema field until promotion.
6. **Promote on evidence, not on a second consumer.** HELIX adopts the mode and moves the generic scripts into a host tool under `tools/`, released with HELIX as ADR-015 does for documentor, when all of these hold: inline code and links, nested lists, a concurrent edit by another person, and edits made in the Docs UI pass; the sync has landed real reviews over the consumer's corpus; and the contract is written as a CONTRACT for the second adapter to implement against.
7. **Review state stays the consumer's policy.** The hash-keyed review ledger, the attestation a named person types at a terminal, seals, and the scan for client names are consumer choices. HELIX's living-document principle (`workflows/principles.md`) says review stamps gate nothing, and `ddx.review` is legacy metadata. The contract needs only item 4's report of changed hashes.

## Why We Chose This

### Over keeping it in the consumer for good
This was the first version of this decision, and it undersold HELIX's stake. HELIX already treats external editing as part of its model: `authoring.home: external-tool` has a checked-out and checked-in lifecycle, an origin URL, a connector field, and an export digest (`workflows/artifact-schema.md`). The checks that make a sync safe, generated tables, pinned sources, frontmatter that is never prose, are HELIX's own semantics, and a consumer that reimplements them will drift from them. A feature that improves how people and agents edit together is core to what HELIX is for.

### Over building it in HELIX now
The contract would be written from one adapter and one read path that was proven on one document type, edited by tool only. The connector calls, the export and the changed-blocks read, only reach the calling agent, so HELIX's own CI cannot exercise them; the consumer's corpus and its reviewers can. Incubating costs a later move of working code. Specifying first risks a mode in the skill that has to be rewritten when the Docs UI or a concurrent edit behaves differently from the tool path.

### Over a separate standalone sync tool or MCP server
A server cannot call the connector. The deterministic parts (map, patch, check, open the PR) fit the host-tool pattern ADR-015 already accepted, and that is where item 6 puts them.

### Over moving the review ledger into HELIX
The ledger is keyed by whole-file hash, and it sits outside the file because a review written into the file changes the hash and stales itself. HELIX's documentor avoids the same circularity another way: its `reviewed` stamp sits in a page header the body digest excludes (`tools/documentor/src/documentor/cli.py`). That suits generated pages whose header HELIX controls, not a governed document whose whole-file hash is the seal key, so merging the two would force each to carry the other's constraints.

## Consequences

**Good**: HELIX gets a defined path to bidirectional editing without committing the skill to one vendor. The consumer builds against a stable HELIX (structured blocks, generated tables, pinned sources) and gets table safety from an existing check. The abstraction is extracted from working code.

**Trade-offs**: Until promotion the contract lives in an ADR and in the consumer's code, so a second consumer would copy it. The ledger and attestation have no HELIX validation. The promotion criteria depend on spike cases nobody has run yet, so the date is open.

**Drift signals to watch**: Docs-specific string handling (`\[`, a byline) in HELIX scripts or mode files; the skill body naming a connector; HELIX gaining a field for a document id or revision; a consumer editing a generated table with `--write` to make a sync pass; an attestation written by an agent; review state in a document's frontmatter in a consumer that keys seals on the file hash; promotion happening before the listed cases pass.

## Assumptions

- A runtime-neutral contract can sit above one adapter: a second surface whose edits arrive as whole documents, not changed blocks, would show the contract too narrow.
- The changed-blocks read can replace export-and-diff for text edits, shrinking the normalizer to a block-to-source mapper plus a word-level patcher, with export-and-diff as the fallback. The spike supports this; the untested cases could show it false.
- A skill plus scripts is enough orchestration: if the sync only runs reliably as a standing service, it belongs in a tool, not a mode.

## Validation

**Result**: partly tested (one position paper, edits made by tool only)
**Evidence**: Three spikes recorded in the consumer's design doc. The first two round-tripped a brief and an assessment through export and did not exercise stale-base merge. The third read changes since a revision from a position paper and found:

- Edited blocks come back whole, untruncated, with bold kept and text raw: `[1]`, `[[wiki-links]]` and underscores arrive as typed, so no unescaping is needed.
- Unchanged blocks are never returned; they fold into a gap count. In a table only the changed row and cell appear, and the gap counts give the row and column index.
- A deleted block or row appears with its id and the first 30 characters. An inserted block or row appears in full with a new id.
- Block ids are stable across edits, and a second read from the same revision returns all edits together.
- Not given: the old text of a changed block (it comes from the file at the base commit), who edited, and comment positions (a separate query returns those).

Not yet tested: inline code and links, nested lists, a concurrent edit by another person, edits made in the Docs UI.

## Concern Impact

- **No concern impact**: the decision adds nothing to HELIX yet and selects and overrides no concern.

## What would change this decision

| Trigger | Move |
|---|---|
| The untested cases pass and real reviews have landed over the corpus | Promote: write the contract, add the mode, move the generic scripts to `tools/` |
| The changed-blocks read fails on inline code, links, nested lists, concurrent edits, or edits made in the Docs UI | Keep export-and-diff with the normalizer as the supported path and delay promotion until a path is reliable |
| A second editing surface is wanted before promotion | Write the contract from the two adapters, then promote |
| Landing a patch to a generated table becomes wanted | Add a table-to-block write-back to `assessment-tables.py`; until then, refuse |
| A consumer other than Atlas needs hash-keyed review state | Reopen the ledger question as its own ADR; check it against the living-document principle first |

## First step

Finish the untested spike cases in the consumer, then build the block-to-source mapper and word-level patcher with tests over the consumer's whole corpus, keeping export-and-diff as the fallback. Write both against the contract in item 1 so they lift without change. No HELIX change is needed first.
