# Practices: Usage Metering (usage-based billing)

These practices are **reviewer-checkable**. Metering is **financial-grade**: a
miscount is lost revenue or an overcharge, so each rule below is verified against
the **running system**, not asserted from a function's existence. They compose
with `verification` (the evidence gate), `enterprise-integration-patterns` (the
idempotent emission edge), and `domain-driven-design` (the usage event's
identity). Where a rule says "exercised on the running system", it is satisfied
by the `verification` evidence gate's artifacts (command + exit status, the live
path driven, the guard branch observed) — **not** by a unit test over a mocked
meter.

## Frame

- The metered subject, the unit billed (per call / per token / per seat / per
  GB-hour), the aggregation function (SUM/COUNT/MAX/UNIQUE_COUNT/LAST), and the
  billing period MUST be named. Pricing model uncertainty (tiers/quotas/overage
  the operator has not fixed) is a **business unknown** → record guidance-needed,
  do not guess.

## Design

- Each billable action MUST be enumerated with **its real call site** — the
  exact point on the request/job path where the action completes — and the
  meter event it emits there. "We'll add a `recordUsage` helper" is not a design;
  the **wire** is.
- The **dedupe/idempotency key** for each event MUST be defined: a stable
  identifier derived from the action (so retries collide) or a UUID persisted
  with the action. Reviewer checks the key is stable across a retry, not random
  per attempt.
- The **independent count** used for reconciliation MUST be named (the raw event
  ledger and/or the billing system's reported total) and the tolerance/period of
  the reconciliation loop SHOULD be stated.
- Late/out-of-order and backfill/correction policy SHOULD be stated (lateness
  window for re-aggregation; explicit adjustment beyond it).

## Implementation

- **MUST: every billable action emits a usage/meter event on its real code
  path.** A metering function that exists but is **not invoked** on the live
  request/job path is a **defect** — the usage is silently un-metered. Reviewer
  verifies the **call site**, not the definition: grep the live handler/job for
  the emit, and confirm it runs when the action runs. *(This is the benched
  defect this concern exists to catch — a `recordUsage` defined but never called
  on the real path; the defined-but-unwired case.)*
- **MUST: usage events are idempotent — every event carries a stable dedupe
  key**, and a replay/retry of the identical action does **not** double-count.
  Reviewer confirms the key is present, stable across retries, and enforced
  (capture-time uniqueness and/or the billing system's identifier window).
- **MUST: metered totals reconcile against an independent count.** A
  reconciliation step compares the metered total to the raw event ledger and/or
  the billing system's reported usage; a divergence beyond the recorded tolerance
  is surfaced. The meter MUST be **auditable** — each billed quantity traces back
  to the events that produced it.
- **MUST NOT: a log line or operational metric used as the billing source of
  truth.** A `log.info` / Prometheus counter on a billable path is **not** a
  meter event. Emit a distinct meter event with a dedupe key (RED metrics may
  also be emitted — different obligation).
- **MUST: emission to the billing system is idempotent.** The dedupe key is
  carried end-to-end; prefer **delta writes** so a re-emit does not re-bill
  (idempotent-receiver at the billing edge — `enterprise-integration-patterns`).
- **SHOULD: late/out-of-order events** are re-aggregated within the lateness
  window or recorded as explicit adjustments — never silently dropped or
  attributed to the wrong period. Backfill/correction is a **recorded
  compensating adjustment**, never an in-place mutation that breaks the audit
  trail.
- **SHOULD: the raw usage record is retained** (an append-only ledger;
  `event-sourcing` is one way) for audit and dispute.

## Testing

- **MUST: a guard/negative test that a retried/duplicate action meters once.**
  Drive the same billable action twice with the same dedupe key against the
  running system and assert the metered total increments **exactly once** (not
  twice). This is the idempotency guard branch the `verification` evidence gate
  requires for the metering acceptance criterion.
- **MUST: a positive test that the billable action's real path emits the event.**
  Exercise the action end-to-end on the running system and observe the meter
  event / metered total move — proving the **wire**, not the definition. A unit
  test that calls `recordUsage()` directly does **not** satisfy this (it would
  pass even when nothing on the real path calls it — the exact defect).
- **MUST: a reconciliation assertion** — the metered total equals the
  independent count for a known sequence of actions (the meter is auditable;
  no silent under/over-count).
- **SHOULD: a late/out-of-order event test** — an event arriving after its period
  is handled per the stated policy, not mis-counted.

## The evidence gate (metering is wired and exercised, not asserted)

Metering wiring MUST be **exercised on the running system**, not asserted from a
function's existence — this is the `verification` evidence gate applied to the
billable path. Before claiming the metering work done, the
`verification-evidence.md` bundle MUST record, from an actual run:

- the **real billable flow driven end-to-end** and the metered total observed to
  move (positive: the wire fires);
- the **idempotency guard branch driven** — the duplicate/retried action — with
  the metered total observed to increment **once** (negative control: a replay
  does not double-count);
- the **reconciliation** observed to match the independent count within
  tolerance.

A meter event whose emit is only *defined* and never observed firing on the
running system is **UNTESTED** — the same failure class the evidence gate refuses
for any unexercised acceptance criterion.

## Quality Gates

- **Every billable action emits a meter event on its real code path** — call
  site verified on the live path, not just a defined-but-unwired function
  (defect if defined-only).
- **Every meter event carries a stable dedupe key**; a retried/duplicate action
  meters **exactly once** (idempotency guard test green against the running
  system).
- **Metered total reconciles against an independent count** within the recorded
  tolerance; each billed quantity traces back to its source events (auditable).
- **No log/metric standing in as the billing source of truth**; meter events are
  distinct, exact, and idempotent.
- **Late/out-of-order and backfill** handled by recorded policy (re-aggregation
  or compensating adjustment), never silent drop or in-place mutation.
- **Metering wiring exercised on the running system** with recorded evidence
  (positive emit + idempotency guard + reconciliation) — not asserted from
  definitions.
