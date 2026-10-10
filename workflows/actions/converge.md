# HELIX Action: Converge

Review a target, resolve blocking findings within the user's scope, and review
the changed target again. Converge supports plans, specifications, artifacts,
and completed work.

## Input

- **Target:** the plan, artifact, work item, or change to review.
- **Rounds:** maximum review rounds; default 2 (initial pass and verification of fixes).
- **Clean streak:** consecutive rounds without blocking findings; default 1.
  Do not repeat unchanged clean content to manufacture a streak; a larger
  streak requires explicit selection and distinct evidence within the ceiling.
- **Spending:** use the shared token ceiling and metering rules in
  `workflows/references/work-item-first.md`; no separate review budget.
- **Review only:** report findings without applying fixes.

If the target or authority is unclear, ask before editing. A plan or spec is
reviewed against its governing artifacts. Completed work is reviewed against
its requirements, decisions, and tests. Use the review action for each pass.

## Loop

1. Review the target adversarially within scope. Classify findings as
   **blocking** when they violate a governing requirement, reveal an unresolved
   correctness or security defect, or invalidate necessary verification.
   Record other useful observations as advisory.
2. Unless review-only, fix each blocking issue in the authorized target. Do not
   dismiss a finding by reclassification. If a finding does not apply, record
   the evidence that resolves it.
3. Re-review changed material and affected dependencies after blocking fixes.
   Advisory observations alone do not trigger another round. Stop when the clean
   streak is reached, the round or spending limit is reached, progress stalls,
   or an unresolved decision needs the user's input.

Existing build, test, security, and conformance requirements remain binding
when they apply. External review is useful evidence, but its availability does
not block a decision.

## Output

Report the target, number of rounds, final disposition, resolved blockers, and
any remaining blockers or advisory findings. Support the conclusion with
evidence.
