---
title: "Frame"
slug: frame
weight: 30
generated: true
---

Generated from [`skills/helix/SKILL.md`](https://github.com/DocumentDrivenDX/helix/blob/main/skills/helix/SKILL.md), the HELIX skill. Edit the skill, not this page.

Use for creating or refining product vision, PRD, feature specs, and user
stories.

1. Read existing Frame artifacts first.
2. **Select concerns — this is a required Frame step.** A frame pass is not
   complete until the project's concerns are selected (or it is explicitly
   recorded that none apply); shipping feature specs with no concern decision is
   a framing gap, not an acceptable default-empty state. At `low`/`medium`,
   drive selection interactively by category (tech stack, data, infrastructure,
   quality). At `high`, infer the selection from the product's nature and record
   each inferred concern as an assumption. Fill each needed exclusive slot per
   §Concern slot resolution and record the chosen filler plus its source in
   `concerns.md`. Selection signals: a UI web app needs `frontend-framework`
   and `e2e-framework` (selecting the tool is not coverage — at least one core
   user flow must have a whole-stack e2e that runs green against the running
   app); an **operator-facing** product (a human manages mutable domain objects
   or lifecycle state through a UI) selects `admin-console`, with the primary
   operator workflow exercised end-to-end through the UI; an **account-based /
   multi-tenant** product selects `auth` (real signup, login/sessions,
   server-side RBAC, isolation through the principal) and fills the
   `auth-provider` slot (an external IdP is a swappable filler, never
   hardcoded). Neither is selected for pure APIs, CLIs, libraries, static
   content sites, or read-only dashboards unless an operator UI is explicitly
   required. Selection happens here, once; propagation to work items is a
   later gate owned by `check`/`polish`, not a re-selection.
3. Read the relevant artifact template, prompt, meta.yml, and active voice
   profile before drafting.
4. Keep each artifact in its lane:
   - Product Vision is direction.
   - PRD is product scope: capabilities, outcomes, priorities, metrics, and
     non-goals.
   - Feature specs are feature behavior, boundaries, edge cases, and
     decomposition.
   - User stories are vertical user journeys and observable acceptance
     criteria.
   - Contracts are exact shared interface surface: API/CLI/event/schema/config/
     telemetry/adapter commands, flags, fields, payloads, status codes, error
     semantics, versioning rules, stability rules, and examples.
   - Solution Design is the feature-level technical approach, domain model,
     component decomposition, and interface usage.
   - Technical Design is the story-level implementation design: files,
     component changes, tests, rollback, sequence, and references to governing
     Contracts.
   Exact shared interface surface belongs in Contract, not PRD, Feature Spec,
   User Story, Solution Design, or Technical Design. Those artifacts may name or
   reference the need for an interface; they do not define the normative
   surface inline.
5. Give each user-story acceptance criterion a stable `US-<n>-AC<m>` ID in
   Given/When/Then form so the story test plan can map it to tests by name.
   Decompose to a **coverage floor** (minimum rigor, not equal depth): every PRD
   functional requirement `FR-n` maps to ≥1 user story (don't bundle unrelated
   `FR-n`s without justification), and every acceptance criterion gets ≥1 test
   that *exercises* it — a named test with no relevant assertion is `UNTESTED`,
   not covered. An untested AC blocks unless a reviewed manual/non-automatable
   exception is recorded with evidence. Every covering test must **cite the AC
   ID it covers** in the canonical, parseable syntax `@covers US-<n>-AC<m>` so
   traceability is machine-checkable — an exercising, passing test that omits
   the citation is `UNCITED_COVERAGE` (fix = add the citation, not a new test),
   distinct from `UNTESTED`; a test that cites an AC it does not exercise is
   `ASSERTED_UNBACKED`. Citation is an additional gate on top of
   exercise+pass+satisfy, never a replacement.
6. Validate blocking template checks before treating the artifact as ready.
7. Create follow-up design or implementation work only after the framing
   artifact can govern it.
