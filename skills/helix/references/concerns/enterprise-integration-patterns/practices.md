# Practices: Enterprise Integration Patterns

These practices govern **asynchronous messaging and cross-system integration** —
the channels, message shapes, routers, transformers, endpoints, and operational
patterns that carry information across a system or context boundary. They do not
govern in-process domain modeling (`domain-driven-design`), codebase layering
(`onion-architecture`), or intra-process object patterns (`design-patterns-gof`);
they reference those concerns at the seam and stay on the wire.

## Design

- For each integration, name the **boundary** it crosses (which system / context
  to which) and pick the **message type** deliberately: a **Command Message**
  invokes behavior, a **Document Message** transfers data, an **Event Message**
  announces a fact. Record the choice — a consumer must not treat an event as a
  command it owns the follow-up to.
- Choose the **channel semantics** explicitly: **Point-to-Point** (work done
  once by one consumer) vs **Publish-Subscribe** (a fact fanned out to many).
  Do not inherit the broker's default by accident.
- State the **delivery guarantee** the design assumes. Default to
  **at-least-once** unless the transport provably guarantees otherwise; where
  loss is unacceptable, require **Guaranteed Delivery** (persisted messages).
- Define the **failure destinations** up front: a **Dead Letter Channel** for
  undeliverable / poison messages and (where the receiver can be handed
  malformed input) an **Invalid Message Channel** for unprocessable content,
  with a retry cap before dead-lettering.
- A material uncertainty about the transport (unknown/changing broker API, cost,
  delivery/ordering semantics, credentials) is a `tech-spike` to de-risk before
  committing the design — not a silent assumption (see
  `workflows/references/concern-resolution.md`).

## Implementation

- Hide the broker behind a **Messaging Gateway**: domain/application code calls a
  domain-shaped publish/handle interface, never the broker SDK directly. The
  concrete client is an outer-ring adapter (`onion-architecture`).
- Put routing in **routers** (Content-Based Router, Message Filter, Recipient
  List), not in the sender. The sender publishes to a channel; it does not know
  its consumers.
- Use **Splitter / Aggregator / Resequencer** for composite or ordered flows,
  and a **Process Manager** (or **Routing Slip**) for a multi-step orchestration
  whose state and branching a single message cannot carry.
- Transform at the boundary: **Envelope Wrapper** for transport headers,
  **Content Enricher** to add missing fields, **Content Filter** to drop fields
  the receiver should not get, **Normalizer** to fold many incoming formats into
  one canonical shape.

## MUST

- **Every async consumer that mutates state is idempotent** (Idempotent
  Receiver) — replaying the same message does **not** double-apply (no double
  charge, double send, double insert). Idempotency is achieved by explicit
  de-duplication (a processed-message key) or by semantically idempotent
  operations, and is verified by replaying a delivered message and observing one
  effect.
- **A poison / undeliverable message goes to a Dead Letter Channel** — never
  silently dropped and never retried infinitely. Retries are capped; on
  exhaustion the message is dead-lettered with enough context to diagnose it.
- **A malformed / unprocessable message is quarantined** on an Invalid Message
  Channel (or dead-lettered) rather than crashing the consumer or poisoning the
  main channel.
- **Every message carries a Correlation Identifier** so a reply matches its
  request and a single logical flow is traceable across every hop. The
  correlation id is propagated, not regenerated, at each hop.
- **Application/domain code does not import the broker SDK** — it depends on a
  Messaging Gateway interface; the broker client lives in the outer ring.
- **Channel delivery semantics are explicit** — point-to-point vs
  publish-subscribe is a recorded choice, and the assumed delivery guarantee
  (at-least-once / guaranteed) is stated, not implied.
- **The sender does not hardcode its consumers** — routing lives in a router or
  the channel topology, so adding a consumer does not change the sender.

## SHOULD

- **Prefer Guaranteed Delivery where message loss is unacceptable** — persist
  messages so a broker crash does not lose them, rather than relying on
  best-effort in-memory transport.
- **Use Competing Consumers for throughput** on a point-to-point channel, and a
  **Resequencer** when order matters but parallel/competing consumption can
  scramble it — do not assume order on a parallel channel.
- **Use a Transactional Client** when consume-and-act must commit or roll back
  together (a crash mid-process must not lose or double-apply the work).
- **Add a Wire Tap / Message Store** for auditability of high-value flows, and a
  **Control Bus** to manage/monitor the running messaging system, rather than
  bolting observability on after an incident.
- **Choose the message type to match intent** — emit an Event Message for a fact
  others may react to (keeping systems independent), a Command Message only when
  you genuinely intend to invoke behavior on a specific receiver.
- **Carry the correlation id into traces/logs** (compose with `o11y-otel`) so the
  message flow and the distributed trace line up.

## Boundary with neighbors

See `concern.md` for the canonical Boundary (vs `domain-driven-design`,
`onion-architecture`, `design-patterns-gof`). EIP owns the at-least-once
channel-delivery model that *causes* the redelivery downstream consumers must
absorb — `concurrency-model` (in-process workers), `event-sourcing` (event
handlers), and `cqrs` (projection updaters) each apply the resulting
idempotency requirement at their own surface; this concern does not restate
their application of it.

## Quality Gates

- Every state-mutating async consumer is idempotent, verified by a **replay
  test**: delivering the same message twice yields exactly one effect.
- A Dead Letter Channel exists and is reached on retry exhaustion; a poison
  message is observably dead-lettered (not dropped, not infinitely retried),
  verified by feeding a failing message and observing it land in the DLC.
- Malformed input is quarantined (Invalid Message Channel / dead-lettered)
  without crashing the consumer, verified by feeding a malformed message.
- Messages carry a propagated Correlation Identifier; a single flow is traceable
  end-to-end across hops from message metadata (or correlated traces).
- No domain/application module imports the broker SDK — messaging is behind a
  Messaging Gateway (grep/import-graph check).
- Channel semantics (point-to-point vs pub-sub) and the assumed delivery
  guarantee are recorded for each integration.
