---
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
---

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
- **Must cover**: the artifact catalog and activity loop; the routing skill and alignment; concerns and principles; runtime boundary and autonomy; evidence and quality gates; human-facing deliverables
- **Must omit**: none
- **Max messages**: 5
- **Takeaway**: one document discipline governs agent work from intent to release, and your agents can have it without changing the tools you run

## Story

- **Flow**: evaluation-briefing
- **Takeaway**: one document discipline governs agent work from intent to release
- **Messages** (ranked by how much each moves the decision to run a trial):
  1. Teams working with agents today lose the disciplines human teams built. Specs, designs, and decisions drift until review or production catches it (evidence: docs/helix/00-discover/product-vision.md#why-now; docs/helix/01-frame/prd.md#problem)
  2. HELIX is a method, not a platform: 53 document templates across a seven-activity loop, and one skill that routes twenty-one modes over those documents (evidence: docs/helix/01-frame/prd.md#summary; workflows/README.md#activities; skills/helix/SKILL.md#routing-rules; docs/helix/01-frame/prd.md#core-workflow-contract)
  3. The discipline propagates and proves itself. Concerns and principles reach every document and task, and every claim of done carries evidence a validator can check (evidence: workflows/README.md#cross-cutting-context; docs/helix/01-frame/concerns.md; workflows/principles.md; docs/helix/01-frame/features/FEAT-016-artifact-honesty.md; workflows/ratchets.md; docs/helix/02-design/adr/ADR-009-acceptance-criteria-ownership.md)
  4. It runs on the runtime, tracker, and stack the team already has, and how much an agent does without asking is a dial the team sets (evidence: docs/helix/01-frame/prd.md#non-goals; docs/helix/01-frame/features/FEAT-013-runtime-install-coverage.md; docs/helix/02-design/adr/ADR-003-autonomy-spectrum.md)
  5. The same documents come back out as decks, briefs, and status reports people read, so the discipline pays off outside engineering too (evidence: docs/helix/01-frame/features/FEAT-017-iteration-documentation.md; workflows/modes/present.md)
- **Beats and titles** (titles written before any body):

  | # | Beat | Title (claim) | Message | Exhibit |
  |---|---|---|---|---|
  | 1 | takeaway | One document discipline governs agent work from intent to release | takeaway | title slide |
  | 2 | what-changed | Agents now write most production code without a shared practice | M1 | novelty-to-default timeline with the gap marked |
  | 3 | cost-of-today | Without that practice, agent code drifts from its governing documents | M1 | three failure panels |
  | 4 | what-it-is | HELIX answers with 53 document templates across a seven-activity loop | M2 | seven-row activity table |
  | 5 | what-it-is | One skill routes twenty-one modes over those documents | M2 | four mode panels |
  | 6 | how-it-works | The alignment check reads those documents before anyone codes | M2 | four-step flow with the alignment step highlighted |
  | 7 | what-changes | Fifty concerns carry shared practices into every document | M3 | four panels: concerns, principles, slots, spread |
  | 8 | proof | Every shared practice ends in evidence a validator can check | M3 | claim versus evidence, two columns |
  | 9 | boundaries | HELIX checks your documents and leaves your runtime and stack alone | M4 | boundary box: your tools around HELIX |
  | 10 | what-changes | Those documents also become the decks and status reports people read | M5 | three output panels |
  | 11 | ask | Pilot HELIX for one quarter and count what the documents catch | takeaway | ask band and three steps |
  | 12 | sources | Sources | all | source table |

- **Concept coverage** (every concept group the inventory surfaced, in authority order; inventory: 56 documents, 79,885 words, top 60 recurring concepts clustered into twelve groups):

  | # | Concept group | Authority | Status | Carried by / reason |
  |---|---|---|---|---|
  | 1 | The problem: drift, contradiction, lost context in agent-written work | vision, PRD | covered | M1 |
  | 2 | The artifact catalog and authority hierarchy (53 types, templates, prompts, quality criteria) | PRD, README, artifact-hierarchy | covered | M2 |
  | 3 | The seven-activity loop and its gates | README, conventions | covered | M2 |
  | 4 | The routing skill: twenty-one modes, alignment as the required one, the four-step contract | PRD, SKILL.md | covered | M2 |
  | 5 | Concerns, principles, and slots that propagate practices | README, concerns.md, principles.md | covered | M3 |
  | 6 | Evidence and quality: acceptance criteria ownership, claims-vs-reality, ratchets, validators | FEAT-016, ADR-009, ratchets | covered | M3 |
  | 7 | Runtime boundary, portability, and packaging (no CLI, tracker, or engine; six hosts) | PRD non-goals, FEAT-013, CONTRACT-001 | covered | M4 |
  | 8 | The autonomy spectrum and stop triggers | ADR-003, FEAT-011 | covered | M4 |
  | 9 | Human-facing outputs: iteration documents and deliverables | FEAT-017, present mode | covered | M5 |
  | 10 | Self-application: HELIX's own architecture, contracts with DDx, tracker data design | architecture, CONTRACT-001 to 003, data-design | omitted | audience: internal engineering detail of how HELIX builds itself, not what an adopter gets |
  | 11 | The public microsite and demos | FEAT-007, FEAT-012 | omitted | audience: marketing surface, not the method |
  | 12 | Success targets (findings per run, runtimes, repositories) | vision, PRD | covered | ask, as the measure of the trial |

- **Horizontal-logic test**: pass. Read in order, the titles move from the audience's change (2) to its cost (3), to what HELIX is (4, 5), how it works (6), what propagates (7), how it proves itself (8), what it leaves alone (9), what comes out for people (10), and a trial sized by the documents' own measure (11); each title reuses a word from the one before, and the ask repeats "documents" from the takeaway.

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

### 6. The alignment check reads those documents before anyone codes

**Pattern**: process-flow
**Body**:
- Write the brief: intent, requirements, constraints, decisions
- Check alignment: drift, contradictions, stale assumptions
- Plan the work: bounded items with scope and evidence
- Run it: your own runtime executes, measures, reports back
**Visual**: kind: process-flow | steps: Write the brief; Check alignment; Plan the work; Run it | highlight: 2 | caption: the step nobody does by hand today. Four-step flow from the requirements document's workflow contract
**Notes**: This is the four-step contract the requirements document commits to. On one OAuth change in the vision's worked example, the alignment check found three affected specs, one conflicting decision, and four missing stories before anyone wrote code.
**Sources**: S7, S8

### 7. Fifty concerns carry shared practices into every document

**Pattern**: claim-evidence
**Body**:
- A concern is a cross-cutting rule set: accessibility, security, verification, data quality
- Each concern names the practices every downstream document and task inherits
- Principles settle tensions the same way each time, starting with spec is the contract
- Exclusive slots hold one choice each: one frontend framework, one runtime, one auth provider
**Visual**: kind: panels | items: Concerns / 50 cross-cutting rule sets; Principles / how tensions get resolved; Slots / one filler per exclusive position; Spread / into every document and task. Four panels from the workflow's cross-cutting context and the principles file
**Notes**: This is what keeps a team's agents consistent with each other as well as with the specs. The team selects a concern once during framing; it then propagates and nobody re-decides it per task. Slots are why two agents cannot pick two frontend frameworks.
**Sources**: S9, S10

### 8. Every shared practice ends in evidence a validator can check

**Pattern**: two-column-comparison
**Body**:
- Claim: a test covers a requirement
- Evidence: the test cites the requirement it exercises, by id
- Claim: the work is complete
- Evidence: a validator ran and the record names the command and the guard branches
**Visual**: kind: two-column | left: The claim | right: The evidence HELIX requires | rows: A test covers a requirement / The test cites the requirement it exercises, by id; The work is complete / A validator ran and the record names the command and the guard branches; Someone promises a metric / The metric definition and its dashboard row exist | prefer: right | verdict: a claim without evidence blocks the work as a phantom claim. Two columns from the artifact-honesty feature and the acceptance-criteria decision
**Notes**: The artifact-honesty rule: any assertion of a test, a coverage figure, or a metric that does not exist is a blocking finding, not a style note. A quality floor, once reached, never slides back. The templates' own checks now run as scripts.
**Sources**: S11, S12

### 9. HELIX checks your documents and leaves your runtime and stack alone

**Pattern**: claim-evidence
**Body**:
- No command-line tool, tracker, queue, or execution engine ships with it
- It installs on six hosts today, from Claude Code to Databricks Genie
- Your technology choices stay yours; HELIX imposes none
- How much an agent does without asking is a three-position dial you set
**Visual**: kind: boundary | outer: your runtime and tools | outer-note: tracker, queue, CI, stack, judgment | inner: HELIX | inner-note: templates plus one skill | caption: reads and writes your documents, asks before anything irreversible. Boundary diagram from the requirements document's non-goals
**Notes**: The non-goals from the requirements document, and the autonomy decision: low asks before each step, medium pauses on ambiguity, high records assumptions and proceeds, and a hard floor of stop triggers holds at every level. This answers the objection every platform team is forming by now.
**Sources**: S13, S14, S15

### 10. Those documents also become the decks and status reports people read

**Pattern**: claim-evidence
**Body**:
- Roadmaps, iteration plans, and status reports come from the same governed documents
- A status report cites evidence per claim; a client cut never contradicts it
- A deck or brief projects the documents in a human voice, every number sourced
- This deck came out of that pipeline, with its own gates and inspection
**Visual**: kind: panels | items: Status reports / evidence per claim against the plan; Decks and briefs / the human-facing projection; Release notes / from the deploy documents. Three output panels from the iteration-documentation feature and the present mode
**Notes**: The discipline is not only for engineers. The iteration documents exist for people who coordinate, and the present mode exists for people outside the project. Say that this deck is the worked example: its script, its sources, and its inspection record are in the repository.
**Sources**: S16, S17

### 11. Pilot HELIX for one quarter and count what the documents catch

**Pattern**: ask-next-steps
**Body**:
- Pick one active project with an agent already in the loop, by the end of this week
- Adopt the templates and run one alignment check on its documents in the first sprint
- Review the findings together after four weeks against the bar of under 3 drift findings per check
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

## Assumptions and gaps

- **Assumption**: the audience is engineering leadership evaluating adoption; inferred from the vision's target market. The operator should confirm before sending the deck.
- **Assumption**: the occasion is a 20-minute evaluation call; inferred from the audience. Sets the 10-slide budget from the evaluation-briefing flow.
- **Assumption**: the decision sought is a one-quarter trial on one project; the vision holds no ask, so this is the smallest reversible commitment consistent with adopting incrementally.
- **Assumption**: survey breadth, because the previous cut of this deck covered only the drift problem and the operator asked for the whole method; the concept coverage table records what a survey at this budget still leaves out.
- **Gap**: the budget cuts the optional cost-and-risk beat; the requirements document's risks (noisy findings, slow adoption) go to the notes of slide 9 when asked.
- **Gap**: the concern count (50) and the mode count (21) come from the library and the routing table, content files instead of governing artifacts; the PRD states neither number.
- **Gap**: no artifact holds the presenter or call date; both come from the meeting invite at render time.

## Render

- **Theme**: deliverables/theme.yml (HELIX ships no design-system artifact of its own)
- **Targets**: docs/helix/06-iterate/deliverables/assets/DEL-001-helix-evaluation-deck.pptx (rendered by scripts/render-deck.js from this script), docs/helix/06-iterate/deliverables/assets/DEL-001-helix-evaluation-deck.pdf (LibreOffice export of the pptx)
- **Gate**:
  - Titles: headline pass clean; check-deliverable.py reports no title.slop and no horizontal_logic findings.
  - Coverage: twelve concept groups from the inventory (56 documents, 79,885 words), ten covered and two omitted with reasons; all six must-cover concepts carried; survey breadth satisfied.
  - Script checks: pass, 0 blocking, 0 warnings; validate-instance.py 0 findings.
  - Horizontal logic: pass; the titles-only read in Story is the argument and ends in the ask.
  - Vertical logic: pass; each body carries the evidence its title claims, and the counts on slides 4, 5, and 7 come from the sections in Sources.
  - Fidelity: pass; every figure re-read against the sections in Sources.
  - Voice: pass; Vale with the Helix styles reports 0 errors.
  - Visual: pass. deck-qa.py rasterized all 14 slides through LibreOffice and reports 0 blocking findings (2 warnings: the second and third sources pages repeat the first's layout, by design). I inspected the contact sheet on 2026-09-11; the first render split the activity table onto a continuation slide and wrapped one panel label mid-word, fixed in the renderer's table pagination and panel padding and by renaming the label, then re-rendered and re-inspected.
  - File: pass; the presentation validator passes, 14 slides with speaker notes, no placeholder text.
  - Flow checklist (evaluation-briefing): titles move from the audience's problem to a trial; slide 4 names the category (a method: templates and one skill) before any capability; the ask labels its number a target; slide 9 states four things HELIX does not do; the ask names one project, one quarter, one measure, with owner and date columns for the room; no body uses a term the audience would need defined.
