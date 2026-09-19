# Current-State Inventory Generation Prompt

Record what the organization already has, graded for evidence, before any
target state is proposed.

## Storage Location

Store at: `docs/helix/00-discover/current-state-inventory-[estate-name].md`

## Purpose

Answers: **What does this organization actually have, and how much of that do
we know rather than assume?**

The second half is the point. An inventory that lists components without
grading them reads as knowledge and is often mostly hearsay — a slide box and
a running production system look identical in a table. The evidence grade is
what separates them, and it is the artifact's reason to exist.

## Role Boundary

A Current-State Inventory is not an architecture. Architecture states what the
system should be and records the decisions that get it there; this states what
is there now. When an entry needs a decision, the decision goes in an ADR and
this inventory cites it.

It is also not a [[data-flow-analysis]]. That documents **one** business
process end to end — its actors, transformations and constraints. This covers
**many** components at register depth, one row each.

It is not a vendor evaluation. Comparative assessment belongs in
[[competitive-analysis]].

## Method

1. **Fix the boundary first.** Name what the inventory covers and what it
   excludes. An unbounded inventory is never finishable and never trusted.
2. **Choose one grouping scheme** — capability, layer, owning function, vendor
   — and hold it for the whole instance. Mixed schemes hide gaps.
3. **One row per component.** Resist bundling: two products under one row take
   one grade, and the weaker evidence disappears behind the stronger. If two
   things have different grades, owners or adoption states, they are two rows.
4. **Grade every row, then find the source.** Write the citation before the
   grade is allowed to be Evidenced. A source is a named document, meeting,
   or person plus a date — not "the team says".
5. **Tally the totals from the rows you just wrote.** Never carry them
   forward.
6. **State the unevidenced share in words.** The reader should not have to do
   arithmetic to learn how much of this is assumption.

## Grading Honestly

The pressure on this artifact is always toward optimism: a sponsor wants the
estate to look known, and every Assumed row reads as a gap in the author's
work rather than a gap in the organization's knowledge. It is the opposite.
**The unevidenced rows are the finding.** An inventory that grades two-thirds
of its entries Assumed has done its job and should say so in its own words.

Watch for these specifically:

- **Bundling as flattery.** Merging rows reduces the count of unevidenced
  entries without changing what is known.
- **Evidenced by familiarity.** "Everyone knows we use X" is Assumed.
- **Aspirational drift.** A component that is planned, funded and staffed is
  still Aspirational until it exists.
- **Stale totals.** Numbers carried from a previous revision assert a
  freshness the revision does not have.

## Inputs

- Existing architecture diagrams, slides and vendor lists — treat each as a
  claim to verify, never as a source
- Meeting notes, emails and interviews, which are where citations come from
- Any system of record for assets, licences or spend

## Quality Checks

- Every entry carries exactly one grade from the declared vocabulary
- Every Evidenced entry names a source and a date
- Totals tally against the rows in this revision
- The unevidenced share appears in prose
- Scope and exclusions are both stated
- No target state, recommendation or decision appears anywhere
