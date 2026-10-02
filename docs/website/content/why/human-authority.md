---
title: "The ‘H’ principle: Human authority balanced with agentic autonomy"
weight: 1
---

> Agent autonomy should match the task, while humans define its boundaries.

Some work needs close human involvement, such as when shaping a goal, when mistakes are difficult/expensive to reverse, or when an agent does not yet have enough reliable context to make a sound decision. There’s also work that an agent can carry through with little or no intervention because it is well specified, well understood, and easy to verify.

HELIX treats this variation as a spectrum. Human authority determines the boundaries of the work, while the degree of autonomy inside those boundaries can change from task to task and with time, as the project develops.

## The HELIX spectrum

At one end of the spectrum, an agent waits for human direction before taking meaningful action. A person defines each step, reviews intermediate decisions, and decides when the agent can proceed. At the other end, an agent can complete an authorized task or bounded sequence of tasks independently, including making local decisions, using available tools, verifying its work, and returning the result with supporting evidence. The same agent may have more freedom in one part of a project than in another.

A team might allow an agent to make routine code changes independently while requiring approval before it changes an architectural decision. The same agent might be given broad freedom to investigate a failing test, but a much narrower scope when the investigation points toward changing a requirement. Tasks may also begin with close supervision and move toward greater autonomy once the agent has gathered enough context and demonstrated that the workflow behaves reliably.

## What determines the level of autonomy

Several conditions influence where the slider should sit.

**Task risk** matters because some decisions are inexpensive to reverse while others can affect architecture, security, data, production systems, or customer-facing behavior. A small and reversible implementation change can usually tolerate more autonomous execution than a decision that changes a system boundary or alters an externally visible contract.

**Context quality** matters because autonomy depends on the agent having enough reliable information to act within the project's intent. Clear requirements, current specifications, linked architecture decisions, relevant code, and explicit acceptance criteria allow an agent to operate with greater independence. Missing, contradictory, or outdated context gives the team a
reason to reduce autonomy until those gaps are resolved.

**Confidence in the workflow** matters separately from confidence in the model. A team may have a workflow with strong verification, well-defined escalation conditions, and reliable artifact relationships, which makes delegation safer even when individual model outputs remain fallible. A newer or poorly understood workflow may warrant closer supervision until the team has evidence about how it behaves.

**The consequences of mistakes and missed opportunities** also matter. Reducing autonomy can lower the risk of an incorrect decision, but excessive supervision can introduce delay, interrupt useful execution, and prevent agents from completing work they are capable of handling. HELIX therefore treats both error cost and opportunity cost as part of the decision.

## Human authority defines the boundaries

Humans define the goal, what the agent may change, when it must ask for a decision, and what evidence it must provide before the work is complete. Within those boundaries, the agent can make the decisions necessary to carry out its task.

If the work requires a change outside its authority, the agent should explain the problem, provide the relevant evidence, and ask for a decision. It may propose a way forward, but it must not expand its own permissions in order to continue.

For example, an agent may be authorized to refactor an implementation while preserving a specification, but discovering that the specification itself is incomplete changes the nature of the task. The agent can surface the conflict, gather evidence, and propose a revision, while the authority to accept that change depends on the boundaries established for the work.

This distinction also means that human authority does not require continuous approval. An agent working inside a well-defined scope should be able to make the local decisions necessary to complete the task without repeatedly asking for permission. Requiring approval for every action would remove much of the value of delegation and would make the slider effectively fixed at the human-directed end.

## The balance changes during the work

A task can move between close supervision and independent work as new information appears. An agent might discover during testing that two requirements conflict, prompting the team to resolve the disagreement and update the relevant documents before it continues.

This applies to both planning and execution, the two strands of the HELIX double helix. Humans and agents can contribute to either strand, with their involvement changing according to the work, the risks, and what they learn along the way.

## Relationship to the other HELIX principles

The autonomy slider depends on the rest of the HELIX model.

**Evidence over confidence** provides a basis for deciding whether greater autonomy is producing reliable results. **Linked artifacts** provide the requirements and decisions the agent needs. **Intent over inference** keeps its work aligned with the project's agreed goals. **Execution feedback over fixed plans** allows new evidence from implementation and
production to change both the plan and, when appropriate, the level of supervision. The team can give an agent more independence as the work becomes clearer, or become more involved when a new risk or unresolved decision requires attention.

Together, these principles allow teams to delegate substantial work without treating autonomy as a permanent setting. HELIX makes the degree of autonomy a deliberate project decision that can move as the work, the evidence, and the risk change.
