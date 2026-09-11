---
title: "One document discipline governs agent work from intent to release"
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
    - id: FEAT-016
      kind: informed_by
    - id: FEAT-017
      kind: informed_by
    - id: ADR-003
      kind: informed_by
```

# One document discipline governs agent work from intent to release

## Brief

- **Audience**: engineering leaders (head of platform, VP of engineering) whose teams build with AI agents and who decide which practices those teams adopt
- **Occasion**: a 20-minute evaluation call, presented live, then sent as a PDF
- **Decision or action sought**: run HELIX on one real project for one quarter and count what the documents catch
- **Time slot or page budget**: 20 minutes, 10 content slides
- **Kind**: deck
- **Constraints**: HELIX house theme; no customer names; targets labeled as targets, never as results
- **Scope**: docs/helix; workflows/README.md; workflows/principles.md; workflows/ratchets.md; workflows/conventions.md; workflows/artifact-hierarchy.md; workflows/concerns; skills/helix/SKILL.md
- **Breadth**: survey
- **Angle**: none
- **Must cover**: the artifact catalog and activity loop; the routing skill and alignment; layered authority as control; concerns and principles; human and agent hand-offs; runtime boundary and autonomy; evidence and quality gates; human-facing deliverables
- **Must omit**: none
- **Max messages**: 5
- **Takeaway**: one document discipline governs agent work from intent to release, and your agents can have it without changing the tools you run

## Story

- **Flow**: evaluation-briefing
- **Takeaway**: one document discipline governs agent work from intent to release
- **Messages** (ranked by how much each moves the decision to run a trial):
  1. Teams working with agents lose the disciplines human teams built; specs, designs, and decisions drift until review catches it (evidence: docs/helix/00-discover/product-vision.md#why-now; docs/helix/01-frame/prd.md#problem)
  2. HELIX is a method, not a platform: 53 document templates across a seven-activity loop, and one skill that routes twenty-one modes over those documents (evidence: docs/helix/01-frame/prd.md#summary; workflows/README.md#activities; skills/helix/SKILL.md#routing-rules)
  3. The layers are the control. Each layer governs the next, concerns and gates carry that control down, and every claim of done ends in evidence (evidence: workflows/artifact-hierarchy.md#the-hierarchy-is-the-control-loop; workflows/principles.md#layers-are-the-control; workflows/README.md#cross-cutting-context; docs/helix/01-frame/features/FEAT-016-artifact-honesty.md)
  4. People decide and agents draft, at governed hand-offs: approval, the autonomy level, stop triggers, escalation; and it all runs on the runtime and stack the team already has (evidence: workflows/principles.md#humans-decide-agents-draft; workflows/README.md#human-ai-collaboration; docs/helix/02-design/adr/ADR-003-autonomy-spectrum.md; docs/helix/01-frame/prd.md#non-goals)
  5. The same documents come back out as decks, briefs, and status reports people outside engineering read (evidence: docs/helix/01-frame/features/FEAT-017-iteration-documentation.md; workflows/modes/present.md)
- **Beats and titles** (titles written before any body):

  | # | Beat | Title (claim) | Message | Exhibit |
  |---|---|---|---|---|
  | 1 | takeaway | One document discipline governs agent work from intent to release | takeaway | title slide |
  | 2 | what-changed | Agents now write most production code without a shared practice | M1 | novelty-to-default timeline with the gap marked |
  | 3 | cost-of-today | Without that practice, agent code drifts from its governing documents | M1 | three failure panels |
  | 4 | what-it-is | HELIX answers with 53 document templates across a seven-activity loop | M2 | seven-row activity table |
  | 5 | what-it-is | One skill routes twenty-one modes over those documents | M2 | four mode panels |
  | 6 | how-it-works | Each document layer governs the next, from vision down to code | M3 | five-step layer flow |
  | 7 | what-changes | Concerns and gates carry that control across every layer | M3 | without and with layered control, two columns |
  | 8 | what-changes | Every layer also yields documents people outside engineering read | M5 | three-row outputs table |
  | 9 | proof | One alignment gate caught three drifted documents before anyone coded | M3 | four count panels from the worked example |
  | 10 | boundaries | At every gate a person decides and an agent drafts | M4 | people hold versus agents hold, two columns |
  | 11 | ask | Pilot HELIX for one quarter and count what each gate catches | takeaway | ask band and three steps |
  | 12 | sources | Sources | all | source table |

- **Concept coverage** (every group the inventory surfaced, in authority order; inventory: 56 documents, three passes: recurring concepts, catalog structure, roles and hand-offs, plus the authority floor of top-ranked headings):

  | # | Concept group | Authority | Status | Carried by / reason |
  |---|---|---|---|---|
  | 1 | The problem: drift, contradiction, lost context in agent-written work | vision, PRD | covered | M1 |
  | 2 | The artifact catalog and authority hierarchy (53 types, templates, prompts, quality criteria) | PRD, README, artifact-hierarchy | covered | M2 |
  | 3 | The seven-activity loop | README, conventions | covered | M2 |
  | 4 | The routing skill: twenty-one modes, alignment as the required one, the four-step contract | PRD, SKILL.md | covered | M2 |
  | 5 | Layered authority as control: each layer governs the next, a change enters at the top layer it affects (structure pass S1) | artifact-hierarchy, principles, graph | covered | M3 |
  | 6 | Cross-layer propagation and gates: 50 concerns with practices, gates between activities, floors that never slide back (structure S2, S3) | README, concerns, GATE files, ratchets | covered | M3 |
  | 7 | Evidence and quality: acceptance criteria ownership, claims-vs-reality, validators | FEAT-016, ADR-009 | covered | M3 |
  | 8 | Where humans and agents meet: approval, autonomy level, stop triggers, escalation, review (roles pass; README collaboration; principles) | principles, README, ADR-003, FEAT-011 | covered | M4 |
  | 9 | Runtime boundary and portability (no CLI, tracker, or engine; six hosts) | PRD non-goals, FEAT-013 | covered | M4 |
  | 10 | Human-facing outputs: iteration documents and deliverables | FEAT-017, present mode | covered | M5 |
  | 11 | Self-application: HELIX's own architecture, contracts with DDx, tracker data design | architecture, CONTRACT-001 to 003, data-design | omitted | audience: internal engineering detail of how HELIX builds itself, not what an adopter gets |
  | 12 | The public microsite and demos | FEAT-007, FEAT-012 | omitted | audience: marketing surface, not the method |
  | 13 | Success targets (findings per run, runtimes, repositories) | vision, PRD | covered | ask, as the measure of the trial |

- **Horizontal-logic test**: pass. Read in order, the titles move from the audience's change (2) to its cost (3), to what HELIX is (4, 5), how the layers control the work (6, 7), what comes out for people (8), proof at one gate (9), who decides at every gate (10), and a trial that counts what each gate catches (11); each title reuses a word from the one before, and the ask repeats "gate" from slides 7 to 10 and "documents" from the takeaway.

## Content

### 1. One document discipline governs agent work from intent to release

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

### 3. Without that practice, agent code drifts from its governing documents

**Pattern**: claim-evidence
**Body**:
- Specs, designs, and tests fall out of sync because nobody walks them between sessions
- A feature ships whose design contradicts a decision recorded months earlier
- Each new conversation re-improvises the workflow, so reviews that should happen do not
**Visual**: kind: panels | items: Drift / specs and code diverge between sessions; Contradiction / a design ignores an earlier decision; Lost context / every session starts from zero. Three failure panels from the requirements document's problem statement
**Notes**: These are the three failure modes the requirements document names. Each shows up late, in review or in production, which is why the cost is high. Ask which one the audience saw last week.
**Sources**: S3

### 4. HELIX answers with 53 document templates across a seven-activity loop

**Pattern**: table
**Body**:
- Discover: vision, business case, market and competitive analysis
- Frame: requirements, features, user stories, concerns, principles
- Design: architecture, decisions, contracts, solution and technical designs
- Test: test plans and quality expectations written before code
- Build: implementation plans against those tests
- Deploy: checklists, runbooks, monitoring, release notes
- Iterate: metrics, backlog, iteration plans, status reports, deliverables
**Visual**: kind: table | columns: Activity / What the templates produce | rows: Discover / vision, business case, market and competitive analysis; Frame / requirements, features, user stories, concerns, principles; Design / architecture, decisions, contracts, solution and technical designs; Test / test plans and quality expectations, written before code; Build / implementation plans against those tests; Deploy / checklists, runbooks, monitoring, release notes; Iterate / metrics, backlog, iteration plans, status reports, deliverables | highlight: 2. Seven-row table from the workflow's activity list and the catalog
**Notes**: HELIX is a method you adopt, not a platform you join. Each template carries an authoring prompt and quality criteria, and the templates rank: vision governs requirements, requirements govern designs, designs govern tests and code. Every one of the 53 is optional; teams adopt one type at a time.
**Sources**: S4, S5

### 5. One skill routes twenty-one modes over those documents

**Pattern**: claim-evidence
**Body**:
- A single skill installs on the agent runtime and reads the same documents
- It routes each request to one mode: frame, align, evolve, review, present, and more
- Alignment is the required mode; it finds drift and hands back a plan
- The skill body is portable: no runtime commands, so it loads on any host
**Visual**: kind: panels | items: Frame / vision, requirements, stories; Align / drift, gaps, contradictions; Evolve / thread one change through; Present / decks, briefs, reports. Four of the twenty-one modes the routing table names
**Notes**: The team never invokes a HELIX command, because there is none. They invoke their agent, and the agent invokes the skill. The four panels are the modes this audience will use first; the rest are in the appendix source.
**Sources**: S4, S6

### 6. Each document layer governs the next, from vision down to code

**Pattern**: process-flow
**Body**:
- Vision: direction and who it is for
- Requirements: scope, outcomes, non-goals
- Designs: decisions, contracts, components
- Tests: acceptance before any code
- Code: only what the layers above authorize
**Visual**: kind: process-flow | steps: Vision; Requirements; Designs; Tests; Code | highlight: 5 | caption: a change enters at the top layer it touches and flows down. Five-step layer flow from the artifact hierarchy's control loop
**Notes**: This is the mechanism, not a filing order. An agent may act only within what the layer above authorizes. On one OAuth change the vision's worked example starts with the security architecture, then the specs, then the stories, and no code moves until then; slide 9 shows the count.
**Sources**: S19, S20

### 7. Concerns and gates carry that control across every layer

**Pattern**: two-column-comparison
**Body**:
- Without layers: each agent re-decides the framework, the auth provider, the test approach per task
- With layers: the team selects a concern once at framing and its practices propagate down
- Without layers: drift shows up in review or in production
- With layers: entry and exit gates stop work moving down, and quality floors never slide back
**Visual**: kind: two-column | left: Without layered control | right: With layered control | rows: Each agent re-decides framework, auth, and test approach per task / The team selects a concern once and its practices propagate down; Drift shows up in review or in production / Gates stop work moving down a layer; A claim of done goes unchecked / Every claim cites evidence a validator can check | prefer: right | verdict: the rules live in the layers, not in a prompt. Two columns from the principles and the cross-cutting context
**Notes**: Fifty concerns in the library, each with practices keyed to the activity they apply in. Exclusive slots (one frontend framework, one runtime, one auth provider) are why two agents cannot make two different choices. The artifact-honesty rule closes the loop: a claim without evidence blocks.
**Sources**: S9, S11, S19

### 8. Every layer also yields documents people outside engineering read

**Pattern**: table
**Body**:
- Status report: for sponsors and clients, from the iteration plan, evidence per claim
- Deck or brief: for executives and customers, from any governed set, every number sourced
- Release notes: for users and support, from the deploy documents
**Visual**: kind: table | columns: Output / Who reads it / Comes from | rows: Status report / sponsors and clients / the iteration plan, evidence per claim; Deck or brief / executives and customers / any governed document set, every number sourced; Release notes / users and support / the deploy documents | highlight: 2. Three-row outputs table from the iteration-documentation feature and the present mode
**Notes**: The discipline is not only for engineers. A client cut of a status report may subset the internal one but never contradict it. Say that this deck is the worked example: its script, its sources, and its inspection record are in the repository.
**Sources**: S16, S17

### 9. One alignment gate caught three drifted documents before anyone coded

**Pattern**: claim-evidence
**Body**:
- A team asked its agent to add OAuth login
- The alignment check found 3 affected feature specs and 2 affected designs
- It flagged 1 recorded decision that conflicted with the OAuth pattern
- It listed 4 missing user stories and 1 test plan to revise
**Visual**: kind: panels | items: 3 specs / affected by the change; 1 decision / in conflict with OAuth; 4 stories / missing and now listed; 1 test plan / to revise first. Four count panels from the vision's worked example
**Notes**: This is the worked example in the product vision, not a customer result. The order matters: the plan starts with the security architecture revision, then the specs, then the stories. The bar the product sets for itself, under 3 findings per check on a healthy project, is a target and belongs to the ask.
**Sources**: S8

### 10. At every gate a person decides and an agent drafts

**Pattern**: two-column-comparison
**Body**:
- People hold intent, judgment, and approval: what to build, which decision stands, when work is complete
- Agents hold throughput: drafting, checking, surfacing contradictions, recording evidence
- The autonomy level sets when an agent pauses; stop triggers name what it never does unasked
- All of it runs on the runtime, tracker, and stack you already have; HELIX ships none
**Visual**: kind: two-column | left: People hold | right: Agents hold | rows: What to build and which decision stands / Drafting every document in its template; Approval that turns a draft into authority / Checking each draft against the layer above; When the work is complete / Surfacing drift, contradictions, and gaps; How much runs unasked, a three-position dial / Stopping at the triggers and handing judgment back | prefer: left | verdict: the hand-offs have owners and rules, never an implied one. Two columns from the humans-decide principle and the collaboration table
**Notes**: The two strands of the helix share one loop with different jobs. Low autonomy asks before each step, medium pauses on ambiguity, high records assumptions and proceeds, and a hard floor of stop triggers holds at every level. Nothing here needs a new tool: no command-line tool, tracker, queue, or execution engine ships with HELIX, and it installs on six hosts today.
**Sources**: S21, S22, S15, S13, S14

### 11. Pilot HELIX for one quarter and count what each gate catches

**Pattern**: ask-next-steps
**Body**:
- Pick one active project with an agent already in the loop, by the end of this week
- Adopt the templates and run one alignment check on its documents in the first sprint
- Review the findings together after four weeks against the bar of under 3 findings per check
- Without a trial the practice stays improvised and drift keeps surfacing in review
**Visual**: kind: none | owners: ; ; | dates: ; ;. Ask band in the secondary hue, then three numbered steps with owner and date columns left blank for the audience to fill
**Notes**: Stop after the ask. The bar is a target the product sets for itself, not a result; say so. If asked about cost, the trial needs one champion and no new tooling.
**Sources**: S7, S18

### 12. Sources

**Pattern**: appendix-sources
**Body**:
- Every figure and claim above maps to a section of the product vision, the requirements document, a feature specification, a decision record, or the workflow documents listed below
**Visual**: kind: none. Two-column source list in caption size, claim on the left, document section on the right
**Notes**: Not presented.
**Sources**: S1

## Sources

| Id | Claim or figure | Governing artifact and section |
|---|---|---|
| S1 | A methodology and artifact catalog for AI-assisted teams: templates plus one skill | docs/helix/00-discover/product-vision.md#mission-statement |
| S2 | AI-assisted development went from novelty to default; most developers ship AI-touched code daily | docs/helix/00-discover/product-vision.md#why-now |
| S3 | Three failure modes: artifact drift, inconsistent agent behavior, lossy session boundaries | docs/helix/01-frame/prd.md#problem |
| S4 | Templates for 53 artifact types plus a single routing skill; no CLI, tracker, or execution loop | docs/helix/01-frame/prd.md#summary |
| S5 | The seven activities, the artifact loop, and the authority hierarchy | workflows/README.md#activities, workflows/README.md#authority-hierarchy, workflows/artifact-hierarchy.md |
| S6 | Twenty-one routed modes in the routing table; alignment is the required mode | skills/helix/SKILL.md#routing-rules, docs/helix/01-frame/prd.md#goals |
| S7 | Four-step contract: write the brief, check alignment, plan the work, run it | docs/helix/01-frame/prd.md#core-workflow-contract |
| S8 | OAuth example: three specs and two designs affected, one decision in conflict, four stories missing | docs/helix/00-discover/product-vision.md#user-experience |
| S9 | Concerns propagate practices downstream; the project's active concerns and slots; 50 concerns in the library | workflows/README.md#cross-cutting-context, docs/helix/01-frame/concerns.md, workflows/concerns |
| S10 | Seven principles, from spec is the contract to deliverable over machinery, with tension resolution | workflows/principles.md#principles, docs/helix/01-frame/principles.md |
| S11 | Artifact honesty: phantom claims block; verification evidence comes from the running system | docs/helix/01-frame/features/FEAT-016-artifact-honesty.md, workflows/concerns/verification/practices.md |
| S12 | Tests cite the criterion they cover; quality floors never slide back | docs/helix/02-design/adr/ADR-009-acceptance-criteria-ownership.md, workflows/ratchets.md |
| S13 | Non-goals: no CLI, tracker, queue, or engine; no imposed technology; judgment stays with people | docs/helix/01-frame/prd.md#non-goals |
| S14 | Six install surfaces: DDx, Claude Code, Codex, Copilot, Databricks Genie, Grok Build | docs/helix/01-frame/features/FEAT-013-runtime-install-coverage.md, docs/install/README.md |
| S15 | Autonomy is a three-position spectrum with a hard-stop floor at every level | docs/helix/02-design/adr/ADR-003-autonomy-spectrum.md |
| S16 | Roadmap, iteration plan, status report; a client cut may subset but never contradict | docs/helix/01-frame/features/FEAT-017-iteration-documentation.md |
| S17 | Deliverables projected from governed artifacts, every number sourced, gated and inspected | workflows/modes/present.md, workflows/activities/06-iterate/artifacts/deliverable/meta.yml |
| S18 | Targets: < 3 findings per run; 3 runtimes in 12 months; 50+ repos in 18 months | docs/helix/00-discover/product-vision.md#success-definition, docs/helix/01-frame/prd.md#success-metrics |
| S19 | Layers are the control: each layer governs the next; a change enters at the top layer it affects; rules live in a layer, not a prompt | workflows/principles.md#layers-are-the-control |
| S20 | The hierarchy as control loop: authority flows down, concerns cross layers, gates sit between layers, humans hold the hand-offs | workflows/artifact-hierarchy.md#the-hierarchy-is-the-control-loop |
| S21 | Humans decide, agents draft: people own intent, judgment, approval; agents own drafting, checking, surfacing, recording; every hand-off has an owner and a rule | workflows/principles.md#humans-decide-agents-draft |
| S22 | Hand-off table: approval, autonomy level, stop triggers, escalation, surfaced judgment, and the rule behind each | workflows/README.md#human-ai-collaboration, docs/helix/00-discover/product-vision.md#key-value-propositions |

## Assumptions and gaps

- **Assumption**: the audience is engineering leadership evaluating adoption; inferred from the vision's target market. The operator should confirm before sending the deck.
- **Assumption**: the occasion is a 20-minute evaluation call; inferred from the audience. Sets the 10-slide budget from the evaluation-briefing flow.
- **Assumption**: the decision sought is a one-quarter trial on one project; the vision holds no ask, so this is the smallest reversible commitment consistent with adopting incrementally.
- **Assumption**: survey breadth, because the previous cut of this deck covered only the drift problem and the operator asked for the whole method; the concept coverage table records what a survey at this budget still leaves out.
- **Gap**: the budget cuts the optional cost-and-risk beat; the requirements document's risks (noisy findings, slow adoption) go to the notes of slide 9 when asked.
- **Assumption**: two concept groups (layered authority as control; where humans and agents meet) were under-stated in the corpus until 2026-09-11; the principles, hierarchy, README, and vision now state them, and the inventory's structure and roles passes surface them without those statements.
- **Gap**: the concern count (50) and the mode count (21) come from the library and the routing table, content files instead of governing artifacts; the PRD states neither number.
- **Gap**: no artifact holds the presenter or call date; both come from the meeting invite at render time.

## Render

- **Theme**: deliverables/theme.yml (HELIX ships no design-system artifact of its own)
- **Targets**: docs/helix/06-iterate/deliverables/assets/DEL-001-helix-evaluation-deck.pptx (rendered by scripts/render-deck.js from this script), docs/helix/06-iterate/deliverables/assets/DEL-001-helix-evaluation-deck.pdf (LibreOffice export of the pptx)
- **Gate**:
  - Titles: headline pass clean; check-deliverable.py reports no title.slop and no horizontal_logic findings.
  - Coverage: thirteen concept groups from the inventory's three passes (recurring concepts, catalog structure, roles and hand-offs) plus the authority floor; eleven covered across five messages, two omitted with reasons; all eight must-cover concepts carried, including layered authority as control and human and agent hand-offs; survey breadth satisfied.
  - Script checks: pass, 0 blocking, 0 warnings; validate-instance.py 0 findings.
  - Horizontal logic: pass; the titles-only read in Story is the argument and ends in the ask.
  - Vertical logic: pass; each body carries the evidence its title claims; the counts on slides 4, 5, and 9 come from the sections in Sources.
  - Fidelity: pass; every figure re-read against the sections in Sources, including the four sections added to the corpus on 2026-09-11 (S19 to S22).
  - Voice: pass; Vale with the Helix styles reports 0 errors (two long-sentence warnings in the Story's evidence lists).
  - Visual: pass. deck-qa.py rasterized all 16 slides through LibreOffice and reports 0 blocking findings (4 warnings: the four appendix continuation pages repeat the first's layout, by design). I inspected the contact sheet and slide 6 at full size on 2026-09-11; the first renders broke "Requirements" mid-word in the five-chevron flow and pushed the flow caption past the margin, fixed in the renderer (over-wide words now count as overflow so the fit shrinks them; five-step flows use a shallower chevron; captions clamp inside the slide), then re-rendered and re-inspected.
  - File: pass; the presentation validator passes, 16 slides with speaker notes, no placeholder text.
  - Flow checklist (evaluation-briefing): titles move from the audience's problem to a trial; slide 4 names the category (a method: templates and one skill) before any capability; the ask labels its number a target; slide 10 states what stays with people and what ships with nothing; the ask names one project, one quarter, one measure, with owner and date columns for the room; no body uses a term the audience would need defined.
