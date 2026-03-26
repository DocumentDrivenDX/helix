---
name: helix-review
description: Run the HELIX fresh-eyes review. Use when the user wants `helix review` behavior after implementation.
argument-hint: "[scope]"
---

# Review

Execute the HELIX fresh-eyes review action.

## Steps

1. Read and apply `workflows/actions/fresh-eyes-review.md`.
2. Scope the review to `$ARGUMENTS` when provided, otherwise review the recent
   implementation work.
3. Focus on bugs, regressions, missing tests, and follow-on work.
4. Report concrete findings first. If the work is clean, say so briefly.

## Output

- findings first
- concrete evidence
- recommended fixes or follow-on issues when needed
