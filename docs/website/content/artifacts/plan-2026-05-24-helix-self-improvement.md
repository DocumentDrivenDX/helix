---
title: "Plan — HELIX self-improvement from the yolo-demo arc (2026-05-24, rev 2: codex-reviewed)"
slug: plan-2026-05-24-helix-self-improvement
weight: 540
activity: "Design"
source: "02-design/plan-2026-05-24-helix-self-improvement.md"
generated: true
---
# Plan — HELIX self-improvement from the yolo-demo arc (2026-05-24, rev 2: codex-reviewed)

## Context

Distilled from an autonomous "one-shot a working app at max autonomy" build
(`~/Projects/helix-yolo/`): HELIX drove a real, accessible Next.js + bun invoicing app
(build 0, 123 unit + 32 e2e, WCAG AA) across several codex rounds (NOT-READY → SHIP-WITH-FIXES).
Seven failure modes recurred. Fixes captured as **three buckets**: 1) **docs/** governing specs,
2) **workflows/** templates/prompts/examples + actions/concerns/references/ratchets, 3) the
**skill** (`skills/helix/SKILL.md`). Each learning spans the buckets (spec authorizes → template/action
operationalizes → skill performs). *Rev 2 incorporates codex review.*

## The seven learnings

- **L1 — Claims-vs-reality is the dominant artifact defect** (template-conformant docs claiming
  tests/coverage/metrics that don't exist). Prototype built (uncommitted): `ASSERTED_UNBACKED` +
  phantom-claim ratchet.
- **L2 — Autonomy is first-class.** Scaffolding already exists but is *dangling*: `input.md` defines
  `low/medium/high` semantics governed by **FEAT-011 / TD-011**, which were removed in the collapse
  (823aa1ac). High autonomy must also *infer concern selection*.
- **L3 — Concerns library is the lever but was inert** (bare API, no UI, until selection forced).
- **L4 — Meta-gates exist but don't run in the loop** (`validate`/`align`/`check`).
- **L5 — Progressive `evolve` beats re-splat; convergence ≠ "reviewer says SHIP."**
- **L6 — Templates should bake in AC↔test traceability** (stable AC IDs, G/W/T, matrix, layer allocation).
- **L7a — Headless activation is phrasing-dependent** (slash inert; by-name works). **L7b — composed
  concerns should ship known friction** (bun:sqlite under `next build` → `bun --bun`).

---

## Bucket 1 — docs/ spec updates

| # | Change | File(s) | Done when |
|---|--------|---------|-----------|
| L2 | **Restore FEAT-011 (slider-autonomy) + TD-011** to resolve the dangling refs (`input.md:16`, CONTRACT-002 recorded hash, CONTRACT-001). Keep the existing **`low/medium/high`** vocab + semantics; **extend** with: concern-inference at high autonomy, resolution precedence, hard-stop invariant, and explicit "autonomy changes checkpoint density, never collapses the 7-activity loop." | `docs/helix/01-frame/features/FEAT-011-slider-autonomy.md`, `docs/helix/02-design/technical-designs/TD-011-slider-autonomy-implementation.md` | both files exist; CONTRACT-002 hash re-blessed; input.md refs resolve |
| L2 | Confirm PRD autonomy goal | `docs/helix/01-frame/prd.md:97` | **already reworded** (current tree) — just verify on commit |
| L2 | ADR for the autonomy spectrum decision (cite FEAT-011/TD-011) | `docs/helix/02-design/adr/ADR-0NN-autonomy-spectrum.md` | ADR exists, cited by FEAT-011 + skill |
| L1 | **New `FEAT-016` — artifact-honesty / claims-vs-reality** (codex: split out, it's global artifact honesty not just tests). Cross-ref from FEAT-008 + FEAT-014. | `docs/helix/01-frame/features/FEAT-016-artifact-honesty.md` | FEAT exists; describes `ASSERTED_UNBACKED` + zero-floor ratchet |
| L4/L5 | Meta-gates-in-loop + evolve-default + convergence criterion | extend `FEAT-014-workflow-coverage.md` | FEAT mandates self-validation mode-gates + states convergence = "verified + finding-classes folded into gates" |
| L3 | Concern selection mandatory + propagation gate | extend `FEAT-006-concerns-practices-context-digest.md` | FEAT requires concern selection in frame + a propagation gate |
| L6 | AC↔test traceability is a template requirement | extend `FEAT-008-artifact-template-quality.md` | requires stable AC IDs + matrix + layer allocation |
| L7a | Headless activation phrasing | `docs/install/*.md`, cross-ref `FEAT-013` | install docs teach by-name activation; slash noted interactive-only |

## Bucket 2 — workflows/ template / prompt / example / action updates

| # | Change | File(s) | Done when |
|---|--------|---------|-----------|
| L1 | `ASSERTED_UNBACKED` + claims-vs-reality check (built, uncommitted) | `workflows/actions/reconcile-alignment.md` (≈:216-235) | fixture naming a nonexistent test is flagged + blocks |
| L1 | Phantom-claim zero-floor sub-ratchet (built, uncommitted) | `workflows/ratchets.md` (≈:135-144) | documented; tied to acceptance-criteria ratchet |
| L4 | Self-validation as **workflow-mode gates** (NOT literal "run validate+align+check" — avoid recursion) | `workflows/actions/implementation.md`, `evolve.md`, + `measure`/`report` actions | each names a verify-activity gate that fails on findings |
| L3 | Concern selection a required frame step + auto-infer at high autonomy; `check`/`polish` are **propagation gates only** (not selection) | `workflows/actions/frame.md`, `workflows/references/concern-resolution.md` | frame with no concerns flags; autonomy=high auto-selects; check flags missing propagation |
| L7b | Composed-concern friction + conflict handling | `workflows/concerns/react-nextjs/practices.md`, `workflows/concerns/typescript-bun/practices.md`, `workflows/references/concern-resolution.md` | bun:sqlite/next-build friction + `bun --bun` documented |
| L6 | Stable AC IDs (US-x-ACn) + Given/When/Then in user stories | `workflows/activities/01-frame/artifacts/user-stories/{template.md,prompt.md,example.md,meta.yml}` | meta `required_sections` enforce AC IDs; example shows them |
| L6 | Build on the **existing** `story-test-plan` AC-mapping (template.md:26-31); `test-plan` **aggregates** strategy — don't duplicate the story-level matrix | `workflows/activities/03-test/artifacts/{story-test-plan,test-plan}/*` | story-test-plan AC matrix strengthened; test-plan aggregates + layer allocation |
| L5 | Evolve-default + convergence criterion (**not** principles.md) | `workflows/actions/evolve.md`, `workflows/actions/fresh-eyes-review.md`, `reconcile-alignment.md` (or new review-integration reference) | stated + referenced from loop/review actions |

## Bucket 3 — skill (`skills/helix/SKILL.md`) — normative & mode-based only

| # | Change | Done when |
|---|--------|-----------|
| L2 | Autonomy section: `low/medium/high` + semantics (checkpoint density, assumption-recording, **concern-inference depth**, stack depth), **resolution precedence** (per-invocation override → artifact frontmatter / project policy → runtime default; no CLAUDE.md), hard-stop invariant, and "never collapses the 7-activity loop" | SKILL.md autonomy section; routes honor the level |
| L3 | Frame route makes concern selection prominent; at high autonomy auto-selects by inferring product nature | SKILL.md frame route + autonomy interplay documented |
| L4 | Point build/evolve/review routes at the workflow-mode self-validation gates (reference modes, **not** literal commands) | SKILL.md references the gate-bearing actions |
| L7a | **Do NOT** put runtime-specific "Skill tool_use" expectations in SKILL.md (runtime-neutrality). Activation mechanics live in `docs/install/`, `tests/install/`, FEAT-013/014; SKILL.md stays mode-based | no runtime-specific assertions added to skill body |

---

## Resolved open questions (per codex)

- **Claims-vs-reality home:** its **own FEAT-016** (global artifact honesty), cross-ref'd from FEAT-008/FEAT-014.
- **Autonomy resolution precedence:** per-invocation override → artifact frontmatter / project policy → runtime default. **No CLAUDE.md dependency.**
- **Autonomy vocab:** reuse existing **`low/medium/high`** (input.md/REFERENCE/EXECUTION) — do not introduce a new vocabulary.
- **Evolve/convergence home:** the `evolve`/`fresh-eyes-review`/`reconcile-alignment` actions (or a new review-integration reference), **not** `workflows/principles.md`.

## Sequencing & dependencies

- **Phase 0 (commit what's built):** L1 ratchet (`reconcile-alignment.md` + `ratchets.md`) + PRD `:97` (already reworded). Re-bless ddx hashes; commit.
- **Phase 1 (honesty + meta-gates):** L1 (new FEAT-016, fixture, enforcement) + L4 (mode-gates). Highest leverage.
- **Phase 2 (autonomy):** L2 — restore FEAT-011/TD-011 (reconcile CONTRACT-002 hash + input.md), extend with concern-inference + precedence + loop invariant → SKILL.md autonomy section. Foundational for L3.
- **Phase 3 (concerns):** L3 (depends on L2) + L7b.
- **Phase 4 (templates):** L6 (independent; builds on story-test-plan).
- **Phase 5 (activation + convergence policy):** L7a (install/tests/FEAT, folds into the live integration-test epic) + L5.

## Invariants

- Runtime neutrality: autonomy + concern signals in runtime-neutral artifacts (frontmatter/project policy), never CLAUDE.md; **no runtime-specific assertions in the skill body**.
- High autonomy changes checkpoint density only — never collapses the seven-activity loop (enforce in FEAT-011/ADR/skill).
- Every change keeps the full repo gates green (the repo test suite / `just test` + `git diff --check`, not only `tests/validate-skills.sh`) and re-blesses the ddx review hashes it touches.

*codex verdict on rev 1: SOUND-WITH-CHANGES; this rev 2 incorporates all top-3 must-fixes + bucket-fit notes.*
