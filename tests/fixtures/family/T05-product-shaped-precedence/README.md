# T5 — marker declares both methodologies → both active, scoped [HIGH RISK]

**Flow classification:** legacy marker-routing fixture. Retained as a frozen
compatibility probe for the old `methodologies:` marker and public
`helix-infra` sibling-skill design.

## Scenario

`helix-library`, `helix`, and `helix-infra` are all installed. The
workspace carries a `.helix.yml` at its root declaring BOTH
methodologies with explicit scopes:

```yaml
helix_version: 1
methodologies:
  - id: helix
    root: docs/helix/
  - id: helix-infra
    root: infra/terraform/
defaults:
  methodology: helix
```

The workspace contains `docs/helix/01-frame/prd.md` and
`infra/terraform/main.tf` — both methodology shapes are present, but
the marker resolves the ambiguity.

## Why it matters

This is the canonical "explicit marker decides" test. Per design §1.5
resolution chain, when the marker lists 2+ methodologies and neither
`/<id>` prefix nor `HELIX_METHODOLOGY` is set, cwd-under-scope wins;
if cwd is at repo root, `defaults.methodology:` wins. The user prompt
("record an ADR for our SSO approach") has no infra signal, so the
default applies and the ADR routes to the product methodology even
though both shapes coexist.

The old heuristic precedence behavior (repo-shape sniffing,
alphabetical tie-break) is FROZEN and only fires when `.helix.yml` is
absent — see T05a for that path.

## What passes

- `Write` `tool_use` against `docs/helix/02-design/<NNNN>-<slug>.md`.
- Prose MAY include a one-line "marker:helix" trace banner.
- Prose MUST NOT contain a Write outside `docs/helix/02-design/`.
- Prose MUST NOT contain a setup-gap (marker is well-formed).

## What fails

- ADR written to `docs/adr/` (helix-infra silently won despite
  marker default).
- ADR written outside `docs/helix/02-design/`.
- Two writes (both methodologies fired despite default).
- Setup-gap (marker not read).

## Risk

HIGH. The marker IS the operator's intent; if the skill ignores it
and falls back to heuristics, every dual-install user with an
explicit marker gets surprise routing.
