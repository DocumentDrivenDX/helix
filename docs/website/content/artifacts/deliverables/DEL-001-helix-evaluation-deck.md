---
title: "Document discipline catches agent drift before review"
slug: DEL-001-helix-evaluation-deck
weight: 480
activity: "Iterate"
source: "06-iterate/deliverables/DEL-001-helix-evaluation-deck.md"
generated: true
collection: deliverables
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

> **Source identity** (from `06-iterate/deliverables/DEL-001-helix-evaluation-deck.md`):

```yaml
ddx:
  id: DEL-001
  type: deliverable
  activity: iterate
  kind: deck
  status: draft
  authoring:
    home: repo
    export:
      - docs/helix/06-iterate/deliverables/assets/DEL-001-helix-evaluation-deck.pptx
      - docs/helix/06-iterate/deliverables/assets/DEL-001-helix-evaluation-deck.pdf
  links:
    - id: helix.product-vision
      kind: informed_by
    - id: PRD-001
      kind: informed_by
```

# Document discipline catches agent drift before review

## Brief

- **Audience**: engineering leaders (head of platform, VP of engineering) whose teams build with AI agents and who decide which practices those teams adopt
- **Occasion**: a 20-minute evaluation call, presented live, then sent as a PDF
- **Decision or action sought**: run HELIX on one real project for one quarter and count the drift it catches before review
- **Time slot or page budget**: 20 minutes, 10 content slides
- **Kind**: deck
- **Constraints**: HELIX house theme; no customer names; targets labeled as targets, never as results
- **Takeaway**: document discipline catches agent drift before review, and your agents can have it without changing the tools you run

## Story

- **Flow**: evaluation-briefing
- **Takeaway**: document discipline catches agent drift before review
- **Messages** (ranked by how much each moves the decision to run a trial):
  1. The way teams work with agents today lets specs, designs, and code drift until review or production catches it (evidence: docs/helix/01-frame/prd.md#problem, the three failure modes; docs/helix/00-discover/product-vision.md#why-now; docs/helix/00-discover/product-vision.md#target-market)
  2. HELIX is document templates plus one alignment check that finds drift before anyone writes code (evidence: docs/helix/00-discover/product-vision.md#mission-statement; docs/helix/01-frame/prd.md#core-workflow-contract; docs/helix/00-discover/product-vision.md#user-experience, the OAuth example with its counts)
  3. It runs inside the tools the team already uses and takes nothing over (evidence: docs/helix/00-discover/product-vision.md#positioning; docs/helix/01-frame/prd.md#non-goals)
  4. HELIX states the bar for judging it up front, and today that bar is a target rather than a result (evidence: docs/helix/00-discover/product-vision.md#success-definition; docs/helix/01-frame/prd.md#success-metrics)
- **Beats and titles** (titles written before any body):

  | # | Beat | Title (claim) | Message | Exhibit |
  |---|---|---|---|---|
  | 1 | takeaway | Document discipline catches agent drift before review | takeaway | title slide |
  | 2 | what-changed | Agents now write most production code without a shared practice | M1 | novelty-to-default timeline with the gap marked |
  | 3 | cost-of-today | Without that practice, agent code drifts from specs and decisions | M1 | three failure panels |
  | 4 | what-it-is | HELIX traces every agent change to a governing document | M2 | the double helix: documents and runtime joined by alignment |
  | 5 | how-it-works | The alignment check reads those documents before anyone codes | M2 | four-step flow with the alignment step highlighted |
  | 6 | what-changes | Drift surfaces at the alignment check instead of in review | M2 | today versus after, two columns |
  | 7 | proof | One OAuth change showed three drifted specs before coding | M2 | four count panels from the worked example |
  | 8 | proof | A healthy project averages under 3 drift findings per check | M4 | three stat callouts labeled target |
  | 9 | boundaries | HELIX checks documents and leaves your runtime and stack alone | M3 | boundary box: your tools around HELIX |
  | 10 | ask | Pilot HELIX on one project this quarter and count the drift | takeaway | ask band and three steps |
  | 11 | sources | Sources | all | source table |

- **Horizontal-logic test**: pass. Read in order, the titles move from the audience's change (2) to its cost (3), to what HELIX is (4), how it works (5), what changes (6), proof (7, 8), what it leaves alone (9), and a trial sized by the proof slide's measure (10); each title reuses a word from the one before, and the ask repeats "drift" from the takeaway.

## Content

### 1. Document discipline catches agent drift before review

**Pattern**: title
**Body**:
- An evaluation briefing for engineering leaders whose teams build with AI agents
**Visual**: kind: none. Full-bleed dark surface with the title in the display face, the subtitle naming the audience, and the date; the helix motif at the right edge
**Notes**: Say the takeaway once, then say the ask comes on the last slide and is one project for one quarter. Do not explain HELIX yet.
**Sources**: S1

### 2. Agents now write most production code without a shared practice

**Pattern**: claim-evidence
**Body**:
- Most professional developers ship agent-written code every day
- The output is locally good and globally inconsistent
- The document disciplines human teams built never reached the agents
- Every practice era gets its equivalent of test-driven development
**Visual**: kind: timeline | milestones: agents as novelty; agents as default practice; a shared practice for agents | now: 2 | marker: no shared practice yet | caption: how agent-written code became the default before any discipline caught up. Timeline drawn from the vision's Why Now section
**Notes**: Name the change; do not argue it. This audience lives it. The missing third milestone is the deck.
**Sources**: S2

### 3. Without that practice, agent code drifts from specs and decisions

**Pattern**: claim-evidence
**Body**:
- Specs, designs, and tests fall out of sync because nobody walks them between sessions
- A feature ships whose design contradicts a decision recorded months earlier
- Each new conversation re-improvises the workflow, so reviews that should happen do not
**Visual**: kind: panels | items: Drift / specs and code diverge between sessions; Contradiction / a design ignores an earlier decision; Lost context / every session starts from zero. Three failure panels from the requirements document's problem statement
**Notes**: These are the three failure modes the requirements document names. Each shows up late, in review or in production, which is why the cost is high. Ask which one the audience saw last week.
**Sources**: S3

### 4. HELIX traces every agent change to a governing document

**Pattern**: claim-evidence
**Body**:
- HELIX is a method, not a tool: document templates plus one alignment skill
- Every change traces to the document that governs it
- The content runs on any agent runtime that reads and writes markdown
- Teams adopt one document type at a time
**Visual**: kind: helix | left: documents | right: your runtime | left-note: intent, design, tests | right-note: code, runs, evidence | rungs: alignment. Two strands joined by alignment rungs, the product's own metaphor from the mission statement
**Notes**: Category first: a method you adopt. The picture is the product's own metaphor. The last bullet is the one that lowers switching cost, so land on it.
**Sources**: S1, S4

### 5. The alignment check reads those documents before anyone codes

**Pattern**: process-flow
**Body**:
- Write the brief: intent, requirements, constraints, decisions
- Check alignment: drift, contradictions, stale assumptions
- Plan the work: bounded items with scope and evidence
- Run it: your own runtime executes, measures, reports back
**Visual**: kind: process-flow | steps: Write the brief; Check alignment; Plan the work; Run it | highlight: 2 | caption: the step nobody does by hand today. Four-step flow from the requirements document's workflow contract
**Notes**: This is the four-step contract the requirements document commits to. The highlighted step is the one that replaces manual document walking, and slide 7 shows it on a real change.
**Sources**: S5

### 6. Drift surfaces at the alignment check instead of in review

**Pattern**: two-column-comparison
**Body**:
- Today: ad hoc prompting, manual document upkeep, and hoping for the best
- After: agents and people share one practice, and every change traces to a document
- Today: drift shows up in review or in production
- After: the alignment check catches drift before the first line of code
**Visual**: kind: two-column | left: Today | right: With HELIX | rows: Ad hoc prompting, manual document upkeep, and hoping for the best / Agents and people share one practice, and every change traces to a document; Drift shows up in review or in production / The alignment check catches drift before the first line of code | prefer: right | verdict: the biggest change is where drift shows up. Two columns from the vision's target-market table
**Notes**: The left column is what the audience recognizes. The verdict line is the whole deck in one sentence.
**Sources**: S6

### 7. One OAuth change showed three drifted specs before coding

**Pattern**: claim-evidence
**Body**:
- A team asked its agent to add OAuth login
- The alignment check found 3 affected feature specs and 2 affected designs
- It flagged 1 recorded decision that conflicted with the OAuth pattern
- It listed 4 missing user stories and 1 test plan to revise
**Visual**: kind: panels | items: 3 specs / affected by the change; 1 decision / in conflict with OAuth; 4 stories / missing and now listed; 1 test plan / to revise first. Four count panels from the vision's worked example
**Notes**: This is the worked example in the product vision, not a customer result. The point is the order: the plan starts with the security architecture revision, then the specs, then the stories, and no code moves until then.
**Sources**: S7

### 8. A healthy project averages under 3 drift findings per check

**Pattern**: stat-callout
**Body**:
- Under 3 findings per alignment check on a healthy document set
- 3 runtimes documented within 12 months
- 50 or more public repositories using the templates within 18 months
**Visual**: kind: stat | stats: < 3 / drift findings per check on a healthy project; 3 / runtimes documented within 12 months; 50+ / public repositories within 18 months | label: target. Three targets from the success definition, each labeled as a target
**Notes**: Every number on this slide is a target, not a result; say so before anyone asks. The first one is the measure the trial on slide 10 uses.
**Sources**: S8

### 9. HELIX checks documents and leaves your runtime and stack alone

**Pattern**: claim-evidence
**Body**:
- No command-line tool, tracker, queue, or execution engine ships with it
- Your technology choices stay yours; HELIX imposes none
- Product, design, and architecture judgment stays with people
- How much an agent does without asking is a dial you set
**Visual**: kind: boundary | outer: your runtime and tools | outer-note: tracker, queue, CI, stack, judgment | inner: HELIX | inner-note: templates plus one skill | caption: reads and writes your documents, asks before anything irreversible. Boundary diagram from the requirements document's non-goals
**Notes**: The non-goals from the requirements document. This answers the objection every platform team is forming by now, so give it time.
**Sources**: S9

### 10. Pilot HELIX on one project this quarter and count the drift

**Pattern**: ask-next-steps
**Body**:
- Pick one active project with an agent already in the loop, by the end of this week
- Adopt the templates and run one alignment check on its documents in the first sprint
- Review the findings together after four weeks and decide whether to widen
- Without a trial the practice stays improvised and drift keeps surfacing in review
**Visual**: kind: none | owners: ; ; | dates: ; ;. Ask band in the secondary hue, then three numbered steps with owner and date columns left blank for the audience to fill
**Notes**: Stop after the ask. If asked about cost, the trial needs one champion and no new tooling.
**Sources**: S5, S8

### 11. Sources

**Pattern**: appendix-sources
**Body**:
- Every figure and claim above maps to a section of the product vision or the requirements document listed below
**Visual**: kind: none. Two-column source list in caption size, claim on the left, document section on the right
**Notes**: Not presented.
**Sources**: S1

## Sources

| Id | Claim or figure | Governing artifact and section |
|---|---|---|
| S1 | HELIX is a methodology and artifact catalog for AI-assisted teams; the double helix of a document strand and an execution runtime; document disciplines packaged as templates plus one skill | docs/helix/00-discover/product-vision.md#mission-statement |
| S2 | AI-assisted development crossed from novelty to default; most professional developers ship AI-touched code daily; locally good, globally inconsistent; the era's TDD-equivalent practice | docs/helix/00-discover/product-vision.md#why-now |
| S3 | Three failure modes: artifact drift, inconsistent agent behavior (a feature whose design contradicts an earlier ADR), lossy session boundaries | docs/helix/01-frame/prd.md#problem |
| S4 | Positioning: a methodology you adopt, not a platform you join; runs on any runtime that reads and writes markdown; adopt incrementally | docs/helix/00-discover/product-vision.md#positioning, docs/helix/00-discover/product-vision.md#key-value-propositions |
| S5 | Four-step workflow contract: write the brief, check alignment, create the work plan, run it in the factory | docs/helix/01-frame/prd.md#core-workflow-contract |
| S6 | Target market: current solution is ad hoc prompting, manual document maintenance, hoping for the best; teams switch because every change traces back to a governing artifact and the alignment skill catches drift early | docs/helix/00-discover/product-vision.md#target-market |
| S7 | OAuth example: the alignment skill finds 3 feature specs and 2 solution designs affected, 1 ADR in conflict, 4 user stories to add, 1 test plan to revise, ordered by authority | docs/helix/00-discover/product-vision.md#user-experience |
| S8 | Targets: healthy artifact sets average < 3 alignment findings per run; 3 documented runtime deployments within 12 months; 50+ public repos within 18 months | docs/helix/00-discover/product-vision.md#success-definition, docs/helix/01-frame/prd.md#success-metrics |
| S9 | Non-goals: no CLI, tracker, queue, or execution engine; no technology choices imposed; no replacement for product, design, or architectural judgment; autonomy is a controllable spectrum | docs/helix/01-frame/prd.md#non-goals |

## Assumptions and gaps

- **Assumption**: the audience is engineering leadership evaluating adoption; inferred from the vision's target market. The operator should confirm before sending the deck.
- **Assumption**: the occasion is a 20-minute evaluation call; inferred from the audience. Sets the 10-slide budget from the evaluation-briefing flow.
- **Assumption**: the decision sought is a one-quarter trial on one project; the vision holds no ask, so this is the smallest reversible commitment consistent with adopting incrementally.
- **Gap**: the budget cuts the optional cost-and-risk beat; the requirements document's risks (noisy findings, slow adoption) go to the notes of slide 9 when asked.
- **Gap**: no artifact holds the presenter or call date; both come from the meeting invite at render time.

## Render

- **Theme**: deliverables/theme.yml (HELIX ships no design-system artifact of its own)
- **Targets**: docs/helix/06-iterate/deliverables/assets/DEL-001-helix-evaluation-deck.pptx (rendered by scripts/render-deck.js from this script), docs/helix/06-iterate/deliverables/assets/DEL-001-helix-evaluation-deck.pdf (LibreOffice export of the pptx)
- **Gate**:
  - Titles: headline pass clean; check-deliverable.py reports no title.slop and no horizontal_logic findings.
  - Script checks: pass, 0 blocking, 1 warning accepted (slides 2 to 4 share the claim-evidence pattern with three different visuals: timeline, panels, helix); validate-instance.py 0 findings.
  - Horizontal logic: pass; the titles-only read in Story is the argument and ends in the ask.
  - Vertical logic: pass; each body carries the evidence its title claims, and slide 8's title states the number as a target.
  - Fidelity: pass; every figure re-read against the sections in Sources.
  - Voice: pass; Vale with the Helix styles reports 0 errors.
  - Visual: pass. deck-qa.py rasterized all 12 slides through LibreOffice and reports 0 blocking findings (1 warning: the second sources page repeats the first's layout, by design). I inspected the contact sheet and slides 2 and 5 at full size on 2026-09-11; the first render clipped chevron labels on slide 5, fixed in the renderer's chevron inset and re-rendered.
  - File: pass; the presentation validator passes, 12 slides with speaker notes, no placeholder text.
  - Flow checklist (evaluation-briefing): titles move from the audience's problem to a trial; slide 4 names the category before any capability; slide 8 labels every number a target; slide 9 states four things HELIX does not do; the ask names one project, one quarter, one measure, with owner and date columns for the room; no body uses a term the audience would need defined.
