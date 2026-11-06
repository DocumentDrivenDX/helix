# Writing pass

HELIX keeps two layers. Artifact instances under the project's HELIX root are the system of record: agents load them as context, reviewers check them for traceability, and they keep the `artifact-signal` voice they were written in. People read projections of them: the pages `guide` generates for developers, operators, users, and data consumers (`workflows/references/publishing.md`), and the decks and briefs `present` generates (`deliverable`). This pass is for the projections. Every published page and every deliverable gets the same seven steps before handoff. Steps 3 and 6 are measured, so two authors, or two agents, reach the same bar in any repository that uses HELIX.

The rules live in `workflows/voice.yml`. Each profile's `limits` sets words per sentence, sentences per paragraph or list item, and words per table cell. The shared `prose` lists name phrases to avoid, status and authorship words, and gendered pronouns for an unnamed person. An audience names each page's voice and word budget; a deliverable takes its type's voice. documentor (`documentor check-pages`) measures guide pages, and `skills/helix/scripts/validate-instance.py` measures a deliverable (its type sets `prose.audience: human`); both report each breach as a `prose.*` finding.

## Information only

A page states facts about the system and how to work with it. It does not carry:

- who wrote, owns, updated, or reviews it. Where a fact needs an owner, such as who supplies an unknown, name the role ("the architecture owner"), not the person;
- its own status: "draft", "provisional", "pending review", or "validated";
- to-dos, pending trials, or work for someone else to do;
- sentences about the page itself, such as "this document covers".

Authorship, status, and history belong in source control and the tracker; where the page came from is its provenance header (`publishing.md`); open work belongs in a work item. Evidence a claim rests on is a fact and stays, written about the system: "the tests run offline", not "this page was not checked live". This rule refines the `artifact-signal` profile's `avoid` list (delivery-history citations, unsupported claims) and does not relax it.

## The pass

1. **Name the reader and their task.** The flow states it for each page; restate it for yourself: who opens the page, and what can they do after reading it? Each section must serve that task. Cut or link anything else.
2. **Review the content.** Read the page as its reader, against the sources it describes, before touching the wording:
   - **Each section serves the reader's task.** A section the reader does not need goes.
   - **Each claim is current.** Check every statement of status, behavior, location, or count against the code, the configuration, and the governing artifacts it rests on. Where an artifact and the code disagree, the page follows the code and the disagreement goes to the handoff report, for `align` to settle in the artifact; never carry a claim because an artifact states it.
   - **Nothing is copied wholesale.** The page explains; the artifact records. A table that restates an ADR, a contract, or the configuration becomes a one-line summary with a link.
   - **Nothing is about the document.** Status notes, authorship, to-dos, and owner-of-a-gap lines leave for the tracker (see "Information only").
   - **Reference data a reader looks up**, such as a long table of limits, moves into a collapsed `<details>` block or a reference page of its own.

   List in the handoff report what was cut, moved, or corrected and the source for each correction; the page carries none of that.
3. **Measure.** Run `documentor check-pages <page>` (or `validate-instance.py` for a deliverable); without a tool, count against the profile's limits by hand. It prints each long sentence, crowded paragraph, overfull cell, and avoided phrase with its line, and the word count against any budget.
4. **Cut before you rewrite.** Remove what the "Information only" section excludes and what a link can carry: restated rules, repeated summaries, narration of the page's own structure. Move evidence a reader opens only to check a claim, such as long source lists and each test's limits, into a collapsed `<details>` block under its table. A `<details>` block does not count against the budget.

   Cut whole points, never grammar. Dropping articles, verbs, or subjects to reach a budget produces telegraph prose: "one reaches the menu", "sharing one trace with the gateway's in its collector". If a page is still over budget after the cuts, cut another point or split the page.
5. **Rewrite what is left.**
   - Lead each section with the sentence that answers its heading.
   - Use one idea per sentence, and keep the actor and the verb: "the service saves the record", not "the record is saved".
   - Use "is", "has", and "does"; write the plain verb rather than a noun made from it.
   - Put a citation (a decision, a test, a path) at the end of the sentence it supports, once.
   - Give a table cell one fact. A cell that needs a second sentence wants a row, a note under the table, or a `<details>` block.
   - Keep must, should, and may, every identifier, and every stated unknown when shortening.
   - Refer to an unnamed person as "they" or "them". Code and test names stay as written.
6. **Measure again.** Run the check until it reports no `prose.*` finding, then stamp the page's provenance (`documentor stamp`, or by hand).
7. **Read it once, aloud, as the reader, and check the grammar.** A sentence can pass every number and still sound like nobody. Look for:
   - an "it" or "they" whose noun is in another sentence, or is not there at all;
   - a sentence or cell with no verb where the cells beside it have one, and list items in different forms;
   - missing articles and doubled negatives ("not unfamiliar");
   - "; else" or a colon standing in for a sentence that should be written out;
   - table cells that end with a period while the cells around them do not.

## What the pass keeps

Every identifier, command, path, and must, should, or may the page takes from its sources, and every stated unknown. Evidence may move into `<details>`; it does not leave the page. The artifacts the page draws from are not edited by this pass: a fix they need goes through `align` or `refresh`.

## In a repository

`documentor check` gates guide pages in CI (`publishing.md`, "Checks"). For deliverables, a project can make `validate-instance.py` treat prose findings as blocking in its `.helix.yml`:

```yaml
prose:
  strict: true
  exempt:                 # paths to skip, relative to the .helix.yml directory
    - "docs/helix/06-iterate/deliverables/archive/*"
```
