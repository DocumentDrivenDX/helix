---
title: "ADR-006: Concern boundary lives once, in concern.md"
slug: ADR-006-concern-boundary-lives-once
weight: 210
activity: "Design"
source: "02-design/adr/ADR-006-concern-boundary-lives-once.md"
generated: true
collection: adr
---

> **Source identity** (from `02-design/adr/ADR-006-concern-boundary-lives-once.md`):

```yaml
ddx:
  id: ADR-006
  depends_on:
    - helix.prd
```

# ADR-006: Concern boundary lives once, in concern.md

| Date | Status | Deciders | Related | Confidence |
|------|--------|----------|---------|------------|
| 2026-05-30 | Accepted | HELIX maintainers | plan-2026-05-30-artifact-types-and-concerns-audit, ADR-004 (dependencies encoding), ADR-005 (practices format) | High |

## Context

| Aspect | Description |
|--------|-------------|
| Problem | The current concern file shape mandates three sections that naturally restate the same boundary: `concern.md`'s `Boundary` section, `practices.md`'s `Boundary with neighbors` section, and the `Constraints` / `Drift Signals` / `Quality Gates` sections that re-encode the same MUSTs in three different formats. Restating the boundary in three places is the structural cause of the verbosity flagged across the catalog — not editorial style. |
| Current State | The 2026-05-30 audit rated 11 of 48 artifact types and 22 of 49 concerns `verbose`. The concerns trace uniformly to this restatement pattern: the audit found `authorization-model`, `multi-tenancy`, `resilience`, `enterprise-integration-patterns`, `relational-data-modeling`, `verification`, `usage-metering`, `ux-radix`, `twelve-factor`, `event-sourcing`, `deployment-topology` all carrying the same Boundary text in three places. Editorial trims partially regress without a shape fix because the contract still asks for three boundary sections. The audit also surfaced two adjacent restatement vectors — `meta.yml` carrying taxonomies and process metadata that duplicate prompt/template content, and prompts/templates each carrying their own checklist of the same rules — that an editorial-only pass would not address. |
| Requirements | The catalog contract must define section ownership so the boundary is stated once, the other sections reference-not-restate it, and a schema validator can flag restatement as drift instead of relying on editorial review. The contract must also fold in the editorial rules from the dropped concision phase so the same contract that eliminates structural restatement also eliminates the adjacent vectors. |

## Decision

Every concern's boundary lives canonically in `concern.md`'s `Boundary`
section, and **only** there. The audit-named `Boundary with neighbors`
section in `practices.md` is removed; the `Constraints`, `Drift Signals`,
and `Quality Gates` sections that remain (in either file, per the
practices-format decision in ADR-005) **reference** the canonical boundary
rather than restating it.

Restatement of boundary prose outside `concern.md`'s `Boundary` section is
now a **drift signal** the catalog schema validator (introduced in Phase 1
Track B) can detect and flag.

We also fold the editorial rules from the dropped concision phase into this
ADR so the contract that fixes the structural restatement also fixes the
adjacent vectors:

1. **`meta.yml` is for machine validation + relationships only.** It does
   not carry taxonomies, process metadata, decision frameworks, success
   indicators, engagement levels, or other content that duplicates prompt
   or template prose. Anything in `meta.yml` that is not consumed by a
   validator or relationship resolver is drift.
2. **Prompt Quality Checklist and template Review Checklist are not both
   present.** The catalog picks one home per artifact type; the other is
   removed. (Default home: template Review Checklist for human-authored
   artifacts; prompt Quality Checklist for generator-authored artifacts.
   Per-artifact choice is recorded in `meta.yml`.)
3. **Tutorial-grade code blocks move to resource docs.** Full Dockerfiles,
   complete Hugo configs, large CSS blocks, multi-step tmux scripts, and
   similar long-form examples do not live in `concern.md` or
   `practices.md`. They live under `docs/resources/` and the concern
   references them by path.

Each of these is enforceable by the same validator that flags boundary
restatement: presence of disallowed `meta.yml` keys, presence of both
checklists, or code blocks exceeding a size threshold become drift
signals.

**Key Points**: boundary stated once in `concern.md` | other sections
reference-not-restate | restatement is a validator-flagged drift signal |
`meta.yml` is machine-only | one checklist per artifact | tutorial code
lives in resource docs

## Alternatives

| Option | Pros | Cons | Evaluation |
|--------|------|------|------------|
| Keep three boundary sections; rely on editorial review to keep them in sync | No contract change; no validator work | The 2026-05-30 audit shows editorial review does not keep them in sync — 22 concerns drifted into restatement; partial trims regress because the contract still asks for three sections | Rejected: this is the status quo the audit flagged |
| Put the boundary in `practices.md`'s `Boundary with neighbors` instead and have `concern.md`'s `Boundary` reference it | Keeps the neighbor-comparison framing | `concern.md` is the entry document a reader opens first; making it reference forward is worse ergonomics; the `practices.md` boundary section is the one that drifted, not `concern.md`'s | Rejected: wrong canonical home |
| Remove the boundary concept entirely; rely on Constraints / Drift Signals / Quality Gates | One fewer section type | The boundary is the load-bearing scope statement; the MUSTs are derived from it. Removing the boundary makes the MUSTs unmoored | Rejected: loses the source of truth |
| **Boundary lives once in `concern.md`; everything else references; validator flags restatement; fold editorial rules into the same contract** | Eliminates structural cause of restatement; mechanizable; one contract covers all three vectors | Requires validator work and a mechanical edit phase to remove the restated prose | **Selected: smallest sufficient structural fix** |

## Consequences

| Type | Impact |
|------|--------|
| Positive | The Phase 3 mechanical edits become a deterministic translation — remove the `Boundary with neighbors` section and rewrite Constraints / Drift Signals / Quality Gates as references — rather than a judgment call. |
| Positive | Future concerns can pass the catalog validator only if the boundary is stated once; the verbose-by-restatement pattern cannot reintroduce silently. |
| Positive | The validator that enforces single-boundary also enforces the `meta.yml` / dual-checklist / tutorial-code rules, so the dropped concision phase's intent is preserved without a separate editorial pass. |
| Positive | The catalog contract becomes one coherent policy — file shape, machine metadata, prose ownership, and resource separation are all enforced by the same validator. |
| Negative | Every existing concern needs the Phase 3 mechanical edit (remove `Boundary with neighbors`, rewrite three sections to reference the canonical boundary). |
| Negative | Several `meta.yml` files lose substantial content (the taxonomies and process metadata that duplicate prompt/template); this is a one-time migration. |
| Negative | The validator must define what "restatement" means precisely enough to catch real drift without false positives on legitimate cross-reference prose. |
| Neutral | The `practices.md` file remains; its body (Design / Implementation / MUST / SHOULD / Quality Gates, or the activity-keyed form per ADR-005) keeps its non-boundary content. |

## Risks

| Risk | Prob | Impact | Mitigation |
|------|------|--------|------------|
| Validator definition of "restatement" produces false positives on legitimate cross-references | M | M | Start with structural checks (presence of a `Boundary with neighbors` H2; `meta.yml` keys outside the allowlist; both checklists present) before attempting prose-similarity detection |
| Phase 3 edits remove prose readers actually relied on for the neighbor comparison | L | M | The canonical `Boundary` section can grow to subsume any load-bearing neighbor language; the rule is "stated once," not "stated minimally" |
| The `meta.yml` allowlist is too narrow and breaks existing tooling | M | M | Inventory consumers of `meta.yml` keys before defining the allowlist; the allowlist is the union of consumed keys |
| Tutorial code moved to `docs/resources/` loses context that made it useful in-line | L | L | Concerns reference the resource doc by path with a one-line summary of what the resource demonstrates |
| Choosing prompt vs template checklist per artifact reopens the orthogonality discussion the catalog is trying to close | L | M | Record the default rule (template checklist for human-authored, prompt for generator-authored) and require an explicit override in `meta.yml` only when deviating |

## Validation

| Success Metric | Review Trigger |
|----------------|----------------|
| The catalog schema validator flags any concern with a `Boundary with neighbors` H2 outside `concern.md`'s `Boundary` section | A new concern lands with restated boundary prose without the validator failing |
| Every `meta.yml` in the catalog contains only keys on the consumer-derived allowlist | A `meta.yml` key is added that no validator or relationship resolver reads |
| No artifact type ships both a prompt Quality Checklist and a template Review Checklist | A PR introduces or restores the duplicate checklist |
| Concern files contain no tutorial-grade code blocks (size threshold honored); tutorial content lives under `docs/resources/` and is referenced by path | A concern grows a multi-screen code example inline |
| Phase 3's mechanical edit pass removes the `Boundary with neighbors` section from every concern and rewrites Constraints / Drift Signals / Quality Gates as references, without regressing the canonical `Boundary` content | The audit re-run still flags the restatement pattern after Phase 3 lands |

## References

- [Plan: artifact-types-and-concerns audit (2026-05-30)](/artifacts/plan-2026-05-30-artifact-types-and-concerns-audit/)
- ADR-004: Dependencies encoding (Phase 1 catalog contract)
- ADR-005: Practices format (Phase 1 catalog contract)
- [PRD](/artifacts/prd/)
