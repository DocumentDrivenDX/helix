---
name: helix
description: |
  HELIX skill — single entrypoint for product/feature/requirements work,
  infrastructure changes, data pipelines, and web/frontend operations.
  Engage on prompts to frame, align, decompose, prioritize, propose,
  capture, review, decide, evolve, or release work — also without naming
  a HELIX artifact (e.g. "frame the opportunity", "review the
  architecture"). Engage on any named HELIX artifact: PRD, ADR, FEAT,
  feature spec, technical design, implementation plan, test plan,
  runbook, release notes, user stories, roadmap brief, requirements.
  Engage on infra verbs (terraform/tofu/kubectl, provision/destroy/
  rotate, CI, credentials), data verbs (backfill/ingest/migrate a table
  or schema, profile a source, data contract), web verbs (deploy/ship,
  monitoring, page perf) — these route INTERNALLY to the matching mode.
  Engage on "what's next" / "plan the change" / cross-flow queries.
  Once engaged, route to one of: product, infra, data, web. Honor
  explicit prefix (/helix-infra → infra mode) or HELIX_METHODOLOGY= env
  override.
argument-hint: "[intent or scope]"
---

# HELIX Router

Use this as the HELIX entrypoint. Users should not need to memorize individual
workflow skill names. Route the request to the smallest HELIX workflow that
fits, then follow the matching workflow contract below.

Rule: do not add separate public `helix-*` skills. Add or refine a route inside
this skill instead.

## When to engage (read first; non-negotiable)

You ENGAGE this skill — call `Skill(helix)` — whenever any of these is true,
regardless of whether the artifact content is attached, the workspace is
empty, or the request looks like a generic task. Once engaged, you route
INTERNALLY to one of four modes (product / infra / data / web). The skill
does not have sibling skills to defer to — internal routing is the only
routing.

Engage when:

- The prompt names a HELIX artifact (PRD, ADR, FEAT, feature spec,
  technical design, implementation plan, test plan, runbook, release
  notes, user stories, roadmap brief, requirements) — even when the
  prompt asks you to *review* or *expand* one whose content is not
  attached. Engage; THIS SKILL knows how to resolve the artifact path
  from the marker + graph + cwd, you do not.
- The prompt uses a HELIX planning verb (frame, align, decompose,
  prioritize, propose, capture, review, decide, evolve, refresh,
  release) against a product/feature/requirements object → route to
  **product** mode.
- The prompt uses an IaC verb (terraform/tofu/kubectl, provision/destroy/
  rotate, set up CI, manage credentials) → route to **infra** mode
  AFTER consulting `stop_at` triggers.
- The prompt uses a data-pipeline verb (backfill/ingest/migrate a table
  or schema, profile a source, write a data contract) → route to
  **data** mode.
- The prompt uses a web/frontend verb (deploy/ship to production, add
  monitoring for a user-facing flow, optimize page performance) → route
  to **web** mode AFTER consulting `stop_at` triggers.
- The prompt asks "what's next", "plan the change", "decide what to do",
  or any cross-flow query that needs the marker to answer → route to
  the §Check And Next contract.

Operator overrides (rare but honored):

- Explicit prefix `/helix-infra ...`, `/helix-data ...`, `/helix-web ...`
  pins the internal mode for the rest of the prompt. Engage and route
  directly to the named mode without re-evaluating triggers.
- `HELIX_METHODOLOGY=<mode>` env (legacy alias for `HELIX_FLOW=<mode>`)
  sets the session-default internal mode.

Verbose-but-stuck anti-pattern: narrating HELIX-shaped reasoning in
assistant text WITHOUT calling `Skill(helix)` is a contract violation.
The Skill tool_use must fire as the FIRST tool_use of the turn when any
of the engage conditions above is true.

## Internal routing modes

After engagement, the skill drives behavior by mode. The bench grades by
mode-specific observable behavior (the `route_decision_internal` matcher),
not by a narrated routing intent.

| Mode | Triggers | Required observable behavior (any 2 satisfy the matcher) |
|---|---|---|
| `product` | HELIX artifact named; planning verb against product/feature/requirements; cross-flow query | (a) Read `.helix.yml` AND `workflows/graph.yml` BEFORE any Write/Edit (`read_before_write` matcher); (b) Read of named upstream artifacts (vision, PRD, feature spec) per the graph BEFORE drafting; (c) cite `ddx.links` / `informs` edges in any new artifact |
| `infra` | IaC verb (terraform/tofu/kubectl, provision/destroy/rotate); CI/credentials ops | (a) Consult `library/skill-prompts/stop-at-triggers.yml` for `apply` or `secret_read` triggers BEFORE any Bash; (b) Read of infra-shaped artifacts (architecture, runbook, deployment-checklist); (c) explicit confirmation prompt before terraform/tofu/kubectl/credential operations |
| `data` | Data-pipeline verb (backfill/ingest/migrate, profile a source, data contract) | (a) Read of data-contract / data-quality-expectations / data-architecture artifacts; (b) cite producer/consumer or PII/governance posture in prose; (c) defer schema mutations behind a `stop_at` confirmation |
| `web` | Web/frontend verb (deploy/ship, add monitoring for a user flow, optimize page perf) | (a) Read of architecture / design-system / monitoring-setup / runbook artifacts in the deploy-flow scope; (b) cite Web Vitals / RUM / page-error vocabulary in prose; (c) defer production deploys behind a `stop_at` confirmation |

Skipping the mode-required behavior is a routing failure even if the Skill
tool_use fires. The bench measures this.

## Activation discipline (do these in order, every time the skill engages)

### 1. Locate the marker

Find `.helix.yml` by walking UP from the current working directory to the
git root (the directory containing `.git/`). Stop at the first `.helix.yml`
encountered. If the cwd is `/repo/services/api/docs/helix/` and the marker
lives at `/repo/.helix.yml`, you MUST find the parent marker — do not give
up after searching cwd only.

Concretely: run `git rev-parse --show-toplevel` (or fall back to walking up
until `.git/` is found), then check for `.helix.yml` at the top.

### 1.5 Read marker AND graph before any Write/Edit (ordering invariant)

The FIRST `Write` or `Edit` tool_use in the session MUST be preceded by at
least one `Read` matching `.helix.yml` AND at least one `Read` matching
`workflows/graph.yml`. Skipping either is a contract violation, EVEN IF the
Skill tool_use has already fired. The failure mode this rule prevents — the
verbose-but-stuck pattern — is the agent narrating HELIX-shaped reasoning
from training while the marker scope, the type catalog, and the prerequisite
chain go unconsulted. The resulting artifact looks plausible but is
unanchored to the workspace's actual contract.

The order between the two Reads is not constrained: marker-first is the
natural sequence; graph-first is acceptable for graph-query-only prompts
like "What's next?" (no Write/Edit follows).

This ordering invariant is independent of autonomy level. Under
`autonomous` the skill MAY proceed without operator confirmation, but it
MUST NOT skip the two Reads — autonomy waives the human-in-the-loop ask,
not the workspace-grounding contract.

If the marker is absent and the skill is engaging by heuristic (§2 banner
case), the `Read` for `.helix.yml` is satisfied by the failed lookup itself
(the Read tool_use occurred even though the file did not exist); the `Read`
for `workflows/graph.yml` is still required before any Write/Edit because
the type catalog binds artifact templates.

The bench enforces this via the `read_before_write` matcher.

### 2. Decide activation state

Before anything else: check the explicit operator overrides. They win over
marker contents.

- **Explicit prefix in the prompt** (`/helix-infra ...`, `/helix-data ...`,
  `/helix-web ...`): pins the internal mode for this turn. Engage,
  skip mode re-evaluation, route directly to the named mode.
- **Env override** (`HELIX_METHODOLOGY=<mode>` or `HELIX_FLOW=<mode>`):
  same handling — pins the session-default internal mode.

Only after overrides are checked, evaluate the marker:

- **Marker present and well-formed**: parse it. The `flows[]` list (legacy
  alias `methodologies[]:` accepted under M020 warn) is the authorization
  boundary. If `helix` is listed, this skill is active for the listed
  `root:` scope. If `helix` is NOT listed (the marker only declares a
  non-helix flow), defer to that flow's process — do not engage.

- **Multiple distinct flows in `flows[]` with an ambiguous verb** (e.g.
  `flows: [{id: helix, root: docs/helix/}, {id: helix-infra, root:
  docs/helix-infra/}]` and the prompt uses a verb like "plan the rollout"
  that could mean product-rollout planning under `helix` OR infrastructure
  rollout planning under `helix-infra`): apply the resolution chain first:
  explicit prefix → HELIX_FLOW env → cwd-under-root → `defaults.flow` in
  the marker. If the chain does not resolve — no override, no env, cwd is
  outside every declared `root:`, no `defaults.flow` key — you MUST emit
  the disambiguation banner naming BOTH candidate flows and asking which one
  applies:

      Ambiguous request: both `helix` (root: <helix-root>) and `helix-infra` (root: <infra-root>) are active — which flow should handle this?
      Re-run with the explicit prefix `/helix` or `/helix-infra`, or set HELIX_FLOW=<id>.

  Substitute the actual `root:` values from the marker. Do NOT silently
  pick one flow. Do NOT route to infra mode under the `helix` flow just
  because the prompt contains an infra-adjacent noun. Wait for the operator
  to choose.

- **Multiple helix instances in `flows[]`** (e.g.
  `flows: [{id: helix, instance: web, root: services/web/}, {id: helix,
  instance: mobile, root: apps/mobile/}]`): you do NOT auto-pick. Emit the
  disambiguation banner:

      Multiple helix instances declared: <instance-1> (root: <root-1>),
      <instance-2> (root: <root-2>). Re-run with the explicit prefix
      `/helix:<instance-name>` or set HELIX_INSTANCE=<name>.

  Then stay silent. Do not call `Skill(helix)`. The cwd-under-scope rule
  (§3) does NOT promote one instance over the other when the prompt is
  ambiguous — only an explicit prefix, env override, or cwd that lies
  inside exactly one `root:` resolves it.

- **Marker present and malformed** (YAML parse error, missing required keys,
  root outside repo, duplicate id, root resolves to nonexistent dir): STOP.
  Report the marker error verbatim with file and line. Do NOT fall back to
  heuristics.

- **Marker absent, heuristic file present** (`workflows/methodology.yml`,
  `docs/helix/` tree, etc. — legacy heuristic filename retained for
  back-compat detection): emit this banner verbatim before any other
  output:

      No .helix.yml found. Activating helix by heuristic (path: <heuristic-path>).
      Run /helix init-marker to make this explicit.

  Substitute the actual heuristic-path that triggered activation. Then
  proceed.

- **Marker absent, no heuristic**: report no active flow. If asked for a
  machine-readable response, return `{"active": []}`. Do not improvise
  that helix is active.

### 3. Enforce scope

For every operation that writes or edits a file, check that the target path
is INSIDE the active flow's `root:` from the marker. If the user asks for
a write outside that scope:

- Refuse the write.
- Surface the marker entry that scoped the flow and the offending target
  path.
- Ask whether they want to (a) update the marker to broaden scope, or
  (b) redirect the write to under the scope, or (c) cancel.

Do NOT silently write outside scope. Scope is the marker's contract.

When the marker declares multiple flows at different scopes, the flow
whose `root:` contains the cwd wins. If cwd is outside every declared
scope, follow the resolution chain: explicit prefix → HELIX_FLOW env
(legacy HELIX_METHODOLOGY) → cwd-under-root → defaults.flow → single
entry → disambiguation banner with deterministic tie-break by listed
order.

### 4. Author / edit artifacts

When asked to author or edit an instance document, follow the type's
`template.md` and `prompt.md` from the library. Look up the type via the
flow's `workflows/graph.yml` — every node points at a `library:<slug>`
or `local:<slug>` type, and the library tree is at the canonical install
root (`library/` after this install).

**Edit existing instances; Write only new ones.** When the requested
artifact already exists at the resolved path, use `Edit` (target the
specific lines/sections changing), NOT `Write` (which replaces the file
body and discards any operator-added content not in the new draft).
Verify the file exists via `Read` before deciding: a successful Read of
the resolved path means the instance is live and any modification MUST
go through `Edit`; only a missing-file outcome authorizes `Write`. This
applies to every operator verb that mutates an existing artifact —
"update", "modify", "amend", "add a requirement to", "thread X through"
— regardless of how small the change is. Replacing a live PRD/FEAT/ADR
via `Write` to add one bullet is a contract violation even when the
new body looks correct, because frontmatter round-trip (§6) and
operator-added content outside the model's draft are silently dropped.

Instance edges (PRD → FEAT, ADR → technical-design, etc.) belong in the
instance's frontmatter under `ddx.links:`. Never embed edges in the body
or in this skill's prompts.

Cross-flow edges (e.g. PRD informs an infra-mode artifact) must be
declared in `external_edges:` of `workflows/graph.yml` first, then in the
instance frontmatter with `cross_flow: true` (legacy alias
`cross_methodology: true` accepted for one cycle).

### 5. Authorization boundary

**REJECT — do not engage** when the prompt names a flow (via explicit
prefix `/helix-<flow>`, env-override `HELIX_METHODOLOGY=<flow>` or
`HELIX_FLOW=<flow>`, or natural-language equivalent like "use the
helix-infra flow") that the marker's `flows:` list does NOT authorize.
This rule is non-negotiable and overrides every engage-by-default
trigger in §"When to engage" and every mode-routing rule below it. An
explicit prefix or env override is a *request* to activate a flow; the
marker is the *authorization* to do so. No marker authorization, no
activation — even when the prefix is explicit, even when the user is
insistent, even when the work looks routine. The §2 operator-override
priority (prefix/env wins over marker for mode-routing decisions) does
NOT bypass this check — it applies only when the requested flow is
already authorized by the marker.

Emit this diagnostic verbatim (substituting the actual flow name and
marker path), then STOP — no Read of artifacts, no Write, no Edit, no
mode routing, no "but I can still help with…" offer:

    Cannot engage <flow-name> here — the requested flow `<flow-name>`
    is not authorized: the .helix.yml marker does not list it.
    The marker authorizes only: <comma-separated list of marker flows>.
    To proceed, either (a) add `<flow-name>` to the marker's `flows:`
    list, or (b) re-run with a flow the marker authorizes.

Your refusal prose MUST include: (a) the name of the requested flow,
and (b) a phrase stating the .helix.yml marker does not list or
authorize it. Use the verbatim template above — do not paraphrase it.

Concretely: if the marker declares only `flows: [{id: helix, ...}]`
and the prompt is `HELIX_METHODOLOGY=helix-infra rotate the upstream DNS
provider`, the requested flow is `helix-infra`, which is NOT `helix`.
Reject. Do not silently route to infra mode under the `helix` flow —
the env override named a different flow, and re-interpreting it as the
authorized flow is a contract violation.

The marker's `flows:` list is the authorization boundary. An explicit
`/helix <verb>` prefix or `HELIX_METHODOLOGY=helix` env override wins
ONLY if `helix` is a marker member.

### 6. Frontmatter round-trip

Never rewrite unknown frontmatter keys. When you edit an instance
document's body, preserve `ddx.id`, `ddx.review`, `ddx.links`, AND any
vendor-namespaced (`x-*`) or legacy (`relationships:`, `depends_on:`)
keys byte-equivalent. Key order is preserved (insertion-order dict +
`yaml.safe_dump(..., sort_keys=False)`).

Legacy → new key translation (e.g. `relationships:` → `ddx.links:`) is
done ONLY by the explicit migration script
`library/scripts/migrate_relationships_to_links.py`. Never translate as
a side effect of an incidental edit.

## Concern slot resolution

A **slot** is an exclusive functional position a project must fill exactly
once (one frontend framework, one language runtime, one e2e tool, one auth
backend). Slots are declared in the shipped library at
`<plugin-root>/workflows/concerns/slots.yml` — load it from the canonical
install root (the same `<plugin-root>` used by §Catalog Resolution). The
file declares exclusive slots plus shipped defaults; membership in a slot
is **derived** from each concern's own `## Slot` section, never listed in
`slots.yml`.

For every needed exclusive slot, resolve the filler in this fixed order
(first match wins):

1. **Operator override** — `docs/helix/01-frame/concerns.local.yml` in the
   project tree. Read this BEFORE concerns.md exists, during high-autonomy
   concern selection.
2. **Shipped default** — the `defaults:` map in `slots.yml`.
3. **Recorded assumption** — if neither source resolves, infer from the
   product's nature and record it as an assumption in `concerns.md`.

Exclusive slots and their shipped defaults (current `slots.yml`):

| Slot | Shipped default |
|---|---|
| `frontend-framework` | `react-nextjs` |
| `language-runtime` | `typescript-bun` |
| `e2e-framework` | `e2e-playwright` |
| `auth-provider` | `auth-local-sessions` |
| `datastore` | — (no default; select on signal) |
| `deploy-target` | — (no default; select on signal) |
| `architecture-style` | — (no default; select on signal) |

**Contract**: select each needed slot **once per session** during §Frame
step 2, and record the chosen filler PLUS its source (`operator-override`,
`shipped-default`, or `assumption`) in `concerns.md`. Propagation to work
items and downstream artifacts is a later gate (owned by `check`/`polish`),
never a re-selection.

## Routing Rules

Prefer the first matching route:

| User intent | Mode |
|---|---|
| Convert rough intent into governed HELIX work | input |
| Create or refine product vision, PRD, feature specs, or user stories | frame |
| Reconcile artifacts, check traceability, find drift, align documents, or move content between artifact layers | align |
| Check an artifact instance against its template and prompt; improve in place | validate |
| Bring every artifact instance up to date with the current templates and prompts | refresh |
| Thread a new, changed, removed, or incident-driven requirement through existing artifacts | evolve |
| Create a technical design before implementation | design |
| Reconstruct missing or incomplete docs from evidence | backfill |
| Fresh-eyes review of recent work, PRs, plans, or implementation | review |
| Refine work items for execution readiness | polish |
| Decide the next safe HELIX action | check or next |
| Execute one bounded implementation pass | build |
| Run the bounded operator loop | run |
| Commit verified HELIX/DDx work | commit |
| Cut a release | release |
| Run an optimization experiment | experiment |
| Monitor a background HELIX run | worker |

When multiple routes fit, choose the highest-authority planning route first:
`frame` before `design`, `align` before `evolve` when the task is diagnostic,
and `evolve` before `build` when a requested implementation lacks governing
artifact coverage.

## Catalog Resolution

When a workflow mode needs an artifact template, prompt, or quality
criteria, resolve catalog paths against the mounted skill content, in
this order of preference:

1. `references/activities/<NN>-<activity>/artifacts/<type>/` — relative
   to this `SKILL.md`. This is the agentskills.io progressive-disclosure
   layout used by skill bundles (e.g. Databricks Genie Code, the Vercel
   Labs Skills CLI install path).
2. `<plugin-root>/workflows/activities/<NN>-<activity>/artifacts/<type>/`
   in plugin installs that vendor the source tree. The `<plugin-root>`
   placeholder is the runtime's plugin path (for example
   `~/.claude/plugins/helix/` under Claude Code); each runtime's install
   guide under `docs/install/` names the concrete location for that runtime.

The seven activities and the artifact types they own:

| Activity | Artifact types (directory names under `<activity>/artifacts/`) |
|---|---|
| `00-discover` | `business-case`, `competitive-analysis`, `opportunity-canvas`, `product-vision`, `resource-summary` |
| `01-frame` | `compliance-requirements`, `concerns`, `feasibility-study`, `feature-registry`, `feature-specification`, `parking-lot`, `pr-faq`, `prd`, `principles`, `research-plan`, `risk-register`, `security-requirements`, `stakeholder-map`, `threat-model`, `user-stories`, `validation-checklist`, `data-prd` |
| `02-design` | `adr`, `architecture`, `contract`, `data-design`, `design-system`, `proof-of-concept`, `security-architecture`, `solution-design`, `tech-spike`, `technical-design`, `data-architecture` |
| `03-test` | `security-tests`, `story-test-plan`, `test-plan`, `test-procedures`, `test-suites`, `data-quality-expectations` |
| `04-build` | `implementation-plan` |
| `05-deploy` | `deployment-checklist`, `monitoring-setup`, `release-notes`, `runbook` |
| `06-iterate` | `improvement-backlog`, `metric-definition`, `metrics-dashboard`, `security-metrics` |

Each artifact-type directory contains `template.md`, `prompt.md`,
`meta.yml`, and an `example.md` (or `example-*.md`). Common queries
("list artifact types under activity 01-frame", "what's the path to
the prd template") can be answered from this table without traversing
the filesystem; deeper queries that need template or prompt content
require loading the file from one of the resolution paths above.

If the catalog is at neither location, the runtime has not mounted it;
report this as a setup gap rather than improvising paths or guessing
artifact-type names.

## Project Root Resolution

When a workflow mode needs to enumerate artifact instances within the
operator's project (used by §Refresh and similar batch operations),
resolve the project HELIX root in this order:

1. Explicit path provided by the operator at invocation
   (e.g., `refresh docs/helix/`).
2. Runtime-supplied project-config value when present
   (`helix_root` in DDx project config; equivalent in other runtimes).
3. Convention: `docs/helix/` under the runtime's working directory,
   with sub-directories `00-discover`, `01-frame`, …, `06-iterate`.

If none of the three resolves to a directory containing the expected
activity sub-directories, surface a setup gap rather than improvising.
Batch operations on chat-only runtimes (Databricks Genie Code, GitHub
Copilot) require step 1 — the operator names the root in the prompt.

## Autonomy

HELIX expresses an autonomy **policy**; the runtime supplies the agency. The
policy is a three-position spectrum that controls **how often a workflow pauses
for confirmation** — never which activities run.

| Level | Behavior |
|---|---|
| `low` | Ask before each step and before creating each downstream artifact. Do not infer unconfirmed scope. Concern selection stays interactive. |
| `medium` (default) | Create deterministic non-conflict artifacts; pause when ambiguity or conflict blocks deterministic progress. Prompt for concern selection when none exists. |
| `high` | Create downstream artifacts without pausing unless a hard stop blocks progress; record assumptions as speculative work rather than asking. When no concerns are declared, **infer** the concern selection from the product's nature and record it as an assumption. |

**Resolution precedence** (first match wins): per-invocation override →
governing artifact frontmatter / project policy → runtime default (`medium`).
The autonomy signal lives only in runtime-neutral artifacts; do not read or
write it from a runtime instruction file.

**Hard-stop invariant (all levels).** Autonomy changes the *pause threshold*,
never the *stop floor*. Stop and surface to a human, at any level, when two
higher-or-equal-authority artifacts truly contradict, when the next action is
destructive or irreversible and unauthorized, or when a decision only a human
can make is required. High autonomy proceeds through *resolvable* conflicts
(recording assumptions); it never proceeds through a hard stop.

**Never-collapse-the-loop invariant (all levels).** Autonomy changes checkpoint
density only. It never collapses the seven-activity loop into one generic prompt
and never skips an activity the work requires — a high-autonomy run executes the
same activities a low-autonomy run would, pausing less often.

Routes that pause (input, frame, evolve, design, build) honor the resolved
level; routes that select concerns honor the high-autonomy inference path.

## Apply The Autonomy Level

A second-axis autonomy declaration is layered on top of the policy spectrum
above for runtimes that support an explicit operator-facing level
(`manual` / `guided` / `autonomous` / `aggressive`). When that declaration is
present, consult it before every state-changing tool use.

Before any tool use that mutates state (Write, Edit, Bash that writes, git,
install), determine the effective autonomy by reading sources in this order;
the first source that defines a level wins:

1. **Per-prompt override** — slash prefix (`/helix-autonomous`, `/helix-manual`)
   or `HELIX_AUTONOMY=<level>` environment variable.
2. **Repo-user-local override** — `.helix-autonomy.yml` at the repo root
   (gitignored; per-user-per-repo).
3. **User default** — `~/.config/helix/autonomy.yml` (per-user, all repos).
4. **Repo default** — the `autonomy:` block in `.helix.yml`
   (committed, team baseline).
5. **Skill default** — `guided` if no source defines a level.

Then dispatch on the resolved level:

- `manual` — state the proposed action, list its effects, and ask
  "OK to proceed?" before ANY tool use (Read, Write, Edit, Bash).
- `guided` — state the proposed action briefly. Ask before the *first*
  state-changing tool use in the conversation. Subsequent state-changing
  tool uses within the same turn proceed silently UNLESS the action touches
  a `stop_at` event.
- `autonomous` — proceed without asking; surface results after the fact.
  Stop only on a `stop_at` event or irreducible ambiguity (e.g. two equally
  valid graph routes, an ambiguous methodology activation). **Even when
  silently routing via `defaults.flow` / `defaults.methodology`, prose-
  attribute the routing decision in your FIRST text block** — name the
  chosen flow ("Routing to helix because the marker's default flow is
  helix") so downstream readers and bench graders can confirm the routing
  decision. Silent routing is operationally allowed; silent-AND-unspoken
  routing is a contract violation.
- `aggressive` — as `autonomous`, but additionally take initiative across the
  full methodology graph (e.g. draft ALL declared prerequisites plus the
  requested artifact in one pass). Still honors `stop_at` and irreducible
  ambiguity. Same prose-attribution rule as `autonomous`.

`stop_at` is a hard floor that fires at every level, including `autonomous`
and `aggressive`. The authoritative trigger list lives at
`library/skill-prompts/stop-at-triggers.yml`. Load it at graph-mode start
and consult each trigger's matcher before every mutating tool use. A repo
may add triggers via `stop_at_extensions:` in `.helix-autonomy.yml`; the
active set is the union of base + extensions. Base triggers cannot be
removed.

The base v1 triggers are:

| Trigger id | Fires on |
|---|---|
| `marker_edit` | Write/Edit on `.helix.yml` or `.helix-autonomy.yml` |
| `cross_methodology_edge_creation` | Write/Edit that introduces `cross_methodology: true` or `cross_instance: true` |
| `branch_or_merge` | Bash running `git checkout|merge|push|reset|rebase|cherry-pick` or `gh pr merge|create` |
| `secret_read` | Read or Bash targeting `.env`, `.tfvars`, `credentials.json`, `.pem`, `id_rsa(.pub)`, `private_key`, `.key`, `secrets/` |
| `large_diff` | Single Write/Edit whose content exceeds 500 lines (per tool_use, not aggregated) |
| `apply` | Bash running `terraform apply`, `tofu apply`, `databricks jobs|pipelines run|update`, `kubectl apply|delete|patch` |

When a trigger matches, emit an explicit confirmation prompt that names the
trigger and the proposed action, then wait for the operator's reply. The
prompt must be distinct from generic affirmations — at minimum, restate the
action and ask whether to proceed (e.g. "About to run `terraform apply` in
infra/prod — should I proceed?"). Generic `ok?` / `yes?` prompts do not
satisfy the contract.

## Workflow Contracts

### Input

Use for sparse user intent that needs to become governed HELIX work.

1. Clarify scope only when missing information would make the resulting work
   unsafe or unactionable.
2. Identify governing artifacts that already exist.
3. Produce or update planning work items rather than implementation work when
   authority is missing.
4. Keep created work standalone: include context, acceptance criteria, labels,
   parent/dependency relationships, and verification commands.

### Frame

Use for creating or refining product vision, PRD, feature specs, and user
stories.

1. Read existing Frame artifacts first.
2. **Select concerns — this is a required Frame step.** A frame pass is not
   complete until the project's concerns are selected (or it is explicitly
   recorded that none apply); shipping feature specs with no concern decision is
   a framing gap, not an acceptable default-empty state. At `low`/`medium`,
   drive selection interactively by category (tech stack, data, infrastructure,
   quality). At `high`, infer the selection from the product's nature and record
   each inferred concern as an assumption. **Fill each needed exclusive slot**
   (a slot is an exclusive functional position — one frontend framework, one
   language runtime; defined in
   `<plugin-root>/workflows/concerns/slots.yml`) by resolution order:
   operator override (`docs/helix/01-frame/concerns.local.yml`) → shipped default
   (`slots.yml`) → recorded assumption, and record the chosen filler plus its
   source in `concerns.md`. A web app must fill `frontend-framework` — the
   shipped default `react-nextjs` applies with no operator config. A UI web app
   must also fill `e2e-framework` (default `e2e-playwright`); selecting the tool
   is not coverage — ≥1 core user-flow must have a whole-stack e2e that runs green
   against the running app (a browser e2e for a client-rendered UI, or an
   HTTP+HTML-assertion e2e for a server-rendered one). An **operator-facing**
   product (a human operator manages mutable domain objects or lifecycle state
   through a UI) selects `admin-console` — the operator's jobs-to-be-done (CRUD +
   control actions like pause/cancel) built as usable UI, with the primary
   operator workflow exercised end-to-end *through the UI*. An **account-based /
   multi-tenant** product (users/tenants/sign-in/roles/principal-scoped data)
   selects `auth` — real signup→tenant+owner, login/sessions, server-side RBAC +
   platform-admin, isolation through the principal — and fills the `auth-provider`
   slot (default `auth-local-sessions`; an external IdP is a swappable filler,
   never hardcoded). Neither is selected for pure APIs, CLIs, libraries,
   static content sites, or read-only dashboards (unless an operator UI is
   explicitly required). Selection happens here, once; propagation to work
   items is a later gate owned by `check`/`polish`, not a re-selection.
3. Read the relevant artifact template and prompt before drafting.
4. Keep each artifact in its lane:
   - Product Vision is direction.
   - PRD is product scope: capabilities, outcomes, priorities, metrics, and
     non-goals.
   - Feature specs are feature behavior, boundaries, edge cases, and
     decomposition.
   - User stories are vertical user journeys and observable acceptance
     criteria.
   - Contracts are exact shared interface surface: API/CLI/event/schema/config/
     telemetry/adapter commands, flags, fields, payloads, status codes, error
     semantics, versioning rules, stability rules, and examples.
   - Solution Design is the feature-level technical approach, domain model,
     component decomposition, and interface usage.
   - Technical Design is the story-level implementation design: files,
     component changes, tests, rollback, sequence, and references to governing
     Contracts.
   Exact shared interface surface belongs in Contract, not PRD, Feature Spec,
   User Story, Solution Design, or Technical Design. Those artifacts may name or
   reference the need for an interface; they do not define the normative
   surface inline.
5. Give each user-story acceptance criterion a stable `US-<n>-AC<m>` ID in
   Given/When/Then form so the story test plan can map it to tests by name.
   Decompose to a **coverage floor** (minimum rigor, not equal depth): every PRD
   functional requirement `FR-n` maps to ≥1 user story (don't bundle unrelated
   `FR-n`s without justification), and every acceptance criterion gets ≥1 test
   that *exercises* it — a named test with no relevant assertion is `UNTESTED`,
   not covered. An untested AC blocks unless a reviewed manual/non-automatable
   exception is recorded with evidence. Every covering test must **cite the AC
   ID it covers** in the canonical, parseable syntax `@covers US-<n>-AC<m>` so
   traceability is machine-checkable — an exercising, passing test that omits
   the citation is `UNCITED_COVERAGE` (fix = add the citation, not a new test),
   distinct from `UNTESTED`; a test that cites an AC it does not exercise is
   `ASSERTED_UNBACKED`. Citation is an additional gate on top of
   exercise+pass+satisfy, never a replacement.
6. Validate blocking template checks before treating the artifact as ready.
7. Create follow-up design or implementation work only after the framing
   artifact can govern it.

### Align

Use for reconciliation, traceability audits, drift checks, and artifact content
placement reviews.

1. Start from authority: vision, PRD, features/stories, architecture/ADRs,
   designs, tests, implementation plans, code. The spec stack is the contract;
   code is a projection of it. Traceability is **bidirectional**: every material
   code surface (route/screen/CLI/API/job/migration) traces to a governing
   artifact, and every acceptance criterion traces to an exercising test. Unmapped
   material surfaces and unimplemented criteria are both alignment findings.
2. Reconstruct intent from planning artifacts before inspecting lower layers.
3. Classify each gap as `ALIGNED`, `INCOMPLETE`, `DIVERGENT`,
   `UNDERSPECIFIED`, `STALE_PLAN`, or `BLOCKED`.
4. Produce one durable alignment report when the action is more than a
   conversational review. The report must remain reviewable by a human in
   under ten minutes.
5. For every non-aligned gap (`INCOMPLETE`, `UNDERSPECIFIED`, `DIVERGENT`,
   `STALE_PLAN`), the handoff to implementation must name all four of:
   - **Destination artifact type** (e.g. PRD, FEAT, US, ADR, TD, TP) where
     the gap is resolved.
   - **Deliverable shape**: the concrete content to add (e.g. "a TD section
     answering X", "a US covering Y", "an ADR recording the Z choice").
   - **Suggested next workflow mode** (`frame`, `design`, `polish`, `build`,
     `validate`, `evolve`, `backfill`) — never a CLI command.
   - **Evidence references**: artifact paths plus line numbers (or section
     anchors) supporting the finding.
6. Create or identify follow-up work for every non-aligned gap using the
   handoff fields above.

### Validate

Use to check a single artifact instance against its governing template and
prompt and improve it in place.

1. Load the artifact instance and resolve its artifact type: read `ddx:`
   frontmatter when present (`ddx.type`, else inferred from `ddx.id`
   prefix); otherwise resolve by path or filename pattern against the
   artifact-type catalog the runtime exposes.
2. Load the artifact-type's `template.md`, `prompt.md`, and `meta.yml`
   from the resolved catalog path (see §Catalog Resolution).
3. Run structural conformance: required section headings from `template.md`
   are present, and required frontmatter fields from `meta.yml` are
   populated.
4. Run prompt-section conformance: every section the `prompt.md` asks for is
   answered in the instance or explicitly marked N/A with a reason.
5. Classify each finding keyed to the relevant template or prompt section
   using the Align taxonomy: `ALIGNED`, `INCOMPLETE`, `DIVERGENT`,
   `UNDERSPECIFIED`, `STALE_PLAN`, or `BLOCKED`.
6. Produce updates: when the user invoked validate to fix, apply edits
   in place for every finding the template + prompt comparison can
   resolve mechanically — typically `INCOMPLETE` findings (missing
   required sections, stale frontmatter shape, renamed headings). For
   findings classified as `DIVERGENT`, `UNDERSPECIFIED`, `STALE_PLAN`,
   or `BLOCKED` — which need human judgement — surface a §Align gap-to-
   implementation handoff for that specific finding instead of editing.
   When the user invoked validate to audit, surface a §Align handoff
   for every non-`ALIGNED` finding regardless of mechanical
   resolvability.

### Refresh

Use to bring every artifact instance under a project HELIX tree up to
date with the current canonical templates and prompts. §Refresh is
§Validate (fix-mode) applied across a whole project in one pass.

1. Resolve the project HELIX root per §Project Root Resolution.
   Enumerate every artifact instance under it. Group instances by
   activity directory (00-discover, 01-frame, …, 06-iterate). Skip
   anything that isn't an artifact instance (READMEs, plan
   sub-directories, generated files).
2. For each instance, run §Validate in fix-mode. When the runtime
   supports sub-agent dispatch, parallelise across the activity groups
   (one agent per activity); otherwise execute the groups in activity
   order.
3. Aggregate the per-instance §Validate outputs into a single report:
   per-classification counts using the unified taxonomy (`ALIGNED` /
   `INCOMPLETE` / `DIVERGENT` / `UNDERSPECIFIED` / `STALE_PLAN` /
   `BLOCKED`) plus the union of every §Align gap-to-implementation
   handoff §Validate produced.
4. §Refresh surfaces handoffs in the report. It does **not** itself
   file work items — that responsibility stays with the runtime: DDx
   runtimes may file work items in response, Claude Code runtimes may emit
   tracker issues, chat-only runtimes may simply display the report.
   This keeps §Refresh runtime-neutral while preserving §Align's
   tracker-mutation rules for runtimes that have a tracker.
5. §Refresh is read-only against templates and prompts in the skill
   catalog. If §Refresh reveals that a template itself needs to change,
   route through `evolve` against the catalog separately.

### Evolve

Use when the user wants to add, remove, amend, or thread a requirement through
the HELIX artifact stack.

1. Read the entry artifact's frontmatter; collect its `ddx.id` and
   `ddx.depends_on` list.
2. Walk the dependency graph in both directions: forward along
   `ddx.depends_on` (artifacts this one relies on — authority above) and
   reverse by scanning all governing artifacts for `ddx.depends_on` entries
   pointing back at this `ddx.id` (downstream impact).
3. When `ddx:` frontmatter is absent, fall back to filesystem traversal:
   activity-numbered directories in the project's HELIX layout supply the
   authority hierarchy; artifact-type directories supply the type
   relationships.
4. Detect conflicts with existing artifacts and open work.
5. Apply updates from the highest-authority artifact down: vision, PRD,
   feature specs/stories, architecture/ADRs, solution and technical
   designs, test plans, implementation plans, then code.
6. Surface conflicts explicitly when a downstream artifact contradicts an
   updated upstream — do not silently overwrite the downstream; route it
   through the §Align gap-to-implementation handoff instead.
7. Create follow-up work with dependencies where ordering matters.
8. Prefer **progressive evolution** of the specific affected artifacts over
   re-generating the stack. Converge on "verified + each finding-class folded
   into a gate" (a template check, an acceptance criterion, a concern
   propagation check, or a ratchet) — not on a bare reviewer "SHIP" verdict.
   Intrinsic gates (build, test, conformance, phantom-claim count) block;
   external adversarial review is advisory and never a hard gate.

### Design

Use when implementation needs design authority before build work.

1. Load governing artifacts, existing designs, implementation context, tests,
   and open work for the scope.
2. Draft problem statement, requirements, architecture decisions, interfaces,
   data model, errors, security, testing, sequencing, risks, and observability.
3. Iterate through self-critique until material changes converge.
4. Write the design to the project HELIX design location.
5. Derive ordered, verifiable implementation work from the design.

### Backfill

Use to reconstruct missing or incomplete HELIX artifacts from evidence.

1. Read available evidence: artifacts, implementation, tests, releases, and
   recorded decisions.
2. Separate confirmed facts from inference.
3. Reconstruct only what the evidence supports.
4. Mark uncertainty explicitly.
5. Create follow-up work for unresolved authority gaps.

### Review

Use for fresh-eyes review of plans, PRs, implementation, or recent work.

1. Scope the review narrowly.
2. Inspect governing artifacts, changed implementation, tests, and public
   projection relevant to the scope.
3. Report findings first, ordered by severity, with concrete evidence.
4. Run the **claims-vs-reality** check: any artifact assertion of a test,
   coverage figure, or emitted metric that does not exist is a blocking
   phantom-claim finding (zero-floor), not a stylistic note.
5. File durable follow-up work for actionable medium-or-higher findings in
   the project's work tracker.
6. A clean verdict is necessary but not sufficient: the loop converges only
   when the work is verified **and** each finding-class is folded back into a
   gate so it cannot silently recur. Drive fixes by progressive evolve against
   the specific finding, not by re-generating the artifact or implementation.
7. **Intrinsic gates block; external adversarial review is advisory.** The
   intrinsic gates — build, test, template conformance, the phantom-claim count
   — block convergence. An external adversarial reviewer (a separate tool or
   model) is advisory input only and must never be a hard gate: when it hangs,
   errors, or is unavailable, convergence is decided by the intrinsic gates.

### Polish

Use to refine work items before execution.

1. Load open work for the scope and any governing plan.
2. Run multiple passes for deduplication, coverage, acceptance quality,
   dependency correctness, sizing, and label hygiene.
3. Require execution-ready work items to name exact files, commands, checks, fields,
   or observable repository states.
4. If acceptance cannot be sharpened from governing artifacts, flag the work as
   not execution-ready and route it back through planning.

### Check And Next

Use when the safe next action is ambiguous, when the user asks "what's
next" / "what's blocked" / "plan the change", or when a single ask
straddles two or more flows declared in the marker (e.g. the prompt
names a data-pipeline artifact whose blocker is an infra prerequisite).

1. Inspect the queue, governing artifacts, and known blockers.
2. Decide conservatively among build, design, alignment, backfill, polish, wait,
   guidance, or stop.
3. Do not dispatch another workflow silently.
4. When recommending the next action against a specific gap, name it using
   the §Align gap-to-implementation handoff shape: destination artifact
   type, deliverable shape, suggested next workflow mode, and evidence
   references (paths plus line numbers). Never prescribe a CLI command.
5. If missing tracked work is discovered, create or recommend explicit work
   before returning the next action.

#### Cross-flow ask — owner-flow first, then prerequisite fan-out

A **cross-flow ask** is any prompt whose answer requires consulting more
than one flow in the marker. Three shapes recur:

- **Single-artifact ask whose blocker lives in another flow.** Example:
  "The monitoring dashboard needs a DNS record. Set this up." The
  monitoring-setup artifact is owned by `helix-data` (it lives under
  `pipelines/<scope>/` per the marker); the DNS record is owned by
  `helix-infra`. The data flow is the **owner-flow** because it owns
  the artifact named in the prompt. Infra is a **prerequisite-flow**
  that must satisfy a precondition before the data-flow item ships.
- **Multi-flow status query.** Example: "What's blocked across the
  project?" / "What's next?" against a marker with two or more flows.
  Every active flow in the marker is a candidate owner — none can be
  silently dropped.
- **PRD-needs-infra ask.** Example: "The PRD needs new infra — plan
  it." Product owns the PRD (owner-flow); infra owns the provisioning
  artifact downstream. The PRD edit and the infra plan are TWO
  artifacts in TWO flows, linked by a cross-flow edge.

Cross-flow contract (every cross-flow ask):

1. **Engage owner-flow first.** Identify the flow whose `root:` owns
   the named artifact (or the artifact the prompt's noun phrase most
   directly names). Call `Skill(<owner-flow>)` — `Skill(helix-data)`,
   `Skill(helix-infra)`, `Skill(helix-web)`, or `Skill(helix)` — as
   the first flow-skill tool_use of the turn. Do not jump straight to
   the prerequisite flow because its verb (DNS, deploy, provision)
   appears in the prompt — that's the verbose-but-stuck anti-pattern
   in cross-flow shape. The artifact's home flow wins.
2. **Read the owner-flow's named upstream artifacts.** From the
   marker's `root:` for the owner-flow, locate and Read the artifact
   the prompt references (e.g. `monitoring-setup.md`,
   `data-product-brief.md`, `prd-*.md`) BEFORE proposing any action.
   For each upstream named in `ddx.links:` or `informs` edges that
   the answer depends on, Read it too. Catalogue which artifacts
   exist (with path + status from frontmatter) and which are missing.
3. **Fan out to prerequisite-flows.** For each cross-flow
   prerequisite the owner-flow surfaces (e.g. the monitoring-setup
   prose says "dashboard URL needs DNS"; the PRD's acceptance
   criteria require a new VPC), call `Skill(<prerequisite-flow>)`
   for THAT flow before drafting the prerequisite-flow action. Each
   active flow that owns part of the answer gets its own Skill
   tool_use — silent multi-flow narration from a single skill call
   is a contract violation.
4. **For a multi-flow status query** ("what's blocked across the
   project?", "what's next?"), engage EVERY flow listed in the
   marker. Call `Skill(<flow-id>)` once per flow before reporting
   per-flow status. Answering from prose alone — reading the
   workspace files without firing a Skill tool_use for each flow —
   is the failure mode this rule prevents.

Cross-flow response shape (always emit all three):

- **Named upstream artifacts and their state.** A list of the
  artifacts the answer depends on, each annotated `exists` (with
  path + frontmatter `status:` if present) or `missing` (with the
  graph node that says it should exist). Example:
  `pipelines/customer-events/monitoring-setup.md` (exists,
  status: in-progress); `infra/dns/customer-events.tf` (missing,
  required by monitoring-setup prose).
- **Cross-flow prerequisites.** Name each prerequisite as
  "`<owner-flow>` needs `<prerequisite-flow>` to <verb> <object>
  before `<owner-flow>` can <ship-verb> <artifact>". Example:
  "helix-data needs helix-infra to provision the DNS record for
  `customer-events.metrics.example.com` before helix-data can mark
  monitoring-setup ready."
- **Concrete next action per flow.** For each flow with an action
  pending, emit a §Align gap-to-implementation handoff: destination
  artifact type (e.g. `network-iac` under `infra/`), the flow's mode
  (product / infra / data / web), and evidence paths with line
  numbers (e.g. `pipelines/customer-events/monitoring-setup.md:20`).
  Never prescribe a CLI command; the operator chooses dispatch.

Do not skip the owner-flow Skill call because the prompt is short or
the prerequisite verb is loud. Do not collapse multiple flows into a
single Skill call. The bench grades cross-flow rows by counting
per-flow `Skill(helix-<id>)` tool_use events; a confident prose
answer with no per-flow Skill call is the exact failure CF-02 and
CF-03 measure.

### Build And Run

Use only when the user explicitly asks for HELIX execution.

1. Build handles one bounded implementation pass for a selected work item.
2. Run handles the bounded operator loop over ready work.
3. Stay within the governing work item.
4. Do not broaden scope beyond the named work.
5. Verify with the project gate before reporting completion. Verification
   includes the self-validation mode-gate: acceptance criteria satisfied and the
   claims-vs-reality check clean (zero phantom claims). This is a verify-activity
   gate, not a literal validate-then-align-then-check command sequence.
6. **Not "done" until re-reviewed and the full stack is exercised with recorded
   evidence** (the `verification` concern — the evidence gate, distinct from
   `testing` strategy and the `e2e-framework` tooling). A green unit suite is
   not done: for a buildable product, drive the real user flows against the
   **running** system end-to-end with a whole-stack exercise appropriate to the
   product (for a UI web app that means ≥1 core flow via a whole-stack e2e that
   runs green — a **browser e2e** for a client-rendered UI, or an
   **HTTP+HTML-assertion e2e** for a server-rendered UI; either is first-class.
   The running UI MUST give current-location feedback: the active
   nav item shows a visible active state **and** `aria-current="page"`, with the
   e2e asserting that cue for ≥1 route (in the rendered markup for a server-
   rendered UI, via the browser for an SPA), required and never substituted by
   a class/style or screenshot assertion; for a service/CLI, the equivalent
   end-to-end invocation against the running system), do an adversarial
   re-review against the ACs
   and integration risks, and record the evidence artifacts — the command run +
   its exit status, the target URL/env, the core flows exercised, and the
   re-review checklist. **Verify-don't-trust**: never assert a result you did
   not observe; treat a self-reported "complete" as a hypothesis to verify.
   **Selection↔build coherence**: the built app must honor the *selected* slots —
   selecting `react-nextjs` then shipping a non-React app, or selecting an e2e
   framework then shipping no e2e, is a defect, not a quiet substitution (SSR/RSC
   is fine; the point is React/Next is present). A stack change mid-build is a
   **recorded deviation** (update the slot in `concerns.md` + reason + evidence),
   never silent. Honor the exceptions (library / docs-only / non-buildable work, or
   full-stack e2e genuinely infeasible — record the reason and substitute the
   strongest observable evidence). See
   `<plugin-root>/workflows/concerns/verification/practices.md`.
7. **Data-backed products ship a governed sample/seed dataset** (the
   `sample-data` concern — distinct from `testing`'s fixtures/factories). Seed
   the running product with **varied** data generated by a semantic faker
   library (the tech stack's named default — `@faker-js/faker` for
   `typescript-bun`, `Faker` for `python-uv`), **not** a couple of thin
   hardcoded rows, covering schema-relevant edge cases (empty, long, large,
   boundary, all status/enum variants) so the UI's
   empty/overflow/large-number/all-status states are exercised. Deliver it as a
   **governed, idempotent seed script** with guardrails: an explicit faker seed
   for determinism (with a stable locale and pinned faker version), clearly
   synthetic non-PII values, and never run against or mixed with production.
   Curated literal edge-case records inside the seed script are encouraged. See
   `<plugin-root>/workflows/concerns/sample-data/practices.md`.

### Commit

Use when verified work should be committed.

1. Inspect the diff and separate unrelated user changes.
2. Run the project gate.
3. Commit only the intended scope with traceable message text.
4. Preserve managed-execution history: never squash, rebase, amend, or filter
   branches containing runtime-generated execution commits.

### Release

Use for cutting a HELIX plugin release.

1. Confirm release scope and version.
2. Run required validation and site build.
3. Tag, push, and publish according to project release rules.
4. Report artifacts, tag, and verification results.

### Experiment

Use for metric-driven optimization loops.

1. Define the goal, metric, baseline, intervention, and stop condition.
2. Run bounded iterations.
3. Measure after each iteration.
4. Keep changes or revert/adjust based on metric evidence.
5. To validate a **methodology or skill change** (a workflow prompt, template,
   or this routing skill), use the **regression bench**: record a committed
   baseline, run a fixed brief from the bare prompt with the improved skill
   *installed* (never by redirecting reads), score intrinsic metrics against the
   baseline, and **keep what moved, cut what didn't**. The bench is the standing
   answer to "how do we know this change is impactful."

### Worker

Use to launch and monitor a background HELIX operator loop.

1. Start the run with durable logs and pid capture.
2. Poll sparingly for progress, blockers, or completion.
3. Report status without losing the run evidence.
4. Stop only when requested or when the workflow reaches a safe stopping point.

## Consult The Graph Before Authoring

When the user asks for a new artifact of type `T` in the active methodology `M`
(per the resolved marker), consult `M`'s `workflows/graph.yml` before drafting.
This is the runtime use of the methodology graph: the same edges the validator
checks govern what the skill should surface as prerequisites at authoring time.

1. Read `M`'s `workflows/graph.yml` (resolved via the §Catalog Resolution path
   for the active methodology's plugin root).
2. Find the node `n` whose `type` matches `library:T` or `local:T`.
3. Enumerate incoming edges to `n` whose `kind` is one of
   `{requires, contains, informs}`.
4. For each such edge `(src → n, kind, required)`:
   - If `required: true` AND no instance of `src.type` exists in this
     methodology's instance scope, **surface this as a prerequisite**. Per the
     resolved §Autonomy level, either ask whether to draft `src` first
     (`low`/`medium`), or draft `src` autonomously then `n` (`high`).
   - If `required: false` AND no instance of `src.type` exists, note it as a
     "consider also drafting" but do not block authoring of `n`.
5. Only after prerequisites are present (or the operator has explicitly chosen
   to skip them) proceed to author the requested artifact.
6. After authoring, populate `ddx.links` to point at existing upstream
   instances. **Do not invent links**: per Edge Authority Asymmetry, types
   declare what is possible and instances declare what is actual. Every
   `ddx.links` entry is a deliberate authoring decision, never a mechanical
   projection of a graph edge.

Graph consultation is **per-authoring**, not per-session: re-consult on every
new artifact request because the instance scope may have changed since the
previous turn (operator-side edits, parallel work, evolve passes).

If the graph carries a **non-standard or locally-added edge** (a project's
`workflows/graph.yml` introduces an edge not in the canonical HELIX library —
e.g. `prd requires market-validation-brief`), the same rules apply: a graph
edge governs what the skill surfaces, regardless of whether the edge matches
general HELIX knowledge. Surfacing only the canonical edges and skipping the
graph-declared ones is a graph-consultation defect, not an acceptable
shorthand.

## Alignment Content Migration

If a user asks whether content belongs in the right HELIX document, use align
mode. The alignment output must include a content migration ledger for every
misplaced content unit:

| Field | Required content |
|---|---|
| Source | Artifact path and line references |
| Content unit | Small named chunk of content |
| Classification | `keep`, `move`, `split`, `delete`, `needs-new-artifact`, or `decision-needed` |
| Destination | Exact destination artifact path or artifact type |
| Content to add | Destination-shaped draft content |
| Template fit | Destination section and blocking/warning checks |
| Destination risks | Any template check the proposed addition would fail |
| Follow-up | Tracker issue ID or explicit issue to create |

Do not remove content from one artifact unless the destination content and
follow-up work are captured durably.

## Operating Discipline

- Use the workflow contracts in this skill as the active interface; consult
  packaged workflow prompts only when deeper mode-specific detail is needed.
- For projects with a work tracker, obey work-item-first rules before writing
  files or tracker mutations.
- Do not silently start implementation when the request is planning, alignment,
  review, or routing.
- If the correct route is unclear, use check mode rather than guessing.
- Preserve the HELIX artifact authority hierarchy: vision, PRD,
  features/stories, architecture and ADRs, designs, tests, implementation
  plans, code.
- **Short affirmations inherit the prior turn's offered scope.** When the user
  replies with a bare confirmation (`"do it"`, `"yes"`, `"go"`) after the
  prior turn surfaced multiple branches or options, do not silently pick one.
  Ask which branch, or — if only one was recommended — restate it verbatim
  before acting.
- **Scope complaints and pasted-evidence reactions route to `align` or
  `evolve`, not to direct edits.** When the user pastes a snippet and says
  something like "this isn't going to scale" or "what is this BS", treat the
  complaint as evidence for §Align (find the upstream artifact that should
  govern the pattern) or §Evolve (thread the new constraint through the
  artifacts). Do not patch the pasted code in place.
- **Operator pushback on a reported blocker triggers an alignment surface,
  not a retry.** When the user pushes back on a claim like "this is blocked"
  or "you said this couldn't be done", the response must name the specific
  artifact-line evidence behind the blocker and route through the §Align
  handoff fields. Retrying the same operation without diagnosis is
  forbidden.
- **`check` mode returns status; design changes are a follow-up turn.** When
  asked "what's the situation with X" or "is X needed", surface the current
  state plus a §Align-shaped next-step recommendation. Do not bundle a design
  proposal in the same turn — the operator decides whether to invoke
  `design` or `evolve` next.
