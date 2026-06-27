# HELIX Action: Converge

You are driving a target to convergence: review it adversarially, resolve every
blocking finding, and re-review — repeating until the review comes back clean. The
operator should never have to hand-type "review until it converges, then implement,
then review again" — this action *is* that loop, enforced.

Converge does not invent a new review. It wraps the existing review capability
(`fresh-eyes-review` for completed work, the adversarial-review skill for a plan
or spec) in a fixed-point loop with an explicit stop rule.

## Action Input

You may receive:

- a **target**: a plan, spec, artifact, work item, diff, or PR to converge
- `--rounds <N>`: maximum review rounds before giving up (default 5)
- `--clean-streak <K>`: consecutive zero-blocking rounds required to declare
  convergence (default 1; use 2 for high-stakes targets)
- `--review-only`: run the loop without applying fixes (report what blocks
  convergence and stop) — for targets the operator wants to resolve by hand

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

## STEP 0 - Bootstrap

0. **Context Recovery**: Re-read AGENTS.md so project instructions are fresh in
   your working memory.
1. Identify the target and its kind (plan / spec / artifact / work item / diff).
   This selects the review capability:
   - a **plan or spec** (not yet implemented) → adversarial-review skill if
     available, else the `review` reading applied to the document.
   - **completed work** (a diff, PR, or closed item) → `fresh-eyes-review`.
2. Load the governing artifacts the target must satisfy (its acceptance criteria,
   the specs above it in the authority hierarchy) — they are the bar the review
   judges against, so a clean review means "satisfies these", not "looks fine".

## STEP 1 - Review Round

Run one review pass using the capability chosen in STEP 0 — converge does not
invent its own review:

- **Completed work** → run `fresh-eyes-review` against the diff/PR and its
  governing acceptance criteria. It produces `CLEAN | ISSUES_FOUND` with
  per-finding severity (critical / high / medium / low) across its passes.
- **Plan or spec** → run the adversarial-review skill if available, else apply the
  `review` reading to the document against its governing artifacts.

Whichever ran, the review must be **adversarial, not confirmatory** (the
`verification` concern's re-review rule): it actively looks for how the target is
wrong — contradictions, missing constraints, unhandled paths, acceptance criteria
the target skirts rather than satisfies, scope that is hollow (stubbed) or padded
(gold-plated, per the `scope-discipline` concern).

Normalize the review's findings into converge's two-level loop vocabulary:

- **BLOCKING** — `fresh-eyes-review` **critical** or **high** (or an
  adversarial-review must-fix): a contradiction, a missing required constraint, an
  unsatisfied governing acceptance criterion, a correctness/security defect, or a
  scope/verification-gate violation. Convergence is not reached while one stands.
- **ADVISORY** — `fresh-eyes-review` **medium** or **low** (or an adversarial-review
  nice-to-have): a non-blocking improvement. Recorded, not gating.

A round with zero BLOCKING findings (a `fresh-eyes-review` of `CLEAN`, or one whose
only findings are medium/low) is a **clean round**.

## STEP 2 - Resolve

Unless `--review-only`:

- For each BLOCKING finding, apply the fix to the target (edit the plan/spec/
  artifact, or correct the code) so the finding no longer holds.
- A finding is **resolved** only when the underlying issue is fixed — never by
  reclassifying it to advisory or asserting it away. If a BLOCKING finding is
  genuinely a false positive, record why it does not apply; that is a resolution,
  not a dismissal.
- Do not introduce unrequested scope while resolving (the change that fixes a
  finding stays scoped to that finding).

## STEP 3 - Loop or Stop

- If the last round was clean and the clean streak has reached `--clean-streak`
  (default 1, and only after at least one round that produced or resolved a
  finding — a single clean review of an unchanged target counts as the streak):
  **CONVERGED**. Stop.
- If BLOCKING findings were resolved this round: go to STEP 1 for another round
  (a fix can introduce a new defect; re-review confirms it did not).
- If `--rounds` is exhausted with BLOCKING findings still standing, or the same
  BLOCKING finding recurs unresolved across rounds (a fix loop that is not making
  progress): **NOT_CONVERGED**. Stop and report the standing findings — do not
  loop forever, and do not declare done over an unresolved blocker.

## Output

Report:

1. Target and review capability used.
2. Per round: blocking count, advisory count, findings resolved.
3. Final disposition and, if NOT_CONVERGED, the standing BLOCKING findings and
   why they remain.

Then emit the machine-readable trailer:

```
CONVERGE_STATUS: CONVERGED|NOT_CONVERGED
TARGET: <id-or-path>
ROUNDS: N
BLOCKING_RESOLVED: N
BLOCKING_STANDING: N
ADVISORY_OPEN: N
```

- `CONVERGED`: a clean streak of `--clean-streak` rounds reached; no BLOCKING
  finding stands.
- `NOT_CONVERGED`: round budget exhausted or no-progress loop detected with
  BLOCKING findings standing. This is an honest stop, not a failure to hide.

## Runtime Integration Appendix

This appendix covers how a runtime realizes the converge action.

### Review capability resolution

- **Plan / spec convergence**: prefer an adversarial-review capability if the
  runtime provides one (e.g. the adversarial-review skill, or a second model
  harness for cross-model critique). Otherwise apply the `review` reading to the
  document directly.
- **Completed-work convergence**: use `fresh-eyes-review` against the diff/PR and
  its governing acceptance criteria.

The loop, the BLOCKING/ADVISORY classification, and the stop rule are
runtime-neutral; only the underlying review capability is runtime-supplied.

### Relationship to other actions

- `converge` is the loop; `fresh-eyes-review` and the adversarial-review skill are
  the single-pass reviews it drives.
- After an implementation pass, converge the work before advancing the queue:
  `implementation` then `converge` is the enforced replacement for the operator
  hand-typing "implement, then review until clean".
- `converge` on a plan before implementation is the enforced replacement for
  "review the plan until it converges, then build".
