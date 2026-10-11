# UX coverage and runtime evidence

## Scope

For affected interactive UI stories, add the optional UX Coverage section to
the existing story test plan. Check/Polish/handoff require it for readiness;
legacy omission remains structurally valid. Pure API/static-content stories
need no invented interactions. Apply the six categories to the affected scope,
not every screen or control in the product.

## Coverage format

| Pattern | Disposition | AC IDs or Reason |
|---|---|---|
| navigation | covered | US-001-AC1 |
| keyboard-overlays | covered | US-001-AC1 |
| async-actions | not-applicable | No mutation or network action in this slice |
| forms | not-applicable | No form in this slice |
| data-states | not-applicable | Static content only |
| destructive-actions | not-applicable | No destructive operation |

Use exactly one row for each category and one UX Coverage section. covered
rows contain one or more stable numeric US-<n>-AC<m> IDs, comma-separated,
resolving to this STP's Acceptance Criteria Test Mapping. That existing mapping
owns test names, asserted behavior, @covers citation and file/command; do not
create a second competing test matrix. not-applicable rows explain the absent
pattern in this bounded slice. A category may reference multiple ACs.

The instance validator checks row completeness, references and populated mapped
test/assertion/file fields. It does not establish that a referenced test exists,
uses @covers correctly, ran or verifies the actual behavior. Semantic review
must assess the whole assertion and appropriateness of each exclusion. A
present but incomplete section blocks structural validation; legacy absence
passes structure but cannot establish readiness for affected new UX work.

## Runtime proof and exceptions

Review verifies actual mapped test source, the AC citation and meaningful
assertions. Build drives the affected flow and failure branches through the
appropriate real-surface harness. Record command/exit, target environment,
observations and artifact paths in docs/helix/04-build/verification-evidence.md.
For navigation assert semantic current location and check a visible bound cue;
for modals test focus entry/containment/return; for async actions test pending,
duplicate guard and failure recovery. Non-modal and native navigation behavior
follow their actual patterns. No screenshot-only semantic proof.

With ai-design-system also record installed versions, lint result, audit
URLs/routes, supported theme/appearance coverage, JSON/HTML/screenshot paths,
and warning dispositions. An audit checks presentation adoption and contrast,
not these behavioral flows. Reviewed exceptions identify scope, owner, rationale,
alternative observed evidence and review/removal trigger; no silent --off,
ignore, allow-list or warning suppression. SDK-owned warnings go to the SDK owner.
Catalog validation is not a consumer integration run; never claim the latter
from the former.
