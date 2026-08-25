---
title: "Validate"
slug: validate
weight: 50
generated: true
---

Generated from [`skills/helix/SKILL.md`](https://github.com/DocumentDrivenDX/helix/blob/main/skills/helix/SKILL.md), the HELIX skill. Edit the skill, not this page.

Use to check a single artifact instance against its governing template and
prompt, then edit resolvable findings in place.

1. Load the artifact instance and resolve its artifact type: read `ddx:`
   frontmatter when present (`ddx.type`, else inferred from `ddx.id`
   prefix); otherwise resolve by path or filename pattern against the
   artifact-type catalog the runtime exposes.
2. Load the artifact-type's `template.md`, `prompt.md`, `meta.yml`, and active
   voice profile from the resolved catalog path (see §Catalog Resolution and
   §Voice Resolution).
3. Run structural conformance: required section headings from `template.md`
   are present, and required frontmatter fields from `meta.yml` are
   populated.
4. Run prompt-section conformance: every section the `prompt.md` asks for is
   answered in the instance or explicitly marked N/A with a reason.
5. Run voice conformance against the active profile, then classify each finding
   keyed to the relevant template, prompt, meta.yml, or voice-profile section
   using the Align taxonomy: `ALIGNED`, `INCOMPLETE`, `DIVERGENT`,
   `UNDERSPECIFIED`, `STALE_PLAN`, or `BLOCKED`. For `artifact-signal`, flag
   filler, unscoped claims, unsupported implementation-status language in
   specifications, missing actors, hidden assumptions, and prose that smooths
   away artifact IDs, paths, commands, metrics, statuses, acceptance criteria,
   or trace links. If Sloptimizer is available, it may perform this pass using
   the active HELIX profile as constraints; otherwise apply the profile
   directly.
6. Produce updates: when the user invoked validate to fix, apply edits
   in place for every finding the template, prompt, metadata, or voice-profile
   comparison can resolve mechanically — typically `INCOMPLETE` findings
   (missing required sections, stale frontmatter shape, renamed headings,
   unsupported filler, or unscoped claims). For
   findings classified as `DIVERGENT`, `UNDERSPECIFIED`, `STALE_PLAN`,
   or `BLOCKED` — which need human judgement — surface a §Align gap-to-
   implementation handoff for that specific finding instead of editing.
   When the user invoked validate to audit, surface a §Align handoff
   for every non-`ALIGNED` finding regardless of mechanical
   resolvability.
