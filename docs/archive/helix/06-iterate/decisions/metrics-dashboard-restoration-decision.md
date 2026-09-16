# Metrics Dashboard — Restoration Decision

> Historical decision; superseded by the worked example at `docs/helix/06-iterate/metrics-dashboard.md`.

`metrics-dashboard` is restored as the canonical iterate-activity summary
artifact.

## Decision

This artifact is restored rather than retired. The original intent still
exists in current HELIX and is not fully replaced by the metric-definition
files alone.

## Why It Exists

- Metric definitions describe what to measure.
- The metrics dashboard interprets the current measurement set against a
  baseline.
- The result answers the review question: did the latest changeset improve
  the system?

## Canonical Inputs

- `docs/helix/06-iterate/metrics/*.yaml`
- measurement output from the current iteration
- prior iteration baseline or committed floor
- `docs/helix/06-iterate/security-metrics.md` when security posture affects interpretation

## Minimum Prompt Bar

- Start from the canonical metric definitions.
- Compare current values to a baseline or ratchet floor.
- State whether the change improved, regressed, or stayed within noise.
- Cite the metric source and measurement command or report.
- Keep the artifact focused on the decision, not on raw dashboard plumbing.

## Minimum Template Bar

- review window
- explicit baseline
- metric table with source references
- trend notes
- decision or recommendation
- follow-up items or tracker links

## Canonical Replacement Status

`metrics-dashboard` is not superseded by a tracker primitive. Tracker issues
capture follow-up work, but they do not replace the iteration-level summary
that interprets the measured system state.
