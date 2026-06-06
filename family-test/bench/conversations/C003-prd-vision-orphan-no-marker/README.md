# C003 — "Let's create a PRD"; vision exists, no marker (guided, exploratory)

**Category:** conversation library (plan §1.5 row C003)
**Phase:** P5b
**Tier:** exploratory

## Scenario

Workspace state:
- NO `.helix.yml` (no methodology marker).
- An approved `docs/helix/00-discover/product-vision.md` (VIS-001) is
  present — a HELIX-shaped artifact already exists but no marker
  authorises the methodology.

Operator says: "Let's create a PRD for the coffee-ordering app."

## Expected behaviour

Under `autonomy=guided` the skill MUST:

1. Engage (orphan-artifact heuristic per SKILL.md §1.5 — a HELIX-shaped
   artifact lives in the tree but is unmarked).
2. Surface the missing marker as a prerequisite to authoring the PRD
   (the cascade rule: PRD requires vision AND marker). Because the
   vision artifact already exists, the cascade resolves to "add the
   marker, then write the PRD."
3. ASK before mutating — either before writing `.helix.yml` or before
   writing the PRD draft. Guided autonomy requires confirmation before
   the FIRST state-changing tool_use.

## Why this is exploratory, not core

Orphan-artifact engagement (no marker, but artifacts present) is a
heuristic surface — it can mis-fire on partial HELIX trees from prior
methodologies the operator has since abandoned. The cascade-and-ask
flow it triggers is the same surface AM-02 / C005 exercise more
deterministically; C003 only adds the orphan-trigger variant. Listed
exploratory per plan §5 row C003.

## Negative control

Plugin removed (`plugins_remove: [methodology-product]`). Without the
helix methodology plugin, the skill cannot engage on either the marker
absence or the orphan vision; the agent may draft a PRD from training,
but it will NOT pause to ask about adding `.helix.yml` and the
confirmation matcher cannot fire on marker-aware language.
