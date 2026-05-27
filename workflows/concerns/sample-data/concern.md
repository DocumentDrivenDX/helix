# Concern: Sample Data

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
