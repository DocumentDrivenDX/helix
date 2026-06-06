# 04-build

Purpose: pipeline code, orchestration, lineage instrumentation,
implementation plan. The implementation plan is the gate that turns
contracts + design + tests into shipped pipeline code.

Inputs: `data-quality-tests` (informs, required), `data-design`
(informs, required), `data-architecture` (informs for lineage-spec).

Outputs:
- `implementation-plan` (exit-gate): build sequence, orchestrator
  choice (Airflow / dbt / DLT / Glue / Beam / Flink / custom), task
  topology, dependency graph, deployment strategy.
- `lineage-spec`: emitter_strategy (OpenLineage / dbt-style / custom),
  nodes_to_emit, consumer_of_lineage (Marquez / DataHub / custom).

Exit gate: `build-validation` — the implementation plan compiles
against the design (every Silver/Gold node in the design appears as a
task in the plan); lineage-spec emitter is chosen (or explicitly
deferred); pipeline code exists for every contract.

Concerns: orchestrator-specific idioms must NOT leak into the design
(design is orchestrator-agnostic; the plan binds it); lineage must
emit at the contract boundary (not just internally).
