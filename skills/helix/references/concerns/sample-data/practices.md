# Practices: Sample Data

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
