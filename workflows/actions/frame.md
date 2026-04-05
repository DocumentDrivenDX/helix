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
Key sections: mission statement, vision, target market, value propositions,
product principles, success metrics, non-goals.

### PRD

Follow the template at `workflows/phases/01-frame/artifacts/prd/`.
Key sections: problem & goals, users & scope, requirements (P0/P1/P2),
functional requirements, constraints & assumptions, risks, success criteria.

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
