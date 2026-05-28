---
title: "Product Vision"
linkTitle: "Product Vision"
slug: product-vision
activity: "Discover"
artifactRole: "core"
weight: 10
generated: true
---

## Purpose

A **north star document** that makes the product's direction transferable. Its
unique job is to answer four questions before any PRD exists: who is this for,
what alternative do they use today, what future state are we trying to create,
and how will we know the direction is working?

Every downstream artifact — PRD, specs, designs, tests — traces back to this
document. If the vision is vague, everything built on it drifts.

## Authoring guidance

- **Be concise** — keep the mission to 1-2 sentences.
- **Be specific** — name target customers, name competitors, state measurable
  outcomes. Placeholders and hedging ("various users", "significant impact")
  are not acceptable.
- **Be compelling** — connect the vision to real customer pain and a concrete
  end state.
- **Be honest** — if you can't fill a section with substance, that's a signal
  the thinking isn't done yet. Flag it rather than filling with platitudes.

<details>
<summary>Boundaries: what belongs elsewhere</summary>

Product vision is for *direction*. If you find yourself writing about:

| This content | Belongs in |
|---|---|
| Methodology, activities, authority order | `workflows/README.md`, activities glossary |
| Market sizing, revenue model, investment rationale | `00-discover/business-case.md` |
| Competitor analysis or feature-by-feature comparison | `00-discover/competitive-analysis.md` |
| Principles or judgment lenses | `01-frame/principles.md` |
| Risks (likelihood × impact) | `01-frame/risk-register.md` (master), PRD risks (PRD-scoped) |
| Non-goals, "what we won't build" | `01-frame/prd.md` |
| Per-feature requirements | `01-frame/features/FEAT-*.md` |
| UI interaction details (clicks, screens) | feature spec or user story |
| Architecture or technology choices | `02-design/` |
| Release-scoped success metrics | `01-frame/prd.md` (vision keeps strategic, long-horizon outcomes only) |
| Definitional schemas for metrics | `06-iterate/metric-definition.md` |

</details>

<details>
<summary>Quality checklist from the prompt</summary>

After drafting, verify every item. If any blocking check fails, revise before
committing.

### Blocking

- [ ] H2 section list exactly matches the template (no added, removed, or renamed sections)
- [ ] Body is ≤ 1.5× the template's line count (currently ≤ 105 lines)
- [ ] Positioning names a specific customer segment (not a category)
- [ ] Positioning names a specific competitor or alternative (not "existing solutions")
- [ ] Target market is specific enough to identify real people
- [ ] Every success metric has a numeric target or measurable outcome
- [ ] User experience section describes a concrete scenario (not abstract benefits)

### Warning

- [ ] Mission fits in a tweet (under 280 characters)
- [ ] Vision describes an end state, not a timeline or market position
- [ ] Why Now cites an observable change, not a general trend
- [ ] Value propositions pass the "so what?" test
- [ ] No section contains only placeholder text
- [ ] No sentence's main predicate is `not <noun>` without a positive predicate in the same sentence

</details>

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.product-vision.depositmatch
---
# Product Vision

## Mission Statement

DepositMatch helps small bookkeeping firms reconcile client invoices to bank
deposits in minutes instead of hours.

## Positioning

For bookkeeping firms with 5-25 recurring clients who spend hours matching
incoming deposits to invoices, DepositMatch is a reconciliation workspace that
groups bank deposits, suggests invoice matches, and records reviewer decisions.
Unlike spreadsheet checklists and generic accounting exports, DepositMatch
keeps the matching evidence, exceptions, and client follow-up in one place.

## Vision

Bookkeepers start each morning with a short review queue instead of a bank
statement and a spreadsheet. Most deposits are already matched with evidence.
Unclear deposits are grouped by client, amount, and date so the reviewer can
accept, split, or flag them without rebuilding the trail.

**North Star**: A bookkeeping firm can close weekly deposit reconciliation for
20 clients in under one hour with fewer than 2% unresolved deposits.

## User Experience

Maya manages reconciliation for twelve dental practices. On Monday morning she
opens DepositMatch and sees 184 deposits imported from bank feeds. The product
has already matched 161 deposits to invoices with high confidence. Maya reviews
the suggested matches, accepts the obvious ones in batches, and spends the rest
of the session on exceptions: two split payments, one duplicate invoice number,
and three deposits that need client clarification. At the end, she exports a
review log for each client and sends three follow-up questions without leaving
the workspace.

## Target Market

| Attribute | Description |
|-----------|-------------|
| Who | Bookkeeping firms with 5-25 employees serving recurring small-business clients |
| Pain | Reconciliation is manual, repetitive, and hard to audit across clients |
| Current Solution | QuickBooks or Xero exports, bank reports, spreadsheets, and email follow-up |
| Why They Switch | Client volume has grown faster than reviewer capacity, and spreadsheet trails are too fragile for monthly close |

## Key Value Propositions

| Value Proposition | Customer Benefit |
|-------------------|------------------|
| Deposit-to-invoice match suggestions | Reviewers spend time confirming exceptions instead of searching every line item |
| Evidence-backed review log | Firms can explain every accepted match during client questions or month-end review |
| Exception queue by client | Unclear deposits are routed to follow-up without losing the surrounding context |

## Success Definition

| Metric | Target |
|--------|--------|
| Primary KPI | Median weekly reconciliation time below 3 minutes per client by the second month of use |
| Match accuracy | Accepted suggestions remain above 95% in reviewer audit samples |
| Exception handling | 90% of unresolved deposits have an owner and next action within one business day |

## Why Now

Small bookkeeping firms are taking on more recurring clients while bank feeds,
invoice exports, and payment processor reports have become easier to access.
The missing layer is not another accounting system. It is a focused review
workspace that turns those feeds into a trustworthy reconciliation queue before
month-end pressure accumulates.
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="/reference/glossary/activities/"><strong>Discover</strong></a> — Validate that an opportunity is worth pursuing before committing to a development cycle.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/00-discover/product-vision.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="/artifact-types/discover/business-case/">Business Case</a><br><a href="/artifact-types/discover/competitive-analysis/">Competitive Analysis</a><br><a href="/artifact-types/discover/opportunity-canvas/">Opportunity Canvas</a><br><a href="/artifact-types/frame/prd/">PRD</a></td></tr>
<tr><th>HELIX documents</th><td><a href="https://github.com/DocumentDrivenDX/helix/blob/main/docs/helix/00-discover/product-vision.md"><code>docs/helix/00-discover/product-vision.md</code></a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Product Vision Prompt

Create a concise product vision that aligns stakeholders on direction before
requirements, design, and delivery work begin.

## Storage Location

Store at: `docs/helix/00-discover/product-vision.md`

## Purpose

A **north star document** that makes the product&#x27;s direction transferable. Its
unique job is to answer four questions before any PRD exists: who is this for,
what alternative do they use today, what future state are we trying to create,
and how will we know the direction is working?

Every downstream artifact — PRD, specs, designs, tests — traces back to this
document. If the vision is vague, everything built on it drifts.

## Reference Anchors

Use these references as grounding, not as extra sections to copy:

- `docs/resources/product-vision-board.md` captures target group, needs, product direction, and business goals. HELIX uses the same strategic ingredients but keeps detailed business justification in the Business Case.
- `docs/resources/geoffrey-moore-positioning.md` forces the vision to name the target customer, need, category, benefit, and primary alternative.
- `docs/resources/atlassian-vision-creation.md` frames vision as the shared picture of the future that aligns stakeholders before strategy and execution.

## Template Adherence

**The template is the contract.** The 8 sections in `template.md` cover what a
vision should say. Do not add new H2 sections. Do not rename or reorder
existing ones. The body should land within ~1.5× the template&#x27;s line count
(template is ~70 lines, so target ≤ 105).

If you have content that doesn&#x27;t fit one of the 8 sections, see &quot;Stay in your
lane&quot; below — it almost certainly belongs in a different artifact type.

## Stay in Your Lane

Product vision is for *direction*. If you find yourself writing about:

| This content | Belongs in |
|---|---|
| Methodology, activities, authority order | `workflows/README.md`, activities glossary |
| Market sizing, revenue model, investment rationale | `00-discover/business-case.md` |
| Competitor analysis or feature-by-feature comparison | `00-discover/competitive-analysis.md` |
| Principles or judgment lenses | `01-frame/principles.md` |
| Risks (likelihood × impact) | `01-frame/risk-register.md` (master), PRD risks (PRD-scoped) |
| Non-goals, &quot;what we won&#x27;t build&quot; | `01-frame/prd.md` |
| Per-feature requirements | `01-frame/features/FEAT-*.md` |
| UI interaction details (clicks, screens) | feature spec or user story |
| Architecture or technology choices | `02-design/` |
| Release-scoped success metrics | `01-frame/prd.md` (vision keeps strategic, long-horizon outcomes only) |
| Definitional schemas for metrics | `06-iterate/metric-definition.md` |

## Key Principles

- **Be concise** — keep the mission to 1-2 sentences.
- **Be specific** — name target customers, name competitors, state measurable
  outcomes. Placeholders and hedging (&quot;various users&quot;, &quot;significant impact&quot;)
  are not acceptable.
- **Be compelling** — connect the vision to real customer pain and a concrete
  end state.
- **Be honest** — if you can&#x27;t fill a section with substance, that&#x27;s a signal
  the thinking isn&#x27;t done yet. Flag it rather than filling with platitudes.

## Section-by-Section Guidance

### Mission Statement
Write it so someone outside the team understands what you do in one breath.
Test: could you say this in a single tweet?

### Positioning (Moore&#x27;s Template)
Fill in every blank with a real noun. &quot;For [target] who [need]&quot; must name a
specific customer segment and a specific pain — not a category. &quot;Unlike
[alternative]&quot; must name an actual product or approach the customer uses today.
If you can&#x27;t name the alternative, you don&#x27;t understand the market yet.

### Vision
Describe the desired end state, not a timeline. What changes for users? What
changes in the market? Avoid &quot;we will be the leading...&quot; — describe what the
world looks like, not your position in it.

### User Experience
Walk through a concrete session. Use present tense. Name the actions the user
takes and what the system does in response. This should read like a usage
scenario, not marketing copy.

### Target Market
&quot;Who&quot; must be specific enough to find these people. &quot;Software teams&quot; is too
broad. &quot;Teams of 3-15 engineers using AI coding agents daily who ship
weekly&quot; is specific enough.

### Key Value Propositions
Each row must pass the &quot;so what?&quot; test. The customer benefit column should
describe what changes for the customer, not restate the capability.

### Success Definition
Every metric must be measurable with a tool or process you can name. &quot;User
satisfaction&quot; is not measurable. &quot;NPS &gt; 40 from monthly survey&quot; is.

These are *strategic, long-horizon* outcomes — what success looks like over
12–24 months. Release-scoped metrics belong in the PRD; feature-scoped metrics
in feature specs; metric schemas in `metric-definition`. Aim for 3–5 strategic
indicators, not a comprehensive metric catalog.

### Why Now
Ground this in an observable change — a technology shift, a market event, a
regulatory change, a behavioral trend. &quot;AI is getting better&quot; is too vague.
&quot;Coding agents can now implement bounded tasks reliably but teams lack a
supervisory layer&quot; is grounded.

## Quality Checklist

After drafting, verify every item. If any blocking check fails, revise before
committing.

### Blocking

- [ ] H2 section list exactly matches the template (no added, removed, or renamed sections)
- [ ] Body is ≤ 1.5× the template&#x27;s line count (currently ≤ 105 lines)
- [ ] Positioning names a specific customer segment (not a category)
- [ ] Positioning names a specific competitor or alternative (not &quot;existing solutions&quot;)
- [ ] Target market is specific enough to identify real people
- [ ] Every success metric has a numeric target or measurable outcome
- [ ] User experience section describes a concrete scenario (not abstract benefits)

### Warning

- [ ] Mission fits in a tweet (under 280 characters)
- [ ] Vision describes an end state, not a timeline or market position
- [ ] Why Now cites an observable change, not a general trend
- [ ] Value propositions pass the &quot;so what?&quot; test
- [ ] No section contains only placeholder text
- [ ] No sentence&#x27;s main predicate is `not &lt;noun&gt;` without a positive predicate in the same sentence</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---
ddx:
  id: product-vision
---

# Product Vision

## Mission Statement

[One to two sentences: What we do + for whom + why it matters]

## Positioning

For [target customer] who [need or problem],
[product name] is a [category] that [key benefit].
Unlike [current alternative], [product name] [primary differentiator].

## Vision

[What does the world look like when this product succeeds? Describe the desired end state — not when it happens, but what changes for users and the market.]

**North Star**: [Single sentence describing ultimate success state]

## User Experience

[Describe what a typical session looks like when this product works as intended. Walk through a concrete scenario from the user&#x27;s perspective — what do they do, what happens, how does it feel?]

## Target Market

| Attribute | Description |
|-----------|-------------|
| Who | [Specific customer type] |
| Pain | [Primary pain point] |
| Current Solution | [What they use today] |
| Why They Switch | [What makes the status quo untenable] |

## Key Value Propositions

| Value Proposition | Customer Benefit |
|-------------------|------------------|
| [Core capability] | [Why it matters to customer] |
| [Core capability] | [Why it matters to customer] |

## Success Definition

| Metric | Target |
|--------|--------|
| Primary KPI | [Specific measurable outcome] |
| [Supporting metric] | [Specific measurable outcome] |

## Why Now

[One paragraph: What has changed — in the market, technology, or user behavior — that makes this the right time to build this? Why would waiting be costly?]

## Review Checklist

Use this checklist when reviewing a product vision artifact:

- [ ] Mission statement is specific — names the user, the problem, and the approach
- [ ] Positioning statement differentiates from the current alternative
- [ ] Vision describes a desired end state, not a feature list
- [ ] North star is a single measurable sentence
- [ ] User experience section describes a concrete scenario, not abstract benefits
- [ ] Target market identifies specific pain points and switching triggers
- [ ] Value propositions map to customer benefits, not internal capabilities
- [ ] Success metrics are measurable and time-bound
- [ ] Why Now section names a specific change, not a vague opportunity
- [ ] Business case details, competitor matrices, requirements, and technical choices are left to their own artifacts
- [ ] No implementation details (technology choices, architecture) — those belong in design</code></pre></details></td></tr>
</tbody>
</table>
