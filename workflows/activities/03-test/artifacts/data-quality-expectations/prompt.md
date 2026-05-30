# Data Quality Expectations Generation Prompt

Define the quality contracts that the data pipeline must satisfy, written as
testable predicates on data shape, completeness, accuracy, and freshness.

## Purpose

Data Quality Expectations is the **contract layer between PRD (kind: data) (what quality
is needed) and implementation** (how to verify it). Its unique job is to define
measurable quality assertions as executable tests: data should not be released
to consumers until these contracts are satisfied.

Unlike Test Plan (which is the overall test strategy) or Test Suites (which is
test code organization), Data Quality Expectations are the *quality commitments*
written in a machine-readable form before code is written.

## Reference Anchors

Use these local resource summaries as grounding:

- `docs/resources/databricks-sdp-expect.md` grounds Databricks Semantic Data
  Platform `EXPECT ... ON VIOLATION ...` syntax for inline quality assertions
  and contract-driven pipeline composition.
- `docs/resources/dbt-tests.md` grounds dbt's assertion language (tests,
  contracts, and constraints) for data quality as code.
- `docs/resources/great-expectations.md` grounds Great Expectations vocabulary,
  expectations, suites, and checkpoints for flexible, reusable quality checks.

## Focus

- For each requirement in the PRD (kind: data), write at least one testable expectation.
- Group expectations by layer (Bronze, Silver, Gold) and validate at the
  appropriate layer.
- Use SDP `EXPECT` syntax for Databricks Streaming Tables, dbt tests for
  transformed tables, and Great Expectations for custom or complex checks.
- Name what happens when expectations fail: quarantine the data, alert,
  rollback, or skip dependent pipelines.
- Document freshness SLAs and how they are monitored (timestamp columns,
  row-count trends, lag detection).

## Role Boundary

Data Quality Expectations are not implementation code, not test infrastructure,
and not the data model. They are the *contract* that implementation must satisfy.

**Databricks Platform Substitution:** If you are adopting this on another data
platform, substitute as follows:

| Databricks Concept | Snowflake Equivalent | BigQuery Equivalent | On-Prem / Other |
|---|---|---|---|
| SDP `EXPECT ... ON VIOLATION ...` | Data Quality Checks + Task error handling | BigQuery Data Quality API + assertions | dbt tests, Great Expectations, SQL assertions |
| Streaming Tables with built-in `EXPECT` | Stream-triggered materialized views + constraints | Dataflow with Beam assertions | Flink-based pipelines with custom state |
| SDP Genie for test generation | dbt auto-generate tests from table samples | BigQuery Data Catalog insights | dbt, custom metadata scanning |
| Databricks Lakeview dashboards for monitoring | Snowflake Dashboards | Looker, Data Studio | Grafana, custom dashboards |

## Completion Criteria

- Every P0 requirement from PRD (kind: data) has at least one corresponding expectation.
- Expectations are grouped by layer (Bronze input validation, Silver
  transformation contracts, Gold business rule verification).
- Expectations are written in the platform's native syntax (SDP `EXPECT`,
  dbt test, Great Expectations).
- Each expectation names the failure mode: what happens if the check fails
  (quarantine, alert, skip downstream, rollback).
- Freshness SLAs are explicit: expected refresh interval and how lag is
  detected.
- Quality dashboards or monitoring strategy is sketched (where operators watch,
  what metrics matter, alert thresholds).
- Expectations are prioritized (which checks must pass for release, which are
  advisory).
