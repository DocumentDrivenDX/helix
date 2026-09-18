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

Use this as the HELIX entrypoint. Users should not need to memorize individual
workflow skill names. Resolve the active scope, choose the domain lane, route
to the smallest workflow mode that fits, then load and follow that mode's
contract from the catalog (§Mode Contracts).
Rule: do not add separate public `helix-*` skills. Add or refine a route
inside this skill instead.

## When to engage (read first; non-negotiable)

Engage whenever a condition below holds, whether or not the artifact content
is attached, the workspace is empty, or the request looks generic. Engagement
is the first tool action of the turn: hosts with a skill tool invoke the
`helix` skill through it; hosts without one load this `SKILL.md` body via the
host mechanism (a slash command, skill auto-load, or a read of this file).
Narrating HELIX-shaped reasoning without that action is a contract violation.

Engage when the prompt:

- names a HELIX artifact (PRD, ADR, FEAT, feature spec, technical design,
  implementation plan, test plan, runbook, release notes, user stories,
  roadmap, iteration plan, status report, requirements), even to *review* or
  *expand* one whose content is not attached; the path resolves from the
  marker, graph, and cwd.
- uses a lane trigger from the §Routing Axes table → that lane and its
  matching mode; infra and web triggers consult `stop_at` first.
- asks "what's next", "plan the change", "decide what to do", or any
  cross-flow query that needs the marker to answer → `check`.
- asks to "grill me", "interview me" about a plan/design, or to stress-test
  decisions one question at a time → `grill`.
- asks for a deck, slides, pitch, board or exec update, one-pager, brief,
  memo, or a client-ready or customer-facing document built from project
  artifacts → `present`.

## Routing Axes

Route by four axes: (1) **scope instance**, the `flows:` entry in
`.helix.yml` that owns the target; (2) **domain lane**, product, web, infra,
data, or another documented lane implied by scope and concerns, internal
context and never a public skill name; (3) **workflow mode** (§Routing
Rules); (4) **autonomy and stop rules**, proceed or pause before a
state-changing action (§Autonomy).

| Domain lane | Triggers | Required observable behavior |
|---|---|---|
| `product` | HELIX artifact named; planning verb (frame, align, decompose, prioritize, propose, capture, review, decide, evolve, refresh) against a product/feature/requirements object; cross-flow query | (a) Read `.helix.yml` AND the bound graph before any file write or edit; (b) Read named upstream artifacts (vision, PRD, feature spec) per the graph BEFORE drafting; (c) cite `ddx.links` / `informs` edges in any new artifact |
| `infra` | IaC verb (terraform/tofu/kubectl, provision/destroy/rotate); set up CI; manage credentials | (a) Consult the stop triggers (`workflows/stop-triggers.yml`) for `apply` or `secret_read` before any shell command; (b) Read infra-shaped artifacts (architecture, runbook, deployment-checklist); (c) explicit confirmation prompt before terraform/tofu/kubectl/credential operations |
| `data` | Data-pipeline verb (backfill/ingest/migrate a table or schema, profile a source, write a data contract) | (a) Read data-contract / data-quality-expectations / data-architecture artifacts; (b) cite producer/consumer or PII/governance posture in prose; (c) defer schema mutations behind a `stop_at` confirmation |
| `web` | Web/frontend verb (deploy/ship to production, add monitoring for a user-facing flow, optimize page performance) | (a) Read architecture / design-system / monitoring-setup / runbook artifacts in the deploy-flow scope; (b) cite Web Vitals / RUM / page-error vocabulary in prose; (c) defer production deploys behind a `stop_at` confirmation |

Skipping lane-required behavior is a routing failure even when the mode is
correct.

## Activation Discipline (in order, every time the skill engages)

### 1. Locate the marker

Walk up from cwd to the repository root (the directory containing `.git/`);
the first `.helix.yml` found governs work started in any subdirectory. Do
not stop after searching cwd only.

### 2. Read the marker and bind the graph before any file write or edit

This skill speaks in three primitives, read markdown, write markdown, and search files (host tool names: on hosts with named tools a file write or edit is Write or Edit, a shell command is Bash, a file read is Read).

Before the first file write or edit of the session, read the marker and bind
the methodology graph via §Catalog Resolution, in either order; skipping
either produces artifacts narrated from training and is a contract violation.
A graph bind is always achievable in supported layouts, so a missing
project-local `workflows/` never justifies stopping or skipping edits: bind
from a later resolution step. A read whose target does not resolve does not
count. `high` autonomy waives the human-in-the-loop ask, not this grounding.
Under heuristic activation (§3) the failed marker lookup satisfies the
marker read and the shipped catalog satisfies the graph bind.

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

- **Marker absent, no heuristic**: report no active flow; machine-readable
  form `{"active": []}`.

### 4. Enforce scope

Every write or edit targets a path inside the active flow's `root:`. For a
write outside scope: refuse, surface the marker entry that scoped the flow
and the offending path, and ask whether to (a) broaden the marker, (b)
redirect under scope, or (c) cancel. With several flows, the flow whose root
contains cwd wins; otherwise follow the §3 chain. Never invent a selector
outside the marker.

### 5. Author and edit artifacts

Bind the type's `template.md`, `prompt.md`, `meta.yml`, and active voice
profile from the resolved catalog and load `modes/_authoring.md` (graph
prerequisites, links, edge rules) first; never author from the catalog
listing alone. Principles resolve project-first: the project's
`01-frame/principles.md` when it exists, else `workflows/principles.md`
(floor `references/principles.md`); no merging. Prefer in-place edits and
create only when the file is missing: a successful read of the resolved path
means the instance is live and every modification, however small, is an
in-place edit that preserves frontmatter and operator-added content. Instance
edges (PRD → FEAT, ADR → technical design) live in the instance's
`ddx.links:` frontmatter, never in the body or this skill; cross-flow edges
are declared in the graph's `external_edges:` first, then in the instance
with `cross_flow: true` (legacy alias `cross_methodology: true`).

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
Runtime aliases choose among marker-authorized flows; they cannot broaden
the marker.

### 7. Frontmatter round-trip

Never rewrite unknown frontmatter keys. When editing a body, preserve
`ddx.id`, `ddx.review`, `ddx.links`, vendor-namespaced (`x-*`) and legacy
(`relationships:`, `depends_on:`) keys byte-equivalent and in order. Legacy →
new key translation is explicit migration work, never a side effect.

### 8. Externally authored artifacts (the checkout cycle)

`ddx.authoring.home` says where an instance is authored. `repo` means the
Markdown file **is** the document. `external-tool` means the document lives in
a collaboration tool and the file carries its identity plus, after a check-in,
a copy of its content. Field definitions are normative in
`workflows/artifact-schema.md` (Authoring home); the working practice is in
`workflows/conventions.md`.

**Default to `repo`.** Choose `external-tool` only on a demonstrated need for
heavy human manipulation of format or content — a canvas iterated live in a
workshop, a deck whose layout is part of the deliverable. Collaboration is not
the test: a document several people contribute to that could have been written
in Markdown is `repo`. `home` is fixed at creation. Changing it is a deliberate
migration, never a side effect of an edit, and a document that later copies its
content into the repository does not thereby become repo-authored.

**Never edit an `external-tool` body to change its content.**
`authoring.origin` is the write surface for the life of the document. Editing
the Markdown forks the artifact from its authoring home, and the fork is
silent — the next check-in overwrites it. Route the change to the tool and
report that you did; this extends the §5 prefer-in-place-edit rule one step
further, because here even an in-place edit is the wrong surface.

**Treat `state: checked-out` content as undependable.** Before the first
check-in the body carries identity and description only; after a later checkout
it is the previous copy, which the tool has moved past. Do not quote a
checked-out artifact as current, do not set `ddx.status: approved` on one, and
do not approve anything that depends on one. Surface the checkout instead:
name the artifact, its `origin`, and what it blocks.

**Read `state: checked-in` bodies as the read surface.** A checked-in body is
what consumers resolve against; `authoring.export` is the committed original it
came from and `authoring.export_sha256`, when present, is that file's digest at
check-in. If the digest no longer matches the export, the body is stale: say
so and route to a fresh check-in rather than reasoning from it. A missing
digest means unknown, not mismatched.

**`state` is terminal in neither direction.** A checked-in document returns to
`checked-out` for its next revision, reusing the same `origin`, `export`, and
`export_sha256`; checking out again never deletes content the repository
already holds. A check-in is one change carrying the body, the export file, the
digest, and the `state` flip together — splitting them leaves the frontmatter
and the body disagreeing. Checking in does not approve the document; it makes
approval possible.

Producing a check-in body from an external document is a runtime capability.
If the runtime offers none, say so and leave `state` alone. Hand-transcribing
content and flipping `state: checked-in` claims a fidelity the repository
cannot back.

## Concern slot resolution

A **slot** is an exclusive functional position a project must fill exactly
once (one frontend framework, one language runtime, one e2e tool, one auth
backend). Slots are declared in the shipped catalog at `concerns/slots.yml`, resolved
via §Catalog Resolution — the in-tree `workflows/concerns/slots.yml` when a
vendored tree is present, otherwise the `references/concerns/slots.yml` floor
beside this SKILL.md (which always resolves). The file declares exclusive slots
plus shipped defaults; membership in a slot is **derived** from each concern's
own `## Slot` section, never listed in `slots.yml`.

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
| Turn governed artifacts into a deck, one-pager, or brief for clients, sponsors, or executives | present |
| Hand governed work to the runtime for execution, source control, or packaging | runtime-handoff |

When several routes fit, take the highest-authority planning route: `frame`
before `design`; `align` before `evolve` when the task is diagnostic;
`evolve` before a runtime handoff when the requested implementation lacks
governing coverage. `grill` beats `input`/`frame`/`design` when the operator
asks to be interviewed or to stress-test decisions before authoring; a bare
"plan" is not grill. A roadmap, iteration plan, or status report routes to
`iterate` even when a change triggers it, and reviewing an iteration against
its plan is `iterate`; `review` stays fresh-eyes critique of work products,
PRs, and plans.

## Mode Contracts

Each mode's contract is one file, `modes/<mode>.md`, in the bound catalog
(`workflows/modes/` in source checkouts and vendored trees,
`references/modes/` in generated packages, resolved by §Catalog Resolution):
one per routed mode plus the shared `workflows/modes/_authoring.md` and
`workflows/modes/_report.md`. After routing, load the routed mode's file and
follow it as the active interface; modes that create or edit instances also
load `modes/_authoring.md`; align, validate, refresh, check, project-audit,
review, and converge end with the `modes/_report.md` block. Mode files point
at their deeper procedure under `actions/` when one exists; consult it only
when the contract needs more step detail. The `present` mode also reads six
files under `workflows/deliverables/` (floor `references/deliverables/`):
`theme.yml`, `slide-patterns.yml`, `deliverable-mappings.yml`,
`deck-flows.yml`, `deck-craft.md`, and `visual-specs.md`.

## Catalog Resolution

When a mode needs a mode contract, template, prompt, quality criteria, voice
registry, concerns, slots, principles, stop triggers, or the graph, resolve
in this fall-through order; the first source that resolves wins, and
project-local or source-checkout ranks never demote below an installed
plugin.

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
   then `<plugin-root>/skills/helix/references/...`; the install guide names
   the variable per host.
5. **Generated `references/` floor** beside this `SKILL.md`, shipped in
   plugin packages and skill bundles so a catalog always resolves:
   `graph.yml`, `voice.yml`, `stop-triggers.yml`, `principles.md`, and the
   `modes/`, `activities/`, `concerns/`, `actions/`, `templates/`,
   `deliverables/`, and `references/` trees.
6. **Fail closed**: if nothing binds, stop with a diagnostic listing every
   path attempted. Never invent templates or contracts from training data.

Same-source rule: once a source binds, load everything (graph, modes,
templates, prompts, meta, voice, concerns, principles, references, stop
triggers) from it, and state which source bound when it is not the floor
("catalog: in-tree `workflows/graph.yml`"). Adopters need only `.helix.yml`
and instance documents; they never copy templates. Artifact types: one
directory per type under `<activity>/artifacts/`, enumerated in `graph.yml`;
each holds `template.md`, `prompt.md`, `meta.yml`, and `example.md`. Concern
slots and their shipped defaults live in `workflows/concerns/slots.yml`
(floor `references/concerns/slots.yml`); defaults are starting points a
project overrides, not choices HELIX imposes.

## Voice Resolution

Load the voice registry (`workflows/voice.yml`, floor `references/voice.yml`)
from the same bind as the graph. The active profile comes from the type's
`meta.yml` (`voice: <profile>` or `voice.profile: <profile>` with section
overrides); a missing `voice` means the registry's `default_profile`
(`artifact-signal`). Profiles (conciseness, audience, required moves, avoid
list) are defined in `voice.yml`; apply one as artifact contract, not generic
polish. A prose tool may audit against it when available; never required.

## Project Root Resolution

When a mode enumerates instances in the operator's project (refresh and
similar batch operations), resolve the project HELIX root in order: (1) an
explicit path given at invocation; (2) a runtime-supplied project config
value; (3) the convention `docs/helix/` under the working directory with
`00-discover` … `06-iterate` subdirectories. If none resolves, surface a
setup gap rather than improvising. Chat-only runtimes require option 1.

## Autonomy

HELIX expresses the policy; the runtime supplies the agency. Three positions
control how often a workflow pauses for confirmation, never which activities
run.

| Level | Behavior |
|---|---|
| `low` | Ask before each step and before creating each downstream artifact. Do not infer unconfirmed scope. Concern selection stays interactive. |
| `medium` (default) | Create deterministic non-conflict artifacts; pause when ambiguity or conflict blocks deterministic progress. Prompt for concern selection when none exists. |
| `high` | Create downstream artifacts without pausing unless a hard stop blocks progress; record assumptions rather than asking. Infer concern selection from the product's nature and record it as an assumption. |

Precedence (first match wins): per-invocation override (the operator names a
level in the prompt) → the `autonomy:` block in `.helix.yml` → default
`medium`. The signal lives only in runtime-neutral artifacts. Hard-stop
invariant (all levels): autonomy moves the pause threshold, never the stop
floor; stop and surface to a human when two higher-or-equal-authority
artifacts truly contradict, when the next action is destructive or
irreversible and unauthorized, or when only a human can decide.
Never-collapse-the-loop invariant: a high-autonomy run executes the same
activities a low-autonomy run would, pausing less often.

Stop triggers (`stop_at`) are a hard floor at every level. The authoritative
list is `workflows/stop-triggers.yml` (floor `references/stop-triggers.yml`,
resolved via §Catalog Resolution), six base triggers: `marker_edit`,
`cross_methodology_edge_creation`, `branch_or_merge`, `secret_read`,
`large_diff`, `apply`. Load it when the skill engages and consult it before
every state-changing action; a repo may add triggers under
`autonomy.stop_at_extensions:` in `.helix.yml`, and base triggers cannot be
removed. When a trigger matches, name the trigger and the proposed action,
ask whether to proceed, and wait ("About to run `terraform apply` in
infra/prod — should I proceed?"); a generic `ok?` does not satisfy the
contract. At every level, name the routing decision in the first text block
when routing silently via `defaults.flow`: silent routing is allowed,
unspoken routing is not.

## Operating Discipline

- Prefer the product unit (or methodology content that changes behavior) over
  process redesign. Bound process machinery, freeze it, deliver.
- Do not skip real defect checks (tests, product ACs, claims-vs-reality,
  scope discipline) under cover of shipping faster.
- With a work tracker, obey `workflows/references/work-item-first.md` before
  writing files or mutating the tracker.
- Do not silently start implementation when the request is planning,
  alignment, review, or routing; when the route is unclear, use `check`.
- Preserve the authority hierarchy: vision, PRD, features/stories,
  architecture and ADRs, designs, tests, implementation plans, code.
- Short affirmations ("do it", "yes") inherit the prior turn's offered scope:
  several branches offered → ask which; one recommended → restate it exactly
  before acting.
- Scope complaints and pasted-evidence reactions ("this isn't going to
  scale") route to `align` or `evolve`, never to direct edits of the pasted
  code.
- Operator pushback on a reported blocker triggers an alignment surface, not
  a retry: name the artifact-line evidence and route through the
  `modes/_report.md` handoff fields.
- `check` returns status; design changes are a follow-up turn the operator
  chooses.
