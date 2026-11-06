---
ddx:
  id: ADR-016
  status: accepted
  authoring:
    home: repo
---

# ADR-016: Visuals are one vocabulary, drawn from governed sources

## Problem

Every DocumentDrivenDX product draws pictures its own way. documentor draws Mermaid flowcharts, a
hand-routed deployment SVG, an HTML field guide, and presentations through a browser-only
renderer. HELIX's own design documents hold hand-drawn diagrams beside a model that could draw
them, and the agent that writes guide pages draws its own Mermaid instead of citing the
generated views. The same picture of HELIX exists four times in four styles. Colors come from
four places, none of them the product's theme, and a hand-drawn picture drifts from the code with
nothing to say when. Nothing tells an author whether a picture is worth drawing, or which kind
answers the reader's question.

## Decision

We will treat a visual as data in one closed vocabulary, drawn from a governed source, and decide
in HELIX when to draw one and which.

- The vocabulary is DocumentDrivenDX/umf-visual's `umf.visual` 1.0: seven kinds (`flow`, `sequence`,
  `structure`, `state`, `timeline`, `comparison`, `metric`) and 22 forms, with roles, statuses,
  evidence, and walkthrough steps, and no color, size, or position.
- DocumentDrivenDX/ux-builder draws it (`@ux-builder/visuals`) in the product's theme; documentor
  produces visuals from the architecture model and its generators and places them on every site.
- HELIX owns the decision: `workflows/references/visuals.md` says when a visual earns its place
  (structure prose cannot carry, one question the reader has, a governed source) and which kind
  and form answers which question. Each artifact type lists the visuals it usually draws in its
  `meta.yml` (`visuals:`).
- An artifact writes a visual as a fenced block with a stable id: a `visual` block naming its
  source or its kind, form, and question, or, until documentor draws those, a Mermaid block whose
  first line names the id. `validate-instance.py` checks the id, the kind and form, and the
  question, and warns on a visual the type does not list.

## Why We Chose This

### Over each product keeping its own renderer
The pictures already disagree in look and meaning: a dashed line means "not built" in one place
and nothing in another. One vocabulary with one set of roles lets a reader learn the shapes once.
Keeping the vocabulary in umf-visual, apart from both its producers and its renderer, lets HELIX,
documentor, and an app built on ux-builder share it without depending on each other.

### Over free-form diagrams in Markdown
Free-form Mermaid lets any author draw anything, so each draws differently and nothing checks
that a picture matches its source. A closed set of kinds with a question per visual makes the
choice reviewable, and a governed source makes the picture checkable.

### Over drawing every picture a template slot invites
An empty diagram block in a template reads as an instruction to fill it. The rules make drawing
conditional: a table or a sentence is the right answer when it carries the content, and the
type's list is a guide, not a quota.

## Consequences

- Authors stop drawing by hand what a model or an artifact already holds; existing hand-drawn
  diagrams are replaced by id as documentor gains each producer.
- The kinds and forms live in two places, `umf.visual` and `validate-instance.py`'s
  `VISUAL_FORMS`; adding a form in umf-visual means adding it here, and the meta validator reads the
  same table so a type cannot list a form the instance check rejects.
- Until ux-builder's renderer and documentor's producers land, artifacts keep Mermaid with
  `%% id:` lines; the ids are what the later move replaces.
- A new kind needs two pictures it alone serves; the closed set is deliberate.
