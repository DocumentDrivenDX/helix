---
title: "Plan: Fold DataHelix templates into the HELIX catalog"
slug: plan-2026-05-17-fold-datahelix-templates
weight: 520
activity: "Design"
source: "02-design/plan-2026-05-17-fold-datahelix-templates.md"
generated: true
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

> **Source identity** (from `02-design/plan-2026-05-17-fold-datahelix-templates.md`):

```yaml
ddx:
  id: plan.fold-datahelix-templates
  status: draft
```

# Plan: Fold DataHelix templates into the HELIX catalog

**Date:** 2026-05-17
**Status:** Draft, awaiting maintainer decision on naming + scope
**Source:** `.local/workspace-rescue/datahelix-2026-05-17/templates/` — three
data-engineering-specific templates rescued from the operator's pre-collapse
DataHelix workspace project before deleting that workspace folder (which was
biasing Genie Code path lookups).
**Out of scope:** the rescued `skills/datahelix-{input,frame,design,build}.md`
files. Those are pre-umbrella skill duplicates and stay deleted — the HELIX
umbrella covers their behaviour.

## Goal

Adopt three data-engineering-specific artifact templates as first-class
HELIX artifact types so a team running HELIX on a Databricks data
project can frame, design, and define quality for a data product
without leaving the catalog.

## What's being folded

Three templates, each currently at
`.local/workspace-rescue/datahelix-2026-05-17/templates/<name>.md`:

| Template (DataHelix) | Proposed HELIX home | Sibling of |
|---|---|---|
| `data-product-requirements.md` | `workflows/activities/01-frame/artifacts/data-prd/` | `prd`, `feature-specification` |
| `data-architecture-design.md` | `workflows/activities/02-design/artifacts/data-architecture/` | `architecture`, `data-design` |
| `data-quality-expectations.md` | `workflows/activities/03-test/artifacts/data-quality-expectations/` | `test-plan`, `test-suites` |

Sizes are template-only — each is a markdown skeleton with TODO placeholders,
no real content to migrate.

## Why these are new types (not edits to existing ones)

- **`data-prd` vs general `prd`** — Same spine (Summary, Problem and Goals,
  P0/P1/P2). Different shape on consumers (Data Consumers table replaces
  Persona narratives), and three sections the general PRD doesn't cover:
  Data Sources table, Data Quality Requirements table, Databricks-specific
  Technical Context (catalog/schema, medallion layer, pipeline type).
  Folding into general PRD would either bloat it for non-data projects or
  hide data-specific structure behind optional sections.
- **`data-architecture` vs existing `data-design`** — Different abstractions.
  `data-design` is about the **data model** (entities, relations, access
  patterns, migration). `data-architecture` is about the **data pipeline
  architecture** (medallion topology, streaming vs batch, processing
  semantics, governance). The two should coexist: `data-architecture`
  references `data-design`.
- **`data-quality-expectations` is new** — No existing 03-test type covers
  "quality contracts written before implementation as testable predicates on
  data shape". Test-plan is the test strategy; test-suites is test code
  organisation; test-procedures is how to run tests. Data quality
  expectations are the *contract* the implementation must satisfy.

## Naming decisions to resolve

| Question | Options | Recommendation |
|---|---|---|
| Should `data-prd` be a sibling type or a variant of `prd`? | (a) sibling type at `01-frame/artifacts/data-prd/` (b) variant subdirectory at `01-frame/artifacts/prd/variants/data/` | **(a) sibling type.** HELIX's catalog model doesn't currently support type variants. Adding variants now adds machinery for a single instance. |
| `data-prd` or `data-product-requirements`? | (a) abbreviated `data-prd` matches general `prd` (b) full `data-product-requirements` matches the verbose `feature-specification`, `data-quality-expectations` | **(a) `data-prd`.** Matches the precedent set by `prd`. |
| `data-architecture` or `data-architecture-design`? | (a) `data-architecture` matches general `architecture` (b) `data-architecture-design` matches the DataHelix file | **(a) `data-architecture`.** Catalog parent dir is artifact-type name; design/template/prompt are role files inside. The `-design` suffix is redundant. |
| `data-quality-expectations` or `data-quality-contract` or `data-expectations`? | full vs abbreviated names | **`data-quality-expectations`.** Matches Databricks/SDP terminology (`EXPECT` clauses); shorter alternatives lose specificity. |

If you disagree with any of the recommendations above, name the alternative
before Phase B and I'll adjust the rest of the plan.

## Open question: domain-specific catalog vs general-purpose HELIX

HELIX positions itself as "the catalog covers software development from
intent through deployment" (PRD §Goals R-1). Adding three data-engineering
types weighs that positioning toward Databricks/data. Two ways to handle:

1. **Adopt as first-class types.** Three new entries in the catalog
   table, indexed in the §Catalog Resolution inline table. Honest
   acknowledgement that HELIX-for-data is a real adoption shape.
2. **Adopt as data-specialised types in a subnamespace.** New activity
   subdirectories like `01-frame/artifacts/specialized/data-prd/`.
   Keeps the top-level catalog general; signals these are domain
   extensions.

Recommendation: **(1) first-class.** The catalog already has
`security-tests` and `compliance-requirements` as domain-specific types
that nobody objects to. Data-engineering deserves the same treatment.
The naming (`data-` prefix) makes the specialisation obvious without a
separate namespace.

## Phases of work

### Phase A — Decisions

- Maintainer confirms naming choices (this doc + AskUserQuestion)
- Maintainer confirms first-class adoption vs subnamespace
- This phase is one review pass, not implementation

**Deliverable:** decisions captured at the bottom of this plan doc.

### Phase B — Author meta.yml per type

Each new artifact-type directory needs a `meta.yml` matching
`workflows/artifact-schema.md`. The required fields:

- `artifact:` block (name, id, type, activity, optional level)
- `description:`
- `output:` (location, format, naming, examples)
- `validation:` (required_sections, quality_checks; deterministic
  `automated_checks` where possible — see STP-014-A on the catalog's
  R-8 prose-vs-automated split)
- `prompts:` (generation, review)
- `template:` (file, sections)
- `examples:` (file, description)
- `relationships:` (informed_by, informs, referenced_by)
- `references:` (data-platform standards — Databricks SDP docs, Delta
  best-practices, dbt schema-test conventions, etc.)
- `workflow:` (creation_order, approval_required, approvers)
- `tags`, `version`, `last_updated`

For `data-prd`: `informed_by: [product-vision, ...]`, `informs:
[data-architecture, feature-specification, user-stories]`.
For `data-architecture`: `informed_by: [data-prd, prd, ...]`,
`informs: [data-design, data-quality-expectations,
technical-design]`.
For `data-quality-expectations`: `informed_by: [data-prd,
data-architecture]`, `informs: [test-plan, story-test-plan,
implementation-plan]`.

**Deliverable:** three `meta.yml` files staged under
`workflows/activities/{01-frame,02-design,03-test}/artifacts/...`.

### Phase C — Adapt template.md per type

Source templates are already well-shaped. Adaptations:

- Add `ddx: { id: <type-name> }` frontmatter so they match the catalog
  convention.
- Replace path-hardcoded references (`docs/01-frame/prd.md`) with
  HELIX-style placeholders that match the resolved catalog paths.
- Light editing for HELIX voice (terse, declarative, no Markdown
  emoji).
- Keep the Review Checklists at the bottom — these align with the
  `quality_checks` field in `meta.yml` and could become deterministic
  `automated_checks` in a follow-up.

**Deliverable:** three `template.md` files committed.

### Phase D — Author prompt.md per type

Each type needs a generation prompt that guides an agent to author an
instance. Pattern matches existing types like `prd/prompt.md` or
`architecture/prompt.md`:

- Reference anchors (Databricks documentation, Delta best practices)
- Focus (what the prompt enforces)
- Role boundary (what this artifact is NOT)
- Completion criteria

Specific anchors:

- `data-prd`: Databricks UC, Delta, SDP docs; medallion-architecture
  best practices.
- `data-architecture`: Databricks Lakehouse architecture, SDP
  conventions, Auto Loader / Streaming Tables documentation.
- `data-quality-expectations`: Databricks SDP expectations (`EXPECT
  ... ON VIOLATION ...`), dbt tests, Great Expectations vocabulary.

**Deliverable:** three `prompt.md` files committed.

### Phase E — Author example.md per type

Each type needs a worked example. Realistic, not toy. Suggested
domain: a customer-360 pipeline pulling from Salesforce and Stripe
into a Databricks Lakehouse with Bronze/Silver/Gold layers. (This
also seeds the `recipe-app` fixture for STP-014 Scenario 5 — pun aside,
"customer-360" is a more realistic enterprise fixture than a recipe
app for a data-engineering workflow.)

**Deliverable:** three `example.md` files committed, plus an updated
`tests/workflows/fixtures/` decision: extend `recipe-app` or add a
parallel `customer-360-data` fixture for data-engineering scenarios.

### Phase F — Update relationship documentation

- `workflows/artifact-hierarchy.md` — add the new types to the
  dependency graph (data-prd is below prd in the authority hierarchy;
  data-architecture is below architecture; data-quality-expectations
  sits between data-architecture and implementation-plan).
- `workflows/REFERENCE.md` (or whichever doc is the canonical catalog
  index) — list the new types.
- `docs/install/` per-runtime guides — no changes needed; runtimes
  discover types from filesystem scan.

**Deliverable:** updated hierarchy + reference docs.

### Phase G — Update SKILL.md §Catalog Resolution inline table

The inline table in `skills/helix/SKILL.md` enumerates types per
activity. After Phase B–F lands, add the three new types to the
table:

- `01-frame` row gains `data-prd`
- `02-design` row gains `data-architecture`
- `03-test` row gains `data-quality-expectations`

This is what lets Genie answer "list artifact types under 01-frame"
from the loaded SKILL.md without filesystem traversal. Without this
edit the new types exist on disk but Genie can't enumerate them.

**Deliverable:** SKILL.md edit, bundle rebuild, workspace re-upload,
re-run of the Genie e2e to confirm the three new types appear in
prompt-2's response.

### Phase H — Test against Genie + the other runtimes

Run the existing `tests/install/` smoke checks; verify SKILL.md still
parses, frontmatter intact, all activity dirs present.

Run the Genie e2e once more — prompt 2 should now name all 19 types
under `01-frame` (16 existing + 3 new data types, or 16 existing if
data-prd is the only 01-frame addition), and prompt 3 (smoke
alignment) should still execute the §Align contract.

**Deliverable:** updated `tests/install/genie/recordings/` entry +
metadata sidecar confirming the new types are reachable.

### Phase I — Tag release

Cut `v0.5.0` (minor bump — new artifact types are user-visible scope
additions). Publishes the bundle including the three new types so any
adopter can `genie-install` and get them.

**Deliverable:** git tag `v0.5.0`; GitHub release with bundle +
installer assets.

## Suggested bead set

Following the FEAT-013 / FEAT-014 pattern, this work fits comfortably
as one feature with a focused bead set. Proposed beads (1 epic + ~9
children):

| ID (proposed) | Phase | Title |
|---|---|---|
| epic | — | Epic: Fold DataHelix data templates into HELIX catalog (FEAT-015) |
| B1 | B | Author meta.yml for data-prd, data-architecture, data-quality-expectations |
| B2 | C | Adapt template.md for the three new types |
| B3 | D | Author prompt.md for each (with Databricks/SDP reference anchors) |
| B4 | E | Author example.md (customer-360 worked example) |
| B5 | F | Update workflows/artifact-hierarchy.md + REFERENCE.md |
| B6 | G | Update SKILL.md §Catalog Resolution inline table to include the 3 new types |
| B7 | H | Rebuild bundle + re-upload + Genie e2e verifies 3 new types reachable |
| B8 | I | Tag v0.5.0 release |
| B9 | — | (Optional) Author FEAT-015 spec to document this scope addition |

B9 is optional because the change is small enough to land via the
beads alone with this plan as the design doc.

## Risks and decisions deferred

1. **Data-architecture vs solution-design overlap.** A data-pipeline
   architecture is *one specific kind* of solution design. Should
   `data-architecture` declare itself a variant of `solution-design`
   via `informed_by` or a new `extends:` field, or stay parallel?
   Defer; revisit if a second domain (ML, security, etc.) shows up
   asking for the same shape.
2. **R-8 deterministic checks.** STP-014-A flagged that 66% of artifact
   types lack `automated_checks` in `meta.yml`. The data templates'
   Review Checklists are good candidates for deterministic translation
   (e.g. "all P0 requirements have at least one expectation" → a grep
   pattern across the data-quality-expectations doc). Either ship the
   prose-only first version (matches catalog precedent) or invest in
   automated_checks during Phase B (raises the bar for the whole
   catalog). Recommendation: prose-first; promote to automated later.
3. **Databricks-specific vs generic-data-platform terms.** The
   templates lean Databricks (UC, SDP, EXPECT clauses, DBU). HELIX is
   runtime-neutral methodology. Two ways:
   (a) keep Databricks-specific in prompt/template; note in §Role
   Boundary that adopters on other platforms (Snowflake, BigQuery,
   on-prem) should substitute their platform's equivalents.
   (b) genericise the templates to "data platform" language;
   Databricks specifics go in the example.md.
   Recommendation: (a) — the templates are already authored around
   Databricks; genericising would dilute them. The example.md is the
   Databricks-flavoured worked example; an adopter can substitute.

## Decision log (resolved 2026-05-17)

- Naming: `data-prd` / `data-architecture` / `data-quality-expectations` — **approved.**
- Catalog placement: **first-class types**, indexed in the existing
  `01-frame` / `02-design` / `03-test` activity directories alongside
  `prd`, `architecture`, `data-design`, `test-plan`, etc. No
  `specialized/` subnamespace.
- Platform scope: **keep Databricks-specific.** Templates name UC
  catalogs, SDP `EXPECT` clauses, DBU budgets. Adopters on Snowflake /
  BigQuery / on-prem substitute the equivalents on their platform; the
  §Role Boundary in each prompt documents the substitution explicitly.
- FEAT-015 spec document: **skip.** This plan is the design; the bead
  set listed under §Suggested bead set is the implementation path.
  Plan doc + beads is enough for a three-template addition.

## See also

- `.local/workspace-rescue/datahelix-2026-05-17/` — rescued source
- `workflows/artifact-schema.md` — meta.yml schema
- `workflows/activities/02-design/artifacts/data-design/` — adjacent
  existing type
- `docs/helix/03-test/test-plans/STP-014-appendix-real-world-patterns.md`
  §Patterns NOT covered — notes catalog R-8 gap and recommends
  prose-first
