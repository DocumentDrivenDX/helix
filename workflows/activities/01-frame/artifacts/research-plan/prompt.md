# Research Plan Generation Prompt
Plan the smallest useful research effort that will close the key knowledge gaps.

## Reference Anchors

Use these local resource summaries as grounding:

- `docs/resources/nng-ux-research-methods.md` grounds matching research
  methods to questions, evidence types, and product activity.
- `docs/resources/sba-market-research-competitive-analysis.md` grounds demand,
  pricing, customer, and market evidence expectations.

## Focus
- Frame the primary questions and the evidence needed.
- Keep methods, timeline, and risks lean.
- Make the deliverable and success criteria specific.
- Tie every method to a decision that will change if the evidence changes.
- Write one plan per study at `docs/helix/01-frame/research/[study].md`. A
  project's existing single `research-plan.md` stays valid.

## Studies With People

These sections are optional; add them when the study puts people in front of
the product or a prototype.

- **Scenarios** under Methods: each is a goal in the participant's words. Use
  no interface words, so the scenario does not tell them where to click.
- **Success Criteria** under Methods: what the participant has achieved when a
  scenario succeeds, citing the `US-<n>-AC<m>` IDs it exercises.
- **Screener** under Methods: who qualifies, who does not, and the mix of user
  segments.
- **Findings**, once the study has run: a Claims table, one row per claim,
  named by what it says.
  - Raw material (recordings, transcripts, session notes) is never copied into
    the repo; it stays where the study keeps it.
  - Name participants by pseudonym (P1, P2) and mask every excerpt: no names,
    contact details, employers or other detail that identifies a person.
  - Every claim has a Source (which session or document) and a Basis (what it
    rests on, such as "observed in 4 of 6 sessions"). The validator rejects a
    claim with no Source.
  - Rate Confidence apart from Direction, mark a claim Verified only once a
    second person has checked it against its source, and record what
    contradicts it and what the study could not establish.

## Role Boundary

Research Plan is not a PRD or Business Case. It defines how the team will
close uncertainty before downstream artifacts commit to scope, pricing,
metrics, or design assumptions, and its optional Findings record what the
study showed. The PRD, ADRs and designs cite those claims; they do not copy
them.

## Completion Criteria
- Questions are bounded and answerable.
- Methods fit the uncertainty level.
- The plan is short enough to execute.
- Success criteria say what decision the evidence will enable.
