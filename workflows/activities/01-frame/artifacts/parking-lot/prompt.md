# Parking Lot Prompt
Capture deferred work that should not stay in the active path.

## Reference Anchors

Use this local resource summary as grounding:

- `docs/resources/atlassian-product-backlog.md` grounds visible deferred work,
  reprioritization, and closing items that will not be pursued.

## Focus
- Record the item, why it is deferred, and where it belongs next.
- Keep the entry short.
- Link to any relevant artifact or issue.
- Include a concrete revisit trigger; "later" is not a trigger.

## Role Boundary

The Parking Lot is not the backlog or tracker. It holds deferred or future work
that should remain findable without contaminating current scope. Active work
belongs in the Feature Registry and runtime work items. Rejected work should be closed
or cancelled, not parked forever.

## Completion Criteria
- Deferred items are easy to find later.
- Nothing active is buried here.
- Every item has source, rationale, owner, and revisit trigger.

## Promotion to Feature Registry

When a parked entry's revisit trigger fires and the item is ready to enter the
active pipeline, follow the promotion procedure documented in the
[Feature Registry prompt](../feature-registry/prompt.md#promotion-from-parking-lot)
(per [ADR-010](../../../../../docs/helix/02-design/adr/ADR-010-feature-registry-parking-lot-handoff.md)).
