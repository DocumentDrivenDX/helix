---
title: "Design: helix-library Split"
slug: design-2026-06-03-helix-library-split
weight: 410
activity: "Design"
source: "02-design/design-2026-06-03-helix-library-split.md"
generated: true
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

# Design: helix-library Split

- **Date:** 2026-06-03 (drafted), 2026-06-04 (synthesized), 2026-06-04 (monorepo amendment)
- **Status:** Proposed (monorepo topology + test-first principle adopted 2026-06-04)
- **Scope:** Architectural refactor of the HELIX methodology family. Extract a
  shared artifact-type catalog (`helix-library`) and reshape the methodology
  repos (`helix`, `helix-infra`, future `helix-web`) as thin overlays that own
  activities, concerns, principles, and the document graph.
- **Source inputs:** facet proposals for `library-contents`,
  `methodology-skeleton`, `graph-encoding`, `skill-composition`.

---

## 0. 2026-06-04 Amendment: Monorepo Topology + Test-First

The original design (sections 1–13 below) was drafted assuming three
sibling repos (`helix-library`, `helix`, `helix-infra`) each with its
own marketplace entry, CI, and per-type semver. On 2026-06-04 the family
adopted a **monorepo topology**. This amendment summarizes what changes;
later sections retain their original text with NOTE blocks where they
no longer apply.

### Topology

The family lives in the existing `helix/` repo as subdirectories:

```
helix/
├── .claude-plugin/marketplace.json     # ONE marketplace, three plugins
├── library/                            # data plugin (no SKILL.md)
├── product/                            # current helix methodology, renamed
├── infra/                              # absorbed from helix-infra repo
├── tests/fixtures/                     # bench fixtures (test-first)
└── docs/
```

Users install whichever plugins they want via the single `helix-family`
marketplace. The standalone `helix-infra` repo is absorbed (or
deprecated with a README redirect).

### What simplifies

- **Per-type semver (§4.5):** no longer required. Everything ships from
  one commit; library and methodologies cannot drift in flight. Semver
  stays OPTIONAL as a documents-on-disk compatibility hint (the
  `library_type_version` frontmatter is still useful for validating old
  docs against the version they were authored on) but library MINOR
  bumps no longer gate methodology releases.
- **`validator_contract_version` handshake (§6.2):** removed. One
  validator, one tree, one CI. The handshake existed to catch cross-repo
  drift that can no longer happen.
- **Three-step resolution chain (§7.3):** collapses to "look at the
  co-resident `library/`." Resolver tries the relative path
  (`../library/` from a methodology root, or `<repo-root>/library/`)
  first; only falls back to `~/.claude/plugins/helix-library/` when a
  user has installed a single methodology plugin without the library.
- **DDx bead schema (§Phase D0 in plan):** still real (DDx is its own
  surface), but lands in the same commit cadence as the methodologies.

### What stays the same

- Library/methodology architectural split (data plugin vs methodology overlay).
- Two-namespace scheme (`library:` / `local:`); bare slugs still rejected.
- `graph.yml` per methodology.
- Edge model (`requires` / `informs` / `may_surface`).
- Co-activation precedence + bench fixtures (§7.5). MORE important now
  because the family is test-first — see below.
- Additive-only overrides + `_overlays/<binding-id>/` for multi-line.
- Generated activity READMEs.
- ADR as ONE library type with section_aliases.
- 30 types promoted in v1; `architecture` and `contract` stay
  product-local.

### Test-first principle

Bench fixtures are authored FIRST, in a separate workflow phase, BEFORE
any reorganization. The fixtures double as the executable spec for the
family architecture (co-activation precedence, resolver fallback,
override merge, single-plugin install, negative controls). The migration
is "done" when all bench fixtures pass.

### Revised migration shape

The 14-PR / 55h sibling-repo plan in the migration doc is replaced by
~6 PRs / ~25-30h:

1. Reorganize (move existing helix tree to `product/`, scaffold
   `library/` and `infra/`, one CI pipeline, one `marketplace.json`).
2. Promote 30 artifact types to `library/`.
3. Absorb helix-infra into `infra/`.
4. DDx bead schema (`graph_node:` field).
5. Verification (run all bench fixtures green).
6. Tag family release.

The FINAL plan (`plan-2026-06-03-helix-library-FINAL.md` §0) is the
entry-point document for the revised shape.

---

## 1. Goals and Non-Goals

### Goals

- One canonical definition per shared artifact type. ADRs, runbooks, risk
  registers, etc. live in exactly one place across the family.
- Each methodology repo declares only what is methodology-shaped:
  activities, concerns, principles, the document graph, and methodology-local
  artifact types.
- Adding `helix-web` (or any future variant) means: write a `graph.yml`, write
  concerns and principles, and bind library types into activities. No template
  duplication.
- Existing HELIX and helix-infra ADRs, runbooks, etc. continue to validate
  after migration (no document rewrite required).

### Non-Goals

- A general-purpose templating engine. The library is a catalog of typed
  artifacts, not a DSL.
- Auto-resolving cross-methodology version drift. Methodologies pin a library
  major and the family ships in lockstep at major boundaries.
- Replacing DDx as the workflow runtime. The library + methodology repos are
  the content layer; DDx still owns beads, queue, and dispatch.

---

## 2. Architecture Overview

```
                       +--------------------------+
                       |     helix-marketplace    |
                       |    marketplace.json      |
                       |  co-lists 3+ plugins     |
                       +-----------+--------------+
                                   |
              +--------------------+--------------------+
              |                    |                    |
              v                    v                    v
   +---------------------+  +-----------------+  +-----------------+
   |   helix-library     |  |     helix       |  |  helix-infra    |
   |   (data plugin)     |  |  (methodology)  |  |  (methodology)  |
   |  no SKILL.md        |  |  skills/helix/  |  |  skills/helix-  |
   |  library/types/...  |  |  workflows/...  |  |  infra/         |
   |  library/concerns/  |  |                 |  |  workflows/...  |
   +----------+----------+  +--------+--------+  +--------+--------+
              ^                      |                    |
              |                      |                    |
              +----------- resolved at runtime by methodology SKILL.md
                           via the catalog-resolution chain
```

| Component        | Owns                                                         | Does NOT own                                          |
| ---------------- | ------------------------------------------------------------ | ----------------------------------------------------- |
| `helix-library`  | Artifact-type definitions, shared concern definitions, templates, prompts, examples, validation rules (shape). | Activity placement, document-graph edges, methodology-specific concerns or principles, approver role names. |
| `helix` / `helix-infra` / `helix-web` | Activities (`activity.yml` + `README.md`), concerns (local set), principles (local instance), `graph.yml`, methodology-local artifact types, `SKILL.md`. | Library-typed artifact templates, prompts, or shape rules. |
| Methodology `SKILL.md` | When to activate, slash commands, narrative behaviour, the catalog-resolution prose. | Templates. Resolves them from the library at runtime. |

Two namespaces are used in all cross-references:

- `library:<slug>` — resolves under the library catalog tree.
- `local:<slug>` — resolves under the methodology's own `workflows/artifacts/`.

Bare slugs are deprecated; existing per-artifact `meta.yml` `relationships`
become methodology-side edges in `graph.yml`.

---

## 3. Library Contents (v1)

Library v1 ships **30 types** — every type marked `universal` in the inventory
plus four contested-as-library decisions (`adr`, `principles`, `concerns`,
`business-case`).

### Promoted (universal shape — in library)

`resource-summary`, `compliance-requirements`, `concerns`, `feasibility-study`,
`parking-lot`, `principles`, `research-plan`, `risk-register`,
`security-requirements`, `stakeholder-map`, `threat-model`,
`validation-checklist`, `adr`, `security-architecture`, `proof-of-concept`,
`tech-spike`, `security-tests`, `test-plan`, `test-procedures`, `test-suites`,
`implementation-plan`, `deployment-checklist`, `monitoring-setup`,
`release-notes`, `runbook`, `improvement-backlog`, `metric-definition`,
`metrics-dashboard`, `security-metrics`, `business-case`.

### Stays methodology-local (in `helix`)

`competitive-analysis`, `opportunity-canvas`, `product-vision`, `pr-faq`,
`prd`, `feature-registry`, `feature-specification`, `user-stories`,
`solution-design`, `technical-design`, `story-test-plan`, `design-system`,
`data-architecture`, `data-design`, `data-quality-expectations`,
`architecture`, `contract`.

> Note: `architecture` and `contract` are flagged "methodology-agnostic but
> currently product-shaped" in the inventory. They stay HELIX-local in v1.
> Promotion to the library is deferred until `helix-web` or another consumer
> demonstrates a second instance — at that point a generic `architecture` or
> `topology` type can be carved out without speculative design.

### Stays methodology-local (in `helix-infra`)

`change-intent`, `change-plan`, `apply-evidence`, `module-guide`.

### Variants resolved as siblings, not subtypes

- **ADR**: ONE library type. Required sections are the superset
  (`context`, `decision_drivers`, `considered_options`, `decision`,
  `consequences`, `status`). Section aliases (`alternatives`→`considered_options`,
  `drivers`→`decision_drivers`) make existing HELIX ADRs validate unchanged.
  Methodology-specific drivers (e.g. helix-infra's "concern_traced") are
  appended via graph-side overrides, not by forking the type.
- **runbook vs module-guide**: `runbook` ships in the library; `module-guide`
  stays in `helix-infra` as a methodology-local type. The latter's `meta.yml`
  carries a documentation-only `references: [{title: "Adapted from",
  file: "library:runbook"}]` link.
- **contract vs module-interface**: same pattern — `contract` in library,
  `module-interface` is helix-infra-local (deferred to a future version if it
  emerges).

### 3.1 New-type promotion workflow

When a methodology needs an artifact type the library doesn't have (e.g.
hypothetical `helix-data` adding `data-contract`):

1. **Ship local first.** The requesting methodology declares
   `type: local:data-contract` in its `graph.yml` and ships the four files
   in `workflows/artifacts/data-contract/`. No library change required.
2. **Demonstrate use.** A second methodology adopts the same type
   independently (also as `local:`), demonstrating cross-methodology fit.
3. **Promote.** Open a PR against `helix-library` that adds the type under
   `types/data-contract/`. This is a library MINOR bump (additive). Each
   methodology updates its `graph.yml` from `local:data-contract` to
   `library:data-contract` at its own pace; no family lockstep required.

This makes the cost of "wrong" promotion symmetric: it's cheap to keep a
type local, and cheap to promote later. The architecture/contract policy
of §3 is the general rule.

---

## 4. Library `meta.yml` Shape and Extension Semantics

### 4.1 Canonical library `meta.yml`

The library `meta.yml` is **methodology-agnostic**. It drops:

- `activity:` (placement is methodology-owned)
- `output.location` (becomes a default, overridable per binding)
- `workflow.approvers` (role names are methodology-specific)
- `relationships.informed_by` / `relationships.informs` (graph edges live in
  `graph.yml`)

Worked example (`helix-library/types/adr/meta.yml`):

```yaml
schema_version: 1
artifact:
  name: Architecture Decision Record
  id: adr
  type: document
  level: project

id_format:
  prefix: ADR
  pattern: "ADR-[0-9]{3}"
  example: ADR-001

description: |
  An ADR records one non-obvious decision: context, alternatives, choice,
  consequences. Immutable once Accepted. To revise, create a new ADR with
  Supersedes: ADR-XXX.

default_output:
  location: docs/adr/ADR-{number}-{decision-name}.md
  format: markdown
  naming: ADR-{number}-{decision-name}.md

reuse_policy: write-once

validation:
  required_sections:
    - context
    - decision_drivers
    - considered_options
    - decision
    - consequences
    - status
  section_aliases:
    considered_options: [alternatives]
    decision_drivers:   [drivers]
  pattern_checks:
    - pattern: "ADR-[0-9]{3}"
      expected: ">=1"
    - pattern: "Proposed|Accepted|Rejected|Deprecated|Superseded"
      expected: ">=1"
  quality_checks:
    - check: single_decision
      severity: blocking
    - check: alternatives_evaluated
      severity: blocking
    - check: consequences_explicit
      severity: warning

prompts:
  generation: prompt.md
  review: review.md

template:
  file: template.md

example:
  file: example.md

tags: [architecture, decision-record]
version: 1.0.0
```

### 4.2 Extension via graph.yml overrides (NOT via overlay.yml)

The four facet proposals diverged on the extension mechanism:

- `library-contents` proposed sidecar `binding.yml` + `overlay.yml` files at
  `workflows/activities/<NN>/artifacts/<slug>/`.
- `graph-encoding` proposed inline `config:` / `overrides:` blocks on each
  graph node in `workflows/graph.yml`.

**Reconciliation: graph.yml owns it.** The `library-contents` facet's
overlay-files-per-binding design effectively recreates the artifacts-subdir
sprawl the migration is meant to retire. The `graph-encoding` facet's
inline-override design keeps the methodology shape in one diffable file. We
adopt graph.yml as the single binding+override surface, with one carve-out:
when an override needs more than a few lines (a multi-paragraph prompt
appendix, a non-trivial template addition), the graph node may point to
companion files at `workflows/artifacts/_overlays/<binding-id>/{prompt-append.md,template-append.md}`.

### 4.3 Override rules (additive only)

The resolver merges library `meta.yml` + graph-node `overrides:` into a single
resolved spec at load time. Rules:

| Field                          | Override semantics                                 |
| ------------------------------ | -------------------------------------------------- |
| `required_sections`            | Union with `overrides.extra_required_sections`. Additive only — cannot remove. |
| `quality_checks`               | Append `overrides.extra_quality_checks`. IDs unique per methodology. |
| `pattern_checks`               | Append.                                            |
| `prompts.generation`           | Library file is canonical. Overlay may concatenate `prompt-append.md`. |
| `template.file`                | Library file is canonical. Overlay may concatenate `template-append.md`. |
| `default_output.location`      | Replaceable per binding.                           |
| `relationships`                | Not in library. Owned by `graph.yml` edges.        |

Rationale: additive-only overlays force methodologies to pick the library
type that fits, or declare a methodology-local type. They cannot silently
weaken a library-declared shape.

### 4.4 Resolved spec at load time

A `library:adr` node in helix-infra resolves to:

```
required_sections = base ∪ extra        (no shrinkage)
quality_checks    = base ++ extra        (severity preserved)
prompt            = base ++ prompt_append (string concat)
template          = base ++ template_append
relationships     = graph-derived (informed_by/informs from edges)
output.location   = override OR base default
```

Validators consume the resolved spec; the author of an artifact never sees the
split.

### 4.5 Library type versioning (per-type semver, no lockstep on minor)

> NOTE: section superseded by monorepo decision 2026-06-04. Per-type
> semver is no longer required because library, product, and infra ship
> from the same commit. The `library_type_version` frontmatter remains
> a useful documents-on-disk compatibility hint (validating an old doc
> against the spec it was authored on), but the per-type bump rules and
> the deprecation-window protocol are obsolete: family advances in
> lockstep at every commit. Original section preserved below for audit.

Each library type carries its own semver in `meta.yml.version`. Library-wide
versioning composes these:

- **Patch (1.0.x):** typo, wording, alias-only changes. No methodology action.
- **Minor (1.x.0):** ADDITIVE only — new types, new optional fields, new
  `section_aliases`, NEW `required_sections` entering as `severity: warning`.
  Methodologies pinning `^1.0.0` pick this up automatically; no methodology
  release required.
- **Major (2.0.0):** any breaking change — a warning-grade `required_section`
  promotes to `blocking`, a type is removed, a field semantic changes.
  Lockstep applies: every methodology in the family must republish against
  library 2.x before users upgrade.

**Document-side version recording.** Every artifact instance writes
`library_type_version: 1.0.0` into its frontmatter at creation. The validator
loads the SPEC THAT WAS CURRENT WHEN THE DOCUMENT WAS CREATED for in-flight
validation, and the SPEC THAT IS CURRENT IN THE PINNED METHODOLOGY for new
documents. Migration of an existing doc to a newer spec is opt-in (run
`helix migrate-doc <path> --target-version 1.1.0` to re-validate and stamp
the new version).

**Deprecation-window protocol for newly-required sections.** A new
`required_sections` entry MUST enter library catalog as
`severity: warning` for at least one minor release. It only promotes to
`blocking` at the next major. This prevents "library 1.0.5 bricks every
in-flight ADR overnight."

**Cross-methodology pinning.** Two methodologies in the family MAY pin
different library minors (e.g. `helix@^1.0.0` and `helix-infra@^1.1.0`).
The resolution chain finds the library version closest to each methodology's
pin; if the user's installed library satisfies both, both work. If not, the
methodology surfaces a setup-gap message naming the required range.

### 4.6 Forking a library type (opt-out path)

A methodology may decide a library type no longer fits — e.g. it wants
to weaken a section that additive-only overrides forbid. Forking is:

1. Copy the library type tree to
   `<methodology>/workflows/artifacts/<slug>/`.
2. Change every `graph.yml` reference from `type: library:adr` to
   `type: local:adr`. The `local:` qualifier makes the shadow explicit;
   `local:adr` shadows `library:adr` ONLY within that methodology's graph.
3. Existing on-disk documents continue to validate because forks start
   as supersets (you cannot remove sections in-flight; only the local
   type's NEXT major may shrink them).
4. Reverse migration (going back to `library:adr` later) is allowed; the
   validator emits per-document migration tickets for any doc that drifted
   from the library shape during the fork.

The validator rejects a graph that declares both `library:adr` and
`local:adr` as separate nodes referring to the same conceptual type — pick
one. (To run a true variant, use a different slug: `local:adr-lightweight`.)

---

## 5. Methodology Skeleton (post-migration)

### 5.1 File-by-file layout (helix-infra)

```
helix-infra/
├── AGENTS.md
├── CLAUDE.md
├── README.md
├── justfile
├── .claude-plugin/
│   └── plugin.json                       # declares requires: [helix-library]
├── docs/                                 # unchanged
├── scripts/
│   ├── helix_graph_check.py              # NEW — graph validator
│   └── helix_graph_render.py             # NEW — renders activity READMEs
├── skills/
│   └── helix-infra/
│       ├── SKILL.md                      # see §7
│       └── vendor/                       # optional, release-build only
│           └── helix-library/            # frozen snapshot for offline installs
└── workflows/
    ├── methodology.yml                   # NEW — methodology manifest
    ├── graph.yml                         # NEW — the document graph
    ├── principles.md                     # stays (local instance)
    ├── library-manifest.yml              # OPTIONAL — quick-lookup index
    ├── activities/
    │   ├── 01-intent/
    │   │   ├── activity.yml              # NEW
    │   │   └── README.md                 # generated from graph.yml
    │   ├── 02-plan/
    │   │   ├── activity.yml
    │   │   └── README.md                 # generated
    │   └── 03-apply-verify/
    │       ├── activity.yml
    │       └── README.md                 # generated
    ├── concerns/                         # unchanged shape
    │   ├── blast-radius-and-rollout/
    │   ├── credentials-and-state-secrets/
    │   ├── drift-and-verification/
    │   ├── privileged-access-impact/
    │   ├── resource-ownership-boundary/
    │   └── state-boundaries/
    │       └── {concern.md, practices.md}
    └── artifacts/                        # methodology-local types ONLY
        ├── change-intent/
        │   ├── meta.yml
        │   ├── template.md
        │   ├── prompt.md
        │   └── example.md
        ├── change-plan/
        ├── apply-evidence/
        ├── module-guide/
        └── _overlays/                    # multi-line graph overrides
            └── adr@02-plan/
                ├── prompt-append.md
                └── template-append.md
```

What disappeared from helix-infra: the per-activity `artifacts/<slug>/` tree
for any library-resolved type. ADR's four files (`meta.yml`, `template.md`,
`prompt.md`, `example.md`) no longer exist in helix-infra — they live in
`helix-library/types/adr/`.

### 5.2 `methodology.yml` (manifest)

```yaml
id: helix-infra
name: HELIX for Infrastructure
version: 0.2.0

library:
  plugin: helix-library
  version_range: ">=1.0.0, <2.0.0"
  resolution_chain:
    - ~/.claude/plugins/helix-library/
    - ../../../helix-library/                  # sibling dev checkout
    - ./skills/helix-infra/vendor/helix-library/   # frozen release build

principles_instance: ./principles.md
concerns_root:        ./concerns
activities_root:      ./activities
graph:                ./graph.yml
local_artifacts_root: ./artifacts
```

### 5.3 `activity.yml` (per activity)

```yaml
id: 02-plan
name: Plan
purpose_ref: ./README.md#purpose
exit_gate: plan-validation                # node id in graph.yml
inputs_from:  [01-intent]
outputs_to:   [03-apply-verify]
```

Activity-level prose (purpose, narrative inputs/outputs, exit-gate language)
stays in `README.md`. The README is generated from `graph.yml` + the
`narrative.md` companion file, eliminating the drift class.

---

## 6. Document Graph (`graph.yml`)

`graph.yml` is the single source of truth for which artifact types appear in
which activity, with what dependencies, cardinality, and overrides. The
library is methodology-agnostic; everything methodology-shaped lives here.

### 6.1 Full worked example — helix-infra

```yaml
# helix-infra/workflows/graph.yml
version: 1
methodology:
  id: helix-infra
  library_version: "^1.0.0"

activities:
  - id: 01-intent
    name: Intent
    exit_gate: intent-validation
  - id: 02-plan
    name: Plan
    exit_gate: plan-validation
  - id: 03-apply-verify
    name: Apply & Verify
    exit_gate: apply-validation

# Singletons available from a given activity onward.
cross_cutting:
  - node: concerns
    type: library:concerns
    scope: singleton
    available_from: 01-intent
    overrides:
      allowed_concerns:
        - state-boundaries
        - resource-ownership-boundary
        - blast-radius-and-rollout
        - drift-and-verification
        - credentials-and-state-secrets
        - privileged-access-impact

  - node: principles
    type: library:principles
    scope: singleton
    available_from: 01-intent

nodes:
  # ---- 01-intent ----
  - id: change-intent
    type: local:change-intent
    activity: 01-intent
    cardinality: one-per-change
    requires: []

  - id: intent-validation
    type: library:validation-checklist
    activity: 01-intent
    cardinality: singleton-per-activity
    requires: [change-intent]
    role: exit-gate

  # ---- 02-plan ----
  - id: change-plan
    type: local:change-plan
    activity: 02-plan
    cardinality: one-per-change-intent
    requires: [change-intent]
    may_surface: [adr]

  - id: adr
    type: library:adr
    activity: 02-plan                       # nominal home
    scope: cross-cutting                    # may be produced anywhere
    cardinality: many
    requires: []
    overrides:
      extra_quality_checks:
        - id: concern_traced_to_iac_concerns
          description: |
            Decision must cite at least one of the six helix-infra concerns
            as a driver, or explicitly note "none — pure mechanics".
          severity: warning
      prompt_append:   _overlays/adr@02-plan/prompt-append.md
      template_append: _overlays/adr@02-plan/template-append.md

  - id: plan-validation
    type: library:validation-checklist
    activity: 02-plan
    cardinality: singleton-per-activity
    requires: [change-plan]
    role: exit-gate

  # ---- 03-apply-verify ----
  - id: apply-evidence
    type: local:apply-evidence
    activity: 03-apply-verify
    cardinality: one-per-change-plan
    requires: [change-plan]

  - id: module-guide
    type: local:module-guide
    activity: 03-apply-verify
    cardinality: one-per-module
    requires: [apply-evidence]

  - id: apply-validation
    type: library:validation-checklist
    activity: 03-apply-verify
    cardinality: singleton-per-activity
    requires: [apply-evidence, module-guide]
    role: exit-gate

allowed_cycles: []
```

### 6.1.1 Edge types

`graph.yml` supports three edge kinds:

| Edge          | Semantics                                                       | Validator action                  |
| ------------- | --------------------------------------------------------------- | --------------------------------- |
| `requires:`   | Hard prerequisite. Target document MUST exist before this node is dispatchable. | Enforced. Walked in acyclicity check. |
| `informs:`    | Forward soft edge. "This artifact informs that later artifact." Advisory; used for traceability rendering. | Recorded; NOT enforced.           |
| `may_surface:`| Optional production. "While working on this node you MAY also produce instances of that node." | Recorded; renderer surfaces in UI. |

Forward `informs:` edges are walked across activities for traceability
rendering (e.g. "ADR-007 informs runbook RB-002"). They do NOT participate
in the acyclicity check.

`requires:` may cross activities backward (always — e.g. `apply-validation`
in activity 03 requires `apply-evidence` in activity 03 and indirectly
`change-plan` from 02). Cross-activity backward `requires:` is the default;
no special markup needed.

### 6.1.2 `allowed_cycles` worked example

The HELIX 06-iterate → 01-frame "loop" is modeled as a typed re-entry edge
that the runner walks but the acyclicity checker skips:

```yaml
allowed_cycles:
  - from: 06-iterate
    to:   01-frame
    kind: re-entry
    rationale: |
      Iteration learnings re-open the framing activity. Each pass is a
      new walk over the graph; in-document references to prior PRDs are
      explicit ("Supersedes PRD-003").
```

Re-entry edges:

- Are walkable by the runner (the skill can dispatch back into 01-frame).
- Are SKIPPED by the acyclicity check (the graph remains a DAG modulo
  `allowed_cycles`).
- Require an explicit `kind:` and `rationale:` for reviewability.

### 6.2 Validator contract (`helix-library/scripts/helix_graph_check.py`)

**Ownership:** the validator lives in `helix-library`, not duplicated in each
methodology. Methodologies invoke it via the catalog resolution chain:

```
# in each methodology's justfile
check-graph:
    python3 $(./scripts/resolve-library-root.sh)/scripts/helix_graph_check.py \
        --methodology workflows/
```

A tiny per-methodology `resolve-library-root.sh` walks the §7.3 chain to
locate the library root (managed plugin → sibling dev → vendored release).

**Validator contract version.** The library publishes
`validator_contract_version: 1` (constant declared in
`helix-library/scripts/CONTRACT_VERSION`). Each methodology's `graph.yml`
declares `validator_contract: 1`. The validator hard-fails on mismatch,
naming both the library version and the methodology's expected contract.

This eliminates the by-copy validator drift and gives the family one upgrade
surface for graph-shape rules.

> NOTE: `validator_contract_version` handshake superseded by monorepo
> decision 2026-06-04. With one tree, one validator, one CI, cross-repo
> drift cannot occur, so the handshake is removed. The validator still
> lives under `library/scripts/`; methodologies still invoke it via the
> co-resident path. The `CONTRACT_VERSION` file is dropped.

Deterministic, py3-stdlib only. Asserts:

1. Every `nodes[].type` resolves: `library:<id>` exists in pinned library;
   `local:<id>` exists under `workflows/artifacts/<id>/meta.yml`.
2. Every `requires` / `may_surface` target is a declared node id.
3. Every `activities[].exit_gate` is a node with `role: exit-gate` in that
   activity.
4. The DAG over `requires` is acyclic except for `allowed_cycles`.
5. Each activity has at least one non-exit-gate node.
6. `overrides.extra_required_sections` does not name a section already in
   the library base (additive-only enforcement).
7. `overrides.extra_quality_checks[].id` is unique per methodology.
8. `cross_cutting` nodes are not duplicated in `nodes`.

### 6.3 Runtime query surface

```
graph.nodes_for_activity("02-plan")
graph.prerequisites("change-plan")
graph.unmet_prerequisites(node_id, filesystem_state)
graph.exit_gate("02-plan")
graph.is_activity_complete("02-plan", state)
graph.resolve_type("adr")          # merged spec
```

These are the only entrypoints the skill needs at runtime.

### 6.4 Activity READMEs are generated

`scripts/helix_graph_render.py` walks `graph.yml` + the per-activity
`narrative.md` companion file (hand-authored prose) and emits
`activities/<id>/README.md`. The README carries a banner:

```
<!-- generated from graph.yml + narrative.md — edit those, not this -->
```

CI re-runs the renderer and fails on diff.

---

## 7. Skill Composition

### 7.1 Decision: library is a data plugin, not a skill

`helix-library` ships as a Claude Code plugin with a `plugin.json` but **no
`skills/` directory**. It exposes only a data tree. Routing decisions and
slash commands live exclusively in methodology skills.

Rationale: a library SKILL.md has no user-facing intent — users never ask "load
the ADR template", they ask "frame a PRD" (which a methodology skill handles,
and IT then resolves the template from the catalog). A second skill would
either never activate (wasteful) or compete for routing (incorrect).

### 7.2 Marketplace

> NOTE: section partially superseded by monorepo decision 2026-06-04.
> The marketplace.json shape is unchanged (one marketplace, three plugin
> entries, the `requires` field still advisory), but the `source.url`
> entries all point at the SAME repo with different subdirectories.
> Concretely each `source` becomes
> `{"source": "url", "url": "https://github.com/DocumentDrivenDX/helix.git", "subdirectory": "library"}`
> (and `"subdirectory": "product"` / `"infra"` for the other two). The
> name "helix-family" replaces "helix" as the marketplace id to reflect
> that one repo serves all three plugins.

One marketplace co-lists the family:

```json
{
  "name": "helix",
  "description": "HELIX methodology family + shared artifact-type library",
  "owner": { "name": "DocumentDrivenDX",
             "url": "https://github.com/DocumentDrivenDX" },
  "plugins": [
    {
      "name": "helix-library",
      "description": "Shared artifact-type catalog. Data tree, no skill.",
      "source": { "source": "url",
                  "url": "https://github.com/DocumentDrivenDX/helix-library.git" }
    },
    {
      "name": "helix",
      "description": "Product/feature methodology. Requires helix-library.",
      "source": { "source": "url",
                  "url": "https://github.com/DocumentDrivenDX/helix.git" },
      "requires": ["helix-library"]
    },
    {
      "name": "helix-infra",
      "description": "IaC operator methodology. Requires helix-library.",
      "source": { "source": "url",
                  "url": "https://github.com/DocumentDrivenDX/helix-infra.git" },
      "requires": ["helix-library"]
    }
  ]
}
```

We do **not** depend on `requires` auto-installing dependencies. If the user
ends up with helix installed but no helix-library, the methodology skill
surfaces a clear setup-gap message on first invocation.

### 7.3 Catalog resolution chain (replaces today's §Catalog Resolution)

> NOTE: chain collapses under monorepo decision 2026-06-04. With
> library, product, and infra co-resident, the resolver tries the
> well-known relative path first (`<monorepo-root>/library/`, reachable
> from either methodology root as `../library/`) and falls back to
> `~/.claude/plugins/helix-library/` only for users who installed a
> single methodology plugin without the library. Steps 2b (sibling dev
> checkout — same shape as the monorepo case, just inside one repo) and
> 2c (vendored release) collapse into the single co-resident lookup.
> Original three-step chain preserved below for audit and for the
> single-plugin install case.

Methodology `SKILL.md` carries this prose:

```markdown
## Catalog Resolution

When a workflow mode needs an artifact template, prompt, or quality criteria,
resolve in this order:

1. **Methodology-local catalog** — `<plugin-root>/workflows/artifacts/<type>/`.
   Used for types this methodology owns exclusively. The list of
   methodology-local types is the union of `local:` entries in
   `<plugin-root>/workflows/graph.yml`.

2. **Shared library catalog** — `<library-root>/types/<type>/`. Resolve
   `<library-root>` by trying, in order:
   a. `~/.claude/plugins/helix-library/`
   b. `<plugin-root>/../helix-library/` (sibling dev checkout)
   c. `<plugin-root>/skills/<methodology-id>/vendor/helix-library/`
      (vendored release build)

3. If nothing resolves: surface a setup gap naming the missing plugin and the
   install command. Do NOT improvise paths, invent template content, or fall
   back to prior knowledge of what the type "usually looks like."

The mapping of type to activity lives in `workflows/graph.yml`, NOT in the
library — the library is methodology-agnostic; activity assignment is a
methodology choice.
```

### 7.4 Reference scheme

All cross-tree references in `graph.yml`, `activity.yml`, and prose use the
two-namespace scheme:

- `library:<slug>` — under the resolved library root.
- `local:<slug>` — under `<plugin-root>/workflows/artifacts/`.

Bare slugs are rejected by the validator at v1.

### 7.5 Co-activation and precedence (mixed repos, both skills loaded)

The default install state per §7.2 leaves users with multiple methodology
skills loaded (e.g. `helix` + `helix-infra`). A repo may also legitimately
contain BOTH signals (an infra repo that documents its own product shape).
This is the precedence contract:

**Detection signals (per methodology).** Each methodology SKILL.md declares
detection signals in frontmatter:

```yaml
# skills/helix-infra/SKILL.md frontmatter
detection:
  signals:
    - path_exists: workflows/methodology.yml
      methodology_id: helix-infra
    - file_glob: ["*.tf", "*.tfvars", "providers.yml", "main.tf"]
      weight: 0.5
```

```yaml
# skills/helix/SKILL.md frontmatter
detection:
  signals:
    - path_exists: workflows/methodology.yml
      methodology_id: helix
    - path_exists: docs/helix/
      weight: 0.5
```

**Precedence rules (in order).**

1. **Active methodology wins.** If the current working tree's git root
   contains `workflows/methodology.yml`, that methodology owns the routing.
   The other methodology's skill defers.
2. **CWD context wins.** If the user is editing a file under a methodology's
   `workflows/` or `docs/` tree, that methodology wins.
3. **Single high-confidence signal wins.** If only one methodology's strong
   signal (a `methodology.yml`) fires, it wins.
4. **Both fire, neither dominant.** The skill that activates emits a
   one-line disambiguation banner:

   ```
   Both helix and helix-infra detect this repo. Defaulting to helix
   (alphabetical). Override: prefix the command with "/helix-infra ..." or
   set HELIX_METHODOLOGY=helix-infra in shell.
   ```

   Deterministic tie-break: alphabetical by methodology id.
5. **Explicit override always wins.** `HELIX_METHODOLOGY=<id>` env var or
   command prefix (`/<methodology-id> <verb>`).

**Generic verbs route by active methodology.** "Create an ADR" with both
skills loaded routes to whichever methodology won by rules 1–4. The
disambiguation banner fires when the choice is non-obvious (rule 4).

**Bench fixture (required).** `tests/fixtures/co-activation/` contains:

- `infra-only/` — only `*.tf` and `workflows/methodology.yml` for helix-infra.
- `product-only/` — only `docs/helix/` and `workflows/methodology.yml` for helix.
- `mixed/` — both `*.tf` AND `docs/helix/`, no `workflows/methodology.yml`.
- `dual-methodology/` — two methodology roots in subdirs.

Bench asserts the correct skill activates (or the banner fires) for each
fixture.

---

## 8. Cross-Facet Reconciliation

Five conflicts surfaced across facets; resolutions below.

### 8.1 Extension mechanism: overlay.yml vs graph.yml overrides

- **Conflict:** `library-contents` proposed sidecar `binding.yml` +
  `overlay.yml` files. `graph-encoding` proposed inline `overrides:` blocks
  on graph nodes.
- **Resolution:** graph.yml is canonical. Inline overrides for short edits;
  `workflows/artifacts/_overlays/<binding-id>/{prompt-append.md,template-append.md}`
  for multi-line appends. Sidecar `binding.yml` is rejected — it recreates
  the artifacts-subdir sprawl the migration is meant to retire.

### 8.2 Activity ownership in library `meta.yml`

- **Conflict:** All facets agreed `activity:` should leave library `meta.yml`,
  but disagreed where it goes — `methodology-skeleton` put it in
  `activity.yml`, `graph-encoding` put it on each graph node, `skill-composition`
  put it in `library-manifest.yml`.
- **Resolution:** Activity placement lives on the **graph node**
  (`graph.yml`). `activity.yml` references nodes by id for its exit-gate.
  `library-manifest.yml` is downgraded to an optional convenience index
  generated from `graph.yml` (not authored).

### 8.3 References format: bare slug vs qualified id

- **Conflict:** `library-contents` used bare slugs (`adr`), `methodology-skeleton`
  and `graph-encoding` used qualified ids (`library:adr` / `local:adr`).
- **Resolution:** qualified ids everywhere. The validator rejects bare slugs.
  This costs a small amount of typing in exchange for unambiguous resolution
  when a methodology declares both `library:adr` and `local:adr-variant`.

### 8.4 Library distribution: vendored vs plugin

- **Conflict:** `methodology-skeleton` made the library vendored by default
  (via subtree). `skill-composition` made it a separate plugin by default.
- **Resolution:** Separate plugin by default; vendored as a release-build
  option (last fallback in the resolution chain). `methodology.yml.library`
  enumerates the resolution chain explicitly so each install style works.

> NOTE: superseded by monorepo decision 2026-06-04. Library, product,
> and infra are co-resident in one repo, so "vendored" and "separate
> plugin" collapse: there is one tree. Users who install a single
> plugin (just `helix` or just `helix-infra`) still get the library
> co-installed because the marketplace bundles it; the resolver still
> finds it via the co-resident relative path. The
> `methodology.yml.library` resolution chain is reduced to a single
> well-known relative path; the entry remains for the (rare) split
> install where a user took a methodology plugin and an
> out-of-tree library override.

### 8.5 Cross-cutting nodes (ADR, concerns, principles)

- **Conflict:** `graph-encoding` introduced `scope: cross-cutting`.
  `methodology-skeleton` modeled them as ordinary nodes with cardinality
  `many`.
- **Resolution:** Adopt `scope: cross-cutting`. ADR explicitly may be
  produced from any activity; concerns and principles are
  `scope: singleton, available_from: 01-intent`. The validator allows
  cross-cutting nodes to be referenced from any activity's `requires`.

---

## 9. Tradeoffs Accepted

1. **Additive-only overlays.** Methodologies cannot shrink a library type's
   required sections. If a methodology needs fewer sections, it forks the
   type. Mitigated by choosing supersets as library defaults (e.g. ADR uses
   the helix-infra-superset of 6 sections; HELIX's 4-section list is a
   strict subset).
2. **Section aliases (`alternatives`→`considered_options`)** ship in
   `meta.yml`. Adds resolver complexity in exchange for zero-rewrite
   migration of existing HELIX ADRs.
3. **Activity READMEs become generated.** Drift class eliminated, at the
   cost of a workflow change for editors. Banner + companion
   `narrative.md` mitigates this.
4. **Library plugin has no SKILL.md.** Atypical for Claude Code plugins.
   The library's README clearly states "data tree, no skill", and the
   marketplace description repeats it.
5. **`requires:` is advisory.** Setup-gap message on first invocation is
   the actual safety net.
6. **Two namespaces (`library:` / `local:`)** are typed everywhere a slug
   appears. Verbosity in exchange for unambiguous resolution under overrides.
7. **Single ADR with optional section_aliases instead of variant subtypes.**
   No `adr-with-concern-trace` / `adr-with-ac-trace` zoo; methodology
   wires intent via graph-node overrides.
8. **`architecture` and `contract` stay HELIX-local in v1.** Defers
   generalization until a second methodology demonstrates an instance.
   `helix-infra`'s topology design lives as a methodology-local type for now.
9. **Library version pinning is lockstep at MAJOR boundaries only.** Library
   MINOR (additive — new types, new optional fields, new aliases, warning-grade
   sections) does NOT require methodology releases. Each methodology pins
   `^1.0.0` and picks up minor improvements automatically. Methodologies may
   pin different minors in flight. MAJORs require family-wide republish. See
   §4.5 for the full versioning model.

   > NOTE: superseded by monorepo decision 2026-06-04. Family ships from
   > one commit so "library minor without methodology release" is no
   > longer a thing — every change is a family release. Tradeoff is moot.
10. **Vendored fallback duplicates bytes per release build.** Accepted for
    offline / air-gapped installs that cannot rely on a sibling plugin.

---

## 10. Resolved Questions (review-folded)

1. **Resolver / validator location.** RESOLVED: lives in
   `helix-library/scripts/helix_graph_check.py`. Methodologies invoke it
   via the resolution chain. See §6.2 and the `validator_contract_version`
   handshake.
2. **Template heading vs required_sections.** RESOLVED: validator accepts
   any canonical-or-aliased heading. Validator fails only if NO heading
   variant is present in the resolved template. `template_append.md` SHOULD
   include canonical headings; the `helix migrate-headings` advisory
   rewrites existing docs to canonical when invoked (opt-in).
3. **Library-version enforcement.** RESOLVED: hard-fail in CI (via
   `validator_contract_version` mismatch), warn at runtime so dev installs
   are not blocked mid-edit.
4. **`concerns` and `principles` as singleton library types.** RESOLVED for
   v1: library ships shape-only `meta.yml` + how-to-author prompt; methodology
   provides content via `principles_instance` and `concerns_root` in
   `methodology.yml`.
5. **Cross-methodology shared overlays.** Out of scope for v1. Duplicate
   override files between methodologies if needed; revisit if `helix-web`
   emerges and the duplication is non-trivial.
6. **Backward compatibility for direct catalog reads.** RESOLVED: see §12.
7. **DDx beads ↔ graph nodes.** RESOLVED: bead frontmatter gains a
   `graph_node: <methodology-id>:<node-id>` field, optional during the
   transition, required once both methodologies migrate. Resolver translates
   on-disk paths to graph nodes for existing beads. Land the schema
   addition in DDx BEFORE Phase D2 (bench dispatch) so beads created
   post-migration can reference graph nodes deterministically.
8. **Cycle support.** RESOLVED: see §6.1.2. Re-entry edges are typed and
   skipped by the acyclicity check.

---

## 11. References

- Inventory and facet proposals (Phase 1 + Phase 2 outputs)
- `helix/skills/helix/SKILL.md` — current §Catalog Resolution prose
- `helix-infra/skills/helix-infra/SKILL.md` — current §"Where the methodology lives"
- `helix/workflows/activities/*/artifacts/*/meta.yml` — current per-artifact shape
- `helix-infra/workflows/activities/*/artifacts/*/meta.yml` — current IaC shape

---

## 12. Consumer Repo Migration (existing helix users)

Repos that already consume HELIX (`synaptiq-*`, etc.) have two surfaces that
could break under the migration: (a) on-disk document instances, and (b)
tooling/scripts that hardcode template paths.

### 12.1 Document instances are unaffected

Documents on disk (PRDs, ADRs, runbooks) are NOT path-coupled to template
locations. They were written via prompts and validated against `meta.yml` at
authoring time. After migration:

- The validator resolves the same schemas (now via the library), and the
  existing documents continue to pass because library types are supersets
  with aliases (§4.1).
- Newly-required sections enter as warnings for at least one minor cycle
  (§4.5 deprecation window). Existing docs are never bricked.

### 12.2 Tooling that reads template paths directly

Some scripts and editor tooling `cat
workflows/activities/02-design/artifacts/adr/template.md` today. After
migration that path is gone.

**Deprecation shim.** HELIX v1.0 ships
`scripts/legacy_path_shim.py` which:

- Maps every old `workflows/activities/<NN>/artifacts/<slug>/<file>` path
  to the resolved library or local path.
- Logs a deprecation warning (`stderr`) on each hit naming the new path.
- Is invoked by a symlink farm under `workflows/activities/<NN>/artifacts/`
  for one minor cycle (HELIX 1.0.x and 1.1.x).
- Symlinks removed in HELIX 1.2.0. Hard break documented in release notes.

**Migration script.** `scripts/migrate_consumer_repo.py` (shipped in HELIX)
scans a consumer repo for hardcoded old paths in `scripts/`, `Makefile`,
`justfile`, `.github/workflows/`, and emits a report. No rewrite (consumers
own their tooling); just visibility.

### 12.3 Vendored / forked methodologies

Consumer repos that VENDOR (subtree-copied) the old
`workflows/activities/<NN>/artifacts/<slug>/` tree as-is continue to work —
their vendored copy is a snapshot. The migration only affects upstream
HELIX; downstream forks may upgrade at their own pace. The risk register
calls out orphaned forks explicitly.

### 12.4 SKILL.md prose changes

The methodology SKILL.md changes (§7.3) update internal catalog-resolution
prose but do NOT change user-facing slash commands or trigger phrases.
Existing skill invocations (`/helix frame`, "create an ADR", etc.) continue
to work identically.

---

## 13. Open Follow-ups (low-severity / out of scope for v1)

These were surfaced during adversarial review but do not block v1:

- **Phase C effort buffer.** The original ~18h estimate for HELIX migration
  is optimistic. The plan now applies a 50% buffer; Phase C is budgeted at
  ~27h. Re-baselined in the final plan.
- **graph.yml pre-split for HELIX.** HELIX's `graph.yml` is likely to
  exceed 400 lines once all 47 types, cross-cutting nodes, overlays, and
  narrative-bind references land. The plan now pre-splits HELIX's graph
  into `workflows/graph/<activity>.yml` files from day one. Validator
  reads the directory.
- **Cross-methodology shared overlay tree** (`helix-family-overlays`):
  deferred until `helix-web` appears and demonstrates duplication cost.
- **Resolver as a stand-alone CLI** (`helix resolve <type>`): deferred;
  the per-methodology `resolve-library-root.sh` is enough for v1.
- **Performance** (large graphs, many overrides): the validator is
  py3-stdlib and runs in milliseconds at current sizes; revisit if
  HELIX graph exceeds 100 nodes.

