---
ddx:
  id: helix.workflow.concern-resolution
  depends_on:
    - helix.workflow.principles-resolution
    - FEAT-006
  review:
    self_hash: 108ccd9f48540a5fdb52001a620d1521e562abf9cd4ea33903748becd999bca1
    deps:
      FEAT-006: d2eab5444f4c023232a08e0774b6738c3d9abf6a4da48b7d59e775750ed1412a
      helix.workflow.principles-resolution: fe8bbb3f17f8f153acd66e91c48bfb775972ef271361a1c660d1c83c69f15648
    reviewed_at: "2026-05-26T17:45:37Z"
---
# Concern and Practices Resolution

This reference defines the shared pattern that HELIX action prompts follow
to load the active project concerns and their associated practices.

## Resolution Logic

### Concerns

1. Check: does `docs/helix/01-frame/concerns.md` exist and have content?
   - Yes -> load it as the active concerns document.
   - No -> no active concerns. Omit concerns and practices from context.

There are no default concerns. Unlike principles, concerns are always
project-specific. A project without a concerns file simply has no declared
cross-cutting context beyond principles.

### Area Filtering

Each concern declares an `areas` field in its `concern.md`. The canonical
area taxonomy is:

| Area value | Matches work item labels | Typical concerns |
|------------|-------------------|------------------|
| `all` | Every work item | Tech stacks, security |
| `ui` | `area:ui`, `area:frontend` | a11y, i18n, design system |
| `api` | `area:api`, `area:backend` | o11y, rate limiting |
| `data` | `area:data` | Data modeling, migration |
| `infra` | `area:infra` | Deployment, monitoring |
| `cli` | `area:cli` | CLI conventions |

Concerns use comma-separated lists for multiple areas (e.g., `ui, api`).

The area taxonomy is **extensible per-project**. Projects declare their area
labels in `docs/helix/01-frame/concerns.md` under `## Area Labels`. The
defaults above cover most projects; add custom areas when needed.

Common HELIX-repo extensions include `docs`, `site`, `demo`, `testing`, and
`artifacts`. A work item may carry more than one `area:*` label when its scope spans
more than one surface.

**Matching rules**:
- `areas: all` matches every work item regardless of labels.
- `areas: ui` matches work items with `area:ui` or `area:frontend`.
- `areas: api` matches work items with `area:api` or `area:backend`.
- A work item with multiple area labels matches any concern that declares any of
  those areas.
- A work item with **no** `area:*` labels matches only concerns with `areas: all`.
- Area labels drive matching only. They are not concern names and must not be
  copied into the `<concerns>` field of a context digest.

**Triage/evolve/polish must assign area labels** before assembling the
context digest. If a work item's area is ambiguous, prefer the more inclusive
label or assign multiple labels.

### Practices

1. Parse the active concerns document for selected concerns (listed under
   `## Active Concerns`).
2. Filter to concerns matching the current work item's area scope.
3. For each matched concern, load
   `workflows/concerns/<concern-name>/practices.md` from the library.
4. Apply project overrides (listed under `## Project Overrides` in the
   concerns document) on top of library practices.

Project overrides take full precedence.

## Injection Preamble

After resolving active concerns and merged practices, include them in
your working context:

```markdown
## Active Concerns

{area-matched concern names and key constraints}

## Active Practices

{merged practices from matched concerns with project overrides applied}

Use the declared concerns and practices when making choices.
When a concern specifies a tool, convention, or quality requirement,
follow it rather than choosing an alternative.
```

## When to Apply

Action prompts that involve technology or quality choices must resolve and
inject concerns at their Activity 0 or Bootstrap step, alongside principles.

| Action | Injection Point |
|--------|----------------|
| `implementation.md` | Activity 0 (Bootstrap) — alongside principles and quality gates; Activity 7 runs concern-declared quality gates |
| `fresh-eyes-review.md` | Activity 0 — verify implementation follows concern conventions; Pass 3 checks concern-specific practices |
| `plan.md` | Before first refinement round — concerns constrain architecture |
| `evolve.md` | Activity 0 — concerns affect scope; Activity 3 detects concern conflicts from new requirements |
| `reconcile-alignment.md` | Activity 0 — concern drift across all layers (code, docs, ADRs); Activity 3 detects per-concern tooling drift |
| `polish.md` | Bootstrap — verify work items reference correct concern context; area label enforcement for concern matching; acceptance criteria tool consistency |
| `frame.md` | Bootstrap — concern selection happens during framing |
| `experiment.md` | Bootstrap — experiments must use declared concerns |
| `check.md` | Activity 0 — load concerns for queue health; Activity 2 checks area label coverage, digest freshness, missing concerns.md |
| `backfill-helix-docs.md` | Activity 0 — discover active concerns or propose them from evidence; Activity 4 may create concerns.md |

## Concern Selection in /helix frame

Concern **selection** happens once, during Frame, and is a **required** Frame
step (FEAT-006 FR-14): a frame pass is not complete until concerns are selected
or it is explicitly recorded that none apply. `check` and `polish` are
**propagation gates**, not selection — they verify and fix that an
already-selected concern reached every area-matched work item; they do not perform or
re-perform selection.

When `/helix frame` runs and no `docs/helix/01-frame/concerns.md` exists, resolve
selection by the active autonomy level (FEAT-011; see `workflows/actions/input.md`):

**`low` / `medium` — interactive selection:**

1. List available concerns from `workflows/concerns/` grouped by category.
2. Ask the user about each category:
   - Tech stack: "What language, runtime, and package manager?"
   - Data: "What database or data layer?"
   - Infrastructure: "Where will this deploy?"
   - Quality: "Do you need a11y, i18n, o11y?"
3. Match answers to available concerns.
4. If custom needs exist, document them as project overrides.
5. Write `docs/helix/01-frame/concerns.md`.

**`high` — inferred selection:**

1. Classify the product nature from the vision / PRD / intent (web app, API
   service, CLI, data pipeline, library).
2. Map the nature to candidate library concerns — e.g. web app → a tech-stack
   concern + a frontend concern + `a11y-wcag-aa`; API service → tech-stack +
   `o11y-otel` + `security-owasp`.
2a. **Auto-select `verification` for any buildable product.** `verification` is
   the always-on **evidence gate** ("not done until observed evidence of the
   running system exists"); it is composable (no slot) and composes on top of
   `testing` and the `e2e-framework` slot — it does not replace either. Add it
   to the inferred selection for every buildable product, recorded as an
   assumption. **Exceptions are narrow**: only library / docs-only / non-buildable
   work (no running stack to exercise) may omit `verification`. A buildable
   product where full-stack e2e is genuinely infeasible **still selects
   `verification`** — it only *relaxes the full-stack-e2e form of evidence*,
   recording the specific reason and substituting the strongest observable
   evidence available. See `workflows/concerns/verification/concern.md`.
2b. **Auto-select `sample-data` for any data-backed product.** A data-backed
   product — one whose value shows through data it stores and renders — must
   seed a **governed, varied demo/sample dataset** via a semantic faker (the
   tech stack's named default: `@faker-js/faker` for `typescript-bun`, `Faker`
   for `python-uv`, etc.), covering schema-relevant edge cases (empty, long,
   large, boundary, all status/enum variants), so the running app exercises its
   empty/overflow/large-number/all-status UI states instead of shipping a couple
   of thin hardcoded rows. It is composable (no slot); `areas: data` scopes its
   practices to data-layer work items, so the resolver still selects it for
   data-backed products **without over-broadening to `all`**. Add it to the
   inferred selection for every data-backed product, recorded as an assumption.
   See `workflows/concerns/sample-data/concern.md`.
2c. **Auto-select `admin-console` for any operator-facing product.** When a human
   operator / back-office / admin user must **manage mutable domain objects or
   lifecycle state through a UI**, select `admin-console`: the operator's
   jobs-to-be-done — CRUD over the core domain objects **plus** the domain's
   lifecycle/control actions (schedule, pause, cancel, resume, retry, archive,
   revoke, approve, …) — must be built as **usable UI**, and the **primary
   operator workflow must be exercised end-to-end through the UI** (not API-only;
   the form is the `verification` concern's call). It is composable (`areas: ui,
   api`). Do **not** select it for pure API services, CLIs, libraries, public/
   marketing content sites, or read-only dashboards unless an operator UI is
   explicitly required. Record as an assumption. See
   `workflows/concerns/admin-console/concern.md`.
2d. **Auto-select `auth` for any account-based / multi-tenant product.** When the
   product has **accounts, users, tenants, orgs, sign-in/session semantics,
   roles, or principal-scoped data or actions**, select `auth`: a real signup
   (provisioning the account/tenant + owner), login/logout/sessions, server-side
   RBAC + (for multi-tenant) a platform-admin, and isolation enforced **through
   the authenticated principal** — with the backend behind the `auth-provider`
   slot. It is composable (`areas: api, data, ui`); also **fill the
   `auth-provider` slot** (default `auth-local-sessions`; an external IdP like
   Auth0/OIDC is a swappable filler, never hardcoded). Do **not** select it for
   anonymous public sites, libraries, single-user local CLIs, or machine-only
   internal APIs unless user/tenant principals are explicit. Record as an
   assumption. See `workflows/concerns/auth/concern.md`.
2e. **Auto-select `domain-driven-design` for any domain-rich business product.** When the
   product has non-trivial business entities with invariants, lifecycle, and relationships
   (invoicing, CRM, ordering, billing, scheduling, ledgers — essentially any real business
   app), select `domain-driven-design`: a ubiquitous language, explicit bounded contexts, and
   behavior-rich aggregates whose roots enforce invariants in the domain layer. Composable
   (no slot; `areas: data, api`); compose with the chosen `architecture-style` (DDD = *what* to
   model, architecture-style = *how* to layer it). Do **not** select it for pure
   presentation/marketing sites, thin CRUD-only tools with no business rules, or libraries with
   no domain. Record as an assumption. See `workflows/concerns/domain-driven-design/concern.md`.
2f. **Scan the full concern library by `## When to use`, high-precision.** Beyond the always-on
   bullets above, enumerate every concern under `workflows/concerns/` and select one **only when
   its `## When to use` MUST-have signal matches the product AND its stated negative/exclusion
   criteria do not fire** — recording, per selected concern, the one-line evidence for why it
   matched. No global match-all; an unjustified selection is over-selection drift. High-signal
   triggers: `multi-tenancy` (tenants share the system), `authorization-model` (roles/permissions
   beyond login), `event-sourcing` (audit/history/timeline is value-bearing), `cqrs` (divergent
   read/write in a bounded context), `enterprise-integration-patterns` (async messaging / queues /
   webhooks), `resilience` (synchronous external deps in the request path), `api-style` (any
   networked interface — default REST or same-repo RPC), `caching-strategy` (read-heavy hot path,
   tolerable staleness), `relational-data-modeling` (persists relational data),
   `frontend-architecture` (non-trivial interactive UI), `twelve-factor` (a deployed service),
   `concurrency-model` (real concurrency / background processing), `usage-metering` (usage-based
   billing), `mcp-server` (exposes tools/data to LLM agents), the `databricks-*` family (targets
   the Databricks lakehouse), and the pattern catalogs `design-patterns-gof` /
   `enterprise-application-patterns` (recurring OO / enterprise persistence decisions). Also **fill
   the exclusive `architecture-style` slot on signal** (it has no default): `onion-architecture`
   or `clean-architecture` for a domain-centric system, `hexagonal-architecture` for many
   symmetric adapters, `classic-layered` for thin/low-ceremony — leave it unfilled (recorded
   assumption) only for trivial CRUD.
2g. **Record each selected concern's `## Artifact Impact` into `concerns.md`** (and its context
   digest). Each concern's `concern.md` declares, under `## Artifact Impact`, which artifacts its
   selection must change (ADR / FEAT / TD / DATA_DESIGN / IMPLEMENTATION_PLAN / DESIGN_SYSTEM / …).
   Carrying that forward is what makes the downstream framing/design/build prompts realize it and
   lets reconcile-alignment's **Concern→Artifact Realization** check verify it — a selected concern
   that leaves no trace in its declared artifacts is drift.
3. **Fill each needed exclusive slot** (FEAT-006 slots; FEAT-011 FR-3). A slot is
   an exclusive functional position a concern fills — one frontend framework, one
   language runtime, etc. Determine which slots the product needs (**a web app
   must fill `frontend-framework`** — leaving it empty and raw-serving HTML is the
   bug this guards against; a runnable product fills `language-runtime`; **a web
   app with a UI must also fill `e2e-framework`** — default `e2e-playwright`),
   then for each needed slot resolve a filler in this order, first match wins:
   1. **Operator override** — the slot's value in
      `docs/helix/01-frame/concerns.local.yml`, if that file exists. Read it
      **before** writing `concerns.md`.
   2. **Shipped default** — the slot's value in `defaults:` of
      `workflows/concerns/slots.yml`.
   3. **Assumption** — if neither supplies a filler, record an assumption to
      revisit; never make a silent pick.
   Record the chosen filler **and its source** (`concerns.local.yml override`,
   `slots.yml default`, or `assumption`) in `concerns.md`. Slot membership is
   derived: a concern fills slot X iff its `concern.md` `## Slot` names X.
   **Filling `e2e-framework` selects the tool; it is not e2e coverage.** A UI web
   app must additionally have **≥1 core user-flow covered by a whole-stack e2e that
   actually RUNS GREEN against the running app** — a **browser e2e** for a
   client-rendered UI, or an **HTTP+HTML-assertion e2e** (drive the live server,
   assert the rendered markup) for a server-rendered one; both are first-class. A
   config plus a `.spec` file that never runs does not satisfy this. The
   run-core-flow gate lives in the selected `e2e-framework` filler's practices
   (e.g. `e2e-playwright` for the browser case) and the `verification` evidence
   gate; an unexercised flow's AC is `UNTESTED`, not covered.
3a. **Unmatched capability — decide by RISK, don't ignore or fabricate.** When the
   brief needs a capability with no matching concern (e.g. an email-delivery
   provider, an event-streaming bus, send-time optimization, usage-based billing,
   a marketplace deploy), route it:
   - **Clear, low-risk, well-understood** (a known provider, a standard
     integration) → add a concern (provider-behind-abstraction — name the
     capability/slot, let the provider fill it) or capture the choice in an ADR.
   - **Material uncertainty** — unknown/changing API, cost, permissions/credentials,
     correctness, or operational risk (this holds **even for a known vendor**:
     billing, marketplaces, send-time optimization, queue design) → define a
     **`tech-spike`** (02-design) and de-risk it before committing the design.
     Prefer a **bounded, runnable** spike when feasible (small, time/scope-boxed);
     when running is infeasible or unsafe (external/paid APIs, missing creds, long
     benchmarks) record a **blocked spike** — why it could not run, what was read
     or simulated instead, and which decisions stay **provisional**.
   - **Anti-reframe: "known" means EVIDENCED, not familiar.** A capability is
     "clear/low-risk" only when its design-defining facts are **evidenced** — by an
     operator statement, a governing artifact, an existing implementation, a
     docs/API proof, or a completed spike — **not** because the model is familiar
     with the domain, and **not** because you picked a mechanism or named a
     provider. Before routing such a capability to a concern or ADR, name its
     **top 1-3 design-defining decisions** (anything that could change API shape,
     data model, pricing/cost semantics, security/permissions, operational
     guarantees, or work decomposition). If any is **assumed** rather than
     evidenced, that is material uncertainty → `tech-spike`, **even when you have
     chosen a provider and deferred its live integration** (deferring the live
     provider de-risks integration timing, not the design-defining decision).
     Deferring the external call does **not** defer the **app-side data the
     current runnable slice's integration contract requires** — the events/records
     the app must emit (e.g. usage-metering events for billing) are build-work for
     the slice; build and verify them now. (Sequencing the outbound call to a later
     slice is legitimate only once spike evidence, a blocked-spike rationale, or
     guidance-needed is recorded — never a way to skip exercising a known vendor.) An
     **operator-marked "spike/unknown" is authoritative** evidence of uncertainty —
     do not demote it to a concern. The only alternative to a spike is a **recorded
     assumption + residual-risk note**, acceptable *only* when the assumption is
     reversible/non-blocking, explicitly provisional, or the spike is blocked —
     never as an equal substitute when the design commits to the assumption. For a
     **business/product** unknown a technical spike cannot answer (e.g. a pricing
     model), record **guidance-needed** or a blocked spike instead of forcing a
     technical spike.
   Do not fabricate a concern for something not yet understood; do not silently
   drop a brief capability. (Same rule applies in `evolve`; see
   `workflows/actions/evolve.md`.)
4. Write `docs/helix/01-frame/concerns.md` with the inferred selection (composable
   concerns + the resolved slot fillers), recording each inferred concern as an
   **assumption** (a recorded inference, not a confirmed choice) rather than
   pausing to ask.
5. Run the Conflict Detection below over the inferred set; record unresolved
   conflicts as assumptions to revisit, never as a silent pick.
6. Never overwrite an existing `concerns.md` by inference — inference only fills
   an absent selection.

## Conflict Detection

When a project selects multiple concerns, check for conflicting practices:

1. For each practice category (linter, formatter, testing, etc.), check
   whether multiple concerns declare different values.
2. If a conflict exists and no project override resolves it, flag it to
   the user with a concrete example.
3. Conflicts must be resolved via project overrides before the concerns
   file is considered complete.

### Composed-concern runtime friction

Some concern pairs declare individually-correct practices that nonetheless
collide at **runtime/build time** rather than at the practice-value level. These
do not show up as a "linter A vs linter B" conflict, so check for them
explicitly when composing concerns:

- **`typescript-bun` + `react-nextjs`**: `bun:*` built-ins (notably
  `bun:sqlite`) resolve only under the Bun runtime, but `next build`/`next
  start` execute under Node. The fix is to run Next.js under `bun --bun`, or to
  keep `bun:*` built-ins out of the Next.js runtime path (isolate the data layer
  in a separate Bun service). Record the chosen resolution as a project override.
  See the friction sections in both concerns' `practices.md`.

When a composed-concern friction is identified, resolve it the same way as a
practice conflict: record the resolution as a **project override** in
`docs/helix/01-frame/concerns.md` so the build-time choice is explicit rather
than rediscovered when the build breaks.

## Relationship to ADRs and Spikes

Concerns are the index; ADRs provide the rationale; spikes provide the
evidence:

```
Spike/POC (gather evidence)
  → ADR (record decision with rationale)
    → Concern (index for context assembly)
      → Context Digest (injected into work items)
```

- A spike or POC investigates a question.
- An ADR records the decision with rationale, citing the spike.
- The concern references the ADR in its `## ADR References` section.
- Project overrides that depart from library defaults must cite the
  governing ADR.

When a referenced ADR is superseded, `/helix polish` must flag the
affected concern for re-evaluation.

## Propagation Completeness

When a concern is introduced or changed, it must propagate through the full
work item lifecycle. This section defines how to verify propagation completeness.

Propagation is a **gate**, distinct from selection. Selection is a one-time
Frame decision (above). The checks here detect and fix work items that a selected
concern failed to reach; a `check` run that finds an area-matched work item missing
its concern is a **blocking propagation finding**, not a prompt to re-select.

### What Must Propagate

When `docs/helix/01-frame/concerns.md` changes (concern added, removed, or
practices updated), the following must be updated for all work items whose area
matches the changed concern's scope:

1. **Context digests**: The `<context-digest>` block must include the concern
   and its key practices.
2. **Acceptance criteria**: At least one acceptance criterion must reference a
   concern-appropriate tool or practice (e.g., `bun:test` for `typescript-bun`,
   `cargo clippy` for `rust-cargo`).
3. **Quality gates**: The work item's governing action must run the concern's
   declared quality gates during the measure activity.

### How to Check

Use these steps to verify propagation completeness for a scope:

1. Load active concerns per the resolution logic above.
2. For each concern, list all work items in scope with matching area labels.
3. For each work item:
   - Check `<context-digest>` includes the concern. If missing → stale digest.
   - Check acceptance criteria reference concern-appropriate tools. If missing
     or referencing wrong tools → concern gap.
   - Check that the work item's last `<measure-results>` (if any) includes the
     concern's quality gates. If missing → unmeasured.
4. Report counts: total work items, work items with full coverage, work items with gaps.

### When to Run

| Trigger | Action |
|---------|--------|
| `/helix check` Activity 2 | Concern Health — detect propagation gaps, recommend POLISH |
| `/helix polish` Activity 2-N | Concern Propagation Verification — fix gaps during refinement |
| `/helix measure` | Verify concern gates were run and recorded |
| `/helix report` batch mode | Aggregate concern coverage across scope |

### Concern Change Detection

To detect whether concerns have changed since work items were created or last
polished:

1. Check `git log --since=<last-polish-date> -- docs/helix/01-frame/concerns.md workflows/concerns/`
2. If changes exist, the concern library has been updated and existing work items
   may have stale digests and acceptance criteria.
3. `/helix check` should recommend `POLISH` when concern changes are detected.
