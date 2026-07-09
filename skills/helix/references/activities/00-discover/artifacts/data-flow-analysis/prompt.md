# Data Flow Analysis Generation Prompt

Document one existing business process or data flow exactly as it operates
today, before any future-state solution is chosen.

## Storage Location

Store at: `docs/helix/00-discover/data-flow-analysis-[flow-name].md`

## Purpose

Answers: **What does this flow actually do today, and what would we need to
know to modernize it?** This is a concrete, technical companion to
higher-level Discover artifacts — it documents a system as it exists, not a
market or an opportunity.

## Role Boundary

Data Flow Analysis is not Data Design. Data Design documents the entity
model for a system being built (Design phase, future-state). Data Flow
Analysis documents an existing flow as it runs today (Discover phase,
as-is), before anyone has decided what the future solution looks like. One
instance covers one flow; a legacy migration effort typically produces
several, one per row of a discovery inventory.

## Key Principles

- **One flow per document.** Do not try to cover an entire legacy system in
  a single pass — break it into individual flows first.
- **Name sources and sinks concretely.** The actual system, table, file, or
  API, not a vague description like "the database."
- **Type every actor.** Each one is either a person doing a manual step or
  an automated system; say which, and what they actually do.
- **Capture data on both sides.** What comes in and what goes out, in
  enough detail that another engineer could find it without asking the
  person who wrote this document.
- **Constraints matter as much as the happy path.** Format, timing, volume,
  and access requirements shape any future redesign as much as the
  transformation logic does.
- **Don't skip Risks, Assumptions, and Modernization Notes.** This section
  is the payoff for doing this analysis instead of just reading the code or
  spreadsheet directly.
- **Leave the Notes section genuinely open-ended.** An engineer who fills it
  with several unprompted observations engaged with the problem; an empty
  Notes section on a nontrivial flow is a sign the analysis was rushed.

## Quality Checklist

- [ ] Every source and sink is named concretely
- [ ] Every actor is identified as a Person or an Automated System
- [ ] Business value is stated explicitly in Flow Summary
- [ ] Constraints on inputs and outputs are captured
- [ ] Overall complexity or scale is estimated, even roughly
- [ ] Risks, assumptions, and modernization recommendations are present, not
      left blank
