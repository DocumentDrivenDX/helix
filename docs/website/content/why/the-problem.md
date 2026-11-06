---
title: The Problem
weight: 2
---

When AI agents start doing substantial engineering work, they begin exposing weaknesses in prevalent software development practices such as Waterfall, Agile, and now Vibe coding that teams could previously work around.

HELIX addresses this by starting from the problem: how do you preserve intent, context, human authority, and evidence as work moves between people, agents, planning, and execution?

## Waterfall separates planning from execution

> *Plan completely. Then execute.*

Waterfall assumes you can know enough in advance to define the system before implementation begins.

This is challenging because software hardly behaves that neatly in real life. The team actually learns things by building. Requirements that looked straightforward may create unexpected constraints later; designs may prove impractical when someone tries to implement them; some technical assumptions may prove completely wrong later.

When planning and execution are treated as separate phases, these challenges create a growing distance between the original plan and the system being built. Teams can then either continue following a plan that no longer reflects reality, or repeatedly stop to rewrite it.

Turns out you cannot solve the problem with better planning itself, as it stems from treating a plan as though execution has nothing useful to teach it.

In HELIX, planning and execution remain connected. Implementing can change a design, expose a missing requirement, challenge an assumption, or show that the original plan needs revision. Those changes flow back into the project artifacts rather than remaining only in someone's head.

## Agile can leave too much knowledge undocumented

> *Execute. Plan as you go.*

Agile addressed many of the problems created by heavy upfront planning, but some implementations went too far in the opposite direction.

Design decisions moved into conversations and requirements were distributed across tickets, stand-ups, chat threads, and people's memories. Teams could still work effectively because the people involved shared enough context to understand what was meant.

But all that changes when the context itself needs to travel; when someone leaves, for example, the project's memory may leave with them. A new engineer may see what the code does without knowing why the team designed it that way.

AI agents bring this problem to the spotlight because they can’t simply join the team to inherit institutional memory. They need project knowledge in a form they can actually access and use.

This is why documents are at the heart of HELIX, but not as mere paperwork. Requirements, specifications, design decisions, tests, and other artifacts together provide a durable record of what the team is trying to achieve, how important decisions were made, and what the system is expected to do.

The artifacts also need to stay connected and up to date, as a collection of documents that contradict one another cannot be useful context for either a human or an agent.

## Vibe coding makes every session start again

> *Tell the agent what you want and iterate from there.*

For small, self-contained tasks, prompt-based development can work remarkably well. The goal fits into a prompt, the code is easy to inspect, and a person can quickly judge whether the result is acceptable.

Problems arise when the task at hand depends on knowledge that does not fit comfortably into that interaction at all. For instance, an agent working in a larger codebase may need to understand why an interface behaves a particular way, which requirement takes precedence, what constraints must not be violated, what previous approaches have already failed, and which decisions require human approval.

Without that context, the agent has to infer. It may derive requirements from existing code (even if it is wrong). The agent may make a locally sensible change that conflicts with a broader design decision. It may waste time and resources by repeatedly rediscovering information that another agent session had already learned.

The human must then restore the missing context every single time: explaining the goal again, pointing out constraints again, correcting the same assumptions again, and deciding whether they can trust the result.

You cannot expect to overcome these limitations with a different model because it’s the project itself that has failed to retain enough usable knowledge for the next piece of work.

HELIX addresses this by treating project context as something that should persist beyond an individual prompt or agent session.

- Intent belongs in explicit artifacts.
- Relationships between those artifacts help determine which context matters.
- When implementation reveals something new, that knowledge can be carried back into the project rather than disappearing when the session ends.

## The common problem with all three is loss of continuity

On the surface, it may appear that waterfall, poorly documented Agile, and prompt-driven development fail in different ways, but they share a deeper problem.

Something important gets disconnected in each approach:

- Planning becomes disconnected from what execution teaches us.
- Project knowledge gets disconnected from the people or agents who need it.
- Implementation becomes disconnected from documented intent.
- Autonomy gets disconnected from clear human authority.
- Completion becomes disconnected from evidence that the work is actually correct.

AI agents amplify each of these gaps as they can act quickly and at greater scale, with an incorrect assumption that once affected a few lines of code now shaping an entire sequence of changes (before a human even looks at the result).

The situation will not improve with simply more planning, more documentation, or more supervision. Each of those can become wasteful if applied without regard to the work being done.

What matters is keeping the important parts of the development process connected.

## HELIX treats those connections as part of the system

HELIX is built around five principles:

- **Human authority balanced with agentic autonomy:** agents can take on more work when the task, context, risk, and available evidence support it, while humans still define the boundaries.
- **Evidence over confidence:** accept work because it has been checked instead of because an agent sounds certain that it is complete.
- **Linked artifacts over isolated or ephemeral plans:** project knowledge lives in connected artifacts that remain available to humans and agents over time.
- **Intent over inference:** documented intent governs the work rather than leaving agents to reconstruct requirements from whatever the code currently happens to do.
- **eXecution feedback over fixed plans:** implementation, testing, review, and operation continuously feed what they reveal back into planning.

These principles are meant to work together.

- A requirement gives an agent intent.
- A design provides context.
- Human authority defines what the agent may decide for itself.
- Execution produces new information.
- Tests and review provide evidence.

When something changes, the relevant artifacts change with it. In this new development process, agents can do meaningful engineering work without forcing humans to become full-time dispatchers, and humans can retain authority without having to supervise every individual action.

The next page, [The Thesis](https://github.com/DocumentDrivenDX/helix/blob/main/why/the-thesis), describes how HELIX turns these ideas into a development control system.
