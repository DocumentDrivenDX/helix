# HELIX Action: Frame

You are creating or refining the highest-authority artifacts in the HELIX
stack: product vision, PRD, feature specifications, and user stories.

These documents govern everything downstream — designs, tests, implementation,
and deployment. Treat every decision here as load-bearing.

## Action Input

You may receive:

- no argument (default: frame the whole project)
- a scope such as `auth`, `payments`, `mobile`

## Authority

Frame-activity artifacts sit at authority levels 1-3:

1. Product Vision (level 1)
2. Product Requirements / PRD (level 2)
3. Feature Specs / User Stories (level 3)

These govern all downstream work. Do not contradict existing higher-level
artifacts unless the scope explicitly asks you to revise them.

## STEP 0 — Bootstrap

0. **Load active design principles** following the principles-resolution
   reference for this runtime. Use them to shape requirements priorities. If no
   project principles file exists, note that you will bootstrap one as part of
   this frame action.
0a. **Concern selection is a required Frame step.** Load or initialize active
   concerns following the concern-resolution reference for this runtime. A frame
   pass is not complete until concerns are selected (or it is explicitly
   recorded that no concerns apply) — shipping feature specs with no concern
   decision is a framing gap, not an acceptable default-empty state (FEAT-006
   FR-14). If `docs/helix/01-frame/concerns.md` does not exist, resolve the
   selection by autonomy level (see `input.md` autonomy semantics and FEAT-011):
   - **`low` / `medium`**: drive concern selection interactively — ask the user
     per category (tech stack, data, infrastructure, quality) and create the
     concerns document alongside other Frame artifacts.
   - **`high`**: **infer** the concern selection from the product's nature
     (e.g. a web app implies a tech-stack + frontend + `a11y-wcag-aa` concern; an
     API service implies tech-stack + `o11y-otel` + `security-owasp`), write
     `concerns.md`, and record each inferred concern as an assumption rather than
     pausing to ask. Never overwrite an existing `concerns.md` by inference;
     detect conflicts among inferred concerns per `concern-resolution.md`.

   Concern selections inform feasibility, constraints, and deployment sections of
   the PRD and feature specs. Selection happens here, once; propagation to work items
   is a later **gate** owned by `check`/`polish`, not a re-selection.

## STEP 1 — Discovery

1. Read existing Frame-activity artifacts:
   - `docs/helix/00-discover/product-vision.md`
   - `docs/helix/01-frame/prd.md`
   - `docs/helix/01-frame/features/FEAT-*.md`
   - `docs/helix/01-frame/concerns.md` (if it exists)
2. Read the artifact templates for product vision, PRD, feature specifications,
   and concerns from the runtime's artifact catalog under
   `activities/00-discover/artifacts/product-vision/`,
   `activities/01-frame/artifacts/prd/`,
   `activities/01-frame/artifacts/feature-specification/`, and
   `activities/01-frame/artifacts/concerns/`.
3. Load numbering rules and determine the next artifact ID:
   - Read the feature-specification meta.yml to understand the ID format
     (`FEAT-{number}`), naming pattern, and reuse policy.
   - List all files matching `docs/helix/01-frame/features/FEAT-*.md`.
   - Extract the numeric portion from each filename, find the maximum N, and
     set **next FEAT ID = N + 1** (use `001` if no files exist yet).
   - Record this value; it is authoritative for every feature spec created in
     this session. Do not guess or reuse an existing number.
4. Identify what exists, what's missing, and what needs updating for the
   requested scope.

## STEP 0.5 — Work Item Acquisition

Before creating or modifying any artifacts, acquire a governing work item for
this frame pass to record progress and govern changes. See the runtime's
work-item acquisition reference for the full pattern.

## STEP 2 — Draft

For each missing or outdated artifact:

1. Use the template structure as a guide
2. Draft the content based on:
   - Existing code and docs (if this is an existing project)
   - The user's scope description
   - Industry best practices for the domain
3. Be specific: name target users, state measurable goals, define concrete
   requirements, set explicit non-goals

### Product Vision

Follow the template from the product-vision artifact directory. Read both
`template.md` (structure) and `prompt.md` (section-by-section guidance and
quality checklist) before drafting.

Key sections: mission statement, positioning, vision, user experience, target
market, value propositions, product principles, success metrics, why now,
non-goals.

### PRD

Follow the template from the prd artifact directory. Read both `template.md`
(structure) and `prompt.md` (section-by-section guidance and quality checklist)
before drafting.

Key sections: summary (standalone 1-pager), problem & goals, success metrics,
non-goals, users & scope, requirements (P0/P1/P2), functional requirements,
acceptance test sketches, technical context, constraints & assumptions, risks,
open questions, success criteria.

### Feature Specs

For each major capability, create
`docs/helix/01-frame/features/FEAT-NNN-<name>.md` using the **next FEAT ID**
determined in Step 1 (incrementing by one for each additional spec created
in the same session). Do not pick an ID by guessing — only use the scanned
value.

Before writing each feature spec, validate any `depends_on` entries in its
frontmatter:
- Each dependency ID must resolve to an existing artifact on disk (e.g.,
  `prd.md` for a spec that depends on the PRD).
- If a target does not exist, either remove the dependency or stop and
  request guidance before writing the file. Never write an artifact whose
  `depends_on` references a non-existent target.

Key sections: overview, problem statement, functional requirements,
non-functional requirements, user story references, edge cases, success
metrics, constraints, dependencies, out of scope.

User stories are referenced by ID — do not duplicate story content in the
feature spec. Stories are separate files with their own lifecycle.

### User Stories

Follow the template from the user-stories artifact directory. Read both
`template.md` and `prompt.md` before drafting.

For each vertical slice, create `docs/helix/01-frame/user-stories/US-NNN-<slug>.md`.
One file per story. Key sections: story statement, context, walkthrough,
acceptance criteria (Given/When/Then), edge cases, test scenarios with
concrete values, dependencies, out of scope.

User stories are stable design artifacts — tracker issues reference them, not
the other way around. Write them to last across multiple implementation cycles.

## STEP 3 — Iterative Refinement

For each drafted artifact, perform 3-5 rounds of self-critique:

1. Challenge every assumption
2. Check for missing requirements, edge cases, and failure modes
3. Verify non-goals actually exclude what they should
4. Ensure success metrics are measurable
5. Check that feature specs cover the PRD requirements
6. Verify user stories have deterministic acceptance criteria

### Vision-specific critique

If you drafted or updated the product vision, also check:

1. **Positioning**: Does the "For [target]" name a findable group of people?
   Does "Unlike [alternative]" name something real? If either is vague, the
   positioning isn't done.
2. **Vision**: Does it describe an end state or just a market position? "We
   will be the leading X" is a goal, not a vision.
3. **User Experience**: Could someone build a prototype from this scenario? If
   it reads like marketing copy, rewrite it as a usage walkthrough.
4. **Target Market**: Would you know where to find these customers? If "Who"
   is broad enough to include everyone, it's too broad.
5. **Success Definition**: Can you name the tool or process that measures each
   metric? If not, the metric isn't measurable yet.
6. **Why Now**: Does it cite a specific, observable change? "AI is improving"
   is not specific. Name what changed and when.

### PRD-specific critique

If you drafted or updated the PRD, also check:

1. **Problem**: Does it describe a failure mode or just the absence of your
   product? "Users don't have X" is weak. Quantify the pain.
2. **Goals**: Are they state changes or activities? "Build a dashboard" is an
   activity, not a goal.
3. **Success Metrics**: Does every metric have a numeric target and a named
   measurement method? If either is missing, the metric isn't usable.
4. **Non-Goals**: Would someone on the team plausibly argue for including each
   excluded item? If not, the non-goal is a strawman.
5. **P0 Requirements**: Could someone write an acceptance test for each one?
   If not, it's too vague to be P0.
6. **Personas**: Are they specific enough to find a real person who matches?
   Generic roles with generic pain points are templates, not personas.
7. **Risks**: Does every mitigation name a concrete action? "Monitor closely"
   is not a mitigation.
8. **Markers**: Search for `[TBD]`, `[TODO]`, `[NEEDS CLARIFICATION]`. None
   should remain outside the Open Questions section.
9. **Acceptance Test Sketches**: Does every P0 have a scenario with inputs and
   expected outputs? Could an implementer write a passing test from the sketch
   alone?
10. **Technical Context**: Are versions specific? Could an implementer set up
    the dev environment from this section alone? Note: Technical Context
    records current stack decisions; it does not make them. Stack selection
    decisions and their rationale belong in ADRs. If a choice here conflicts
    with or isn't yet backed by an ADR, flag it in Open Questions.
11. **Open Questions**: Are unresolved items collected here instead of buried
    as markers? Does each question name who can answer and what's blocked?

### Feature-spec-specific critique

If you drafted or updated a feature spec, also check:

1. **Overview**: Does it link to a specific PRD requirement (P0-N, P1-N)?
   "Improves the user experience" is not a link.
2. **Functional Requirements**: Is each one independently testable? Could
   someone write an acceptance test from the requirement alone?
3. **Non-Functional Requirements**: Does every NFR have a specific numeric
   target? "Must be fast" is not a requirement.
4. **User Stories**: Are stories referenced by ID with links, not duplicated
   inline? Stories are separate governing artifacts.
5. **Dependencies**: Are feature IDs and external systems named specifically?
   "Depends on auth" is too vague.

### User-story-specific critique

If you drafted or updated user stories, also check:

1. **Persona**: Does "As a" name a specific persona from the PRD? "As a user"
   is not specific enough.
2. **Action vs. system behavior**: Does "I want" describe what the user does,
   not what the system does internally?
3. **Value**: Does "So that" name a measurable outcome? "So that I can use
   the feature" is circular.
4. **Walkthrough**: Could a QA engineer use it as a manual test script? Does
   it trace one complete path from trigger to outcome?
5. **Acceptance Criteria**: Is each criterion a single Given/When/Then? Split
   compound criteria into separate items.
6. **Test Scenarios**: Do they include concrete values, not placeholders? Could
   an implementer copy them into a test file?
7. **Stability**: Is this story written to last? It will be referenced by
   multiple tracker issues across design, build, and test activities.

### Validation gate

After refinement, read `meta.yml` (specifically the `validation.quality_checks`
section) and `prompt.md` from each artifact directory you touched. Verify all
**blocking** quality checks pass. If any fail, revise the artifact before
proceeding to Step 4. Do not commit an artifact that fails a blocking check.
See ADR-004 for why validation rules live in `meta.yml` rather than a separate
`dependencies.yaml`.

## STEP 3.5 — Principles Bootstrap (if needed)

If no `docs/helix/01-frame/principles.md` exists for this project:

1. Present the HELIX defaults from the runtime's principles file to the user.
2. Ask:
   - "What does your project value most?"
   - "What trade-offs do you consistently lean toward?"
   - "What past mistakes should these principles help you avoid?"
3. Synthesize user input and defaults into a project principles document.
4. Check for tensions between principles using the principles-resolution
   reference for this runtime.
5. Write `docs/helix/01-frame/principles.md`.

Skip this activity if the principles file already exists.

## STEP 4 — Work Item Creation

Create work items for Design-activity work implied by the framing:

- One work item per feature spec that needs a solution design
- Label with `helix,activity:design`
- Set `spec-id` to the feature spec ID
- Set acceptance criteria to "solution design exists and covers feature requirements"

## STEP 5 — Output

Write all artifacts to their canonical locations and commit.

## STEP 6 — Measure

Verify the frame pass against the governing work item's acceptance criteria.
See the measure action for the full pattern.

1. **Artifact completeness**: All required artifacts for the scope have been
   created or updated.
2. **Validation gates**: All blocking quality checks from `meta.yml`
   (`validation.quality_checks`) and `prompt.md` pass for each artifact.
3. **Work item creation**: Downstream design work items have been filed for
   each feature spec.
4. **Concern selection (required)**: verify concern selection was performed —
   `docs/helix/01-frame/concerns.md` exists with an active selection (or an
   explicit "no concerns apply" record). At high autonomy, verify inferred
   concerns are recorded as assumptions. Verify consistency with artifact
   content. A frame pass that produced feature specs but no concern decision
   fails this gate.
5. **Record results** on the governing work item via the runtime-provided work-item source.

## STEP 7 — Report

Close the frame cycle and feed back into the planning cycle. See the report
action for the full pattern.

1. If measurement passed, close the governing work item with evidence summary.
2. If validation gates failed or guidance is needed, create follow-on items.
3. The design work items created in Step 4 are the primary downstream output —
   they enter the planning cycle for design and polish.

Report:
1. Artifacts created or updated
2. Key decisions made
3. Open questions requiring stakeholder input
4. Work items created for downstream work
5. Measurement results

```
FRAME_STATUS: COMPLETE|GUIDANCE_NEEDED
ARTIFACTS_CREATED: N
ARTIFACTS_UPDATED: N
ITEMS_CREATED: N
MEASURE_STATUS: PASS|FAIL|PARTIAL
ITEM_ID: <governing-item-id>
FOLLOW_ON_CREATED: N
```

## Runtime Integration Appendix

This appendix covers how a runtime realizes the frame action. The reference
paths and work-item acquisition below are runtime-neutral; for the concrete
commands of a specific runtime, see its install guide (DDx:
[docs/install/ddx.md](../../docs/install/ddx.md)).

### STEP 0 — Reference resolution

- Principles: `workflows/references/principles-resolution.md`
- Concerns: `workflows/references/concern-resolution.md`
- Defaults principles file: `workflows/principles.md`
- Feature-specification meta: `workflows/activities/01-frame/artifacts/feature-specification/meta.yml`
- Product-vision template: `workflows/activities/00-discover/artifacts/product-vision/`
- PRD template: `workflows/activities/01-frame/artifacts/prd/`
- User-stories template: `workflows/activities/01-frame/artifacts/user-stories/`
- Concerns template: `workflows/activities/01-frame/artifacts/concerns/`

### STEP 0.5 — Work-item acquisition

Acquire the governing work item before modifying files, per
`workflows/references/bead-first.md`: find an open planning item labelled
`kind:planning,action:frame` (claim it if found) or create one with labels
`helix,kind:planning,action:frame`, a `<context-digest>` description naming the
scope and existing artifacts, and acceptance "Artifacts created/updated per type
requirements; downstream design issues filed; validation gates pass". The
runtime supplies the work-item store; for the concrete commands see its install
guide ([docs/install/ddx.md](../../docs/install/ddx.md) for DDx).

### Action input examples

```
helix frame
helix frame auth
helix frame "real-time notifications"
```

### Output trailer

```
FRAME_STATUS: COMPLETE|GUIDANCE_NEEDED
ARTIFACTS_CREATED: N
ARTIFACTS_UPDATED: N
ISSUES_CREATED: N
MEASURE_STATUS: PASS|FAIL|PARTIAL
ITEM_ID: <governing-item-id>
FOLLOW_ON_CREATED: N
```
