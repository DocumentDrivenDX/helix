---
title: "Developer orientation pilot"
slug: developer-orientation-pilot
weight: 660
activity: "Iterate"
source: "06-iterate/developer-orientation-pilot.md"
generated: true
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

> **Source identity** (from `06-iterate/developer-orientation-pilot.md`):

```yaml
ddx:
  id: helix.developer-orientation-pilot
  status: draft
  authoring:
    home: repo
```

# Developer orientation pilot

## Scope and completion conditions

Create HELIX's solution overview, developer guide, and one end-to-end
architecture walkthrough. Use repository evidence to improve reusable catalog
types without introducing duplicate structural authority. Complete when the
instances and examples exist, entrypoints link them, graph/reference publication
is regenerated, and repository gates have recorded outcomes.

## Plan

1. Trace current routing, catalog, packaging, and validation sources.
2. Write the overview and guide; attach the authoring walkthrough to Architecture.
3. Extract two artifact types and optional walkthrough guidance from the pilot.
4. Regenerate derived content; validate type shape, instances, and full suite.

## Findings and template changes

| Pilot finding | Reusable change |
|---|---|
| Architecture is long and mixes introductory and detailed reference material | Solution Overview supplies a concise system map and reading path with explicit authority links |
| Existing contributor instructions referred to obsolete skill/release surfaces | Developer Guide requires source-backed commands, generated-output recipes, expected results, and a maintained contributor entrypoint |
| HELIX is content plus a skill; a service-centric diagram would misrepresent it | Diagram prompts require actual actors/content, labeled interactions, and a legend |
| Static validators do not establish live model behavior | Walkthrough steps name evidence and verification limits |
| A repository-reading author cannot establish newcomer success | Guide requires an observed trial or explicit pending status |

## Boundaries and follow-up

The walkthrough is an adjacent architecture explanation, not a third new type.
Overview and guide remain drafts until human review. No unfamiliar-developer
trial has occurred; a future trial should record environment, first task, help
needed, observed result, and blockers. No live model, deployment, or release is
part of this pilot.

## Verification and continuation

Completed: three pilot documents, two four-file catalog types, optional
walkthrough guidance, contributor links, generated graph, reference pages, and
published project artifacts.

- `python3 scripts/helix_validate_artifact_meta.py`: 57 types pass.
- Instance validator: Solution Overview and Developer Guide pass with zero findings.
- New instance Markdown links: all relative targets exist.
- `just test`: passes. The deck lane initially skipped missing `pptxgenjs`;
  rerunning `just test-deck-render` with the bundled Node dependency succeeds,
  including geometry checks and rasterizing 12 slides. The optional PowerPoint
  validator skips because the chosen Python lacks `lxml`/`defusedxml`.
- Innsigle lane skips because its CLI is unavailable and package access is
  restricted. Headline source byte comparison skips an absent external checkout.
- Hugo production-base-path build: passes.
- `python3 scripts/check-website-links.py`: 65,576 links/images resolve across
  391 pages.
- `lefthook run pre-commit`: passes; its advisory revalidation script reports
  a missing historical path and is configured nonblocking.
- `git diff --check`: passes.

The default Python lacks PyYAML. Validation used an existing cached PyYAML
installation via `PYTHONPATH`; the guide now includes dependency recovery.
No unfamiliar-developer trial has occurred. Remaining evaluation is human review
of the drafts and a real newcomer first-contribution session. No release or
remote publication was performed.
