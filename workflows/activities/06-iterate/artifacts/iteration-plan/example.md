---
ddx:
  id: example.iteration-plan.depositmatch
  depends_on:
    - example.roadmap.depositmatch
    - example.improvement-backlog.depositmatch
---

# Iteration Plan

| | |
|---|---|
| **Iteration** | IT-05 |
| **Dates** | Mon 1 Jun → Fri 12 Jun 2026 |
| **Review** | Fri 12 Jun, 30-minute demo with pilot-bank operations lead |
| **Lead** | Delivery Lead |
| **Roadmap Slot** | Roadmap order 1 — CSV import validated against real pilot-bank exports |

## Iteration Goal

> By 12 Jun, a pilot-bank operations user imports a real deposit export and
> sees validated rows with actionable errors — shown live in the review demo
> against an anonymized pilot fixture, with the import test suite green.

## Committed Outcomes

Each participating workstream commits exactly one Good, one Better, and one
Best outcome. Good is the protected floor; Best drops first, then Better.
Tiers: 🟢 Good = committed for the review · 🔵 Better = first traded under
pressure · 🟣 Best = only if the iteration runs clean.

| ID | Workstream | Tier | Outcome | Owner | Governing Artifact | Acceptance Evidence |
|----|------------|------|---------|-------|--------------------|---------------------|
| WS-1-good | WS-1 | 🟢 Good | A real anonymized pilot export imports with validated rows — fixtures collected, anonymization documented, all fixture error classes handled | Priya | Improvement backlog rank 1; FEAT-001; story test plan US-003 | Fixture set committed; tests citing US-003 ACs pass; live demo at review |
| WS-1-better | WS-1 | 🔵 Better | Upload p95 latency watch item on the pilot dashboard | Priya | Improvement backlog rank 2 | Dashboard panel live with alert threshold |
| WS-1-best | WS-1 | 🟣 Best | Per-row error messages include remediation hints | Sam | FEAT-001 | Hint text reviewed by operations lead; shown in demo |

**Not participating this iteration**: WS-2 (matching starts IT-06 per
roadmap order 2), WS-3 (reporting gated on matching)

## Trade Rules

- Best drops first, then Better — the Delivery Lead calls trades and records
  them in the status report.
- WS-1-good is never traded: without it the review demo has no honest data
  and the iteration fails. A Good at risk is an escalation, not a trade.

## Tasks

The plan owns membership; the tracker owns live state. Existing work items
are selected by ID in the Work Item column; rows marked `—` are created by
the runtime from this table and back-referenced here. Status records
planning-time state and is not maintained after derivation. Workstream
aliases come from the roadmap's registry; work items carry the alias as a
label (`ws:WS-1`).

### WS-1 · Data Intake — fixtures

| ID | Task | Outcome | Owner | Due | Status | Work Item |
|----|------|---------|-------|-----|--------|-----------|
| 1.1 | Collect three real pilot-bank exports under the data agreement | WS-1-good | Priya | Wed 3 Jun | Backlog | wi-231 (existing) |
| 1.2 | Script and document the anonymization pass | WS-1-good | Priya | Fri 5 Jun | Backlog | — |

### WS-1 · Data Intake — import validation

| ID | Task | Outcome | Owner | Due | Status | Work Item |
|----|------|---------|-------|-----|--------|-----------|
| 2.1 | Enumerate fixture error classes into US-003 test cases | WS-1-good | Sam | Fri 5 Jun | Backlog | — |
| 2.2 | Implement per-row validation error messages | WS-1-good | Sam | Wed 10 Jun | Backlog | — |
| 2.3 | Add remediation hints to error messages | WS-1-best | Sam | Thu 11 Jun | Backlog | — |

### WS-1 · Data Intake — pilot dashboard

| ID | Task | Outcome | Owner | Due | Status | Work Item |
|----|------|---------|-------|-----|--------|-----------|
| 3.1 | Add upload p95 latency panel with alert threshold to the pilot dashboard | WS-1-better | Priya | Tue 9 Jun | Backlog | — |

## Risks

| Risk | Impact | Response |
|------|--------|----------|
| Pilot bank delays export delivery | H | Escalate through the pilot sponsor by 3 Jun; fall back to synthetic fixtures and flag confidence in the review |
| Anonymization strips fields validation depends on | M | Review field list with operations lead before scripting |

## Review Checklist

- [x] Goal is falsifiable at the review date
- [x] Every participating workstream has exactly one Good, one Better, and one Best outcome
- [x] Every committed outcome has an owner, acceptance evidence, and at least one task
- [x] Workstream aliases match the roadmap's registry — none minted here
- [x] Trade rules make the drop order deterministic (Best, then Better; Good never)
- [x] Every task has a stable ID, maps to a committed outcome, and names its work item or is marked for creation
- [x] Runtime work items can derive from the task tables without inventing scope
