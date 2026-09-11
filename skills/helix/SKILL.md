---
name: helix
description: |
  HELIX skill, the single public entrypoint for HELIX document and workflow
  work. Engage on prompts to frame, align, validate, evolve, refresh, design,
  backfill, review, polish, converge, audit, grill, or bootstrap (genesis)
  governed artifacts and work. Engage on any named HELIX artifact: PRD, ADR,
  FEAT, feature spec, technical design, implementation plan, test plan,
  runbook, release notes, user stories, roadmap, iteration plan, status
  report, requirements. Engage on "what's next", "plan the change",
  cross-flow queries, and human-iteration planning (roadmap, workstreams,
  sprint plan, status report). Engage on desired state vs implementation,
  specs behind code, and pruning work items against specs. Engage on "grill
  me" or stress-testing a plan one question at a time. Product, web, infra,
  and data are domain lanes that shape context and stop rules, not sibling
  skills or workflow modes.
argument-hint: "[intent or scope]"
---

# HELIX Router

Use this as the HELIX entrypoint. Users should not need to memorize individual
workflow skill names. Resolve the active scope, choose the relevant domain lane,
route to the smallest HELIX workflow mode that fits, then load and follow that
mode's contract from the catalog (§Mode Contracts).

Rule: do not add separate public `helix-*` skills. Add or refine a route inside
this skill instead.

## When to engage (read first; non-negotiable)

Engage this skill whenever any condition below is true, regardless of whether
the artifact content is attached, the workspace is empty, or the request looks
like a generic task. Engagement is the first tool action of the turn:

- **Skill-tool hosts** (Claude Code, Codex, opencode): invoke the `helix`
  skill through the host's skill tool first.
- **Hosts without a skill tool**: load this `SKILL.md` body via the host
  mechanism (`/helix`, skill auto-load, or a read of this file) first.

Narrating HELIX-shaped reasoning without that engagement action is a contract
violation.

Engage when:

- The prompt names a HELIX artifact (PRD, ADR, FEAT, feature spec, technical
  design, implementation plan, test plan, runbook, release notes, user
  stories, roadmap, iteration plan, status report, requirements), even when
  it asks to *review* or *expand* one whose content is not attached. This
  skill resolves the artifact path from the marker, graph, and cwd.
- The prompt uses a HELIX planning verb (frame, align, decompose, prioritize,
  propose, capture, review, decide, evolve, refresh) against a
  product/feature/requirements object → product lane, matching mode.
- The prompt uses an IaC verb (terraform/tofu/kubectl, provision/destroy/
  rotate, set up CI, manage credentials) → infra lane, after consulting
  `stop_at` triggers.
- The prompt uses a data-pipeline verb (backfill/ingest/migrate a table or
  schema, profile a source, write a data contract) → data lane.
- The prompt uses a web/frontend verb (deploy/ship to production, add
  monitoring for a user-facing flow, optimize page performance) → web lane,
  after consulting `stop_at` triggers.
- The prompt asks "what's next", "plan the change", "decide what to do", or
  any cross-flow query that needs the marker to answer → `check` mode.
- The prompt asks to "grill me", "interview me" about a plan/design, or to
  stress-test decisions one question at a time → `grill` mode.

## Routing Axes

Once engaged, route by four axes:

1. **Scope instance**: which `flows:` entry in `.helix.yml` owns the target
   artifact or requested project area.
2. **Domain lane**: product, web, infra, data, or another documented lane
   implied by the scope and artifact concerns. Lanes are internal context,
   never public skill names.
3. **Workflow mode**: one HELIX document/workflow action (§Routing Rules).
4. **Autonomy / stop rules**: whether the runtime can proceed or must pause
   before a state-changing action (§Autonomy).

| Domain lane | Triggers | Required observable behavior |
|---|---|---|
| `product` | HELIX artifact named; planning verb against product/feature/requirements; cross-flow query | (a) Read `.helix.yml` AND the bound graph BEFORE any Write/Edit; (b) Read named upstream artifacts (vision, PRD, feature spec) per the graph BEFORE drafting; (c) cite `ddx.links` / `informs` edges in any new artifact |
| `infra` | IaC verb (terraform/tofu/kubectl, provision/destroy/rotate); CI/credentials ops | (a) Consult `library/skill-prompts/stop-at-triggers.yml` for `apply` or `secret_read` triggers BEFORE any Bash; (b) Read infra-shaped artifacts (architecture, runbook, deployment-checklist); (c) explicit confirmation prompt before terraform/tofu/kubectl/credential operations |
| `data` | Data-pipeline verb (backfill/ingest/migrate, profile a source, data contract) | (a) Read data-contract / data-quality-expectations / data-architecture artifacts; (b) cite producer/consumer or PII/governance posture in prose; (c) defer schema mutations behind a `stop_at` confirmation |
| `web` | Web/frontend verb (deploy/ship, add monitoring for a user flow, optimize page perf) | (a) Read architecture / design-system / monitoring-setup / runbook artifacts in the deploy-flow scope; (b) cite Web Vitals / RUM / page-error vocabulary in prose; (c) defer production deploys behind a `stop_at` confirmation |

Skipping lane-required behavior is a routing failure even if the workflow mode
is otherwise correct.

## Activation Discipline (in order, every time the skill engages)

### 1. Locate the marker

Find `.helix.yml` by walking up from the current working directory to the
repository root (the directory containing `.git/`). Stop at the first marker
found. A marker at the repository root governs work started in any
subdirectory; do not give up after searching cwd only.

### 2. Read the marker and bind the graph before any Write/Edit

Before the first Write or Edit of the session, read the `.helix.yml` marker
and bind the methodology graph via §Catalog Resolution. Skipping either is a
contract violation: it produces artifacts narrated from training rather than
anchored to the workspace's catalog and prerequisite chain. A graph bind is
always achievable in supported layouts, so a missing project-local
`workflows/` is never a reason to stop or skip edits; bind from a later
resolution step and proceed. A read whose target does not resolve does not
count. The order of the two reads is not constrained. This invariant is
independent of autonomy level: `high` autonomy waives the human-in-the-loop
ask, not workspace grounding. When the marker is absent and the skill engages
by heuristic (§3), the failed marker lookup satisfies the marker read and the
shipped catalog satisfies the graph bind.

### 3. Decide activation state

- **Marker present and well-formed**: the `flows[]` list (legacy alias
  `methodologies[]`, accepted with a warning) is the authorization boundary.
  If `helix` is listed, this skill is active for the listed `root:` scope. If
  not, defer to the listed flow's process. A minimal marker:

      flows:
        - id: helix
          root: docs/helix/

- **Several distinct flows and an ambiguous verb** (for example `helix` and
  `helix-infra`, prompt "plan the rollout"): resolve cwd-under-root →
  `defaults.flow` → single entry. If none resolves, emit the disambiguation
  banner naming both candidate flows with their roots and ask which applies.
  Do not silently pick one, and do not route to the infra lane under `helix`
  because the prompt contains an infra-adjacent noun.
- **Several helix instances** (`instance:` values with different roots): if
  cwd lies inside exactly one root, choose it and say so; otherwise emit the
  banner listing instances and roots, then stop until the operator chooses.
- **Marker present and malformed** (YAML error, missing required keys, root
  outside repo, duplicate id, nonexistent root): STOP and report the error
  with file and line. Do not fall back to heuristics.
- **Marker absent, heuristic present** (`docs/helix/` tree or
  `workflows/methodology.yml`): emit this banner before any other output,
  then proceed with the shipped catalog; a `docs/helix/` tree without a
  marker is not a reason to decline edits:

      No .helix.yml found. Activating helix by heuristic (path: <heuristic-path>).
      Add a .helix.yml marker at the repository root to make this explicit.

- **Marker absent, no heuristic**: report no active flow. If asked for a
  machine-readable response, return `{"active": []}`.

### 4. Enforce scope

Every write or edit must target a path inside the active flow's `root:`. For
a write outside scope: refuse, surface the marker entry that scoped the flow
and the offending path, and ask whether to (a) broaden the marker, (b)
redirect under scope, or (c) cancel. When several flows are declared, the
flow whose root contains the cwd wins; otherwise follow the §3 resolution
chain. Never invent a selector outside the marker.

### 5. Author and edit artifacts

Before authoring or editing an instance, bind the type's `template.md`,
`prompt.md`, `meta.yml`, and active voice profile from the resolved catalog
and load `modes/_authoring.md` (graph prerequisites, links, edge rules). Do
not author from the activity table alone.

Edit existing instances; Write only new ones. Verify with a Read: a
successful Read of the resolved path means the instance is live and every
modification, however small, goes through Edit, which preserves frontmatter
and operator-added content. Only a missing file authorizes Write.

Instance edges (PRD → FEAT, ADR → technical design) belong in the instance's
frontmatter under `ddx.links:`, never in the body or in this skill. Cross-flow
edges are declared in `external_edges:` of the graph first, then in the
instance with `cross_flow: true` (legacy alias `cross_methodology: true`).

### 6. Authorization boundary

Reject, without engaging, any prompt that names a flow (in natural language or
through a runtime alias) that the marker's `flows:` list does not authorize.
This overrides every engage trigger. Emit this diagnostic, substituting the
flow name and marker flows, then stop with no reads, writes, routing, or
"but I can still help" offer:

    Cannot engage <flow-name> here — the requested flow `<flow-name>`
    is not authorized: the .helix.yml marker does not list it.
    The marker authorizes only: <comma-separated list of marker flows>.
    To proceed, either (a) add `<flow-name>` to the marker's `flows:`
    list, or (b) re-run with a flow the marker authorizes.

Re-interpreting an unauthorized flow as an authorized one (routing
`helix-infra` work through the infra lane under `helix`) is a violation.
Runtime aliases may choose among marker-authorized flows; they cannot broaden
the marker.

### 7. Frontmatter round-trip

Never rewrite unknown frontmatter keys. When editing a body, preserve
`ddx.id`, `ddx.review`, `ddx.links`, vendor-namespaced (`x-*`) and legacy
(`relationships:`, `depends_on:`) keys byte-equivalent and in order. Legacy →
new key translation is explicit migration work, never a side effect.

## Routing Rules

Prefer the first matching route:

| User intent | Workflow mode |
|---|---|
| Convert rough intent into governed HELIX work | input |
| Grill / interview / stress-test a plan or design until shared understanding (one question at a time) | grill |
| Create or refine product vision, PRD, feature specs, or user stories | frame |
| Reconcile artifacts, check traceability, find drift, align documents, or move content between artifact layers | align |
| Check an artifact instance against its template and prompt; edit resolvable findings in place | validate |
| Bring every artifact instance up to date with the current templates and prompts | refresh |
| Thread a new, changed, removed, or incident-driven requirement through existing artifacts | evolve |
| Create a technical design before implementation | design |
| Reconstruct missing or incomplete docs from evidence | backfill |
| Fresh-eyes review of recent work, PRs, plans, or implementation | review |
| Refine work items for execution readiness | polish |
| Plan or report a human iteration — sequence a roadmap, define workstreams, cut an iteration/sprint plan, write a status report | iterate |
| Decide the next safe HELIX action | check |
| Run an optimization experiment | experiment |
| Bootstrap a brand-new project from bare intent (name, research, vision, scaffold) | genesis |
| Drive a plan or completed work to convergence: review adversarially, fix, re-review until clean | converge |
| Audit where a project stands (specs↔impl↔tests↔ACs aligned? complete? next action?) | project-audit |
| Decompose an oversized code module/file into encapsulated units behind a verify gate | decompose-module |
| Build up end-to-end coverage as a ladder of increasingly complex real-client scenarios | e2e-ladder |
| Hand governed work to the runtime for execution, source control, or packaging | runtime-handoff |

When multiple routes fit, choose the highest-authority planning route first:
`frame` before `design`, `align` before `evolve` when the task is diagnostic,
and `evolve` before handing work to the runtime when requested implementation
lacks governing artifact coverage. Prefer `grill` over `input`/`frame`/`design`
when the operator asks to be interviewed or to stress-test decisions before
authoring; do not steal generic turns that only say "plan" without grill
intent.

Iteration-cadence precedence: authoring or updating a roadmap, iteration plan,
or status report routes to `iterate` even when a change triggers it.
Reviewing an iteration against its plan is `iterate` (a status report);
`review` stays fresh-eyes critique of work products, PRs, and plans.

## Mode Contracts

Each mode's contract is one file, `modes/<mode>.md`, in the bound catalog:
`workflows/modes/` in source checkouts and vendored trees, `references/modes/`
in generated packages, resolved by §Catalog Resolution. After routing, load
the routed mode's file before acting and follow it as the active interface.
Modes that create or edit artifact instances also load `modes/_authoring.md`.
Reports (alignment, validation, refresh, check) use the shape in
`modes/_report.md` so runtimes and evaluations can consume them. Mode files
point at their deeper procedure under `actions/` when one exists; consult it
only when the contract needs more step detail.

Mode files: `workflows/modes/input.md`, `workflows/modes/grill.md`,
`workflows/modes/frame.md`, `workflows/modes/align.md`,
`workflows/modes/validate.md`, `workflows/modes/refresh.md`,
`workflows/modes/evolve.md`, `workflows/modes/design.md`,
`workflows/modes/backfill.md`, `workflows/modes/review.md`,
`workflows/modes/polish.md`, `workflows/modes/iterate.md`,
`workflows/modes/check.md`, `workflows/modes/experiment.md`,
`workflows/modes/genesis.md`, `workflows/modes/converge.md`,
`workflows/modes/project-audit.md`, `workflows/modes/decompose-module.md`,
`workflows/modes/e2e-ladder.md`, `workflows/modes/runtime-handoff.md`, plus
the shared `workflows/modes/_authoring.md` and `workflows/modes/_report.md`.

## Catalog Resolution

When a mode needs a mode contract, artifact template, prompt, quality
criteria, voice registry, concerns library, slots, stop triggers, or the
methodology graph, resolve paths in this deterministic fall-through order; the
first source that resolves wins. Never demote project-local or
source-checkout ranks below an installed plugin.

1. **Marker `graph:` pointer**: if the active `.helix.yml` declares a
   `graph:` (or `catalog:`) path that resolves, bind it. A set-but-broken
   pointer emits a one-line warning and falls through; it never blocks.
2. **In-tree project catalog**: `workflows/graph.yml`, `workflows/modes/`,
   and `workflows/activities/<NN>-<activity>/artifacts/<type>/`, found by
   walking up from cwd to the directory holding the resolved marker. This is
   the self-hosting case (the HELIX repo and consumers that vendor the
   catalog). Skip this step when there is no marker.
3. **Source-checkout / full plugin-dir catalog**: from the realpath of this
   `SKILL.md`, bind `../../workflows/...` when the skill lives at
   `skills/helix/SKILL.md` inside a HELIX checkout, a `--plugin-dir` tree, or
   a full-repo plugin install.
4. **Plugin env root (additive)**: if steps 2–3 did not bind and
   `$GROK_PLUGIN_ROOT` or `$CLAUDE_PLUGIN_ROOT` is set, try
   `<env-root>/workflows/...` then `<env-root>/skills/helix/references/...`.
5. **Generated `references/` floor**: `references/graph.yml`,
   `references/modes/`, `references/activities/...`, `references/concerns/`,
   `references/actions/`, `references/templates/`, and
   `references/voice.yml` relative to this `SKILL.md`, shipped in plugin
   packages and skill bundles so a catalog always resolves.
6. **Fail closed**: if nothing binds, stop with a diagnostic listing every
   path attempted. Never invent templates or contracts from training data.

Same-source rule: once a catalog source binds, load graph, modes, templates,
prompts, meta, voice, concerns, and stop triggers from that same bind. State
which source bound when it is not the generated floor (for example "catalog:
in-tree `workflows/graph.yml`"). Adopter projects need only `.helix.yml` and
instance documents; they never need to copy templates.

The seven activities and the artifact types they own (metadata queries only;
authoring always binds the real template, prompt, and meta from a resolved
source):

| Activity | Artifact types (directory names under `<activity>/artifacts/`) |
|---|---|
| `00-discover` | `business-case`, `competitive-analysis`, `data-flow-analysis`, `market-analysis`, `opportunity-canvas`, `product-vision`, `resource-summary` |
| `01-frame` | `compliance-requirements`, `concerns`, `feasibility-study`, `feature-registry`, `feature-specification`, `parking-lot`, `pr-faq`, `prd`, `principles`, `research-plan`, `risk-register`, `roadmap`, `security-requirements`, `stakeholder-map`, `threat-model`, `user-stories`, `validation-checklist` |
| `02-design` | `adr`, `architecture`, `contract`, `data-design`, `design-system`, `proof-of-concept`, `security-architecture`, `solution-design`, `tech-spike`, `technical-design`, `data-architecture` |
| `03-test` | `security-tests`, `story-test-plan`, `test-plan`, `test-procedures`, `test-suites`, `data-quality-expectations` |
| `04-build` | `implementation-plan` |
| `05-deploy` | `deployment-checklist`, `monitoring-setup`, `release-notes`, `runbook` |
| `06-iterate` | `improvement-backlog`, `iteration-plan`, `metric-definition`, `metrics-dashboard`, `security-metrics`, `status-report` |

Each type directory holds `template.md`, `prompt.md`, `meta.yml`, and an
`example.md`. Concern slots and their shipped defaults live in
`workflows/concerns/slots.yml` (floor: `references/concerns/slots.yml`);
defaults are starting points a project overrides, not choices HELIX imposes.

## Voice Resolution

Load the voice registry (`workflows/voice.yml`, floor `references/voice.yml`)
from the same bind as the graph. Resolve the active profile from the artifact
type's `meta.yml`: `voice: <profile>` or `voice.profile: <profile>` (with
declared section overrides); a missing `voice` means the registry's
`default_profile` (`artifact-signal`).

| Profile | Conciseness | Use |
|---|---:|---|
| `machine-facts` | 1/10 | Extracted facts, context digests, generated indexes, machine-facing state. |
| `artifact-signal` | 2/10 | HELIX artifacts, templates, prompts, metadata, alignment and validation reports. |
| `public-site` | 3/10 | Microsite pages, public demos, introductions, catalog summaries. |
| `human-facing` | 5/10 | Deliverables projected for clients, sponsors, and executives: decks, one-pagers, briefs. Subset the source, never contradict it; no HELIX vocabulary in the body. |

Apply the profile as artifact contract, not generic polish. For
`artifact-signal`, lead with decisions, requirements, constraints, evidence,
risks, or open questions; preserve IDs, paths, commands, metrics, statuses,
trace links, assumptions, non-goals, and acceptance criteria; keep
specifications focused on intent rather than implementation status. A prose
tool (for example Sloptimizer) may audit or rewrite against the active
profile when available; HELIX never requires one.

## Project Root Resolution

When a mode enumerates artifact instances in the operator's project (refresh
and similar batch operations), resolve the project HELIX root in order:
(1) an explicit path given at invocation; (2) a runtime-supplied project
config value when present; (3) the convention `docs/helix/` under the working
directory with `00-discover` … `06-iterate` subdirectories. If none resolves
to a directory with the expected activity subdirectories, surface a setup gap
rather than improvising. Chat-only runtimes require option 1.

## Autonomy

HELIX expresses an autonomy policy; the runtime supplies the agency. The
policy is a three-position spectrum controlling how often a workflow pauses
for confirmation, never which activities run.

| Level | Behavior |
|---|---|
| `low` | Ask before each step and before creating each downstream artifact. Do not infer unconfirmed scope. Concern selection stays interactive. |
| `medium` (default) | Create deterministic non-conflict artifacts; pause when ambiguity or conflict blocks deterministic progress. Prompt for concern selection when none exists. |
| `high` | Create downstream artifacts without pausing unless a hard stop blocks progress; record assumptions rather than asking. Infer concern selection from the product's nature and record it as an assumption. |

Resolution precedence (first match wins): per-invocation override (the
operator names a level in the prompt) → the `autonomy:` block in `.helix.yml`
→ default `medium`. The autonomy signal lives only in runtime-neutral
artifacts.

Hard-stop invariant (all levels): autonomy changes the pause threshold, never
the stop floor. Stop and surface to a human when two higher-or-equal-authority
artifacts truly contradict, when the next action is destructive or
irreversible and unauthorized, or when a decision only a human can make is
required. Never-collapse-the-loop invariant: autonomy changes checkpoint
density only; a high-autonomy run executes the same activities a low-autonomy
run would, pausing less often.

Stop triggers (`stop_at`) are a hard floor at every level. The authoritative
list is `library/skill-prompts/stop-at-triggers.yml`; load it when the skill
engages and consult it before every state-changing tool call. A repo may add
triggers under `autonomy.stop_at_extensions:` in `.helix.yml`; base triggers
cannot be removed.

| Trigger id | Fires on |
|---|---|
| `marker_edit` | Write/Edit on `.helix.yml` |
| `cross_methodology_edge_creation` | Write/Edit introducing `cross_methodology: true` or `cross_instance: true` |
| `branch_or_merge` | Bash running `git checkout|merge|push|reset|rebase|cherry-pick` or `gh pr merge|create` |
| `secret_read` | Read or Bash targeting `.env`, `.tfvars`, `credentials.json`, `.pem`, `id_rsa(.pub)`, `private_key`, `.key`, `secrets/` |
| `large_diff` | Single Write/Edit whose content exceeds 500 lines (per call) |
| `apply` | Bash running `terraform apply`, `tofu apply`, `databricks jobs|pipelines run|update`, `kubectl apply|delete|patch` |

When a trigger matches, name the trigger and the proposed action, ask whether
to proceed, and wait ("About to run `terraform apply` in infra/prod — should
I proceed?"). Generic `ok?` prompts do not satisfy the contract. At every
level, name the routing decision in the first text block when routing
silently via `defaults.flow`; silent routing is allowed, unspoken routing is
not.

## Operating Discipline

- Prefer the product unit (or methodology content that changes behavior) over
  process redesign. Bound process machinery, freeze it, deliver.
- Do not skip real defect checks (tests, product ACs, claims-vs-reality,
  scope discipline) under cover of shipping faster.
- For projects with a work tracker, obey work-item-first rules before writing
  files or mutating the tracker.
- Do not silently start implementation when the request is planning,
  alignment, review, or routing. If the correct route is unclear, use `check`
  rather than guessing.
- Preserve the artifact authority hierarchy: vision, PRD, features/stories,
  architecture and ADRs, designs, tests, implementation plans, code.
- Short affirmations ("do it", "yes") inherit the prior turn's offered scope.
  When several branches were offered, ask which; when one was recommended,
  restate it exactly before acting.
- Scope complaints and pasted-evidence reactions ("this isn't going to
  scale") route to `align` or `evolve`, never to direct edits of the pasted
  code.
- Operator pushback on a reported blocker triggers an alignment surface, not
  a retry: name the artifact-line evidence behind the blocker and route
  through the §Align handoff fields.
- `check` returns status; design changes are a follow-up turn the operator
  chooses.
