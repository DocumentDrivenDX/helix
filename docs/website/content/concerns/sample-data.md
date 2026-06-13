---
title: "Sample Data"
slug: sample-data
generated: true
aliases:
  - /reference/glossary/concerns/sample-data
---

**Category:** Quality Attributes · **Areas:** data

## Description

## Category
quality-attribute

## Areas
data

## Boundary

This concern owns **governed app seed/demo data** — the data a data-backed
product ships with so it feels real and exercises its UI states. It is distinct
from `testing`, and the two must not blur:

- **`testing`** owns test fixtures, factories, mocks, isolation, and
  assertion-specific data — the throwaway data a single test constructs to
  exercise one behavior and then tears down. (Its "fake data over fixtures"
  practice governs *test* data.)
- **`sample-data`** owns the **seed/demo dataset** the running product is
  populated with — the rows a reviewer, a demo, or a screenshot actually sees.
  Its job is to make a data-backed product feel real and to drive every UI
  state (empty, full, long, overflowing, boundary, every status/enum variant).

"e2e runs against realistic data" is not this concern collapsing into `testing`:
`sample-data` produces the governed seed the running system loads; `testing`
decides what a test asserts. Keep them separate.

## Components

- **Semantic fake-data library** — a semantically-aware generator (names,
  emails, addresses, prices, dates, lorem) as a **tech-stack-specific named
  default**, following the active runtime concern:
  - `typescript-bun` → **`@faker-js/faker`**
  - `python-uv` → **`Faker`**
  - `rust-cargo` → **`fake`**
  - other stacks → the idiomatic semantic faker for that runtime

  This is the default tool, **not** the determinism mechanism (see Constraints).
- **Seed script** — a governed, idempotent, re-runnable deliverable that
  populates the running product's datastore with the generated dataset.
- **Curated edge-case records** — literal rows inside the seed script that
  guarantee specific boundary cases the generator would otherwise hit only by
  chance.

## Constraints

### Determinism comes from the seed, not the library

- Determinism is produced by an **explicit seed** passed to the faker, a
  **stable locale/config**, a **pinned dependency version**, and a
  **deterministic generation order** — not by the choice of library. Re-running
  the seed script with the same seed must produce the same dataset.
- Record or print the seed so a dataset can be reproduced exactly.

### Generate varied shapes and schema-relevant edge cases

- Generate **varied** data — not N copies of one row. Vary string lengths,
  optional-field presence, value ranges, and timestamps.
- Cover **schema/domain-relevant edge cases** so every UI state renders:
  **empty** (zero rows / empty collections), **long** (long strings, long
  lists), **large** (big numbers, large counts), **boundary** (min/max,
  just-over/just-under limits), and **all status/enum variants**.
- Edge cases are **bounded by default, not invalid-by-reflex** — generate the
  realistic boundaries the schema and domain allow, not malformed data the
  product is not required to accept.

### The seed script is a governed deliverable

- The seed script is a **first-class, idempotent/re-runnable** deliverable, not
  an afterthought. Re-running it converges to the same governed dataset rather
  than duplicating rows.
- **Guardrails**:
  - Set an **explicit faker seed** for reproducibility.
  - Use **clearly synthetic, non-PII** values — never real or realistic
    personal data.
  - **Never execute against, or mix with, production** data or a production
    datastore. Seed only non-production environments.
- Avoid **thin, ad-hoc, hardcoded-only** data (a couple of uniform rows). But
  **curated literal edge-case records inside the governed seed script are
  encouraged** — they are often the clearest way to guarantee a specific
  boundary case exists.

## Drift Signals (anti-patterns to reject in review)

- A couple of thin, hardcoded, uniform rows as the only seed data → generate a
  varied dataset via the semantic faker plus curated edge-case records
- No semantic faker dependency for a data-backed product → add the tech stack's
  named default (`@faker-js/faker`, `Faker`, `fake`, …)
- Seed data with no edge cases (no empty / long / large / boundary / all-status
  coverage) → add schema-relevant edge cases so every UI state renders
- Nondeterministic seed generation (no explicit seed, unstable locale, unpinned
  faker version, unordered generation) → make it reproducible
- Real or realistic PII in sample data → replace with clearly synthetic values
- A seed script that can run against / mix with production → restrict it to
  non-production environments

## When to use

Any **data-backed product** — one whose value shows through data it stores and
renders. High autonomy auto-selects this concern for data-backed products (see
`workflows/references/concern-resolution.md`); `areas: data`
scopes its practices to data-layer work items. Compose with the tech-stack concern
(which fixes the faker library) and with UX concerns (the varied data is what
exercises the empty/overflow/large-number states the UI must handle).

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- DATA_DESIGN: governed seed/demo dataset covering empty/long/large/boundary + all status-enum UI states
- IMPLEMENTATION_PLAN: idempotent re-runnable seed script with explicit faker seed; non-PII, non-production only

## ADR References

## Practices by activity

Agents working in any of these activities inherit the practices below through runtime work context, such as a DDx bead context digest.

These practices govern the **app seed/demo dataset** a data-backed product ships
with — the data that makes it feel real and drives every UI state. They do not
govern test data: `testing` owns fixtures, factories, and assertion-specific
data (see the boundary in `concern.md`).

## Frame

- Use the **semantic fake-data library** that is the named default for the
  active runtime concern:
  - `typescript-bun` → `@faker-js/faker`
  - `python-uv` → `Faker`
  - `rust-cargo` → `fake`
  - other stacks → the idiomatic semantic faker for that runtime
- Add it as a project dependency at a **pinned version**. The library is the
  default generator, not the source of determinism.

## Design

Determinism comes from how the generator is driven, not from which one:

- Pass an **explicit seed** to the faker at the top of the seed script.
- Fix a **stable locale/config** so generated values do not shift with the
  environment.
- **Pin the faker version** so an upgrade cannot silently change the dataset.
- Generate in a **deterministic order** — no reliance on map/set iteration
  order or wall-clock time.
- Record/print the seed so any dataset can be reproduced exactly.
- Produce **varied** rows — vary string lengths, optional-field presence, value
  ranges, and timestamps. Never N copies of one row.
- Cover the **schema/domain-relevant edge cases** so every UI state renders:
  - **empty** — zero rows / empty collections (the empty-state UI)
  - **long** — long strings, long lists (overflow / truncation UI)
  - **large** — big numbers, large counts (formatting / pagination UI)
  - **boundary** — min/max and just-over/just-under schema limits
  - **all status/enum variants** — one record per status so every badge/branch
    renders
- Keep edge cases **bounded** — realistic extremes the schema and domain allow,
  not malformed data the product need not accept.

## Build

- The seed script is **idempotent and re-runnable**: running it again converges
  to the same governed dataset rather than appending duplicates.
- Guardrails:
  - **Explicit faker seed** — reproducible runs.
  - **Clearly synthetic, non-PII values** — never real or realistic personal
    data.
  - **Never against / mixed with production** — seed only non-production
    environments; the script must refuse a production target.
- Prefer the faker for bulk variety; add **curated literal edge-case records**
  inside the same governed script for boundary cases you must guarantee. Avoid
  thin hardcoded-only data as the *whole* dataset.

## Test

- A semantic faker library is a pinned dependency for the data-backed product.
- A governed, idempotent seed script exists and populates the running product.
- The seed dataset is varied and covers empty / long / large / boundary /
  all-status edge cases (verifiable by row-count + variety in the seeded store).
- Generation is deterministic: explicit seed, stable locale, pinned version,
  ordered generation.
- Sample data is clearly synthetic (no PII) and the seed never targets
  production.

## Cross-cutting

### Boundary with testing

- `sample-data` populates the **running product**; `testing` constructs
  throwaway data for a single assertion. Do not seed the app from test fixtures,
  and do not assert product behavior against the demo seed instead of
  purpose-built test data.
