# Report shape (shared contract)

Alignment, validation, refresh, check, and project-audit outputs end with one
machine-readable block in this shape so a runtime can file work from it and an
evaluation can grade it. The prose report stays human-first; the block is the
contract.

```yaml
helix_report:
  mode: align            # align | validate | refresh | check | project-audit
  scope: docs/helix/     # flow root, artifact path, or selector
  catalog: in-tree       # which §Catalog Resolution source bound
  summary:
    aligned: 12
    incomplete: 2
    divergent: 0
    underspecified: 1
    stale_plan: 0
    blocked: 0
  findings:
    - id: F-1
      classification: INCOMPLETE   # ALIGNED | INCOMPLETE | DIVERGENT | UNDERSPECIFIED | STALE_PLAN | BLOCKED
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

Rules:

- Every finding carries a classification from the Align taxonomy and at least
  one evidence path; `lines` are optional but preferred.
- Every non-`ALIGNED` finding carries the four handoff fields (destination
  type, deliverable shape, next mode, evidence). Never a CLI command.
- `summary` counts equal the findings by classification.
- Assumptions made under `high` autonomy are listed, each with its source.
- Runtimes that file work items copy `handoff` into the item; chat-only
  runtimes display the block unchanged.
