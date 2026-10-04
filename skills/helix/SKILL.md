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
  me" or stress-testing a plan one question at a time. Engage on decks,
  slides, one-pagers, briefs, and client-ready or executive documents built
  from governed artifacts (present). Product, web, infra, and data are
  domain lanes that shape context and stop rules, not sibling skills.
argument-hint: "[intent or scope]"
---

# HELIX Router

Use this as the HELIX entrypoint. Resolve the active scope, choose the domain
lane, route to the smallest fitting workflow mode, then follow that mode's
contract from the catalog (§Mode Contracts).
Rule: do not add separate public `helix-*` skills. Add or refine a route
inside this skill instead.

## When to engage

Load this skill through the host's skill tool or read this file. Resolve
missing artifact paths from the marker and catalog. Engage when the prompt
names a HELIX artifact (see the frontmatter description), even to *review* or
*expand* one whose content is not attached, or when it uses a lane trigger from
§Routing Axes (infra and web triggers consult `stop_at` first). Also engage on:
"what's next", "plan the change", or a cross-flow query needing the marker →
`check`; "grill me" or stress-testing decisions one question at a time →
`grill`; a deck, slides, one-pager, brief, memo, or client-ready document built
from project artifacts → `present`.

## Routing Axes

Route by four axes: (1) **scope instance**, the `flows:` entry in
`.helix.yml` that owns the target; (2) **domain lane**, internal context and
never a public skill name; (3) **workflow mode** (§Routing Rules);
(4) **autonomy and stop rules** (§Autonomy).

| Domain lane | Triggers | Required observable behavior |
|---|---|---|
| `product` | HELIX artifact named; planning verb (frame, align, decompose, prioritize, propose, capture, review, decide, evolve, refresh) against a product/feature/requirements object; cross-flow query | (a) Read `.helix.yml` and bind the graph before editing; (b) read the target and governing artifacts relevant to the request; (c) record supported `ddx.links` when the artifact type calls for them |
| `infra` | IaC verb (terraform/tofu/kubectl, provision/destroy/rotate); set up CI; manage credentials | (a) Consult the stop triggers (`workflows/stop-triggers.yml`) for `apply` or `secret_read` before any shell command; (b) Read infra-shaped artifacts (architecture, runbook, deployment-checklist); (c) explicit confirmation prompt before terraform/tofu/kubectl/credential operations |
| `data` | Data-pipeline verb (backfill/ingest/migrate a table or schema, profile a source, write a data contract) | (a) Read data-contract / data-quality-expectations / data-architecture artifacts; (b) cite producer/consumer or PII/governance posture in prose; (c) defer schema mutations behind a `stop_at` confirmation |
| `web` | Web/frontend verb (deploy/ship to production, add monitoring for a user-facing flow, optimize page performance) | (a) Read architecture / design-system / monitoring-setup / runbook artifacts in the deploy-flow scope; (b) cite Web Vitals / RUM / page-error vocabulary in prose; (c) defer production deploys behind a `stop_at` confirmation |

Skipping lane-required behavior is a routing failure even when the mode is
correct.

## Activation Discipline (in order, every time the skill engages)

### 1. Locate the marker

Walk up from cwd to the repository root (the directory containing `.git/`);
the first `.helix.yml` found governs work started in any subdirectory.

### 2. Read the marker and bind the graph before any file write or edit

Read the marker and resolve the graph through §Catalog Resolution, trying the
remaining catalog locations when the project has no `workflows/` directory.
Use a graph that was successfully read. This applies at every autonomy level.
Under heuristic activation (§3), the failed marker lookup and the shipped
catalog provide the context.

### 3. Decide activation state

- **Marker present and well-formed**: the `flows[]` list (legacy alias
  `methodologies[]`, accepted with a warning) is the authorization boundary.
  `helix` listed → active for the listed `root:`; not listed → defer to the
  listed flow's process. Minimal marker:

      flows:
        - id: helix
          root: docs/helix/

- **Several flows or instances and an ambiguous target**: resolve
  cwd-under-root → `defaults.flow` → single entry; if none resolves, emit the
  disambiguation banner and stop until the operator chooses. Never silently
  pick one. Detail: `modes/check.md` §Flow disambiguation.
- **Marker present and malformed** (YAML error, missing required keys, root
  outside repo, duplicate id, nonexistent root): STOP and report the error
  with file and line; no heuristic fallback.
- **Marker absent, heuristic present** (`docs/helix/` tree or
  `workflows/workflow.yml`): emit this banner before any other output, then
  proceed with the shipped catalog; the missing marker is not a reason to
  decline edits:

      No .helix.yml found. Activating helix by heuristic (path: <heuristic-path>).
      Add a .helix.yml marker at the repository root to make this explicit.

- **Marker absent, no heuristic**: report in plain language that no active flow
  was found.

### 4. Enforce scope

Every write or edit targets a path inside the active flow's `root:`. For a
write outside scope: refuse, surface the scoping marker entry and the offending
path, and ask whether to (a) broaden the marker, (b) redirect under scope, or
(c) cancel. With several flows, the flow whose root contains cwd wins;
otherwise follow the §3 chain. Never invent a selector outside the marker.

### 5. Author and edit artifacts

Bind the type's `template.md`, `prompt.md`, `meta.yml`, and active voice
profile from the resolved catalog and load `modes/_authoring.md` first; never
author from the catalog listing alone. Principles resolve project-first: the project's
`01-frame/principles.md` when it exists, else `workflows/principles.md`
(floor `references/principles.md`); no merging. Create an instance only when
its file is missing; if the resolved path reads successfully, every
modification, however small, is an in-place edit that preserves frontmatter
and operator-added content. Instance edges (PRD → FEAT, ADR → technical
design) live in the instance's `ddx.links:` frontmatter, never in the body or
this skill; cross-flow edges are declared in the graph's `external_edges:`
first, then in the instance with `cross_flow: true` (legacy alias
`cross_methodology: true`).

### 6. Authorization boundary

Reject, without engaging, any prompt that names a flow (in natural language
or through a runtime alias) the marker's `flows:` list does not authorize;
this overrides every engage trigger. Emit this diagnostic, then stop with no
reads, writes, routing, or "but I can still help" offer:

    Cannot engage <flow-name> here — the requested flow `<flow-name>`
    is not authorized: the .helix.yml marker does not list it.
    The marker authorizes only: <comma-separated list of marker flows>.
    To proceed, either (a) add `<flow-name>` to the marker's `flows:`
    list, or (b) re-run with a flow the marker authorizes.

Re-interpreting an unauthorized flow as an authorized one (routing
`helix-infra` work through the infra lane under `helix`) is a violation.
Runtime aliases choose among authorized flows; they cannot broaden the marker.

### 7. Frontmatter round-trip

Never rewrite unknown frontmatter keys. When editing a body, keep `ddx.id`,
`ddx.review`, `ddx.links`, vendor-namespaced (`x-*`) and legacy
(`relationships:`, `depends_on:`) keys byte-equivalent and in order. Legacy →
new key translation is explicit migration work, never a side effect.

### 8. Externally authored artifacts (the checkout cycle)

`ddx.authoring.home` says where an instance is authored: `repo` means the
Markdown file **is** the document; `external-tool` means the document lives in
a collaboration tool and the file carries its identity plus, after a check-in,
a copy of its content. Definitions: `workflows/artifact-schema.md` (Authoring
home); practice: `workflows/conventions.md`.

- **Default to `repo`.** Choose `external-tool` only on a demonstrated need for
  heavy human manipulation of format or content (a canvas iterated live, a deck
  whose layout is the deliverable); collaboration alone is not the test. `home`
  is fixed at creation; changing it is a deliberate migration, never a side
  effect of an edit.
- **Never edit an `external-tool` body to change its content.**
  `authoring.origin` is the write surface; editing the Markdown silently forks
  the artifact and the next check-in overwrites the fork. Route the change to
  the tool and report that you did.
- **`state: checked-out` content is undependable.** Before the first check-in
  the body is identity and description only; after a later checkout it is the
  previous copy. Do not quote it as current, set `ddx.status: approved` on it,
  or approve anything depending on it. Surface the checkout: name the artifact,
  its `origin`, and what it blocks.
- **`state: checked-in` bodies are the read surface.** `authoring.export` is
  the committed original; `authoring.export_sha256`, when present, is its
  digest at check-in. A digest that no longer matches the export means the body
  is stale: say so and route to a fresh check-in. A missing digest means
  unknown, not mismatched.
- **`state` is terminal in neither direction.** A checked-in document returns
  to `checked-out` for its next revision, reusing `origin`, `export`, and
  `export_sha256`; checkout never deletes content the repository holds. A
  check-in is one change carrying the body, export file, digest, and `state`
  flip together. Checking in makes approval possible; it is not approval.
- Producing a check-in body from an external document is a runtime capability.
  If the runtime offers none, say so and leave `state` alone; hand-transcribing
  and flipping `state: checked-in` claims a fidelity the repository cannot
  back.

## Concern slot resolution

A **slot** is an exclusive functional position a project fills exactly once
(frontend framework, language runtime, e2e tool, auth backend). Slots and
shipped defaults are declared in `concerns/slots.yml` (via §Catalog
Resolution); read them there, not from this skill. Membership is derived from
each concern's `## Slot` section. Resolve each needed slot in this order, first
match wins: (1) operator override in `docs/helix/01-frame/concerns.local.yml`,
read before `concerns.md` exists; (2) the `defaults:` map in `slots.yml`; (3) a
recorded assumption inferred from the product's nature. Select each slot
**once per session** during §Frame step 2 and record the filler plus its source
(`operator-override`, `shipped-default`, or `assumption`) in `concerns.md`.
Propagation downstream is a later gate (`check`/`polish`), never a
re-selection. Detail: `modes/frame.md`.

## Routing Rules

Prefer the first matching route:

| User intent | Workflow mode |
|---|---|
| Convert rough intent into governed HELIX work | input |
| Grill / interview / stress-test a plan or design until shared understanding (one question at a time) | grill |
| Create or refine product vision, PRD, feature specs, or user stories | frame |
| Reconcile relevant documents, check traceability, find drift, or place content in the right artifact | align |
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
| Explicitly audit a named scope across specs, implementation, and tests | project-audit |
| Decompose an oversized code module/file into encapsulated units behind a verify gate | decompose-module |
| Build up end-to-end coverage as a ladder of increasingly complex real-client scenarios | e2e-ladder |
| Turn governed artifacts into a deck, one-pager, or brief for clients, sponsors, or executives | present |
| Hand governed work to the runtime for execution, source control, or packaging | runtime-handoff |

When several routes fit, take the highest-authority planning route: `frame`
before `design`; `align` before `evolve` when the task is diagnostic;
`evolve` before a runtime handoff when the requested implementation lacks
governing coverage. `grill` beats `input`/`frame`/`design` when the operator
asks to be interviewed or to stress-test decisions before authoring; a bare
"plan" is not grill. A roadmap, iteration plan, status report, or review of an
iteration against its plan routes to `iterate` even when a change triggers it;
`review` stays fresh-eyes critique of work products, PRs, and plans.

## Mode Contracts

Each mode's contract is one file, `modes/<mode>.md`, in the bound catalog
(§Catalog Resolution): one per routed mode plus the shared
`workflows/modes/_authoring.md` and `workflows/modes/_report.md`. After routing, load the routed mode's file and
follow it as the active interface; modes that create or edit instances also
load `modes/_authoring.md`. Use `modes/_report.md` when a structured report is
requested or required by a runtime consumer. Consult a mode's `actions/`
procedure only when the contract needs more step detail. The `present` mode
names the `workflows/deliverables/` files (floor `references/deliverables/`)
it reads.

## Catalog Resolution

To resolve a mode contract, template, prompt, quality criteria, voice
registry, concerns, slots, principles, stop triggers, or the graph, use this
fall-through order; the first source that resolves wins, and project-local or
source-checkout ranks never demote below an installed plugin.

1. **Marker `graph:` pointer**: a `graph:` (or `catalog:`) path in the
   active `.helix.yml` that resolves; a set-but-broken pointer warns once
   and falls through.
2. **In-tree project catalog**: `workflows/graph.yml`, `workflows/modes/`,
   and `workflows/activities/<NN>-<activity>/artifacts/<type>/`, walking up
   from cwd to the directory holding the marker (self-hosting and vendored
   cases). Skip when there is no marker.
3. **Source-checkout / full plugin-dir catalog**: `../../workflows/...` from
   the realpath of this `SKILL.md` when it lives at `skills/helix/SKILL.md`
   inside a HELIX checkout, a plugin-dir tree, or a full-repo plugin install.
4. **Plugin env root (additive)**: if steps 2–3 did not bind and the host
   exposes a plugin root through its environment, `<plugin-root>/workflows/...`
   then `<plugin-root>/skills/helix/references/...` (the install guide names
   the variable per host).
5. **Generated `references/` floor** beside this `SKILL.md`, shipped in
   plugin packages and skill bundles so a catalog always resolves; it mirrors
   the `workflows/` catalog.
6. **Fail closed**: if nothing binds, stop with a diagnostic listing every
   path attempted. Never invent templates or contracts from training data.

Same-source rule: once a source binds, load everything (graph, modes,
templates, prompts, meta, voice, concerns, principles, references, stop
triggers) from it, and state which source bound when it is not the floor
("catalog: in-tree `workflows/graph.yml`"). Adopters need only `.helix.yml`
and instance documents; they never copy templates. Artifact types: one
directory per type under `<activity>/artifacts/`, enumerated in `graph.yml`;
each holds `template.md`, `prompt.md`, `meta.yml`, and `example.md`.

## Voice Resolution

Load the voice registry (`workflows/voice.yml`, floor `references/voice.yml`)
from the same bind as the graph. The active profile comes from the type's
`meta.yml` (`voice: <profile>` or `voice.profile: <profile>` with section
overrides); a missing `voice` means the registry's `default_profile`
(`artifact-signal`). Apply the profile as artifact contract, not generic
polish. A prose tool may audit against it; none is required.

## Project Root Resolution

When a mode enumerates instances in the operator's project, resolve the
project HELIX root in order: (1) an
explicit path given at invocation; (2) a runtime-supplied project config
value; (3) the convention `docs/helix/` under the working directory with
`00-discover` … `06-iterate` subdirectories. If none resolves, surface a
setup gap rather than improvising. Chat-only runtimes require option 1.

## Autonomy

HELIX expresses the policy; the runtime supplies the agency. Three levels
control how often a workflow pauses, never which activities run.

| Level | Behavior |
|---|---|
| `low` | Ask before each step and before creating each downstream artifact. Do not infer unconfirmed scope. Concern selection stays interactive. |
| `medium` (default) | Create deterministic non-conflict artifacts; pause when ambiguity or conflict blocks deterministic progress. Prompt for concern selection when none exists. |
| `high` | Create downstream artifacts without pausing unless a hard stop blocks progress; record assumptions rather than asking. Infer concern selection from the product's nature and record it as an assumption. |

Precedence (first match wins): per-invocation override (the operator names a
level in the prompt) → the `autonomy:` block in `.helix.yml` → default
`medium`. Hard-stop invariant (all levels): autonomy moves the pause
threshold, never the stop floor; stop and surface to a human when two
higher-or-equal-authority artifacts truly contradict, when the next action is
destructive or irreversible and unauthorized, or when only a human can decide.
Never-collapse-the-loop invariant: every level runs the same activities;
higher levels pause less.

Stop triggers (`stop_at`) are a hard floor at every level. The authoritative
list is `workflows/stop-triggers.yml` (floor `references/stop-triggers.yml`),
six base triggers: `marker_edit`, `cross_methodology_edge_creation`,
`branch_or_merge`, `secret_read`, `large_diff`, `apply`. Load it when the skill
engages and consult it before every state-changing action; a repo may add
triggers under `autonomy.stop_at_extensions:` in `.helix.yml`, and base
triggers cannot be removed. When a trigger matches, name the trigger and the proposed action,
ask whether to proceed, and wait ("About to run `terraform apply` in
infra/prod — should I proceed?"); a generic `ok?` does not satisfy the
contract. When routing silently via `defaults.flow`, name the routing decision
in the first text block: silent routing is allowed, unspoken routing is not.

## Operating Discipline

- Prefer the product unit (or methodology content that changes behavior) over
  process redesign. Do not skip real defect checks under cover of shipping
  faster.
- Consult `workflows/references/work-item-first.md` when a user or runtime
  requires tracker-backed execution; ordinary authoring and alignment do not
  create tracker items by default.
- Do not silently start implementation when the request is planning,
  alignment, review, or routing; when the route is unclear, use `check`.
- Preserve the authority hierarchy: vision, PRD, features/stories,
  architecture and ADRs, designs, tests, implementation plans, code.
- Short affirmations ("do it", "yes") inherit the prior turn's offered scope;
  clarify only when it remains ambiguous.
- Scope complaints and pasted-evidence reactions ("this isn't going to
  scale") route to `align` or `evolve`, never to direct edits of the pasted
  code.
- Operator pushback on a blocker calls for reviewing the relevant artifact and
  evidence before retrying or changing direction.
- `check` returns status; design changes are a follow-up turn the operator
  chooses.
