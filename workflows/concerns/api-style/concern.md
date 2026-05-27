# Concern: API Style

## Category
architecture

## Areas
api

## Boundary

This concern owns **the synchronous request/response interface style a service
EXPOSES** — how a caller and a service exchange information in a single
client-initiated, response-awaited call, and which interface paradigm carries
that exchange: **REST** (resource-oriented over HTTP semantics), **GraphQL**
(client-specified queries against one schema endpoint), **gRPC**
(contract-first protobuf over HTTP/2, with streaming), **RPC-style /
server-actions** (typed procedure calls — tRPC, Next.js server actions — for a
same-repo first-party client), or **MCP** (the Model Context Protocol — the
**agent-facing** style that exposes tools, resources, and prompts to an LLM
client over JSON-RPC 2.0, the AI-client analog of REST-for-humans and
gRPC-for-services). It owns the contract shape, the error shape, the
versioning/typing of that contract, where input is validated, and the
cacheability of responses. It is a **decision-guide**: it picks the style on
selection signals and holds the chosen style to its standard shape. When the
chosen style is MCP, the **MCP-specific** discipline — tool/resource/prompt
modeling, description quality, transport + OAuth, and the agent-exposure threat
surface (prompt injection, tool poisoning, confused-deputy, token passthrough,
human-in-the-loop for destructive tools) — is owned by **`mcp-server`**; this
concern only places MCP among the styles and names when to pick it. Three
neighbors must stay distinct:

- **`enterprise-integration-patterns`** owns **asynchronous messaging BETWEEN
  systems** — channels, routers, delivery guarantees, dead-letter paths, where
  sender and receiver are decoupled in space and time over a broker. This
  concern owns the **synchronous request/response interface a service exposes**:
  one caller, one call, one awaited response, no broker between them. The line
  is load-bearing: a queue/topic/webhook-ingest is EIP; an HTTP/RPC endpoint a
  client calls and blocks on is api-style. A single product commonly has both (a
  REST API at the edge **and** a message queue inside) — they compose, they do
  not overlap. Do **not** restate channel/router/delivery-guarantee rules here.
- **`onion-architecture`** owns the **layering within one deployable** —
  dependencies point inward, infrastructure is the outer ring. The API is an
  **outer-ring delivery adapter**: the controller/resolver/handler/procedure
  translates a wire request into a call on an inner application service and
  translates the result back out. api-style says *what the wire contract and
  error shape are*; onion says *the handler is outer-ring code that depends
  inward on the application service, never the reverse*. Do **not** restate the
  dependency rule — reference onion for the arrangement.
- **`domain-driven-design`** owns the **domain model** — aggregates, value
  objects, invariants, the ubiquitous language. The API is a **translation
  layer OVER the domain, not the domain itself**: REST resources / GraphQL
  types / protobuf messages / RPC DTOs are the **wire representation** a client
  sees, deliberately decoupled from the internal aggregate so the domain can
  evolve without breaking the contract (and the contract can evolve without
  reshaping the domain). Do **not** let wire types become the domain model, and
  do **not** restate aggregate/invariant rules here — defer to DDD.

## Components

- **Interface paradigm** — the chosen style: REST, GraphQL, gRPC,
  RPC/server-actions, or **MCP** (the agent-facing style). One style per exposed
  surface (a product may expose more than one surface — see the hybrid note in
  *When to use*).
- **Contract / schema** — the typed, versioned description of the interface: an
  OpenAPI spec for REST, a GraphQL schema (SDL), a protobuf `.proto`, the
  inferred-or-declared procedure types for RPC, or for **MCP** the
  **JSON-Schema-typed tool definitions** (resources and prompts are
  metadata/argument models, not JSON-Schema in the same way) discovered over the
  protocol (`tools/list`, `resources/list`, `prompts/list`) — where a tool's
  **description** is part of the contract because it is the model's only
  affordance for deciding when to call it. The contract is the source of truth a
  client codes against, not the implementation.
- **Resource / operation surface** — REST **resources** addressed by URI and
  acted on with HTTP verbs; GraphQL **queries/mutations/subscriptions** against
  one endpoint; gRPC **service methods** (unary + the three streaming modes);
  RPC **procedures** grouped into routers; **MCP** **tools** (model-invoked
  functions), **resources** (app-controlled context data addressed by URI), and
  **prompts** (user-invoked templates) exchanged as JSON-RPC methods.
- **Error shape** — the style's standard failure representation: HTTP **status
  codes** (REST/RPC-over-HTTP), the GraphQL **`errors` array** in an otherwise
  `200` body, gRPC **status codes**, the **JSON-RPC 2.0 `error` object** (and,
  for MCP tool execution, the `isError` result flag). Consistent and
  machine-readable, never an ad-hoc `{ "ok": false }` smuggled into a `200`.
- **Boundary validation** — the point where untrusted input is validated and
  coerced into typed, trusted values before it reaches the application service
  (request-body/param validation, schema-typed inputs, protobuf message
  validation, Zod-validated procedure inputs).
- **Cacheability surface** — whether and how responses are cacheable: REST's
  HTTP cache semantics (verbs, status, cache headers, ETags) are a first-class
  advantage; GraphQL (single POST endpoint) and gRPC (binary HTTP/2) forgo HTTP
  caching and cache at the field/application layer instead.
- **Versioning/evolution strategy** — how the contract changes without breaking
  clients: REST versioned paths/media types, GraphQL **additive evolution +
  field deprecation** (avoid endpoint versioning), protobuf **field-number
  back/forward compatibility**, RPC procedure additive change with shared types.

## Constraints

### One style per exposed surface, chosen on selection signals

- The interface paradigm for a given exposed surface is a **deliberate, recorded
  choice**, driven by the selection signals below — not inherited from a tutorial
  or the first framework reached for. A product MAY expose more than one surface
  (a public REST/GraphQL edge **and** internal gRPC between services **and** an
  MCP surface for AI agents); each surface picks its own style for its own
  consumer. Do not run two styles over the **same** surface for the same client.
  When the consumer is an **LLM agent / AI client** consuming exposed tools,
  data, or prompts for autonomous use, the style is **MCP** (and its
  MCP-specific discipline is `mcp-server`'s).

### The contract is typed and versioned; clients code against it, not the implementation

- Every exposed surface has an **explicit, typed contract** (OpenAPI / GraphQL
  schema / `.proto` / inferred-or-declared RPC types) that is the source of
  truth. Clients depend on the contract, not on implementation internals.
- The contract **evolves without breaking existing clients**: additive change +
  deprecation (GraphQL), back/forward-compatible field numbers (protobuf),
  versioned paths/media types (REST), or additive procedures with shared types
  (RPC). A breaking change is a versioned/communicated event, never a silent
  reshape.

### Input is validated at the boundary

- Untrusted input is **validated and coerced at the API boundary** into typed,
  trusted values **before** it reaches the application service. The inner layers
  receive validated domain inputs, not raw request payloads. (How invariants are
  enforced inside the domain is `domain-driven-design`'s; this concern guarantees
  the wire input is checked at the seam.)

### Errors use the style's standard shape

- Failures are returned in the **style's standard, machine-readable shape**: HTTP
  **status codes** for REST/RPC-over-HTTP (4xx client / 5xx server, not `200`
  with an error body), the GraphQL **`errors` array**, gRPC **status codes**.
  Error shape is **consistent across the surface**, so a client handles failure
  uniformly.

### The wire contract is a translation over the domain, not the domain

- Wire types (REST resources, GraphQL types, protobuf messages, RPC DTOs) are a
  **representation for clients**, mapped to/from the domain model at the boundary.
  The internal aggregate is **not** serialized directly onto the wire, and the
  wire shape is **not** treated as the domain. This decoupling is what lets the
  contract and the domain evolve independently (it composes with
  `onion-architecture`'s boundary-DTO rule and `domain-driven-design`'s model).

### Match HTTP semantics when the style is HTTP-resource-oriented

- For REST, **HTTP verbs carry method semantics** (GET safe + cacheable, PUT/DELETE
  idempotent, POST for non-idempotent creation) and **status codes carry outcome**
  — Richardson **Level 2** at minimum. HTTP is not a dumb tunnel for a single
  `POST /api` RPC (that is Level 0). Cacheability and idempotency are **derived
  from** honoring these semantics, not bolted on.

### Streaming and transport are chosen for the interaction, not the default

- A **streaming** interaction (server push, long-lived bidirectional exchange,
  high-throughput internal calls) is a deliberate reason to choose **gRPC** (its
  four method kinds) — not something to fake over request/response polling.
  Conversely, **browser reach and HTTP caching** are deliberate reasons NOT to
  choose gRPC at a public/web edge (binary HTTP/2 is poorly browser- and
  cache-friendly).

## Drift Signals (anti-patterns to reject in review)

- A single `POST /api` (or one verb for everything) tunneling RPC over HTTP while
  calling itself REST → Richardson **Level 0**; use real resources + verbs +
  status codes (Level 2), or pick an honest RPC/GraphQL style
- An error returned as **`200 OK` with `{ "error": ... }`** (REST/RPC-over-HTTP)
  → use the correct HTTP **status code**; reserve the GraphQL `errors` array for
  GraphQL
- Inconsistent/ad-hoc error shapes across one surface → standardize on the
  style's error shape so clients handle failure uniformly
- The internal **aggregate/ORM row serialized directly** onto the wire → map to a
  wire DTO/resource at the boundary; the contract is a translation over the domain
- **No typed/versioned contract** (hand-rolled JSON with no OpenAPI/schema/proto)
  → publish the contract clients code against
- A **breaking change shipped silently** (field removed/retyped, resource moved)
  → version or deprecate; never reshape an in-use contract in place
- **Raw request payloads passed unvalidated** into the application service →
  validate and coerce at the boundary first
- **GraphQL resolvers issuing per-item queries** with no batching → the **N+1
  problem**; batch with a DataLoader (or equivalent)
- **GraphQL or gRPC chosen reflexively for a thin first-party CRUD web app** with
  one client and no flexible-fetch / streaming need → over-engineering; REST (or
  same-repo RPC/server-actions) is the simpler correct default
- **gRPC exposed directly to a browser / public partners** as the public edge →
  binary HTTP/2 is poor for browser reach and HTTP caching; keep gRPC internal and
  put REST/GraphQL at the edge
- **Two API styles over the same surface for the same client** → pick one per
  surface; do not maintain parallel paradigms for one consumer
- A **human/service REST or gRPC API hand-wrapped as "agent tools"** with no MCP
  contract (bespoke function-calling glue per client) when the consumer is an LLM
  agent → expose an **MCP** surface (standard tool/resource/prompt discovery);
  see `mcp-server`
- An **MCP surface treated as just another REST endpoint** — tools with terse or
  missing descriptions (the model's only affordance), destructive tools with no
  human-in-the-loop, or upstream tokens passed straight through → these are
  `mcp-server`'s MCP-specific failures; defer the agent-exposure discipline there

## When to use

**Select for every product that EXPOSES a synchronous request/response interface**
— any web/service API a client calls and awaits. It is a **non-exclusive,
composable decision-guide** concern (no slot): rather than one style winning the
project, it **recommends a default and names when each alternative wins**, and a
product MAY expose more than one surface (each picking its own style). It does
**not** apply to a product whose only inter-system communication is asynchronous
messaging (that is `enterprise-integration-patterns`) or a single-process
library/CLI with no exposed interface.

**Default stance — REST (or same-repo RPC/server-actions for a first-party web
client).**

> **Default to REST** for a public or partner-facing API, for resource-oriented
> CRUD, and wherever broad client reach and HTTP caching matter — it is
> resource-oriented over standard HTTP semantics (Richardson Level 2+), universally
> reachable, and cacheable for free. **For a first-party web client in the same
> repo/monorepo** (e.g. a Next.js app talking to its own backend) where there is
> no third-party consumer, **a typed RPC/server-actions style (tRPC, Next.js
> server actions)** is the simpler default — end-to-end type safety with no
> separate contract artifact. **Choose GraphQL** when many heterogeneous clients
> need *flexible, client-specified* data shapes from a shared backend and
> over-fetching / under-fetching or client-driven round-trips are a real, present
> cost (a data-intensive aggregating BFF for varied frontends) — accept its
> single-endpoint HTTP-caching loss and the N+1/resolver discipline it demands.
> **Choose gRPC** for *internal* service-to-service communication where you
> control both ends and want a strict protobuf contract, low-latency binary
> transport, and first-class streaming — not for a browser-facing or
> broadly-public edge, where its weak browser reach and HTTP-cacheability rule it
> out. **Choose MCP** when the **consumer is an LLM agent / AI client** and you
> are exposing **tools, data, or prompts for autonomous use** — an AI-native
> product (or an existing product) making its capabilities consumable by
> assistants/agents over a standard protocol rather than bespoke per-client
> function-calling glue. MCP is the agent-facing surface; its MCP-specific
> contract, transport/auth, and especially the agent-exposure **security**
> discipline are owned by **`mcp-server`** (select it alongside api-style when
> the surface is MCP). **Do NOT** reach for GraphQL or gRPC on a thin
> single-client first-party CRUD app: that is cost without payoff (KISS/YAGNI);
> REST or same-repo RPC/server-actions is the right answer. Hybrids are
> legitimate — gRPC between backend services, GraphQL or REST as the BFF/edge,
> REST for public partners, **MCP for AI agents** — when each surface's signal
> genuinely differs.

`areas: api` scopes its practices to the API/service work items where the
interface lives. Compose with **`onion-architecture`** (the API handler is an
outer-ring adapter depending inward), **`domain-driven-design`** (the contract is
a translation over the domain model), **`enterprise-integration-patterns`** (the
*asynchronous* counterpart for cross-system messaging — distinct surface),
**`mcp-server`** (when the surface is **agent-facing**: the MCP-specific
tool/resource/prompt, transport/auth, and agent-exposure security discipline),
`security-owasp` (boundary input validation / authz on the exposed surface), and
the tech-stack concern (which fixes the HTTP/RPC framework and codegen).

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: interface style choice per surface (REST/GraphQL/gRPC/RPC/MCP) + versioning strategy
- TD: the API contract artifact (OpenAPI/GraphQL SDL/proto/RPC types), error shape, boundary validation, cacheability
- TEST_PLAN: contract conformance + boundary input-validation tests on the exposed surface

## ADR References

Record an ADR when selecting a non-default style for an exposed surface
(GraphQL or gRPC over the REST / same-repo-RPC default, MCP for an agent-facing
surface, or running multiple styles in a hybrid), naming the surface, its
consumers, and the decisive signal (public/partner reach + caching → REST;
flexible client-specified data across many clients → GraphQL; internal
service-to-service + streaming + strict contract → gRPC; first-party same-repo
client → RPC/server-actions; **LLM agent / AI client consuming exposed
tools/data/prompts → MCP**, also selecting `mcp-server`). A material
uncertainty about the interface (unknown client needs, streaming/transport
constraints, contract/versioning strategy) is a `tech-spike`, not a silent
assumption (see `workflows/references/concern-resolution.md`).
