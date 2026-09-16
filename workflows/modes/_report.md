# Report shape (shared contract)

Align, validate, refresh, check, project-audit, review, and converge outputs
end with one machine-readable block in this shape so a runtime can file work
from it and an evaluation can grade it. The prose report stays human-first;
the block is the contract.

```yaml
helix_report:
  mode: align            # align | validate | refresh | check | project-audit | review | converge
  scope: docs/helix/     # flow root, artifact path, or selector
  catalog: in-tree       # which §Catalog Resolution source bound
  summary:
    aligned: 12
    incomplete: 2
    divergent: 0
    underspecified: 1
    stale_plan: 0
    blocked: 0
    phantom_claims: 0    # review, converge: asserted tests, coverage, or metrics that do not exist
  findings:
    - id: F-1
      classification: INCOMPLETE   # ALIGNED | INCOMPLETE | DIVERGENT | UNDERSPECIFIED | STALE_PLAN | BLOCKED
      severity: high               # optional: blocking | high | medium | low (review, converge)
      artifact: docs/helix/01-frame/prd.md
      lines: [88, 94]
      claim: FR-4 has no covering user story
      evidence: [docs/helix/01-frame/user-stories.md]
      handoff:
        destination_type: user-stories
        deliverable: a story covering FR-4 with Given/When/Then ACs
        next_mode: frame
        evidence: [docs/helix/01-frame/prd.md:88]
  assumptions:
    - text: the deploy flow is out of scope for this pass
      source: operator prompt
  next_mode: frame       # the single recommended next action, or none
```

## Handoff fields

Every non-`ALIGNED` finding carries all four; a handoff is never a CLI
command.

- **`destination_type`**: the artifact type (PRD, FEAT, user-stories, ADR,
  technical-design, test-plan, ...) where the gap is resolved.
- **`deliverable`**: the concrete content to add ("a TD section answering X",
  "a story covering Y", "an ADR recording the Z choice").
- **`next_mode`**: the routed mode that produces it (`frame`, `design`,
  `polish`, `validate`, `evolve`, `backfill`), or `runtime-handoff` when
  execution is already governed.
- **`evidence`**: artifact paths plus line numbers or section anchors
  supporting the finding.

## Rules

- Every finding carries a classification from the Align taxonomy and at least
  one evidence path; `lines` are optional but preferred.
- `severity` is set by review and converge; `blocking` findings and any
  `phantom_claims` above zero block convergence.
- `summary` counts equal the findings by classification.
- Assumptions made under `high` autonomy are listed, each with its source.
- Runtimes that file work items copy `handoff` into the item; chat-only
  runtimes display the block unchanged.
