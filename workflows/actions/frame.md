# HELIX Action: Frame

You are creating or refining the highest-authority artifacts in the HELIX
stack: product vision, PRD, feature specifications, and user stories.

These documents govern everything downstream — designs, tests, implementation,
and deployment. Treat every decision here as load-bearing.

## Action Input

You may receive:

- no argument (default: frame the whole project)
- a scope such as `auth`, `payments`, `mobile`

Examples:

- `helix frame`
- `helix frame auth`
- `helix frame "real-time notifications"`

## Authority

Frame-phase artifacts sit at authority levels 1-3:

1. Product Vision (level 1)
2. Product Requirements / PRD (level 2)
3. Feature Specs / User Stories (level 3)

These govern all downstream work. Do not contradict existing higher-level
artifacts unless the scope explicitly asks you to revise them.

## PHASE 0 — Bootstrap

0. **Load active design principles** following `workflows/references/principles-resolution.md`.
   Use them to shape requirements priorities. If no project principles file
   exists, note that you will bootstrap one as part of this frame action.

## PHASE 1 — Discovery

1. Read existing Frame-phase artifacts:
   - `docs/helix/00-discover/product-vision.md`
   - `docs/helix/01-frame/prd.md`
   - `docs/helix/01-frame/features/FEAT-*.md`
2. Read the artifact templates:
   - `workflows/phases/00-discover/artifacts/product-vision/`
   - `workflows/phases/01-frame/artifacts/prd/`
   - `workflows/phases/01-frame/artifacts/feature-specification/`
3. Identify what exists, what's missing, and what needs updating for the
   requested scope.

## PHASE 2 — Draft

For each missing or outdated artifact:

1. Use the template structure as a guide
2. Draft the content based on:
   - Existing code and docs (if this is an existing project)
   - The user's scope description
   - Industry best practices for the domain
3. Be specific: name target users, state measurable goals, define concrete
   requirements, set explicit non-goals

### Product Vision

Follow the template at `workflows/phases/00-discover/artifacts/product-vision/`.
Read **both** `template.md` (structure) and `prompt.md` (section-by-section
guidance and quality checklist) before drafting.

Key sections: mission statement, positioning, vision, user experience, target
market, value propositions, product principles, success metrics, why now,
non-goals.

### PRD

Follow the template at `workflows/phases/01-frame/artifacts/prd/`.
Read **both** `template.md` (structure) and `prompt.md` (section-by-section
guidance and quality checklist) before drafting.

Key sections: summary, problem & goals, success metrics, non-goals, users &
scope, requirements (P0/P1/P2), functional requirements, constraints &
assumptions, risks, success criteria.

### Feature Specs

For each major capability, create `docs/helix/01-frame/features/FEAT-NNN-<name>.md`.
Key sections: overview, problem statement, functional requirements, user
stories with acceptance criteria, non-functional requirements, constraints.

## PHASE 3 — Iterative Refinement

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
   should remain in the committed document.

### Validation gate

After refinement, read `dependencies.yaml` and `prompt.md` from each artifact
directory you touched. Verify all **blocking** quality checks pass. If any
fail, revise the artifact before proceeding to Phase 4. Do not commit an
artifact that fails a blocking check.

## PHASE 3.5 — Principles Bootstrap (if needed)

If no `docs/helix/01-frame/principles.md` exists for this project:

1. Present the HELIX defaults from `workflows/principles.md` to the user.
2. Ask:
   - "What does your project value most?"
   - "What trade-offs do you consistently lean toward?"
   - "What past mistakes should these principles help you avoid?"
3. Synthesize user input and defaults into a project principles document.
4. Check for tensions between principles (see `workflows/references/principles-resolution.md`).
5. Write `docs/helix/01-frame/principles.md`.

Skip this phase if the principles file already exists.

## PHASE 4 — Issue Creation

Create tracker issues for Design-phase work implied by the framing:

- One issue per feature spec that needs a solution design
- Label with `helix,phase:design`
- Set `spec-id` to the feature spec ID
- Set acceptance criteria to "solution design exists and covers feature requirements"

## PHASE 5 — Output

Write all artifacts to their canonical locations and commit.

Report:
1. Artifacts created or updated
2. Key decisions made
3. Open questions requiring stakeholder input
4. Tracker issues created for downstream work
