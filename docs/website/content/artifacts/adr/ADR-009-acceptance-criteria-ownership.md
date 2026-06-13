---
title: "ADR-009: Acceptance Criteria Live in User-Stories; Feature-Specification Owns Functional Areas and Decomposition"
slug: ADR-009-acceptance-criteria-ownership
weight: 240
activity: "Design"
source: "02-design/adr/ADR-009-acceptance-criteria-ownership.md"
generated: true
collection: adr
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

> **Source identity** (from `02-design/adr/ADR-009-acceptance-criteria-ownership.md`):

```yaml
ddx:
  id: ADR-009
  depends_on:
    - helix.prd
```

# ADR-009: Acceptance Criteria Live in User-Stories; Feature-Specification Owns Functional Areas and Decomposition

| Date | Status | Deciders | Related | Confidence |
|------|--------|----------|---------|------------|
| 2026-05-30 | Accepted | HELIX maintainers | user-stories, feature-specification | High |

## Context

| Aspect | Description |
|--------|-------------|
| Problem | The rule "AC-IDs live in user-stories" is restated five times across the `user-stories` artifact (meta `quality_checks`, meta `automated_checks`, prompt section, prompt blocking checklist, template) and partly mirrored on `feature-specification`. The boundary "FEAT owns FR-n; stories own AC-IDs" is asserted in multiple places but is not load-bearing in any single one, which makes it easy for a future edit to drop the rule on one side without noticing. |
| Current State | `feature-specification` includes acceptance-criteria guidance in its prompt and template (covering happy paths, errors, edge cases with observable outcomes) alongside its FR-n and functional-area material. `user-stories` carries the canonical AC-ID rule but duplicates it across five surfaces. The split of ownership between the two artifacts is implicit rather than declared. |
| Requirements | The HELIX frame phase must have exactly one artifact that owns acceptance-criteria definition and AC-IDs. The boundary must be stated once, load-bearing, and survive future edits. Feature-specification must remain the home of functional areas and the decomposition test (which stories the feature decomposes into) without restating AC material. |

## Decision

Acceptance criteria and AC-IDs live exclusively in `user-stories`.
`feature-specification` declares FR-IDs, functional areas, and the
decomposition test (which user stories the feature decomposes into) but does
**not** define or restate acceptance criteria.

Phase 3 will remove AC-ID and acceptance-criteria restatement from
`feature-specification`'s prompt and template. `user-stories` keeps the single
canonical AC-ID rule, with the meta-quality-check duplication trimmed so the
rule lives in one place rather than five.

**Key Points**: AC-IDs owned by `user-stories` | `feature-specification` owns
FR-IDs, functional areas, and decomposition | rule stated once, not echoed
across surfaces

## Alternatives

| Option | Pros | Cons | Evaluation |
|--------|------|------|------------|
| Keep AC material on both artifacts and rely on cross-references | Uniform appearance; each artifact looks self-contained | Five-way restatement on `user-stories` plus partial mirror on `feature-specification`; no single load-bearing statement; future edits silently drift one side | Rejected: duplication without authority is the current failure mode |
| Move AC ownership to `feature-specification` instead | Feature is the higher-level container; AC near FRs reads naturally | Stories become weaker as test contracts; AC-IDs lose their natural scope (US-`<n>`-AC`<m>`); breaks the decomposition direction (feature -> stories -> AC) | Rejected: AC-ID identity is story-scoped, not feature-scoped |
| **AC-IDs on `user-stories` only; `feature-specification` owns FR-IDs and decomposition** | Single owner per concept; load-bearing rule; preserves the FR -> story -> AC chain; matches how AC-IDs are already scoped | Requires Phase 3 mechanical edits to `feature-specification` prompt/template and trimming `user-stories` meta duplication | **Selected: smallest change that makes the boundary load-bearing** |

## Consequences

| Type | Impact |
|------|--------|
| Positive | The "AC-IDs live in user-stories" rule is stated once and is load-bearing rather than echoed five ways. |
| Positive | `feature-specification` focuses on FR-IDs, functional areas, and the decomposition test, which is its actual job. |
| Positive | The FR -> story -> AC decomposition direction is visible in the artifact shapes themselves. |
| Positive | Future edits cannot silently drift the boundary; there is one place to change. |
| Negative | Phase 3 must touch `feature-specification`'s prompt and template to remove acceptance-criteria material, and trim `user-stories` meta to collapse the five-way restatement. |
| Neutral | The FR-n / AC-ID identifier schemes themselves are unchanged. |

## Risks

| Risk | Prob | Impact | Mitigation |
|------|------|--------|------------|
| `feature-specification` authors continue to write AC inline by habit | M | M | Phase 3 prompt edits redirect AC material to `user-stories`; reviewers reject AC in feature-specification |
| Removing AC guidance from `feature-specification` weakens feature-level testability framing | L | M | Decomposition test stays on feature-specification and points reviewers at the story-level AC for testability |
| `user-stories` meta trimming drops a check that was actually catching defects | L | M | Phase 3 keeps the single canonical AC-ID rule; only redundant restatements are removed |

## Validation

| Success Metric | Review Trigger |
|----------------|----------------|
| `feature-specification` prompt and template contain no AC-ID or acceptance-criteria definitions after Phase 3 | Acceptance-criteria material reappears in `feature-specification` |
| `user-stories` states the AC-ID rule in exactly one canonical place | The AC-ID rule is restated across multiple surfaces of `user-stories` again |
| `feature-specification` carries the decomposition test (which stories the feature decomposes into) and FR-IDs as its primary content | A feature is filed without the decomposition test or FR-IDs |

## References

- [PRD](/artifacts/prd/)
- [Plan: 2026-05-30 Artifact Types and Concerns Audit](/artifacts/plan-2026-05-30-artifact-types-and-concerns-audit/)
