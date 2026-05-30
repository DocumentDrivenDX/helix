---
title: "Databricks Declarative Pipelines (Lakeflow / DLT)"
slug: databricks-declarative-pipelines
generated: true
aliases:
  - /reference/glossary/concerns/databricks-declarative-pipelines
---

**Category:** Data-Pipeline · **Areas:** data, infra

## Description

## Category
data-pipeline

## Areas
data, infra

## Platform

**Platform-specific (Databricks).** Lakeflow Spark Declarative Pipelines (SDP) —
**formerly Delta Live Tables (DLT)** — is Databricks' declarative ETL framework.
It is one component of **Lakeflow** (with **Lakeflow Connect** for ingestion and
**Lakeflow Jobs**, formerly Workflows, for orchestration). Existing DLT code
runs unchanged; the current API names are preferred going forward.

## Boundary

This concern owns **declarative ETL on Databricks** — defining datasets and
transformations and data-quality expectations, and letting the framework manage
the dependency DAG, incremental processing, and quality enforcement. It must not
duplicate its neighbors:

- **Generic data modeling / `domain-driven-design`** owns *what the data means*
  — the logical model the pipeline's datasets realize. This concern owns *how
  the transformation is declared and run*. Do not re-derive the domain model in
  pipeline terms.
- **`enterprise-integration-patterns` (EIP)** owns **asynchronous messaging and
  integration across system boundaries** — channels, routers, idempotent
  receivers, dead-letter handling for message flow. Declarative pipelines own
  **in-pipeline batch/streaming dataset transformation** with a
  framework-managed DAG. They relate at ingestion (a pipeline may read a Kafka/
  Kinesis source), but the **expectation/DAG/incremental** machinery here is not
  EIP's channel/router machinery — name the pipeline pattern; leave cross-system
  messaging to EIP. (A pipeline reading from a broker still respects EIP's
  at-least-once/idempotency reality at the ingestion edge.)
- **`unity-catalog`** *governs* the datasets the pipeline produces (its streaming
  tables and materialized views land in a `catalog.schema`); this concern
  *produces* them. Do not restate the grant model here.
- **`testing` / `verification`** own test strategy and the evidence gate. This
  concern owns the **declarative data-quality expectations** that run as part of
  the pipeline — a complementary, in-pipeline quality control, not a replacement
  for unit/e2e testing.

## Components

A pipeline is a set of **declarative datasets**; the framework builds the
**dependency DAG** from how datasets reference each other, resolves order
automatically, and processes data **incrementally**.

### Datasets — declared, not orchestrated by hand
- **Streaming table** — incrementally processes an append/streaming source.
  Python: `@dp.table` (legacy `@dlt.table`); SQL: `CREATE OR REFRESH STREAMING
  TABLE`.
- **Materialized view** — a transformation kept up to date. Python:
  `@materialized_view` (legacy via `@dlt.table` on a batch query); SQL:
  `CREATE OR REFRESH MATERIALIZED VIEW`.
- **Temporary view** — intermediate, not published. Python: `@temporary_view`
  (legacy `@dlt.view`).
- Python import: `from pyspark import pipelines as dp` (legacy `import dlt`).

### Data-quality expectations — declared on the dataset
Constraints evaluated on each row; three **actions**:
- **warn** (default / retain) — invalid records are **kept** and the violation is
  **reported** in metrics.
  - Python: `@dp.expect("valid_ts", "ts > '2012-01-01'")`
  - SQL: `CONSTRAINT valid_ts EXPECT (ts > '2012-01-01')`
- **drop** — invalid records are **dropped** before write; reported in metrics.
  - Python: `@dp.expect_or_drop("valid_page", "page_id IS NOT NULL")`
  - SQL: `... EXPECT (...) ON VIOLATION DROP ROW`
- **fail** — invalid records **halt the pipeline update**.
  - Python: `@dp.expect_or_fail("valid_count", "count > 0")`
  - SQL: `... EXPECT (...) ON VIOLATION FAIL UPDATE`
- **Grouped**: `@dp.expect_all(dict)`, `@dp.expect_all_or_drop(dict)`,
  `@dp.expect_all_or_fail(dict)`.
- Violations surface in the pipeline's **Data Quality** tab / **event log**
  metrics (warn and drop record metrics; fail halts the run).

### Framework-managed concerns
- **Automatic dependency resolution** and DAG construction from dataset
  references.
- **Incremental processing** for streaming tables; **CDC** via **AUTO CDC /
  `APPLY CHANGES`** for change-data-capture upserts.
- **Automatic lineage** (composes with `unity-catalog`).
- **Development vs production** execution modes (dev: fast iteration / reused
  compute; prod: fresh compute, retries).
- **Unit testing** of transformation logic.

## Constraints

### Declare datasets and transformations; let the framework orchestrate
- Datasets are **declared** (streaming table / materialized view / temporary
  view) and the framework builds the **dependency DAG**, resolves order, and
  processes **incrementally**. Do not hand-roll orchestration, dependency wiring,
  or manual incremental bookkeeping that the framework owns.
- Use the **streaming table** for incremental/append sources and the
  **materialized view** for kept-fresh transformations — chosen deliberately,
  not by defaulting everything to one.

### Every dataset declares data-quality expectations
- Each published dataset declares **expectations** with the **action chosen to
  match intent**: **warn** to observe-and-keep, **drop** to quarantine bad rows
  from the target, **fail** to halt on a violation that must never pass. A
  published dataset with **no** expectations is a quality gap.
- **fail** is for invariants that must never reach downstream; **drop** for rows
  that should not pollute the target but should not stop the pipeline; **warn**
  for observe-only. Reserve **fail** for genuine must-not-pass invariants (it
  halts the run).

### CDC uses the framework's change-apply, not hand-rolled merges
- Change-data-capture upserts use **AUTO CDC / `APPLY CHANGES`**, not a
  hand-written merge that re-implements the framework's CDC handling.

### Datasets land in Unity Catalog
- The pipeline's published tables/views land in a governed `catalog.schema` and
  are governed by **`unity-catalog`** (grants, ownership, lineage). Do not write
  to ungoverned/legacy locations.

### Dev vs prod modes are distinct
- Use **development** mode for iteration and **production** mode for scheduled
  runs (fresh compute, retries) — do not ship dev-mode shortcuts to production.

## Drift Signals (anti-patterns to reject in review)

- Hand-rolled orchestration / dependency wiring / manual incremental bookkeeping
  that the framework manages → declare datasets and let SDP build the DAG and
  process incrementally
- A **published dataset with no expectations** → declare expectations; choose
  warn/drop/fail to match the data-quality intent
- **fail** used where a row should merely be dropped (needlessly halting the
  pipeline), or **warn** used where a bad row must never reach downstream → match
  the action to intent
- A hand-written CDC merge re-implementing change handling → use **AUTO CDC /
  `APPLY CHANGES`**
- Pipeline output written to an **ungoverned/legacy location** instead of a
  Unity Catalog `catalog.schema` → publish into the governed namespace
- **Dev-mode** behavior (reused compute, skipped retries) shipped to production →
  run scheduled pipelines in production mode
- Expectations treated as a **substitute for unit/e2e testing** → expectations
  are in-pipeline data-quality control; compose with `testing`/`verification`

## When to use

A product that runs **ETL on the Databricks lakehouse as declarative pipelines**
— ingest + transform into streaming tables and materialized views with
data-quality expectations, letting the framework own orchestration and
incremental processing. This is the data-pipeline member of the Databricks
family; select it together with **`unity-catalog`** (which governs the datasets
it produces) and, when the product is a Databricks-hosted app reading those
datasets, **`databricks-apps`**. It is composable (no slot); `areas: data, infra`
scopes its practices to the data and pipeline/infra work items.

Do **not** select it for ETL that does not run on Databricks, or for a thin
app with no pipeline — use the generic data-modeling / EIP concerns there, and
relate (do not duplicate) them here.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: dataset shape (streaming-table vs materialized-view), expectation policy (warn/drop/fail), CDC strategy
- TD: declarative datasets + framework-managed DAG/incremental; AUTO CDC / APPLY CHANGES; dev vs prod modes
- DATA_DESIGN: published streaming tables/materialized views landing in a governed catalog.schema
- TEST_PLAN: per-dataset data-quality expectations + transformation-logic unit tests

## ADR References

Record an ADR for the pipeline's dataset shape (streaming-table vs
materialized-view boundaries), the data-quality expectation policy
(warn/drop/fail per dataset), and the CDC strategy (`APPLY CHANGES`). A material
uncertainty (source-system semantics, ingestion volume, CDC ordering) is a
`tech-spike`, not a silent assumption (see
`workflows/references/concern-resolution.md`).

## Practices by activity

Agents working in any of these activities inherit the practices below via the bead's context digest.

These practices govern **declarative ETL on Databricks** — declaring datasets,
transformations, and data-quality expectations and letting the framework manage
orchestration and incremental processing. They do not restate the logical data
model (`domain-driven-design`), the grant model (`unity-catalog`), or
cross-system messaging (`enterprise-integration-patterns`) — see the boundary in
`concern.md`.

## Requirements (Frame activity)

- Confirm ETL runs **on Databricks as declarative pipelines** (Lakeflow / SDP,
  formerly DLT).
- Identify the **sources** (cloud storage, Kafka/Kinesis/etc.) and the
  **published datasets** the product needs, plus the data-quality invariants per
  dataset.

## Design

- Decide each dataset's shape: **streaming table** (incremental/append source)
  vs **materialized view** (kept-fresh transformation) vs **temporary view**
  (intermediate, unpublished).
- Design the **data-quality expectation policy** per dataset, choosing
  warn/drop/fail to match intent (observe-and-keep / quarantine / must-not-pass).
- Design **CDC** via **AUTO CDC / `APPLY CHANGES`** where upserts from a change
  feed are needed — not a hand-rolled merge.
- Target the pipeline output at a governed **Unity Catalog `catalog.schema`**.

## Implementation

- Import `from pyspark import pipelines as dp` (legacy `import dlt` still runs).
- Declare datasets with `@dp.table` (streaming table) / `@materialized_view` /
  `@temporary_view`, or the SQL `CREATE OR REFRESH STREAMING TABLE` /
  `MATERIALIZED VIEW` — let the framework build the dependency DAG and process
  incrementally. Do not hand-roll orchestration or incremental bookkeeping.
- Declare **expectations** on each published dataset:
  - warn: `@dp.expect("name", "predicate")` / `CONSTRAINT ... EXPECT (...)`
  - drop: `@dp.expect_or_drop(...)` / `... ON VIOLATION DROP ROW`
  - fail: `@dp.expect_or_fail(...)` / `... ON VIOLATION FAIL UPDATE`
  - grouped: `@dp.expect_all` / `expect_all_or_drop` / `expect_all_or_fail`
- Use **AUTO CDC / `APPLY CHANGES`** for change-data-capture upserts.
- Run scheduled pipelines in **production** mode (fresh compute, retries); use
  **development** mode only for iteration.

## Testing / Verification

- **Unit-test** the transformation logic (the framework supports this).
- Verify expectations behave: feed a row that violates a **drop** expectation
  and confirm it is **dropped** from the target (and counted in metrics); feed a
  row that violates a **fail** expectation and confirm the update **halts** —
  observed in the Data Quality tab / event log, not assumed.
- Verify the published datasets land in the governed **Unity Catalog
  `catalog.schema`** and lineage is captured.

## Boundary with neighbors

See `concern.md` for the canonical Boundary (vs domain modeling,
`enterprise-integration-patterns`, `unity-catalog`, `testing` /
`verification`). Composition in the Databricks family: this concern produces
the data; `unity-catalog` governs it; `databricks-apps` hosts apps that
consume it — each owns its piece, none restates the others.

## Quality Gates

- ETL is expressed as **declarative datasets** (streaming tables / materialized
  views) with the framework owning the **dependency DAG** and **incremental
  processing** — no hand-rolled orchestration.
- **Every published dataset declares data-quality expectations**, with the
  action (warn/drop/fail) chosen to match intent; **fail** is reserved for
  must-not-pass invariants.
- A **drop** expectation is verified to drop violating rows from the target (with
  metrics), and a **fail** expectation is verified to halt the update — observed
  in the event log / Data Quality tab.
- CDC upserts use **AUTO CDC / `APPLY CHANGES`**, not a hand-written merge.
- Published datasets land in a governed **Unity Catalog `catalog.schema`** (not a
  legacy/ungoverned location); scheduled runs use **production** mode.
