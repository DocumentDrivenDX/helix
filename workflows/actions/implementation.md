# HELIX Action: Implementation

You are performing one bounded HELIX execution pass against the runtime
tracker.

Your goal is to choose one ready execution work item, implement it completely
without drifting from the authoritative planning stack, satisfy all applicable
project quality gates, create any necessary follow-on items, commit the work
with explicit item traceability, close the item, and exit.

This action is intentionally bounded. In single-item mode, it handles one item
and exits. In batch mode, the supervisor provides a list of related items to
implement sequentially within one session — claim each, implement, verify,
close, then move to the next. Batch mode saves context-loading cost when items
share the same governing artifacts.

When the ready queue drains, the external supervisor should run the check
action instead of continuing blindly.

## Action Input

You may receive:

- no argument
- an explicit work item ID
- a scope selector such as `US-042`, `FEAT-003`, `area:auth`, or `activity:deploy`

If no argument is given, choose the best ready HELIX execution work item.

## Authority Hierarchy

When artifacts disagree, use this hierarchy:

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

Use the runtime-provided work-item source only.

This action works only on execution work items. Exclude review items by default.

Eligible items are ready (no unresolved blockers) and represent execution work
rather than review work.

Do not claim or implement review-activity items with this action.

## Core Principle

Do the work. The goal is continuous forward progress on real implementation.

Select the issue most likely to close cleanly in this run. Prefer straightforward
tasks with clear acceptance criteria.

**Do not decompose epics during build.** If the selected candidate is an epic
without child task items, exit cleanly so the supervisor can route to the
polish action for proper decomposition. Decomposition is planning work, not
implementation work — mixing them leads to agents skipping the breakdown and
jumping straight to code.

Hard problems should be attacked, not deferred. If the toolchain doesn't compile,
try to fix it. If the spec is ambiguous, make the best-effort interpretation
consistent with the authority hierarchy and document your reasoning. Only bail when
there is a genuine contradiction between governing artifacts that you cannot
resolve, or an intractable technical problem after real effort.

"Not safe to execute as written" is almost never the right conclusion. The right
conclusion is usually: do the part that IS safe, create follow-on issues for the
rest, and close the issue.

## STEP 0 - Bootstrap

0. **Context Recovery**: Re-read AGENTS.md so project instructions are fresh
   in your working memory. After long sessions, context compaction may have
   dropped critical project rules. This step is cheap insurance against drift.
1. Verify the runtime-provided work-item source is available. Stop immediately if unavailable.
2. Inspect the current git worktree.
   - Do not revert unrelated changes.
   - If unrelated changes create commit risk, isolate your work item changes
     rather than cleaning the tree destructively.
3. Load project quality and completeness gates.
   - Read the build-activity enforcer and any repo-specific CI, lint, test,
     security, or release rules.
   - Load ratchet floor fixtures if the project has adopted quality ratchets.
     Note the current floors so Step 7 can compare against them.
4. Load active design principles.
   - Follow the runtime's principles-resolution pattern.
   - If `docs/helix/01-frame/principles.md` exists and has content, load it.
   - Otherwise load the runtime's default principles file.
   - Apply these principles when making judgment calls throughout this task.
5. Load active concerns and practices.
   - Follow the runtime's concern-resolution pattern.
   - If `docs/helix/01-frame/concerns.md` exists, load the declared concerns and
     merged practices.
   - Use the declared concern tools, conventions, and patterns throughout
     implementation. Do not substitute alternative tools without an explicit
     project override or ADR.
6. Read the work item's context digest if present.
   - If the item description starts with a context-digest block, parse it and
     use the summarized principles, concerns, practices, ADRs, and governing
     context as your working authority.
   - If no digest exists (legacy item), rely on steps 4-5 above plus the
     item's `spec-id` to reconstruct context.

## STEP 1 - Candidate Discovery

Determine the candidate set:

1. If the input is an explicit work item ID:
   - inspect only that item
2. If the input is a scope selector:
   - search ready HELIX execution items matching the selector
3. If no input is given:
   - inspect ready HELIX execution items, excluding review-activity items

Use tracker commands to list ready items, show item details, and inspect
dependency trees.

## STEP 2 - Candidate Ranking

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

**Skip and exit** when:

- the item is an epic without child task items — this needs polish
  decomposition, not implementation. Report the epic ID and exit so the
  supervisor can route to polish.

Reject only when:

- the issue directly contradicts a higher-authority governing artifact and the
  contradiction cannot be resolved by reasonable interpretation
- the issue is truly a planning or decision task that requires human input

When an issue seems too hard or too broad, the right response is to create
follow-on issues for the parts you cannot tackle in this pass, implement the
clearest slice, and close the issue scoped to what you did. Do not bail just
because the full scope is large.

If genuinely no candidate can make forward progress, report what is blocked and
why with specific artifact references. Exit cleanly so the supervisor can run
the queue-health check.

## STEP 3 - Claim And Context Load

For the selected work item:

1. Re-read the selected item immediately before claiming:
   - Verify the item is still ready, still executable, and has not drifted
     materially in `spec-id`, dependencies, parentage, or other governing
     metadata.
   - If it drifted materially, do not claim it from stale assumptions; return
     to candidate selection or stop with the blocker.
2. Claim the item via the tracker.
3. Inspect:
   - item fields and labels
   - `spec-id`
   - parent epic or parent item
   - dependency tree
   - acceptance text
   - related story, feature, or area labels
4. Load the governing artifacts referenced by:
   - `spec-id`
   - item description
   - parent item or epic
   - linked user story, feature, design, or test artifacts
5. Determine the work activity from labels:
   - `activity:build`
   - `activity:deploy`
   - `activity:iterate`

## STEP 4 - Pre-Execution Validation

Before editing code or docs, validate:

- the issue is still ready and unblocked
- the governing artifacts provide enough context to make reasonable progress
- there is no direct contradiction between higher-authority artifacts

If context is thin but not contradictory:

- make the best-effort interpretation consistent with the authority hierarchy
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

## STEP 5 - Activity-Appropriate Execution

### `activity:build`

Follow Build-activity discipline strictly:

- implement only what is needed to satisfy the governing tests and artifacts
- do not change test expectations just to make the issue pass
- do not add unspecified features
- keep changes scoped to the issue
- refactor only after verification is green

### `activity:deploy`

Follow Deploy-activity discipline strictly:

- execute rollout, release, monitoring, and runbook work only within the issue scope
- do not expand product behavior or sneak in implementation changes unrelated to deployment safety
- verify rollback and observability expectations where required

### `activity:iterate`

Follow Iterate-activity discipline strictly:

- limit changes to documented cleanup, lessons, backlog, or metrics work
- do not turn iterate work into hidden feature implementation
- capture concrete follow-on execution issues when new work is discovered

## STEP 6 - Follow-On Issue Capture

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
- encode blockers via the runtime-provided work-item source's dependency mechanism

## STEP 7 - Verification

Run verification scoped to what you changed, not the full workspace.

**Scope verification to changed crates and files.** If you changed files in
two crates, run clippy, tests, and fmt on those two crates — not the entire
workspace. The pre-commit hooks handle full workspace verification on commit,
so you do not need to duplicate that work. This saves significant time and
token cost.

At minimum, verify:

- the work item acceptance criteria are satisfied
- relevant tests pass in the changed crates/packages
- lint, format, or static analysis passes on the changed crates/packages
- docs/config/runbooks are updated where required
- **selection↔build coherence (when `verification` is active):** the built system
  honors the **selected concerns and slots** — each selected slot's filler is
  actually used (a selected `frontend-framework: react-nextjs` ⇒ a real React/Next
  app exists, SSR/RSC fine; a selected UI slot ⇒ a core-flow whole-stack e2e ran
  green — a browser e2e for a client-rendered UI, or an HTTP+HTML-assertion e2e for
  a server-rendered one; both first-class). A selected slot the build **silently
  abandoned** (selected react-nextjs but shipped a non-React app; selected a UI
  slot but shipped no core-flow e2e at all) is a blocking defect — not a quiet
  substitution. Changing a selected stack mid-build
  is allowed only as a **recorded deviation**: update the slot/concern selection in
  `concerns.md`, give a reason tied to an acceptance constraint, update the
  verification plan, and run the substitute evidence. Honor the `verification`
  exceptions (library / docs-only / non-buildable / genuinely-infeasible e2e),
  recorded the same way. (See `workflows/concerns/verification/practices.md`.)
- ratchet enforcement commands pass if the project has adopted quality ratchets.
  If a ratchet auto-bump is triggered, include the updated floor fixture in the
  work item commit.
- **concern-declared quality gates** pass for the active concerns scoped to
  this item's area. Run the gates declared in each matched concern's practices
  under the Quality Gates section. Common examples:
  - `rust-cargo`: `cargo clippy`, `cargo fmt --check`, `cargo deny check advisories`, `cargo machete`
  - `typescript-bun`: `biome check`, `bun:test`
  - `python-uv`: `ruff check`, `ruff format --check`, `pyright`
  - `go-std`: `go vet`, `golangci-lint run`, `govulncheck`
  - `security-owasp`: the per-stack dependency audit command from the concern
  - Use project overrides from `concerns.md` when they specify alternative
    commands or additional flags. Scope gate runs to changed packages, not
    the full workspace.

If the repository defines canonical verification wrappers or proof lanes, use
those wrappers for closure evidence. Narrower package or file commands are for
debugging after the canonical lane fails; they do not replace the maintained
closure surface.

**Self-validation mode-gate (must fail on findings).** Verification is not
complete until the *verify activity* over this work yields no blocking finding.
This is a workflow-mode gate, not a literal "run validate then align then
check" command list — running those actions from inside build would recurse the
loop. Concretely, before closing the item confirm:

- every acceptance criterion the item claims is `SATISFIED`, not merely
  `UNTESTED`, and
- the **claims-vs-reality** check passes: the item and the artifacts it touched
  assert no test, coverage figure, or emitted metric that does not exist —
  `ASSERTED_UNBACKED` count is **zero** (phantom-claim zero-floor ratchet, see
  `workflows/ratchets.md` and FEAT-016).

A blocking finding here fails verification exactly like a failing test: fix it
within scope or leave the item open with a precise status note.

**Verify, don't trust a self-reported "complete."** Run the gates and read their
real output; never close an item on the strength of a status line claiming
success. An autonomous pass can report "complete" after dying mid-run (e.g. on
an API overload) — actually running verification here is what catches it. When a
gate fails for a **transient** reason (API overload, network blip, flaky
external dependency), retry it; do not record a transient error as a genuine
failure, and never paper over it with a self-asserted pass. (The bounded
operator loop driving these passes — the skill's run/worker route — re-runs
verification after each pass for the same reason.)

If verification fails:

- fix the problem within the work item scope, or
- leave the item open with a precise status note and follow-on items if needed

Do not commit broken work as a completed item.

If a canonical verification run contradicts a previously closed item, do not
leave that item green. Reopen it immediately or create a linked regression item
that records the exact contradictory command, date, exit status, and reviewed
artifacts.

## STEP 7.5 - Measure

Record verification results on the work item via the runtime-provided work-item source. See the
measure action for the full pattern.

After verification passes, record the results (timestamp, status, per-criterion
pass/fail with evidence, per-gate pass/fail, per-ratchet measured vs. floor).

If verification failed and cannot be fixed within scope, record the failure on
the work item and do not proceed to commit.

## STEP 7.6 - Self-Review

Before committing, perform one quick fresh-eyes review:

1. Re-read the work item acceptance criteria.
2. Re-read the complete diff you are about to commit.
3. For each changed function, ask: "If I were reviewing this code for the
   first time, what would I flag?"
4. Check for: unclosed resources, missing error handling, hardcoded values
   that should be configuration, TODO comments that should be follow-on items,
   test assertions that are too loose or tautological.

If issues are found, fix them before proceeding to Step 8.

## STEP 7.7 - Converge (bounded evolve-until-converged)

"Go check your work again" is not optional polish — it is the loop that drives a slice to *done*,
not to first-green. This step **orchestrates existing checks; it defines no new convergence criterion
of its own.**

**The single convergence oracle (compose the two canonical definitions; do not restate them):** a
slice is *converged* iff **both** hold —

1. `reconcile-alignment` reports its STEP 10 **Convergence criterion** met for this scope (every gap
   classified, traceability complete, zero `ASSERTED_UNBACKED`, each finding-class folded into a gate
   — including the `Concern→Artifact Realization` check), **and**
2. the `04-build` `GATE.yaml` **exit_requirements** pass — the it.39 verification evidence gate (every
   AC's real path **and** guard branch driven on the running system) plus tests/coverage/lint.

**The loop:**

1. Run `reconcile-alignment` on this work item's slice and confirm the `04-build` exit gate.
2. If the oracle holds → converged; proceed to STEP 8.
3. Else → **progressive `evolve`** (per `workflows/actions/evolve.md` and reconcile STEP 10's
   "progressive evolve, not re-splat") targeting the **specific** findings — never regenerate the
   slice — then re-run STEP 7 (Verification) and return to 7.7.1.
4. **Bounded:** cap at `CONVERGE_MAX_PASSES` (default **5**). At the cap without convergence, **STOP**:
   leave the work item **open** with an explicit **NON-CONVERGED** status note listing the unresolved
   finding-classes — never "done with caveats", never commit it as complete — and surface it to the
   operator. A bounded loop that halts with an honest non-converged state is the guarantee against
   both an infinite loop and a false "done".

Runtime: file-by-default — capture each pass's findings as the work item's evidence. Under DDx this is
**one governing "convergence attempt"** record (bead), with per-pass findings as evidence on it — not
a bead per finding.

## STEP 8 - Commit, Gate, Push, And Close

If the work item is complete:

1. Re-read the selected item immediately before closing:
   - Verify it has not been superseded or materially drifted while execution
     was in progress.
   - If it drifted materially, do not close it from stale assumptions; stop,
     reopen the decision path, or create the required follow-on item.
2. Review the diff for scope discipline.
3. Create a comprehensive commit that references the work item ID.
4. Include in the commit message:
   - work item ID
   - concise summary
   - governing artifact references where helpful
   - verification summary
5. **ACCEPTANCE CHECK**: Before committing, verify the work item's acceptance
   criteria are satisfied. If the item has a `spec-id`, find the matching
   acceptance manifest (e.g., `TP-SD-010.acceptance.toml`) and verify:
   - Each criterion the item claims to satisfy is marked `active` or `satisfied`
   - The referenced test or evidence actually exists and passes
   - If acceptance scripts exist (`scripts/check-acceptance-traceability.sh`,
     `scripts/check-acceptance-coverage.sh`), run them
   Do not close a work item whose acceptance criteria are not verifiably met.
6. **PRE-PUSH GATE**: Before pushing, run the project's full quality gate.
   This is CRITICAL because agent sandboxes may bypass pre-commit hooks.
   - If the project has `lefthook`: run `lefthook run pre-commit`
   - Otherwise: run the project's canonical build check (e.g., `cargo check
     --workspace`, `npm test`, or whatever AGENTS.md defines as the gate)
   - If the gate fails: fix the issue, amend the commit, and re-run the gate.
     Do NOT push broken code. Do NOT skip this step.
   - The scoped verification in Step 7 catches most issues, but this
     full-workspace gate catches cross-crate and cross-module breakage
     that scoped checks miss (e.g., trait/impl mismatches across files).
7. Push to remote: `git pull --rebase && git push`
8. Close the work item via the runtime-provided work-item source.

If the worktree contains unrelated changes, commit only the files that belong
to the work item. Never revert unrelated work just to simplify the commit.

## STEP 9 - Report

Close the execution cycle and feed back into the planning cycle. See the
report action for the full pattern.

1. The work item was already closed in Step 8. Verify the close comment
   includes measurement evidence.
2. Follow-on items created in Step 6 re-enter the planning cycle for polish
   and subsequent build.
3. If the work item could not be closed (verification failed, acceptance
   unmet), it remains open with measurement results recorded — the next check
   action will route it appropriately.

## STEP 10 - Output

Report:

1. Selected Work Item
2. Why It Was Chosen
3. Governing Artifacts
4. Work Completed
5. Follow-On Items Created
6. Measurement Results (PASS/FAIL/PARTIAL with evidence summary)
7. Verification Performed
8. Commit Created
9. Final Item Status
10. Open Risks Or Decisions

```
MEASURE_STATUS: PASS|FAIL|PARTIAL
ITEM_ID: <id>
FOLLOW_ON_CREATED: N
```

Be precise and deterministic.

## Runtime Integration Appendix

This appendix covers how a runtime realizes the implementation action. The
reference paths and work-item acquisition below are runtime-neutral; for the
concrete commands of a specific runtime, see its install guide (DDx:
[docs/install/ddx.md](../../docs/install/ddx.md)).

### STEP 0 — Reference resolution

- Build-activity enforcer: `workflows/activities/04-build/enforcer.md`
- Ratchets: `workflows/ratchets.md`
- Principles: `workflows/references/principles-resolution.md`
  (default: `workflows/principles.md`)
- Concerns: `workflows/references/concern-resolution.md`
- Context-digest: `workflows/references/context-digest.md`

Confirm the runtime-provided work-item source is available before proceeding; stop immediately if
it is not.

### STEP 1-2 — Candidate discovery

Use the runtime-provided work-item source to list ready execution items, show
item details, and inspect dependency trees so you can rank candidates.

### STEP 3 — Claim and load

Re-read the selected item, then claim it through the runtime-provided work-item source so
concurrent work is prevented before loading its governing artifacts.

### STEP 7.5 — Measure

Record verification results on the work item through the runtime-provided work-item source. The
recorded results should carry a timestamp, an overall PASS|FAIL|PARTIAL status,
per-criterion acceptance pass/fail with evidence, per-gate concern/command
pass/fail, and per-ratchet floor-vs-measured pass/fail.

### STEP 8 — Close

Re-read the selected item, then close it through the runtime-provided work-item source with the
evidence summary.

### Action input examples

```
helix build
helix build US-042
helix build area:auth
```

### Output trailer

```
MEASURE_STATUS: PASS|FAIL|PARTIAL
ITEM_ID: <governing-item-id>
FOLLOW_ON_CREATED: N
```

If the work item could not be closed, it remains open — the next `/helix check`
will route it appropriately.
