---
ddx:
  id: example.status-report.depositmatch
  depends_on:
    - example.iteration-plan.depositmatch
---

# Status Report

| | |
|---|---|
| **Iteration** | IT-05 |
| **As Of** | Fri 12 Jun 2026 |
| **Kind** | Iteration review |
| **Audience** | Team + pilot-bank operations lead |
| **Plan** | iteration-plan-IT-05.md |

## Summary

> The iteration goal landed: a real anonymized pilot export imports with
> validated rows and actionable errors, demoed live. The Best and Better
> outcomes were traded per the plan's rules to protect it. The anonymization
> field-list question needs a decision before IT-06 planning.

## Outcome Status

| ID | Workstream | Tier | Outcome | Status | Evidence |
|----|------------|------|---------|--------|----------|
| WS-1-good | WS-1 | 🟢 Good | A real anonymized pilot export imports with validated rows | done | Three anonymized fixtures committed under `fixtures/pilot/`; US-003 test suite green (14 tests, each citing its AC); live demo at review |
| WS-1-better | WS-1 | 🔵 Better | Upload p95 latency watch item on pilot dashboard | dropped | Traded 9 Jun per trade rules to protect WS-1-good after error-class count doubled |
| WS-1-best | WS-1 | 🟣 Best | Per-row error messages include remediation hints | dropped | First drop under trade rules, 4 Jun |

## Changes and Trades

- WS-1-best dropped 4 Jun, WS-1-better dropped 9 Jun — both per the plan's
  trade order (Best first, then Better), called by the Delivery Lead. No
  Good-tier escalations.

## Blockers and Risks

| Blocker / Risk | Outcome Affected | Needs | Owner |
|----------------|------------------|-------|-------|
| Anonymization strips two fields matching may depend on | IT-06 roadmap slot | Operations lead to confirm field list by 16 Jun | Priya |

## Next Steps

- File WS-1-better (latency watch) back into the improvement backlog → Priya → 15 Jun
- Confirm anonymization field list with operations lead → Priya → 16 Jun
- Cut IT-06 iteration plan from roadmap order 2 → Delivery Lead → 15 Jun

## Review Checklist

- [x] Every row traces to an iteration-plan outcome ID
- [x] Every done or at-risk claim cites evidence — no phantom claims
- [x] Trades reference the plan's trade rules or name their approver
- [x] Decisions needed name their decider
