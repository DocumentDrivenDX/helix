# HELIX Action: Polish Issues

You are performing iterative issue refinement before implementation begins.

"Check your issues N times, implement once."

Your goal is to improve issue quality through multiple refinement passes:
deduplication, coverage verification against the plan, acceptance criteria
sharpening, dependency correction, and convergence detection. This front-loaded
investment prevents expensive rework during implementation.

## Action Input

You may receive:

- no argument (default: all open issues)
- a scope such as `auth`, `FEAT-003`, `phase:build`
- `--rounds N` controlling maximum refinement passes (default: 6)

Examples:

- `helix polish`
- `helix polish auth`
- `helix polish --rounds 10 FEAT-003`

## Tracker Rules

Use the built-in tracker only. Follow:

- See `helix tracker --help` for tracker conventions

Issues are stored in `.helix/beads.jsonl`.

## PHASE 0 - Load Current State

0. **Context Recovery**: Re-read AGENTS.md so project instructions are fresh
   in your working memory. After long sessions, context compaction may have
   dropped critical project rules. This step is cheap insurance against drift.
1. Verify the built-in tracker is available.
   - If `helix tracker status` fails, stop immediately.
2. Load all open issues for the scope.
   - `helix tracker list --status open --json`
   - `helix tracker list --status in_progress --json` (if relevant to scope)
3. Load the governing plan document if one exists.
   - Check `docs/helix/02-design/plan-*.md` for the scope
   - Check other planning artifacts (PRD, feature specs, architecture docs)
4. Record initial issue count and state as the baseline.

## PHASE 1 through N - Refinement Passes

Each pass performs ALL of the following checks. Track changes made per pass.

### Deduplication

- Find issues with overlapping scope, description, or acceptance criteria.
- Merge duplicates into a single canonical issue that preserves the strongest
  elements of each.
- When merging, preserve all dependency relationships from both issues.
- Close the redundant issue with a note pointing to the canonical one.

### Plan Coverage Verification

- If a plan document exists, verify every section has at least one issue.
- If a section has no issue, create one with proper labels, spec-id, and
  acceptance criteria derived from the plan.
- If an issue exists but doesn't map to any plan section, flag it for review.

### Acceptance Criteria Sharpening

- Replace vague criteria with testable statements.
  - Bad: "auth should work correctly"
  - Good: "login with valid credentials returns 200 and a JWT; login with
    invalid credentials returns 401 with error code AUTH_INVALID"
- Ensure every issue has at least one concrete acceptance criterion.
- Add verification method: what command or test proves this criterion is met?

### Dependency Verification

- Verify dependency chains are correct: if issue A depends on issue B, does B
  actually produce what A needs?
- Look for missing dependencies: does this issue assume work that hasn't been
  captured as a dependency?
- Look for circular dependencies and break them.
- Verify `spec-id` points to the correct governing artifact.

### Sizing

- Flag issues that are too large for a single bounded implementation pass.
  An issue is too large if it touches more than 3 files in different subsystems
  or requires more than one architectural decision.
- Split oversized issues into smaller, independently verifiable slices.
- Preserve the dependency ordering when splitting.

### Label Hygiene

- Ensure every issue has the `helix` label.
- Ensure every issue has exactly one phase label (`phase:build`, `phase:deploy`,
  or `phase:iterate`).
- Ensure area labels are present where applicable.
- Ensure `kind:*` labels match the issue's actual type.

## Convergence Detection

Track a change count per round: number of issues modified, created, or merged.

When change count drops below 3 for two consecutive rounds, declare convergence
and stop refinement.

If max rounds is reached without convergence, report the current state and
recommend additional rounds or user guidance.

## Output

Report a summary of all modifications made across rounds, then these trailer
lines:

```
POLISH_STATUS: CONVERGED|IN_PROGRESS
POLISH_ROUNDS: N
ISSUES_MODIFIED: count
ISSUES_CREATED: count
ISSUES_MERGED: count
```

- `CONVERGED`: change velocity dropped below threshold
- `IN_PROGRESS`: max rounds reached but velocity still above threshold
