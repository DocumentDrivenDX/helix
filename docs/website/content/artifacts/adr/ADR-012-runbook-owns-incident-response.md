---
title: "ADR-012: Runbook owns incident response procedures; monitoring-setup owns detection only"
slug: ADR-012-runbook-owns-incident-response
weight: 270
activity: "Design"
source: "02-design/adr/ADR-012-runbook-owns-incident-response.md"
generated: true
collection: adr
---

> **Source identity** (from `02-design/adr/ADR-012-runbook-owns-incident-response.md`):

```yaml
ddx:
  id: ADR-012
  depends_on:
    - helix.prd
```

# ADR-012: Runbook owns incident response procedures; monitoring-setup owns detection only

| Date | Status | Deciders | Related | Confidence |
|------|--------|----------|---------|------------|
| 2026-05-30 | Accepted | HELIX maintainers | plan-2026-05-30-artifact-types-and-concerns-audit, monitoring-setup, runbook | High |

## Context

| Aspect | Description |
|--------|-------------|
| Problem | The 2026-05-30 artifact-types-and-concerns audit flagged an ownership collision between `monitoring-setup` and `runbook`: both currently define incident-response routing. `monitoring-setup`'s template carries an `Incident Response` section (escalation paths, response procedures) that duplicates and competes with `runbook`'s `Common Incident Procedures` and escalation content. With two artifact types claiming the same surface, operators must reconcile two sources of truth at the moment they can least afford to. |
| Current State | `monitoring-setup/template.md` includes an `## Incident Response` section. `runbook/template.md` includes `## Common Incident Procedures` (with per-incident sections and a security/data-safety incident path) and explicit escalation routing. The two artifact types overlap on response procedures and escalation rather than partitioning detection from response. |
| Requirements | The catalog must assign incident-response ownership to exactly one artifact type. The other type must stop defining that surface so operators have a single canonical procedure document during an incident. |

## Decision

`monitoring-setup` owns **detection only**: SLI/SLO definitions, alert
routing inputs, threshold tuning, and the observability surface that
produces signals.

`runbook` owns **incident response**: the procedures operators run when
those signals fire — recovery steps, common incident procedures,
escalation paths, and incident commander routing.

In Phase 3, the `Incident Response` section is removed from the
`monitoring-setup` template. Any content from that section not already
covered moves to `runbook`. After Phase 3, the catalog validator can
treat presence of an `Incident Response` (or equivalent response-procedure)
H2 in `monitoring-setup` as a drift signal.

**Key Points**: monitoring-setup = detection surface | runbook = operator
procedure | Phase 3 removes Incident Response from monitoring-setup
template | content not already in runbook moves there

## Alternatives

| Option | Pros | Cons | Evaluation |
|--------|------|------|------------|
| Keep both artifact types defining incident response; rely on authors to keep them in sync | No catalog change | The audit found they are already out of sync; two sources of truth during an incident is the worst possible time for ambiguity | Rejected: status quo the audit flagged |
| Move detection ownership into `runbook` and remove `monitoring-setup` | Single artifact type for the whole operational surface | Detection (SLI/SLO definitions, alert thresholds) and response (procedures, escalation) are authored by different people at different cadences; collapsing them loses that separation | Rejected: conflates two genuinely distinct authoring surfaces |
| **`monitoring-setup` owns detection; `runbook` owns response; Phase 3 removes the Incident Response section from monitoring-setup** | Clean partition aligned to the actual purpose of each artifact type; single source of truth for procedures; enforceable by validator | Requires a content migration for any monitoring-setup content not already in runbook | **Selected: smallest sufficient ownership fix** |

## Consequences

| Type | Impact |
|------|--------|
| Positive | Operators have a single canonical document (`runbook`) for incident procedures and escalation. |
| Positive | `monitoring-setup` becomes focused on its actual purpose — the observability surface — without bleeding into operator procedure. |
| Positive | The catalog validator can flag any future reintroduction of response procedures into `monitoring-setup` as drift. |
| Positive | Authoring cadences are no longer entangled: detection thresholds can evolve without re-touching response procedures, and vice versa. |
| Negative | Phase 3 must perform a content migration from `monitoring-setup`'s Incident Response section to `runbook` for anything not already covered. |
| Negative | Existing `monitoring-setup` artifacts authored under the previous contract need a one-time edit to remove the Incident Response section. |
| Neutral | The two artifact types continue to live side-by-side in the `05-deploy` activity; only their boundaries change. |

## Risks

| Risk | Prob | Impact | Mitigation |
|------|------|--------|------------|
| Content in `monitoring-setup`'s Incident Response section is lost rather than migrated | L | H | Phase 3 migration explicitly diffs the removed content against the runbook template before deleting; anything not already covered is added to runbook |
| Authors continue to add response procedures to `monitoring-setup` after Phase 3 | M | M | Catalog validator flags `Incident Response` (or equivalent response-procedure) H2 in `monitoring-setup` as drift |
| The detection/response partition is unclear at the boundary (e.g. alert routing) | M | M | Detection ends at "signal produced and routed to a destination"; response begins at "operator receives signal and acts." Alert routing destinations (PagerDuty, channel) are detection; what the recipient does is response |
| Existing references from outside the catalog point to the removed section | L | L | Phase 3 ships a redirect note in commit message and updates in-tree references in the same change |

## Validation

| Success Metric | Review Trigger |
|----------------|----------------|
| `monitoring-setup/template.md` contains no Incident Response section after Phase 3 | A PR reintroduces an Incident Response H2 (or equivalent response-procedure section) into `monitoring-setup` |
| All response-procedure content from the removed section is present in `runbook` (either pre-existing or migrated) | Phase 3 lands without a diff confirming migration coverage |
| The catalog validator flags `monitoring-setup` artifacts that carry response-procedure sections | A monitoring-setup artifact ships with response-procedure content and validation passes |
| Operators consulting `runbook` during an incident find escalation and procedure content without needing to cross-reference `monitoring-setup` | An incident retrospective surfaces split-source-of-truth as a contributing factor |

## References

- [Plan: artifact-types-and-concerns audit (2026-05-30)](/artifacts/plan-2026-05-30-artifact-types-and-concerns-audit/)
- [PRD](/artifacts/prd/)
- `workflows/activities/05-deploy/artifacts/monitoring-setup/template.md`
- `workflows/activities/05-deploy/artifacts/runbook/template.md`
