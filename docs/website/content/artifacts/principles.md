---
title: "Project Principles"
slug: principles
weight: 160
activity: "Frame"
source: "01-frame/principles.md"
generated: true
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

> **Source identity** (from `01-frame/principles.md`):

```yaml
ddx:
  id: helix.principles
  depends_on:
    - helix.prd
    - helix.product-vision
  review:
    self_hash: 23db2c830aa9a8cabe8d7b6701b4da13bbe04bc979a9c0dc24900f1de2093cf2
    deps:
      helix.prd: e11b46de6300cc84460245fcfd6739210ce38406a76f90e32d26685938302eb1
      helix.product-vision: 13555b55d11d13ad2c01657a4f3b9c421867ca9f41dfb575c829ecb7c0990164
    reviewed_at: "2026-06-14T03:20:37Z"
```

# Project Principles

These principles guide judgment calls across all HELIX activities when
working on HELIX itself. They are not workflow rules or process enforcement
— they are lenses applied when choosing between two valid options. The only
constraint: principles cannot negate HELIX mechanics (artifact authority
order, activity gates, tracker semantics).

This file was authored from the vision; mechanics-describing items below
(authority is the resolver; documents are the contract; alignment is
continuous; work flows in every direction) read as principles but are
actually load-bearing HELIX mechanics. Treat them as principles only in the
sense that they steer judgment about how to extend HELIX itself.

## Principles

1. **Authority is the resolver.** Conflicts between artifacts resolve up the
   artifact authority hierarchy, never down. Source code never overrides
   specification.

2. **Documents are the contract.** Every consequential decision lands as an
   artifact update. If a decision is not in the documents, it does not exist.

3. **Alignment is continuous.** The loop runs always; drift is caught early,
   not in a quarterly audit. The alignment skill is the operator of this rule.

4. **HELIX doesn't run anything.** Execution is the runtime's job — DDx,
   Databricks Genie, Claude Code, anything that reads and writes files.
   HELIX produces aligned documents and plans; the runtime executes them.

5. **Less is more.** HELIX owns the methodology and one skill — not the
   toolbox. Every feature added to HELIX is weighed against "could this live
   in the runtime instead?"

6. **Work flows in every direction.** A test exposes a design gap; a metric
   revises a feature spec; a vision update propagates down. The activity
   names locate the kind of work, not its position in a sequence.

7. **Discipline over improvisation.** AI agents improvise well; the value of
   HELIX is the discipline that makes improvisation reviewable.

## Tension Resolution

| When these pull against each other | Resolve by |
|---|---|
| **Less is more** vs. methodology depth | Trim. If a methodology detail can live in `workflows/` or a glossary page rather than a flagship artifact, move it there. |
| **HELIX doesn't run anything** vs. operator convenience | Move the convenience to the runtime adapter, not HELIX. Wrappers that shorten DDx invocations are DDx's job. |
| **Documents are the contract** vs. ship-it pressure | Capture the decision as a document update before merging; otherwise the change exists only in code and the artifact graph diverges. |

## Size Guidance

Keep this file under ~60 lines. If a principle requires more than two
sentences to explain, it is probably a methodology document, not a
principle. Move the long-form rationale to `workflows/README.md` or a
dedicated explainer and leave one-line guidance here.
