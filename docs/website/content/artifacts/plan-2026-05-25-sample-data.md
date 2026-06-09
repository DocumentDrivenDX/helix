---
title: "Plan — sample-data concern (semantic faker, varied shapes) (2026-05-25)"
slug: plan-2026-05-25-sample-data
weight: 590
activity: "Design"
source: "02-design/plan-2026-05-25-sample-data.md"
generated: true
---
# Plan — sample-data concern (semantic faker, varied shapes) (2026-05-25)

## Context

Operator, inspecting the live demo apps: they ship **thin, uniform seed data** (a couple hardcoded rows), so
they feel hollow and never exercise the UI's empty / long-list / large-number / boundary states. Sample-data
generation should be a **first-class HELIX concern** using a semantically-aware library, not an
implementation detail left to chance.

Scope-disciplined: one new composable concern + concern-resolution selection + one FEAT note. No slot (the
faker library is a named default in practices, like other tech-stack-bound tool choices).

## Changes

- **D1 — `sample-data` concern (composable; areas: `data`; composes with the tech-stack concern).** Owns
  **governed app seed/demo data** that makes data-backed products feel real and exercise UI states. **Boundary**
  (codex fix 1): `testing` owns test fixtures/factories/mocks/isolation/assertion-specific data; `sample-data`
  owns app seed/demo data — keep them distinct (don't blur into "e2e runs against realistic data"). Practices:
  use a **semantically-aware fake-data library** as a **tech-stack-specific named default** (`typescript-bun`
  → **`@faker-js/faker`**; `python-uv` → `Faker`; etc.) — this is a default, **not** the determinism mechanism
  (codex fix 2): determinism comes from an **explicit seed**, stable locale/config, pinned dependency version,
  and deterministic generation order. Generate **varied shapes** + **schema/domain-relevant edge cases**
  (empty, long, large, boundary, all status/enum variants — bounded by default, not invalid-by-reflex). The
  **seed script is a governed, idempotent/re-runnable deliverable** with guardrails (codex fix 3): explicit
  faker seed; clearly synthetic **non-PII** values; **never executes against / mixes with prod**. Avoid
  **thin ad-hoc hardcoded-only** data (codex fix 4) — but curated literal edge-case records inside the
  governed seed script are encouraged (often the clearest way to guarantee boundary cases).
- **D2 — concern-resolution auto-selects `sample-data`** for any data-backed product at high autonomy
  (composes; `areas: data` keeps it scoped — the resolver still selects it for data-backed products without
  over-broadening to `all`, codex fix 5).

## Bucket 1 — docs/ specs

| # | Change | File(s) | Done when |
|---|--------|---------|-----------|
| D1 | Govern sample-data as a concern: semantic faker library, varied shapes + edge cases, seed script a governed deliverable | extend `FEAT-006-concerns-practices-context-digest.md` (concern catalog) | FEAT lists sample-data + its intent |

## Bucket 2 — workflows/ concern + resolution

| # | Change | File(s) | Done when |
|---|--------|---------|-----------|
| D1 | New concern `sample-data/` (concern.md + practices.md): Category quality-attribute (data); **Areas: data**; boundary vs `testing` stated; Components = semantic faker lib (tech-stack-specific named default; typescript-bun → @faker-js/faker); Constraints = varied shapes + schema-relevant edge cases (empty/long/large/boundary/all-status, bounded), determinism via explicit seed + stable locale + pinned version + ordered generation, governed idempotent seed script w/ guardrails (non-PII, never prod), avoid thin hardcoded-only (curated edge-case literals OK); Drift Signals = thin ad-hoc rows / no faker / no edge cases / unseeded nondeterminism / PII | `workflows/concerns/sample-data/{concern.md,practices.md}` | concern exists with those practices + boundary |
| D2 | Concern-resolution auto-selects `sample-data` for data-backed products (composable) | `workflows/references/concern-resolution.md` | resolution names sample-data as applicable to data-backed products |

## Bucket 3 — skill (`skills/helix/SKILL.md`) — normative, runtime-neutral

| # | Change | Done when |
|---|--------|-----------|
| D1 | Concern guidance: data-backed products seed VARIED sample data via a semantic faker lib (not hardcoded rows), covering edge cases | SKILL.md reflects the sample-data discipline |

## How we'll re-run the bench (validate THIS plan)

Parallel re-bench (claude + codex). Expect: both select `sample-data`, depend on `@faker-js/faker`, and ship a
**governed seed script** that generates VARIED data + edge cases (empty/long/large/boundary/all-status) — so
the apps exercise empty/overflow/large-number UI states instead of 2 hardcoded rows. Spot-check: faker in
package.json + a seed script + row-count/variety in the seeded store.

## Invariants
- Composable concern (no slot), **areas: data**. The faker library is a tech-stack-specific named default;
  **determinism comes from an explicit seed + stable locale + pinned version + ordered generation**, not from
  the library choice.
- **Boundary:** `testing` owns test fixtures/factories/mocks; `sample-data` owns governed app seed/demo data.
- Seed data is a *governed, idempotent deliverable* with guardrails (non-PII, never prod), not an afterthought.
  Avoid thin hardcoded-only data; curated edge-case literals inside the seed script are fine.
- Composes with tech-stack (faker pick follows the runtime) + ties to UX (exercises empty/overflow states).
- Runtime neutrality; no `Skill tool_use`; don't flatten the loop. Keep `check-workflow-paths` green; re-bless
  ddx hashes; codex-review this plan BEFORE and the diff AFTER.
