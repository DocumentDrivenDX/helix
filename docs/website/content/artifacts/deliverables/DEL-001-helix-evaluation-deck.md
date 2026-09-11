---
title: "Your agents can ship with the discipline your best teams already use"
slug: DEL-001-helix-evaluation-deck
weight: 1020
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
      - docs/helix/06-iterate/deliverables/assets/DEL-001-helix-evaluation-deck.html
  links:
    - id: helix.product-vision
      kind: informed_by
    - id: PRD-001
      kind: informed_by
```

# Your agents can ship with the discipline your best teams already use

## Brief

- **Audience**: engineering leaders (head of platform, VP of engineering) whose teams build with AI agents and who decide what practices those teams adopt
- **Occasion**: a 20-minute evaluation call, presented live, then sent as a PDF or the HTML deck
- **Decision or action sought**: run HELIX on one real project for one quarter and measure the drift it catches
- **Time slot or page budget**: 20 minutes, at most 10 content slides
- **Kind**: deck
- **Constraints**: HELIX house theme; no customer names; targets stay labeled as targets, not results
- **Takeaway**: give your agents the same document discipline your best teams already use, and drift stops being a surprise

## Story

- **Spine**: situation-complication-resolution
- **Titles-only read**:
  1. Your agents can ship with the discipline your best teams already use
  2. AI-assisted development is now the default, and the practice behind it is not
  3. Three failures repeat on every AI-assisted team: drift, local decisions, lost context
  4. Teams switch when every change traces back to a governing document
  5. HELIX is a methodology you adopt, not a platform you join
  6. Write the brief, check alignment, plan the work, run it in your own factory
  7. Five things change once the catalog and the alignment skill are in place
  8. Fewer than 3 alignment findings per run is the health bar we hold ourselves to
  9. HELIX takes no runtime, no tracker, and no technology choice away from you
  10. Run HELIX on one project this quarter and measure the drift it catches
  11. Sources

## Content

### 1. Your agents can ship with the discipline your best teams already use

**Pattern**: title
**Body**:
- An evaluation briefing for engineering leaders whose teams build with AI agents
**Visual**: full-bleed indigo surface, the title lower-left in Georgia, a thin terracotta rule under the subtitle, date bottom-left
**Notes**: Open with the takeaway sentence. Say that the ask is one pilot project for one quarter and that it comes on the last slide.
**Sources**: S1

### 2. AI-assisted development is now the default, and the practice behind it is not

**Pattern**: claim-evidence
**Body**:
- Most professional developers ship AI-touched code every day
- The work is locally good and globally inconsistent
- The disciplines human teams built over decades never reached the agents
- This era will have its equivalent of test-driven development
**Visual**: a two-band timeline drawn from the vision's Why Now section: "novelty" fading into "default practice", with a gap marker labeled "no shared methodology" under the second band
**Notes**: This is the situation. Agents are ready; teams improvise the methodology around them. Do not argue the premise; most leaders in this audience live it.
**Sources**: S2

### 3. Three failures repeat on every AI-assisted team: drift, local decisions, lost context

**Pattern**: claim-evidence
**Body**:
- Specs, designs, and tests fall out of sync because nobody walks them between sessions
- A feature ships whose design contradicts a decision recorded months earlier
- Each new conversation re-improvises the workflow, so reviews that should happen do not
**Visual**: three-panel illustration keyed to the PRD's failure modes: a spec and code diverging, a decision record with a red conflict marker, a chat window closing with context spilling out
**Notes**: These are the three failure modes the requirements document names. Each one shows up late, in review or in production, which is why the cost is high.
**Sources**: S3

### 4. Teams switch when every change traces back to a governing document

**Pattern**: two-column-comparison
**Body**:
- Today: ad hoc prompting, manual document upkeep, and hoping for the best
- With HELIX: agents and people share one methodology, and every change traces to a governing document
- Today: drift surfaces in review or production
- With HELIX: an alignment pass catches drift early, before it accumulates
**Visual**: two columns headed "Today" and "With HELIX" with two parallel rows each and the check mark on the right column
**Notes**: The target-market table in the vision. The left column is what the audience recognizes; the right column is the claim the rest of the deck has to earn.
**Sources**: S4

### 5. HELIX is a methodology you adopt, not a platform you join

**Pattern**: claim-evidence
**Body**:
- A catalog of document templates, from product intent through deployment and feedback
- One skill that keeps those documents aligned as the work moves
- Content that runs on any agent runtime that reads and writes markdown
- No lock-in: adopt one document type at a time
**Visual**: a double-helix diagram from the vision's mission: the document strand (intent, design, tests) and the execution strand (the team's runtime) joined by rungs labeled "alignment"
**Notes**: The double helix is the product's own metaphor. The point for this audience is the last bullet: adoption is incremental and reversible.
**Sources**: S1, S5

### 6. Write the brief, check alignment, plan the work, run it in your own factory

**Pattern**: process-flow
**Body**:
- Write the brief: intent, requirements, constraints, decisions
- Check alignment: find drift, contradictions, stale assumptions
- Plan the work: bounded items with scope and evidence expectations
- Run it in your factory: your runtime executes, measures, and reports back
**Visual**: four-step chevron flow left to right in indigo with the "check alignment" step in terracotta, a caption beneath it reading "the step nobody does by hand today"
**Notes**: This is the four-step contract the requirements document commits to. Walk the OAuth example from the vision: the alignment pass finds the three affected specs, the conflicting decision, and the missing stories, ordered by authority, before anyone writes code.
**Sources**: S6, S7

### 7. Five things change once the catalog and the alignment skill are in place

**Pattern**: table
**Body**:
- Authority-ranked catalog: changes propagate predictably
- Single alignment skill: drift caught early, no manual walk
- Portable content: runs on any runtime that reads markdown
- Document-driven reviews: audits documents, not chat transcripts
- Methodology, not platform: adopt incrementally, no lock-in
**Visual**: a five-row, two-column table (capability, what changes for your team) from the vision's value propositions, the alignment row highlighted, full width beneath the title
**Notes**: The fifth item, methodology not platform, is already on slide 5; leave it in the table and do not repeat it aloud.
**Sources**: S8

### 8. Fewer than 3 alignment findings per run is the health bar we hold ourselves to

**Pattern**: stat-callout
**Body**:
- Under 3 findings per alignment run on a healthy document set
- 3 runtimes documented within 12 months
- 50 or more public repositories using the catalog within 18 months
**Visual**: three stat callouts in a row, "< 3", "3", and "50+", each with a one-line caption and a "target" label in muted text
**Notes**: These are targets, not results; say so. The first one is the bar for judging a pilot, which sets up the ask.
**Sources**: S9

### 9. HELIX takes no runtime, no tracker, and no technology choice away from you

**Pattern**: claim-evidence
**Body**:
- No command-line tool, tracker, queue, or execution engine ships with it
- No technology choices imposed; your stack stays yours
- No replacement for product, design, or architectural judgment
- How much an agent does without asking is a dial you set
**Visual**: a boundary diagram: a box labeled "your runtime and tools" wrapping a smaller box labeled "HELIX: templates + one skill", with arrows only from the smaller box outward
**Notes**: The non-goals from the requirements document. This slide answers the objection every platform team raises, so give it time.
**Sources**: S10

### 10. Run HELIX on one project this quarter and measure the drift it catches

**Pattern**: ask-next-steps
**Body**:
- Pick one active project with an agent already in the loop, by the end of this week
- Adopt the catalog and run an alignment pass on its documents in the first sprint
- Review the findings together after four weeks and decide whether to widen
- Without a pilot the practice stays improvised and drift keeps surfacing late
**Visual**: ask band in terracotta on the alternate surface, then three numbered steps with owner and date columns left blank for the audience to fill
**Notes**: Stop after the ask. If asked about cost, the answer is that the pilot needs one champion and no new tooling.
**Sources**: S6, S9

### 11. Sources

**Pattern**: appendix-sources
**Body**:
- Every figure and claim above maps to a section of the product vision or requirements document listed below
**Visual**: two-column source list in caption size, claim on the left, document section on the right
**Notes**: Not presented.
**Sources**: S1

## Sources

| Id | Claim or figure | Governing artifact and section |
|---|---|---|
| S1 | HELIX is a methodology and artifact catalog for AI-assisted teams; the double helix of a document strand and an execution runtime | docs/helix/00-discover/product-vision.md#mission-statement |
| S2 | AI-assisted development crossed from novelty to default; most professional developers ship AI-touched code daily; locally good, globally inconsistent; the TDD-equivalent practice | docs/helix/00-discover/product-vision.md#why-now |
| S3 | Three failure modes: artifact drift, inconsistent agent behavior (a feature whose design contradicts an earlier ADR), lossy session boundaries | docs/helix/01-frame/prd.md#problem |
| S4 | Target market: current solution is ad hoc prompting and manual document maintenance; teams switch because every change traces back to a governing artifact and the alignment skill catches drift early | docs/helix/00-discover/product-vision.md#target-market |
| S5 | Positioning: a methodology you adopt, not a platform you join; runs on any runtime that reads and writes markdown; adopt incrementally, no lock-in | docs/helix/00-discover/product-vision.md#positioning, docs/helix/00-discover/product-vision.md#key-value-propositions |
| S6 | Four-step workflow contract: write the brief, check alignment, create the work plan, run it in the factory | docs/helix/01-frame/prd.md#core-workflow-contract |
| S7 | OAuth example: the alignment skill finds three feature specs, two designs, one conflicting decision, four missing stories, one test plan, ordered by authority | docs/helix/00-discover/product-vision.md#user-experience |
| S8 | Five value propositions: authority-ranked catalog, single alignment skill, portable content, document-driven reviews, methodology not platform | docs/helix/00-discover/product-vision.md#key-value-propositions |
| S9 | Targets: healthy artifact sets average < 3 alignment findings per run; 3 documented runtime deployments within 12 months; 50+ public repos within 18 months | docs/helix/00-discover/product-vision.md#success-definition, docs/helix/01-frame/prd.md#success-metrics |
| S10 | Non-goals: no CLI, tracker, queue, or execution engine; no technology choices imposed; no replacement for product, design, or architectural judgment; autonomy is a controllable spectrum | docs/helix/01-frame/prd.md#non-goals |

## Assumptions and gaps

- **Assumption**: audience is engineering leadership evaluating adoption; inferred from the vision's target market. The operator should confirm before sending the deck.
- **Assumption**: occasion is a 20-minute evaluation call; inferred from the audience. Sets the 10-slide budget.
- **Assumption**: the decision sought is a one-quarter pilot on one project; the vision holds no ask, so this is the smallest reversible commitment consistent with "adopt incrementally".
- **Gap**: the requirements document summary says "~32 artifact types" while the catalog holds 53; the deck omits the count instead of picking a side. Route to `align`.
- **Gap**: no artifact holds the presenter or call date; both come from the meeting invite at render time.

## Render

- **Theme**: deliverables/theme.yml (HELIX ships no design-system artifact of its own)
- **Targets**: docs/helix/06-iterate/deliverables/assets/DEL-001-helix-evaluation-deck.pptx, docs/helix/06-iterate/deliverables/assets/DEL-001-helix-evaluation-deck.html
- **Gate**:
  - Script checks: pass. check-deliverable.py reports 0 blocking and 0 warnings; validate-instance.py reports 0 findings.
  - Fidelity: pass. Every claim re-read against the product vision and PRD sections in Sources. The stale artifact-type count in the PRD summary stays out of the deck and sits under Assumptions and gaps.
  - Voice: pass. Vale with the Helix styles reports 0 errors.
  - Visual: pass. The HTML render ran in a browser at 1280x720 per slide; all 11 slides came out as images and I inspected each on 2026-09-10. The first pass showed a broken comparison layout on slide 4 (a stylesheet class collision), top-heavy frames on slides 2, 3, 6, and 8, and bullets restating the table on slide 7. All fixed and re-inspected; no console errors.
  - File: partial. The .pptx passes the presentation validator (schema, relationships, content types) with 11 slides, speaker notes, and no placeholder text. This host could not rasterize the .pptx (no LibreOffice; PowerPoint and Keynote scripted export timed out on automation permission), so one look at its slides in PowerPoint remains before anyone sends the deck.
