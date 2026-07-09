---
title: "Market Analysis"
linkTitle: "Market Analysis"
slug: market-analysis
activity: "Discover"
artifactRole: "supporting"
weight: 90
generated: true
---

## Purpose

Answers: **Is this opportunity real, and how big?** Market Analysis is not
Competitive Analysis or Business Case. It owns market sizing, growth
trajectory, and the sub-approaches under consideration. Competitive Analysis
owns competitive pressure, alternatives, and defensible positioning once a
direction is chosen. Business Case owns investment logic (cost, ROI,
go/no-go).

## Authoring guidance

- **Name the sub-approaches** — if the opportunity spans distinct supply
  chains, cost structures, or buyer segments, size and discuss each rather
  than collapsing them into one pitch.
- **Cite every figure** — every market-size or growth-rate number traces to
  an entry in Sources; do not present modeled or recalled figures as
  sourced fact.
- **Separate facts from assumptions** — mark confidence explicitly when a
  claim is a stated market-report driver versus an inferred implication.
- **Defer decisions, don't make them** — sub-approach commitment, sourcing
  relationships, and positioning anchors belong in Frame; record them here
  as Open Questions, not as conclusions.
- **Stay evidence-first** — Strategic Implications should read as "what the
  sizing and competitive-density data imply," not as an independent pitch.

<details>
<summary>Quality checklist from the prompt</summary>

- [ ] Every sub-approach the opportunity could take is named, not collapsed
- [ ] Every market-sizing figure cites a source
- [ ] Key Drivers separate stated market-report findings from inferred trends
- [ ] Strategic Implications are grounded in the sizing/competitive-density
      data above them, not asserted independently
- [ ] At least one Open Question is explicitly deferred to Frame
- [ ] Sources section lists every citation used in the body

</details>

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: market-analysis
---

# Market Analysis: SMB Expense-Report Automation

**Activity:** Discover
**Status:** Draft
**Date:** 2026-03-01

## Concept

Automated expense-report capture and approval for small and mid-size
businesses (SMBs, 10-250 employees), evaluated across two distinct
sub-approaches since they imply different integration and pricing models:

1. **Standalone SaaS** (receipt capture, OCR, approval workflow, sold direct
   to finance teams)
2. **Embedded add-on** (same capability, sold as a module inside an existing
   SMB accounting platform's marketplace)

## Market Size & Growth

- Global expense management software market: **$5.5B (2026) → $9.8B
  (2032)**, ~10.2% CAGR.
- SMB-segment expense management specifically: **~$1.2B in 2026**.
- Embedded finance / accounting-platform add-ons (all categories): 24%
  CAGR 2025-2031 — the fastest-growing distribution channel in the broader
  market.

**Read:** the standalone-SaaS lane is larger today but growing in line with
the category average; the embedded-add-on lane is smaller but growing more
than twice as fast, suggesting distribution-channel choice matters more than
product-category choice for a new entrant.

## Competitive Landscape

### Standalone SaaS
- **Established direct competitors**: Expensify, Ramp, Brex — all target
  SMB-to-mid-market and bundle expense management with a corporate card
  product.
- **Incumbents moving in**: QuickBooks and Xero have each shipped native
  expense-capture features in the last two years, narrowing the gap a
  standalone tool needs to close.

### Embedded add-on
- **Marketplace competitors**: a small number of narrow OCR-only apps listed
  in the QuickBooks and Xero app marketplaces; none bundle approval workflow.
- Fewer than 10 marketplace listings combine capture and approval as of
  2026 — the add-on lane is less contested than standalone SaaS.

## Key Drivers

- SMB finance teams are a stated market-report driver toward "fewer
  point-tools, more embedded workflow" — not just a niche preference.
- Card-linked expense products (Ramp, Brex) are growing faster than
  capture-only tools, suggesting a card attachment may matter more than
  OCR accuracy as a differentiator.
- Accounting-platform marketplaces are actively promoting embedded
  add-ons as a growth lever for their own platforms, which lowers
  distribution cost for an add-on entrant.

## Strategic Implications

- **Standalone SaaS**: the lane is larger but already has three well-funded
  direct competitors plus two incumbents encroaching — a new entrant needs a
  differentiator sharper than "capture and approve expenses."
- **Embedded add-on**: less crowded and higher-growth, but ties the product's
  reach to a single accounting platform's marketplace and distribution
  decisions.
- **Pricing signal**: standalone competitors bundle a card product to
  capture interchange revenue; a pure software play without a card may not
  sustain comparable margins.

## Open Questions

**For Frame:**

- Does this venture commit to standalone SaaS, the embedded-add-on lane, or
  a phased path (embedded first, standalone later)?
- Is a card-issuing partnership available, or is this a pure software
  entrant competing against card-subsidized incumbents?
- What functional differentiator, beyond capture-and-approve, anchors the
  positioning once a lane is chosen?

## Sources

- [Global Expense Management Software Market Report (example)](https://example.com/expense-management-market)
- [Embedded Finance Distribution Trends (example)](https://example.com/embedded-finance-trends)
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Discover</strong></a> — Validate that an opportunity is worth pursuing before committing to a development cycle.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/00-discover/market-analysis.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="../../../artifact-types/discover/competitive-analysis/">Competitive Analysis</a><br><a href="../../../artifact-types/discover/business-case/">Business Case</a><br><a href="../../../artifact-types/discover/opportunity-canvas/">Opportunity Canvas</a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Market Analysis Prompt&#10;&#10;Create a market analysis that sizes the opportunity, surveys its growth&#10;drivers, and grounds later Discover/Frame work in market-report evidence —&#10;before any sub-approach, sourcing, or positioning decision has been made.&#10;&#10;## Reference Anchors&#10;&#10;Use this local resource summary as grounding:&#10;&#10;- `docs/resources/sba-market-research-competitive-analysis.md` grounds&#10;  market, competitor, pricing, and demand evidence expectations.&#10;&#10;## Storage Location&#10;&#10;Store at: `docs/helix/00-discover/market-analysis.md`&#10;&#10;## Purpose&#10;&#10;Answers: **Is this opportunity real, and how big?** Market Analysis is not&#10;Competitive Analysis or Business Case. It owns market sizing, growth&#10;trajectory, and the sub-approaches under consideration. Competitive Analysis&#10;owns competitive pressure, alternatives, and defensible positioning once a&#10;direction is chosen. Business Case owns investment logic (cost, ROI,&#10;go/no-go).&#10;&#10;## Key Principles&#10;&#10;- **Name the sub-approaches** — if the opportunity spans distinct supply&#10;  chains, cost structures, or buyer segments, size and discuss each rather&#10;  than collapsing them into one pitch.&#10;- **Cite every figure** — every market-size or growth-rate number traces to&#10;  an entry in Sources; do not present modeled or recalled figures as&#10;  sourced fact.&#10;- **Separate facts from assumptions** — mark confidence explicitly when a&#10;  claim is a stated market-report driver versus an inferred implication.&#10;- **Defer decisions, don&#x27;t make them** — sub-approach commitment, sourcing&#10;  relationships, and positioning anchors belong in Frame; record them here&#10;  as Open Questions, not as conclusions.&#10;- **Stay evidence-first** — Strategic Implications should read as &quot;what the&#10;  sizing and competitive-density data imply,&quot; not as an independent pitch.&#10;&#10;## Quality Checklist&#10;&#10;- [ ] Every sub-approach the opportunity could take is named, not collapsed&#10;- [ ] Every market-sizing figure cites a source&#10;- [ ] Key Drivers separate stated market-report findings from inferred trends&#10;- [ ] Strategic Implications are grounded in the sizing/competitive-density&#10;      data above them, not asserted independently&#10;- [ ] At least one Open Question is explicitly deferred to Frame&#10;- [ ] Sources section lists every citation used in the body</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: market-analysis&#10;---&#10;&#10;# Market Analysis: [Opportunity Name]&#10;&#10;**Activity:** Discover&#10;**Status:** Draft&#10;**Date:** [YYYY-MM-DD]&#10;&#10;## Concept&#10;&#10;[The candidate opportunity, evaluated across its distinct sub-approaches when&#10;the opportunity spans more than one viable shape — do not collapse them into&#10;one pitch if the supply chains, cost structures, or buyer segments differ.]&#10;&#10;1. **[Sub-approach 1]** ([short description])&#10;2. **[Sub-approach 2]** ([short description])&#10;3. **[Positioning or packaging layer]** (if applicable, layered on either&#10;   sub-approach above)&#10;&#10;## Market Size &amp; Growth&#10;&#10;- [Segment]: **$[X] ([year]) → $[Y] ([future year])**, ~[Z]% CAGR.&#10;- [Narrower/adjacent segment]: **~$[X] in [year]**.&#10;- [Most relevant slice]: [growth rate] CAGR [year range], reaching an&#10;  estimated **$[X] by [year]**.&#10;&#10;**Read:** [One or two sentences interpreting what the sizing data implies for&#10;this opportunity — which sub-approach is higher-growth vs. higher-volume,&#10;whether the category is funded/real vs. niche/speculative.]&#10;&#10;## Competitive Landscape&#10;&#10;### [Sub-approach 1 or segment]&#10;- **[Competitor archetype, e.g. vertically integrated brands]**: [names].&#10;- **[Other archetype, e.g. ingredient/platform suppliers]**: [names].&#10;- **Incumbents moving in**: [named incumbents and their observed activity, if any].&#10;- [Count or density signal, e.g. &quot;N distinct brands active as of [year]&quot;].&#10;- **Pricing observed**: [named price points with units, if available].&#10;&#10;### [Sub-approach 2 or segment]&#10;- [Named competitors with a one-line differentiator each].&#10;&#10;### [Positioning/packaging layer, if applicable]&#10;- [Buyer-behavior signal, e.g. &quot;% of buyers actively avoid X&quot;].&#10;&#10;## Key Drivers&#10;&#10;- [Named consumer/market driver, with confidence — market-report driver vs.&#10;  niche preference].&#10;- [Category-wide growth signal vs. the specific opportunity].&#10;- [Buyer-behavior driver relevant to entry strategy, e.g. trial behavior,&#10;  switching cost].&#10;&#10;## Strategic Implications&#10;&#10;- **[Sub-approach 1]**: [room to enter, level of crowding, what differentiation&#10;  needs to look like beyond the generic category claim].&#10;- **[Sub-approach 2]**: [structural advantage/disadvantage, e.g. easier to&#10;  differentiate regionally but harder to scale].&#10;- **[Positioning/packaging layer]**: [whether it is table-stakes or a real&#10;  differentiator].&#10;- **Pricing signal**: [what the observed price premium or lack of one implies&#10;  for go-to-market — premium/DTC vs. price-sensitive staple].&#10;&#10;## Open Questions&#10;&#10;**For Frame:**&#10;&#10;- [Sub-approach or segment commitment the venture still needs to decide, and why].&#10;- [Whether a defensible sourcing/supply relationship exists, or the entrant is&#10;  a pure brand-layer player].&#10;- [Positioning anchor beyond the baseline category claim].&#10;&#10;## Sources&#10;&#10;- [Source title](URL)&#10;- [Source title](URL)</code></pre></details></td></tr>
</tbody>
</table>
