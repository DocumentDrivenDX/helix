---
ddx:
  id: METRIC-name
---

# Metric Definition: [NAME]

> Store at `docs/helix/06-iterate/metrics/[NAME].yaml`

```yaml
name: [kebab-case-identifier]
description: [What this metric measures]
unit: [seconds|bytes|percent|count|score|...]
direction: [lower|higher]
command: [repeatable shell command that actually runs and emits the value]
output_pattern: "[regex with capture group]"
baseline: [the value the command produced on a recorded run — measured, not asserted]
target: [the value that counts as success, in the same unit]
tolerance: [noise band, e.g. "5%" or "100ms"]
last_verified: [ISO-8601 date the command was last run and confirmed to emit this value]
interpretation: [How to read meaningful changes]
labels:
  [key]: [value]
```

**The measurement must be real.** `command` must have actually been run and
confirmed to emit the value before this metric is trusted; record that run date
in `last_verified`. A metric whose command was never run — an
asserted-but-unmeasured number — is a phantom claim (FEAT-016), not a metric.
`baseline` is what the command *produced*, never a target typed in by hand; for
a regression bench (a metric validating a methodology/skill change), `baseline`
is the bare-prompt reading and `target` is the value that earns the change its
keep.
