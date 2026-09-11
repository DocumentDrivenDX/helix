---
ddx:
  id: helix.workflow.principles
  authoring:
    home: repo
  depends_on:
    - helix.workflow
  review:
    self_hash: 2a9c7544929c1d7cf2707b447723a5d17261cd52ca1a6dfabcb3b22f9ae6b0f4
    deps:
      helix.workflow: 24bc127a783c568be4813f8a7665c82abc04056dd94718eda32a51fa9191b543
    reviewed_at: "2026-06-14T03:20:37Z"
---
# HELIX Design Principles

## Purpose

These principles guide judgment calls during design, implementation, and review.
They are defaults — a project should override them with its own principles file
at `docs/helix/01-frame/principles.md`. When no project file exists, HELIX loads
these defaults.

Principles guide decisions; they are not workflow rules. Process enforcement
belongs in activity enforcers and ratchets.

## Principles

### Spec Is The Contract

The governing artifact stack (vision → PRD → features → stories/ACs → ADRs/design)
is the contract and the source of truth; code is a **projection** of it. Two
consequences: (1) cross-implementation comparison and reproduction start from the
**spec**, not the code surface — equivalence is spec equivalence. (2) Traceability
is **bidirectional** — every material code surface traces to a governing artifact
(no code outside spec), and every acceptance criterion traces to an exercising
test (no spec without implementation). Code that outran its spec and a spec that
outran its code are both drift. Keep the spec current *with* the code in the same
change, not best-effort afterward — best-effort spec evolution is not reproducible.

### Design for Change

Build for modification, not perfection. Prefer structures that are easy to
replace or extend over structures that are clever but rigid. When a design
choice makes future changes harder, that cost should be explicit and justified.

### Design for Simplicity

Start with the minimal structure that could work. Additional components,
layers, or abstractions require documented justification. Complexity that
serves no current requirement is waste — remove it.

### Validate Your Work

Decisions should be testable. If you cannot describe how you would know whether
a design choice is working, the choice is not complete. Prefer designs that
surface their own health.

### Make Intent Explicit

Code, configs, and documents should say what they mean. Avoid implicit
conventions, magic values, and behavior that depends on undocumented ordering.
When intent is ambiguous, name it.

### Prefer Reversible Decisions

When two options are otherwise equivalent, choose the one that is easier to
undo. Commit to irreversible choices deliberately, with documented rationale.
Reversibility buys options; irreversibility spends them.

### Deliverable Over Machinery

Ship the product unit (vision/PRD capability, user-visible slice, or — when the
product is methodology — the template/skill/prompt that changes behavior).
Process machinery is a derivative: bound it, freeze it, deliver. Deferred rigor
is a tracker item or parking-lot line, not a redesign tranche. Prefer checks
that catch real defects; kill work that only deepens process. Do not use this
principle to skip tests, product ACs, claims-vs-reality, or scope-discipline.
When process rounds outrun delivered units, stop and deliver.

### Layers Are the Control

The artifact hierarchy is not a filing order; it is how automated work is
controlled. Each layer governs the one beneath it (vision governs
requirements, requirements govern designs, designs govern tests, tests govern
code), concerns propagate practices down through every layer, gates sit
between activities, and floors never slide back. An agent may act only
within what the layers above it authorize, and a change enters at the
highest layer it affects and flows down. When a rule needs enforcing,
put it in a layer, not in a prompt.

### Humans Decide, Agents Draft

The two strands of the helix share one loop with different jobs. People
own intent, judgment, and approval: what to build, which decision stands,
whether work is done. Agents own throughput: drafting, checking,
surfacing, and recording. The hand-off points are explicit and governed,
never implied: the autonomy level sets how often an agent pauses, stop
triggers name what it must never do unasked, approval turns a draft into
authority, and a refusal or an escalation returns judgment to a person.
A workflow that lets an agent settle a question only a human can answer,
or that makes a human do work an agent can check, has the strands crossed.

## Tension Resolution

These principles can conflict. When they do, apply the principle whose
violation would cause the worse outcome in context. Document the tension
in the commit message or design note so future reviewers understand the
trade-off.

Common tensions:

- **Simplicity vs. Validate Your Work**: the simplest design may not expose
  good observability. Prefer validation unless the observability cost is
  genuinely disproportionate.
- **Design for Change vs. Simplicity**: extensibility points add structure.
  Add them only when the change direction is known; do not extend for
  hypothetical futures.
- **Deliverable Over Machinery vs. Validate Your Work**: keep real evidence
  gates (build, test, claims-vs-reality); do not invent gates for completeness
  theater.
- **Deliverable Over Machinery vs. Spec Is The Contract**: product specs stay
  authoritative; freeze process meta-work mid-delivery, not required product
  ACs for the ship unit.

## Size Guidance

A principles document longer than ~12 items is likely a policy document, not a
decision guide. At 8 items, consider whether all of them change decisions. At
12, consider consolidating. At 15 or more, prune to the principles that
actually changed your last five decisions.
