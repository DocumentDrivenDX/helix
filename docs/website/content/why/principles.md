---
title: Principles
weight: 1
---

The five HELIX principles below serve as core decision-making guidelines for software teams when defining goals, delegating tasks to AI agents, verifying work, and adapting to real-world feedback.

These principles are far from sequential, nor do they prescribe local workflow practices. They are intended to help teams choose between approaches that may both appear reasonable but lead to different outcomes. Each principle has a dedicated page that explains its meaning, consequences, and trade-offs. 

## The HELIX manifesto 

> **H**uman authority balanced with agentic autonomy 
> **E**vidence over confidence 
> **L**inked artifacts over isolated or ephemeral plans
> **I**ntent over inference 
> e**X**ecution feedback over fixed plans 

HELIX balances human authority with agentic autonomy. The remaining principles express priorities rather than absolute exclusions. Confidence, individual documents, inference, and plans remain useful, but they should not replace validation, connected context, explicit intent, or feedback from execution.

## H: Human authority balanced with agentic autonomy

> Agent autonomy should match the task, while humans define its boundaries.

HELIX treats human involvement and agent autonomy as a spectrum rather than a fixed division of work. At one end, the agent does nothing without human direction. At the other, it can complete an authorized task or sequence of tasks independently. Most work sits somewhere between these two points.

Teams can move the level of autonomy up or down depending on the task's risk, the quality of the available context, their confidence in the workflow, and the consequences of getting the decision wrong or missing an opportunity.

Human authority defines the boundaries of that autonomy. Humans define the goal, decide what the agent is authorized to do, identify decisions that require escalation, and determine what evidence the agent must return. Within those boundaries, an agent can work independently without asking for approval at every step. 

The balance can also change as work moves between planning and execution. Humans may take the lead when defining intent or resolving ambiguity, while agents may take the lead during well-defined implementation or verification work. New evidence can change that balance again. In the double-helix model, human and agent participation can vary throughout the project according to what the work requires.

[Read the full principle](human-authority/).

## E: Evidence over confidence

> Confidence in quality comes from validation instead of how certain an agent sounds.

LLMs can produce answers that are persuasive and expressed with high confidence even when they are wrong, incomplete, or inconsistent with the project's intent. HELIX therefore separates an agent's confidence in its own output from confidence in the quality of the work. 

Work is complete only when there is evidence that it satisfies the commitments recorded in the artifact graph. Generating an output, changing the requested files, compiling the code, or passing a narrow set of tests may be part of that evidence, but none is sufficient by itself in every case. 

The right evidence depends on the task and its acceptance criteria. It may include automated test results, static-analysis findings, interface-level checks, observability data, or documented findings from human or agent review. A separate review prompt or another model can help produce that evidence.

Verification must check both whether the result works and whether it remains aligned with authoritative artifacts. An implementation can function correctly and still be incomplete if it contradicts a specification, ignores a selected concern, or leaves related documents out of date. 

HELIX builds quality confidence from evidence rather than relying on hallucinated confidence from the system that produced the work. 

[Read the full principle](evidence-over-confidence/).

## L: Linked artifacts over isolated or ephemeral plans

> Project knowledge should live in connected artifacts that evolve with the code.

HELIX treats documentation as part of the working system rather than a temporary planning layer that becomes obsolete once implementation begins. Goals, requirements, architecture, design decisions, constraints, and expected behavior should be recorded in human-readable form and updated as the software changes.

These artifacts form a graph. Vision documents, requirements, specifications, architecture decisions, designs, tests, plans, work items, and implementation evidence link to one another so that humans and agents can understand where a decision came from, what depends on it, and what else may need to change when that decision changes.

The artifact graph must evolve with the code. If implementation changes while the governing artifacts remain static, those artifacts stop providing reliable context. HELIX therefore treats keeping code and its governing artifacts aligned as part of the development process rather than as documentation work to do later. 

Linked artifacts also make context easier to select. An agent does not need every document in the repository for every task. Artifact relationships, flow scopes, domain lanes, and authority rules help it find the relevant context without treating the entire project as one large prompt.

Because this knowledge lives in the artifact graph rather than inside a specific model, agent, tracker, or runtime, it remains portable. Teams can change tools or execution platforms without rebuilding the project's intent, architecture, and decision history around a new system. HELIX defines the artifact relationships and authority rules; individual runtimes supply their own commands, queues, and tracker integrations.

[Read the full principle](linked-artifacts/).

## I: Intent over inference

> Documented intent governs implementation without being silently redefined by existing code.

Agents often infer requirements from the code, tests, work items, and documents nearest to the task. Those inferences can help uncover missing information without replacing explicit project intent.

HELIX organizes artifacts by abstraction and authority: 

- **Vision documents** explain why the project exists. 
- **Requirements** define what it must achieve.
- **Specifications** describe expected behavior. 
- **Designs** record how the team intends to build it. 
- **Tests** provide evidence.
- **Code** shows what currently exists.


When artifacts disagree, the team must identify and reconcile the conflict. Evidence from implementation may justify revising a requirement or specification, but the team must make that change explicitly and update the affected artifacts. An agent must not treat existing behavior as intended behavior merely because the code already implements it.

[Read the full principle](intent-over-inference/).

## X: eXecution feedback over fixed plans

> Planning guides execution, and execution continuously updates the plan.

HELIX treats planning and execution as connected strands rather than separate stages. Requirements, specifications, and designs shape implementation, while implementation, testing, review, and production use generate new evidence about whether those plans still hold. 

That evidence flows back to the appropriate planning layer. 

- A constraint discovered during implementation may require a design change. 
- A failed acceptance test may reveal an incomplete specification. 
- Production behavior may challenge an assumption in the requirements. 

HELIX responds to this feedback with the smallest sufficient intervention. New evidence should change only what needs to change: fix the implementation when the specification is still correct, revise the specification when the expected behavior was incomplete, or revisit a higher-level decision when the evidence shows that the underlying assumption no longer holds. 

Plans remain useful because they guide execution. They remain current because execution can challenge and revise them as the project learns.

[Read the full principle](execution-feedback/).

## How the principles work together

- **L**inked artifacts preserve the project's shared knowledge, evolve with the code, and keep that knowledge portable across tools and runtimes.
- **I**ntent governs implementation and guides how the team reconciles disagreements between artifacts. Evidence can justify revising that intent, but the change must be explicit.
- **H**uman authority defines the boundaries within which agent autonomy can vary. The balance changes with the task, its risks, and the available evidence.
- **E**vidence establishes whether the work satisfies the project's commitments. Confidence in quality comes from validation rather than an agent's assurance that the work is complete.
- e**X**ecution feedback carries what the team learns back into plans and artifacts. HELIX responds with the smallest sufficient intervention, updating the affected artifacts and implementation without unnecessary disruption.

The [Use HELIX](/use/) section translates these principles into workflows, alignment loops, and adoption guidance. The [Artifact Types](/artifact-types/) catalog defines the documents that carry project intent, while the [Concerns](/concerns/) library applies standards and constraints across the artifact graph.



---

