# Decision Brief Generation Prompt

Frame one decision in one context, compare the options against that context
on cited evidence, and recommend, so a reviewer can check the argument before
the decision is made. The brief is advisory.

## Storage Location

Store at: `docs/helix/02-design/decision-brief-DB-{number}-{decision-name}.md`,
or the path the flow's graph profile sets for this type (`locations:`).

## Purpose

Answers: **Given this context, which option do we recommend, why, on what
conditions, and what would change the answer?** It sits before an ADR. It is
the argument; the ADR is the record of what was decided.

## Role Boundary

A [[component-profile]] (reusable or contextual) records what is known about
one component; the brief uses it as evidence and does not restate it. An ADR
records a decision once taken; a brief recommends before one is. The brief
never overrides requirements, approved decisions, or concerns: it names them
as bounds in Context and reasons within them. If the recommendation
conflicts with an approved decision, say so as a risk and route it to the
owner; do not argue the decision away inside the brief.

## Method

1. **Frame the decision.** One decision, one context, one decider. If two
   choices can vary independently (what to build on, where to run it), write
   two briefs or two clearly separate sections.
2. **Collect the bounds.** From the project's requirements, approved ADRs, and
   [[concerns]], list what narrows the choice. Cite each by id or path.
3. **List the options,** including the status quo and any option a reviewer
   will ask "why not?" about.
4. **Gather evidence.** Cite technology briefs and component profiles by
   pinned revision. Evidence from outside the project is advisory; it informs
   the evaluation and does not set a requirement.
5. **Evaluate every option on the same criteria,** drawn from the bounds. A
   cell with no evidence says Unknown.
6. **Recommend.** One option for this context, its conditions, why it beats
   the strongest alternative, and what would change it.
7. **Record risks and unknowns** with a route. An owner, date, or figure
   appears only if a project artifact states it.
8. **Pin the evidence** before publishing: every reference carries the revision
   it was read at.

## Writing for the reviewer

The reader is a reviewer, often outside the team, who will check the argument
not the author. Plain words, claims in the sentence, citations after. State
the recommendation first in Recommendation, not in a closing paragraph, and
say what would change it. Do not inflate a conditional recommendation into a
certainty.

## Inputs

- Requirements, approved ADRs, concerns, and principles that bound the choice
- Technology briefs and component profiles for each option
- The current state, for the status quo option
