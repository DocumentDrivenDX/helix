---
title: "Build Plan: Requirement-linked verification"
slug: plan-2026-10-12-requirement-test-verification
weight: 540
activity: "Build"
source: "04-build/plan-2026-10-12-requirement-test-verification.md"
generated: true
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

> **Source identity** (from `04-build/plan-2026-10-12-requirement-test-verification.md`):

```yaml
ddx:
  id: plan-2026-10-12-requirement-test-verification
  authoring:
    home: repo
```

# Build Plan: Requirement-linked verification

## Scope

Replace HELIX's mandatory shared verification-evidence file with verification
through existing requirement/test mappings, test-source citations and observed
run results. Separate evidence applies only to observations outside the normal
test/reporting path. Preserve runtime, negative-branch and downstream-consumer
verification strength. This is a methodology change in the HELIX repository;
DDx already consumes its own structured verification mappings and is unchanged.

Governing artifacts:
- `docs/helix/01-frame/features/FEAT-008-artifact-template-quality.md` FR-6: story-level AC/test ownership.
- `docs/helix/01-frame/features/FEAT-010-testing-strategy-templates.md` FR-6/8/9:
  coverage floor, observed runtime evidence and canonical citations.
- `docs/helix/01-frame/features/FEAT-016-artifact-honesty.md`: factual completion
  claims must resolve to actual tests and measurements.
- `workflows/concerns/testing/`: layer selection and real-surface harnesses.
- `workflows/concerns/verification/`: observed outcomes before completion.
- Story Test Plan catalog: existing mappings and canonical `@covers` citations.

## Shared Constraints

- Keep the existing automated tests-passing check and manual acceptance review;
  do not invent an executable semantic gate or imply HELIX ships a gate runner.
- Requirement IDs stay stable; test names describe behavior and conditions.
  Prefer source comments/annotations for citations; existing canonical citations
  in test bodies, names or doc comments remain valid. No wholesale test renames.
- Existing story test plans own mappings. Use existing Notes/Executable Proof
  fields and normal run reports; no new mandatory matrix, schema or artifact.
- A mapped/cited test is not proof it exists, meaningfully asserts the criterion,
  ran, or passed. Skipped, stale, failed and missing runs cannot prove completion.
- Run references identify the tested revision (and dirty diff if relevant),
  command, status, environment and scope. Prefer existing CI/runtime metadata.
  Retention must keep accepted evidence accessible; expired evidence is unknown.
- Automated real-surface tests may capture full runtime evidence. Supplemental
  records are conditional on a proof gap, not on task size or implementation type.
- Libraries/docs use applicable suites/builds; runtime exceptions still require
  scope, rationale, owner/review and strongest observed substitute evidence.
- Preserve old evidence and links. Stop new mandatory appends; no bulk migration,
  generated index, union merge rule, runtime tooling, tracker mutation or release.

## Implementation Slices

| Slice | Scope | Depends On | Validation Gate |
|---|---|---|---|
| B-001 | Update FEAT-008 authority; define portable verification storage/traceability and naming contract | None | Astra Ultra plan review; check scope and existing citation syntax |
| B-002 | Update verification/testing concerns, Build gate/enforcer, STP and test-suite guidance, UX/metering/formal references and review/alignment consumers | B-001 | No live mandatory shared-file refs; runtime/guard/consumer requirements retained |
| B-003 | Add focused contract regression tests; regenerate public reference docs and required packaged projections | B-002 | New tests, full `just test`, generated-content validation and diff check |
| B-004 | Astra Ultra implementation review; fix findings and revalidate; commit, push and create PR | B-003 | No unresolved blocking findings; PR attached to chat |

## Execution Contract

The user explicitly authorized planning, Astra Ultra review, implementation,
second review and PR creation. Work on an isolated branch from main; preserve
unrelated changes. No merge or release is authorized. Token estimate is unknown;
no spending ceiling was specified. Review uses Astra with ultra reasoning.

## Continuation Evidence

Astra Ultra plan review: no blocking findings. Folded in FEAT-010 authority,
legacy citation compatibility and precise Build gate scope. B-001 through B-003
are implemented. Astra Ultra implementation review: APPROVE, no blocking or
warning findings; independently reran all five contract tests. Addressed its
closeout note by replacing the pending status here.

Observed validation on the branch diff from `479ce8a2`: `just test` exited 0
under `uv run --offline --with pyyaml` (UV cache in a temporary directory).
The optional deck-render lane skipped because pptxgenjs is unavailable; all
other lanes passed, with the Innsigle lane separately rerun using its pinned
verifier and a temporary npm cache (exit 0). `just check-website-links` exited 0:
63,883 internal links/images resolved across 386 pages. `git diff --check`
passed. Generated-content freshness will be checked after committing, because
its validator compares projections against HEAD. B-004 review is complete;
commit/push/PR publication remain the final steps. The PR owns publication and
CI status. These catalog checks do not claim consumer runtime verification.
Record review dispositions and final validation here or in the PR's existing
validation summary. Do not create a generic verification diary.

## Validation Plan

- Review with Astra Ultra before implementation; fold in material findings.
- Contract tests reject mandatory monolithic storage and lost traceability,
  runtime proof, run provenance, conditional supplements and naming guidance.
- Update source before generated docs; use repository reference generator.
- Run `just test`, `bash tests/validate-website-generated.sh`, and
  `git diff --check`; diagnose failures without disabling checks.
- Review completed diff with Astra Ultra; resolve material findings and rerun
  affected checks. Inspect the PR's CI after publication.

## Risks and Rollbacks

| Risk | Response | Rollback |
|---|---|---|
| Removing storage requirement weakens proof | Preserve assertion/source/result review and runtime requirements | Revert methodology change |
| CI artifacts expire or cover wrong revision | Require retained accessible provenance; mark unknown until rerun | Use existing durable closeout location |
| Generated guidance reintroduces old rule | Generate from canonical source and scan live references | Regenerate fixed source |
| Legacy links break | Preserve existing files and historical references | No historical migration |

## Exit Criteria

- Existing mappings/citations/results suffice for ordinary automated verification.
- Behavior-based naming and stable citation examples are clear and portable.
- Supplemental evidence is conditional and linked from existing owning records.
- No live guidance mandates `verification-evidence.md` or a replacement file.
- Runtime/guard/downstream proof and reviewed exceptions remain required.
- Required validations pass and Astra Ultra review findings are resolved.
- Changes are committed and a PR is created; its URL is attached to this chat.
