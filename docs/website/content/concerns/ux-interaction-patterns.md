---
title: "UX Interaction Patterns"
slug: ux-interaction-patterns
generated: true
aliases:
  - /reference/glossary/concerns/ux-interaction-patterns
---

**Category:** Quality Attributes · **Areas:** ui, frontend

## Description

## Category
quality-attribute

## Areas
ui, frontend

## Boundary

Owns basic user-visible behavior independently of framework, component library,
brand or hosting. ux-radix and packaged-design-system compose this baseline; neither
library adoption nor accessibility-friendly primitives prove a user flow works.
a11y-wcag-aa owns compliance; e2e-framework owns the execution harness.

## Constraints

- Native links and navigation landmarks for destinations; visible current
  location plus aria-current="page" where page navigation exists. Same-page
  tabs use aria-selected and the tab pattern, not aria-current as a substitute.
- All interactive flows complete by keyboard with visible focus. Apply composite
  arrow keys/typeahead only to the actual widget pattern, not ordinary nav links.
- Modal dialogs trap focus, have accessible names, support applicable dismissal,
  and restore focus to their trigger or a logical successor. Non-modal popovers
  allow focus to leave; do not impose modal trapping on them.
- Async actions show progress, prevent duplicate submission while pending, and
  show success/failure with a recovery path. Preserve entered data on failure.
- Forms expose labels and actionable validation errors; placeholders alone are
  not labels. Data surfaces have applicable loading, empty and error/retry states.
- Destructive actions follow the project's explicit confirmation or recovery
  contract. Irreversible/high-impact actions require confirmation; reviewed undo
  may govern low-risk reversible actions. Never silently delete.
- Search exposes query, results/no-results and reset. Plain text filtering does
  not require a combobox; selectable suggestions use the matching widget pattern.

## When to use

Interactive user interfaces. Static content, pure APIs and source-free prose
record non-applicability rather than inventing interaction flows. Patterns apply
only to affected surfaces. Existing ux-radix selections inherit this baseline;
select it directly with other libraries, without selecting Radix as a side effect.

## Artifact Impact

- USER_STORIES: applicable UX behaviors as stable observable acceptance criteria
- DESIGN_SYSTEM: app-specific navigation, state, modality and recovery conventions
- TEST_PLAN: UX Coverage in affected STPs, mapping patterns and AC IDs to assertions
- IMPLEMENTATION_PLAN: observed interaction results linked through existing STP mappings and normal run reports; conditional supplemental observations per verification practices

## Drift Signals

- Only token audit or unit snapshots offered as interaction proof
- Active nav color with no aria-current, invisible focus, silent failures
- Universal focus traps, arrow-key nav, or combobox filters without pattern fit
- An affected STP missing UX Coverage or an exclusion with no reason

## Practices by activity

Agents working in any of these activities inherit the practices below through runtime work context, such as a DDx bead context digest.

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
