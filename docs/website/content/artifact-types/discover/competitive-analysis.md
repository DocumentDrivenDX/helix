---
title: "Competitive Analysis"
linkTitle: "Competitive Analysis"
slug: competitive-analysis
activity: "Discover"
artifactRole: "supporting"
weight: 12
generated: true
---

## Purpose

Answers: **How do we win in this market?** Keep the comparison factual, compact, and focused on positioning.

The Competitive Analysis is not the Business Case or PRD. It owns market
pressure, alternatives, competitor evidence, and the position the product can
defend. Business Case owns investment logic; PRD owns product requirements.

## Authoring guidance

- **Cover direct and indirect competitors** - compare strengths, weaknesses, and target customers.
- **Find the angle** - identify gaps and defensible differentiation.
- **Stay objective** - base claims on facts, not wishes.
- **Include substitutes** - manual workarounds and adjacent tools can be the real competition.
- **Separate facts from assumptions** - mark source and confidence for each claim.
- **Create follow-up research when evidence is thin** - do not hide gaps behind confident prose.

<details>
<summary>Quality checklist from the prompt</summary>

- [ ] At least 3 competitors analyzed
- [ ] Direct and indirect competitors included
- [ ] Feature matrix is factual
- [ ] Differentiation is specific and defensible
- [ ] Sources or explicit assumptions cited for competitor data
- [ ] Strategic implications name where to attack, defend, and avoid

</details>

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.competitive-analysis.depositmatch
  depends_on:
    - example.product-vision.depositmatch
  review:
    self_hash: 732b5273a4a651c0ac6e10f66ce97b29772b1b706582cf8bcc5b72f4767aa793
    deps:
      example.product-vision.depositmatch: 8abbb2fcb552b536f07829f57d91ef3ae8dbf52a6066955222e83d196b59b5ae
    reviewed_at: "2026-05-15T04:11:24Z"
---

# Competitive Analysis

## Market Landscape

| Attribute | Assessment |
|-----------|------------|
| Market Maturity | Mature workflows with emerging AI assistance |
| Growth Rate | Unknown; validate during research |
| Key Trends | Bookkeeping firms want reviewer capacity, auditability, and fewer spreadsheet handoffs |
| Entry Barriers | Medium: financial-data trust, accountant workflow fit, and integrations |
| Buyer Power | Medium: firms can stay with existing accounting tools and spreadsheets |

## Competitive Forces

| Force | Pressure | Evidence / Confidence | Implication |
|-------|----------|-----------------------|-------------|
| Direct Rivalry | Medium | Category assessment, low confidence | Avoid broad accounting-suite competition. |
| Substitutes | High | Product Vision assumption, medium confidence | Manual spreadsheet workflows are the default alternative. |
| New Entrants | Medium | Category assessment, low confidence | Defensibility must come from workflow trust, not matching alone. |
| Buyer Power | Medium | Target customer assumption, medium confidence | Pricing must map to saved reviewer time and client capacity. |

## Competitor Profiles

| Competitor | Type | Positioning | Target Segment | Strengths | Weaknesses | Source / Confidence |
|------------|------|-------------|----------------|-----------|------------|---------------------|
| Spreadsheet reconciliation | Substitute | Flexible manual workspace | Small bookkeeping teams | Ubiquitous, cheap, easy to customize | Weak audit trail, slow review, hard exception ownership | Product Vision, medium confidence |
| Accounting-platform bank feeds | Indirect | Reconciliation inside the accounting ledger | Firms already standardized on one ledger | Native transaction context and bank connectivity | Less focused on cross-client review queues and evidence-backed exception handling | Category assessment, low confidence |
| Generic AI matching tools | Direct / emerging | Automated matching suggestions | Finance operations teams | Fast matching and automation narrative | Trust gap when reviewers cannot inspect evidence before approval | Category assessment, low confidence |

**Indirect Competitors**: Accounting suites, spreadsheet templates, outsourced
bookkeeping labor, and custom scripts. The highest threat is the existing
spreadsheet workflow because it is familiar and has no procurement barrier.

## Feature Comparison

| Feature | DepositMatch | Spreadsheet Workflow | Accounting-Platform Bank Feeds | Generic AI Matching |
|---------|--------------|----------------------|-------------------------------|--------------------|
| CSV import | Full | Full | Partial | Full |
| Suggested matches | Full | None | Partial | Full |
| Evidence before approval | Full | Partial | Partial | Partial |
| Exception ownership | Full | Partial | Partial | None |
| Cross-client review queue | Full | None | Partial | Partial |
| Audit-ready reviewer history | Full | Partial | Partial | Partial |

**Legend**: Full | Partial | Planned | None

## Differentiation Strategy

| Differentiator | Why It Matters | Defensibility |
|----------------|----------------|---------------|
| Evidence-backed suggestions | Reviewers can trust and challenge matches before approval. | Medium |
| Exception ownership | Firms can keep unresolved work from disappearing across clients. | Medium |
| CSV-first onboarding | Pilot firms can start without bank-feed or ledger integrations. | Low |

**Positioning**: For small bookkeeping firms that lose reviewer capacity to
manual deposit reconciliation, DepositMatch is a reconciliation workspace that
makes suggested matches reviewable and exceptions owned. Unlike spreadsheets or
ledger-native feeds, DepositMatch focuses on trust-first review across clients.

## Strategic Implications

- **Attack**: CSV-heavy firms with weekly reconciliation bottlenecks and no
  reliable exception queue.
- **Defend**: Reviewer trust, evidence visibility, and client-level work
  ownership.
- **Avoid**: Broad accounting-suite replacement, fully automated approval, and
  bank-feed integrations before pilot evidence proves demand.
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Discover</strong></a> — Validate that an opportunity is worth pursuing before committing to a development cycle.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/00-discover/competitive-analysis.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="../../../artifact-types/discover/business-case/">Business Case</a><br><a href="../../../artifact-types/discover/opportunity-canvas/">Opportunity Canvas</a><br><a href="../../../artifact-types/frame/prd/">PRD</a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Competitive Analysis Prompt&#10;&#10;Create a competitive analysis that maps the market landscape and establishes differentiation strategy.&#10;&#10;## Reference Anchors&#10;&#10;Use these local resource summaries as grounding:&#10;&#10;- `docs/resources/sba-market-research-competitive-analysis.md` grounds&#10;  market, competitor, pricing, and demand evidence expectations.&#10;- `docs/resources/hbs-five-forces.md` grounds competitive pressure,&#10;  substitutes, entrants, buyers, and positioning.&#10;&#10;## Storage Location&#10;&#10;Store at: `docs/helix/00-discover/competitive-analysis.md`&#10;&#10;## Purpose&#10;&#10;Answers: **How do we win in this market?** Keep the comparison factual, compact, and focused on positioning.&#10;&#10;The Competitive Analysis is not the Business Case or PRD. It owns market&#10;pressure, alternatives, competitor evidence, and the position the product can&#10;defend. Business Case owns investment logic; PRD owns product requirements.&#10;&#10;## Key Principles&#10;&#10;- **Cover direct and indirect competitors** - compare strengths, weaknesses, and target customers.&#10;- **Find the angle** - identify gaps and defensible differentiation.&#10;- **Stay objective** - base claims on facts, not wishes.&#10;- **Include substitutes** - manual workarounds and adjacent tools can be the real competition.&#10;- **Separate facts from assumptions** - mark source and confidence for each claim.&#10;- **Create follow-up research when evidence is thin** - do not hide gaps behind confident prose.&#10;&#10;## Quality Checklist&#10;&#10;- [ ] At least 3 competitors analyzed&#10;- [ ] Direct and indirect competitors included&#10;- [ ] Feature matrix is factual&#10;- [ ] Differentiation is specific and defensible&#10;- [ ] Sources or explicit assumptions cited for competitor data&#10;- [ ] Strategic implications name where to attack, defend, and avoid</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: competitive-analysis&#10;---&#10;&#10;# Competitive Analysis&#10;&#10;## Market Landscape&#10;&#10;| Attribute | Assessment |&#10;|-----------|------------|&#10;| Market Maturity | Emerging / Growing / Mature / Declining |&#10;| Growth Rate | [X]% annually |&#10;| Key Trends | [Trend 1], [Trend 2] |&#10;| Entry Barriers | Low / Medium / High |&#10;| Buyer Power | Low / Medium / High |&#10;&#10;## Competitive Forces&#10;&#10;| Force | Pressure | Evidence / Confidence | Implication |&#10;|-------|----------|-----------------------|-------------|&#10;| Direct Rivalry | Low / Medium / High | [Source or assumption] | [So what] |&#10;| Substitutes | Low / Medium / High | [Source or assumption] | [So what] |&#10;| New Entrants | Low / Medium / High | [Source or assumption] | [So what] |&#10;| Buyer Power | Low / Medium / High | [Source or assumption] | [So what] |&#10;&#10;## Competitor Profiles&#10;&#10;| Competitor | Type | Positioning | Target Segment | Strengths | Weaknesses | Source / Confidence |&#10;|------------|------|-------------|----------------|-----------|------------|---------------------|&#10;| [Competitor 1] | Direct / Indirect / Substitute | [Position] | [Segment] | [Strengths] | [Weaknesses] | [Source, confidence] |&#10;| [Competitor 2] | Direct / Indirect / Substitute | [Position] | [Segment] | [Strengths] | [Weaknesses] | [Source, confidence] |&#10;| [Competitor 3] | Direct / Indirect / Substitute | [Position] | [Segment] | [Strengths] | [Weaknesses] | [Source, confidence] |&#10;&#10;**Indirect Competitors**: [List alternative solutions and threat level]&#10;&#10;## Feature Comparison&#10;&#10;| Feature | Us | Comp 1 | Comp 2 |&#10;|---------|----|--------|--------|&#10;| [Feature 1] | [Status] | [Status] | [Status] |&#10;| [Feature 2] | [Status] | [Status] | [Status] |&#10;&#10;**Legend**: Full | Partial | Planned | None&#10;&#10;## Differentiation Strategy&#10;&#10;| Differentiator | Why It Matters | Defensibility |&#10;|----------------|----------------|---------------|&#10;| [Differentiator 1] | [Customer value] | H/M/L |&#10;| [Differentiator 2] | [Customer value] | H/M/L |&#10;&#10;**Positioning**: For [target customer] who [need], our [product] is a [category] that [key benefit]. Unlike [competitors], we [primary differentiator].&#10;&#10;## Strategic Implications&#10;&#10;- **Attack**: [Where to compete aggressively]&#10;- **Defend**: [Where to protect position]&#10;- **Avoid**: [Where not to compete]</code></pre></details></td></tr>
</tbody>
</table>
