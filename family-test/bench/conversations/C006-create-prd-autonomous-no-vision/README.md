# C006 — Create a PRD: marker active, NO vision (autonomous)

**Category:** conversation-library (happy paths) (plan §1.5b)
**Phase:** P5
**Tier:** must_pass_core

## What this asserts

Marker is active (`helix`), no vision exists, autonomy=autonomous. The
skill MUST engage AND proceed without asking — drafting the vision
first, then the PRD, satisfying the cascade in one turn.

Pair-row contract with C005 (identical workspace + prompt, guided):
- C005 ASKS before mutation.
- C006 PROCEEDS (no pre-mutation confirmation) and writes both
  artifacts.

C005 vs C006 is the canonical autonomy-slider proof for the cascade.

## Negative control

`plugins_remove: [methodology-product]`. Skill unregistered; verdict
flips.
