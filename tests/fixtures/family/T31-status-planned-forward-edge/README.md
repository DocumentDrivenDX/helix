# T31 — status: planned downgrades unresolved I101 to I103 [HIGH RISK]

## Scenario

PRD-001 declares `{ kind: informs, to: FEAT-999, status: planned }`.
FEAT-999 does not yet exist. Per §2.3 the typed forward-reference
annotation downgrades I101 (unresolved target) to **I103** outside
of exit-gate checks.

## Why it matters

S4 review item: without the typed escape hatch, authors faced a
binary choice between (a) creating stub FEAT-999 to satisfy the
validator or (b) deleting the edge they want to declare. status:
planned is the operator-facing way to say "I know this isn't
authored yet; surface it but don't block."

## What passes

- Exit 0 (instance-mode, not exit-gate-mode).
- `I103` warning citing PRD-001 and FEAT-999 and the planned status.
- NO `I101` (the present-status code) — the downgrade must be clean.

## What fails

- I101 fires (status: planned not honored).
- Hard exit (warning escalated).
- I103 fires WITHOUT mention of the planned status (diagnostic
  inaccurate).

## Risk

HIGH. Without this, iterative design (PRD before FEAT) is blocked.
