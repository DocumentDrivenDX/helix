---
title: The Anti-Slop Rules
weight: 4
---

Slop is prose that reads as generated: label titles, reversals, slogans,
hedges, numbers with no source. This page lists the rules HELIX enforces
against it when the `present` mode of the HELIX skill turns governed documents
into [decks and briefs](/use/decks-and-briefs/), where each rule runs, and
what it leaves to a person. It assumes you have read that page. After this one
you can read a gate report and know which finding means what.

## Where the rules run

| Stage | What runs | Tool |
| --- | --- | --- |
| Storyboard | Titles exist before bodies; the headline pass and the titles-only read run on them first | the mode contract; `check-deliverable.py` on the script |
| Script gate | Title, shape, vocabulary, number, placeholder, visual, limit, density, coverage, and ordering checks | `scripts/check-deliverable.py` (beside the skill) |
| Prose lint | Sentence-level rules on the script and on this site | Vale with the Helix styles (`just lint-prose`) |
| Render gate | Geometry checks on the slide file, then every slide as an image, inspected | `scripts/deck-qa.py`, LibreOffice, `pdftoppm` |
| Eval | The gate re-runs on each brief, plus a rubric line that reading only the titles tells the story | `evals/briefs.yml` |

## The voice the rules protect

`workflows/voice.yml` defines two profiles that matter here. Governed
documents use `artifact-signal`: lead with the decision, use exact IDs and
paths, name assumptions and non-goals. Decks and briefs use `human-facing`:
open with what it means for the reader, then the evidence, then the ask; make
every title a claim; define or drop every HELIX and engineering term, with
provenance in an appendix; a source for every number. Its `avoid` list seeds
the rules below: em dashes and filler tokens, rhetorical reversals,
rule-of-three padding, bold-label bullets, reader-steering tics, hedges,
placeholders, internal shorthand.

## The headline pass

Every unit title in a script goes through `title_slop`. A title is one
sentence with a subject, a verb, and one concrete noun; eight words is the
target and ten the hard stop. Each rule below names the shape it catches, with
a case from the test fixture.

| Rule | What it flags | Flagged example |
| --- | --- | --- |
| contrastive reversal | "not X, but Y", "X, not Y", a trailing "is not" | `HELIX is a methodology you adopt, not a platform you join` |
| colon list | a colon followed by two or more items | `Three failures repeat on every AI-assisted team: drift, local decisions, lost context` |
| colon reveal | a colon followed by one item | `The best part: it learns` |
| imperative chain | three or more commands in one title | `Write the brief, check alignment, plan the work, run it in your own factory` |
| listicle count | a number before a listicle noun | `Five things change once the catalog ...` |
| stacked negation | two or more negatives | `HELIX takes no runtime, no tracker, and no technology choice away from you` |
| rule-of-three list | "A, B, and C" | the same title as above |
| flattery | compliments to the reader | `Your agents can ship with the discipline your best teams already use` |
| pseudo-aphorism | slogans: "is the new", a trailing "matters" | `Documentation is the new code review` |
| universal claim | "teams switch", "every team" | `Teams switch when every change traces back to a governing document` |
| mannered phrase | idioms from a vendored list | `Documentation earns its keep on every review` |
| inventory count | a catalog size after a verb like "ships", "routes", "with" | `One skill routes twenty-one modes over those documents` |
| hedge | `also`, `just`, `simply`, `really`, and similar | `Alignment simply reads the documents` |
| over-length | more than ten words | `Each document layer governs the next one, from vision down to code` |

Slide titles get six more rules that internal document headings do not:
container title (four words or fewer ending in a category noun, such as
`Firm capabilities` or `Key considerations`), self-justifying section (`Why we
control it`, `How to read this slide`), shouting label (an all-caps line of
four or more words), invented status (`Working hypothesis`, `tbd`, `in
flight`), taxonomy code (`Zone 6`), and marketing register (`Leverage the
platform layer`).

Titles that pass: `Agent code drifts from its specs and decisions`; `One
alignment pass finds three affected specs before coding` (an evidence count,
not an inventory); `Each document layer governs the next, from vision to code`
(ten words exactly); `Use cases` (a concrete noun, not a container).

## Shapes and restatement

The same script gate runs `shape_slop` over every bullet and every text cell in
a Visual spec (panel labels, comparison rows, captions, verdicts). A shape gets
the label rules plus the closers a title cannot carry: a reversal or aphorism
used as a closing line (`That is what makes it portable.`), flattery, and
trailing commentary, a second sentence that explains the first (`Verifies
citations. Built as the worked example for moving a check between products.`).
Labels that name a part of a figure (a layer, a step, a spoke) only get the
shouting-label check.

Within one slide, the gate compares the title, the on-slide bullets, and the
visual cells pairwise. Two shapes whose content words overlap by half or more
are a restatement: the bullet that repeats the panel, the verdict that repeats
the title. The check is lexical and stays inside one slide.

## Horizontal and vertical logic

Horizontal logic is the titles-only read: in order, the titles state the
argument and end in the ask. The mechanized part is narrow: consecutive titles
must share at least one content word (crude stems, so `gates` matches `gate`),
which is how a title the reader could reorder without loss gets flagged.
Vertical logic, that each body proves its title and nothing else, is a
read-through the mode contract requires at the gate; no script checks it.

## Where the title rules come from

The title and shape rules are a port of the sloptimizer skill's `headline` and
`slide` targets, so the gate holds on a host without that skill. The fixture
`tests/fixtures/validate-deliverable/headline-cases.json` comes from the
upstream repository unchanged (a note beside it records the commit), and
`tests/validate-headline-sync.sh` runs every case through the port and fails
when the two disagree; with the upstream source on the machine it also
compares the fixture and the four phrase lists byte for byte. A host with
sloptimizer installed can run `slop-audit.sh --target slide` on the rendered
`.pptx`, whose text it extracts shape by shape; the mode contract names both
paths.

## The rest of the script gate

Beyond titles, `check-deliverable.py` blocks on:

- HELIX vocabulary in a title, body, or notes: artifact IDs such as `FEAT-16`
  or `ADR-3`, `bead`, `ratchet`, `work item`, `acceptance criteria`, `AC1`,
  `artifact graph`, `frame activity`, `ddx`. They belong in the Sources table.
- A number in a body that does not appear in the Sources table, single digits
  excepted. A unit that cites no source, or cites a source row that does not
  exist.
- Placeholder text anywhere: `[TODO]`, `TBD`, `[Fill in]`, `[...]`, a
  bracketed capitalized phrase.
- A visual that is one generic word (`chart`, `diagram`, `none`) or fewer than
  six words. The spec must say what it shows, its series, and its source.
- Coverage. The Brief declares breadth as `survey` or `deep-dive`; the Story
  carries a concept coverage table where every group is `covered` or
  `omitted`, and an omitted group has a reason of at least three words. A
  survey covers at least five groups. Every must-cover concept shares a content
  word with a covered group; no must-omit concept appears in a title or body.
- Order. A deck opens with the `title` pattern and closes with `ask-next-steps`
  then `appendix-sources`. The Render section names a rendered file and records
  that a person inspected the slides.

It warns on pattern limits from `slide-patterns.yml` (bullets, words per
bullet, body words, title words), more than two consecutive units of one
pattern, more than twelve content slides, and a missing export list.

## Prose lint

Vale with the Helix styles runs on the hand-authored site pages and on every
deliverable script. Errors, which fail the check: em dashes, and filler tokens
such as `delve`, `leverage`, `seamless`, `robust`, `landscape`, `unlock`, `in
summary`. Warnings: hedges, passive voice, sentences over thirty words,
reader-steering tics (`worth noting`, `the real problem`), and wordy phrases
with a shorter form (`in order to`).

## The visual gate

`deck-qa.py` reads the slide file's shapes and reports per slide. Blocking: a
shape past the slide edge, a text box that needs more height than it has (an
autofit box that fits after shrinking to three quarters of its size is a
warning instead), two text shapes that overlap, a table that grows past the
bottom margin. Warnings: a shape inside the half-inch margin, type below twelve
points outside the footer band, text crossing another shape's edge, a line
through text, a table taller than declared, and a slide with the same layout
as the one before it. With LibreOffice and `pdftoppm` present it also renders
every slide to an image and a labeled contact sheet; the mode requires a
person to look at those images before the deck passes.

## What the rules do not catch

The rules match shapes and words. They do not catch a paraphrase of a slogan,
a title that is a claim but the wrong one, a figure that is in the Sources
table and still misreads its section, or a slide that passes every rule and
should not exist. Fidelity to the sources, vertical logic, and the decision to
cut a unit stay with a person, who reviews the script like any other artifact
before it goes out.
