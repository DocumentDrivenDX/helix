# Plan — it.36: bidirectional spec↔code traceability gate + spec-is-the-contract principle

**Status:** draft (pre codex-review, both ends)
**Date:** 2026-05-26
**Branch:** helix-self-improvement-2026-05-24
**Builds on:** it.26 (AC→test), it.37 (PRD subsystem→FEAT→story decomposition)

## Problem (operator-queued "traceability gap review")

HELIX traceability is **one-directional**: it.26 enforces spec→code (every AC has a
citing `@covers` test) and it.37 enforces within-spec decomposition (subsystem→FEAT
→story). There is **no enforced code→spec direction**: a code *surface*
(endpoint/route/screen/CLI command/public capability) with no governing FEAT/FR/AC
is "code outside spec" — currently only informally noted in reconcile STEP 3
("major unplanned code paths", "dead or orphaned implementations"). And the
**principle** — the spec is the contract and the unit of cross-implementation
comparison/reproduction — is stated nowhere.

The operator's reframe: *"Why are agents implementing code outside specs? Why
isn't it obvious that cross-implementation comparison starts with specs?"* Now
that it.37 makes spec stacks **alignable**, it.36 makes the spec↔code mapping
**bidirectional and enforced**, so untraced code is no longer unguarded.

## Design (recommended; crux flagged for codex + operator)

1. **Formalize code→spec in reconcile STEP 3.** Enumerate the material code
   **surfaces** (already partly listed: runtime entry points, public interfaces,
   routes/endpoints, screens/pages, CLI commands, build/deploy surfaces) and
   require each to **map to a governing FEAT/FR/AC**. A surface with no governing
   spec is a **"code outside spec"** finding (advisory→blocking @ ready, the it.26
   pattern). Generalizes the existing "major unplanned code paths" note into a
   structured check.
2. **Pair explicitly with spec→code** (it.26 AC→test + it.37 subsystem→FEAT→story)
   and state the gate is **BIDIRECTIONAL**: `code-outside-spec` AND
   `spec-without-impl` are both drift. Add a "Bidirectional Traceability" framing
   to STEP 3 / the Acceptance Criteria Validation section.
3. **State the PRINCIPLE** (in `workflows/principles.md` and referenced from
   reconcile-alignment): *the spec is the contract and the unit of
   cross-implementation comparison and reproduction; code is a projection of the
   spec.* Best-effort spec evolution is not reproducible.
4. **Runtime-neutral.** reconcile-alignment is an agent action reading `docs/` +
   the code tree; it does not assume a tracker/ddx. The surface→spec mapping is
   done by the REVIEW (no new code-annotation convention) — see crux.

### CRUX (for codex-review + operator steer)
**How does code→spec get established?**
- **(A) Review-mapping (recommended).** The reconcile review inspects surfaces and
  maps each to a governing artifact; an unmappable surface is a finding. No code
  annotations required. Consistent with how it.26/it.37 enforce (review reads
  artifacts). Lowest authoring burden; mapping is the reviewer's judgment.
- **(B) Code annotations.** Require surfaces to cite their spec in-code (e.g.
  `@implements FEAT-002` / `@implements FR-7`), symmetric with the `@covers`
  test-citation. Machine-checkable + reproducible, but imposes an annotation
  burden on all surface code and a new convention.
- Default to (A); (B) is heavier (possible future hardening if (A) proves
  unreliable). Also: blocking-vs-advisory strength, and what granularity counts as
  a "surface" (per-route? per-module? per-capability?).

## Over-engineering guard (YAGNI / DOWITYTD)
- Generalizes existing STEP 3 "unplanned code paths" + it.26/it.37; no new
  artifacts, no new exit-gate, no code-annotation convention (under option A).
  Test "would this make sense with no ddx?" — yes (reconcile-alignment review +
  a principle statement).

## Validation
- Validators green (validate-skills/install-consistency/state-rules/context-digests);
  re-bless stamped docs; SKILL.md ddx-neutral preserved.
- Re-bench cross-harness: a surface with no governing spec/AC trips the code→spec
  finding; an AC with no citing test still trips spec→code (it.26); the principle
  is stated and referenced.

## codex-review (both ends, per practice)
- Review THIS plan before implementing (esp. the crux: review-mapping vs
  annotations; false-positive risk on framework-generated/boilerplate surfaces).
- Review the DIFF after implementing.

## codex PLAN-review outcome — SOUND-WITH-FIXES (2026-05-26); crux resolved → A + mapping table
1. **Crux resolved: keep default A (review-mapping), NOT `@implements`.** Lower
   burden, runtime-neutral, language-agnostic, no stale comments. Reproducibility
   comes from a **required surface inventory + mapping TABLE in the reconcile
   output**, not annotations. `@implements` = optional future hardening if review
   mapping proves noisy.
2. **Narrow "material surface"**: externally-observable/lifecycle-significant —
   routes/endpoints, screens/pages, CLI commands, public APIs, event consumers/jobs,
   domain migrations, behavior-altering flags/config, deploy/runtime surfaces.
   EXCLUDE generated/vendor/build output, framework plumbing, passive wrappers,
   default config, unexposed scaffolding.
3. **Don't force every surface → FEAT/FR/AC**: product capabilities → FEAT/FR/AC;
   technical/operational surfaces → ADR, technical-design, concern, deployment-
   checklist, runbook, or data-design. (Avoids health-check/migration/layout false
   positives.)
4. **Scope blocking to ready-for-handoff/review/merge**; mid-iteration scaffolding
   advisory. Add a **"temporary scaffold" disposition** — allowed only when
   unexposed/disabled and tied to a planned resolution.
5. **Generalize, don't parallel**: replace STEP 3's loose "major unplanned code
   paths" + "dead/orphaned implementations" bullets with a structured
   **"Bidirectional Traceability"** subsection + surface-map rows.
6. **Fix runtime-neutrality claim**: reconcile bootstrap still assumes a tracker —
   make a **report-only mode valid when no tracker exists** (or weaken to
   "runtime-vendor-neutral, tracker-backed follow-up when available").
7. **Surface-map row fields** (makes A reproducible): surface ID/name, file/path
   evidence, kind, governing artifact ID, mapping rationale, classification,
   disposition.
8. **Principle "Spec Is The Contract" in `workflows/principles.md`** + a short
   **SKILL.md** Align/Build pointer (code is a projection of the governing artifact
   stack; unmapped material surfaces are alignment findings). Not principle-only —
   it's also a mechanic.
9. **Update the principles TEMPLATE/defaults** too, else generated
   `docs/helix/01-frame/principles.md` omit it.
10. **Use the existing taxonomy** (no vague "code outside spec" bucket): unmapped
    shipped surface = `DIVERGENT`/`UNDERSPECIFIED`; dead/orphaned = `STALE_PLAN`/
    `DIVERGENT`; legitimate boilerplate = `ALIGNED/NON_MATERIAL` with evidence.
