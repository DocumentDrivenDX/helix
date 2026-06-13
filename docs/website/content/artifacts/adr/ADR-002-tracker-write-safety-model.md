---
title: "ADR-002: HELIX Tracker Write Safety Model"
slug: ADR-002-tracker-write-safety-model
weight: 170
activity: "Design"
source: "02-design/adr/ADR-002-tracker-write-safety-model.md"
generated: true
collection: adr
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

> **Source identity** (from `02-design/adr/ADR-002-tracker-write-safety-model.md`):

```yaml
ddx:
  id: ADR-002
  depends_on:
    - helix.prd
    - ADR-001
  review:
    self_hash: 852db3925a3fb93caf0078bfbf138d5881a9be4ddeb70ad6cea96908e08d1343
    deps:
      ADR-001: 16f033617d3ab84a6fa5ebd48d0ec171f1999e6332e26dc956fa7b1a7a8b2685
      helix.prd: 703d5ebaa378d037fd5ff6cbdf43e015ee014ca6a29b5df0b4c67ba9b117a510
    reviewed_at: "2026-05-15T04:11:24Z"
```

# ADR-002: HELIX Tracker Write Safety Model

| Date | Status | Deciders | Related | Confidence |
|------|--------|----------|---------|------------|
| 2026-03-27 | Proposed | HELIX maintainers | tracker, installer, tests | High |

## Context

| Aspect | Description |
|--------|-------------|
| Problem | The built-in HELIX tracker stores one JSON object per line in `.helix/issues.jsonl`, but current mutation paths are naive enough that malformed writes or overlapping edits can corrupt the file and break all tracker operations. |
| Current State | Tracker writes are implemented as full-file read/modify/write cycles with no explicit conflict detection contract, no malformed-file recovery contract, and limited metadata mutation support. Real planning work has already reproduced JSONL corruption while refining issues. |
| Requirements | HELIX needs a conservative local tracker that is safe enough for agent-driven issue refinement and concurrent local supervision. The tracker must surface malformed state explicitly, define what concurrency/conflict guarantees are supported, and make metadata mutation available through first-class commands instead of direct file edits. |

## Decision

We will define the HELIX tracker as a conservative file-backed system with
explicit write-safety guarantees, conflict visibility, and fail-closed
corruption handling.

The tracker will not pretend to provide arbitrary multi-writer transactional
semantics. Instead, it will define the supported local execution model,
require explicit detection or prevention of silent lost updates, and make
malformed tracker state a surfaced failure rather than something the rest of
HELIX must guess around.

The supported local model must explicitly include one automated `ddx work`
session progressing execution while another local session refines specs or
tracker issues. The write-safety model therefore has to support not just file
integrity, but also concurrency-visible mutation semantics that let the runner
revalidate issue state at safe boundaries.

**Key Points**: explicit local write model | fail closed on malformed state |
first-class mutation APIs instead of manual JSONL edits

## Alternatives

| Option | Pros | Cons | Evaluation |
|--------|------|------|------------|
| Keep naive JSONL read/modify/write and rely on careful operator usage | Lowest implementation effort | Proven corruption risk, no race semantics, unsafe for agent-driven refinement | Rejected: already failing in real use |
| Replace the tracker immediately with a database-backed system | Stronger concurrency primitives | Much larger implementation jump, higher distribution complexity, changes HELIX surface area substantially | Rejected for now: too large for the immediate hardening goal |
| **Keep JSONL but define and enforce a conservative write-safety contract** | Preserves the current HELIX tracker shape, addresses current failures, enables deterministic testing | Requires explicit conflict/corruption handling and careful write-path design | **Selected: smallest sufficient hardening** |

## Consequences

| Type | Impact |
|------|--------|
| Positive | Tracker behavior becomes specifiable and testable instead of depending on lucky file writes. |
| Positive | HELIX issue refinement can move toward first-class metadata mutation APIs rather than direct JSONL edits. |
| Positive | The tracker becomes a reliable coordination layer between automated execution and interactive refinement. |
| Positive | Malformed tracker state becomes diagnosable instead of cascading into undefined behavior. |
| Negative | Tracker commands may fail more often and earlier when they detect malformed or conflicting state. |
| Negative | Additional deterministic tests and write-path safeguards are required before the contract is real. |
| Neutral | The tracker remains file-backed and local-first for now. |

## Risks

| Risk | Prob | Impact | Mitigation |
|------|------|--------|------------|
| The supported local concurrency model remains underspecified | M | H | Pair this ADR with an explicit tracker contract artifact and deterministic tests |
| The hardening layer adds partial protections but still misses silent lost updates | M | H | Make race and corruption scenarios executable in the harness before claiming safety |
| Metadata mutation expansion broadens the surface faster than the safety model | M | M | Define mutation contract first, then add APIs behind tests |
| File safety improves but `ddx work` still closes stale work after concurrent refinement | M | H | Define pre-claim/pre-close revalidation and issue supersession semantics in the technical design |

## Validation

| Success Metric | Review Trigger |
|----------------|----------------|
| Tracker docs and tests describe the same write-safety and corruption-handling model | Any tracker mutation behavior that is implemented but not captured in the contract or tests |
| Real malformed-state and overlapping-mutation scenarios fail conservatively instead of corrupting the file | A reproduced issue causes invalid JSONL or silent lost updates |
| HELIX issue refinement no longer requires direct JSONL surgery for supported metadata changes | A HELIX workflow still needs manual JSONL edits for normal tracker mutation needs |
| Concurrent local operator refinement is surfaced as queue drift rather than hidden stale execution | `ddx work` claims or closes work after a material tracker change without revalidation |

## References

- [Product Vision](/artifacts/product-vision/)
- [PRD](/artifacts/prd/)
- ADR-001: HELIX Supervisory Control Model
