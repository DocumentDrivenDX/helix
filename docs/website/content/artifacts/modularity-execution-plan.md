---
title: "Modularity and Encapsulation Execution Plan"
slug: modularity-execution-plan
weight: 480
activity: "Build"
source: "04-build/modularity-execution-plan.md"
generated: true
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

> **Source identity** (from `04-build/modularity-execution-plan.md`):

```yaml
ddx:
  id: helix.plan.modularity-encapsulation
  authoring:
    home: repo
```

# Modularity and Encapsulation Execution Plan

## Scope

Implement the operator-requested baseline: every project with handwritten source explicitly designs module ownership, encapsulation, and dependency boundaries before feature implementation. Governing artifacts: `docs/helix/01-frame/features/FEAT-006-concerns-practices-context-digest.md`, `FEAT-008-artifact-template-quality.md`, `FEAT-011-slider-autonomy.md`, and `workflows/references/concern-resolution.md`. Extend those requirements where needed rather than silently contradicting optional concern selection.

## Shared Constraints

- HELIX remains runtime-neutral methodology, templates, and validation; project import checkers belong in adopting projects, not a new universal HELIX language analyzer.
- Add a composable `modularity-and-encapsulation` baseline for handwritten source, including libraries, at all autonomy levels. Architecture style stays optional and signal-selected; no forced Clean/Hexagonal pattern.
- Architecture owns durable module/dependency rules; Contracts own exact shared interfaces; technical designs reference and apply them. Tiny projects may use one module and an explicit absence of integrations. Source-free projects record non-applicability. Preserve FEAT-008 backward compatibility: legacy Architecture instances without Module Boundaries remain structurally valid, but source work is not execution-ready until adoption evidence is added. New templates include the section; when present its evidence is mechanically checked.
- Existing concern documents are not silently overwritten. Missing baseline is a blocking readiness finding with an explicit adoption task. Bounded adoption/checker work may execute before the floor exists; dependent feature work may not. Exceptions name owner, exact scope, authority, rationale, alternative verification, and a review/removal trigger; widening baselines or exceptions to hide new debt is prohibited. Existing violations are individually recorded; unchanged debt can be baselined, but new violations fail.
- The baseline avoids outlawing pure libraries in the core. Classify domain types/invariants separately from service orchestration and integration representations. Pure domain types should be isolated; a classic-layered project may deliberately accept persistence coupling under its style, recorded in the boundary map. Do not silently impose inversion or require a composition root where classic-layered allows local construction; always document the construction policy. Integration ownership and minimal exports still apply. Export the smallest useful API, protect invariants and mutable state, prohibit cycles unless an explicit justified exception is recorded.
- Project overrides may adapt mechanisms, but cannot silently erase baseline evidence: departures require a scoped exception with governing authority, rationale, and alternative verification. Preserve unrelated operator edits by working from origin/main in an isolated worktree. Do not alter marker scope. Source catalog changes are explicitly authorized by the operator.

## Implementation Slices

| Slice | Area | Depends On | Files / Result | Validation Gate |
|---|---|---|---|---|
| M1 | concern policy | None | New concern/practices; FEAT-006 and concern resolution select baseline at all levels and handle existing/source-free projects | python3 tests/test_modularity.py |
| M2 | design contracts | M1 | Architecture template/prompt/meta/example include Module Boundaries and validate evidence when present using a new module_boundaries automated rule in skills/helix/scripts/validate-instance.py; TD, implementation-plan, test-plan prompts require application and checker sequencing; preserve interface authority | python3 scripts/helix_validate_artifact_meta.py; bash tests/validate-instance.sh |
| M3 | workflow propagation | M1, M2 | Frame/Genesis (applicability only; Genesis remains ready for Frame), Design, Polish, Check, Build/review/alignment enforce baseline and readiness; one shared reference prevents divergent rules | python3 tests/test_modularity.py; bash tests/validate-actions.sh |
| M4 | verification and publication | M1–M3 | Regression tests wired into just test; generated graph/reference/site refreshed using canonical generators | just test; git diff --check; pre-commit |
| M5 | review and landing | M4 | Astra Ultra implementation review, fixes, PR, green required CI, merge preserving commits | reviewer findings disposition and GitHub checks |

## Issue Decomposition

The slices above are the bounded direct-implementation work units; no queue drain is authorized. Each depends on the preceding policy/design contract and carries its validation gate. Polish outcome: M1 targets workflows/concerns/modularity-and-encapsulation/{concern,practices}.md, workflows/references/concern-resolution.md, and FEAT-006; M2 targets the architecture catalog quartet, technical-design/implementation-plan/test-plan prompts and templates; M3 targets mode contracts and associated action prompts plus Build GATE.yaml/input-gates.yml/enforcer.md; M4 targets tests/test_modularity.py, justfile, .github/workflows/test.yml, and generated reference pages. Each slice is bounded by its table gate and the explicit exclusions above. Apply Polish to refine this plan after the Astra review; create tracker items only if required by the repository or requested by the operator.

## Validation Plan

Add failing regression coverage before implementation. Prove source projects at low/medium/high autonomy and libraries are covered; source-free projects can declare N/A; existing selections produce adoption findings instead of silent mutation. Exercise the real instance validator: complete tiny architecture passes, legacy missing section remains structurally valid but workflow readiness blocks; present-but-empty or incomplete boundary section fails; boundary ownership/allowed+forbidden dependencies/integration owner/wiring/check command are required evidence. Policy/workflow tests verify propagation but do not claim to analyze an adopting project's imports. Include a small adopting-project demonstration that a forbidden import fails its checker and allowed imports pass, clearly identified as a fixture rather than a production universal analyzer. Run `just test`, `python3 scripts/helix_validate_artifact_meta.py`, `git diff --check`, and enabled pre-commit hooks. Do not weaken unrelated gates or skip known failures; diagnose environment limitations separately.

## Risks and Rollbacks

| Risk | Response | Rollback |
|---|---|---|
| Mandatory concern conflicts with previous optionality | Amend governing selection requirements and resolver together; record adoption findings for existing projects | Revert feature commits normally |
| Architecture ritual burdens tiny projects | One-row map; explicit no integration/wiring needed; no mandated rings or interface per function | Simplify required evidence without dropping ownership |
| Prose-only rules create false assurance | Distinguish structural instance checks from semantic review and project-local import enforcement; negative controls | Repair specific check, never claim semantic guarantees from regex |
| Generated changes obscure source | Run canonical generators and inspect output; no unrelated generated edits | Regenerate from reverted source |

## Exit Criteria

- Astra Ultra plan review findings are resolved: classic-layered compatibility explicit; legacy validation additive with readiness migration; module_boundaries automated rule checks real evidence; exception precedence and adoption escape path explicit. Reviewer confirms dispositions before implementation.
- Baseline and artifact/workflow obligations agree; examples validate.
- Regression checks prove missing boundary evidence is rejected and adopting-project checker negative control works.
- Full validation and enabled hooks pass; implementation review issues are resolved.
- PR is merged only with green required CI and intact history; report merge commit and review evidence.

## Execution Evidence

Plan review: Astra Ultra requested revisions; all four findings and both refinements were resolved and the revised plan cleared. Implementation review: Astra Ultra identified three P2 issues and one consistency refinement; all were fixed and verified. Review records are adjacent to this plan.

Validation completed: 13 modularity regression tests; 55 artifact schemas; all 55 catalog examples; full `just test`; `git diff --check`; and `lefthook run pre-commit --all-files`. The deck lane was rerun with bundled pptxgenjs and passed geometry/raster checks; its additional external PPTX validator was unavailable locally. The local Innsigle lane skipped because its optional CLI was unavailable; remote Website CI is the landing gate for website checks. Policy assertions verify methodology propagation, not runtime agency; structural checks verify populated evidence, not semantic truth.

No tracker was mutated or queue work dispatched. The implementation remains on an isolated branch so unrelated operator changes are preserved. Landing requires green PR checks and a plain fast-forward; no squash or rebase.
