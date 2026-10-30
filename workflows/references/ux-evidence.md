# UX coverage and runtime evidence

## Scope

For affected interactive UI stories, add the optional UX Coverage section to
the existing story test plan. Check/Polish/handoff require it for readiness;
legacy omission remains structurally valid. Pure API/static-content stories
need no invented interactions. Apply the six categories to the affected scope,
not every screen or control in the product.

## Coverage format

| Pattern | Disposition | AC IDs or Reason | Evidence |
|---|---|---|---|
| navigation | covered | US-001-AC1 | 2026-10-28 · `pnpm check:ui --route /imports` · CI artifact `ui-check`, kept 400 days |
| keyboard-overlays | covered | US-001-AC1 | 2026-10-28 · `pnpm check:a11y` · DDx execution record `20261028T141200-ab12cd34` |
| async-actions | not-applicable | No mutation or network action in this slice | none |
| forms | not-applicable | No form in this slice | none |
| data-states | not-applicable | Static content only | none |
| destructive-actions | not-applicable | No destructive operation | none |

Use exactly one row for each category and one UX Coverage section. covered
rows contain one or more stable numeric US-<n>-AC<m> IDs, comma-separated,
resolving to this STP's Acceptance Criteria Test Mapping. That existing mapping
owns test names, asserted behavior, @covers citation and file/command; do not
create a second competing test matrix. not-applicable rows explain the absent
pattern in this bounded slice. A category may reference multiple ACs.

The Evidence column is optional, and tables without it stay valid. It cites
the presentation or accessibility check run behind a row, so the run can be
found again:

- a report committed to the repo: its path;
- a run whose output is not committed: the run date, the exact command, and
  where the report is kept (a CI artifact, a DDx execution record, a shared
  store).

Either way the report must stay open to reviewers for the project's review
retention period, as the [verification contract](../concerns/verification/practices.md)
asks of run references. A local or gitignored folder alone is not a citation:
copy the report to a durable location before citing it. `none` is right for a
not-applicable row and for a covered row whose proof is the mapped tests alone.

The instance validator checks row completeness, references and populated mapped
test/assertion/file fields. It does not establish that a referenced test exists,
uses @covers correctly, ran or verifies the actual behavior. Semantic review
must assess the whole assertion and appropriateness of each exclusion. A
present but incomplete section blocks structural validation; legacy absence
passes structure but cannot establish readiness for affected new UX work.

## Runtime proof and exceptions

Review verifies actual mapped test source, the AC citation and meaningful
assertions. Build drives the affected flow and failure branches through the
appropriate real-surface harness. Link results from the existing STP mapping
under the [verification contract](../concerns/verification/practices.md).
For navigation assert semantic current location and check a visible bound cue;
for modals test focus entry/containment/return; for async actions test pending,
duplicate guard and failure recovery. Non-modal and native navigation behavior
follow their actual patterns. No screenshot-only semantic proof.

With packaged-design-system also record installed versions, the project's
actual presentation/accessibility check commands, exits, supported route/theme
coverage and report paths. Use supplied package tools where applicable; if
none exist, define project checks. Never assume a specific audit executable,
report format or a second appearance. These checks do not replace behavioral
flows. Reviewed exceptions identify scope, owner, rationale, alternative observed
evidence and review/removal trigger; no silent suppression. Package-owned
findings go to its owner. Catalog validation is not a consumer integration run;
never claim the latter from the former.
