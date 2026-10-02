---
title: "The ‘L’ principle: Linked artifacts over isolated or ephemeral plans"
weight: 3
---

> Project knowledge should live in connected artifacts that evolve with the code.

When a person or agent takes on a task, they need to understand what the software should do, why it has its current design, and which decisions govern the work. A plan left in a conversation or a document that no longer matches the software can leave those questions unanswered.

HELIX keeps this knowledge in connected artifacts that the team maintains alongside the code. Goals, requirements, architecture, design decisions, and expected behavior remain available in human-readable form, so someone continuing the work can understand the reasoning behind the implementation.

## The artifact graph

The artifact graph consists of the project's documents and other records, together with the links that explain how they relate. These include vision documents, requirements, specifications, architecture decisions, designs, tests, plans, work items, and evidence from implementation and review.

A feature specification might link to the requirement it addresses, the design that explains how it works, and the tests that check its behavior. These relationships give humans and agents a way to find the context behind a task and understand which other parts of the project a change could affect.

For example, an agent investigating a failing test may need to read the specification that defines the expected behavior and the design decision that explains the current approach. Following those connections helps it understand the problem before proposing a fix, while giving a reviewer a way to check the proposal against the same project knowledge.

## What makes the graph useful

The usefulness of the graph depends on what its artifacts explain and how the team maintains them.

**Clear purpose** helps each document answer a particular question. Requirements describe what the software must achieve, specifications explain expected behavior, and design documents record how the team intends to build it and why. Writing these decisions down gives people and agents information that may be difficult to recover from the code alone.

**Useful relationships** connect documents that have a reason to refer to one another. A link should help explain where a decision came from, what depends on it, or which evidence supports it. Connecting every document to every other document would make it harder to identify the relationships that matter.

**Current information** allows the team to rely on the graph when making decisions. When a requirement or design changes, the affected documents need updating so that an agent does not mistake an earlier plan for current instructions. Conflicting records need attention before they can provide reliable guidance.

**Relevant context** keeps each task manageable. An agent working on one feature needs its requirements, constraints, and related decisions, without necessarily needing every document in the repository. HELIX uses artifact relationships, project scope, and document authority to select that information, with links providing a route to further context when the work requires it.

## Keeping documents and code aligned

Maintaining the graph is part of developing the software. When a change affects a documented decision or expected behavior, the team should identify the affected artifacts and update them as part of the work, so that the next task starts with an accurate account of the project.

For example, if a team moves data validation into a shared component, the design document should explain the component's role, while any affected specifications and tests should reflect changes to behavior. An agent working on a related feature can then find the component and understand why it exists before adding similar logic elsewhere.

A disagreement between code and documentation still requires an explicit decision. If the implementation contradicts an agreed requirement, the team may need to fix the code or approve a change to the requirement before updating the related documents. Simply rewriting the specification to match whatever the code currently does would lose the distinction between intended and existing behavior.

The updates should follow the consequences of the change. A small fix that preserves the documented design may leave most artifacts untouched, while a change to shared behavior may require several documents and tests to change together.

## Keeping project knowledge portable

Project knowledge should remain available when a team changes models, agents, trackers, or execution platforms. Keeping requirements, designs, decisions, and their relationships in project artifacts allows that knowledge to survive beyond the tool or conversation in which it originated.

HELIX defines how the artifacts relate and which documents govern the work, while individual runtimes provide commands, queues, and tracker integrations. Moving to another platform may require changes to those integrations, but the team should be able to carry its recorded intent, architecture, and decision history into the new setup.

## Relationship to the other HELIX principles

**Human authority balanced with agentic autonomy** determines what an agent may change and when it needs a decision from the team. Connected documents give the agent the information it needs to work within those boundaries.

**Evidence over confidence** connects completion decisions to the checks and findings that support them. **Intent over inference** governs how the team resolves disagreements between documents and implementation, while **execution feedback over fixed plans** carries discoveries from the work back into the relevant artifacts.

These relationships allow someone returning to the project to understand what the team intended, what it changed, and why it accepted the result, without having to reconstruct that history from scattered conversations or the code alone.


