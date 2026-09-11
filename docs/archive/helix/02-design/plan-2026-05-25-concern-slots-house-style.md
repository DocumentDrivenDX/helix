# Plan — concern slots + operator house-style (2026-05-25)

## Context

The regression bench surfaced that high-autonomy concern-selection is non-deterministic across runs:
one run inferred `react-nextjs` (a real React UI), the next inferred raw `typescript-bun` server-rendered
HTML and **filled no frontend-framework concern at all**. The operator's standing intent ("a real
human-facing UI via a supported framework") has nowhere to live, and inference has no tiebreak when
several concerns could fill the same functional position.

**The fix is a minimal taxonomy — one new dimension (a *slot*) — plus a single keyed registry of defaults,
layered with an operator override.** Scope-disciplined: add the slot concept, wire it into high-autonomy
inference + an integrity check, ship defaults for the two slots the bench exercises. No friction matrix,
no `alternatives:`/`conflicts-with:` fields (membership is derived from slots, not duplicated).

## Design (settled)

Three facts kept separate (the `(default)` inline marker wrongly fused them and made "two defaults for one
slot" representable — the same self-claim drift class as the prd template↔meta 1/8):

| Fact | Nature | Home |
|---|---|---|
| what slot a concern can fill | intrinsic (react-nextjs **is** a frontend framework) | `## Slot` in `concern.md` |
| which concern wins a slot by default | relational (a choice **among** competitors) | `slots.yml` `defaults:` — **map keyed by slot** |
| operator house override | same relational shape | `concerns.local.yml` `defaults:` (layered on top) |

- **"slot", not "role"** — DDx already owns "role" for persona bindings; avoid the collision.
- **Membership is derived, not listed**: a concern is a candidate for slot X iff its own `## Slot` says X.
  Adding a concern carries zero registry sync burden; the registry only ever holds the one
  irreducibly-relational fact (the default per slot).
- **Two-defaults is forbidden by the integrity check**: `defaults:` is a map keyed by slot (one default
  per slot), but YAML keeps the *last* of duplicate keys silently rather than erroring — so the keyed shape
  alone is not the guarantee. The Slot Registry Integrity check rejects duplicate `defaults:` keys, which is
  what actually makes "two defaults for one slot" impossible. (codex-review fix, 2026-05-25)
- **Resolution order per needed exclusive slot** (high autonomy): operator override (`concerns.local.yml`)
  → shipped default (`slots.yml`) → otherwise record an assumption (never a silent pick).
- **A web app must fill the `frontend-framework` slot** — the actual bug was that inference left it empty
  and raw-served HTML. Filling the slot (default `react-nextjs`) is the core behavioral change.

```yaml
# workflows/concerns/slots.yml — single source of truth (shipped)
slots:
  frontend-framework: { exclusive: true }
  language-runtime:    { exclusive: true }
  datastore:           { exclusive: true }   # no members in the lib yet — slot defined, no default
  deploy-target:       { exclusive: true }
  # composable positions (compose freely, no single winner) need no slot entry:
  # a11y, security, testing, o11y, i18n
defaults:
  frontend-framework: react-nextjs
  language-runtime:   typescript-bun
```

```yaml
# docs/helix/01-frame/concerns.local.yml — operator house-style (optional, read BEFORE concerns.md exists)
defaults:
  frontend-framework: react-nextjs   # override of the shipped default, per project
```

```markdown
# react-nextjs/concern.md
## Slot
frontend-framework
```

## Bucket 1 — docs/ specs

| # | Change | File(s) | Done when |
|---|--------|---------|-----------|
| S1 | Define the slot concept + the `slots.yml` registry + `concerns.local.yml` override + resolution order + the structural single-default guarantee | extend `FEAT-006-concerns-practices-context-digest.md` | FEAT documents slot, keyed-default registry, derived membership, override layering |
| S2 | High-autonomy inference fills each **needed exclusive slot** via override→default→assumption; a web app must fill `frontend-framework` | extend `FEAT-011-slider-autonomy.md` (FR-3) | FR-3 describes slot-filling + the house-style override |

## Bucket 2 — workflows/ actions + concerns

| # | Change | File(s) | Done when |
|---|--------|---------|-----------|
| S1 | Ship `slots.yml` (4 exclusive slots + 2 defaults) | `workflows/concerns/slots.yml` (new) | file exists, valid YAML |
| S1 | Add `## Slot` to the concerns that fill exclusive slots | `react-nextjs` → frontend-framework; `typescript-bun,python-uv,go-std,rust-cargo,scala-sbt` → language-runtime | each names a slot present in `slots.yml` |
| S2 | Concern-selection resolution: per needed exclusive slot, apply override→default→assumption; record the chosen filler + its source in `concerns.md` | `workflows/references/concern-resolution.md` | high-autonomy section describes slot resolution + reads `concerns.local.yml` |
| S3 | **Integrity check** (M2 discipline): every `## Slot` names a known slot; every `defaults:` value names a concern whose `## Slot` matches that key; defaults only for `exclusive` slots; `concerns.local.yml` overrides name real slot+concern | `workflows/actions/reconcile-alignment.md` (+ optional `scripts/` linter) | a drifted registry (typo default / unknown slot) is flagged |

## Bucket 3 — skill (`skills/helix/SKILL.md`) — normative, runtime-neutral

| # | Change | Done when |
|---|--------|-----------|
| S2 | Frame/concern-selection guidance: at high autonomy, fill exclusive slots from `concerns.local.yml` → `slots.yml` defaults → assumption; web apps fill `frontend-framework` | SKILL.md reflects slot resolution + house-style override |

(No "role" collision, no friction matrix, no `alternatives:` field — membership is derived from `## Slot`.)

## How we'll re-run the bench (validate THIS plan)

1. Re-run the clean bench (`bin/rerun-clean.sh`, bare prompt, improved HELIX) and score with the honest
   `bin/score.sh`. **Expect the `frontend-framework` slot now filled with `react-nextjs` UNPROMPTED**
   (UI kind: spa, `*.tsx` present) — the house default takes effect with no operator config.
2. Add a `concerns.local.yml` pinning a different filler and re-infer in a scratch frame to confirm the
   override beats the shipped default (cheap, no full app build).
3. Confirm the integrity check flags a deliberately-drifted `slots.yml` (typo default).
4. Keep only what moved/clarified a metric.

## Invariants
- "slot" not "role"; defaults live in one keyed map + the integrity check rejects duplicate keys (YAML alone
  is last-wins, so the check is what forbids two-defaults).
- Membership derived from `## Slot`, never a second list to sync.
- Runtime neutrality; no `Skill tool_use` in the skill body; don't flatten the loop.
- Keep `check-workflow-paths` green; re-bless ddx hashes; commit unsigned only if the signer is unavailable.
