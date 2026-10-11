---
title: "UX behavior and packaged design systems"
slug: design-ux-governance
weight: 420
activity: "Design"
source: "02-design/design-ux-governance.md"
generated: true
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

> **Source identity** (from `02-design/design-ux-governance.md`):

```yaml
ddx:
  id: helix.design.ux-governance
  authoring:
    home: repo
```

# UX behavior and packaged design systems

## Scope and authority

The operator authorized reusable UX implementation guidance and then required
vendor/client-neutral package support on 2026-10-11. HELIX has no dependency on
any private design-system implementation. When an applicable design system is
available as npm packages, use it. If none is available, retain the selected
alternative or let the adopting project write its own concern.

This refines concern propagation, DESIGN.md and story-test-plan coverage.
ADR-011 retains Radix/shadcn ownership. No new public skill, runtime CLI,
tracker mutation, release or component-library slot is required.

## Decisions

- ux-interaction-patterns owns the neutral behavioral baseline. Existing
  ux-radix/AppKit selections compose it without changing their component owner.
- packaged-design-system owns the generic npm adoption contract. Project
  evidence supplies actual packages, versions, compatibility, exported APIs,
  tokens, supported themes, customization points and verification commands.
  No client, private product, package scope or audit tool is prescribed.
- Available applicable systems are preferred over rebuilding components.
  Existing selections require an authorized adoption update; unknown fit or
  unavailable registry access is a recorded question/blocker.
- Resolve competing library/style/toolchain prescriptions through existing
  project overrides and ADR policy. Compact contexts retain the behavioral
  floor and selected component owner even with many active concerns.
- DESIGN.md accepts local values or versioned external token references;
  component wiring belongs in TDs. Embedded/no-navigation views record actual
  applicability instead of inventing features.
- Optional STP UX Coverage maps six categories to the existing AC/test matrix.
  Legacy omission remains structurally valid; affected new UI readiness needs
  adoption. Structure does not prove test existence, execution or behavior.
- Run supplied applicable package checks. When tools are absent, projects
  define concrete presentation/accessibility checks; actual interaction tests
  remain separate. No provider, lint framework, audit executable or output path
  is universal.

## Acceptance and ordered implementation

1. Neutral and package concerns reach relevant UI/frontend contexts; API-only
   work and unselected concerns remain unaffected.
2. Local and fictional external-package DESIGN examples validate, including
   explicit absence of page navigation.
3. UX coverage positive/negative controls exercise the actual validator.
4. Plan/readiness gates name planned tests; completion requires observed results.
5. Public templates, examples, generated references and PR text contain no
   private-system or client-specific integration details from this change.
6. Regenerate references/artifacts; run just test, generated-content validation,
   artifact schemas, pre-commit and diff checks; update the existing PR.

## Review and verification scope

Astra ultra reviewed the original UX plan and implementation. Its resolved
findings concerned composition compatibility, pattern semantics, structural
versus runtime proof, phase sequencing, blank-cell rejection, navigation
applicability and compact-context retention. It independently passed 16 UX
checks and the diff check. The subsequent operator correction generalizes the
package concern, external example and all downstream advice; it does not claim
an additional Astra review or consumer runtime run.

The original full just test and pre-commit gates passed. Optional deck rendering
was skipped for missing pptxgenjs; existing seal and advisory warnings matched
the baseline. Current generalized revision: `uv run --with pyyaml --python 3.12 just test`
exited 0, including all 16 UX tests and 57 catalog examples. Generated-content
validation and schema validation exited 0. The scan of shipped workflow/code
and public content found no private-product/client identifiers introduced by
this change. The optional render skip and baseline warnings remain as above.
Pre-commit runs again on the final commit; no consumer runtime result is claimed.
