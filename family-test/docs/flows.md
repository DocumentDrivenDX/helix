# Flows — the HELIX family

HELIX is no longer a single methodology. It is a **family of cooperating
flows**: product, data-pipeline, infrastructure, and website (more later).
Each flow is its own plugin with its own skill, graph, and library types;
they cooperate via cross-flow edges, a shared marker (`.helix.yml`), and a
shared library of artifact types.

Design record: [`docs/helix/02-design/plan-2026-06-05-conversation-bench-and-autonomy.md`](../../docs/helix/02-design/plan-2026-06-05-conversation-bench-and-autonomy.md) §11–§14.

## Why "flow" and not "methodology"

`methodology` reads heavy and resists composition. `flow` reads naturally
for "product flow," "data-pipeline flow," "infra flow," and "website flow."
The marker key changed from `methodologies:` to `flows:`; the validator
accepts the legacy key for one deprecation cycle (M020 warn).

| Old term | New term |
|---|---|
| methodology | flow |
| methodology plugin | flow plugin |
| methodology graph (`workflows/graph.yml`) | flow graph |
| methodology activation | flow activation |
| HELIX (capitalised) | HELIX (unchanged — names the family) |

`ddx.methodology:` on instance frontmatter is renamed to `ddx.flow:` with
the same one-cycle alias.

## The four flows at v1

| Flow id | Plugin dir | What it owns |
|---|---|---|
| `helix` | `family-test/methodology-product/` | Product lifecycle: vision → PRD → FEAT → US → ADR → TD → tests → release |
| `helix-data` | `family-test/methodology-data/` | Data-pipeline lifecycle: profile → contract → design → validate → build → operate → evolve |
| `helix-infra` | `family-test/methodology-infra/` | Infrastructure lifecycle: change-intent → plan → apply → verify |
| `helix-web` | `family-test/methodology-web/` (P9 scaffold; future) | Website lifecycle: IA → design system → page-spec → build → deploy |

Each flow plugin ships:

- `skills/<flow-id>/SKILL.md` — the activation discipline + verb anchors
- `workflows/graph.yml` — the type-pair graph (nodes are library/local
  types; edges are `requires`/`contains`/`informs`)
- `workflows/activities/` — per-activity prompts (where applicable)
- `library/types/` — flow-specific types (helix-data owns 12 new types)

## How a flow is "active"

A flow is **active in a repo** iff it appears under `flows:` in
`.helix.yml`. The marker is committed; team-level. Multiple flows can be
active simultaneously (a monorepo can run helix + helix-data + helix-infra).
A flow may also be active in **multiple instances** (see Multi-instance).

```yaml
# .helix.yml — v2 schema (helix_version: 2)
helix_version: 2
flows:
  - id: helix
    root: docs/helix/
  - id: helix-data
    instance: customer-ingest
    root: pipelines/customer-ingest/docs/helix/
  - id: helix-data
    instance: orders
    root: pipelines/orders-fulfillment/docs/helix/
  - id: helix-infra
    root: infra/
```

`instance:` defaults to `default`. The unique key per entry is
`(id, instance)`. Duplicates are hard-fail (validator code M030).

## Routing — which flow engages

When the user prompts, the resolution chain picks a flow (and instance):

1. **Explicit slash command** — `/helix-frame`, `/helix-data-contract`, etc.
   Slash command names are plugin-prefixed for collision resistance.
2. **Per-prompt env override** — `HELIX_METHODOLOGY=helix-infra` (legacy env
   name; reads as `flow` post-rename).
3. **cwd under flow root** — the longest matching `root:` from the marker
   wins. Path-component-aware matching (NOT string-prefix); see §13.6b.
4. **Description-anchor routing** — Claude's skill router matches the
   prompt verbs against each flow's `description:` (plan §2.2). The verb
   list is the load-bearing surface.
5. **Disambiguation banner** — if multiple flows match equally, the skill
   surfaces the candidates and asks. NEVER silently picks alphabetically.

Verified by:

- 75 routing-eval rows (30 positive, 30 negative, 15 ambiguous) under
  `family-test/bench/routing-evals/`
- 6 multi-instance routing rows (`CI-01`..`CI-03`, `EA-*` cases — see
  bench.md §multi-instance)

## Multi-instance flows

A single flow can run in multiple subtrees of one repo. The discriminator
is the `instance:` field; the unique key is `(flow_id, instance)`. cwd
routing resolves to ONE `(flow, instance)` pair using the
path-component-aware algorithm (`resolve_cwd_to_instance()` in
`library/scripts/helix_check.py`):

1. Resolve each `root:` to an absolute path under repo root.
2. Filter to candidates where `is_path_prefix(root, cwd)` holds.
3. If 0 candidates → fall through to next resolution rule.
4. If 1 candidate → return it.
5. If >1 candidates: pick the deepest. Ties at equal depth:
   - if `HELIX_METHODOLOGY` env names one → that one wins;
   - else if `defaults.methodology` names one → that one wins;
   - else emit the disambiguation banner and ASK. Never auto-pick.

Sibling-tie silent alphabetical selection is explicitly forbidden — the
failure mode the marker was supposed to eliminate.

## Cross-flow edges

A flow may declare `external_edges:` in its graph to inform another flow.
The edge is **advisory** — instance documents reference the upstream via
`ddx.links.kind: informs` (or `informed_by` for inverse) with
`cross_methodology: true` (alias of `cross_flow: true`).

Example: helix-data's graph carries

```yaml
external_edges:
  - from_type: data-product-brief
    to_flow: helix-infra
    to_type: change-intent
    kind: informs
    cardinality: many-to-one
    required: false
```

This says "a `data-product-brief` MAY inform a downstream `helix-infra`
`change-intent`." Whether the link is populated is up to the skill +
autonomy; cross-flow edges are NEVER auto-populated from graph candidates
(Invariant 1 — Edge Authority Asymmetry).

Cross-flow edges helix-data participates in (plan §12.6):

- `helix:prd informs helix-data:data-product-brief`
- `helix-data:data-product-brief informs helix-infra:change-intent`
- `helix-data:metrics-dashboard informs helix:improvement-backlog`
- `helix-web:design-system informs helix-data:metrics-dashboard`

## Cross-instance edges

Two instances of the same flow can reference each other's documents via
`informed_by`. Read-only advisory direction:

```yaml
# in helix.api flow's graph.yml
external_edges:
  - from_type: feature-specification
    to_flow: helix
    to_instance: admin
    to_type: prd
    kind: informed_by
    cardinality: many-to-one
    required: false
```

```yaml
# api/.../FEAT-014.md frontmatter
ddx:
  id: FEAT-014
  type: feature-specification
  flow: helix
  instance: api
  links:
    - kind: informed_by
      to: "helix.admin:PRD-007"
      cross_instance: true
```

Verified by 3 bench rows under `CI-01`..`CI-03`.

## Shared library types

All flows draw their artifact types from a shared `library/types/` catalog.
ADR, principles, runbook, metrics-dashboard, improvement-backlog are
universal; flow-specific types extend (helix-data adds 12; helix-infra
adds change-intent, plan, apply-verify).

Each `library/types/<type>/meta.yml` declares the required sections; the
validator (T-class) gates instance documents against the type contract.

## Activities per flow

| Flow | Activities |
|---|---|
| helix (product) | 00-discover, 01-frame, 02-design, 03-test, 04-build, 05-deploy, 06-iterate |
| helix-data | 00-discover/profile, 01-contract, 02-design, 03-validate, 04-build, 05-operate, 06-evolve/backfill |
| helix-infra | 00-discover, 01-intent, 02-plan, 03-apply-verify, 04-operate |
| helix-web | 00-discover, 01-design, 02-build, 03-deploy, 04-iterate |

Data and product have parallel activity counts but data-native shape: 00
profiles sources before declaring intent; 01 contracts are first-class
(not buried inside design); 03 is `validate` (data-quality contracts as
tests); 05 collapses build/deploy/operate because pipelines run
continuously.

## Cooperating-flow scenarios

Three concrete cases the bench covers (plan §14.1):

| Scenario | Behaviour |
|---|---|
| Product PRD declares it needs a data pipeline. Marker has helix + helix-data. | helix engages first; surfaces helix-data prerequisite; offers to fire helix-data to draft a `data-product-brief` and link cross-flow. |
| Data pipeline's monitoring needs a DNS zone. Marker has helix-data + helix-infra. | helix-data engages; surfaces helix-infra prerequisite; offers to author a helix-infra `change-intent` and link cross-flow. |
| User asks "what's blocked?" in a multi-flow project. | helix engages (catch-all for "what's next/blocked"); reads ALL active flows' graphs; reports per-flow exit-gate status. |

Verified by 3 cross-flow cascade rows + the `C025` cross-flow conversation.

## Worked examples

Each flow ships a complete end-to-end worked example under
`family-test/examples/`. The example is the operator's reference and the
validator's smoke test:

- `examples/helix-data-customer-events/` — Stripe webhooks → S3 → Glue →
  Redshift, walked across all 7 helix-data activities. 11 adversarial
  fixtures F1–F11 (duplicate webhook, late arrival, schema drift, PII,
  RTBF deletion, reconciliation mismatch, lineage gap, cost overrun,
  partition skew, dead-letter replay, consumer breaking-change). Each
  artifact references its fixtures by ID;
  `helix_check.py example --adversarial-coverage` enforces 100% coverage.

A flow is not "real" until its worked example validates clean
(`helix_check.py marker .../examples/.../.helix.yml --strict` exit 0).

## Invariants (load-bearing across all flows)

1. **Edge Authority Asymmetry.** Types declare what's *possible*. Instances
   declare what's *actual*. The skill is the *deliberator*; it MUST NOT
   auto-populate `ddx.links` from graph candidates, even under
   `autonomy=autonomous`. Verified by 4 bench rows under `EA-*`.
2. **Engagement Precedes Authority.** Marker authority, scope enforcement,
   and cascade logic are meaningless until the skill engages. Routing-eval
   pass rate is the floor; every downstream phase verifies engagement
   first.
3. **Discriminating Tests Only.** Every bench row must distinguish
   skill-correct behaviour from skill-absent behaviour via a paired
   negative control. Vacuous discriminators are rejected by the runner
   (T040–T047).
