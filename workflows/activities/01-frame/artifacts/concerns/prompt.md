# Concerns Selection Prompt

Guide the user through selecting project concerns from the library and
declaring any project-specific concerns or overrides.

## Purpose

Project Concerns declare the cross-cutting context that should travel with
downstream work. Their unique job is to keep recurring technology, quality,
data, security, UX, operations, and convention guidance attached to the areas
where it matters.

Concerns are not principles. Principles guide judgment when two valid options
compete. Concerns name active domains whose practices must be considered during
design, test, implementation, and review. Concerns are not ADRs either: an ADR
records a specific decision, while a concern keeps the resulting practices
available to future work.

## Reference Anchors

Use these local resource summaries as grounding:

- `docs/resources/microsoft-azure-well-architected-framework.md` grounds
  cross-cutting quality and operational concerns as actionable practices,
  risks, and tradeoffs.
- `docs/resources/sei-quality-attribute-scenarios.md` grounds quality
  attributes as concrete scenarios and practices, not bare labels.

## Approach

1. Inspect the Product Vision, PRD, Principles, architecture notes, existing
   repository structure, dependencies, deployment files, and current concern
   library at `workflows/concerns/`.

2. List available concerns from `workflows/concerns/`
   grouped by category. Include project-local candidate concerns only when the
   repo clearly has a recurring cross-cutting domain that the library does not
   cover.

3. For each category, infer what you can from the repo and ask only for
   unresolved choices:
   - Tech stack: "What language, runtime, and package manager does this
     project use?"
   - Data: "What database or data layer?"
   - Infrastructure: "Where will this deploy?"
   - Quality: "Do you need accessibility (a11y), internationalization (i18n),
     or observability (o11y) support?"

4. For each selected concern:
   - State why it is active for this project.
   - Declare the area labels where it applies.
   - Capture the key practices that downstream work needs.
   - If overriding library practices, cite the governing ADR when available.
   - If no ADR exists for a significant override, mark it as needing an ADR.

5. Declare the project's area labels — which `area:*` labels will work items use?
   The default set is: `ui`, `api`, `data`, `infra`, `cli`.

6. Check for practice conflicts between selected concerns and resolve them.

7. Write `docs/helix/01-frame/concerns.md`.

## Key Rules

- Concerns are composable. Selecting multiple is normal and expected.
- A concern must be active. Do not include a domain just because it is
  generally good practice.
- Project overrides adapt library mechanisms subject to the source-code baseline
  evidence floor and scoped exception contract in
  `workflows/references/concern-resolution.md`.
- Every override should reference a governing ADR when possible.
- The area taxonomy declared here controls which concerns are injected
  into which work items via `<context-digest>`.
- If a concern describes product behavior, move it to the PRD or a feature
  spec.
- If a concern records a one-time technical choice, move it to an ADR.
- If a concern describes build order, move it to the implementation plan.

## Source-Code Baseline

Apply the all-autonomy source-code baseline in
`workflows/references/concern-resolution.md`: select
`modularity-and-encapsulation` for handwritten source, including libraries and
single-file tools, with selection source `baseline-policy`. For source-free work
record the reason. Existing selections require an explicit adoption update;
missing baseline is a readiness gap, not permission to overwrite selections.

## Observability Applicability

For `o11y-otel`, record applicable practice sections in the existing Why Active /
Key Practices fields: service signals, agent run diagnostics, frontend/data
boundaries, and/or GenAI operations. Agent development need not involve a
model-calling product. These notes are not new slots or profile fields. Select
on a real diagnostic surface and apply service-only obligations conditionally;
a development runner can supply evidence for a static site or library.
