---
title: "Usage Metering (usage-based billing)"
slug: usage-metering
generated: true
aliases:
  - /reference/glossary/concerns/usage-metering
---

**Category:** Revenue-Integrity · **Areas:** api, backend, data

## Description

## Category

revenue-integrity

A metering pipeline that drives invoices is **financial-grade**: a miscount is
lost revenue (under-count) or an overcharge (over-count), so this is a
revenue-integrity concern, not an `observability` one. It deliberately does
**not** sit under `observability`: operational telemetry is best-effort, sampled,
and droppable; a meter that decides what a customer is billed must be **exact,
idempotent, reconcilable, and auditable**. Treating metering as "just another
metric" is the category error this concern exists to prevent.

## Areas

api, backend, data

## Boundary

This concern owns one thing: **every billable action emits an exact,
idempotent, auditable usage/meter event, and the metered total reconciles
against what is billed.** It cuts across the system the way `o11y-otel` does —
it instruments *every billable code path* — but with a financial-grade accuracy
bar that observability does not carry. It is **composable / non-exclusive**:
there is no slot, and it composes on top of whatever billing provider, event
transport, or persistence the product already uses.

Four neighbors must stay distinct:

- **`o11y-otel`** owns **operational** telemetry — traces, metrics, logs for
  debugging and incident response. That telemetry is best-effort and **sampled**:
  dropping or approximating a span is acceptable. A **usage/meter event is the
  opposite** — it is financial, exact, idempotent, and auditable; a dropped or
  double-counted meter event is a revenue defect, not a missing data point. Do
  **not** conflate metering with logging/metrics: a `log.info("charged user")`
  or a Prometheus counter is **not** a meter event. Emit RED metrics *and* a
  meter event on a billable path; they are different obligations with different
  accuracy bars.
- **`event-sourcing`** owns the event-stream persistence mechanic. Usage events
  **can** be persisted as an append-only event stream (an immutable usage
  ledger is exactly the recommended store), but event-sourcing is **one
  implementation** of the audit/replay requirement, not a prerequisite —
  **compose** with it where present; do not require it. This concern states
  *that* metered usage must be reconstructible and replayable; ES is one way to
  hold it.
- **`enterprise-integration-patterns`** owns the messaging/integration mechanics
  at the edge. **Emitting meter events to the billing system** (Stripe meter
  events, usage records) is an integration edge: the **idempotent-receiver**
  pattern applies so the billing system de-dupes a retried emission, and the
  outbound emission is an at-least-once delivery that must not double-charge.
  EIP owns the **transport**; this concern owns *what* must be exact across it.
- **`domain-driven-design`** owns the domain model. A usage event is a
  **domain/integration event with billing meaning** (`ApiCallMetered`,
  `SeatProvisioned`) — DDD names it and gives it ubiquitous language; this
  concern adds the financial-grade capture/idempotency/reconciliation rules that
  a billing event carries beyond an ordinary domain event.

## Components

- **Capture** — at the point of the billable action, on its **real code path**,
  emit a usage/meter event carrying: the metered subject (customer/tenant), the
  quantity (value), the event name/meter, a timestamp, and a **dedupe key**.
  Capture happens where the action actually completes, not in a helper that
  nothing calls.
- **Idempotency key** — every event carries a stable unique identifier (a
  deterministic key derived from the action, or a UUID persisted with it) so
  that retries and at-least-once delivery **de-duplicate** instead of
  double-counting. Stripe enforces uniqueness of the meter event `identifier`
  over a rolling ≥24h window; OpenMeter de-dupes by CloudEvents `id` + `source`.
- **Aggregation** — usage is rolled up over a billing period by a defined
  function: **SUM** (most consumption billing), **COUNT** (equal-weight events),
  **MAX** (peak, e.g. parallel jobs / seats), **UNIQUE_COUNT** (distinct
  entities), **LAST** (snapshot/state). MIN/MAX are duplicate-tolerant; SUM/COUNT
  are **not** and depend on capture-time dedupe being correct.
- **Rating / pricing** — applying the price to the aggregate: tiers, volume
  pricing, **included quotas**, and **overage**. Rating is deterministic and
  reconstructible from the same aggregated input.
- **Emission to billing** — pushing the metered/rated usage to the billing
  system (Stripe meter events / usage records, or an OSS meter like Lago /
  OpenMeter). Emission is **idempotent** (carries the dedupe key end-to-end) and
  prefers **delta writes** so a re-emit does not re-bill.
- **Reconciliation / audit** — an **independent count** (the raw event ledger,
  or the billing system's reported total) is compared against the metered total
  on a schedule; a divergence beyond a small tolerance is flagged. The meter is
  **auditable**: each billed quantity traces back to the events that produced it.

## Constraints

### Metering is financial-grade, not best-effort

- A usage/meter event that drives billing must be **exact, idempotent, and
  auditable**. An under-count silently loses revenue; an over-count overcharges
  the customer. Neither is acceptable as "eventually close enough", which is the
  bar `o11y-otel` telemetry is held to and this concern is **not**.
- A meter event is **not** a log line or an operational metric. Emitting a log
  or incrementing a Prometheus counter on a billable path does **not** satisfy
  this concern; a distinct meter event with a dedupe key must be emitted.

### Every billable action meters on its real code path

- A metering function that **exists but is never invoked on the request/job
  path** is a defect — the usage is silently un-metered (revenue leak). The wire
  is the deliverable, not the function. Verify the **call site on the live path**,
  not just the definition.
- Metering is wired at the point the billable action actually completes, so a
  path that does the work but skips the emit is caught.

### Idempotency: replay must not double-count

- Every event carries a **dedupe/idempotency key**, and a retried or
  re-delivered identical action **meters exactly once**. At-least-once delivery
  is assumed; double-counting on retry is a defect.
- Dedupe is enforced where it can be (capture-time ledger uniqueness, and the
  billing system's `identifier` window), not assumed away.

### Reconciliation: the meter is auditable

- The metered total is periodically reconciled against an **independent count**
  (raw event ledger and/or the billing system's reported usage); a divergence
  beyond a recorded tolerance is surfaced, not ignored. "Invoice parity" — the
  metered total matches what the billing system will bill **before** the invoice
  closes — is the target.
- Every billed quantity is traceable to the source events that produced it; the
  raw usage record is retained for audit/dispute.

### Late, out-of-order, and corrected usage are handled deliberately

- Late-arriving and out-of-order events are handled by a defined policy
  (re-aggregation within a lateness window; an explicit adjustment beyond it),
  not by silently dropping or mis-attributing them to the wrong period.
- Backfill/correction is an explicit, recorded operation (a compensating
  adjustment), never an in-place mutation that breaks the audit trail.

## Drift Signals (anti-patterns to reject in review)

- A `recordUsage` / `meter()` / `trackUsage` function **defined but not called**
  on the real request/job path → un-metered billable action; wire it at the
  call site and verify on the running system
- A billable action with **no meter event** emitted (work done, usage never
  captured) → revenue leak; add capture on the real path
- A meter event with **no dedupe/idempotency key**, or a key that is not stable
  across retries → double-count risk; carry a stable identifier end-to-end
- A retried/duplicate action that **meters twice** → idempotency defect; enforce
  dedupe at capture and at emission
- A `log.info(...)` / metrics counter used **as** the billing source of truth →
  operational telemetry standing in for a meter; emit a real meter event
- **No reconciliation** between metered total and an independent count, or a
  flagged divergence left un-triaged → the meter is unauditable; add the
  reconciliation loop and a tolerance alarm
- Late/out-of-order events **silently dropped** or attributed to the wrong
  period → handle within a defined lateness window or as an explicit adjustment
- Backfill/correction done as an **in-place mutation** of past usage → use a
  recorded compensating adjustment that preserves the audit trail
- A SUM/COUNT aggregation built on a capture path with **no dedupe** → the
  aggregate is unsound; fix dedupe before trusting the total

## When to use

Any product with **usage-based / consumption / metered / seat-overage billing**
— where what a customer owes depends on **how much they used** (API calls,
tokens, compute-seconds, events processed, storage, active seats with overage).
It is composable (no slot); `areas: api, backend, data` scope its practices to
the billable code paths and the usage data layer. Compose with the billing/
integration edge (`enterprise-integration-patterns` for idempotent emission),
with `domain-driven-design` (which names the usage event), optionally with
`event-sourcing` (one way to hold the usage ledger), and with `verification`
(whose evidence gate proves the metering is **wired and exercised on the running
system**, not merely defined). Do **not** select it for **flat-fee /
seat-only-with-no-overage** subscriptions, free products, or non-commercial /
internal tools where no usage drives a charge.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: metering + billing model (aggregation function, idempotency, emission, reconciliation)
- TD: capture on real path / idempotency key / aggregation / rating / emit / reconcile
- FEAT: which actions are billable and the meter each emits
- DATA_DESIGN: usage/meter event ledger with dedupe key, retained for audit
- TEST_PLAN: retried action meters once (idempotency) + metered-total reconciliation

## ADR References

## Practices by activity

Agents working in any of these activities inherit the practices below through runtime work context, such as a DDx bead context digest.

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
