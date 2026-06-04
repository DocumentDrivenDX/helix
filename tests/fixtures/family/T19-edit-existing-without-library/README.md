# T19 — edit-existing PRD with library missing [HIGH RISK]

- **Installed:** `helix` only (NOT `helix-library`)
- **Risk:** high (most-common-action contract)

## Scenario

Same workspace as T2 (a PRD on disk with `library_type:
library:prd`), but the prompt asks to EDIT it (add a Risks section)
rather than to create a new one.

## Why it matters

T2 tests read (allowed) vs create-new (blocked). T19 covers the
boundary case T2 leaves implicit: editing an existing doc whose
`library_type` cannot be resolved. This is the highest-traffic
real-world authoring action. Without a fixture, two impls can
diverge — one allows string-surgery edits, the other blocks. Pin
the contract: edit is authoring; the library is required.

## Pass signature

- NO Edit/Write tool_use against the PRD.
- Prose surfaces the setup-gap (helix-library not installed/missing/
  required) in proximity to a library name token.
- Prose does NOT contain a `## Risks` heading (no improvisation).

## Failure signatures

- Edit tool_use fires → library bypass on edit path.
- Setup-gap fires but `## Risks` appears in prose → mixed signal,
  user may think the edit was made.
