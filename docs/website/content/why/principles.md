---
title: Principles
weight: 1
---

HELIX is a development control system: a framework for keeping AI-assisted
software work coherent at scale. The principles below are the load-bearing
ideas behind that framework.

These are not workflow rules ("write tests first", "review before merging").
Those belong in enforcers. These are the design choices that explain why
HELIX takes the shape it does. When two implementations of the same
workflow could both work, the principles say which one should win.

<!-- vale Helix.PassiveVoice = NO -->
## 1. Planning and execution are intertwined
<!-- vale Helix.PassiveVoice = YES -->

> The framework takes its name from the double helix because the metaphor
> encodes the architecture, not because it sounded good.

Planning and execution are not sequential activities. They happen simultaneously,
at every zoom level, feeding back into each other continuously. A developer
discovers a design flaw during implementation. A review surfaces a missing
requirement. A metric reveals that a feature assumption was wrong. In each
case, the execution strand feeds back into the planning strand, and the
planning strand adjusts what happens next.

This rejection of sequential activities is what makes HELIX different from
waterfall and from the compromise variants of agile. The strands are not
stages. They are simultaneous processes that exist at every layer.

## 2. Documents are the shared context

> Documents are first-class engineering artifacts, not records of work that
> already happened.

Humans and agents both read and write documents. Documents are the durable
layer between them: the shared state that survives sessions, model
upgrades, and team turnover. When a project's institutional knowledge lives
in someone's head, the project loses that knowledge when the person leaves.
When it lives in documents that drive execution, the knowledge compounds.

Every [artifact in HELIX](/artifacts/) has a deliberate role. Vision
documents commit to direction. PRDs commit to requirements. Specs commit
to behaviors. ADRs commit to design choices. Beads commit to
work-in-progress. Together they form a graph that any agent can traverse
when it needs context.

## 3. The artifact authority hierarchy governs reconciliation

> When artifacts at different layers disagree, the higher layer wins.

```
Vision → PRD → Specs → ADRs → Designs → Tests → Plans → Code
```

Source code reflects what exists, not what should exist. If a spec says one
thing and the code says another, the code is wrong, not because code is
unimportant, but because code drifts and specs are deliberate. This single
rule prevents a common failure mode of agentic development: agents that
infer requirements from existing code and propagate implementation accidents
back into specifications.

The authority hierarchy is also how change propagates. A vision shift cascades
downward through every layer. A bug report at the code layer can propagate
up to a spec change and then back down through tests. Either direction
works, but the higher artifact always governs.

## 4. Progressive abstraction is the structure

> Every artifact lives at a specific zoom level. Changes can enter at any
> level and propagate in either direction.

| Layer | Question |
|---|---|
| Vision | What is this and why does it exist? |
| Requirements | What must it do? |
| Specs | What exactly does this feature do? |
| Design | How do we build it? What trade-offs? |
| Tests | How do we know it works? |
| Code | What exists right now? |

The layers are not sequential stages. They are lenses at different zoom
levels, all active simultaneously. The right abstraction for a question
depends on the question: refining a spec is the right move when a feature
is unclear, redesigning a system is the right move when constraints have
shifted, rewriting code is the right move when the spec is correct and the
code is not.

## 5. Human-AI is a continuum, not a binary

> Both humans and AI participate in both strands, at varying ratios per
> task.

There is no clean line where "human work" ends and "AI work" begins. A human
writes a vision. An agent drafts the PRD against it. A human refines. An
agent implements. A human reviews. Every task has a slider, from fully manual
to fully autonomous or anywhere in between, and the right position depends
on the task's stakes and the team's confidence.

This rules out two failure modes. It rules out "AI replaces the human":
no agent automates judgment away. It also rules out
"AI assists but humans do the work that counts"; agents are first-class
participants in the artifact graph, not autocomplete.

<!-- vale Helix.PassiveVoice = NO -->
## 6. Autonomy is supervised, not unbounded
<!-- vale Helix.PassiveVoice = YES -->

> Agents operate inside bounded loops that stop when human judgment is
> needed.

The HELIX methodology layers supervision on top of DDx's bounded execution
loop. DDx provides the queue-drain primitive (`ddx work`): claim a ready
bead, execute it, close it on success. HELIX decides *what* counts as
ready, *which* bead is the highest-impact next move, and *when* to stop
and ask. When forward progress would require authority that is missing,
<!-- vale Helix.PassiveVoice = NO -->
ambiguity that cannot be resolved, or judgment that is genuinely human, the
<!-- vale Helix.PassiveVoice = YES -->
<!-- vale Helix.PassiveVoice = NO -->
loop halts and tells the operator exactly what decision is needed and why.
<!-- vale Helix.PassiveVoice = YES -->

<!-- vale Helix.Hedges = NO -->
Two build-side guards check completion, not just green tests: the
<!-- vale Helix.Hedges = YES -->
[verification exit gate](/use/workflow/#verification-exit-gate) requires
interface-appropriate proof of each acceptance criterion, and the
[evolve-until-converged loop](/use/workflow/#evolve-until-converged)
iterates against specs and concerns until the work converges.

This is what distinguishes HELIX from autonomous agent loops that run until
they crash or burn through a budget. The supervisory pattern is the
operational thesis: agents do work the user has authorized, in shapes the
user can audit, and the user steers by changing tracker state.

## 7. Adversarial review surfaces blind spots

> Different models have different failure modes. Rotate them.

After an agent completes work, a different agent (or the same agent with a
review prompt) examines the result against the artifact hierarchy. Does the
implementation match the spec? Does the spec still align with the PRD? Are
cross-cutting concerns respected? What drift signals are present?

<!-- vale Helix.PassiveVoice = NO -->
Self-review consistently misses the same kinds of errors a model is biased
<!-- vale Helix.PassiveVoice = YES -->
toward producing. Cross-model review breaks that symmetry. Different models
trained on different data with different objectives produce work with
different blind spots, and alternating them catches what a single
perspective never could.

## 8. Least power wins

> The smallest sufficient action is the right action.

When deciding what to do next, HELIX prefers:

- Refining a spec before redesigning a system
- Sharpening an issue before implementing
- Reconciling artifacts before inventing new ones
- Editing existing files before creating new ones
- Reading existing code before writing more

The bias is not toward minimum effort. It is toward minimum disruption.
<!-- vale Helix.PassiveVoice = NO -->
Each layer of HELIX is a place where the system can be repaired or
<!-- vale Helix.PassiveVoice = YES -->
<!-- vale Helix.Hedges = NO -->
extended; the right layer for a given change is usually the smallest one
<!-- vale Helix.Hedges = YES -->
that fully addresses the problem.

---

These eight principles are the *why* of HELIX. The [Use HELIX](/use/)
section describes the *how*: the workflow, the alignment loop, the
recipes. The [Artifacts](/artifacts/) catalog and the
[Concerns](/concerns/) library are how those principles get expressed in
practice.
