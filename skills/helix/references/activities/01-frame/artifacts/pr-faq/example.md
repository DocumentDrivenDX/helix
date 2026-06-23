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
