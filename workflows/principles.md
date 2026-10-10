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

The governing artifacts define the desired system. Code implements that intent;
it cannot silently redefine it. A specification is valid before implementation
exists. An accepted decision means the direction is chosen, not delivered.
Compare implementation with selected requirements when assessing delivery or
running an explicit audit. Record implementation gaps in the runtime tracker,
not as status fields in the specification.

Keep operative requirements and useful rationale in living documents. Source
control owns delivery history: HELIX documents contain no pull-request numbers,
repository revision identifiers, or citations to implementation history.

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

Complete the requested deliverable, which may itself be a specification. Use
process only to resolve relevant uncertainty or prevent a concrete error. Read
the target and the authorities that affect it; expand scope only for a relevant
dependency or conflict. Stop when the requested result is coherent and verified.
Do not turn every finding into a gate or every edit into an audit. Keep tests
and evidence appropriate to the claims being made. Ground agent estimates in
observed token spending; more tokens, documents, or review rounds are not
progress. Follow the spending and update rules in
`workflows/references/work-item-first.md`.

### Layers Are the Control

Vision governs requirements; requirements govern designs and verification.
Resolve conflicting intent at the highest affected authority. Update affected
documents when a decision changes, without traversing unrelated branches of the
artifact graph. The hierarchy establishes meaning, not a mandatory sequence of
ceremonies.

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
