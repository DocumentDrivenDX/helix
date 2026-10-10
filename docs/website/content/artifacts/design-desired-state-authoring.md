---
title: "Desired-state authoring: goal and approach"
slug: design-desired-state-authoring
weight: 400
activity: "Design"
source: "02-design/design-desired-state-authoring.md"
generated: true
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

> **Source identity** (from `02-design/design-desired-state-authoring.md`):

```yaml
ddx:
  id: helix.design.desired-state-authoring
  authoring:
    home: repo
  links:
    - helix.prd
    - helix.principles
```

# Desired-state authoring: goal and approach

## Scope and assumptions

HELIX documents define the intended system and the reasons for consequential
choices. A useful specification is complete before its implementation exists.
Execution status belongs to the runtime work tracker. Repository history
belongs to source control; HELIX documents contain no pull-request numbers,
repository revision identifiers, or delivery-history citations.

## Technical Approach

Each sentence contributes a requirement, decision, action, explanation, or
necessary example. Use canonical terms and name the actor. Put conditions before
actions and give each procedural step one principal action. Preserve obligation,
permission, uncertainty, and exceptions. This is plain technical English, not a
claim of compliance with a controlled-language standard.

Ordinary authoring reads the target and the authorities needed to resolve the
requested change. Follow a relationship only when its content can affect that
change. Align compares the affected documents; implementation assessment is an
explicit, scoped audit. An accepted decision establishes direction, not a claim
that the decision has been implemented.

Architecture and contracts state the operative choices. ADRs retain significant
rationale, with obsolete decisions excluded from routine context. Templates
require only content necessary to understand and use the artifact. Optional
sections can be omitted without N/A entries. Reviews do not automatically create
new gates, documents, work items, or machine-readable reports.

Factual reports still need evidence such as measurements, test results, and
observations. They do not maintain a second execution ledger. Release versions
identify distributions; database transaction semantics remain technical content.

## Component Behavior

| Component | Required behavior |
|---|---|
| Routing skill and workflow contracts | Bound context reads and follow-up actions to the request; preserve explicit audits |
| Artifact catalog | Describe desired outcomes and relevant rationale without delivery bookkeeping |
| Project documents and shared guidance | Apply the same distinction between intent, observations, and execution status |
| Validators and evaluation fixtures | Check useful requirements and requested output shapes, not mandatory ceremony |

## Design Rules

- Keep template structure in templates, authoring instructions in prompts, and
  review criteria in metadata.
- Retain repetition only when a consumer would otherwise miss a necessary rule.
- Preserve artifact identities and technical requirements.
- Moving text into mandatory references is not a reduction. Shorter output is
  useful only when requirements, exceptions, and evidence remain clear.

## Acceptance Criteria

- A small requirement edit consults relevant authorities and stops after the
  requested coherent change; unrelated ADRs require no implementation audit.
- An accepted, unimplemented decision is a valid specification.
- An explicit implementation audit reports missing behavior without weakening
  the specification or inserting implementation status into it.
- Conversational review needs no machine report; a requested structured report
  remains available to runtimes and evaluation consumers.
- Active documents and catalog examples contain no repository-history citations;
  transaction terminology, release versions, and content digests remain valid.
- Narrow, complex, missing-prerequisite, and conflicting-authority scenarios
  each produce the shortest output that keeps requirements, exceptions, and
  evidence clear.

## Risks

Older action procedures and evaluation fixtures can silently reinstate removed
requirements. Reconcile them with the mode contracts. Broad text replacement
can damage technical meaning; inspect matches before changing them.

## Migration & Rollback

Keep artifact paths and identifiers stable. Regenerate derived catalog pages
from their source files. If behavior regresses, restore the affected rule and
its focused check without reinstating unrelated bookkeeping.
