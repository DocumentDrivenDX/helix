# HELIX Action: Fresh-Eyes Review

You are performing a self-review of recently completed work, looking for bugs,
omissions, and quality issues with fresh perspective.

After implementing an issue, 1-3 review passes catch bugs that implementation
blindness misses. Each pass focuses on a different failure mode.

## Action Input

You may receive:

- no argument (default: `last-commit`)
- `last-commit` — review the most recent commit
- `commit:<sha>` — review one specific implementation commit
- a work item ID — review all changes associated with that item
- a file list — review those specific files

## STEP 0 - Identify Review Target

0. **Context Recovery**: Re-read AGENTS.md so project instructions are fresh
   in your working memory. After long sessions, context compaction may have
   dropped critical project rules. This step is cheap insurance against drift.
0a. **Load active design principles** following the principles-resolution
   reference for this runtime. Apply them as review criteria — flag changes
   that violate the active principles.
0b. **Load active concerns and practices** following the concern-resolution
   reference for this runtime. Flag implementation that uses tools or
   conventions inconsistent with the declared concerns (e.g., wrong test
   framework, wrong formatter, wrong import style).
0c. **Read the work item's context digest** if the reviewed item has one.
   Use it as the authoritative summary of what principles, concerns, practices,
   and ADRs govern this work.
1. Determine what was just implemented:
   - If `last-commit` or no argument: `git diff HEAD~1`
   - If `commit:<sha>`: review exactly that commit's diff (`git show <sha>`)
   - If work item ID: load the item, find associated commits via item ID in
     commit messages, compute the aggregate diff
   - If file paths: review those files in their current state
2. Load the governing artifacts for the reviewed code (acceptance criteria,
   test plans, design docs).

## STEP 0.5 - Work Item Acquisition

Before performing review passes, acquire a governing work item for this
review. See the runtime's work-item acquisition reference for the full
pattern.

If reviewing a specific work item ID, the review may record findings on the
execution item itself. Otherwise, create a dedicated review item. All review
findings are governed by the acquired work item.

## Pass 1 - Correctness Review

For every changed function or method:

1. Does it handle all error cases documented in the design?
2. Are edge cases covered (empty input, null, boundary values, overflow)?
3. Does it match the acceptance criteria from the governing issue?
4. Are return values and error codes consistent with interface contracts?
5. Are there off-by-one errors, missing bounds checks, or unclosed resources?

For every changed test:

1. Does it actually test what it claims to test?
2. Are assertions specific enough to catch regressions?
3. Could the test pass even if the code were broken (tautological assertion)?
4. Are error paths tested, not just the happy path?

## Pass 2 - Integration Review

1. How do the changes interact with existing code paths?
2. Are there race conditions, deadlocks, or ordering dependencies?
3. Are there missing imports, broken references, or stale caches?
4. Do configuration changes propagate correctly?
5. Are database migrations reversible?
6. Do API changes maintain backward compatibility where required?

## Pass 3 - Concern-Aware Quality Review

### Security (always, when attack surface exists)

1. Are there injection vulnerabilities (SQL, command, XSS, template)?
2. Are there authentication or authorization bypasses?
3. Is sensitive data logged, cached, or exposed in error messages?
4. Are there O(n^2) loops, unbounded allocations, or missing pagination?
5. Are there unnecessary network calls in hot paths?

### Concern-Specific Practices

For each active concern loaded in Activity 0b, verify the changes follow
the concern's declared practices:

1. **Tech-stack concerns**: Does the code use the declared linter, formatter,
   test framework, and build tool? Flag drift signals — e.g., `require()`
   instead of `import`, `npm run` instead of `bun run`, `println!` instead
   of `tracing::info!`, `vitest` imports in a `bun:test` project.
2. **Security concern** (if active): Are inputs validated at system boundaries?
   Are SQL queries parameterized? Are secrets loaded from environment, not
   hardcoded? Are error messages generic to clients? Check against the
   security concern's practices.
3. **Observability concern** (if active): Are new code paths instrumented
   with tracing spans? Are metrics emitted for new endpoints? Check against
   the observability concern's practices.
4. **Infrastructure concern** (if active): Do new services follow the
   declared deployment pattern? Are Helm values or k8s manifests updated?

Report concern-practice violations as findings with category `drift` and
the specific concern name.

Skip this pass when changes are purely documentation, configuration, or
internal refactoring with no new attack surface, performance impact, or
concern-relevant tooling changes.

## Pass 4 - Operational Learnings

Review the changes for lessons that should be captured in project operational
docs. This pass ensures that hard-won knowledge is not lost to context
compaction or session boundaries.

1. **AGENTS.md drift**: Do the changes introduce new tools, commands, patterns,
   or conventions that AGENTS.md does not yet document? Are there existing
   AGENTS.md instructions that the changes have made stale or wrong?
   - New CLI commands or flags
   - Changed file paths or directory layout
   - New or removed dependencies
   - Changed testing or CI procedures
   - New conventions for naming, structure, or workflow

2. **Behavioral learnings**: Did this implementation reveal non-obvious
   constraints, failure modes, or gotchas that future agents should know about?
   - Surprising API behavior or edge cases
   - Performance constraints discovered during implementation
   - Configuration interactions that were not obvious from docs
   - Test patterns that proved necessary

3. **Apply updates directly**: If AGENTS.md needs updating and the required
   change is clear from the evidence, make the edit. Do not just recommend it.
   Keep AGENTS.md concise — add actionable instructions, not narrative history.

4. **File learnings issues**: For behavioral learnings that do not belong in
   AGENTS.md (they are project-specific knowledge, not agent instructions),
   create a `kind:backlog` issue with label `source:learnings` capturing the
   insight and its evidence.

Skip this pass only when changes are trivial (typos, formatting, comment-only).

## Output

For each issue found, report:

- **File and line**: exact location
- **Category**: bug, security, performance, correctness, integration, drift
- **Severity**: critical, high, medium, low
- **Description**: what is wrong
- **Suggested fix**: how to resolve it

## Filing Findings as Work Items

After completing all review passes, file each actionable finding (severity
`critical`, `high`, or `medium`) as a work item so that findings are durable
and appear in the ready queue for subsequent execution cycles.

For each actionable finding, create a work item with:

- a title with the category prefix
- labels `helix,activity:build,review-finding` plus derived area labels
- `spec-id` set to the governing artifact or file path where the finding
  was identified
- description including: file and line, category, severity, full description,
  and suggested fix
- deterministic acceptance criteria (e.g., "test X passes", "no SQL injection
  in function Y")

Rules for filing:
- `low` severity findings: do not file as work items; report them in the output
  only
- Apply label `review-finding` on every finding item for queryability
- Include at least one scope-appropriate `area:*` label on every filed finding
  so concern matching survives re-entry into the queue
- Derive `area:*` labels in this priority order:
  1. Preserve `area:*` labels from the reviewed execution item when the review
     target is a work item.
  2. Otherwise infer the label(s) from the reviewed scope using the project
     area taxonomy in `docs/helix/01-frame/concerns.md` (or the default
     taxonomy from the concern-resolution reference when the project file does
     not exist).
  3. If the finding spans multiple surfaces, assign multiple `area:*` labels
     rather than picking one arbitrarily.

## Measure

Record review results on the governing work item via the runtime-provided work-item source.
See the measure action for the full pattern.

All four review passes constitute the measurement. Record a summary covering:

- timestamp
- status (CLEAN or ISSUES_FOUND)
- findings counts (total, filed, critical, high, medium, low)
- whether AGENTS.md was updated
- number of learnings items created

## Convergence

A clean review verdict (no findings) is **necessary but not sufficient** for
convergence. The work converges only when it is **verified** *and* each
finding-class this review surfaced has been **folded back into a gate** (a
template check, an acceptance criterion, a concern propagation check, or a
ratchet) so the same class cannot silently recur. "The reviewer said SHIP" is
evidence toward verification, never the definition of done.

Drive resolution by **progressive evolve against the specific finding**, not by
re-splatting the artifact or implementation. Re-generating wholesale discards
the review investment and reintroduces resolved finding-classes. If a
finding-class cannot be folded into a gate now, file it as explicit follow-on
work rather than declaring the loop closed.

**Intrinsic gates are blocking; external adversarial review is advisory.** The
intrinsic gates — build, test, template conformance, the phantom-claim count —
are mechanically checkable and **block** convergence. An external adversarial
reviewer (a separate tool or model invoked for a second opinion) is **advisory
input only** and must never be a hard gate: when it hangs, errors, or is
unavailable, convergence is decided by the intrinsic gates, not stalled waiting
on it. Feed its findings in as evidence; do not let its availability gate the
loop.

## Report

Close the review cycle. See the report action for the full pattern.

1. The filed finding work items are the primary follow-on output — they
   re-enter the planning cycle for polish and build.
2. Close the governing review work item with evidence summary.
3. If issues are found with severity `critical` or `high`, recommend that the
   associated implementation item be reopened or a regression item be created.

Report these trailer lines at the end of your output:

```
REVIEW_STATUS: CLEAN|ISSUES_FOUND
ISSUES_COUNT: N
FINDINGS_FILED: N
AGENTS_MD_UPDATED: YES|NO
LEARNINGS_FILED: N
MEASURE_STATUS: PASS|FAIL|PARTIAL
ITEM_ID: <governing-item-id>
FOLLOW_ON_CREATED: N
```

- `CLEAN`: no issues found across all passes
- `ISSUES_FOUND`: one or more issues identified
- `ISSUES_COUNT`: total number of findings (all severities)
- `FINDINGS_FILED`: number of findings filed as work items (critical+high+medium)
- `AGENTS_MD_UPDATED`: whether AGENTS.md was modified during this review
- `LEARNINGS_FILED`: number of learnings items created (0 if none)

## Runtime Integration Appendix

This appendix covers how a runtime realizes the review action. The reference
paths and work-item acquisition below are runtime-neutral; for the concrete
commands of a specific runtime, see its install guide (DDx:
[docs/install/ddx.md](../../docs/install/ddx.md)).

### STEP 0 — Reference resolution

- Principles: `workflows/references/principles-resolution.md`
- Concerns: `workflows/references/concern-resolution.md`
- Context-digest: `workflows/references/context-digest.md`
- Security concern practices: `workflows/concerns/security-owasp/practices.md`
- Observability concern practices: `workflows/concerns/o11y-otel/practices.md`

In the automated execution loop, prefer `commit:<sha>` from the executed
item's `closing_commit_sha` when tracker-closure bookkeeping produced a newer
tracker-only commit after the implementation commit.

### STEP 0.5 — Work-item acquisition

Acquire the governing work item before modifying files, per
`workflows/references/bead-first.md`: find an open planning item labelled
`kind:planning,action:review` (claim it if found) or create one with labels
`helix,kind:review,kind:planning,action:review`, `spec-id` set to the reviewed
commit or issue, a `<context-digest>` description naming the fresh-eyes review
target (last-commit, issue-id, or file-list), and acceptance "All review passes
complete; findings filed as work items with scope-appropriate area labels;
AGENTS.md updated if needed". The runtime supplies the work-item store; for the
concrete commands see its install guide
([docs/install/ddx.md](../../docs/install/ddx.md) for DDx).

Then assemble or refresh the item's context digest per
`workflows/references/context-digest.md`. If the repo ships
`scripts/refresh_context_digests.py`, use it after creation so the digest and
derived `area:*` labels stay deterministic.

### Filing findings — runtime specifics

File each finding as a work item with labels
`helix,activity:build,review-finding,<derived-area-labels>`, `spec-id` set to
the governing artifact or file path, a description capturing the file and line,
category, severity, full description, and suggested fix, and acceptance set to
deterministic verification criteria for the fix. After creating the item,
assemble or refresh its context digest (e.g. with
`scripts/refresh_context_digests.py` if the repo ships it).

Derive `area:*` labels: first preserve labels from the reviewed execution
item; otherwise infer from the reviewed scope using
`docs/helix/01-frame/concerns.md` (or the default taxonomy in
`workflows/references/concern-resolution.md` when the
project file does not exist).

### Measure — runtime specifics

Record the results on the governing work item (in its notes, if the runtime
provides a notes field) as a `<measure-results>` block of this shape:

```
<measure-results>
  <timestamp>YYYY-MM-DDTHH:MM:SSZ</timestamp>
  <status>CLEAN|ISSUES_FOUND</status>
  <findings total='N' filed='N' critical='N' high='N' medium='N' low='N'/>
  <agents-md-updated>YES|NO</agents-md-updated>
  <learnings-filed>N</learnings-filed>
</measure-results>
```

### Action input examples

```
helix review
helix review last-commit
helix review commit:abc1234
helix review <id>
helix review src/auth/
```

### Output trailer

```
REVIEW_STATUS: CLEAN|ISSUES_FOUND
ISSUES_COUNT: N
FINDINGS_FILED: N
AGENTS_MD_UPDATED: YES|NO
LEARNINGS_FILED: N
MEASURE_STATUS: PASS|FAIL|PARTIAL
ITEM_ID: <governing-item-id>
FOLLOW_ON_CREATED: N
```

The filed finding work items re-enter the planning helix for polish and build.
