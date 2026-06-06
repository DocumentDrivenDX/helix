---
name: helix-data
description: |
  HELIX data-pipeline flow. Activate this skill when the user asks to:
    - design, build, validate, or operate a data pipeline
    - profile a data source or document a producer schema
    - specify a data contract or producer/consumer schema
    - declare PII classification or governance posture
    - author data-prd, data-product-brief, data-architecture,
      data-design, data-quality-expectations, data-quality-tests,
      backfill-plan, evolution-plan, or deprecation-notice
    - design Bronze/Silver/Gold medallion topologies
    - plan dbt models, Airflow DAGs, Databricks DLT/SDP, Glue, Beam,
      Flink pipelines
    - design backfill or reconciliation strategy
    - plan schema evolution or consumer deprecation
    - investigate freshness regression or data-quality alert
version: 0.1.0
license: MIT
---

# HELIX data-pipeline flow

This skill owns the lifecycle of ingest → transform → publish pipelines,
data contracts, quality enforcement, lineage, and backfill/evolution
operations. It does NOT own the apps that emit or consume data (that's
the `helix` product flow), the cloud accounts that host them
(`helix-infra`), or the UI dashboards that visualise them (`helix-web`).

## Activation discipline (do these in order, every time the skill engages)

### 1. Locate the marker

Find `.helix.yml` by walking UP from the current working directory to the
git root (the directory containing `.git/`). Stop at the first `.helix.yml`
encountered. Concretely: run `git rev-parse --show-toplevel`, then check
for `.helix.yml` at the top of the worktree.

### 2. Decide activation state

- **Marker present and well-formed**: parse it. The set of `flows[]`
  entries (v2; legacy alias `methodologies[]:` accepted under M020 warn)
  is authoritative. If `helix-data` is listed, this skill is active for
  the listed `root:` scope. If `helix-data` is NOT listed but a different
  flow is, defer to that flow's skill — do not also activate.

- **Marker present and malformed** (YAML parse error, missing required
  keys, root outside repo, duplicate id, root resolves to nonexistent
  dir): STOP. Report the marker error verbatim with file and line. Do
  NOT fall back to heuristics.

- **Marker absent, but the prompt matches helix-data verbs** (see
  description above — "pipeline", "data contract", "backfill", "schema
  evolution", "Bronze/Silver/Gold", "dbt", "Airflow", "DLT", "Glue",
  "freshness", "PII classification"): engage and offer to add a
  `helix-data` entry to a new `.helix.yml`. Do NOT silently proceed
  with writes outside an explicit marker scope.

- **Marker absent, no matching verbs**: report no active flow.
  Do not improvise that helix-data is active.

### 3. Enforce scope

For every operation that writes or edits a file, check that the target
path is INSIDE the active `helix-data` instance's `root:` from the
marker. If the user asks for a write outside that scope:

- Refuse the write.
- Surface the marker entry that scoped the flow and the offending
  target path.
- Ask whether they want to (a) update the marker to broaden scope, (b)
  redirect the write under the scope, or (c) cancel.

When the marker declares multiple `helix-data` instances (e.g.
`helix-data.customer-ingest`, `helix-data.orders`) at different roots,
the instance whose `root:` contains the cwd wins. If cwd is outside every
declared scope, follow the §1.5 resolution chain in the design (explicit
prefix → HELIX_FLOW env (legacy HELIX_METHODOLOGY) → cwd-under-root →
defaults.flow (legacy defaults.methodology) → single entry →
disambiguation banner with deterministic tie-break).

### 4. Author / edit artifacts

When asked to author or edit an instance document, follow the type's
`template.md` and `prompt.md` from the helix-library plugin. Look up the
type via this flow's `graph.yml` — every node points at a
`library:<slug>` or `local:<slug>` type, and the library tree mounts at
`~/.claude/plugins/<marketplace>/helix-library/<version>/`.

Instance edges (data-product-brief → data-contract, data-contract →
data-quality-expectations, etc.) belong in the instance's frontmatter
under `ddx.links:`. Never embed edges in the body or in this skill's
prompts.

Cross-flow edges (e.g. `data-product-brief informs
helix-infra:change-intent`) must be declared in `external_edges:` of
`workflows/graph.yml` first, then in the instance frontmatter with
`cross_flow: true` (legacy alias `cross_methodology: true` accepted for
one cycle).

### 5. Authorization boundary

The marker's `flows:` list (legacy `methodologies:`) is the authorization
boundary. An explicit `/helix-data <verb>` prefix wins ONLY if `helix-data` is a
marker member. If the user runs `/helix-data contract` and `helix-data`
is NOT in `.helix.yml`, REJECT with a diagnostic naming the marker as
the authorization gate, and offer to add `helix-data` to the marker as
the next action.

### 6. Frontmatter round-trip

Never rewrite unknown frontmatter keys. When you edit an instance
document's body, preserve `ddx.id`, `ddx.review`, `ddx.links`, AND any
vendor-namespaced (`x-*`) or legacy (`relationships:`, `depends_on:`)
keys byte-equivalent. Key order is preserved.

### 7. Consult the graph before authoring (cascade)

When the user asks for a new artifact of type `T`:

1. Read `helix-data`'s `workflows/graph.yml`.
2. Find the node `n` where `n.type` matches `library:T` or `local:T`.
3. Enumerate incoming edges to `n` with `kind` in
   `{requires, contains, informs}`.
4. For each such edge `(src → n, kind, required)`:
   - If `required: true` AND no instance of `src.type` exists in this
     flow's scope, surface this as a prerequisite. Per the
     autonomy slider (§8), either ask whether to draft `src` first, or
     draft it autonomously.
   - If `required: false` AND no instance of `src.type` exists, note it
     as a "consider also drafting" but do not block.
5. Once prerequisites are present (or the user has chosen to skip them),
   proceed to author the requested artifact.
6. After authoring, populate `ddx.links` to point at the upstream
   instances. Do NOT invent links; only link to existing instances
   unless `status: planned` is acceptable per the marker.

Concrete cascades for helix-data:

- **data-contract** has `informs` from `data-product-brief` and
  `source-profile`, and `requires` `consumer-inventory`. Surface any
  missing prerequisite before drafting the contract.
- **data-quality-expectations** has `requires` `data-contract`. Refuse
  to draft expectations without a contract; offer to draft the contract
  first.
- **data-quality-tests** has `requires` `data-quality-expectations`.
- **backfill-plan** has `informs` from `data-architecture` and
  `requires` `data-contract`. Never draft a backfill without naming the
  contract version the backfill restores.
- **evolution-plan** has `requires` `data-contract` and `informs`
  `deprecation-notice`. Surface affected consumers from
  `consumer-inventory` before drafting an evolution plan.
- **deprecation-notice** has `requires` `evolution-plan` AND
  `consumer-inventory`. If the inventory is stale (older than the
  contract version), flag the staleness and refuse to author the notice
  until the inventory is refreshed.

### 8. Cross-flow awareness

helix-data declares the following cross-flow edges in
`workflows/graph.yml` `external_edges:`:

- `helix:prd informs helix-data:data-product-brief` — product PRD frames
  the data product (inbound edge: declared in the helix flow's graph).
- `helix-data:data-product-brief informs helix-infra:change-intent` —
  pipeline needs new infra (outbound: declared here).
- `helix-data:metrics-dashboard informs helix:improvement-backlog` —
  metrics feed product iteration (outbound: declared here).
- `helix-web:design-system informs helix-data:metrics-dashboard` —
  dashboards inherit visual language (inbound: declared in helix-web).

When authoring an artifact that has a cross-flow edge:

1. Check whether the target flow is active in the marker.
2. If yes, surface the cross-flow link as a draft suggestion (or
   auto-author it per autonomy). Populate the instance frontmatter's
   `ddx.links` with the cross-flow target and set `cross_flow: true`
   (legacy alias `cross_methodology: true` accepted for one cycle).
3. If no, note that the cross-flow link would be ideal but the target
   flow is not active in this repo; offer to add it to the marker.

Concrete cross-flow cascades:

- When authoring `data-product-brief`, if the marker has `helix-infra`,
  surface that the pipeline will need a `helix-infra:change-intent` and
  offer to draft it (or draft autonomously). If `helix-infra` is NOT in
  the marker, surface that the new infra dependency means
  `helix-infra` should be added.
- When authoring `metrics-dashboard`, if the marker has `helix`, offer
  to draft a downstream `improvement-backlog` entry that consumes the
  dashboard's metrics.
- When asked "what's next?" or "what's blocked?" in a multi-flow repo,
  read ALL active flows' graphs and report per-flow exit-gate status
  (NOT just helix-data's).

### 9. Autonomy

The autonomy slider determines whether prerequisites and cross-flow
links are *asked about* or *drafted automatically*:

- `manual` — stop at every irreducible decision; ask for confirmation
  before any write (including marker edits and backfill drafts).
- `guided` (default) — ask before writing any new artifact, but proceed
  on confirmation; ask before any backfill/evolution/deprecation
  drafting.
- `autonomous` — engage, read, write, cascade automatically. STILL stop
  before any backfill, evolution-plan, or deprecation-notice — these
  always require explicit operator approval regardless of autonomy.
- `aggressive` — autonomous + execute. helix-data still refuses to
  EXECUTE backfills or deprecations; it will draft them and surface them
  for approval, but will not run them.

Backfills and deprecations are `stop_at` triggers per the autonomy
contract: helix-data drafts them but never executes them without
explicit operator approval, regardless of autonomy level.
