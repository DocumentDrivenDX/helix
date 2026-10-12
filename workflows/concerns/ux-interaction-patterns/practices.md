# Practices: UX Interaction Patterns

## Requirements

- For affected UI work, record applicable patterns and stable story AC IDs in STP UX Coverage; verify behavior on the running system, not by prose or token audit.
- Cover navigation, keyboard/overlays, async actions, forms, data states and destructive actions where applicable; exclude absent patterns with concrete reasons.
- Stories describe observable outcomes: keyboard completion, current location, failure recovery and safe destructive behavior as applicable.

## Design

- DESIGN.md names the visible active cue and semantic state, visible keyboard focus, modal/non-modal behavior, feedback and recovery conventions.
- Use native links for ordinary navigation. Composite widgets follow their own keyboard contract; do not require menu arrow keys for ordinary links.
- Trap focus only in modal overlays. Dismissal and focus return follow the chosen pattern; when a trigger is deleted, choose a logical successor.
- Confirm irreversible/high-impact actions; document reviewed undo for low-risk reversible actions. Preserve form input after failure.
- Loading, disabled, empty, error and success states apply only where they exist. Do not require autosave, global search, range selection or a particular loader style in every app.

## Implementation

- Preserve the chosen component's keyboard semantics and accessible names. Library absence of a needed widget is a documented design gap, not license to invent its API.
- Async controls signal pending state, prevent duplicate requests, and expose recovery after failure. Error feedback must be perceivable without stealing focus unnecessarily.
- Derive visible current-location styling from the semantic state or a stable bound token/class; selected tabs use aria-selected.

## Testing

- Use the STP UX Coverage format in workflows/references/ux-evidence.md. Assert actual outcomes and connect them to stable AC IDs using @covers.
- Drive relevant routes, overlays, pending and failure paths through the real surface harness. Link normal run reports through the existing STP mapping; reports identify tested revision, command/exit, environment and observations. Supplemental observations apply only to proof gaps outside normal reporting, per verification practices.
- A structural validator establishes a populated evidence plan only. Review must verify mapped tests exist, cite the AC, and observed results prove the behavior; screenshots may support visual review but cannot replace semantic assertions.

## Quality Gates

- Affected new/changed UX work has a reviewed UX Coverage map before handoff; legacy omission is an adoption gap, not retroactive structural invalidity.
- Every applicable pattern has observed evidence or a reviewed exception with owner, rationale, alternative evidence and review trigger. No audit-green-only interaction claim.
