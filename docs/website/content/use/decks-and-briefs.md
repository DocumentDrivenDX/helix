---
title: Decks and Briefs from Governed Documents
weight: 3
---

HELIX documents serve the people and agents doing the work. The
`present` mode of the HELIX skill turns them into something a person outside
the project reads or watches: a deck, a one-pager, or a brief, with every
figure traced to the document section it came from. This page assumes you have
a governed set of project documents (a vision, requirements, designs) and an
agent that runs the HELIX skill. After reading it you can ask that agent for a
deck and judge the one it hands back.

## Who it is for

Teams whose sponsors, clients, and executives do not read PRDs. The deck says
what the documents say, in the audience's words, and nothing the documents do
not say. The Markdown script is the document of record, a
[deliverable artifact](/artifact-types/iterate/deliverable/); the rendered
files are fidelity evidence, proof that the script renders as written. A person
reviews the script like any other artifact before it goes out.

## The pipeline

1. Brief. Name the audience, the occasion, the decision you want from the
   room, the time slot, and the kind: deck, one-pager, or brief. Without an
   audience and a decision, nothing gets written.
2. Inventory and scope. The skill reads every document in scope, counts the
   concepts that recur, reads the structure and roles the documents encode,
   and clusters them into five to nine groups. You choose the breadth: a
   survey covers the whole scope; a deep-dive names what it leaves out. Each
   group gets marked covered or omitted, with a reason.
3. Storyboard. One takeaway sentence, three to five messages each with a
   source section, then one claim title per beat, before any body text. The
   titles-only test: read the titles in order; they must state the argument
   and end in the ask. When they fail, the titles change, not the bodies.
4. Headline and shape passes. Each title is one sentence with a subject, a
   verb, and one concrete noun, ten words or fewer. Each bullet, label, and
   caption has to say something the visual does not.
5. Patterns and figures. Each slide gets one pattern (claim with evidence,
   comparison, diagram, statement, ask) and one visual: a chart with named
   series, a layer stack, a cycle, an icon list. A relationship is a diagram,
   not a bullet list.
6. Look. One of the four looks below.
7. Render. The script renders to a slide file and, where the host can export
   one, a PDF.
8. Gate. Script checks first, then a screenshot pass: every slide renders to
   an image and someone looks at each for overflow, collisions, and missing
   visuals. A deck nobody looked at does not pass.

## What the gate refuses

- A number in a body that no source section holds.
- HELIX vocabulary in bodies: artifact IDs, activity names, and work-item
  terms live in the Sources appendix, not on a slide.
- Label titles ("Results", "Approach") and titles that fail the titles-only
  read.
- Bullets that restate the visual or each other.

## The four looks

- `editorial`: serif display type, dark opening and closing slides, light
  content; for evaluation calls and board packs.
- `technical`: one sans-serif family, light throughout, square markers; for
  engineering audiences.
- `bold`: dark throughout, with the secondary hue leading; for pitches and
  keynotes.
- `classic`: serif display type and no marker shape; for proposals and
  printed briefs.

Palette and type come from your project's design-system artifact when it
declares them, otherwise from the HELIX default theme.

## What a host needs to render

Rendering is optional. To produce the files, the host needs Node with
`pptxgenjs` for the slide file, LibreOffice for the PDF export, `pdftoppm` for
the screenshot pass, and `rsvg-convert` or ImageMagick for the icons. Without
them, the skill still writes and checks the script, and says which host can
render it.

## The worked example

HELIX's own evaluation deck,
[One discipline governs agent work from intent to release](/artifacts/deliverables/del-001-helix-evaluation-deck/),
came out of the product vision, requirements, and workflow documents this way.
Its page carries the script, the sources, the gate record, and the rendered
PDF. The full mode contract is on the
[present reference page](/reference/workflow-modes/present/).
