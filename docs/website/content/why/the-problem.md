---
title: The Problem
weight: 2
---

Three approaches dominate how teams think about software delivery. Each one
fails in a specific way once AI agents become first-class participants in
the work.

## Waterfall over-plans

> *Plan completely. Then execute.*

Waterfall assumed a team could plan a system end-to-end before writing
code. In practice, requirements change, designs prove infeasible, and the
gap between plan and reality grows until the plan is fiction. Teams either
ignore the plan or spend more time updating it than building.

Waterfall fails because **planning and execution are not separable**. Real
information about a system surfaces during construction. A plan written
without that information is a hypothesis, not a contract.

## Agile under-plans

> *Execute. Plan as you go.*

Agile, in many of its real-world implementations, swung the other way.
Sprints and standups replaced design documents. The plan moved into
people's heads — what we're building, why this trade-off, what we tried
last time and why it didn't work. Stand-up notes captured fragments;
nothing captured the whole.

This works while the team is small and continuous. It breaks down at scale
or across turnover. When a senior engineer leaves, the institutional
knowledge of a feature leaves with them. When an AI agent joins the team,
it has no head to inherit context from — and the agile failure mode
becomes acute.

Agile fails because **documents are not optional infrastructure**. They
are how knowledge survives the people who produced it.

## Vibe coding skips planning entirely

> *Just tell the agent what to build.*

The newest failure mode is the most seductive: skip planning, point an
agent at a problem, and iterate on its output. This works for small,
self-contained tasks where the entire context fits in one prompt.

It breaks down as codebases grow. Agents loop without progress because
they keep re-deriving requirements from the existing code. Specs drift
from code, and code drifts from intent, until nobody — human or agent —
knows which is authoritative. The human becomes a full-time dispatcher,
re-explaining the same context to every new agent session.

Vibe coding fails because **agents need durable context, not fresh
prompts**. Without it, every session is a cold start.

## HELIX is not a compromise

A natural reading of the three failures suggests a compromise: plan a
little, execute a little, repeat. This is the framing most "agile-plus"
methodologies adopt — and they inherit a softer version of all three
failure modes.

HELIX is a different model entirely. It says:

- **Plan and execute simultaneously**, at multiple levels of abstraction.
- **Use documents as the shared context layer** between humans and agents.
- **Bound the autonomous loop with explicit human decision points.**

Each of these is a structural commitment, not a process tweak. Together
they describe a development control system where AI agents do real work
without losing coherence, and humans steer without becoming dispatchers.

The next page — [The Thesis](/why/the-thesis) — describes how that
control system is shaped, and why the result deserves a name distinct
from what came before.
