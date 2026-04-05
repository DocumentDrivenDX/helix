# HELIX Action: Evolve

You are threading a new requirement through the project's artifact stack.

Your goal is to take a requirement — a feature request, constraint change,
spec amendment, incident learning, or customer feedback — and propagate it
through the governing documents, detect conflicts with existing work, create
properly triaged tracker issues for implementation, and produce a structured
evolution report.

This action modifies governing artifacts. Treat every write with the same
care as a production code change.

## Action Input

You receive:

- A requirement description (natural language or structured)
- Optional: `--scope` to limit blast radius (e.g., `area:wal`, `SD-017`)
- Optional: `--artifact` to target a specific governing artifact
- Optional: `--from` to indicate the requirement source (incident, feedback, etc.)

## Authority Order

When artifacts disagree, use this precedence:

1. Product Vision
2. Product Requirements
3. Feature Specs / User Stories
4. Architecture / ADRs
5. Solution Designs / Technical Designs
6. Test Plans / Tests
7. Implementation Plans
8. Source Code / Build Artifacts

Update higher-authority documents FIRST, then propagate downward. Never
update a lower-authority artifact in a way that contradicts a higher one.

## PHASE 0 — Bootstrap

0. **Load active design principles** following `workflows/references/principles-resolution.md`.
   Use these as scoping guidance when evaluating which artifacts need updates
   and how to resolve judgment calls. Note: `helix evolve` reads principles
   but never modifies the principles file — only `helix frame` may write it.
0a. **Load active concerns and practices** following `workflows/references/concern-resolution.md`.
   Concern context affects the scope of downstream changes — a requirement that
   implies a technology change may need an ADR before implementation.
0b. **Context digest**: When `helix evolve` creates or modifies beads, it must
   assemble a context digest per `workflows/references/context-digest.md` and
   prepend it to the bead description.

## PHASE 1 — Requirement Analysis

Parse the input requirement:

1. Identify the core change — what capability, constraint, or behavior is
   being added, changed, or removed.
2. Classify the type: new feature, amendment, constraint, policy change,
   incident remediation.
3. Assess scope: which subsystems, interfaces, and data models are affected.
4. If the requirement is ambiguous, state your interpretation explicitly
   and proceed. Do not halt for clarification on things you can reasonably
   infer.

## PHASE 2 — Artifact Discovery

Search the project's doc tree for governing artifacts in scope:

1. Read `AGENTS.md` for the project's artifact structure.
2. Search for artifacts that reference the affected subsystems, interfaces,
   or capabilities.
3. Build an ordered list of artifacts to review, highest authority first.
4. For each artifact, note its current state and the section(s) that will
   need updating.
5. **If the evolution will create new numbered artifacts**, load the relevant
   meta.yml files and determine the next available IDs now — before writing
   anything:
   - **New feature spec (FEAT-NNN)**: read
     `workflows/phases/01-frame/artifacts/feature-specification/meta.yml`,
     scan `docs/helix/01-frame/features/FEAT-*.md`, set next FEAT ID = max + 1
     (use `001` if none exist).
   - **New solution design (SD-NNN)**: read
     `workflows/phases/02-design/artifacts/solution-design/meta.yml`,
     scan `docs/helix/02-design/solution-designs/SD-*.md`, set next SD ID =
     max + 1.
   - **New technical design (TD-NNN)**: read
     `workflows/phases/02-design/artifacts/technical-design/meta.yml`,
     scan `docs/helix/02-design/technical-designs/TD-*.md`, set next TD ID =
     max + 1.
   - Record these values. Use them exclusively when assigning IDs; never guess
     or reuse an existing number.

Use commands like:
- `find docs/ -name "*.md" | xargs grep -l "keyword"`
- `ddx bead list --json` to find related open issues

## PHASE 3 — Conflict Detection

For each affected artifact:

1. Read the relevant sections.
2. Check whether the new requirement contradicts existing content.
3. Check whether the new requirement conflicts with open tracker issues.
4. For each conflict found, record:
   - Artifact and section
   - What the artifact currently says
   - What the requirement asks for
   - Whether the conflict is resolvable by reasonable interpretation or
     requires human decision

Conflicts that require human decision are flagged but do NOT halt the
entire evolution. Proceed with non-conflicting artifacts.

## PHASE 4 — Artifact Evolution

For each non-conflicting artifact, in authority order (highest first):

1. Read the current document.
2. Draft the amendment — add, modify, or extend the relevant sections.
3. Validate the amendment does not contradict any higher-authority artifact
   that was already updated in this session.
4. For any **new** artifact being written (not an update to an existing file):
   - Confirm the ID was assigned from the scanned-next-ID computed in Phase 2,
     not guessed.
   - Inspect the dun frontmatter `depends_on` list. For each referenced ID,
     verify the target artifact exists on disk before writing. If a target is
     missing, either remove the dependency or stop and request guidance. Never
     write an artifact with a broken `depends_on` reference.
5. Write the update.
6. If the project uses acceptance manifests (`.acceptance.toml`), update
   those too with new or modified acceptance criteria.
7. If the update touches acceptance artifacts, set
   `NIFLHEIM_ACCEPTANCE_CHANGE=1` before committing.

Keep amendments minimal and scoped. Do not rewrite sections that aren't
affected by the requirement.

## PHASE 5 — Issue Decomposition

Create tracker issues for the implementation work implied by the updated
artifacts:

1. For each updated artifact, determine what code changes are needed.
2. Create issues that are individually implementable in one `helix build`
   cycle.
3. Each issue must pass triage validation:
   - `--labels helix,phase:build,...`
   - `--spec-id` pointing to the updated artifact
   - `--acceptance` with deterministic criteria
4. Set `--parent` if the issues belong to an existing epic.
5. Group related issues under a new epic if the requirement implies
   multiple implementation slices.

## PHASE 6 — Dependency Wiring

Search existing open issues for overlap with the new issues:

1. `ddx bead list --status open --json` to get the current queue.
2. For each new issue, check if existing issues touch the same files,
   subsystems, or acceptance criteria.
3. Add dependencies with `ddx bead dep add` where ordering matters.
4. If the new requirement supersedes an existing issue, mark it with
   `ddx bead update <id> --superseded-by <new-id>`.

## PHASE 7 — Evolution Report and Commit

1. Commit all artifact changes with a message referencing the requirement.
2. Push to the remote.
3. Output a structured report:

```
## Evolution Report

### Requirement
[summary of the requirement]

### Artifacts Updated
- [artifact]: [what changed]

### Artifacts Skipped (Conflicts)
- [artifact]: [conflict description — what needs human resolution]

### Issues Created
- [id]: [title] (spec-id: [ref], deps: [ids])

### Dependencies Wired
- [new-id] depends on [existing-id]: [reason]

### Open Conflicts Requiring Human Resolution
- [description with specific artifact references]
```

4. Output the required trailer:

```
EVOLUTION_STATUS: COMPLETE|CONFLICTS|BLOCKED
ARTIFACTS_UPDATED: [count]
ISSUES_CREATED: [count]
CONFLICTS: [count]
```

`COMPLETE` means all artifacts updated and issues created with no conflicts.
`CONFLICTS` means some artifacts were skipped due to conflicts that need
human resolution, but non-conflicting work was completed.
`BLOCKED` means the requirement fundamentally contradicts the project's
governing artifacts and cannot proceed without human decision.
