---
ddx:
  id: documentor.product-vision
  authoring:
    home: repo
---
# documentor product vision

## Mission statement

Every repository a team governs with HELIX gets documentation its readers can use, in one shape,
kept current by the pull request that changes the code.

## Vision

A developer opens a repository they have never seen and finds an overview, an architecture page,
one request traced through the code, and a guide to the first change. An operator finds what
deploys where, every setting and where its value comes from, and the routine procedures. A user
finds a first session that works as written and the everyday tasks. A data consumer finds the
datasets, their lineage, and what each metric means. Each page says what it was built from, and
the build fails when any of that moves.

HELIX says what a guide is: the audiences, the page kinds, the writing standard, the provenance
header. documentor is the tool that makes the deterministic parts exact (detection, generated
references, architecture views, the drift gate, the site) and leaves judgment to an agent in a
HELIX session. A repository with HELIX and no documentor still gets a guide by hand; documentor makes
it checkable.

## Positioning

- Against hosted documentation platforms and AI writers (Mintlify, Swimm, DeepWiki): documentor
  plans pages from governed intent (vision, requirements, decisions, stories), not from code
  alone; keeps Diátaxis discipline; records provenance at section granularity; and stays in-repo
  Markdown with data-handling rules, which a hosted writer cannot offer a client with regulated
  data.
- Against the stack's own reference tools (mkdocstrings, Storybook, terraform-docs, tablespec's
  guidebook): documentor delegates to them and links their output; it never duplicates a reference
  a better tool already publishes.
- Against site generators (mkdocs, Hugo, Hextra): documentor emits into the site a repository has
  and scaffolds one only when it has none.

## Who it is for

Teams that run several repositories with HELIX and want their documentation consistent across all
of them: the same audiences, the same page shapes, the same gate, with each repository adding
only what is particular to it (a trait, a generator, a page).
