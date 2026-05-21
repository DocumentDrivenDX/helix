---
title: "PR-FAQ"
linkTitle: "PR-FAQ"
slug: pr-faq
activity: "Frame"
artifactRole: "supporting"
weight: 19
generated: true
---

## Purpose

Synthesize the source material into a launch-day press release and FAQ using
a working-backwards lens. The PR-FAQ is not marketing copy. It is the product
argument that proves the team understands the problem, the customer outcome,
the mechanism, the objections, and the adoption boundary before downstream
requirements are written.

## Authoring guidance

- Keep the press release customer-centric, future-facing, concise, and
  jargon-free.
- Start from the customer outcome, not from the team's existing capabilities.
- State the core thesis in one reusable sentence before elaborating in the
  internal sections.
- Name the mechanism that makes the outcome possible, not only the benefit.
- Define the quality bar for the context, data, behavior, or workflow the
  product depends on.
- Define the decision boundary. If the product automates, delegates, or
  recommends work, say what the system may decide, what assumptions it may
  record, and what must return to a human.
- Split the FAQ into customer-facing questions and internal decision
  questions.
- Use the FAQ to surface adoption blockers, feasibility concerns, business
  viability, validation needs, and credible reasons not to use the product.
- Call out assumptions and high-risk gaps instead of glossing over them.

_Additional guidance continues in the full prompt below._

<details>
<summary>Quality checklist from the prompt</summary>

- The press release is readable on its own and fits on roughly one page.
- The press release uses customer language and names a concrete customer
  problem or opportunity.
- The core thesis is one sentence and is captured before detailed internal
  explanation.
- The mechanism is explicit enough to test in the PRD or research plan.
- The quality model names the attributes the product must preserve.
- Decision and autonomy boundaries are neither vague nor over-escalating.
- Customer FAQ answers likely buyer/user questions in plain language.
- Internal FAQ answers the hard commitment questions: feasibility, viability,
  resourcing, risks, scope, kill criteria, and validation.
- The FAQ names who should not adopt the product.
- Next steps, experiments, and downstream projection targets are explicit.

</details>

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.pr-faq.depositmatch
  depends_on:
    - example.product-vision.depositmatch
    - example.opportunity-canvas.depositmatch
    - example.feasibility-study.depositmatch
    - example.compliance-requirements.depositmatch
  review:
    self_hash: 102ec8dcd77efb43d6a73143dc4dbfeb1fc95b0ab516a593166bb8b12dd70686
    deps:
      example.compliance-requirements.depositmatch: ec7fb87a927f7e53a9c323e9af8ee73d667e4520ab596c130077d332d2783c9f
      example.feasibility-study.depositmatch: 356da096953895f8c152a1ac8b880fbc03a3617c1c80516e6f0d3b4033a62c72
      example.opportunity-canvas.depositmatch: 75303097bfeeed0272bd68f90ef887f9a5e646a1272f9a57ccd0d899ae17497a
      example.product-vision.depositmatch: 8abbb2fcb552b536f07829f57d91ef3ae8dbf52a6066955222e83d196b59b5ae
    reviewed_at: "2026-05-15T04:11:24Z"
---
# PR-FAQ: DepositMatch

> Example scenario: a working-backwards PR-FAQ derived from the DepositMatch
> product vision example. It shows how a vision can turn into a customer-facing
> launch narrative, internal product argument, and hard-question FAQ.

## Press Release

**FOR IMMEDIATE RELEASE - AUSTIN, TEXAS - 2026-09-15**

### Headline

DepositMatch helps bookkeeping firms finish weekly deposit reconciliation in minutes.

### Subhead

The new reconciliation workspace suggests invoice matches, preserves evidence,
and turns unclear deposits into owned exceptions for small bookkeeping firms.

### Summary

DepositMatch today announced a reconciliation workspace for bookkeeping firms
serving recurring small-business clients. DepositMatch helps reviewers close
weekly deposit reconciliation faster by matching bank deposits to invoice
exports and keeping the evidence beside every decision. The product is
available today for private pilots with firms managing 5-25 employees.

### The Problem

Small bookkeeping firms spend 4-8 hours each week matching deposits to
invoices across bank exports, accounting reports, spreadsheets, and email.
As client volume grows, routine matching consumes reviewer time and unclear
deposits are easy to lose before month-end close.

### The Solution

DepositMatch imports bank deposits and invoice exports into one review queue.
It suggests matches with evidence, asks reviewers to approve before anything
is accepted, and routes unclear deposits into an exception list with an owner
and next action.

### Quote from Elena Ruiz, Founder

> "Bookkeepers do not need another accounting system. They need a reliable
> way to see what has matched, what has not, and why. DepositMatch gives firms
> a review trail they can trust before month-end pressure starts."

### How It Works

1. Upload a bank deposit CSV and invoice export for a client.
2. Review suggested matches grouped by confidence and evidence.
3. Accept routine matches, split deposits, or reject weak suggestions.
4. Assign every unresolved deposit to an exception owner.
5. Export the reconciliation log for client review.

### Customer Quote

> "We used to spend Monday mornings rebuilding the same spreadsheet for each
> client. In our pilot, most deposits were already grouped with the invoices
> we expected, and the exceptions were clear enough to assign before lunch."
>
> - Maya Patel, reconciliation lead at a 12-person bookkeeping firm

### Availability

DepositMatch is available in private pilot starting September 15, 2026. Pilot
firms can upload CSV exports from their accounting system and bank portal.
Pricing is $149 per firm per month during the pilot, including up to 25 active
clients.

---

## Internal Product Argument

### Core Thesis

Bookkeeping firms can grow client volume without adding reconciliation staff
when routine deposit matching becomes a trustworthy review queue.

### Mechanism

DepositMatch works by turning scattered financial exports into a decision
queue. The product suggests likely matches, shows the evidence behind each
suggestion, requires reviewer approval, and preserves exceptions as owned
work instead of letting them disappear into spreadsheets or email.

### Quality Model

| Attribute | Meaning | How We Know |
|---|---|---|
| Trustworthy | Reviewers can see why a match was suggested before accepting it | Every suggestion shows amount, date, payer, and invoice evidence |
| Bounded | The system never accepts a match without reviewer approval | Accepted matches require reviewer, timestamp, and source rows |
| Actionable | Unmatched deposits leave the session with an owner and next action | 90% of unresolved deposits have owner and next action within one business day |

### Decision / Autonomy Boundary

DepositMatch may suggest matches, group likely exceptions, and preserve the
evidence for review.

DepositMatch may mark low-confidence matches as exceptions and continue the
workflow without blocking routine review.

DepositMatch must not accept matches, post accounting entries, delete source
rows, or decide client follow-up without reviewer approval.

## FAQ

### External FAQs

#### How much does it cost?

Private pilot pricing is $149 per firm per month for up to 25 active clients.
General availability pricing will be set after pilot usage shows the median
number of reconciled clients per firm.

#### How is this different from QuickBooks, Xero, or a spreadsheet?

QuickBooks and Xero are accounting systems. DepositMatch is a focused review
workspace for firms that already export invoice and bank data. Spreadsheets
can track matches, but they do not preserve suggestion evidence, reviewer
approval, exception ownership, and client-level review logs in one workflow.

#### Who is this NOT for?

DepositMatch is not for firms that need full general-ledger posting,
companies reconciling only one internal business, or enterprises that require
direct bank-feed integrations before using any reconciliation workflow.

#### What's not in v1?

- Automatic journal posting.
- Direct bank-feed or accounting-platform sync.
- Payroll, inventory, tax, or credit-card reconciliation.
- Client-facing portals.

#### What platforms / regions / integrations are supported at launch?

The pilot supports modern desktop browsers and CSV imports from bank portals
and accounting exports. It is available to US-based bookkeeping firms during
the private pilot.

#### When can I get it?

Private pilot access begins September 15, 2026.

### Internal FAQs

#### What is the unit economics story? Is this profitable per customer?

At $149 per firm per month, the product is viable only if onboarding and
support stay lightweight. The pilot must prove that firms can configure CSV
column mappings without high-touch services support.

#### What is the riskiest technical assumption?

CSV exports may vary enough that matching quality drops or onboarding becomes
manual. The mitigation is per-client column mapping plus a pilot compatibility
set covering at least three common accounting exports.

#### What experiments must run before we commit?

1. Import sample CSV exports from at least three pilot firms.
2. Measure suggestion acceptance accuracy against reviewer audit samples.
3. Time weekly reconciliation for pilot clients before and after DepositMatch.

#### What is the smallest viable launch?

CSV import, match suggestions, reviewer approval, evidence log, and exception
ownership for weekly deposit reconciliation.

#### What must be true for the core thesis to hold?

Suggestions must be accurate enough to save reviewer time, transparent enough
to earn trust, and bounded enough that reviewers remain responsible for final
acceptance.

#### Where can the system keep moving, and where must it stop?

The system can keep moving by suggesting matches, grouping exceptions, and
recording next actions. It must stop before accepting a match, posting to an
accounting system, or deciding how to answer a client question.

#### Who else has to ship something for this to work?

Pilot firms must provide representative exports. The product team must ship
CSV column mapping, evidence display, and audit-log storage before pilot use.

#### What regulatory or legal exposure does this create?

DepositMatch handles financial records from small businesses. Pilot data must
be encrypted at rest, excluded from analytics events, and governed by a clear
retention policy.

#### How does this scale? What breaks at 10x and 100x usage?

At 10x, saved CSV mappings and import validation become critical. At 100x,
direct accounting integrations and queue performance become the likely
bottlenecks.

#### What are we choosing not to do, and why?

We are not replacing accounting systems because firms already use them as the
system of record. We are not posting journal entries because the first trust
problem is review quality, not accounting automation.

#### What would cause us to abandon this project?

Abandon the project if pilot reviewers accept fewer than 80% of high-confidence
suggestions after two import iterations, or if median reconciliation time does
not improve by at least 40%.

#### What does success look like 12 months after launch?

Fifty bookkeeping firms use DepositMatch weekly, median reconciliation time is
below 3 minutes per client, and accepted suggestion accuracy remains above 95%
in reviewer audit samples.

## Downstream Projection

| Target | What It Should Inherit | Owner / Status |
|---|---|---|
| PRD | Customer segment, problem cost, bounded automation model, pilot metrics | Product / drafted in PRD example |
| Principles | Trustworthy evidence and reviewer-owned final decisions | Product / candidate principle |
| Feature specs | CSV import, suggestion review, exception ownership, audit log | Product + Design / not started |
| Research plan | Pilot measurement for accuracy and time saved | Product / not started |
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="/reference/glossary/activities/"><strong>Frame</strong></a> — Define what the system should do, for whom, and how success will be measured.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/01-frame/pr-faq.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="/artifact-types/frame/prd/">PRD</a><br><a href="/artifact-types/frame/principles/">Principles</a><br><a href="/artifact-types/frame/stakeholder-map/">Stakeholder Map</a><br><a href="/artifact-types/frame/feature-specification/">Feature Specification</a></td></tr>
<tr><th>Referenced by</th><td><a href="/artifact-types/frame/prd/">PRD</a><br><a href="/artifact-types/design/solution-design/">Solution Design</a><br><a href="/artifact-types/frame/feature-specification/">Feature Specification</a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># PR/FAQ Prompt

## Purpose

Synthesize the source material into a launch-day press release and FAQ using
a working-backwards lens. The PR-FAQ is not marketing copy. It is the product
argument that proves the team understands the problem, the customer outcome,
the mechanism, the objections, and the adoption boundary before downstream
requirements are written.

## Research Basis

This artifact follows Amazon/AWS Working Backwards guidance: define the
intended customer experience first, write a concise future press release
before implementation commitment, then use customer and internal FAQs to
surface the most important questions before downstream requirements harden.
See:

- `docs/resources/amazon-working-backwards-prfaq.md`
- `docs/resources/working-backwards-prfaq-template.md`

## Key Principles

- Keep the press release customer-centric, future-facing, concise, and
  jargon-free.
- Start from the customer outcome, not from the team&#x27;s existing capabilities.
- State the core thesis in one reusable sentence before elaborating in the
  internal sections.
- Name the mechanism that makes the outcome possible, not only the benefit.
- Define the quality bar for the context, data, behavior, or workflow the
  product depends on.
- Define the decision boundary. If the product automates, delegates, or
  recommends work, say what the system may decide, what assumptions it may
  record, and what must return to a human.
- Split the FAQ into customer-facing questions and internal decision
  questions.
- Use the FAQ to surface adoption blockers, feasibility concerns, business
  viability, validation needs, and credible reasons not to use the product.
- Call out assumptions and high-risk gaps instead of glossing over them.
- Name which downstream artifacts or public pages should derive from this
  PR-FAQ so the argument does not drift into parallel prose.

## Method

1. Read the governing Product Vision and any existing PRD, principles,
   concern, research, or website narrative relevant to the scope.
2. Identify the customer, their context, the problem or opportunity, the
   proposed solution, the most important benefit, and how success can be
   tested.
3. Extract the strongest version of the product thesis. Prefer a plain,
   falsifiable statement over a slogan.
4. Identify the mechanism behind the thesis. For example, &quot;better context
   produces better agent work&quot; is a mechanism claim; &quot;teams ship faster&quot; is
   only an outcome claim.
5. Identify the decision or autonomy model. Avoid both extremes: do not imply
   humans make every real decision, and do not imply the system can run past
   judgment boundaries without supervision.
6. Write the press release as if the product already shipped, then write the
   FAQ as if a skeptical product, engineering, finance, legal, or operations
   reviewer is trying to find the weak points.
7. End with the downstream projection: the docs, site pages, requirements, or
   principles that should inherit this exact argument.

## Quality Checklist

- The press release is readable on its own and fits on roughly one page.
- The press release uses customer language and names a concrete customer
  problem or opportunity.
- The core thesis is one sentence and is captured before detailed internal
  explanation.
- The mechanism is explicit enough to test in the PRD or research plan.
- The quality model names the attributes the product must preserve.
- Decision and autonomy boundaries are neither vague nor over-escalating.
- Customer FAQ answers likely buyer/user questions in plain language.
- Internal FAQ answers the hard commitment questions: feasibility, viability,
  resourcing, risks, scope, kill criteria, and validation.
- The FAQ names who should not adopt the product.
- Next steps, experiments, and downstream projection targets are explicit.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---
ddx:
  id: pr-faq
---

# PR-FAQ: [PRODUCT NAME]

&lt;!--
This artifact has two halves: a launch-day press release (~350 words) and an
internal FAQ. Write it as if the product ships tomorrow. The press release is
customer-facing; the FAQ is internal and confronts the hard questions. If you
can&#x27;t write a credible PR-FAQ, the team doesn&#x27;t yet understand the problem.

The press release stays customer-facing and concise. The internal sections
capture the reusable product argument: thesis, mechanism, quality model,
decision or autonomy boundary, hard questions, and downstream projection.
Keep internal mechanics out of the customer narrative unless they directly
explain customer value.
--&gt;

## Press Release

**FOR IMMEDIATE RELEASE — [CITY, COUNTRY] — [LAUNCH DATE]**

### Headline

[ONE-LINE VALUE PROPOSITION IN PLAIN ENGLISH. NO JARGON, NO ADJECTIVES LIKE &quot;REVOLUTIONARY&quot; OR &quot;WORLD-CLASS&quot;. STATE WHAT THE PRODUCT DOES AND FOR WHOM.]

### Subhead

[ONE SENTENCE EXPANDING THE HEADLINE: WHO IT IS FOR, WHAT IT DOES, WHY IT MATTERS, WHEN IT IS AVAILABLE.]

### Summary

&lt;!-- The lede. What is being announced, the customer outcome, and why now. 2-4 sentences. --&gt;

[COMPANY NAME] today announced [PRODUCT NAME], [SHORT DESCRIPTION]. [PRODUCT NAME] helps [SPECIFIC CUSTOMER SEGMENT] [ACHIEVE SPECIFIC OUTCOME] by [HOW IT WORKS, ONE PHRASE]. It is available [WHERE/WHEN] starting [DATE].

### The Problem

&lt;!-- Name the customer pain in their words. Not &quot;users struggle&quot; — &quot;a 12-person bookkeeping firm spends 6 hours a week reconciling deposits by hand.&quot; --&gt;

[CONCRETE PROBLEM, IN THE CUSTOMER&#x27;S TERMS, WITH A NUMBER OR FAILURE MODE THAT MAKES IT REAL.]

### The Solution

&lt;!-- How the product solves the problem. Stay at the customer&#x27;s level — what they do, not how the system is implemented. --&gt;

[ONE PARAGRAPH DESCRIBING THE EXPERIENCE OF USING THE PRODUCT TO SOLVE THE PROBLEM ABOVE.]

### Quote from [LEADER NAME, TITLE]

&gt; &quot;[ONE PARAGRAPH IN THE COMPANY&#x27;S VOICE EXPLAINING WHY WE BUILT THIS. NAMES THE CUSTOMER, THE PROBLEM, AND THE COMMITMENT. NOT A SLOGAN.]&quot;

### How It Works

&lt;!-- 3-5 short steps from the customer&#x27;s perspective. --&gt;

1. [STEP ONE]
2. [STEP TWO]
3. [STEP THREE]

### Customer Quote

&gt; &quot;[ONE PARAGRAPH FROM THE IMAGINED CUSTOMER. IN THEIR VOICE. ABOUT THE OUTCOME THEY GOT, NOT THE FEATURES THEY USED. NAMES A SPECIFIC NUMBER, TIME SAVED, OR PROBLEM AVOIDED.]&quot;
&gt;
&gt; — [CUSTOMER NAME, ROLE, COMPANY OR CONTEXT]

### Availability

[WHERE TO GET IT, WHAT IT COSTS, WHAT PLATFORMS, WHAT REGIONS, WHEN, HOW TO SIGN UP.]

---

## Internal Product Argument

### Core Thesis

[ONE SENTENCE. A PLAIN, FALSIFIABLE CLAIM ABOUT WHY THIS PRODUCT SHOULD EXIST.]

### Mechanism

[ONE PARAGRAPH EXPLAINING WHAT MAKES THE THESIS TRUE. NAME THE SYSTEM BEHAVIOR, CONTEXT LAYER, WORKFLOW, DATA MODEL, OR CONTROL LOOP THAT PRODUCES THE OUTCOME.]

### Quality Model

&lt;!--
Name the attributes that must be true for the mechanism to work. These should
be specific enough to become PRD requirements or validation criteria.
--&gt;

| Attribute | Meaning | How We Know |
|---|---|---|
| [ATTRIBUTE] | [WHAT IT MEANS IN THIS PRODUCT] | [EVIDENCE OR CHECK] |
| [ATTRIBUTE] | [WHAT IT MEANS IN THIS PRODUCT] | [EVIDENCE OR CHECK] |
| [ATTRIBUTE] | [WHAT IT MEANS IN THIS PRODUCT] | [EVIDENCE OR CHECK] |

### Decision / Autonomy Boundary

&lt;!--
Use this for any product that automates, delegates, recommends, or changes who
decides what. Define the boundary without teaching the system to defer
everything.
--&gt;

[WHAT THE SYSTEM MAY DECIDE OR DO ON ITS OWN.]

[WHAT ASSUMPTIONS IT MAY RECORD AND CONTINUE WITH.]

[WHAT DECISIONS REQUIRE HUMAN JUDGMENT, APPROVAL, OR A SEPARATE DECISION ARTIFACT.]

## FAQ

&lt;!--
Two halves. External FAQs are what a customer, journalist, or analyst would
ask. Internal FAQs are what an exec, engineer, lawyer, or finance partner
would ask in a review meeting. The internal FAQs should be the hardest
questions you can think of — not soft-balls.
--&gt;

### External FAQs

#### How much does it cost?

[SPECIFIC PRICING. IF FREE, EXPLAIN HOW THE BUSINESS MODEL WORKS. IF NOT YET DECIDED, SAY SO AND NAME THE DECISION OWNER.]

#### How is this different from [EXISTING ALTERNATIVE]?

[NAME THE INCUMBENT OR ADJACENT PRODUCT. DESCRIBE THE SPECIFIC DIFFERENCE — WHO BENEFITS FROM THE DIFFERENCE AND WHEN.]

#### Who is this NOT for?

&lt;!-- Forces honest scoping. --&gt;

[SEGMENT OR USE CASE THAT IS BETTER SERVED BY AN ALTERNATIVE.]

#### What&#x27;s not in v1?

[EXPLICIT LIST OF FEATURES OR USE CASES DELIBERATELY DEFERRED. EACH WITH A REASON.]

#### What platforms / regions / integrations are supported at launch?

[SPECIFIC LIST.]

#### When can I get it?

[DATE OR PHASED ROLLOUT.]

### Internal FAQs

&lt;!--
Each question below should make at least one stakeholder uncomfortable to
answer. If they don&#x27;t, the FAQ is too soft.
--&gt;

#### What is the unit economics story? Is this profitable per customer?

[GROSS MARGIN ESTIMATE. ASSUMPTIONS. WHAT BREAKS THE MODEL.]

#### What is the riskiest technical assumption?

[NAME ONE SPECIFIC FEASIBILITY RISK. WHAT WOULD WE NEED TO BUILD OR PROVE TO DE-RISK IT.]

#### What experiments must run before we commit?

[LIST OF NAMED EXPERIMENTS WITH OWNERS AND DEADLINES. IF NONE — JUSTIFY WHY.]

#### What is the smallest viable launch?

[THE MINIMUM SHAPE OF V1 THAT VALIDATES THE THESIS.]

#### What must be true for the core thesis to hold?

[THE QUALITY MODEL IN OPERATIONAL TERMS. NAME WHAT WOULD MAKE THE PRODUCT&#x27;S CLAIM FALSE.]

#### Where can the system keep moving, and where must it stop?

[THE DECISION OR AUTONOMY BOUNDARY. DISTINGUISH SAFE FORWARD PROGRESS, REVERSIBLE ASSUMPTIONS, DECOMPOSITION, AND TRUE HUMAN DECISION POINTS.]

#### Who else has to ship something for this to work?

[EXTERNAL TEAMS, VENDORS, REGULATORY APPROVALS, OR CUSTOMERS. WHAT&#x27;S THE COMMITMENT STATUS.]

#### What regulatory or legal exposure does this create?

[LICENSING, DATA PROTECTION, FINANCIAL REGULATION, INDUSTRY-SPECIFIC RULES. NAME THE JURISDICTION.]

#### How does this scale? What breaks at 10x and 100x usage?

[SPECIFIC BOTTLENECKS. WHAT WE&#x27;D HAVE TO REBUILD.]

#### What are we choosing not to do, and why?

[EXPLICIT NON-GOALS WITH RATIONALE. PAIRS WITH THE PRD&#x27;S NON-GOALS SECTION.]

#### What would cause us to abandon this project?

&lt;!-- Kill criteria. Concrete, observable. --&gt;

[SPECIFIC SIGNAL — A METRIC TARGET MISSED, A COMPETITOR LAUNCH, A REGULATORY CHANGE — THAT WOULD MAKE US STOP.]

#### What does success look like 12 months after launch?

[QUANTITATIVE TARGETS THAT INFORM THE PRD&#x27;S SUCCESS METRICS.]

## Downstream Projection

&lt;!--
Name where this argument should appear next. For a public site, list the pages
that should derive from this PR-FAQ. For product development, list the PRD,
principles, feature specs, research plans, or decision artifacts that should
inherit the thesis.
--&gt;

| Target | What It Should Inherit | Owner / Status |
|---|---|---|
| [TARGET ARTIFACT OR PAGE] | [THESIS, MECHANISM, QUALITY MODEL, FAQ ANSWER] | [OWNER / STATUS] |
| [TARGET ARTIFACT OR PAGE] | [THESIS, MECHANISM, QUALITY MODEL, FAQ ANSWER] | [OWNER / STATUS] |

## Review Checklist

Use this checklist when reviewing a PR-FAQ artifact:

- [ ] Core thesis is a single plain-language claim, not a slogan
- [ ] Mechanism explains why the thesis should be true
- [ ] Quality model names attributes that can become requirements or checks
- [ ] Decision / autonomy boundary distinguishes progress, assumptions, decomposition, and human decision points
- [ ] Press release names a specific customer segment, not &quot;users&quot; or &quot;teams&quot;
- [ ] Press release reads as a real wire-service story — no marketing fluff
- [ ] Press release stays under ~350 words
- [ ] The Problem section uses the customer&#x27;s words and names a specific failure mode with a number
- [ ] The Solution section describes the customer experience, not the implementation
- [ ] Customer quote describes an outcome the customer got, not features they used
- [ ] Availability names specific dates, prices, platforms, and regions
- [ ] External FAQ explicitly compares to existing alternatives
- [ ] External FAQ names who this is NOT for
- [ ] A FAQ explicitly lists what is out of scope for v1
- [ ] Internal FAQ surfaces at least one credible feasibility or technical risk
- [ ] Internal FAQ confronts unit economics or pricing plausibility
- [ ] Internal FAQ states explicit kill criteria
- [ ] Internal FAQ names experiments or validation steps required before commit
- [ ] Downstream projection lists the artifacts or public pages that should inherit the argument
- [ ] No `[TBD]`, `[TODO]`, or `[NEEDS CLARIFICATION]` markers remain
- [ ] PR-FAQ is consistent with the governing Product Vision</code></pre></details></td></tr>
</tbody>
</table>
