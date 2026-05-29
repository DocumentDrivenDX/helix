---
title: "Resource Summary"
linkTitle: "Resource Summary"
slug: resource-summary
activity: "Discover"
artifactRole: "supporting"
weight: 14
generated: true
---

## Purpose

A **resource summary** is a local, durable note for an external source. Its
unique job is to capture what we learned from the source and how HELIX uses it,
so artifact prompts can cite the local resource library instead of scattering
raw external links through the artifact catalog.

<details>
<summary>Quality checklist from the prompt</summary>

- [ ] Source URL is present
- [ ] Summary is accurate and concise
- [ ] Relevant findings are specific enough to reuse
- [ ] HELIX usage names the artifact, concern, or decision it supports
- [ ] Authority boundary is explicit
- [ ] External links live in the resource summary, not scattered through artifact prompts

</details>

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.resource-summary.product-vision-board
---

# Product Vision Board

## Source

- URL: https://www.romanpichler.com/tools/product-vision-board/
- Accessed: 2026-05-12

## Summary

Roman Pichler's Product Vision Board is a product strategy tool for describing,
visualizing, and validating product vision and strategy. It captures target
group, needs, product direction, and business goals; the extended version adds
business model elements such as competitors, revenue sources, costs, and
channels.

## Relevant Findings

- A vision artifact should name the target group and needs, not only the
  product idea.
- Product direction and business goals belong together at the strategy level.
- Business model detail can be useful, but it should not crowd out the core
  vision.

## HELIX Usage

This resource informs the Product Vision artifact. HELIX uses the same
strategic ingredients while keeping market sizing and investment rationale in
the Business Case.

## Authority Boundary

This resource does not define requirements, competitive analysis, or
implementation plans. Those belong in the PRD, Competitive Analysis, and Design
artifacts.
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Discover</strong></a> — Validate that an opportunity is worth pursuing before committing to a development cycle.</td></tr>
<tr><th>Default location</th><td><code>docs/resources/[resource-slug].md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="../../../artifact-types/discover/product-vision/">Product Vision</a><br><a href="../../../artifact-types/frame/pr-faq/">PR-FAQ</a><br><a href="../../../artifact-types/frame/principles/">Principles</a><br><a href="../../../artifact-types/frame/concerns/">Concerns</a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Resource Summary Generation Prompt&#10;&#10;Create a concise summary of one external resource that HELIX uses to ground an&#10;artifact, concern, decision, or public explanation.&#10;&#10;## Storage Location&#10;&#10;Store at: `docs/resources/[resource-slug].md`&#10;&#10;## Purpose&#10;&#10;A **resource summary** is a local, durable note for an external source. Its&#10;unique job is to capture what we learned from the source and how HELIX uses it,&#10;so artifact prompts can cite the local resource library instead of scattering&#10;raw external links through the artifact catalog.&#10;&#10;## Template Adherence&#10;&#10;Use the sections in `template.md`. Do not add sections unless the source needs&#10;a short note about access limitations.&#10;&#10;## What To Capture&#10;&#10;- The canonical URL and access date.&#10;- A short neutral summary of the source.&#10;- The specific findings HELIX will reuse.&#10;- The artifact, concern, or decision the resource informs.&#10;- The boundary: what this source does not decide.&#10;&#10;## What To Avoid&#10;&#10;- Do not copy long passages from the source.&#10;- Do not summarize the whole source when HELIX only uses one idea.&#10;- Do not turn the note into requirements, design, or implementation guidance.&#10;- Do not cite the source as authority beyond the point HELIX actually uses.&#10;&#10;## Quality Checklist&#10;&#10;- [ ] Source URL is present&#10;- [ ] Summary is accurate and concise&#10;- [ ] Relevant findings are specific enough to reuse&#10;- [ ] HELIX usage names the artifact, concern, or decision it supports&#10;- [ ] Authority boundary is explicit&#10;- [ ] External links live in the resource summary, not scattered through artifact prompts</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: resource-summary&#10;---&#10;&#10;# [Resource Title]&#10;&#10;## Source&#10;&#10;- URL: [Canonical URL]&#10;- Accessed: [YYYY-MM-DD]&#10;&#10;## Summary&#10;&#10;[Two to four sentences summarizing what the source contributes to HELIX.]&#10;&#10;## Relevant Findings&#10;&#10;- [Finding HELIX will reuse]&#10;- [Finding HELIX will reuse]&#10;- [Finding HELIX will reuse]&#10;&#10;## HELIX Usage&#10;&#10;[Name the artifact, concern, decision, or public page this resource informs and&#10;explain how it should be used.]&#10;&#10;## Authority Boundary&#10;&#10;[Explain what this source does not govern. Name the HELIX artifact that owns the&#10;next level of detail when relevant.]&#10;&#10;## Review Checklist&#10;&#10;- [ ] Source URL and access date are present&#10;- [ ] Summary is concise and source-faithful&#10;- [ ] Findings are relevant to HELIX&#10;- [ ] HELIX usage is specific&#10;- [ ] Boundary prevents over-applying the source</code></pre></details></td></tr>
</tbody>
</table>
