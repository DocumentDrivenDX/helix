---
title: "ADR-019: Sync from an external editing surface lives with the consuming repository"
slug: ADR-019-external-editing-surface-sync-lives-with-the-consumer
weight: 370
activity: "Design"
source: "02-design/adr/ADR-019-external-editing-surface-sync-lives-with-the-consumer.md"
generated: true
collection: adr
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

> **Source identity** (from `02-design/adr/ADR-019-external-editing-surface-sync-lives-with-the-consumer.md`):

```yaml
ddx:
  id: ADR-019
  authoring:
    home: repo
  status: proposed
  depends_on:
    - ADR-015
    - ADR-018
```

# ADR-019: Sync from an external editing surface lives with the consuming repository

| Date | Status | Deciders | Related | Confidence |
|------|--------|----------|---------|------------|
| 2026-11-10 | Proposed | HELIX maintainers | `ddx.authoring.home`, CONTRACT-003, `assessment-tables.py`, documentor | Medium |

## Problem

A consuming repository of governed Markdown (Atlas is the case at hand) wants reviewers and Claude to edit a draft copy of each document in Claude Docs, with git staying the record. A sync step turns the draft into a pull request that must leave untouched text byte-identical, because review state keys on the file hash. Two spikes found that the Docs export joins hard-wrapped lines, rewrites table separators, adds a byline, and escapes `[1]` and `[[wiki-links]]`, so the sync must normalize and patch rather than overwrite. Should this workflow be part of HELIX, part of the consuming repository, or a separate tool?

## Decision

We will keep the "Claude Docs sync and edit" workflow, its adapter, the normalize-and-patch step, and the review ledger with attestation out of HELIX, in the consuming repository (a skill plus deterministic scripts there). HELIX adds no mode, validator, or schema field for it now. Specifically:

1. **No vendor-neutral "external editing surface" abstraction in HELIX yet.** One adapter (Claude Docs) and one consumer do not justify one. The neutral shape, an editing surface that returns a patch against a pinned base, is written down here and extracted only when the triggers below fire.
2. **The existing schema already covers the model.** A repo-authored document edited through a draft copy is `authoring.home: repo` (`workflows/artifact-schema.md`, Authoring home). `external-tool` is the opposite relationship: the tool is the write surface and the repository holds a checked-in copy. The draft's doc id, revision, and base commit are operational state, which the schema keeps out of `authoring` and puts with the pull request or tracker. No field is added.
3. **Generic parts stay as specified, owned by the consumer.** Pinned-base patching, three-way merge on a moved base, hash-staling, and the stale-base report are written once, in the consumer, as scripts with tests over its own corpus. They are generic in idea and cheap to lift later because they take a base file, an edited file, and a normalizer.
4. **Vendor parts and policy parts are consumer-only.** The Docs export quirks and the orchestration that must run inside Claude (the export reaches only the calling agent) are vendor-specific. The review ledger, `attest`, seal staling, and the public-repo scan for client names are Atlas policy.
5. **Generated tables are refused, not patched.** The sync reuses HELIX's `skills/helix/scripts/assessment-tables.py` as the check. An edit that lands in a generated table (the Criteria and Comparison tables of a technology assessment, the Recommendations table of a position paper) is rejected with a pointer to the `assessment:` or `recommendations:` block, where the edit belongs. The sync never rewrites a table to match a draft, and never runs `--write` to hide a mismatch.
6. **The review ledger and attestation do not move into HELIX.** HELIX's living-document principle (`workflows/principles.md`) says review stamps establish no readiness and gate nothing, and `ddx.review` is legacy metadata (`workflows/artifact-schema.md`). An attestation that a named person typed at a terminal is a policy a consumer chooses.

## Why We Chose This

### Over putting the workflow in HELIX
HELIX is content plus one skill, and its portability target is a skill body with zero runtime-specific commands (`docs/helix/00-discover/product-vision.md`, Success Definition). The workflow's core is a vendor connector and a Claude-driven orchestration, which is the runtime-specific work that target excludes. The skill-and-scripts surface already carries 8 scripts for artifact checks; a normalizer tuned to one export format would be the first that exists for one vendor's quirks. ADR-015 shows the accepted pattern when machinery is needed: HELIX owns the contract, a host tool owns the deterministic part. That pattern is available later, and nothing here needs it yet.

### Over a vendor-neutral abstraction now
The abstraction would be designed from one adapter. A third spike (below) showed the docs `read` tool can return only the blocks changed since a revision, as raw unescaped text, so the right interface is "edits since a revision", not "export to Markdown and diff". That was one position paper edited by tool; an abstraction built now would still be fitted to one adapter's one read path.

### Over a separate standalone sync tool or MCP server
The export and the changed-blocks read are both connector calls that only the calling agent can make, so a standalone server or HELIX script cannot call them. A server can provide the deterministic parts (normalize, diff, patch, check, open the PR), and those can live as scripts in the consumer. A separate repository would add a release surface for code one consumer uses.

### Over moving the ledger into HELIX
The ledger is keyed by whole-file hash, and its reason to sit outside the file is that a review written into the file changes the hash and stales itself. HELIX's documentor avoids the same circularity another way: its `reviewed` stamp sits in a page header that the body digest excludes (`tools/documentor/src/documentor/cli.py`). That works for generated pages with a header HELIX controls, not for a governed document whose whole-file hash is the seal key. The two mechanisms answer different problems, so merging them would force one to carry the other's constraints.

## Consequences

**Good**: HELIX stays unchanged and vendor-neutral. The consumer builds against a stable HELIX (v0.22: structured blocks, generated tables, pinned sources) and gets table safety by calling an existing check. The first build is a script, so the abstraction is extracted from working code.

**Trade-offs**: A second consumer would copy the scripts until the extraction trigger fires. The ledger and attestation have no HELIX validation, so a consumer that wants them checked in HELIX CI has to wire that itself.

**Drift signals to watch**: A Docs-specific string handling (`\[`, byline) appearing in HELIX scripts or mode files; HELIX gaining a field for a doc id or revision; a consumer editing a generated table with `--write` to make a sync pass; an attestation written by an agent; review state appearing inside a document's frontmatter in a consumer that keys seals on the file hash.

## Assumptions

- Only one consumer needs the workflow: a second HELIX-governed repository adopting it, with the same patch-against-pinned-base need, would show this false.
- A skill plus scripts in the consumer is enough orchestration: if the sync can only run reliably as a standing service, it is not a skill and belongs in a tool.
- The block-edit read path can replace export-and-diff for text edits: the spike supports this, and the normalizer shrinks to a block-to-source mapper plus a word-level patcher. Export-and-diff stays as the fallback. Inline code and links, nested lists, a concurrent edit by another person, and edits made in the Docs UI rather than by tool are untested and could show it false.

## Validation

**Result**: partly tested (one position paper, edits made by tool only)
**Evidence**: Three spikes recorded in the consumer's design doc. The first two round-tripped a brief and an assessment through export; they did not exercise stale-base merge. The third read changes since a revision from a position paper and found:

- Edited blocks come back whole, untruncated, with bold kept and text raw: `[1]`, `[[wiki-links]]` and underscores arrive as typed, so no unescaping is needed.
- Unchanged blocks are never returned; they fold into a gap count. In a table only the changed row and cell appear, and the gap counts give the row and column index.
- A deleted block or row appears with its id and the first 30 characters. An inserted block or row appears in full with a new id.
- Block ids are stable across edits, and a second read from the same revision returns all edits together.
- Not given: the old text of a changed block (it comes from the file at the base commit), who edited, and comment positions (a separate query returns those).

Not yet tested: inline code and links, nested lists, a concurrent edit by another person, edits made in the Docs UI.

## Concern Impact

- **No concern impact**: the decision adds nothing to HELIX and selects and overrides no concern.

## What would change this decision

| Trigger | Move |
|---|---|
| A second HELIX-governed repository adopts the workflow | Extract the patch-against-pinned-base scripts into a host tool in `tools/`, released with HELIX, as ADR-015 does for documentor; the Docs adapter stays outside it |
| A second editing surface (another connector) is wanted | Define the neutral interface in a contract (CONTRACT-NNN) from the two adapters |
| Atlas-type documents gain a HELIX rule that a generated table may be edited in a draft | Add a table-to-block write-back to `assessment-tables.py`; until then, refuse |
| The changed-blocks read path loses fidelity on inline code, links, nested lists, concurrent edits, or edits made in the Docs UI | Fall back to export-and-diff with the normalizer; the decision stands |
| The changed-blocks read holds up across those cases | Drop the normalizer's unescape and unwrap steps in the consumer; the neutral interface becomes "edits since a revision" when a second adapter exists |
| A consumer other than Atlas needs hash-keyed review state (Atlas already runs one: a ledger and an attest command that a person runs at a terminal) | Reopen the ledger question as its own ADR; check it against the living-document principle first |

## First step

The third spike is done and favours the changed-blocks design. Next, in the consumer, not HELIX: finish the untested cases (inline code and links, nested lists, a concurrent edit, edits made in the Docs UI), then build the block-to-source mapper and word-level patcher with tests over the consumer's whole corpus, keeping export-and-diff as the fallback. No HELIX change is needed first; the first HELIX change waits on the extraction trigger.
