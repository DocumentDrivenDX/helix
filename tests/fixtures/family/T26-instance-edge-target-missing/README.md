# T26 — instance edge target missing → I101 with nearest-ids hint [HIGH RISK]

## Scenario

Same setup as T24/T25 but PRD-001 declares `informs → FEAT-999`,
which does not resolve in the corpus. FEAT-001, FEAT-009, FEAT-019
exist.

## Why it matters

This is the typo case the resolution contract (§2.4 step 3) catches.
Diagnostic must:
1. Cite I101 + the unresolved id (FEAT-999).
2. Emit a nearest-ids hint (FEAT-009, FEAT-019) so authors can
   distinguish typo from forward reference.
3. Mention `status: planned` as the escape hatch for forward
   reference (§2.3) — otherwise authors with a real forward ref
   have to delete the edge, defeating the linkage contract.

The S4 review item turned what was "fuzzy hint" into a tested
contract: BOTH the nearest-match AND the planned-option must appear.

## What passes

- Non-zero exit.
- `I101` violation citing the unresolved id, nearest-ids list, AND
  `status: planned` mention.

## What fails

- Exit 0.
- Diagnostic without nearest-id hint OR without status:planned mention.

## Risk

HIGH. Defends the iterative-design happy path where PRDs reference
yet-unauthored FEATs by id.
