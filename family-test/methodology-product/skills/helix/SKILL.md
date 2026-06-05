---
name: helix
description: |
  HELIX product methodology. Activates when `.helix.yml` lists `helix` as
  active OR when fallback heuristics fire (workflows/methodology.yml under
  the working dir).

  Distinct from the helix-library skill, which is data-only.
version: 0.1.0
license: MIT
---

# HELIX product methodology

When this skill is active:

1. Read the consumer repo's `.helix.yml` (root-level). If absent, fall back
   to heuristic activation and emit the disambiguation banner (design §1.3).
2. For each entry in `methodologies:` with `id: helix`, treat `root:` as the
   subtree where helix instance documents live.
3. When asked to author or edit an instance document, follow the type's
   `template.md` and `prompt.md` from the helix-library plugin.
4. Instance edges (PRD → FEAT, ADR → technical-design, etc.) belong in the
   instance's frontmatter under `ddx.links:` per design §2.3. Never embed
   them in the body or in this skill's prompts.
5. Cross-methodology edges (e.g. PRD informs helix-infra:CI-NNN) must be
   declared in `external_edges:` of `workflows/graph.yml` first, then in
   the instance frontmatter.

This skill never rewrites unknown frontmatter keys; round-trip preserves
key order and unknown fields verbatim (design §2.5).
