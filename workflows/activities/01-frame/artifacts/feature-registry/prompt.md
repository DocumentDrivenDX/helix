# Feature Registry Generation Prompt
Maintain the feature registry as the source of truth for IDs, ownership, priority, and relevant dependencies.

## Reference Anchors

Use these local resource summaries as grounding:

- `docs/resources/ibm-requirements-management.md` grounds requirements
  traceability, prioritization, validation, and change management.
- `docs/resources/atlassian-product-backlog.md` grounds visible prioritized
  work, dependency awareness, and refinement.

## Focus
- Assign new FEAT-XXX IDs sequentially.
- Record dependencies that materially affect the scoped outcome.
- Link relevant stories, designs, contracts, tests, and code when useful; do not
  require a complete linkage matrix or normalize document status.
- Keep descriptions short; detail belongs in feature specs, stories, designs, and tests.

## Role Boundary

The Feature Registry is not the PRD, backlog, or tracker. It assigns durable
feature identity and preserves feature-level traceability. The PRD defines
requirements; Feature Specifications define behavior; runtime work items track execution.

## Completion Criteria
- Entries are brief and complete.
- IDs are unique and never reused.
- The registry stays easy to scan.
- Governing intent is discoverable from relevant content; missing links alone
  do not block work or justify separate tasks.

## Promotion from Parking Lot

Per [ADR-010](../../../../../docs/helix/02-design/adr/ADR-010-feature-registry-parking-lot-handoff.md),
`feature-registry` and `parking-lot` stay separate and the handoff is an
explicit recorded transition. When a parking-lot entry's revisit criteria are
met, promote it to the registry with the following procedure.

### Promotion Criteria

A parking-lot entry is eligible for promotion when all of these hold:

- **Revisit trigger fired**: the objective condition recorded on the entry has
  occurred (date reached, dependency landed, external signal observed).
- **Scope decided**: the item has been re-scoped into something a feature spec
  can be written against — not a vague idea kept warm.
- **Owner assigned**: a named owner accepts responsibility for the feature
  for the scoped outcome.
- **Blocking ADRs resolved**: any ADR that the entry was waiting on has landed
  (accepted or rejected); items still pending ADRs stay parked.
- **Dependencies available**: prerequisite features listed on the entry have
  an evidenced condition that supports the dependent behavior.

If any criterion fails, leave the entry parked and update the rationale or
revisit trigger to reflect what is still missing.

### Promotion Procedure

1. **Assign the next sequential FEAT-XXX**: never reuse an ID, including IDs
   from cancelled or deprecated features. Add the new row to `Active Features`
   with its scoped outcome, priority, and owner.
2. **Record the back-link to the parking-lot source**: in the new feature row's
   `Source` column, cite the parking-lot entry title (e.g.
   `parking-lot:<entry-title>`). This makes the parked-to-active transition
   auditable.
3. **Update the parking-lot entry**: mark the entry as promoted, record the
   assigned `FEAT-XXX`, and the promotion date. Do not delete the parking-lot
   entry — the historical record is part of the back-link.
4. **Add useful references**: link available governing artifacts that help the
   scoped work. Do not create placeholders for future documents or graph edges.
5. **Carry over dependencies**: copy any `Dependencies` from the parking-lot
   entry into the registry's `Dependencies` table, expressed as FEAT-to-FEAT
   edges where the prerequisites have FEAT-XXX IDs.

The promotion is complete when the new `FEAT-XXX` row exists with a back-link,
the parking-lot entry records the promotion, and its governing intent is clear.
