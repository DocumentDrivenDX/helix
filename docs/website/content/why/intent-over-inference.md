---
title: "The ‘I’ principle: Intent over inference"
weight: 4
---

> Documented intent governs implementation without being silently redefined by existing code.

An agent working on a task can find examples in the code, assumptions in tests, and suggestions in work items, without knowing whether those sources reflect what the team currently intends. Following an existing implementation can carry an old mistake into new work, while filling gaps with assumptions can introduce features or behavior that the project never required.

HELIX records project intent in documents with defined roles and authority. These documents guide the work, while evidence from implementation can give the team a reason to revise them through an explicit decision.

## Where project intent lives

- **Vision documents** explain why the project exists and the direction it should take.
- **Requirements** define what it must achieve.
- **Specifications** describe expected behavior. 
- **Designs** record how the team intends to build it. 
- **Tests** check the expectations and provide evidence.
- **Code** shows what the software currently does.

Each document answers a different kind of question. An agent choosing how to implement a feature needs the relevant design and specification. In contrast, a question about whether that feature belongs in the project may require returning to the requirements or vision.

The authority hierarchy determines which documents govern when these sources disagree. A design should support the behavior described in its specification, and the specification should satisfy the relevant requirements. A difference in the code provides something to investigate, rather than permission to change those expectations.

## What helps agents follow intent

Several details help an agent distinguish work that the team has agreed on from assumptions that it might otherwise make.

**Purpose and scope** explain what the task should accomplish and where it ends. An agent may identify useful additions while working, but usefulness alone does not make them part of the agreed task. Clear goals and exclusions help it recognize when an idea needs a separate decision.

**Expected behavior** gives the agent a basis for deciding what to implement. Specifications should describe the outcomes the team expects, including conditions that matter to the feature. Where a condition remains unclear, the agent should make that uncertainty visible instead of quietly choosing behavior that later becomes difficult to change.

**Design decisions and constraints** explain choices that the agent needs to respect. An existing approach may reflect a requirement that is difficult to recognize from the code alone, so the agent should understand the reasons behind it before proposing a replacement. Those reasons can also help the team judge whether a constraint still applies.

**Current, consistent documents** reduce the chance that an agent follows an earlier plan. When documents contradict one another, the team needs to resolve the disagreement according to their authority and record any approved change. Choosing whichever version makes implementation easier would leave the underlying conflict unresolved.

## When documents and code disagree

The first step is to identify the difference and the documents that govern it. The agent should explain what the implementation does, what the relevant specification requires, and whether the current task gives it authority to resolve the mismatch.

For example, suppose a specification requires a search to match names regardless of capitalization, while the code only returns exact-case matches. An agent extending the search should flag that difference rather than assume that the current behavior must be intentional. Tests that expect case-sensitive results also need review, since they may preserve the same mistake.

The team may confirm that the specification remains correct and fix the implementation, or discover that an earlier decision changed the intended behavior without updating the documents. Any revision must follow the authority already established for the work, with the affected specifications, tests, and code brought into agreement.

An agent can investigate the problem and propose a resolution without having permission to approve every change that the resolution requires.

## When the documents do not answer the question

Agents still need to make judgments during implementation, particularly about details that the team has left within their authority. The important distinction is whether a choice stays within the agreed behavior or changes what the project is supposed to do.

When a missing answer affects requirements or scope, the agent should describe the question, explain the consequences of the available options, and seek a decision if the choice falls outside its authority. It can record a proposed answer as a proposal, while keeping clear that the team has yet to accept it.

Once the decision is made, the relevant documents should capture it so that later work does not depend on rediscovering the answer in a conversation.

## Relationship to the other HELIX principles

**Human authority balanced with agentic autonomy** determines which decisions an agent may make and when it needs approval. **Evidence over confidence** helps the team establish whether the implementation meets its requirements and whether a proposed change has sufficient support.

**Linked artifacts** connect requirements, specifications, designs, and findings so that people and agents can understand the decisions behind the work. **Execution feedback over fixed plans** allows discoveries during implementation to revise those decisions, with the smallest sufficient change to address what the evidence revealed.

Documented intent can therefore develop as the project learns, while remaining explicit enough for someone joining the work to understand what the team expects, why it changed, and which decisions govern the next task.



