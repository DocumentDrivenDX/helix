# Practices: API Style

These practices govern **the synchronous request/response interface a service
exposes** — choosing the interface style (REST / GraphQL / gRPC /
RPC-server-actions), shaping its contract and errors, validating input at the
boundary, and keeping the wire contract a translation over the domain. They do
**not** govern asynchronous cross-system messaging
(`enterprise-integration-patterns`), codebase layering (`onion-architecture`),
or the domain model itself (`domain-driven-design`); they reference those
concerns at the seam and stay on the exposed interface.

## Decide the style before building the surface

- Name the **exposed surface** and its **consumers** (public/partner clients, a
  first-party web client in the same repo, internal services you own both ends
  of), then pick the style on the decisive signal:
  - **REST** — public/partner API, resource-oriented CRUD, broad client reach,
    HTTP caching matters. **This is the default.**
  - **RPC / server-actions (tRPC, Next.js server actions)** — a first-party web
    client in the same repo/monorepo with no third-party consumer; the simpler
    default there (end-to-end type safety, no separate contract artifact).
  - **GraphQL** — many heterogeneous clients need flexible, client-specified
    data shapes from a shared backend and over/under-fetching is a real cost.
  - **gRPC** — internal service-to-service where you control both ends and want a
    strict protobuf contract, low-latency binary transport, and streaming.
  - **MCP** — the **consumer is an LLM agent / AI client** and you are exposing
    **tools, data, or prompts for autonomous use** (an AI-native product making
    its capabilities consumable by assistants/agents). MCP is the agent-facing
    surface; when you select it, also select **`mcp-server`** for the
    MCP-specific tool/resource/prompt, transport/OAuth, and agent-exposure
    security discipline this generic guide does not hold.
- Do **NOT** reach for GraphQL or gRPC on a thin single-client first-party CRUD
  app — cost without payoff (KISS/YAGNI). Record the choice (and any non-default
  selection) in an ADR.
- A product MAY expose **multiple surfaces** (gRPC internally, REST/GraphQL at
  the edge); pick one style **per surface** for its own reason. Do not run two
  styles over the **same** surface for the **same** client.
- A material uncertainty about the interface (unknown client needs, streaming /
  transport constraints, contract / versioning strategy) is a `tech-spike` to
  de-risk before committing — not a silent assumption (see
  `workflows/references/concern-resolution.md`).

## Define a typed, versioned contract

- Publish an **explicit, typed contract** that is the source of truth clients
  code against: an **OpenAPI** spec (REST), a **GraphQL schema (SDL)**, a
  **`.proto`** (gRPC), or declared/inferred **procedure types** (RPC). Clients
  depend on the contract, not on implementation internals.
- **Evolve without breaking existing clients**: additive change + field
  deprecation (GraphQL), back/forward-compatible field numbers — never reuse or
  renumber a field (protobuf), versioned paths/media types (REST), additive
  procedures with shared types (RPC). A breaking change is versioned and
  communicated, never a silent in-place reshape of an in-use contract.

## Shape REST around HTTP semantics (Richardson Level 2+)

- Address **resources by URI** and use **HTTP verbs for method semantics**: GET
  safe and cacheable, PUT/DELETE idempotent, POST for non-idempotent creation.
  Do **not** tunnel everything through one `POST /api` (Richardson Level 0).
- Carry outcome in **HTTP status codes** (2xx success, 4xx client error, 5xx
  server error) — not `200 OK` with an error body.

## Handle GraphQL's tradeoffs deliberately

- Serve one endpoint with **client-specified queries**; let clients request only
  the fields they need (this is the over/under-fetching win — do not re-add
  fixed endpoints that defeat it).
- **Batch resolver data access** with a **DataLoader** (or equivalent) to avoid
  the **N+1 problem** — a parent resolver returning N items MUST NOT trigger N
  per-item child queries.
- Return failures in the **`errors` array** of the response; do not invent a
  separate error channel. Accept that the single POST endpoint forgoes HTTP
  caching — cache at the field/application layer instead.

## Reserve gRPC for internal, contract-first, streaming use

- Define services and messages in a **`.proto`**; generate typed client/server
  stubs (`protoc`). Use the right **method kind** for the interaction: unary, or
  server- / client- / bidirectional-**streaming** when the exchange is genuinely
  long-lived or high-throughput — do not fake streaming with polling.
- Keep gRPC **internal / service-to-service**; do **not** expose it as the
  browser-facing or broadly-public edge (binary HTTP/2 is poor for browser reach
  and HTTP caching). Put REST/GraphQL at the edge and gRPC behind it.

## Validate input at the boundary

- **Validate and coerce untrusted input at the API boundary** into typed, trusted
  values **before** it reaches the application service (request body/param
  validation, schema-typed inputs, protobuf message checks, Zod-validated RPC
  inputs). The inner layers receive validated domain inputs, never raw payloads.
  (Authn/authz and the broader threat model are `security-owasp`'s; this concern
  guarantees the input is checked at the seam.)

## Keep the wire contract a translation over the domain

- Map between **wire types** (resources / GraphQL types / protobuf messages / RPC
  DTOs) and the **domain model at the boundary**. Do **not** serialize the
  internal aggregate or ORM row directly onto the wire, and do **not** treat the
  wire shape as the domain model.
- The API handler (controller / resolver / service method / procedure) is an
  **outer-ring adapter** (`onion-architecture`): it translates the wire request
  into a call on an inner application service and translates the result back —
  it does not contain domain logic.

## Boundary with neighbors

- **vs `enterprise-integration-patterns`**: api-style is the **synchronous
  request/response interface a service exposes** (one caller, one awaited
  response); EIP is **asynchronous messaging between systems** over a broker.
  A product may have both — a REST/GraphQL/gRPC surface **and** a queue — but do
  not conflate an exposed endpoint with a message channel.
- **vs `onion-architecture`**: the API handler is **outer-ring** and depends
  inward on the application service; do not restate the dependency rule, do honor
  it (no domain logic in the handler, no inward dependency on the handler).
- **vs `domain-driven-design`**: the contract is a **translation over** the
  domain, decoupled so each can evolve; do not let wire types become the domain
  model, and defer aggregate/invariant rules to DDD.
- **vs `security-owasp`**: this concern requires input validation **exists** at
  the boundary; the threat model, authn/authz, and injection defenses are
  `security-owasp`'s — compose, do not restate.
- **vs `mcp-server`**: when the exposed surface is **agent-facing** (an LLM
  client consuming tools/resources/prompts), api-style only places MCP among the
  styles and names when to pick it; the MCP-specific contract (tool descriptions
  as the model's affordance), transport + OAuth, and agent-exposure security
  (prompt injection, tool poisoning, confused-deputy, token passthrough,
  human-in-the-loop for destructive tools) are `mcp-server`'s — compose, do not
  restate.

## Quality Gates

- The exposed surface has an **explicit, typed contract** (OpenAPI / GraphQL
  schema / `.proto` / declared-or-inferred RPC types) that clients code against,
  and its **style was chosen on a recorded signal** (non-default style →
  ADR-recorded).
- **Errors use the style's standard shape** — HTTP **status codes** for
  REST/RPC-over-HTTP (no `200 OK` with an error body), the GraphQL **`errors`
  array**, gRPC **status codes** — and the shape is **consistent across the
  surface**.
- **The contract is versioned/evolvable without breaking existing clients**
  (additive + deprecation / compatible field numbers / versioned paths) — no
  silent in-place reshape of an in-use contract.
- **Untrusted input is validated and coerced at the boundary** before reaching
  the application service; inner layers do not receive raw request payloads
  (verifiable at the handler/resolver/procedure seam).
- **REST surfaces use HTTP verbs + status codes semantically** (Richardson Level
  2+) — no single-`POST` tunnel calling itself REST; GET is safe/cacheable,
  PUT/DELETE idempotent.
- **GraphQL resolvers batch data access** (DataLoader or equivalent) — no N+1
  per-item query fan-out under a list resolver.
- **gRPC is internal, contract-first**, with the right method kind for the
  interaction; it is **not** the browser-facing/public edge (REST/GraphQL is).
- **Wire types are a translation over the domain** — the internal aggregate/ORM
  row is not serialized directly onto the wire; the handler is an outer-ring
  adapter with no domain logic.
- **One style per surface for a given client** — no two paradigms maintained over
  the same surface for the same consumer; and a thin single-client first-party
  CRUD app uses REST or same-repo RPC/server-actions, not GraphQL/gRPC.
