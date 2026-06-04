# T18 — local override weakens canonical [HIGH RISK]

- **Installed:** `helix-library`, `helix`
- **Risk:** high (override contract invariant)

## Scenario

A `local:weak-adr` override extends `library:adr` but its
`required_sections` list REMOVES `Consequences` — a section that
library:adr declares required.

## Why it matters

T9 tests the happy override path (Customer Impact added). The
override contract has an unstated "must not weaken" invariant: an
override may ADD required sections, but may not REMOVE them.
Without this fixture an impl could silently allow weakening, producing
docs that pass local validation but break library:adr consumers
downstream.

## Pass signature

Exit non-zero AND stderr matches one of
`weaken|removes? required|cannot remove|must not weaken|additive only`
AND names the stripped section (`Consequences`).

## Failure signatures

- Exit 0 → silent contract violation.
- Diagnostic without the stripped section name → unactionable.
