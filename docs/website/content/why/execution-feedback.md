---
title: "The ‘X’ principle: eXecution feedback over fixed plans"
weight: 5
---

> Planning guides execution, and execution continuously updates the plan.

A plan reflects what the team already knows when it makes a decision. Later, implementation can expose a limitation in a proposed design, testing can uncover a case the specification never addressed, and production use can challenge an assumption behind a requirement. These findings give the team reasons to revisit particular decisions while continuing to use the parts of the plan that still hold.

HELIX keeps planning and execution connected so that new evidence reaches the documents that guide the work. Changes to those documents then shape what humans and agents do next.

## Planning and execution inform each other

The two strands of the HELIX double helix represent this continuing exchange. Requirements, specifications, and designs guide implementation, while implementation, testing, review, and production use provide new information that can change those documents.

Both strands remain active throughout the project. A team can implement one part of a feature while investigating a finding that changes another part of its design, and a review can raise a question about requirements after implementation has begun.

The team can return to a question about goals, behavior, or design whenever the work reveals a reason to do so. Earlier decisions continue to govern until the team explicitly revises them, giving ongoing work a clear basis even while parts of the plan change.

## What execution can reveal

Different findings require attention at different levels of the plan.

**Implementation constraints** may show that a proposed design cannot support the expected behavior. An agent might discover that a component has a limitation the design did not account for, requiring the team to reconsider the approach while preserving the requirement it needs to satisfy.

**Test results** can reveal a defect in the implementation or a gap in the specification. The team needs to establish what the failure means before deciding what to change, since a failing test alone does not establish that the expected behavior is wrong.

**Review findings** may show that a change conflicts with a design decision, overlooks a constraint, or leaves related documents out of date. These findings help the team identify where the work has departed from the plan and whether the implementation or the documented decision needs attention.

**Production behavior** can challenge assumptions that appeared reasonable during planning. How people use a feature, or how the software behaves under actual operating conditions, may give the team a reason to revisit requirements, with the observed behavior providing evidence for that discussion.

## Choosing the smallest sufficient intervention

HELIX responds to feedback at the narrowest level that fully resolves the problem. If the specification remains correct and the implementation contains a defect, the work may only require a code fix and a test that checks it. If the expected behavior is incomplete, the team may need to revise the specification before changing the implementation.

The size of the response should follow what the evidence reveals. A finding that affects one component does not necessarily justify redesigning the whole system, while a problem in a shared design may require changes across several parts of the project.

The intervention must also include the related updates needed to keep the work consistent. A focused design change can still affect specifications, tests, and several implementation files, all of which need attention if they depend on the decision that changed.

Choosing the smallest sufficient intervention means preserving decisions that still hold while addressing the full consequences of the problem. Leaving a known conflict unresolved would give the next task the same unreliable starting point.

## Updating the plan and continuing the work

Suppose a design assumes that a data service will return all the records needed for a report in one request. During testing, an agent discovers that the service returns only part of the result, so the report omits records even though the request succeeds.

The agent can document the finding and propose a design that retrieves the remaining records. If changing the design falls outside its authority, it needs a decision from the team before proceeding with that change. The requirement for a complete report still holds, while the design and implementation need updating to satisfy it.

Once the team agrees on the change, the relevant documents and work instructions should reflect it so that subsequent work follows the revised approach. Checks should then establish whether the report includes the required records, with the results recorded alongside the change.

This gives the team a way to follow the finding through to its resolution: what execution revealed, which decision changed, what work followed, and what evidence shows that the correction addressed the problem.

## Relationship to the other HELIX principles

**Human authority balanced with agentic autonomy** determines which changes an agent may make and when it needs a decision from the team. **Evidence over confidence** provides the basis for deciding whether a plan needs revision and whether the resulting change resolves the issue.

**Linked artifacts** connect the findings, decisions, and affected work, allowing people and agents to follow the changes. **Intent over inference** keeps existing requirements in force until an authorized decision revises them, so that implementation discoveries inform project intent without silently replacing it.

Together, these principles allow plans to develop alongside the software, with each revision grounded in what the team has learned and carried through to the work it affects.



