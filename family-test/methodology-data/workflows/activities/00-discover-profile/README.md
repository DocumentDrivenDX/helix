# 00-discover-profile

Purpose: identify the data product, profile source schemas + freshness +
PII, enumerate consumers, define SLAs. Acquires source truth BEFORE
declaring intent.

Inputs: a product PRD or business request that hints a data product is
needed. May be empty (greenfield data-product brief).

Outputs:
- `data-product-brief` (exit-gate artifact): problem, consumers,
  data_sources, freshness_sla, success_metrics, non_consumers,
  open_questions.
- `source-profile` per upstream system: schema_snapshot, volume,
  observed freshness, pii_classification, producers_contacted, risks.
- `consumer-inventory`: per-consumer purpose, read_pattern,
  freshness_required, contract_version, dependency_strength.

Exit gate: `discover-validation` — every required edge per `graph.yml`
is satisfied (consumer-inventory exists before any 01-contract draft),
every section per the type's `library:*.required_sections` is present.

Concerns: source-side PII exposure (profile MUST classify), late-arrival
handling intent (recorded in brief, made concrete in 02-design),
producer agreement (producers_contacted is non-optional).
