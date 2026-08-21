# Status Report Generation Prompt

Record how an iteration stands against its plan.

## Purpose

Status Report is the **iteration record** of the iterate loop. Its unique job
is to report each committed outcome's status against the iteration plan's
IDs, with evidence per claim, the trades executed under the plan's trade
rules, the blockers and the decisions they need, and next steps.

It is a point-in-time record, not a live surface. The runtime tracker owns
minute-to-minute status; the report freezes an honest snapshot for the
review, the checkpoint, or the stakeholder update.

## Focus

- Author a report only when it has an audience — a review, a client
  checkpoint, a stakeholder update. The tracker already shows live status;
  a report nobody reads is ceremony.
- Report against the plan's outcome IDs — never introduce outcomes the plan
  does not carry; a new outcome is a plan change first.
- Claims-vs-reality applies to every status, not just done: done and at-risk
  cite the proof or the threat (demo, test, commit, metric), on-track cites
  the observable progress so far, dropped cites the trade or escalation. An
  evidence-free claim is a phantom claim and blocks.
- Record trades explicitly. A dropped Best or Better per the trade rules is
  a one-line entry; a Good at risk is an escalation that names its decider —
  Good outcomes are never traded.
- Route review learnings onward: findings that should compete for future
  attention belong in the improvement backlog, not in the report's tail.
- Write for the named audience; a client-facing report may subset the
  outcomes but never contradict the internal one.
- Tier labels carry over from the plan's convention: emoji plus a
  non-breaking space (U+00A0) plus the word — 🟢 Good, 🔵 Better, 🟣 Best.

## Boundary Test

| If you are writing... | Put it in... |
|---|---|
| One iteration's committed outcomes, owners, and dates | Iteration Plan |
| Live task status, assignees, execution history | runtime work item or issue |
| Point-in-time outcome status with evidence | Status Report |
| Measurement interpretation for the iteration | Metrics Dashboard |
| Prioritized follow-up candidates from learnings | Improvement Backlog |

## Completion Criteria

- Every outcome row traces to a plan ID.
- Every done or at-risk claim cites evidence.
- Trades reference the plan's rules or name their approver.
- Every needed decision names its decider.
