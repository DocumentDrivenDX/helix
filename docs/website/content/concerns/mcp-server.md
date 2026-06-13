---
title: "MCP Server"
slug: mcp-server
generated: true
aliases:
  - /reference/glossary/concerns/mcp-server
---

**Category:** Architecture · **Areas:** api

## Description

## Category
architecture

## Areas
api

## Boundary

This concern owns **the agent-facing interface a product exposes to LLM clients
via the Model Context Protocol (MCP)** — the open standard ("USB-C for AI") for
connecting AI applications and agents to external tools, data, and prompts over
**JSON-RPC 2.0**. It owns how a product models and exposes its three MCP
primitives — **tools** (model-invoked functions), **resources**
(application-controlled context data), **prompts** (user-invoked templates) — the
tool **schema + description discipline** (a tool's description is the model's
only affordance for deciding when and how to call it), the **transport** (stdio
vs Streamable HTTP) and its **OAuth 2.1 authorization**, and — most critically —
the **agent-exposure security surface**: the threats that arise specifically
because an autonomous model, not a human, is driving the calls (prompt
injection, tool poisoning / rug-pulls, confused-deputy, token passthrough,
over-broad tool scopes), and the human-in-the-loop and least-privilege controls
that contain them. Four neighbors must stay distinct:

- **`api-style`** owns the **interface-style decision and the human-/service-
  facing styles** (REST / GraphQL / gRPC / RPC-server-actions) and *places MCP
  among them* as the agent-facing option, naming when to pick it. This concern
  owns **what MCP-specific discipline applies once MCP is chosen** — the
  tool/resource/prompt modeling, transport/auth, and agent-exposure security
  that a generic style guide cannot hold. The line is load-bearing: a request a
  **human or another service** initiates and awaits is api-style (REST/gRPC); a
  surface an **LLM agent autonomously discovers and invokes** over JSON-RPC
  tools/resources/prompts is MCP. A product MAY expose both (a REST edge for
  humans **and** an MCP surface for agents) — they compose. Do **not** restate
  the style-selection decision-guide here; defer it to `api-style`.
- **`enterprise-integration-patterns`** owns **asynchronous messaging between
  systems** — channels, routers, delivery guarantees, dead-letter paths, sender
  and receiver decoupled over a broker. MCP is a **synchronous tool/resource
  interface** an agent calls and awaits (a `tools/call` blocks on its result),
  **not** an async message channel. A tool whose effect is to *enqueue* work
  onto a channel is the seam: the MCP `tools/call` is this concern; the channel
  it writes to is EIP. Do **not** restate channel/delivery-guarantee rules here.
- **`security-owasp`** owns the **general application threat model** — the OWASP
  Top 10, injection, broken access control, secret management, TLS at the
  boundary. This concern owns the **agent-specific threats MCP adds on top**:
  tool poisoning and rug-pulls (the tool metadata the model trusts is itself an
  injection vector), confused-deputy via OAuth proxy + dynamic registration,
  token passthrough to downstream APIs, and over-broad tool scopes that widen an
  agent's blast radius. Compose with `security-owasp` for the baseline; do
  **not** restate the OWASP Top 10 — add the agent-exposure layer.
- **`auth` / `auth-local-sessions`** own the product's **own user
  authentication**. This concern owns the **OAuth 2.1 authorization for the MCP
  HTTP transport specifically** — the MCP server as an OAuth 2.1 *resource
  server*, RFC 9728 protected-resource metadata, RFC 8707 resource-indicator
  audience binding, and the prohibition on token passthrough. Defer the
  product's human login to the auth concern; own the agent-token boundary here.

## Components

- **Tools** — **model-invoked** functions the LLM may call autonomously, each a
  single operation with a **JSON-Schema-typed input** and a **natural-language
  description**. Discovered via `tools/list`, executed via `tools/call`. The
  description is part of the contract: it is the model's *only* affordance for
  deciding when to invoke the tool, so it must be precise, scoped, and honest.
  Tools represent arbitrary effects (write a DB, call an API, modify a file) and
  are the primary security surface.
- **Resources** — **application-controlled** read-only context data addressed by
  **URI** (direct, e.g. `calendar://events/2026`, or templated, e.g.
  `weather://forecast/{city}`), declaring a MIME type. Discovered via
  `resources/list` / `resources/templates/list`, fetched via `resources/read`.
  The host application — not the model — decides which resources to pull into
  context; resources do not take actions.
- **Prompts** — **user-invoked** parameterized templates (surfaced as slash
  commands, command-palette entries, etc.) that scaffold a workflow combining
  tools and resources. Discovered via `prompts/list`, retrieved via
  `prompts/get`. User-controlled: explicitly invoked, never auto-triggered.
- **Transport** — **stdio** (the server runs as a local subprocess; JSON-RPC
  over stdin/stdout; credentials from the environment) or **Streamable HTTP**
  (a single MCP endpoint accepting POST/GET, optionally streaming via SSE, for
  remote/multi-client servers; replaces the deprecated HTTP+SSE transport).
  stdio is preferred where possible; HTTP is for remote exposure.
- **Authorization (HTTP transport)** — **OAuth 2.1**: the MCP server is an OAuth
  2.1 **resource server**; it publishes protected-resource metadata (RFC 9728),
  points clients at an authorization server, and **validates that every access
  token was issued specifically for it** (RFC 8707 resource-indicator / audience
  binding). PKCE, exact redirect-URI matching, and short-lived tokens apply.
  (stdio servers take credentials from the environment, not this flow.)
- **Capability negotiation** — the stateful `initialize` handshake where client
  and server declare which features (tools/resources/prompts; sampling/roots/
  elicitation) they support, so neither assumes an unsupported capability.
- **Error shape** — the **JSON-RPC 2.0 `error` object** for protocol errors, and
  the tool-result **`isError` flag** for tool execution failures the model
  should see and reason about — distinct from a transport/protocol fault.

## Constraints

### Model the primitive to its control surface — tool vs resource vs prompt

- Map each capability to the **right primitive by who controls it**: a
  **model-invoked action with effects** is a **tool**; **read-only context data
  the application supplies** is a **resource**; a **user-invoked workflow
  template** is a **prompt**. Do not expose a side-effecting action as a
  "resource" (resources are read-only), and do not force a passive data fetch
  through a tool the model must decide to call.
- Each tool is **one operation** with a **typed JSON-Schema input** and **typed
  output** — not a god-tool with a free-form `command` string the model fills in.

### A tool's description is the model's only affordance — write it as contract

- Every tool carries a **precise, honest, scoped description** stating what it
  does, when to use it, and what it does NOT do. The model selects tools on
  description text alone; a vague, misleading, or overloaded description is a
  correctness defect, not a docs nit.
- Tool descriptions/annotations are **untrusted input to the model**: never
  embed instructions in a description that try to steer the agent beyond
  describing the tool (and treat *consumed* third-party tool metadata as
  untrusted — see the tool-poisoning constraint).

### Destructive and high-impact tools require human-in-the-loop

- A tool with **irreversible or high-impact effect** (delete, send, pay,
  deploy, mutate external state) **MUST NOT** execute autonomously on the
  model's decision alone: require **explicit user confirmation** at invocation
  (a consent prompt the user sees before the effect happens). Read-only / safe
  tools may be pre-approved; destructive ones may not be silently auto-run.
- The user must be able to **see what each tool does before authorizing it**;
  tool execution is surfaced (approval dialog and/or activity log), not hidden.

### Validate tool inputs at the boundary; least-privilege tool scopes

- **Validate and coerce every tool input against its JSON Schema at the
  boundary** before acting — the caller is an LLM that can emit malformed,
  out-of-range, or adversarial arguments. Inner layers receive validated values,
  never raw model output. (Generic input-validation discipline composes with
  `api-style` / `security-owasp`; this concern requires it on the agent-driven
  tool seam specifically.)
- Apply **least privilege per tool**: a tool's effect and the credential/scope
  it runs under are the **minimum** for its job — no omnibus `*` / `full-access`
  scopes, no bundling unrelated privileges to "save a prompt later". A stolen
  token or a hijacked agent should have the smallest possible blast radius;
  prefer progressive, incremental scope elevation over up-front broad grants.

### Treat consumed tool metadata as untrusted — defend against poisoning & rug-pulls

- **Tool poisoning**: the descriptions/schemas of tools an agent consumes are a
  **prompt-injection / supply-chain surface** — hidden instructions in a tool
  description can hijack the agent. Where this product *aggregates or proxies*
  other MCP servers, treat their tool metadata as untrusted unless the server is
  trusted, and pin/verify it.
- **Rug-pull**: a tool's behavior or description can change *after* the user
  approved it. Detect and re-consent on **changed tool definitions**; do not
  silently honor a mutated tool the user approved in an earlier form.

### MCP HTTP authorization is OAuth 2.1 with audience binding — never pass tokens through

- An HTTP-transport MCP server is an **OAuth 2.1 resource server**: it
  **MUST validate that every inbound access token was issued specifically for
  it** (audience / RFC 8707 resource indicator) and reject tokens that name a
  different audience. PKCE and exact redirect-URI matching apply.
- **Token passthrough is forbidden**: the MCP server **MUST NOT** accept a token
  not issued to it, and **MUST NOT** forward the client's token unmodified to a
  downstream/upstream API — when it calls an upstream API it acts as that API's
  OAuth client with a **separate** token. Passthrough breaks audience
  validation, the audit trail, and the trust boundary (confused-deputy).
- An MCP **proxy** with a static client ID + dynamic client registration **MUST
  obtain per-client user consent** before forwarding to a third-party
  authorization server, or it is a **confused deputy** (a cached consent cookie
  lets an attacker skip the consent screen and steal the auth code).

### Bind the transport — localhost, Origin checks, secure sessions

- A **local** HTTP MCP server **SHOULD bind to localhost** (not `0.0.0.0`) and
  **validate the `Origin` header** to prevent **DNS-rebinding** attacks; a local
  stdio server limits access to its parent client by construction.
- **Sessions are not authentication**: an MCP server **MUST verify every inbound
  request's authorization** and **MUST NOT** treat a session ID as proof of
  identity. Session IDs are **non-deterministic / cryptographically random** and
  **SHOULD be bound to the user** (e.g. `<user_id>:<session_id>`) so a guessed
  session cannot impersonate another user.

## Drift Signals (anti-patterns to reject in review)

- A tool exposed with a **terse, vague, or missing description** (the model's
  only affordance) → write a precise, scoped, honest description as contract
- A **god-tool** taking a free-form `command`/`action` string instead of typed,
  single-purpose tools with JSON-Schema inputs → split into typed operations
- A **destructive tool that auto-executes** on the model's decision with no
  human-in-the-loop confirmation → gate irreversible/high-impact effects behind
  explicit user approval
- A **side-effecting action modeled as a "resource"**, or passive data forced
  through a tool the model must choose to call → match the primitive to its
  control surface (tool = action, resource = read-only context, prompt = template)
- **Raw model-supplied tool arguments acted on unvalidated** → validate/coerce
  against the JSON Schema at the boundary first
- **Omnibus / wildcard tool scopes** (`*`, `full-access`) or bundled unrelated
  privileges granted up front → least-privilege per tool, progressive elevation
- **Token passthrough** — accepting a token not issued to this server, or
  forwarding the client's token unmodified to a downstream API → validate
  audience; use a separate upstream token (confused-deputy risk)
- An MCP server **accepting tokens without audience validation** → MUST verify
  the token was issued for this server (RFC 8707)
- An **OAuth-proxy MCP server with static client ID + dynamic registration and
  no per-client consent** → confused deputy; require per-client consent before
  forwarding
- A local HTTP MCP server **bound to `0.0.0.0` with no `Origin` check** → bind
  localhost, validate Origin (DNS-rebinding)
- A **session ID treated as authentication**, or predictable/sequential session
  IDs → verify authorization per request; use random, user-bound session IDs
- **Consumed third-party tool metadata trusted blindly** (no defense against
  tool poisoning / rug-pull on change) → treat as untrusted; re-consent on
  changed tool definitions

## When to use

Select **whenever the product exposes capabilities to an LLM agent / AI client
over MCP** — an AI-native product (or an existing product) making its tools,
data, or prompts consumable by assistants/agents (Claude, ChatGPT, IDE agents,
custom agents) rather than via bespoke per-client function-calling glue. It is
the agent-facing companion to `api-style`: select **both** when the chosen
interface style for a surface is MCP — `api-style` places MCP among the styles
and records the selection; this concern holds the MCP-specific discipline.

It is **non-exclusive and composable** (no slot): a product commonly exposes a
human/service surface (REST/GraphQL/gRPC under `api-style`) **and** an MCP
surface for agents, and they compose. Do **not** select it for a product with no
agent-facing surface (a plain human/service API is `api-style` alone), or for a
single-process library/CLI that exposes nothing to an external LLM client.

`areas: api` scopes its practices to the API/service work items where the MCP
surface lives. Compose with **`api-style`** (the style-selection decision-guide
that places MCP), **`security-owasp`** (the baseline threat model this concern
adds the agent-exposure layer onto), **`enterprise-integration-patterns`** (the
*asynchronous* messaging counterpart — a tool may enqueue onto a channel, but
the channel is EIP's), **`auth`/`auth-local-sessions`** (the product's own user
login, distinct from the OAuth 2.1 agent-token boundary owned here), and the
tech-stack concern (which fixes the MCP SDK/server framework).

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: primitives exposed, transport (stdio/HTTP) + OAuth 2.1 audience binding, human-in-the-loop + least-privilege scope model
- TD: tool/resource/prompt modeling, JSON-Schema tool inputs + descriptions, boundary validation, agent-exposure threat controls
- FEAT: which capabilities are exposed as tools vs resources vs prompts to the agent
- TEST_PLAN: destructive-tool human-in-the-loop gate, token-audience validation, input-validation on agent args

## ADR References

Record an ADR when exposing an MCP surface: name the **primitives exposed**
(which tools/resources/prompts), the **transport** (stdio for local, Streamable
HTTP for remote) and — for HTTP — the **OAuth 2.1 authorization** design
(resource-server validation, audience binding, no passthrough), and the
**human-in-the-loop policy** for destructive tools and the **scope model**
(least-privilege per tool). A material uncertainty about the agent-exposure
surface (which capabilities are safe to expose autonomously, the auth/transport
choice, the proxy/aggregation trust model) is a `tech-spike`, not a silent
assumption (see `workflows/references/concern-resolution.md`).

## Practices by activity

Agents working in any of these activities inherit the practices below through runtime work context, such as a DDx bead context digest.

These practices govern **the agent-facing interface a product exposes to LLM
clients over the Model Context Protocol (MCP)** — modeling the tool/resource/
prompt primitives, writing tool descriptions as contract, choosing the transport
and its OAuth 2.1 authorization, and defending the agent-exposure security
surface (prompt injection, tool poisoning / rug-pulls, confused-deputy, token
passthrough, over-broad scopes, human-in-the-loop for destructive tools). They
do **not** re-decide the interface style (`api-style` places MCP among the
styles), re-specify the general threat model (`security-owasp`), or govern
asynchronous messaging (`enterprise-integration-patterns`); they reference those
at the seam and stay on the MCP surface.

## Discover

- Confirm the **consumer is an LLM agent / AI client** consuming tools, data, or
  prompts for autonomous use (the `api-style` selection signal for MCP). If the
  consumer is a human or another service, the surface is REST/gRPC/etc., not MCP.

## Frame

- Map each capability to the **right primitive by control surface**:
  - **Tool** — a **model-invoked action with effects** (write, send, call an
    external API); one operation, **typed JSON-Schema input + output**.
  - **Resource** — **application-controlled read-only context data** addressed by
    URI (direct or templated), with a declared MIME type. Not an action.
  - **Prompt** — a **user-invoked workflow template** (slash command etc.),
    explicitly triggered, never auto-fired.
- Do **not** expose a side-effecting action as a resource, and do **not** force
  passive data through a tool the model must decide to call. Record the exposed
  primitives in an ADR.

## Design

- Give every tool a **precise, honest, scoped description** stating what it does,
  when to use it, and what it does NOT do — the model selects tools on this text
  alone, so treat it as part of the contract, not documentation polish.
- Keep tools **single-purpose with typed JSON-Schema inputs** — no god-tool
  taking a free-form `command`/`action` string. Validate inputs against the
  schema (below).
- Do **not** embed steering instructions in a description beyond describing the
  tool, and treat **consumed** third-party tool descriptions as untrusted (tool
  poisoning, below).
- A tool with **irreversible or high-impact effect** (delete, send, pay, deploy,
  mutate external state) **requires explicit user confirmation at invocation** —
  a consent the user sees *before* the effect happens. Read-only/safe tools may
  be pre-approved; destructive ones may not silently auto-run on the model's
  decision.
- Surface tool execution (approval dialog and/or activity log) so the user can
  **see what a tool does before authorizing it**.
- Use **stdio** for a **local** server (runs as a subprocess, JSON-RPC over
  stdin/stdout, credentials from the environment) — preferred where the client
  runs the server locally. Use **Streamable HTTP** for a **remote / multi-client**
  server (single MCP endpoint, POST/GET, optional SSE streaming).

## Build

- **Validate and coerce each tool's arguments against its JSON Schema at the
  boundary** before acting — the caller is an LLM that can emit malformed,
  out-of-range, or adversarial input. Inner layers receive validated values,
  never raw model output.
- Run each tool under the **minimum credential/scope** for its job — no `*` /
  `full-access` / omnibus scopes, no bundling unrelated privileges up front.
  Prefer **progressive scope elevation** (start minimal, elevate on first
  privileged use) so a stolen token's blast radius stays small.
- Treat the **descriptions and schemas of tools this product consumes** as a
  prompt-injection / supply-chain surface: unless the source server is trusted,
  do not let consumed tool metadata steer the agent. Pin/verify metadata from
  proxied or aggregated servers.
- Detect **changed tool definitions** and **re-consent** rather than silently
  honoring a tool whose behavior/description changed after the user approved an
  earlier form (rug-pull).
- An **HTTP-transport** MCP server is an **OAuth 2.1 resource server**: publish
  protected-resource metadata (RFC 9728), require `Authorization: Bearer` on
  every request, and **validate that each token was issued specifically for this
  server** (audience / RFC 8707 resource indicator) — reject mismatched-audience
  tokens with `401`. (stdio servers take credentials from the environment and do
  not run this flow.)
- **Never pass tokens through**: do not accept a token not issued to this
  server, and do not forward the client's token unmodified to an upstream API —
  obtain a **separate** upstream token as that API's OAuth client.
- If this server is an **OAuth proxy** (static client ID + dynamic client
  registration), implement **per-client consent before forwarding** to the
  third-party authorization server, with exact redirect-URI matching and
  single-use `state` — otherwise it is a confused deputy.
- **Sessions are not auth**: verify authorization on **every** request; use
  random, **user-bound** session IDs (`<user_id>:<session_id>`) — never a
  session ID as proof of identity, never predictable session IDs.

## Deploy

- For a local HTTP server, **bind to localhost** (not `0.0.0.0`) and **validate
  the `Origin` header** to prevent DNS-rebinding. Restrict a local HTTP server's
  access (auth token, or IPC/unix socket) so other local processes cannot drive
  it.

## Test

- **Each capability is modeled to the right primitive** — model-invoked actions
  with effects are **tools** (typed JSON-Schema input/output, single-purpose),
  read-only context data is **resources** (URI + MIME type), user-invoked
  templates are **prompts**; no side-effecting "resource", no god-tool with a
  free-form command string.
- **Every tool has a precise, honest, scoped description** (the model's only
  affordance) — verifiable by reading the tool definitions; no terse/missing
  descriptions, no steering instructions smuggled into descriptions.
- **Destructive / high-impact tools require human-in-the-loop confirmation** at
  invocation; they do not auto-execute on the model's decision, and tool
  execution is surfaced (approval and/or activity log).
- **Tool inputs are validated against their JSON Schema at the boundary** before
  acting — inner layers never receive raw model output.
- **Tool scopes are least-privilege** — no `*`/`full-access`/omnibus or bundled
  unrelated privileges; progressive elevation over up-front broad grants.
- **The HTTP transport authorizes with OAuth 2.1 and validates token audience**
  (RFC 8707) — mismatched-audience tokens rejected; **no token passthrough**
  (separate upstream token); an OAuth-proxy server enforces per-client consent.
- **The transport is locked down** — local HTTP servers bind localhost and
  validate `Origin` (DNS-rebinding); sessions are not used as authentication and
  session IDs are random and user-bound.
- **Consumed/aggregated third-party tool metadata is treated as untrusted** —
  defense against tool poisoning, and re-consent on changed tool definitions
  (rug-pull) where the product proxies other MCP servers.

## Cross-cutting

### Boundary with neighbors

- **vs `api-style`**: api-style selects the interface style and *places MCP*
  among them (the agent-facing option) and records the selection; this concern
  holds the MCP-specific discipline once MCP is chosen. Do not re-run the
  style-selection guide here.
- **vs `security-owasp`**: security-owasp owns the baseline threat model (OWASP
  Top 10, injection, access control, secrets, TLS); this concern adds the
  **agent-exposure** layer (tool poisoning, rug-pull, confused-deputy, token
  passthrough, over-broad tool scopes). Compose; do not restate the Top 10.
- **vs `enterprise-integration-patterns`**: MCP is a **synchronous** tool/
  resource interface the agent calls and awaits; a tool that *enqueues* work
  writes to an EIP channel — the `tools/call` is this concern, the channel is
  EIP's. Do not model MCP as an async message bus.
- **vs `auth`/`auth-local-sessions`**: those own the product's own user login;
  this concern owns the **OAuth 2.1 agent-token boundary** for the MCP HTTP
  transport (audience binding, no passthrough). Compose; do not conflate.
