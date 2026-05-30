---
ddx:
  id: FEAT-011
  status: draft
  depends_on:
    - helix.prd
    - FEAT-006
  review:
    self_hash: 0d31847adee3e2048695700a430e37b6c8c65c93c2ce94dc7d2cc11aa5f4f9eb
    deps:
      FEAT-006: 7517c7bf2db366dcdbae3ada995a5c0148955b332cf34d567180dff971d79489
      helix.prd: 2b22383538b33c6ecee57f43d85128dfef7d56254766b757aa36439e35f2bfc9
    reviewed_at: "2026-05-25T20:24:24Z"
---

# Feature Specification: FEAT-011 — Slider Autonomy

**Feature ID**: FEAT-011
**Status**: Draft
**Priority**: P1
**Owner**: HELIX maintainers

## Overview

HELIX expresses an **autonomy policy**; a capable runtime supplies the agency.
This feature defines that policy as a three-position spectrum — `low`,
`medium`, `high` — that controls **how often a HELIX workflow pauses for human
confirmation** without changing **which activities run**. The vocabulary and
the per-level behavior already live in `workflows/actions/input.md`; this spec
makes them a governed feature, extends them with concern-inference at high
autonomy, fixes the resolution precedence, and records the two invariants the
spectrum must never violate.

HELIX still ships no execution engine (PRD Non-Goals). Autonomy is a policy the
methodology authors and a runtime honors. This spec restores the dangling
references to FEAT-011 / TD-011 that survived the scope collapse
(`workflows/actions/input.md`, CONTRACT-001, CONTRACT-002) and re-scopes the
feature to the content-only methodology: there is no `helix run`,
`execute-loop`, or slider-config file — the autonomy signal is carried in
runtime-neutral artifacts (per-invocation argument, artifact frontmatter, or
project policy), never in `CLAUDE.md` or a runtime-specific config.

## Problem Statement

- **Current situation**: `input.md` defines `low`/`medium`/`high` semantics and
  cites "FEAT-011 / TD-011", but those governing artifacts were removed in the
  collapse (823aa1ac), leaving the citation dangling. CONTRACT-002 still records
  a FEAT-011 review-dependency hash that resolves to nothing. Nothing states how
  the level is resolved, what high autonomy may infer, or what it may never
  skip.
- **Pain points**:
  1. **Dangling authority** — the autonomy vocabulary is used across actions but
     governed by no on-disk feature, so the behavior cannot be audited or
     ratcheted.
  2. **Under-defined high autonomy** — "create without prompts" does not say
     whether a high-autonomy run may *select concerns* when none are declared,
     which is exactly the gap that made the concerns library inert
     ([[FEAT-006]]).
  3. **Ambiguous precedence** — when a per-invocation level, an artifact
     frontmatter value, and a runtime default all exist, nothing says which
     wins.
  4. **Risk of loop collapse** — "more autonomy" is easily misread as "skip
     activities", which would flatten the seven-activity loop the PRD forbids.
- **Desired outcome**: a governed autonomy spectrum with a defined resolution
  order, an explicit hard-stop invariant, an explicit never-collapse-the-loop
  invariant, and concern-inference defined for high autonomy.

## Autonomy Levels (canonical semantics)

These reuse the `input.md` semantics verbatim in intent. They are the single
source of truth; `input.md` and other actions implement them.

| Level | Checkpoint density | Assumption handling | Concern inference |
|-------|--------------------|---------------------|-------------------|
| `low` | Ask before each step and before creating each downstream artifact. Do not infer unconfirmed scope. | Confirm every assumption with the user. | Concern selection stays interactive — ask the user per category. |
| `medium` (default) | Create deterministic non-conflict artifacts. Pause when ambiguity or conflict blocks deterministic progress on an affected artifact. | Flag ambiguous scope in artifact/work-item text rather than inventing it. | Prompt for concern selection during framing when no `concerns.md` exists. |
| `high` | Create downstream artifacts without interactive prompts unless blocked by a hard-stop constraint. | Record assumptions as speculative work items (label `kind:speculative`) instead of asking. | **Infer concern selection** from the product's nature and record the inference, rather than pausing to ask. |

## Requirements

### FR-1: Three-position spectrum, default medium

Autonomy is `low`, `medium`, or `high`. The default when no level is supplied
is `medium`. The vocabulary is fixed — actions and the skill must not introduce
a parallel vocabulary (no `ask-first`/`guided`/`yolo` synonyms in normative
text).

### FR-2: Resolution precedence

A workflow resolves the active autonomy level in this order, first match wins:

1. **Per-invocation override** — the level passed with the request (e.g. an
   `--autonomy high` argument or an explicit instruction in the prompt).
2. **Artifact frontmatter / project policy** — an `autonomy:` value declared in
   the governing artifact's frontmatter or in the project's policy artifact
   (runtime-neutral markdown the project commits).
3. **Runtime default** — `medium`.

`CLAUDE.md` (or any runtime-specific instruction file) is **not** part of this
chain. The autonomy signal must be expressible in runtime-neutral artifacts so
the same project behaves identically across runtimes.

### FR-3: Concern-inference at high autonomy

When autonomy is `high` and `docs/helix/01-frame/concerns.md` does not exist,
the workflow infers the concern selection from the product's nature (e.g. a web
app implies a frontend + accessibility concern; a CLI implies a tech-stack
concern) and writes `concerns.md`, recording each inferred concern as an
assumption. At `low`/`medium`, concern selection stays interactive per
[[FEAT-006]]. Inference never silently overrides an existing `concerns.md`.

**Exclusive slots are filled deterministically.** For each *needed* exclusive
slot (the functional positions defined in `workflows/concerns/slots.yml` —
frontend-framework, language-runtime, etc.; see [[FEAT-006]]), high-autonomy
inference fills the slot by resolution order, first match wins:

1. **Operator override** — the slot's value in
   `docs/helix/01-frame/concerns.local.yml` (read before `concerns.md` exists),
   if present.
2. **Shipped default** — the slot's value in `slots.yml` `defaults:`.
3. **Recorded assumption** — if neither supplies a filler, record an assumption
   to revisit; never make a silent pick.

The chosen filler and its source ("concerns.local.yml override", "slots.yml
default", or "assumption") are recorded in `concerns.md`. **A web app must fill
the `frontend-framework` slot** — leaving it empty (raw-served HTML with no
supported framework) is the failure this requirement exists to prevent; the
shipped default `react-nextjs` takes effect with no operator configuration. This
slot-filling only fills *absent* selections; it never overrides an existing
`concerns.md`.

### FR-4: Hard-stop invariant (all levels)

Autonomy raises or lowers the **pause threshold**, never the **stop floor**.
Regardless of level, a workflow must stop and surface to a human when:

- two higher-or-equal-authority artifacts **truly contradict** (a physics-level
  conflict the authority hierarchy cannot reconcile);
- the next action is destructive or irreversible (data loss, history rewrite,
  external publish) and was not explicitly authorized;
- a decision is required that only a human can make (product direction, an
  external contract change).

High autonomy proceeds through *resolvable* conflicts (recording assumptions);
it never proceeds through a hard stop. A runtime preserve/abort outcome is an
execution result handed back to HELIX, not a license to bypass a hard stop.

### FR-5: Never-collapse-the-loop invariant (all levels)

Autonomy changes checkpoint density only. It must never collapse the
seven-activity loop (discover → frame → design → test → build → deploy →
iterate) into a single generic prompt, and must never skip an activity that the
work requires. A high-autonomy run executes the same activities a low-autonomy
run would; it simply pauses less often between and within them. This is the
feature-level binding of PRD Non-Goal "HELIX will not flatten the
seven-activity loop into one generic prompt."

## Acceptance Criteria

| AC ID | Given | When | Then |
|-------|-------|------|------|
| FEAT-011-AC1 | a request with no autonomy argument and no frontmatter `autonomy:` | a HELIX action resolves the level | the level is `medium` |
| FEAT-011-AC2 | a request carrying `--autonomy high` and a governing artifact whose frontmatter says `autonomy: low` | the level is resolved | the per-invocation override wins (`high`) |
| FEAT-011-AC3 | autonomy `high` and no `concerns.md` for a web-app product | a frame/input pass runs | `concerns.md` is created with inferred concerns recorded as assumptions, with no interactive prompt |
| FEAT-011-AC4 | autonomy `high` and two equal-authority artifacts that truly contradict | the workflow reaches the conflict | the workflow stops and surfaces the contradiction (hard stop), it does not pick a side silently |
| FEAT-011-AC5 | any autonomy level | a workflow runs end to end | every activity the work requires still runs; no activity is skipped and the loop is not flattened |
| FEAT-011-AC6 | the restored FEAT-011 file on disk | CONTRACT-002 / CONTRACT-001 / `input.md` are read | their references to FEAT-011 resolve to this artifact |

## Edge Cases and Error Handling

- **Conflicting precedence sources** — if an artifact frontmatter value and a
  project policy value disagree, the nearer governing artifact's frontmatter
  wins; record the divergence as an alignment finding.
- **High autonomy with an existing `concerns.md`** — never overwrite it;
  inference only fills an absent selection.
- **Unknown level token** — treat any value other than `low`/`medium`/`high`
  as unset and fall through to the next precedence source.

## Success Metrics

- Zero dangling FEAT-011 / TD-011 references in the repo after restore.
- Autonomy behavior is auditable: alignment review can classify an autonomy
  precedence or loop-collapse violation as a finding.
- High-autonomy runs select concerns without a human prompt while never
  bypassing a hard stop (measured by the FEAT-011-AC4 / AC5 scenarios).

## Constraints and Assumptions

- HELIX ships the policy, not the agency. The runtime executes; HELIX states
  how often it should pause and what it may never skip.
- The autonomy signal lives only in runtime-neutral artifacts. No `CLAUDE.md`
  dependency, no slider-config file, no CLI flag owned by HELIX.

## Dependencies

- **helix.prd** — autonomy first-class goal (Non-Goals) and the
  seven-activity-loop guarantee.
- **[[FEAT-006]]** — concern selection that high autonomy infers.
- **ADR-003** — the autonomy-spectrum decision record (ADR-003 depends on this feature).

## Out of Scope

- A runtime autonomy UI or config schema (runtime-owned).
- Per-step autonomy beyond the three positions (no numeric slider).
- Replacing human judgment on hard-stop decisions.

## References

- [Autonomy Spectrum ADR](../../02-design/adr/ADR-003-autonomy-spectrum.md)
- [TD-011: Slider Autonomy Implementation](../../02-design/technical-designs/TD-011-slider-autonomy-implementation.md)
- [CONTRACT-002: HELIX Execution-Document Conventions](../../02-design/contracts/CONTRACT-002-helix-execution-doc-conventions.md)
- [Input action](../../../workflows/actions/input.md) — implements these semantics
