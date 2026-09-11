---
ddx:
  id: example.deliverable.depositmatch-pilot-deck
  type: deliverable
  activity: iterate
  kind: deck
  status: draft
  authoring:
    home: repo
    export:
      - docs/helix/06-iterate/deliverables/assets/DEL-001-depositmatch-pilot.pptx
      - docs/helix/06-iterate/deliverables/assets/DEL-001-depositmatch-pilot.html
      - docs/helix/06-iterate/deliverables/assets/DEL-001-depositmatch-pilot.pdf
  links:
    - id: example.business-case.depositmatch
      kind: informed_by
    - id: example.product-vision.depositmatch
      kind: informed_by
---

# A three-month pilot can win back reviewer hours at bookkeeping firms

## Brief

- **Audience**: the firm-owner sponsor and the two partners who approve product spend
- **Occasion**: monthly investment review, 20-minute slot, deck presented live then sent as PDF
- **Decision or action sought**: approve the three-month pilot budget and name who recruits pilot firms
- **Time slot or page budget**: 20 minutes, at most 10 content slides
- **Kind**: deck
- **Constraints**: no client names; figures marked as assumptions stay marked; house theme
- **Scope**: docs/helix/00-discover/business-case.md; docs/helix/00-discover/product-vision.md
- **Breadth**: deep-dive
- **Angle**: the investment decision
- **Must cover**: pilot scope; investment and breakeven; risks
- **Must omit**: none
- **Max messages**: 4
- **Takeaway**: a bounded CSV-first pilot is the cheapest way to learn whether reviewers trust suggested matches and whether firms will pay for the time saved

## Story

- **Flow**: proposal
- **Takeaway**: a bounded CSV-first pilot is the cheapest way to learn whether reviewers trust suggested matches and whether firms will pay
- **Messages** (ranked by how much each moves the decision to fund the pilot):
  1. Firms lose reviewer capacity to manual deposit matching every week, and the market is large enough to matter (evidence: docs/helix/00-discover/business-case.md#executive-summary; docs/helix/00-discover/business-case.md#opportunity-sizing)
  2. A CSV-first pilot learns about reviewer trust faster and cheaper than integrating bank feeds (evidence: docs/helix/00-discover/business-case.md#alternatives-considered)
  3. Year one costs $262,000 and the plan breaks even in month 18 if pilot conversion and pricing hold (evidence: docs/helix/00-discover/business-case.md#investment-required; docs/helix/00-discover/business-case.md#expected-roi)
  4. Three risks decide the pilot, each with a mitigation, and two conditions gate spend beyond it (evidence: docs/helix/00-discover/business-case.md#risk-assessment; docs/helix/00-discover/business-case.md#recommendation)
- **Beats and titles** (titles written before any body):

  | # | Beat | Title (claim) | Message | Exhibit |
  |---|---|---|---|---|
  | 1 | takeaway | A three-month pilot can win back reviewer hours at bookkeeping firms | takeaway | title slide |
  | 2 | recommendation | Approve a three-month pilot that shows reviewers the evidence behind each match | M2 | three-step process strip |
  | 3 | opportunity | Firms spend $1.2B a year on deposit matching; $180M is reachable | M1 | two stat callouts |
  | 4 | problem | Firms lose reviewer capacity to manual deposit matching every week | M1 | annotated spreadsheet |
  | 5 | alternatives | A CSV-first pilot tests reviewer trust faster than bank feeds | M2 | two-column comparison |
  | 6 | investment | Year one costs $262,000; the pilot plan breaks even in month 18 | M3 | cost table with breakeven marker |
  | 7 | risks | Three risks decide the pilot, and each one has a mitigation | M4 | risk grid |
  | 8 | conditions | Two conditions gate any spend beyond the pilot | M4 | two condition cards |
  | 9 | ask | Approve the pilot budget and name a pilot recruiter by month end | takeaway | ask band and steps |
  | 10 | sources | Sources | all | source table |

- **Concept coverage** (every concept group the inventory surfaced, in authority order):

  | # | Concept group | Authority | Status | Carried by / reason |
  |---|---|---|---|---|
  | 1 | Pilot scope: import, evidence-backed review, exception ownership | business case, vision | covered | M2 |
  | 2 | Market and opportunity sizing | business case | covered | M1 |
  | 3 | Investment and breakeven | business case | covered | M3 |
  | 4 | Risks and gating conditions | business case | covered | M4 |
  | 5 | Alternatives considered | business case | covered | M2 |
  | 6 | Strategic alignment with the firm's goals | business case | omitted | angle: the committee decides on cost and risk, and the goals row restates the pilot scope |
  | 7 | Product vision and positioning | vision | omitted | audience: the sponsor authored the vision; slide 4 carries the pain it names |

- **Horizontal-logic test**: pass. The titles move from the ask (2) through the size of the problem (3, 4), why this scope (5), what it costs (6), what could go wrong (7, 8), and back to the ask (9); each reuses a word from the one before, and the ask repeats "pilot" from the takeaway.

## Content

### 1. A three-month pilot can win back reviewer hours at bookkeeping firms

**Pattern**: title
**Body**:
- Investment review, prepared for the sponsor and approving partners
**Visual**: kind: none. Full-bleed dark surface with the deck title lower-left, the hollow marker motif on the right, and the review date beneath
**Notes**: Open with the takeaway sentence from the brief. Say up front that the ask comes on the last slide and takes two decisions.
**Sources**: S1

### 2. Approve a three-month pilot that shows reviewers the evidence behind each match

**Pattern**: claim-evidence
**Body**:
- The pilot builds three things and nothing else
- Reviewers see the evidence behind every suggested match before approving it
- Every exception has a named owner instead of a shared spreadsheet
- Spend beyond the pilot waits for two measured conditions
**Visual**: kind: process-flow | steps: Import; Review; Own exceptions | highlight: 2 | caption: reviewers see the evidence first. Three-step process strip drawn from the pilot scope in the business case, with the review step highlighted
**Notes**: This is the answer-first slide. The rest of the deck supports it: the size of the problem, why this scope, what it costs, what could go wrong, and what we need today.
**Sources**: S1, S2

### 3. Firms spend $1.2B a year on deposit matching; $180M is reachable

**Pattern**: stat-callout
**Body**:
- $1.2B spent yearly on reconciliation labor and tools across small firms
- $180M of that sits in firms of the size we can serve
- Both figures are planning assumptions until the research plan validates them
**Visual**: kind: stat | stats: $1.2B / spent yearly on reconciliation labor and tools across 60,000 small firms; $180M / within reach at the 9,000 firms of the size we can serve | label: planning assumption. Two stat callouts from the opportunity sizing, $1.2B in the primary hue and $180M in the secondary hue, the firm counts as baseline captions
**Notes**: The total assumes 60,000 small bookkeeping firms spending about $20,000 a year each. The reachable slice is the 9,000 firms with five to twenty-five staff. Say plainly that confidence is low and that the pilot is partly how we raise it.
**Sources**: S3, S4

### 4. Firms lose reviewer capacity to manual deposit matching every week

**Pattern**: claim-evidence
**Body**:
- Deposit matching is a weekly chore that competes with client work
- Matching happens across exports, bank statements, and email threads
- Closing the spreadsheet throws away the evidence behind each match
- Firm owners pay for saved time only when they can audit the result
**Visual**: kind: panels | items: Exports / matching happens across exports, bank statements, and email threads; Spreadsheet / closing it throws away the evidence behind each match; Audit / owners pay for saved time only when they can audit the result. Three panels standing in for the annotated matching-spreadsheet screenshot, each marking a place evidence goes missing
**Notes**: Keep this to the lived experience; the sponsor knows the pain. The point is that time saved without an audit trail is not something a firm will pay for.
**Sources**: S5

### 5. A CSV-first pilot tests reviewer trust faster than bank feeds

**Pattern**: two-column-comparison
**Body**:
- CSV-first: learns about reviewer trust in weeks; needs pilot recruiting and careful data handling
- Bank feeds first: stronger automation story; longer build, higher integration risk, slower learning
- Spreadsheet templates: cheapest; keeps no evidence and does not reduce context switching
- Verdict: CSV-first, because the open question is trust, not automation
**Visual**: kind: two-column | left: CSV-first pilot | right: Bank feeds first | rows: Learns about reviewer trust in weeks / Stronger automation story; Needs pilot recruiting and careful data handling / Longer build and higher integration risk; Answers the open question first / Slower learning about the open question | prefer: left | verdict: CSV-first, because the open question is trust, not automation. Two columns from the alternatives table in the business case with the check mark on the preferred column
**Notes**: The alternatives table in the business case also rejects doing nothing for a quarter; mention it only if asked. The comparison is about what we learn fastest.
**Sources**: S6

### 6. Year one costs $262,000; the pilot plan breaks even in month 18

**Pattern**: table
**Body**:
- Year one: $180,000 development, $12,000 infrastructure, $40,000 go-to-market, $30,000 operations
- Year one revenue of $120,000 leaves a $142,000 shortfall we fund deliberately
- Breakeven arrives in month 18 if pilot conversion and pricing hold
**Visual**: kind: table | columns: Year one line / Amount | rows: Development / $180,000; Infrastructure / $12,000; Go-to-market / $40,000; Operations / $30,000; Total / $262,000 | highlight: 5. Five-row cost table for year one from the investment section with the total row highlighted; the month-18 breakeven stays in the body
**Notes**: Years two and three are in the appendix source; do not present them unless a partner asks. The three-year return figure depends on pricing we have not validated, so lead with the year-one number the committee approves.
**Sources**: S7, S8

### 7. Three risks decide the pilot, and each one has a mitigation

**Pattern**: risk-matrix
**Body**:
- Exports vary too much: recruit pilots across three accounting systems, map per client
- Reviewers distrust suggestions: show evidence before approval, require reviewer acceptance
- Firms will not pay enough: validate willingness to pay before widening scope
**Visual**: kind: risk-grid | risks: Exports vary too much / high / medium; Reviewers distrust suggestions / medium / high; Firms will not pay enough / medium / high. Likelihood-by-impact grid from the risk assessment with the three risks as numbered dots and the mitigations from the body keyed by number on the right
**Notes**: The export-variability risk is the most likely and the one the recruiter can reduce before build starts, which is why the ask names a recruiter.
**Sources**: S9

### 8. Two conditions gate any spend beyond the pilot

**Pattern**: claim-evidence
**Body**:
- Recruit at least five pilot firms before expanding beyond import and review
- Measure median reconciliation time and suggestion accuracy during the first two months
- A paid product waits until weekly reconciliation falls under 3 minutes per client
**Visual**: kind: panels | items: Five pilot firms / recruited before expanding beyond import and review; Two measures / median reconciliation time and suggestion accuracy in the first two months. Two condition cards from the recommendation, with the 3-minute paid-product target in the body
**Notes**: These are the conditions in the business case recommendation. They are the sponsor's protection against scope creep and the team's protection against building on unvalidated demand.
**Sources**: S2, S10

### 9. Approve the pilot budget and name a pilot recruiter by month end

**Pattern**: ask-next-steps
**Body**:
- Approve the year-one pilot budget of $262,000 today
- Name the partner who recruits five pilot firms, by month end
- Product lead reports median reconciliation time at the two-month checkpoint
- No decision today delays the pilot a full quarter and keeps firms in manual matching
**Visual**: kind: none | owners: investment committee; a named partner; product lead | dates: today; month end; two-month checkpoint. Ask band in the secondary hue, then three numbered steps with owner and date columns filled from the body
**Notes**: Stop talking after the ask. If the committee wants the three-year numbers, they are in the appendix source and the business case.
**Sources**: S7, S10

### 10. Sources

**Pattern**: appendix-sources
**Body**:
- Every figure and claim above maps to a section of the business case or product vision listed below
**Visual**: kind: none. Two-column source list in caption size, claim on the left, artifact section on the right
**Notes**: Not presented.
**Sources**: S1

## Sources

| Id | Claim or figure | Governing artifact and section |
|---|---|---|
| S1 | Recommended investment is a three-month pilot build for CSV import, evidence-backed match review, and exception ownership | docs/helix/00-discover/business-case.md#executive-summary |
| S2 | Decision: Conditional Go; conditions: recruit at least five pilot firms; measure median reconciliation time and suggestion acceptance accuracy during the first two months | docs/helix/00-discover/business-case.md#recommendation |
| S3 | TAM $1.2B annual workflow spend: 60,000 small bookkeeping firms x $20,000; planning assumption, low confidence | docs/helix/00-discover/business-case.md#opportunity-sizing |
| S4 | SAM $180M: 9,000 firms with five to twenty-five employees x $20,000; medium confidence | docs/helix/00-discover/business-case.md#opportunity-sizing |
| S5 | Firms are losing reviewer capacity to manual deposit matching; firm owners will pay for auditability plus time saved | docs/helix/00-discover/business-case.md#executive-summary, docs/helix/00-discover/product-vision.md#positioning |
| S6 | Alternatives: CSV-first pilot (carry forward), bank feed and accounting sync first (reject for v1), spreadsheet templates (reject), do nothing for one quarter (reject) | docs/helix/00-discover/business-case.md#alternatives-considered |
| S7 | Year one: development $180,000, infrastructure $12,000, go-to-market $40,000, operations $30,000; total costs $262,000 | docs/helix/00-discover/business-case.md#investment-required, docs/helix/00-discover/business-case.md#expected-roi |
| S8 | Year one revenue $120,000, net $142,000 shortfall (shown as -$142,000); breakeven month 18; confidence low until the pilot validates conversion and pricing | docs/helix/00-discover/business-case.md#expected-roi |
| S9 | Risks: CSV exports vary (high, medium); reviewers distrust suggested matches (medium, high); firms will not pay enough (medium, high), each with the mitigation quoted | docs/helix/00-discover/business-case.md#risk-assessment |
| S10 | Paid product path if weekly reconciliation time falls below 3 minutes per client | docs/helix/00-discover/business-case.md#executive-summary |

## Assumptions and gaps

- **Assumption**: the committee approves year-one spend only; years two and three are informational. Inferred from the occasion (monthly investment review). The sponsor should confirm.
- **Gap**: the business case names no pilot recruiter; the ask has the committee name one instead of inventing an owner.
- **Gap**: no artifact holds the review date or presenter; both come from the meeting invite at render time.

## Render

- **Theme**: deliverables/theme.yml (no project design-system declared)
- **Targets**: docs/helix/06-iterate/deliverables/assets/DEL-001-depositmatch-pilot.pptx, docs/helix/06-iterate/deliverables/assets/DEL-001-depositmatch-pilot.html, docs/helix/06-iterate/deliverables/assets/DEL-001-depositmatch-pilot.pdf
- **Gate**: script checks pass (check-deliverable.py, 0 blocking); fidelity pass (every stat callout re-read against the business case); voice pass (Vale Helix styles, 0 errors); visual: every slide rendered to an image and inspected on 2026-09-10, one overflow on slide 6 fixed by shortening the third bullet; file: presentation validator pass, HTML page renders with no console errors
