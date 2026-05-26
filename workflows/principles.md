---
ddx:
  id: helix.workflow.principles
  depends_on:
    - helix.workflow
  review:
    self_hash: 2a9c7544929c1d7cf2707b447723a5d17261cd52ca1a6dfabcb3b22f9ae6b0f4
    deps:
      helix.workflow: 1b6caaf3ebc6950bc4fff314e09bc0ee1b71deaa9223a4a70a13f399291ad98c
    reviewed_at: "2026-05-26T17:17:30Z"
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

## Size Guidance

A principles document longer than ~12 items is likely a policy document, not a
decision guide. At 8 items, consider whether all of them change decisions. At
12, consider consolidating. At 15 or more, prune to the principles that
actually changed your last five decisions.
