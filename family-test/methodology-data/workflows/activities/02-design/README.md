# 02-design

Purpose: topology, medallion layers (Bronze/Silver/Gold),
transformations, storage, idempotency, partitioning, late-arrival
handling. ADRs capture the option-space tradeoffs.

Inputs: `data-contract` (informs, required), `governance-classification`
(informs), prior ADRs.

Outputs:
- `data-architecture` (exit-gate): topology, medallion layers, storage,
  partitioning, idempotency, late-arrival handling.
- `data-design`: detailed transformation specs, schemas per layer.
- `adr` instances for cross-cutting design choices (e.g. Glue vs Spark,
  CDC vs snapshot, streaming vs batch).

Exit gate: `design-validation` — architecture covers every contract's
gold-tier surface; design names idempotency strategy and a late-arrival
policy; every cross-cutting design decision has an ADR (or an explicit
"deferred to evolve" note).

Concerns: idempotency is mandatory (downstream tests assume it);
late-arrival handling is mandatory (silent data loss otherwise);
medallion layer boundaries match the contract's evolution policy
(non-breaking changes stay within a layer).
