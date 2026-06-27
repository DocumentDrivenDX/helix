# HELIX Action: Genesis

You are bootstrapping a brand-new project into HELIX from a bare intent. Genesis
is the fixed opening sequence the operator otherwise re-types every time a project
starts: name it, research the prior art, draft a vision shaped by that research,
and scaffold the HELIX structure — leaving a governed project ready for `frame`.

Genesis does not invent new artifact types. It sequences existing capabilities
(research, vision, frame) so a new project starts governed instead of as an
ungoverned chat.

## Action Input

You may receive:

- a **project name** (or a prompt to choose one) and a one-paragraph intent
- known **constraints**: the engine/runtime it must build on, prior art to replace
  or avoid, the audience, hard non-goals
- `--no-research` to skip the prior-art step when the domain is already well
  understood (record that choice; the default is to research)

## Authority Hierarchy

A genesis project has no artifacts above the vision yet. The vision it produces
becomes the top of the hierarchy:

1. Product Vision  ← genesis produces this
2. Product Requirements  ← the following `frame` produces these
3. Feature Specs / User Stories
4. Architecture / ADRs
5. Solution / Technical Designs

## STEP 0 - Bootstrap

0. **Context Recovery**: Read AGENTS.md if one exists; for a truly empty repo,
   there may be none yet.
1. Confirm the project root and that no HELIX marker / `docs/helix/` already
   exists. If one does, this is not a genesis — route to `frame` or
   `backfill` instead and say so.

## STEP 1 - Name and Intent

1. Establish the project name and a one-paragraph statement of intent: what it is,
   who it is for, and the single problem it exists to solve.
2. Capture the hard constraints and non-goals the operator stated. These bound the
   research and the vision — an explicit non-goal here prevents a class of
   gold-plating later (see the `scope-discipline` concern).

## STEP 2 - Research the Prior Art

Unless `--no-research`: investigate the prior art before committing to a vision,
so the vision is evidence-shaped, not assumed — research before committing to a
direction, time-boxed, with actionable findings.

1. Survey existing solutions in the space — what they do, where they fall short,
   the defensible gap this project fills. Use the research-review / deep-research
   capability if the runtime provides one.
2. Validate the stated engine/runtime constraints: is the intended foundation a
   fit, or does the research surface a better one?
3. Record findings as a `research-plan` / research note under
   `docs/helix/00-discover/` (or the frame research artifact). The vision cites it.

A recorded `--no-research` choice substitutes the operator's stated domain
knowledge for the survey; an unrecorded skip is drift.

## STEP 3 - Draft the Vision

Author the `product-vision` artifact (00-discover) from the intent + research:

- the problem, the audience, and the differentiated approach the research supports
- the explicit non-goals (what this project will *not* be — the research often
  surfaces the tempting-but-wrong adjacencies to name here)
- the success signals that later requirements will refine

Hold the vision to what the research backs. A vision claim with no evidence behind
it is the genesis-stage version of an unbacked assertion — mark it as an
assumption to validate in `frame`, not as fact.

## STEP 4 - Scaffold HELIX

1. Create the HELIX project structure the runtime expects: the marker / project
   config, and the `docs/helix/` activity directories.
2. Record the initial concern selections the vision and constraints already imply
   (language/runtime slot, architecture style if decided) in `concerns.md`, each
   with its source (`operator-override` / `shipped-default` / `assumption`).
3. Leave a clear pointer to the next action: `frame` to turn the vision into a PRD,
   requirements, and stories.

## Output

Report:

1. Project name and one-paragraph intent.
2. Research disposition (survey findings + the chosen foundation, or the recorded
   `--no-research`).
3. The vision artifact path and its named non-goals.
4. The scaffolded structure and initial concern selections.
5. The next action (normally `frame`).

Then emit the machine-readable trailer:

```
GENESIS_STATUS: READY|BLOCKED
PROJECT: <name>
VISION: <path>
RESEARCH: done|skipped-recorded
NEXT: frame
```

- `READY`: vision authored, structure scaffolded, next action is `frame`.
- `BLOCKED`: a prerequisite is missing (e.g. an existing HELIX project found, or a
  constraint that contradicts the intent and needs an operator decision). Report
  the blocker; do not scaffold over an existing project.

## Runtime Integration Appendix

- The marker file, project config, and concrete `docs/helix/` paths are
  runtime-specific; see the runtime's install guide (DDx:
  [docs/install/ddx.md](../../docs/install/ddx.md)).
- Genesis composes `research` (STEP 2), the `product-vision` artifact (STEP 3), and
  hands off to `frame` (STEP 4). It does not duplicate those contracts — it orders
  them for a cold start.
