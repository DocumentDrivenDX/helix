# Concern: Enterprise Integration Patterns

## Category
architecture

## Areas
api, infra

## Boundary

This concern owns **asynchronous messaging and integration ACROSS system and
context boundaries** — how independently-deployed applications, services, and
external systems exchange information over channels rather than in-process
calls. Its vocabulary is Hohpe & Woolf's *Enterprise Integration Patterns*:
messages, channels, routers, transformers, endpoints, and the system-management
patterns that operate the message flow. Three neighbors must stay distinct:

- **`domain-driven-design`** owns **what** propagates and **why** — domain
  events and eventual consistency *across aggregates inside a bounded context*.
  EIP owns the **transport that carries it across the boundary**. The
  distinction is load-bearing: a DDD **domain event** lives **inside** a
  bounded context (a named record of something that happened in the domain,
  used to reconcile aggregates that a single transaction must not span); an EIP
  **Event Message** is that fact **serialized onto a Message Channel that
  crosses a context or system boundary**. DDD decides the fact and the
  invariant it reconciles; EIP decides the channel, the delivery guarantee, and
  the wire shape. Do **not** restate aggregate/invariant/eventual-consistency
  modeling rules here.
- **`onion-architecture`** owns the **layering within one deployable** —
  dependencies point inward, infrastructure is the outer ring. Messaging
  clients, channel adapters, gateways, and consumers are **outer-ring code**
  under Onion's dependency rule: the inner layers declare the port (a publish
  or a handle-message interface in domain terms), and the EIP adapter in the
  outer ring implements it against the broker. EIP says *what* that adapter is
  (a Messaging Gateway, an Idempotent Receiver); Onion says *where it sits and
  which way it depends*. Do **not** restate the dependency rule here.
- **`design-patterns-gof`** owns **intra-process object collaboration** —
  factory, strategy, observer, and the rest, all inside one address space. EIP
  is **cross-process, asynchronous, over a channel**. The trap to reject
  explicitly: **GoF Observer is not a substitute for a Message Channel.**
  Observer is an in-memory, synchronous, same-process notification with no
  durability, no delivery guarantee, no retry, and no dead-letter path; a
  Message Channel decouples sender and receiver across process and time and is
  what you reach for when the boundary is a real system boundary. Name the EIP
  pattern; leave intra-process mechanics to that concern.

## Components

EIP is organized around six **root patterns** and six **pattern categories**.
The root patterns are the spine: a **Message** travels over a **Message
Channel**; **Pipes and Filters** compose processing stages; a **Message
Router** chooses the next channel; a **Message Translator** changes the
message's shape; a **Message Endpoint** is how an application connects to the
channel. The categories below refine those roots.

### Channels — how messages travel
The transport positions: **Point-to-Point Channel** (exactly one consumer
receives each message), **Publish-Subscribe Channel** (every subscriber gets a
copy), **Dead Letter Channel** (where a message the system cannot *deliver*
goes, so it is never silently lost), **Invalid Message Channel** (where a
message the receiver cannot *process* — malformed, nonsensical — goes, kept off
the production channel), **Guaranteed Delivery** (messages persisted to disk so
a broker crash does not lose them).

### Message Construction — what a message means
**Command Message** (tells the receiver what to do), **Document Message**
(passes data without prescribing action), **Event Message** (notifies of a fact
without telling the receiver how to react), **Correlation Identifier** (matches
a reply to its request / traces a message across hops), **Return Address**
(tells the replier which channel to answer on).

### Routing — choosing the next channel without coupling the sender
**Content-Based Router** (route by inspecting content), **Message Filter** (pass
only messages matching criteria), **Splitter** (break one composite message into
many), **Aggregator** (combine related messages into one), **Resequencer** (put
out-of-order messages back in order), **Routing Slip** (attach the ordered list
of steps a message must visit), **Process Manager** (stateful orchestration of a
multi-step flow with branching).

### Transformation — changing shape across the boundary
**Envelope Wrapper** (wrap the payload in infrastructure-required headers, unwrap
on the far side), **Content Enricher** (add data the source could not supply),
**Content Filter** (remove fields the receiver should not see / need),
**Normalizer** (translate many incoming formats into one common format).

### Endpoints — how an application connects to the channel
**Messaging Gateway** (encapsulate messaging behind a domain interface so the app
is unaware of the broker), **Idempotent Receiver** (safely handle the same
message more than once), **Competing Consumers** (multiple consumers drain one
channel in parallel for throughput), **Message Dispatcher** (one consumer
receives and delegates to performers, controlling concurrency), **Transactional
Client** (the endpoint participates in a transaction so consume-and-act commit or
roll back together).

### System Management — operating the message flow
**Control Bus** (a side channel to manage and monitor the running system),
**Detour** (route through extra steps — validation, logging — that can be toggled),
**Wire Tap** (copy traffic to an inspection channel without disturbing the flow),
**Message Store** (persist a record of messages for audit and analysis).

### Compact intent table

| Pattern | Intent | Applies when |
|---------|--------|--------------|
| Message Channel | A logical pipe a sender writes and a receiver reads, decoupling them in space and time | Two systems must communicate without a synchronous in-process call |
| Point-to-Point Channel | Exactly one consumer receives each message | A message represents work that must be done once |
| Publish-Subscribe Channel | Every subscriber receives a copy of each message | A fact must fan out to many independent consumers |
| Dead Letter Channel | Undeliverable messages are moved aside, not lost | Delivery fails / retries are exhausted (a poison message) |
| Invalid Message Channel | Messages the receiver cannot process are quarantined off the main channel | A message is malformed or semantically nonsensical |
| Guaranteed Delivery | Messages are persisted so a broker crash does not lose them | Message loss is unacceptable |
| Command Message | Tell the receiver what operation to run | You are invoking behavior on another system |
| Document Message | Pass data without prescribing what to do with it | You are transferring a data structure / a reply payload |
| Event Message | Notify of a fact without dictating a reaction | You are announcing a state change to whoever cares |
| Correlation Identifier | A field linking a message to its request / trace | Replies must be matched, or a flow traced across hops |
| Return Address | The channel the replier should answer on | Request-reply where the responder must not hardcode the reply channel |
| Content-Based Router | Route by inspecting message content | The destination depends on the message, and the sender must not know it |
| Message Filter | Forward only messages matching criteria | A consumer cares about a subset of a channel's traffic |
| Splitter | Break one composite message into many | A batch/list must be processed element-by-element |
| Aggregator | Combine related messages into one | Split or scattered results must be reassembled |
| Resequencer | Reorder out-of-sequence messages | Order matters but parallel processing scrambled it |
| Routing Slip | Attach the ordered steps a message must visit | A message needs a known sequence of processing stages |
| Process Manager | Stateful orchestration of a multi-step, branching flow | The flow has state and decisions between steps a slip cannot express |
| Envelope Wrapper | Wrap payload in transport-required headers, unwrap after | The infrastructure imposes a message envelope the payload must conform to |
| Content Enricher | Add data the source could not supply | The receiver needs fields missing from the source message |
| Content Filter | Remove fields the receiver should not need or see | A message carries more than the receiver should get |
| Normalizer | Translate many incoming formats into one canonical format | Multiple sources send the same concept in different shapes |
| Messaging Gateway | Hide messaging behind a domain interface | App code should not depend on the broker API |
| Idempotent Receiver | Process the same message any number of times with one effect | At-least-once delivery means duplicates and replays will happen |
| Competing Consumers | Many consumers drain one channel concurrently | Throughput requires parallel processing of a point-to-point channel |
| Message Dispatcher | One consumer delegates work to performers, controlling concurrency | You must control message-to-worker assignment explicitly |
| Transactional Client | Consume-and-act commit or roll back as one unit | Losing or double-applying on a crash mid-process is unacceptable |
| Control Bus | A side channel to manage and monitor the flow | Operators must observe/command the running messaging system |
| Detour | Route through toggleable extra steps | Validation/logging must be insertable without redesign |
| Wire Tap | Copy traffic to an inspection channel | You must observe messages without disturbing the flow |
| Message Store | Persist a record of messages for audit/analysis | You need history without coupling components |

## Constraints

### Channels decouple — do not reintroduce synchronous coupling
- Communication across a system/context boundary goes over a **Message Channel**;
  it is not a disguised synchronous, in-process call. A GoF **Observer** (in-memory,
  same-process, no durability, no delivery guarantee) is **not** a substitute for a
  channel — when the boundary is real, use a channel.
- A channel's delivery semantics are **explicit**: point-to-point (one consumer)
  vs publish-subscribe (fan-out) is a deliberate choice, not an accident of the
  broker's default.

### At-least-once delivery is the default reality — design for duplicates
- Treat delivery as **at-least-once** unless the transport provably guarantees
  otherwise. Duplicates and replays *will* occur (redelivery after a crash,
  lowered quality-of-service, retried sends). Every consumer that mutates state
  must therefore be an **Idempotent Receiver**: reprocessing the same message
  produces the same effect, never a double-apply.
- Where loss is unacceptable, use **Guaranteed Delivery** (persisted messages)
  rather than relying on best-effort in-memory transport.

### Failed and invalid messages have a destination — never a silent drop
- A message the system **cannot deliver** (retries exhausted, poison message)
  goes to a **Dead Letter Channel**; a message the receiver **cannot process**
  (malformed, nonsensical) goes to an **Invalid Message Channel**. The
  distinction is delivery-failure vs content-failure.
- Neither is silently discarded, and neither is retried forever. Infinite retry
  of a poison message is a defect; so is swallowing a failed message with no
  trace.

### Messages are traceable across hops
- Messages carry a **Correlation Identifier** so a reply can be matched to its
  request and a single logical flow can be **traced across every hop** it
  traverses. A flow that cannot be reconstructed from message metadata is a
  diagnosability gap.

### Senders are decoupled from destinations
- Routing decisions live in **routers** (Content-Based Router, Message Filter,
  Recipient List), not in the sender. A sender that hardcodes its consumers'
  identities has reintroduced the coupling the channel was meant to remove.

### The app is shielded from the broker
- Application/domain code talks to a **Messaging Gateway** (a domain-shaped
  interface), not to the broker SDK directly. The broker is an outer-ring detail
  (`onion-architecture`); swapping SQS for Kafka must not ripple into the domain.

### Endpoints are the right type for the message
- **Command / Document / Event** messages are chosen deliberately: a command
  invokes behavior, a document transfers data, an event announces a fact. A
  consumer reacting to an "event" as if it were a command (assuming it owns the
  follow-up action) couples systems that should stay independent.

## Drift Signals (anti-patterns to reject in review)

- A consumer that mutates state but is not idempotent (a replay double-charges,
  double-sends, double-inserts) → make it an **Idempotent Receiver**
- A failed/poison message that is silently dropped, or retried forever with no
  cap → route it to a **Dead Letter Channel**; quarantine malformed input on an
  **Invalid Message Channel**
- Messages with no correlation/trace id, so a flow cannot be reconstructed
  across hops → add a **Correlation Identifier**
- Domain/application code importing the broker SDK directly → hide it behind a
  **Messaging Gateway** (outer-ring adapter under `onion-architecture`)
- A GoF Observer / in-process event bus standing in for cross-system
  integration → use a real **Message Channel** with explicit delivery semantics
- A sender that hardcodes which consumers receive its messages → move the
  decision into a **router**; publish to a channel
- "Exactly-once" assumed from an at-least-once transport → design for duplicates
  (idempotency) rather than assuming they cannot happen
- Order assumed on a parallel/competing-consumer channel with no **Resequencer**
  where order is actually required → make the ordering need explicit
- A multi-step cross-system flow hand-coded with no **Process Manager** /
  **Routing Slip**, leaving its state untracked → model the orchestration

## When to use

Select for any product with **asynchronous messaging or cross-system
integration**: message queues, publish-subscribe / event buses, **event
ingestion or webhooks** (e.g. ingesting SES open/click/bounce events),
**scheduled or queued delivery** (e.g. a priority send queue), background job
processing, or **integration across services or third-party systems** (e.g.
wiring in an external optimizer). A platform that ingests provider events,
schedules delivery through a queue, and integrates a third-party service is a
**strong** fit.

Do **not** select it for a **thin synchronous CRUD app**, a purely in-process
application with no queue / broker / external integration, a static/marketing
site, or a single-process library. There the channel/router/endpoint machinery
is cost without payoff (KISS/YAGNI) — an in-process function call is not an
integration boundary.

It is composable (no slot); `areas: api, infra` scopes its practices to the
service and infrastructure work items where messaging lives. Compose with
**`domain-driven-design`** (which decides the domain events/facts the messages
carry), **`onion-architecture`** (under which messaging adapters are outer-ring
code), the tech-stack concern (which fixes the broker client/library), and
`o11y-otel` (which carries the correlation id into traces).

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: broker/transport + delivery guarantee (at-least-once/exactly-once, persistence, ordering)
- TD: channels, routers, messaging gateway, idempotent receiver, dead-letter/invalid paths
- TEST_PLAN: idempotent-receiver test (replay applies once) + poison-message dead-letter path

## ADR References

Record an ADR when choosing the broker/transport and its delivery guarantee
(at-least-once vs exactly-once, persistence, ordering), since those are the
design-defining decisions for an integration. A material uncertainty about the
transport (unknown API, cost, delivery semantics, ordering) is a `tech-spike`,
not a silent assumption (see `workflows/references/concern-resolution.md`).
