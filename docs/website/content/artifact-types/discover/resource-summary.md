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
<tr><th>Activity</th><td><a href="/reference/glossary/activities/"><strong>Discover</strong></a> — Validate that an opportunity is worth pursuing before committing to a development cycle.</td></tr>
<tr><th>Default location</th><td><code>docs/resources/[resource-slug].md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="/artifact-types/discover/product-vision/">Product Vision</a><br><a href="/artifact-types/frame/pr-faq/">PR-FAQ</a><br><a href="/artifact-types/frame/principles/">Principles</a><br><a href="/artifact-types/frame/concerns/">Concerns</a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Resource Summary Generation Prompt

Create a concise summary of one external resource that HELIX uses to ground an
artifact, concern, decision, or public explanation.

## Storage Location

Store at: `docs/resources/[resource-slug].md`

## Purpose

A **resource summary** is a local, durable note for an external source. Its
unique job is to capture what we learned from the source and how HELIX uses it,
so artifact prompts can cite the local resource library instead of scattering
raw external links through the artifact catalog.

## Template Adherence

Use the sections in `template.md`. Do not add sections unless the source needs
a short note about access limitations.

## What To Capture

- The canonical URL and access date.
- A short neutral summary of the source.
- The specific findings HELIX will reuse.
- The artifact, concern, or decision the resource informs.
- The boundary: what this source does not decide.

## What To Avoid

- Do not copy long passages from the source.
- Do not summarize the whole source when HELIX only uses one idea.
- Do not turn the note into requirements, design, or implementation guidance.
- Do not cite the source as authority beyond the point HELIX actually uses.

## Quality Checklist

- [ ] Source URL is present
- [ ] Summary is accurate and concise
- [ ] Relevant findings are specific enough to reuse
- [ ] HELIX usage names the artifact, concern, or decision it supports
- [ ] Authority boundary is explicit
- [ ] External links live in the resource summary, not scattered through artifact prompts</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---
ddx:
  id: resource-summary
---

# [Resource Title]

## Source

- URL: [Canonical URL]
- Accessed: [YYYY-MM-DD]

## Summary

[Two to four sentences summarizing what the source contributes to HELIX.]

## Relevant Findings

- [Finding HELIX will reuse]
- [Finding HELIX will reuse]
- [Finding HELIX will reuse]

## HELIX Usage

[Name the artifact, concern, decision, or public page this resource informs and
explain how it should be used.]

## Authority Boundary

[Explain what this source does not govern. Name the HELIX artifact that owns the
next level of detail when relevant.]

## Review Checklist

- [ ] Source URL and access date are present
- [ ] Summary is concise and source-faithful
- [ ] Findings are relevant to HELIX
- [ ] HELIX usage is specific
- [ ] Boundary prevents over-applying the source</code></pre></details></td></tr>
</tbody>
</table>
