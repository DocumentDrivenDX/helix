---
ddx:
  id: FEAT-014
  depends_on:
    - FEAT-013
    - helix.prd
    - TP-014
    - TP-014-A
  status: draft
  review:
    self_hash: 759c40f844c097c8f4a02a3ae6de1ca4b8867dc7b102cc7d3d62ec15bea06b99
    deps:
      FEAT-013: d8601a108b58cf7970aa7e6339770fee9ef0b1c1a3639e75b0ea884abf9a03bc
      FEAT-016: 226872932728d635279abac06206be77cee1075d787aae7760010941adb9c1e1
      TP-014: fe45bf000e0976c842065d7ae161456d708b1356f48babb1d283a49aab55bc2e
      TP-014-A: 3ed320673677753445c6b1280d460ceef06a47c4f0953decd1f0ebbe982717ff
      helix.prd: 2b22383538b33c6ecee57f43d85128dfef7d56254766b757aa36439e35f2bfc9
    reviewed_at: "2026-05-25T16:26:54Z"
---

# Feature Specification: FEAT-014 — Workflow Coverage

**Feature ID**: FEAT-014
**Status**: Draft
**Priority**: P0
**Owner**: HELIX maintainers

## Overview

HELIX is not done when its install path works — it is done when its
user journeys work. FEAT-013 covered install. FEAT-014 covers what
happens *after* install: bootstrap a project with a vision, derive
downstream artifacts, iterate on changes, build test and
implementation plans, review, plus the negative-path scenarios where
HELIX must refuse to improvise. Verified per runtime, in Docker
where headless, with manual browser capture where the runtime forces
it (Genie Code). This operationalizes TP-014 and the real-world
intent-pattern findings in TP-014-A.

## Ideal Future State

A user installs HELIX on any of the five supported runtimes (DDx,
Claude Code, OpenAI Codex CLI, GitHub Copilot, Databricks Genie
Code) and runs through the full HELIX workflow — sparse intent →
governed vision and PRD → derived feature specs, ADRs, technical
designs → an iterating change request that threads through the
stack → mechanically-verifiable test and implementation plans →
fresh-eyes review. Each step's output is structurally identical
across runtimes (section headings, frontmatter, dependency edges);
only prose differs. HELIX refuses to silently improvise when the
governing artifacts are missing, when a request contradicts an
existing ADR, when intent is ambiguous, or when the user pastes
evidence of a scope problem expecting in-place patching. The repo's
CI runs the static portion of every scenario on every PR and the
functional portion (with LLM calls) on release tags, with captured
recordings as release evidence.

## Problem Statement

- **Current situation**: FEAT-013 confirms the install path. Beyond
  install, nobody knows whether the runtimes actually produce the
  right HELIX artifact behavior. Manual spot-checks during Genie e2e
  on 2026-05-16 already surfaced one real product bug (bead
  `helix-96f7dd34`: Genie can't resolve bundle-relative catalog
  paths). Without a workflow test suite, every shipped change to
  SKILL.md, templates, or runtime adapters is unverified.
- **Pain points**:
  1. No deterministic check that the routing skill actually routes
     real user prompts to the right mode on each runtime.
  2. No deterministic check that downstream artifacts produced by
     `frame`/`design`/`evolve` carry the right shape (frontmatter,
     dependency edges, template-conformant sections).
  3. No fixture for the iterating-change journey, which is HELIX's
     most-load-bearing claim (authority-hierarchy propagation).
  4. No assertion that HELIX refuses to improvise — yet TP-014-A §5
     documents four real cases where runtimes did improvise when the
     §Operating Discipline contract says they should not.
- **Desired outcome**: a `tests/workflows/` test harness that
  exercises 13 named scenarios per runtime with deterministic pass
  criteria, captures recordings per release, and is wired into the
  default `just test` (static) and `just install-test` (functional)
  recipes.

## Functional Areas

| Area | User question or job | Feature responsibility |
|---|---|---|
| Shared fixture | "What's a representative HELIX project to test against?" | Provide `tests/workflows/fixtures/recipe-app/` with seed prompts, pre-staged baselines, and expectations files all five runtimes consume |
| Shared verifiers | "How do we assert HELIX produced the right shape?" | Provide `verify-sections.sh`, `verify-frontmatter.sh`, `verify-dependency-edges.sh`, `verify-no-orphan-files.sh` |
| Per-runtime harness | "How do we run a scenario on this runtime?" | One subdirectory per runtime with install + scenario-runner + recording config |
| Workflow scenarios | "Does HELIX behave correctly for journey X?" | 13 scenarios covering bootstrap, derive, evolve, test plans, impl plans, status, review, plus 4 negative-path + non-match |
| Test harness entry | "How do we run everything?" | Top-level `just workflow-test` recipe and `tests/workflows/run-all.sh` |
| CI integration | "How does this gate the release?" | Static checks on every PR; functional checks (LLM cost) gated by `TEST_FUNCTIONAL=1`; recordings re-captured per release tag |

## Requirements

### Functional Requirements by Area

#### Shared fixture (FIX-*)

[FIX-01]. `tests/workflows/fixtures/recipe-app/seed/` MUST contain
five text files: `intent.txt`, `change-request.txt`,
`contradiction.txt`, `ambiguous.txt`, `mechanical-prompts.txt`.
Sizes ~30-50 words each (per TP-014 §4). Contents per TP-014
scenario inputs.

[FIX-02]. `tests/workflows/fixtures/recipe-app/baseline/` MUST
contain pre-staged artifact files for scenarios that depend on
scenario 1 + 2 outputs (so later scenarios don't have to re-run
expensive LLM bootstrap): `docs/helix/00-discover/product-vision.md`,
`docs/helix/01-frame/prd.md`, `docs/helix/01-frame/features/FEAT-recipe-share.md`,
`docs/helix/02-design/adr/ADR-001-sqlite.md`,
`docs/helix/02-design/technical-designs/TD-recipe-store.md`.

[FIX-03]. `tests/workflows/fixtures/recipe-app/expectations/` MUST
contain canonical expected outputs per scenario: section-anchor
lists (`sections-vision.txt`, `sections-prd.txt`,
`sections-feat.txt`, `sections-td.txt`), `frontmatter-fields.yml`,
and `expected-mode.txt` per scenario (records the routing mode the
runtime should select).

#### Shared verifiers (VER-*)

[VER-01]. `tests/workflows/shared/verify-sections.sh <artifact> <expected-anchors>`
MUST exit 0 iff every required `^## ` heading in the expected-anchors
file is present in the artifact.

[VER-02]. `tests/workflows/shared/verify-frontmatter.sh <artifact> <expected-fields>`
MUST exit 0 iff the YAML frontmatter parses AND every field in the
expected-fields YAML appears with the documented value or shape.

[VER-03]. `tests/workflows/shared/verify-dependency-edges.sh <artifacts-root> <expected-edges>`
MUST exit 0 iff every parent-child `ddx.depends_on` edge in the
expected-edges file appears in the actual artifact graph and no
forbidden edges exist.

[VER-04]. `tests/workflows/shared/verify-no-orphan-files.sh <root> <allowed-paths>`
MUST exit 0 iff no files exist outside the allowed-paths glob set.

#### Per-runtime harness (RT-*)

[RT-01]. Each of `tests/workflows/{ddx,claude-code,codex-cli,copilot-cli}/`
MUST contain a Dockerfile, an `install.sh`, a `run-scenarios.sh`
script that iterates the 13 scenarios, and per-scenario `*.tape`
files for `vhs` recording.

[RT-02]. `tests/workflows/genie/` MUST contain `install.py` and
`verify.py` wrappers (already exist from FEAT-013), a
`run-scenarios.py` driving the Playwright e2e against the workspace,
plus a `test-procedure-<scenario>.md` for each scenario covering
the manual browser steps.

[RT-03]. Where a runtime cannot satisfy a scenario's requirements
(e.g. Copilot CLI long-form authoring; Genie bundle-catalog
reachability until bead `helix-96f7dd34` lands), the runtime's
scenario MUST emit a skip with an explicit `<runtime>:<reason>`
label (e.g. `genie:catalog-unreachable`) rather than fail
silently.

#### Workflow scenarios (SCN-*)

[SCN-01..10]. Implement the 10 scenarios from TP-014 with the
pass criteria documented there (scenarios 1, 2, 3, 4, 5, 6, 7a,
7b, 7c, plus install which is FEAT-013).

[SCN-11..14]. Implement the four extensions from TP-014-A:
- SCN-11 / 5b: `check`/`next` positive case (status query against
  populated queue; response names next-ready + in-progress +
  blocker + §Align handoff; no CLI command).
- SCN-12 / 7d: non-match assertion. Mechanical prompts like `"pull
  and install"`, `"Use gpt-5.4-mini"` must NOT cause HELIX routing
  to fire. Runtime falls back to direct tool dispatch.
- SCN-13 / 8: `commit`/`release` mode. Dirty worktree with mixed
  bead + unrelated changes; assert scope separation, bead-id
  traceability, pre-push gate passes.
- SCN-14 / 9: `backfill` mode. Given code + tests + no
  `02-design/`, expect a new TD with `[confirmed]`/`[inferred]`
  markers and an uncertainty list naming missing evidence.

[SCN-15..18]. Hardened negative-path extensions per TP-014-A §5:
- SCN-15: Bare `"do it"` after prior turn surfaced ≥2 alternatives.
  Expected: route `check`, name the chosen branch verbatim or ask
  one focused question. Forbidden: silent pick.
- SCN-16: Scope complaint with paste (`"What is this BS? <paste>"`).
  Expected: route `align`/`evolve`, name the upstream artifact.
  Forbidden: in-place patching of the pasted snippet.
- SCN-17: Operator pushback on a reported blocker. Expected: align
  surfaces blocker by artifact:line, then route through §Align
  handoff. Forbidden: retry without diagnosis.
- SCN-18: `check`-mode improvising design. Expected: status +
  §Align next-step recommendation only. Forbidden: bundle design
  proposal in the same turn.

[SCN-19]. Per-scenario fixtures MUST be reused across runtimes —
the fixture is the contract; per-runtime variants describe
invocation and observability only.

#### Test harness entry (ENT-*)

[ENT-01]. `tests/workflows/run-all.sh` MUST build all Docker
images, iterate scenarios per runtime, capture recordings when
`vhs` is available, and exit with the count of failed scenarios.
Mirrors `tests/install/run-all.sh`.

[ENT-02]. The `justfile` MUST expose `workflow-test` and
`workflow-test-functional` recipes. The latter sets
`TEST_FUNCTIONAL=1`.

[ENT-03]. The `justfile` `test` recipe MUST include the static
portion of `workflow-test` (fixture sanity, verifier scripts work
against expectations, no-LLM scenarios pass).

### Acceptance Criteria

| Requirement | Scenario | Given | When | Then |
|---|---|---|---|---|
| FIX-01..03 | Fixture sanity | clean repo at HEAD | `find tests/workflows/fixtures/recipe-app -type f \| wc -l` | ≥ 15 files (5 seed + 5 baseline + 5+ expectations) |
| VER-01 | Section verifier passes on baseline | `recipe-app/baseline/docs/helix/01-frame/prd.md` | `bash tests/workflows/shared/verify-sections.sh <prd> <expected-prd.txt>` | exit 0 |
| RT-01 | Per-runtime images build | `tests/workflows/<runtime>/Dockerfile` | `docker build -t helix-workflow-test:<runtime> .` | exit 0, image present |
| SCN-01..10 | TP-014 scenarios pass on DDx + Claude Code | functional env vars set; static checks already pass | `TEST_FUNCTIONAL=1 bash tests/workflows/run-all.sh` | 10 scenarios pass on DDx + Claude Code (Genie scenarios 2/4/5/6 may be marked `genie:catalog-unreachable` per RT-03 until `helix-96f7dd34` resolves) |
| SCN-11..14 | TP-014-A extensions implemented | scenario fixtures staged | per-scenario verify scripts run | exit 0 on each |
| SCN-15..18 | Refusal hardening evidence | bare-`do-it` / scope-complaint / blocker-pushback / check-improvising fixtures | run scenario | runtime refuses to improvise; output names the expected route or clarifying question |
| ENT-01..03 | Harness entry works | clean repo | `just workflow-test` then `just workflow-test-functional` | both exit 0 |
| MG-01 | build/evolve/review actions | their action prompts are read | each names a verify-activity mode-gate that fails on findings (not a literal validate+align+check command list) |
| MG-02 | a completed workflow run | convergence is evaluated | "verified + finding-classes folded into gates" is the criterion; a bare reviewer "SHIP" does not by itself close the loop |

### Non-Functional Requirements

- **Performance**: full `just workflow-test-functional` completes in
  < 60 minutes on developer hardware. Functional run total cost
  estimated at $3–6 per sweep at Claude Sonnet pricing (per
  TP-014 §8).
- **Cost gating**: static checks on every PR are free. Functional
  checks gated by `TEST_FUNCTIONAL=1`, run on release tags only.
- **Reliability**: static checks must not depend on network access
  beyond the initial Docker base pull.
- **Auditability**: every recording carries a timestamp and HELIX
  version. Recordings dir contains a `.json` sidecar per recording
  (mirroring `tests/install/genie/recordings/<date>.json`).

## Self-Validation Meta-Gates and Convergence

HELIX's verification activities (`validate`, `align`, `check`) exist but did not
run *inside* the build/evolve/review loop, so finding-classes recurred. FEAT-014
mandates that self-validation run as **workflow-mode gates** and defines what
"done" actually means.

### MG-01: Self-validation runs as workflow-mode gates, not literal commands

The build, evolve, and review actions (and the `measure`/`report` actions they
embed) MUST each name a **verify-activity gate** that fails on findings. The
gate is expressed as a workflow mode/activity that must pass — e.g. "the
acceptance-criteria + claims-vs-reality classification yields no blocking
finding" — **not** as a literal "run `validate` then `align` then `check`"
command list. Naming literal action commands would recurse the loop into
itself; naming the *mode-gate* (the verification activity whose output must be
clean) does not.

### MG-02: Convergence ≠ "the reviewer says SHIP"

A workflow converges when **(a)** the work is *verified* — acceptance criteria
satisfied, concern gates green, ratchets within floor, zero `ASSERTED_UNBACKED`
claims ([[FEAT-016]]) — **and (b)** each finding-class surfaced during the run
has been *folded back into a gate* so the same class cannot silently recur. A
reviewer verdict of "SHIP" is evidence, not the definition. Re-splatting the
whole artifact set on every review is forbidden; progressive `evolve` against
the specific finding-class is the convergence path.

### MG-03: Cross-reference

The honesty property the meta-gates enforce is governed by [[FEAT-016]]; a
phantom claim is a blocking finding-class that MUST be folded into a gate, never
waved through by a reviewer verdict.

## Regression Bench: Validating a Methodology Change

Workflow coverage proves HELIX behaves correctly on a fixed set of scenarios.
The **regression bench** answers the adjacent question — *did a change to HELIX
itself actually improve anything?* — and it is the durable asset that separates
real wins from noise. It is a first-class HELIX experiment (see the
[experiment action](../../../workflows/actions/experiment.md)), not a one-off
re-derivation.

### RB-01: Bare-prompt re-run against a committed baseline

The bench fixes a representative brief, records the intrinsic metrics a
**committed baseline** of the methodology produces from the **bare prompt** (no
improved content), then re-runs the same brief after the change. The recorded
baseline — not memory or impression — is the reference point.

### RB-02: Install the improved skill; do not redirect reads

The re-run MUST exercise the change by **installing the improved skill**, never
by pointing the agent at the changed files. Reading-by-redirection measures
"the agent was told to use the new thing," not "the new thing is in force," and
confounds the result.

### RB-03: Intrinsic metrics only

Scoring uses intrinsic, mechanically checkable metrics (build/test pass,
template conformance, phantom-claim count, concern auto-selection,
real-vs-stub output) defined via the metric-definition contract. External
adversarial review is advisory evidence, never a bench metric (the
intrinsic-gates-blocking / external-review-advisory split, [[FEAT-016]] and the
fresh-eyes-review and evolve convergence rules).

### RB-04: Convergence and cut rule

A change converges on the bench when it **moves an intrinsic metric relative to
baseline** and the move survives the confidence floor. A change that does not
move a metric is **cut**, not kept on faith. "It feels better" is not evidence.
Fix the instrument before trusting its reading: a metric that disagrees with the
template it scores (template↔meta drift) is a broken instrument, resolved per
[[FEAT-016]] before the bench result is believed.

## User Stories

Single-feature scope without breakdown into separate stories. Beads
under FEAT-014 act as the implementation work items, organized by
phase (shared fixtures, per-runtime harness, per-scenario
implementations, harness entry, release).

## Edge Cases and Error Handling

- **Genie `helix-96f7dd34` unresolved**: scenarios 2/4/5/6 on Genie
  may produce `genie:catalog-unreachable` skips per RT-03. Tagged
  failures are not release blockers until that bead lands.
- **Copilot CLI long-form authoring**: scenarios 2, 3, 5 on
  Copilot CLI MUST allow up to three turns. If still failing,
  emit `copilot-cli:multi-file-authoring` skip and document an
  IDE-chat manual verification procedure.
- **DDx asymmetry in scenario 5**: bead-shape vs inline-checklist.
  Verifiers normalize to artifact files only; DDx-only `bead_id`
  fields excluded from equivalence checks.
- **Fixture drift**: when `expected-modes.txt`, section anchor
  lists, or frontmatter schemas change in HELIX, the corresponding
  `expectations/` files MUST be updated in the same PR. A doctor
  check fails when expectations reference removed sections.

## Success Metrics

| Metric | Target | Measurement |
|---|---|---|
| Static-coverage scenarios passing | 13 / 13 across all 5 runtimes | `just workflow-test` exit 0 |
| Functional-coverage scenarios passing | 13 / 13 on DDx + Claude Code + Codex CLI (minimum); Copilot CLI ≥ 7 of 13; Genie ≥ 4 of 13 until `helix-96f7dd34` resolves | `TEST_FUNCTIONAL=1 just workflow-test-functional` per release tag |
| Real-world prompt coverage | Top-5 patterns from TP-014-A §4 each have ≥ 1 scenario or per-scenario variant | per-scenario fixture audit |
| Recording freshness | ≥ 1 captured recording per (runtime × scenario) per release tag | `tests/workflows/<runtime>/recordings/` inspection |

## Constraints and Assumptions

- HELIX content stays runtime-neutral. The fixture and verifiers
  are. Per-runtime harness shells are the only runtime-coupled
  artifacts, and they exercise the same fixture.
- TP-014 + TP-014-A are the source of truth for scenario semantics.
  This feature spec lists requirements; the test plan documents the
  scenarios.
- Genie limitations are explicit, not silently absorbed. The
  `<runtime>:<reason>` skip pattern (RT-03) keeps known gaps
  visible.

## Dependencies

- **FEAT-013** (install coverage) — workflow scenarios run AFTER
  install. Reuses `tests/install/<runtime>/install.sh` via symlink.
- **TP-014** (workflow test plan) — defines the 10 base scenarios
  with pass criteria.
- **TP-014-A** (real-world patterns appendix) — defines the four
  extensions (5b, 7d, 8, 9) and the four refusal hardenings
  (SCN-15..18).
- **Bead `helix-96f7dd34`** (Genie catalog reachability) —
  unresolved; affects Genie scenario coverage.
- **`skills/helix/SKILL.md`** §Catalog Resolution (provides inline
  artifact-type index supporting common queries without filesystem
  traversal) and §Operating Discipline (four new refusal rules
  matching SCN-15..18).

## Relationships

- **Extends**: FEAT-013 (install) — workflow coverage is the next
  layer above install.
- **Informs**: future runtime adapters; the test harness shape is
  what new runtimes must match.
- **Referenced by**: TP-014, TP-014-A, the per-scenario beads
  generated under FEAT-014.
