---
name: helix
description: Route HELIX methodology work to the right planning, alignment, design, review, execution, or release workflow. Use when the user asks to use HELIX, work with HELIX artifacts, align documents, frame requirements, design a change, evolve specs, review work, decide what is next, or manage HELIX-governed work without naming a specific helix-* skill.
argument-hint: "[intent or scope]"
---

# HELIX Router

Use this as the HELIX entrypoint. Users should not need to memorize individual
workflow skill names. Route the request to the smallest HELIX workflow that
fits, then follow the matching workflow contract below.

Rule: do not add separate public `helix-*` skills. Add or refine a route inside
this skill instead.

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
4. Keep each artifact in its lane: vision is direction, PRD is product scope,
   feature specs are feature behavior, stories are vertical user outcomes.
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

Use when the safe next action is ambiguous.

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
