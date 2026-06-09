# T7 — marker declares scope-keyed methodologies → cwd selects [HIGH RISK]

## Scenario

`helix-library`, `helix`, and `helix-infra` are all installed. The
workspace `.helix.yml` declares both methodologies with disjoint
scopes and NO `defaults.methodology:`:

```yaml
helix_version: 1
methodologies:
  - id: helix
    root: services/web/docs/helix/
  - id: helix-infra
    root: services/web/infra/terraform/
```

The agent's cwd is `services/web/infra/terraform/`. Per design §1.5
resolution rule 3 ("cwd under one methodology's `root:` wins"), the
infra methodology activates because cwd is inside its scope. The
product methodology stays silent.

## Why it matters

This is the canonical "scope-keyed marker + cwd" test. Two
methodologies share a monorepo, the operator's intent is encoded by
scope assignment, and cwd disambiguates without needing a default or
prefix. If the skill ignores cwd-under-scope and falls back to
defaults / heuristics / alphabetical tie-break, multi-team monorepos
break.

The OLD T07 behavior (mixed signals + disambiguation banner) only
applies when the marker is ABSENT — moved to T07a.

## What passes

- `Write` `tool_use` against `docs/adr/<NNNN>-<slug>.md` OR
  `services/web/infra/terraform/docs/adr/...` per helix-infra's
  authoring routing.
- NO `Write` against `services/web/docs/helix/`.
- NO disambiguation banner (cwd resolves the ambiguity).

## What fails

- `Write` against `services/web/docs/helix/02-design/` (product
  methodology activated despite cwd being outside its scope).
- Disambiguation banner (no ambiguity remains once cwd is consulted).
- Two writes (both methodologies fired).

## Risk

HIGH. Scope-keyed routing by cwd is the monorepo story; if it breaks,
the marker's per-scope expressiveness is dead and operators must
edit the marker for every cwd switch.
