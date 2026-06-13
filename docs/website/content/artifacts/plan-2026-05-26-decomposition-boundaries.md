---
title: "Plan — it.37: artifact-tier decomposition boundaries (PRD ↔ FEAT ↔ story)"
slug: plan-2026-05-26-decomposition-boundaries
weight: 650
activity: "Design"
source: "02-design/plan-2026-05-26-decomposition-boundaries.md"
generated: true
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

# Plan — it.37: artifact-tier decomposition boundaries (PRD ↔ FEAT ↔ story)

**Status:** draft (pre codex-review, both ends)
**Date:** 2026-05-26
**Branch:** helix-self-improvement-2026-05-24

## Problem (bench-evidenced)

The same HubSpot brief produced three structurally **incomparable** spec stacks,
all template-passing:

| harness | FEAT specs | stories | ADRs |
|---|---|---|---|
| claude | **6** (per capability) | 13 per-file `US-NNN` | 7 `ADR-NNN-name` |
| codex | **1** mega ("CRM Delivery Console") + 67-entry parking-lot | 5 per-file | 1 lumped |
| DDx/opus | **0** — no `features/` dir (PRD → flat `user-stories.md`) | 11 in one file | 3 lowercase `adr-NNNN` |

Instrument validated (M2): the DDx skill was byte-identical to current; opus
referenced FEAT 7× and read `activities/01-frame` 10× and **still** skipped the
FEAT tier. So this is real methodology signal, not a stale/missing template.

**Root cause:** HELIX ships Boundary-Test tables + "one feature, one spec — split
two independent capabilities", but the **FEAT-vs-functional-area line is
ambiguous** — codex used `## Functional Areas` (whose own examples include
"Admin, Operator, End user, Auditor") to justify NOT splitting; DDx skipped FEATs
entirely. Gates check presence/structure, not granularity, so 0/1/6-FEAT all
pass. This is **upstream of it.36/spec-first comparison**: you cannot diff
spec-to-spec when one run's `FEAT-004-delivery-engine` is a §section inside
another's single FEAT.

## Operator-confirmed design (AskUserQuestion, 2026-05-26)

1. **FEAT fault-line = LAYERED tests.** Primary: *"Could this be prioritized,
   shipped, or cut as a unit, and carry its own success metric?"* → yes = a FEAT;
   no = a functional area within a FEAT. Tie-breaker (when the ship test is
   ambiguous): **bounded-context / aggregate root** — one FEAT per bounded
   context. Anchor: PRD `FR-n` groups (organized by subsystem) map ~1 subsystem
   → 1 FEAT.
2. **FEAT ↔ story.** FEAT = capability behavior envelope; story = one persona
   completing one goal, demonstrable end-to-end in a single flow. A FEAT has as
   many stories as it has distinct persona-goals. (Story ↔ AC already crisp.)
3. **Enforcement = guidance + reconcile check (NOT a hard exit-gate).** Sharpen
   the prose AND add advisory→blocking reconcile signals (it.26 pattern).

## Changes (runtime-neutral — no ddx assumptions)

### A. `workflows/activities/01-frame/artifacts/feature-specification/prompt.md`
- Add a **Decomposition** subsection stating the layered fault-line verbatim
  (ship/cut/metric primary; bounded-context tie-breaker; ~1 PRD-subsystem → 1
  FEAT). Add the operational split test: *if an "area" passes the ship/cut/metric
  test, it is a FEAT, not an area.*
- Fix the misleading **Functional Areas** examples: replace independent-capability
  examples ("Admin, Operator, End user, Auditor"; "Intake, Planning, Execution,
  Review, Reporting") with within-one-capability examples (a CRM feature's areas
  = Leads, Lists, Segments) + a warning callout that role/stage lists are usually
  *separate features*, not areas.
- Strengthen the existing "one feature, one spec — split two independent
  capabilities" to reference the fault-line test (make "independent" testable).

### B. `workflows/activities/01-frame/artifacts/prd/prompt.md`
- In "Functional Requirements" / "Stay in Your Lane": state the PRD owns
  **breadth** (every capability + `FR-n` + priorities) and **names the
  capability/subsystem groupings that become FEATs**; **depth** lives in FEATs.
  Add: organize FRs by subsystem so each grouping maps to a feature.

### C. `workflows/activities/01-frame/artifacts/user-stories/prompt.md`
- Tighten "One story, one vertical slice" to the confirmed phrasing: *one persona
  completing one goal, demonstrable end-to-end in a single flow.* Reaffirm
  **one file per story** (`US-NNN-<slug>.md`) — flat monolithic `user-stories.md`
  is not the per-story artifact (DDx-opus drifted here).

### D. Naming conventions (make canonical + checkable)
- Reaffirm in the relevant prompts/templates: `FEAT-NNN-<name>.md`,
  `US-NNN-<slug>.md` (one per file), `ADR-NNN-<name>.md` (uppercase, sequential,
  one per material decision). DDx-opus used lowercase `adr-NNNN` + monolithic
  stories — pin the canonical forms.

### E. `workflows/actions/reconcile-alignment.md` — add granularity signals
Alongside the existing "Decomposition coverage (FR → story)" in
`### Acceptance Criteria Validation` (coverage-floor framing, advisory→blocking):
- **FEAT granularity (mega-FEAT smell):** flag a single FEAT whose covered
  `FR-n`s span **>1 PRD subsystem grouping** — likely should split. Advisory
  finding (operator may justify a deliberately monolithic feature).
- **FEAT with 0 stories:** a feature no story references is a coverage gap
  (blocking — mirrors FR-with-no-story).
- **ADR floor (advisory):** material/hard-to-reverse decisions each warrant an
  ADR; flag when one ADR lumps multiple distinct decision-drivers. Keep advisory
  per it.25 ("expectation, not hard gate") — do not over-gate.
- **Naming/structure (advisory):** flag ADRs not matching `ADR-NNN-<name>`,
  stories not per-file `US-NNN-<slug>`.

## Over-engineering guard (YAGNI / DOWITYTD)
- No new artifacts, no new exit-gates. 3 prompt edits + advisory reconcile
  signals + naming reaffirmation. Test "would this make sense with no ddx?" — yes
  (pure artifact guidance + the existing reconcile-alignment action). The
  ship/cut/metric rule is a heuristic, not a counter — avoid hard FEAT-count
  thresholds.

## Validation
- `tests/check-workflow-paths`, `validate-plugin`, `validate-skills` green;
  SKILL.md 0 ddx maintained; re-bless reconcile-alignment + the 3 prompts if
  stamped.
- Re-bench cross-harness on the HubSpot brief: success = the 3 spec stacks become
  **alignable** (FEAT counts converge to ~one-per-capability mapping to the same
  capabilities; per-file stories; canonical ADR naming), AND a deliberately
  monolithic single FEAT trips the reconcile granularity signal.

## codex-review (both ends, per practice)
- Review THIS plan before implementing; incorporate SOUND-WITH-FIXES.
- Review the DIFF after implementing; incorporate before commit.

## codex PLAN-review outcome — SOUND-WITH-FIXES (2026-05-26), all 12 folded in
1. **(missed mode) Add blocking signal for "PRD subsystem group with no FEAT"** —
   the DDx/opus failure (0 FEATs, FRs→stories directly). Without it 0/1/6 all pass.
2. **Make subsystem grouping PARSEABLE** — canonical `### Subsystem: <name>` in the
   PRD with each `FR-n` under exactly one subsystem (replaces loose "by subsystem
   or flow"). The `FR→subsystem→FEAT` check needs structure, not scraping.
3. **Parseable FEAT coverage field** — each FEAT explicitly lists the PRD
   FRs/subsystem(s) it covers (not prose in Overview/Dependencies).
4. **Tighten ship/cut/metric** — ship/cut = "can be removed/deferred without making
   another *named* capability incoherent"; metric = a feature-level product/user
   outcome, not any local counter.
5. **Better Functional-Areas example** — "Leads, Lists, Segments" can still be
   independent capabilities; use truly subordinate areas, e.g. CSV import → "field
   mapping, validation, duplicate handling, confirmation".
6. **Mega-FEAT advisory + require justification** — advisory unless a FEAT spans >1
   PRD subsystem AND lacks a rationale that the cross-subsystem workflow IS the feature.
7. **Scope FEAT-with-0-stories blocking to "ready for downstream handoff"** — a FEAT
   may validly exist before stories during draft framing.
8. **No-tracker/read-only reconcile path** — granularity checks run as report
   findings even with no tracker (runtime-neutrality).
9. **Update TEMPLATES + checklists, not only prompts** — agents follow the concrete
   template shape: PRD, FEAT, user-story, ADR templates need the canonical grouping,
   coverage, naming, per-file requirements.
10. **Add ADR prompt storage/naming** — meta says `ADR-{n}-{name}.md` but the ADR
    prompt lacks it, so lowercase `adr-NNNN` recurs.
11. **Bench assertions for all 3 observed failures** — no `features/` dir; mega-FEAT
    spanning subsystems; monolithic `user-stories.md`; lowercase/lumped ADRs.
12. **Reconcile checks must be structural/parseable** else it is just better prose
    and harnesses still diverge while claiming compliance.

## codex DIFF-review outcome — SOUND-WITH-FIXES (2026-05-26); #1-#7 folded in, #8 scoped
Diff-review found #1-#4/#7/#8 substantially covered, #5/#6/#9-#12 partial. Applied:
- **#1** parseable `**Cross-Subsystem Rationale**` field added to FEAT template (was an
  HTML comment); reconcile reads it as the mega-FEAT split-exemption.
- **#2** fixed the FEAT prompt pointer (rationale → the new field, not "Covered PRD Requirements").
- **#3** FEAT template Functional-Areas blurb tightened to "within one capability" + caution.
- **#4** PRD template review checklist gains the `### Subsystem:` / one-FR-per-subsystem item.
- **#5** user-story template gains a Review Checklist (one file per story, one persona-goal, FEAT/FR links).
- **#6** ADR template heading `# ADR-NNN` + meta `location` token fixed (`{id}`→`{number}`, was risking `ADR-ADR-001`).
- **#7** reconcile parsing contract made exact (named header fields + case-insensitive subsystem match).
- **#8 (bench assertions) — DELIBERATELY SCOPED, not built this iteration.** The operator-confirmed
  enforcement is **guidance + reconcile check (advisory→blocking, like it.26)** — an agent-run review action,
  NOT a CI validator/fixture. The decomposition checks now live in reconcile-alignment with exact parseable
  anchors (#7), matching how it.26 (AC→test) enforces. **The assertion is the cross-harness RE-BENCH** (a
  deliberately monolithic single FEAT must trip the reconcile subsystem→FEAT / mega-FEAT signal). A
  standalone structural validator (detecting 0-FEAT / mega-FEAT / monolithic `user-stories.md` /
  lowercase-ADR from the spec files) is **optional future hardening** — warranted only if the re-bench shows
  the reconcile action does not reliably catch the failures. YAGNI per the confirmed "not a hard gate" design.
