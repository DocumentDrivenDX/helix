# Practices: Databricks Declarative Pipelines (Lakeflow / DLT)

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
