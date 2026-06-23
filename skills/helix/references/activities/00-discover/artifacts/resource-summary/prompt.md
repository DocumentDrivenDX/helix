# Resource Summary Generation Prompt

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
- [ ] External links live in the resource summary, not scattered through artifact prompts
