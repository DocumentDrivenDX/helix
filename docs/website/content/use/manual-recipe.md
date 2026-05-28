---
title: Manual HELIX Recipe
weight: 20
---

Use this recipe when humans are driving the project and agents are helpers, not
queue managers. No DDx tracker, CLI wrapper, or background runtime is required.

## What the runtime must provide

In a manual workflow, the "runtime" can be a person plus a chat session. It must
provide:

- A way to load the current repository and selected HELIX artifacts into the
  agent context.
- A way for humans to approve artifact edits before downstream work begins.
- A visible handoff note for implementers that states scope, authority, and
  acceptance criteria.
- A place to record evidence after implementation, such as a pull request,
  changelog entry, or implementation note.

## Recipe 1: create the first artifact stack

Start with the smallest useful stack:

- Product vision: what the project exists to accomplish.
- PRD: users, problems, non-goals, constraints, and success criteria.
- Feature spec or user story: one bounded outcome to build next.
- Design note: the chosen approach, rejected alternatives, risks, and open
  questions.
- Implementation handoff: allowed files, acceptance criteria, validation, and
  evidence expectations.

Human workflow:

- Copy the closest templates from the artifact-type catalog.
- Fill facts directly; leave unknowns marked as open questions.
- Keep authority clear: vision governs PRD, PRD governs feature specs, feature
  specs govern design, design governs implementation.
- Ask an agent to critique gaps, contradictions, and missing acceptance
  criteria before any code changes.

Prompt:

```text
Read these HELIX artifacts in authority order: product vision, PRD, feature
spec, and design note. Identify contradictions, missing decisions, unclear
acceptance criteria, and implementation risks. Do not edit code. Propose
artifact edits only, and separate facts from assumptions.
```

## Recipe 2: run the first alignment pass

Alignment asks whether downstream artifacts still obey upstream intent.

Human workflow:

- Give the agent the artifact stack in authority order.
- Ask it to compare each downstream artifact against its governing upstream
  artifacts.
- Accept only concrete edits that preserve the authority order.
- Update the artifacts by hand or ask the agent to patch only named files.

Prompt:

```text
Run a HELIX alignment review for this artifact stack. Compare downstream
documents against upstream authority. Return findings with severity, affected
artifact, governing source, and proposed edit. Do not create tasks yet.
```

## Recipe 3: create the first implementation handoff

An implementation handoff converts aligned artifacts into bounded execution.

The handoff should state:

- Governing artifacts and the exact sections that matter.
- Allowed write scope.
- Files or areas that are out of scope.
- Acceptance criteria.
- Required validation or evidence.
- How to record follow-up work.

Prompt:

```text
Create an implementation handoff from these aligned HELIX artifacts. The handoff
must include governing sources, allowed write scope, explicit non-goals,
acceptance criteria, validation expectations, and follow-up capture rules. Do
not implement yet.
```

Implementation prompt:

```text
Implement this handoff only. Read the named governing artifacts, change only the
allowed files, do not broaden scope, and report evidence against each acceptance
criterion. If you discover unrelated work, record it as follow-up instead of
implementing it.
```
