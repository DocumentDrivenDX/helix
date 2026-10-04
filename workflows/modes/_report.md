# Reports

Use a clear conversational answer by default. A durable artifact or
machine-readable block is appropriate when the user requests one or a runtime
consumer requires it.

## Optional structured report

For align, validate, refresh, check, project-audit, review, or converge, this
schema is available when structured output is requested:

```yaml
helix_report:
  mode: align            # align | validate | refresh | check | project-audit | review | converge
  scope: docs/helix/     # requested flow root, artifact, or selector
  catalog: in-tree       # optional bound catalog source
  summary:
    aligned: 12
    incomplete: 2
    divergent: 0
    underspecified: 1
    stale_plan: 0
    blocked: 0
    phantom_claims: 0    # optional; review or converge when checked
  findings:
    - id: F-1
      classification: INCOMPLETE
      severity: high      # optional; review and converge
      artifact: docs/helix/01-frame/prd.md
      lines: [88, 94]     # optional
      claim: FR-4 has no covering user story
      evidence: [docs/helix/01-frame/user-stories.md]
      handoff:            # include when the consumer needs a concrete handoff
        destination_type: user-stories
        deliverable: a story covering FR-4 with verifiable criteria
        next_mode: frame
        evidence: [docs/helix/01-frame/prd.md:88]
  assumptions:
    - text: deployment behavior was outside the requested scope
      source: operator prompt
  next_mode: frame        # optional recommendation
```

Include fields that help the user or consumer; omit empty sections and
inapplicable dimensions. `summary` counts must match the findings included in
the report. Findings need a classification and evidence. Add `severity` when
review or converge uses it. Add a handoff only when a runtime consumer or the
user needs a concrete destination and next step; it is not required for every
finding. State assumptions when they affect the conclusion.

When converge is requested, unresolved blocking findings keep it open. A
`phantom_claims` count is a zero-floor convergence gate only when claims-vs-
reality was part of that review. Do not create tracker items or new gates just
to populate a report.
