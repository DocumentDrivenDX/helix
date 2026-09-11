---
title: "Evolve"
slug: evolve
weight: 80
generated: true
---

Generated from [`workflows/modes/evolve.md`](https://github.com/DocumentDrivenDX/helix/blob/main/workflows/modes/evolve.md), the mode contract the HELIX skill loads. Edit that file, not this page.

Use when the user wants to add, remove, amend, or thread a requirement through
the HELIX artifact stack.

1. Read the entry artifact's frontmatter; collect its `ddx.id` and
   `ddx.links` list. `ddx.links` is the canonical instance-edge field used
   by both authoring and Evolve.
2. Build the impact graph from every governing artifact's `ddx.links` entries,
   then walk it in both directions:
   - typed downstream entries (`kind: informs`, `contains`, or `enables`) point
     from the current artifact to the target they inform;
   - typed upstream entries (`kind: informed_by`, `depends_on`, `requires`, or
     `references`) point from the current artifact to the authority it relies on;
   - untyped string entries are accepted as upstream shorthand for existing
     project documents.
   The upstream impact set is every artifact reachable through upstream edges;
   the downstream impact set is every artifact reached by reversing upstream
   edges and following downstream entries.
3. Compatibility: if `ddx.links` is absent, Evolve MAY read legacy
   `ddx.depends_on`, top-level `depends_on`, or `relationships.depends_on` as
   upstream edges, and `relationships.informs` / `relationships.referenced_by`
   as downstream edges. If canonical `ddx.links` is present, it wins; preserve
   legacy fields byte-for-byte but do not silently translate or mass-migrate
   them during an incidental Evolve pass.
4. When `ddx:` frontmatter is absent, fall back to filesystem traversal:
   activity-numbered directories in the project's HELIX layout supply the
   authority hierarchy; artifact-type directories supply the type
   relationships.
5. Detect conflicts with existing artifacts and open work.
6. Apply updates from the highest-authority artifact down: vision, PRD,
   feature specs/stories, architecture/ADRs, solution and technical
   designs, test plans, implementation plans, then code.
7. Surface conflicts explicitly when a downstream artifact contradicts an
   updated upstream — do not silently overwrite the downstream; route it
   through the §Align gap-to-implementation handoff instead.
8. Create follow-up work with dependencies where ordering matters.
9. Prefer **progressive evolution** of the specific affected artifacts over
   re-generating the stack. Converge on "verified + each finding-class folded
   into a gate" (a template check, an acceptance criterion, a concern
   propagation check, or a ratchet) — not on a bare reviewer "SHIP" verdict.
   Intrinsic gates (build, test, conformance, phantom-claim count) block;
   external adversarial review is advisory and never a hard gate.

Procedure: `workflows/actions/evolve.md` (deeper step detail; this file is the contract).
