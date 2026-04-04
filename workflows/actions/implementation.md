# HELIX Action: Implementation

You are performing one bounded HELIX execution pass against the built-in
tracker (`helix tracker`).

Your goal is to choose one ready execution issue, implement it completely
without drifting from the authoritative planning stack, satisfy all applicable
project quality gates, create any necessary follow-on issues, commit the work
with explicit issue traceability, close the issue, and exit.

This action is intentionally bounded. In single-issue mode, it handles one issue
and exits. In batch mode, the supervisor provides a list of related issues to
implement sequentially within one session — claim each, implement, verify, close,
then move to the next. Batch mode saves context-loading cost when issues share
the same governing artifacts.

When the ready queue drains, the external supervisor should run
`workflows/actions/check.md` instead of continuing blindly.

## Action Input

You may receive:

- no argument
- an explicit issue ID
- a scope selector such as `US-042`, `FEAT-003`, `area:auth`, or `phase:deploy`

Examples:

- `helix build`
- `helix build <id>`
- `helix build US-042`
- `helix build area:auth`

If no argument is given, choose the best ready HELIX execution issue.

## Authority Order

When artifacts disagree, use this order:

1. Product Vision
2. Product Requirements
3. Feature Specs / User Stories
4. Architecture / ADRs
5. Solution Designs / Technical Designs
6. Test Plans / Tests
7. Implementation Plans
8. Source Code / Build Artifacts

Rules:

- Higher layers govern lower layers.
- Tests govern build execution but do not override requirements or design.
- Source code reflects current state but does not redefine the plan.
- If an issue conflicts with its governing artifacts, do not implement the drift.
- Prefer aligning code and docs to plan. Only propose plan changes when the
  evidence is strong and the governing artifacts are stale or incomplete.

## Tracker Rules

Use the built-in tracker only. Follow:

- See `helix tracker --help` for tracker conventions

Issues are stored in `.ddx/beads.jsonl`.

This action works only on execution issues. Exclude review issues by default.

Eligible issues are ready (no unresolved blockers) and represent execution work
rather than review work.

Do not claim or implement `phase:review` issues with this action.

## Core Principle

Do the work. The goal is continuous forward progress on real implementation.

Select the issue most likely to close cleanly in this run. Prefer straightforward
tasks with clear acceptance criteria. When given an epic, decompose it into
subtasks and implement the first one — decomposition IS implementation work.

Hard problems should be attacked, not deferred. If the toolchain doesn't compile,
try to fix it. If the spec is ambiguous, make the best-effort interpretation
consistent with the authority order and document your reasoning. Only bail when
there is a genuine contradiction between governing artifacts that you cannot
resolve, or an intractable technical problem after real effort.

"Not safe to execute as written" is almost never the right conclusion. The right
conclusion is usually: do the part that IS safe, create follow-on issues for the
rest, and close the issue.

## PHASE 0 - Bootstrap

0. **Context Recovery**: Re-read AGENTS.md so project instructions are fresh
   in your working memory. After long sessions, context compaction may have
   dropped critical project rules. This step is cheap insurance against drift.
1. Verify the built-in tracker is available.
   - If `helix tracker status` fails, stop immediately.
2. Inspect the current git worktree.
   - Do not revert unrelated changes.
   - If unrelated changes create commit risk, isolate your issue changes rather
     than cleaning the tree destructively.
3. Load project quality and completeness gates.
   - Read relevant HELIX guidance such as `workflows/phases/04-build/enforcer.md`
     and any repo-specific CI, lint, test, security, or release rules.
   - Load ratchet floor fixtures if the project has adopted quality ratchets
     (see `workflows/ratchets.md`). Note the current floors so Phase 7
     can compare against them.

## PHASE 1 - Candidate Discovery

Determine the candidate set:

1. If the input is an explicit issue ID:
   - inspect only that issue
2. If the input is a scope selector:
   - search ready HELIX execution issues matching the selector
3. If no input is given:
   - inspect ready HELIX execution issues, excluding `phase:review`

Use tracker commands such as:

- `helix tracker ready`
- `helix tracker show <id>`
- `helix tracker dep tree <id>`

## PHASE 2 - Candidate Ranking

Rank candidates deterministically.

Prefer, in order:

1. explicit user-selected issue
2. unblocked issue with the clearest governing artifacts
3. issue on or near the critical path because other issues depend on it
4. issue whose acceptance criteria are specific and locally verifiable
5. smallest coherent slice likely to finish cleanly in one run

De-prioritize (but do not automatically reject) when:

- governing artifacts are thin — try to infer intent from the authority stack
- acceptance criteria are broad — scope down to the clearest slice and implement that
- the issue is an epic — decompose into subtasks and implement the first one

Reject only when:

- the issue directly contradicts a higher-authority governing artifact and the
  contradiction cannot be resolved by reasonable interpretation
- the issue is truly a planning or decision task that requires human input

When an issue seems too hard or too broad, the right response is to decompose it
into smaller pieces, implement the easiest piece, and create follow-on issues for
the rest. Do not bail just because the full scope is large.

If genuinely no candidate can make forward progress, report what is blocked and
why with specific artifact references. Exit cleanly so the supervisor can run
the queue-health check.

## PHASE 3 - Claim And Context Load

For the selected issue:

1. re-read the selected issue immediately before claim:
   - `helix tracker show <id> --json`
   - verify the issue is still ready, still executable, and has not drifted
     materially in `spec-id`, dependencies, parentage, or other governing
     metadata
   - if it drifted materially, do not claim it from stale assumptions; return
     to candidate selection or stop with the blocker
2. claim it with `helix tracker update <id> --claim`
3. inspect:
   - issue fields and labels
   - `spec-id`
   - parent epic or parent issue
   - dependency tree
   - acceptance text
   - related story, feature, or area labels
4. load the governing artifacts referenced by:
   - `spec-id`
   - issue description
   - parent issue or epic
   - linked user story, feature, design, or test artifacts
5. determine the work phase from labels:
   - `phase:build`
   - `phase:deploy`
   - `phase:iterate`

## PHASE 4 - Pre-Execution Validation

Before editing code or docs, validate:

- the issue is still ready and unblocked
- the governing artifacts provide enough context to make reasonable progress
- there is no direct contradiction between higher-authority artifacts

If context is thin but not contradictory:

- make the best-effort interpretation consistent with the authority order
- document your interpretation in the commit message
- implement the clearest slice of the work
- create follow-on issues for anything that needs further clarification

Only stop implementation when:

- governing artifacts directly contradict each other at the same or higher
  authority level AND the contradiction cannot be resolved by project vision
  and principles
- the issue requires a human decision (e.g., product direction, API contract
  change) that the agent cannot make

"Underspecified" is not a reason to stop. Underspecified means: scope down to
what IS specified, implement that, and create follow-on issues for the rest.

## PHASE 5 - Phase-Appropriate Execution

### `phase:build`

Follow Build-phase discipline strictly:

- implement only what is needed to satisfy the governing tests and artifacts
- do not change test expectations just to make the issue pass
- do not add unspecified features
- keep changes scoped to the issue
- refactor only after verification is green

### `phase:deploy`

Follow Deploy-phase discipline strictly:

- execute rollout, release, monitoring, and runbook work only within the issue scope
- do not expand product behavior or sneak in implementation changes unrelated to deployment safety
- verify rollback and observability expectations where required

### `phase:iterate`

Follow Iterate-phase discipline strictly:

- limit changes to documented cleanup, lessons, backlog, or metrics work
- do not turn iterate work into hidden feature implementation
- capture concrete follow-on execution issues when new work is discovered

## PHASE 6 - Follow-On Issue Capture

If execution reveals additional work, decide whether to absorb or split:

**Absorb into the current issue** when the follow-on work is:

- small (< 30 minutes, < 100 lines changed)
- directly adjacent to what you already changed (same file, same module)
- a doc/manifest update triggered by the code you just wrote (e.g., promoting
  an acceptance criterion in the TOML after implementing the feature)
- a test update for the code you just changed

Absorbing small adjacent work reduces issue churn and keeps the tracker
meaningful. The goal is one issue per coherent unit of work, not one issue
per observation.

**Create a new follow-on issue** when the work is:

- in a different subsystem or crate than the current issue
- a newly discovered bug unrelated to the current change
- a design or architecture change that needs its own review
- large enough to be its own implementation cycle (> 1 hour estimated)
- blocked on something the current issue can't resolve

When creating follow-on issues:

- make them atomic and deterministic
- set `spec-id` to the nearest governing artifact
- add the correct HELIX labels
- encode blockers with `helix tracker dep add`

## PHASE 7 - Verification

Run verification scoped to what you changed, not the full workspace.

**Scope verification to changed crates and files.** If you changed files in
two crates, run clippy, tests, and fmt on those two crates — not the entire
workspace. The pre-commit hooks handle full workspace verification on commit,
so you do not need to duplicate that work. This saves significant time and
token cost.

At minimum, verify:

- the issue acceptance criteria are satisfied
- relevant tests pass in the changed crates/packages
- lint, format, or static analysis passes on the changed crates/packages
- docs/config/runbooks are updated where required
- ratchet enforcement commands pass if the project has adopted quality ratchets
  (see `workflows/ratchets.md`). If a ratchet auto-bump is triggered,
  include the updated floor fixture in the issue commit.

If the repository defines canonical verification wrappers or proof lanes, use
those wrappers for closure evidence. Narrower package or file commands are for
debugging after the canonical lane fails; they do not replace the maintained
closure surface.

If verification fails:

- fix the problem within the issue scope, or
- leave the issue open with a precise status note and follow-on issues if needed

Do not commit broken work as a completed issue.

If a canonical verification run contradicts a previously closed issue, do not
leave that issue green. Reopen it immediately or create a linked regression issue
that records the exact contradictory command, date, exit status, and reviewed
artifacts.

## PHASE 7.5 - Self-Review

Before committing, perform one quick fresh-eyes review:

1. Re-read the issue acceptance criteria.
2. Re-read the complete diff you are about to commit.
3. For each changed function, ask: "If I were reviewing this code for the
   first time, what would I flag?"
4. Check for: unclosed resources, missing error handling, hardcoded values
   that should be configuration, TODO comments that should be follow-on issues,
   test assertions that are too loose or tautological.

If issues are found, fix them before proceeding to Phase 8.

## PHASE 8 - Commit, Gate, Push, And Close

If the issue is complete:

1. re-read the selected issue immediately before close:
   - `helix tracker show <id> --json`
   - verify it has not been superseded or materially drifted while execution
     was in progress
   - if it drifted materially, do not close it from stale assumptions; stop,
     reopen the decision path, or create the required follow-on issue
2. review the diff for scope discipline
3. create a comprehensive commit that references the issue ID
4. include in the commit message:
   - issue ID
   - concise summary
   - governing artifact references where helpful
   - verification summary
5. **ACCEPTANCE CHECK**: Before committing, verify the issue's acceptance
   criteria are satisfied. If the issue has a `spec-id`, find the matching
   acceptance manifest (e.g., `TP-SD-010.acceptance.toml`) and verify:
   - Each criterion the issue claims to satisfy is marked `active` or `satisfied`
   - The referenced test or evidence actually exists and passes
   - If acceptance scripts exist (`scripts/check-acceptance-traceability.sh`,
     `scripts/check-acceptance-coverage.sh`), run them
   Do not close an issue whose acceptance criteria are not verifiably met.
6. **PRE-PUSH GATE**: Before pushing, run the project's full quality gate.
   This is CRITICAL because agent sandboxes may bypass pre-commit hooks.
   - If the project has `lefthook`: run `lefthook run pre-commit`
   - Otherwise: run the project's canonical build check (e.g., `cargo check
     --workspace`, `npm test`, or whatever AGENTS.md defines as the gate)
   - If the gate fails: fix the issue, amend the commit, and re-run the gate.
     Do NOT push broken code. Do NOT skip this step.
   - The scoped verification in Phase 7 catches most issues, but this
     full-workspace gate catches cross-crate and cross-module breakage
     that scoped checks miss (e.g., trait/impl mismatches across files).
7. push to remote: `git pull --rebase && git push`
8. close the issue with `helix tracker close <id>`

If the worktree contains unrelated changes, commit only the files that belong to
the issue. Never revert unrelated work just to simplify the commit.

## PHASE 9 - Output

Report:

1. Selected Issue
2. Why It Was Chosen
3. Governing Artifacts
4. Work Completed
5. Follow-On Issues Created
6. Verification Performed
7. Commit Created
8. Final Issue Status
9. Open Risks Or Decisions

Be precise and deterministic.
