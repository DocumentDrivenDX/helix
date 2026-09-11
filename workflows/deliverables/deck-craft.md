# Deck craft

How the `present` mode turns a large set of governed artifacts into a short
deck that a reader can follow from the titles alone. `deck-flows.yml` holds
the ordered beats per occasion; this file holds the reasoning behind them and
the tests a storyboard must pass. Numbers in brackets point at the sources at
the end.

The craft comes from five traditions that agree more than they differ:
consulting structure (Minto, McKinsey), presentation design (Duarte,
Reynolds), pitch templates (Kawasaki, Sequoia, Y Combinator), narrative
memos (Amazon, Raskin, TED), and the spoken summary formula that NotebookLM's
Audio Overview makes visible. What they share: one idea at the top, a few
messages under it, evidence under each message, and an order in which each
step answers the question the previous step raised.

## Distillation

A project carries a vision, requirements, designs, plans, reports, and
decisions. A deck carries one takeaway, three to five messages, and the
evidence for each. Distillation is the work of getting from the first to
the second without inventing anything.

Think bottom-up, present top-down. Minto's pyramid puts the answer at the
top, groups the supporting arguments beneath it, and puts the data under
each argument; the analysis runs from data to answer, the delivery runs the
other way [1]. Anderson's throughline is the same idea for talks: one
sentence of 15 words or fewer that every part of the talk serves, with
anything that does not serve it cut [11].

Before any of this, inventory the scope. Distillation ranks and cuts from
what was read, so reading too little produces a confident deck about a
corner of the subject. List every document in the declared scope by
authority with the claims its sections make, and the concepts that recur
across documents (`scripts/corpus-inventory.py` does the counting).
Cluster those into five to nine concept groups in the audience's words.
The groups are the candidates; the steps below choose among them, and
every group the deck does not carry is written down as omitted with its
reason. Breadth (`survey` or `deep-dive`) is a declared control in the
Brief, not a consequence of which sections happened to be read.

Work in this order:

1. Name the decision. Who is in the room, what will they decide or do, and
   what would make them say yes or no. The decision ranks everything that
   follows; a fact that does not move the decision does not enter the deck.
   Kawasaki's ten-slide limit rests on the same premise: a room cannot hold
   more than about ten concepts, so choose the ten that decide [6].
2. Write the takeaway. One sentence, in the audience's vocabulary, stating
   what will be true for them if they act. It is the title slide and the
   last line of the ask. If you cannot write it, you do not yet know what
   the deck is for; go back to the decision.
3. Choose three to five messages. Each is a claim that, if believed, moves
   the audience toward the takeaway. Minto's rule of three for supporting
   points is the default; five is the ceiling [1]. Together the messages
   cover the decision without overlapping (Minto's MECE test) [1].
4. Attach evidence to each message. For every message, list the source
   sections that prove it and the single figure, example, or comparison you
   will put on the slide. A message with no source section is a gap to ask
   about or an assumption to record, never a slide. Every number keeps its
   source through to the appendix.
5. Rank by the decision. Order messages by how much each one moves the
   decision, not by how the sources are organized. The source order is the
   author's; the deck order is the audience's.

What to cut, in this order: background the audience already has (Minto's
Situation is one slide at most, and only what they already agree with [1]);
detail that proves nothing on the slide (it goes to speaker notes or the
appendix, as McKinsey decks push supporting data to appendices [2]);
messages that repeat another message from a different angle; anything that
requires a HELIX or engineering term the audience does not use. Reynolds
calls the remainder signal and everything else noise; the hardest edit is
to stop adding [5].

## Narrative arcs

An arc is the order of the messages. Pick by occasion, not by preference;
`deck-flows.yml` fixes the order per occasion. The arcs below are the ones
the flows draw on.

Answer first (Minto's pyramid). Lead with the recommendation, then the
reasons, then the evidence. Use it when the audience is deciding and is
short on time: proposals, status reviews, board updates [1]. The SCQA
opening (situation the audience agrees with, the complication that changed
it, the question that raises, the answer) is the introduction to a pyramid,
not the whole deck [1].

Change, stakes, promised land (Raskin's strategic narrative). Name a change
in the world before naming the product; show that the change makes winners
and losers; describe the promised land the audience wants; only then
introduce what you offer as the means to get there; then prove you can
deliver [10]. Use it when the audience must first accept that the old way
stops working: investor pitches and evaluation briefings.

What is, what could be (Duarte's sparkline). Alternate between the current
state and the better state so the gap stays visible, end with a call to
action and a picture of the world after the audience acts, which Duarte
calls the new bliss [3]. Use it when the audience must feel the gap, not
just measure it: internal alignment, kickoffs.

Problem, solution, proof (Sequoia, Y Combinator, Kawasaki). Purpose,
problem, solution, why now, market, competition, model, team, financials,
vision is Sequoia's order [7]; YC's is close, held to 10 to 12 slides with
one takeaway per slide and detail pushed to an appendix [8]. Use it for
pitches and product walkthroughs, where the audience will check each claim
against the last.

Plan, actual, next. Commitments, what happened against them, why the
variance, what changes now, what you need. This is the status arc; it is a
pyramid with the headline state at the top.

Written narrative. Amazon replaced decks with six-page memos because a
narrative forces the writer to say what matters more than what, and how
things relate, where slides let both go unsaid [9]. The lesson for decks:
the storyboard is the narrative. If the titles do not read as a memo, the
deck will not either.

## Horizontal and vertical logic

Two tests, both from consulting practice [2].

Horizontal logic: read only the titles, first to last. They must form the
argument: each title answers the question the previous title raised and
sets up the next, and the last content title is the ask. A reader who sees
nothing but the titles should be able to state the takeaway and the
decision. Titles that name topics ("Results", "Approach") fail the test;
titles that repeat each other fail it; titles that could be reordered
without loss fail it. The fix is always in the titles, never in the bodies.

Vertical logic: on each slide, the body proves the title and the title is
proven by the body. Strip the title and ask what the exhibit shows; the
answer must be the title. Strip the body and ask what would prove the
title; the answer must be the exhibit. A title the body cannot prove is
rewritten to what the body does prove, or the slide is cut. Duarte's glance
test is the reader-side version: a slide must make its point in about three
seconds [4].

Both tests run on the storyboard before bodies exist, and again at the gate
after bodies exist. The mode's gate treats a failure of either as a loop
back to the storyboard, not as a polish item.

## Transition rules

Each title answers the question the previous slide left open. The reader
should be able to say, after any slide, what the next one has to address;
the next title addresses it. When you cannot name the question a slide
raises, it has no successor and belongs in the appendix or the notes.

One number per beat. A beat that needs three numbers is three beats or one
table. The number the slide is about gets the callout; every other figure
waits for its own slide or goes to the notes.

Callbacks. The ask repeats the takeaway's words. Proof slides use the same
noun the problem slide used. When a later slide relies on an earlier one,
say so in the title or the first bullet. The NotebookLM overview does this
aloud ("so we've established", "as we wrap up") and it is why a listener
can follow a long summary without notes [12].

Signpost the shape early. A short deck needs no agenda; a deck of ten or
more slides names its three to five sections up front so the audience
knows where the ask lands. NotebookLM's opening does the same job: a hook,
then what the source is and why the listener should care, before the first
point [12].

Close with synthesis, not summary. The last content slide restates the
takeaway as the ask with owners and dates. Anderson's advice is to script
the opening minute and the closing lines and to zoom out to the vision at
the end [11]; NotebookLM ends on a final thought or question rather than a
list [12]. A "Questions?" or "Thank you" slide is not a close.

## Length budgets

The budget comes from the time slot, not from the source volume. Half a
slide per minute of talk is the working rate (`slides_per_minute_of_talk`
in `slide-patterns.yml`): a 5-minute slot holds 2 to 3 content slides, 10
minutes holds 5, 20 minutes holds 10, and 30 minutes holds 12, which is the
cap without an explicit exception. Kawasaki's 10/20/30 sets the same shape:
ten slides, twenty minutes, thirty-point type, so the deck fits the
attention available and leaves the rest of the slot for discussion [6].
Sequoia and YC land at 10 to 12 slides for a pitch [7][8].

Per slide, the pattern limits in `slide-patterns.yml` hold: at most 60 body
words, at most 5 bullets, one visual. Reynolds' rule is that slides support
the speaker and are not the document; a slide dense enough to read alone is
a "slideument" and fails as a slide [5][4]. The detail lives in the notes
and the appendix, which have no word budget.

When the slot shrinks, cut beats in the order `deck-flows.yml` gives, never
by compressing more content into each slide. A one-pager or brief is a
different kind, not a denser deck.

## Storyboard before bodies

McKinsey teams write a ghost deck before any production: one line per slide
with the action title, a note on the exhibit that will prove it, and a tag
saying whether the data is in hand [2]. The narrative is locked before
anyone draws a chart. Duarte's version is a sticky note per idea, one idea
per note, arranged and re-arranged until the order holds [4].

The `present` mode's storyboard is the same artifact. Its contents, in
order:

1. The flow, chosen by occasion from `deck-flows.yml`.
2. The takeaway sentence.
3. The three to five messages, each with its evidence table: source section,
   figure or example, and whether the source holds it or it is a gap.
4. One claim title per beat in the flow, each mapped to a message, with a
   one-line note of the exhibit. Optional beats are included only when a
   message needs them.
5. The horizontal-logic test, recorded as pass or as the rewrites it took.

No body text, no visual specification beyond the one-line exhibit note, no
pattern choice yet. When the titles read as the argument, bodies follow;
until then, the titles are the work. Titles rewritten after bodies exist
usually mean the bodies were written to the wrong story.

## Sources

1. Barbara Minto, The Pyramid Principle, and the SCQA introduction:
   https://modelthinkers.com/mental-model/minto-pyramid-scqa and
   https://thinkinsights.net/strategy/scqa-logic
2. McKinsey-style action titles, horizontal and vertical logic, and the
   ghost deck: https://a1slides.com/mckinsey-presentation-framework/ and
   https://www.autopresent.ing/blog/mckinsey-deck/
3. Nancy Duarte, Resonate, the sparkline and the new bliss:
   https://www.duarte.com/blog/business-communication-demands-3-act-story-structure/
4. Nancy Duarte, slide:ology, the glance test and one idea per slide:
   https://hbr.org/2012/10/do-your-slides-pass-the-glance-test and
   https://www.duarte.com/resources/guides-tools/the-glance-test/
5. Garr Reynolds, Presentation Zen design principles:
   https://www.garrreynolds.com/design-tips
6. Guy Kawasaki, the 10/20/30 rule: https://guykawasaki.com/the_102030_rule/
   (summarized at
   https://sixminutes.dlugan.com/10-20-30-rule-guy-kawasaki-powerpoint/)
7. Sequoia Capital, Writing a Business Plan:
   https://www.sequoiacap.com/article/writing-a-business-plan/
8. Y Combinator, How to Build Your Seed Round Pitch Deck:
   https://www.ycombinator.com/library/2u-how-to-build-your-seed-round-pitch-deck
   (summarized at https://www.joinleland.com/library/a/y-combinator-pitch-deck)
9. Amazon narrative memos, Bezos on why narrative beats slides:
   https://www.cnbc.com/2018/04/23/what-jeff-bezos-learned-from-requiring-6-page-memos-at-amazon.html
   and https://slab.com/blog/jeff-bezos-writing-management-strategy/
10. Andy Raskin, The Greatest Sales Deck I've Ever Seen:
    https://medium.com/the-mission/the-greatest-sales-deck-ive-ever-seen-4f4ef3391ba0
11. Chris Anderson, TED Talks, the throughline and scripted open and close:
    https://www.ted.com/read/ted-talks-the-official-ted-guide-to-public-speaking
    (notes at https://calvinrosser.com/notes/ted-talks-chris-anderson/)
12. NotebookLM Audio Overview, the observable structure:
    https://blog.google/technology/ai/notebooklm-audio-overviews/,
    https://support.google.com/notebooklm/answer/16212820, and
    https://nicolehennig.com/notebooklm-reverse-engineering-the-system-prompt-for-audio-overviews/
