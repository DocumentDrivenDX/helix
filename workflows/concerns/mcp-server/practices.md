# Practices: MCP Server

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
