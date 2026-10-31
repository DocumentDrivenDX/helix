---
ddx:
  id: ADR-016
  status: accepted
  authoring:
    home: repo
---

# ADR-016: Slot defaults depend on the platform profile

| Date | Status | Deciders | Related | Confidence |
|------|--------|----------|---------|------------|
| 2026-10-31 | Accepted | HELIX maintainers | FEAT-006, FEAT-011, ADR-014, concerns/databricks-apps, concerns/lakebase, concerns/databricks-obo-identity | High |

## Context

| Aspect | Description |
|--------|-------------|
| Problem | Slot defaults in `slots.yml` are global (`react-nextjs`, `typescript-bun`, `auth-local-sessions`). They suit a self-hosted TypeScript web app, but a product hosted on Databricks Apps needs a different, coherent stack: a Python backend, a Vite SPA it serves, Lakebase, and platform identity. Today every such project restates that stack in `concerns.local.yml`, and two of its fillers exist only as project-owned concerns. |
| Current State | The recommended Databricks combination is prose in the `databricks-apps` concern's `## When to use`, which resolution never reads. The `datastore` slot has no library member. Integrity rules for `slots.yml` are described but not executable. |
| Requirements | Keep slot membership derived from each concern's `## Slot`; keep one global default per slot; keep operator overrides first; add no runtime dependency. |

## Decision

We will add `profiles:` to `slots.yml`. A profile is keyed by the concern that
triggers it, names that one governing slot and filler under `when`, supplies
defaults for other slots, and lists recommended composable concerns under
`compose`. Resolution per needed slot becomes: operator override, then the
matching profile default, then the global default, then a recorded assumption.
The governing slot resolves first.

The first profile is `databricks-apps`: `python-uv`, `react-vite`, `lakebase`,
and `databricks-obo-identity`, composing `databricks-appkit-ui`,
`unity-catalog`, and `databricks-ai-gateway`. `lakebase` and
`databricks-obo-identity` become library concerns.

`scripts/check_concern_slots.py` makes the Slot Registry Integrity rules
executable, including the profile rules: at most one profile per trigger, a
profile never defaults its own trigger slot, and `compose` holds only slot-free
concerns.

**Key Points**: conditional defaults, not new slots | operator override still
wins | one profile matches a project | integrity is checked in CI

## Alternatives

| Option | Pros | Cons | Evaluation |
|--------|------|------|------------|
| Change the global defaults to the Databricks stack | No new mechanism | Wrong for every product not on Databricks | Rejected |
| Leave the stack to each project's `concerns.local.yml` | No change | Every Databricks project restates the same stack; drift between projects | Rejected |
| Implied concerns declared inside each concern (`## Implies`) | Local to the trigger concern | Spreads relational facts across concern files; contradicts the registry holding the relational facts | Rejected |
| **Profiles keyed by a governing slot filler in `slots.yml`** | One place for relational facts; conditional; overridable; checkable | One more resolution step | **Selected** |

## Consequences

| Type | Impact |
|------|--------|
| Positive | A Databricks project selects its full stack by filling `deploy-target`; the `datastore` slot gains a library member; registry integrity fails CI instead of relying on review. |
| Negative | Resolution has four steps instead of three; frame prompts and the skill must resolve the governing slot first. |
| Neutral | ADR-014's question (variants versus separate concerns per slot) is unchanged. |

## Risks

| Risk | Prob | Impact | Mitigation |
|------|------|--------|------------|
| Two profiles match one project | L | M | One trigger per profile, a single governing slot per profile, checked by the integrity script |
| Platform facts in the new concerns go stale | M | M | Each concern dates its platform facts; re-verify before a design depends on them |

## Validation

- `tests/validate-concern-slots.sh` passes on the shipped registry and rejects each broken fixture.
- The `frame-databricks-app-profile` eval brief resolves the profile from a vision that names Databricks Apps.
