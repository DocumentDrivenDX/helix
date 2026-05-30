---
ddx:
  id: helix.principles
  depends_on:
    - helix.prd
    - helix.product-vision
  review:
    self_hash: 63b4bf567663fa5d7f4d61531ac1dd51c16cfd1002e51459746c7b874b0fc1da
    deps:
      helix.prd: 703d5ebaa378d037fd5ff6cbdf43e015ee014ca6a29b5df0b4c67ba9b117a510
      helix.product-vision: 79d80961a61599087606ddda314e16409a244db23581fbd2eecd3b66353cebf9
    reviewed_at: "2026-05-15T04:11:24Z"
---
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
