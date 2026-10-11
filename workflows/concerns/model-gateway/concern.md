# Concern: Model Gateway (model access)

## Category
infrastructure

## Areas
api, infra

## Boundary

Owns: what the product names when it needs a model, who owns the gateway
routes behind those names and the access callers hold to them, and how the
product proves each model it depends on is callable the way it will actually
call it. Platform-neutral: it applies to any gateway that fronts model
endpoints (a cloud platform's gateway, an LLM proxy, a hosted API gateway), and
to a product that calls providers through its own routing layer.

Does not own: which product principal may use which feature
(`authorization-model`); billable meter events (`usage-metering`; a gateway's
budgets and rate limits are operational limits, not the product's meter);
app-side timeout, retry and breaker policy (`resilience`); trace propagation and
span content (`o11y-otel`); tools the product exposes to others (`mcp-server`;
function tools sent *to* a model are a capability to verify here, not that
concern); identity and credentials on a specific platform (the platform concern,
for example `databricks-apps`). A platform realization of this concern, when one
exists (for example `databricks-ai-gateway`), composes with it.

## Components

- **Model alias**: a product-owned name for a job (for example `quick`,
  `balanced`, `deep`, or `extract`, `draft`), bound to a gateway route outside
  the product. An alias names a need, not a model and not a reasoning effort.
- **Gateway route**: what an alias resolves to, with its fallback chain and
  limits, owned outside the product release.
- **Adapter**: the one place the product speaks to the gateway, on one API
  route.
- **Deploy gate**: a check run at deploy against every alias the product needs.

## Constraints

- **Name the need, not the model.** Product code and plug-ins declare an alias.
  The binding from alias to model lives outside the product release, so a model
  change needs no product release.
- **One owner for routes and caller access.** Whoever creates a gateway route
  also issues the access callers hold to it (keys, grants, scopes). Access
  granted anywhere else drifts or is overwritten.
- **The deploy gate proves each alias is callable as the product calls it.**
  Every required alias name is present and non-empty, and one call per alias uses
  the same route, the same features (tools, streaming, structured output), and
  the same credential the product uses. A missing name or an unusable alias fails
  the deploy, not a user's first prompt. A plain-prompt probe passes while tool
  calls fail.
- **A model must support what the adapter uses on the route it speaks.**
  Capability differs by model family and route; verify by calling, not by
  documentation.
- **Rebinding an alias is a model substitution** and passes the evals of every
  workflow that declares the alias.
- **Attribution.** Each model call can be matched to the gateway's request log by
  an id the product sends, and the gateway's usage record names the principal the
  product attributes the call to.
- **No stacked retries.** App-side retries do not sit on top of a gateway
  fallback chain without a budget; one layer owns each retry.

## Drift Signals (anti-patterns to reject in review)

- A concrete model or route name hardcoded in product code or a plug-in
  manifest → declare an alias
- Caller access granted by hand or by a repository that does not own the route
- Deploy passes while the first real prompt fails → the gate does not call every
  alias
- A readiness probe sends a plain prompt but production sends tools → probe the
  features actually used
- An alias rebound without re-running the evals that depend on it
- An alias name that resolves to nothing without failing the deploy
- Model calls the gateway's request log cannot be matched to

## When to use

Any product that calls models through a gateway or routing layer. Composable (no
slot). Pair with a platform realization when one exists, with `o11y-otel` when
model calls must be traced end to end, and with `usage-metering` when model use
is billed.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- TD: states the alias set, who owns each route and the access callers hold, the adapter route and features used, and the gate's coverage
- TEST_PLAN: a gate that calls each alias with the features in use; evals gating alias rebinds
- deployment-checklist: required alias names present after the settings are resolved; access verified by a real call

## ADR References

Selecting this concern needs no ADR; `concerns.md` records it. Write an ADR only
when the project deviates from a constraint here. An unverified capability (does
this model accept tools on this route?) is a probe or `tech-spike`, not an
assumption.
