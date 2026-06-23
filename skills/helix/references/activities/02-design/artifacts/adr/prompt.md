# Architecture Decision Record (ADR) Generation Prompt

Write a compact ADR that captures one architecture-significant decision, the
alternatives, and the consequences.

## Storage Location

Store at: `docs/helix/02-design/adr/ADR-NNN-<decision-name>.md` — **one decision
per file**. Naming is canonical and checkable: uppercase `ADR`, a **zero-padded
3-digit** sequential number, then a kebab-case decision name (e.g.
`ADR-001-modular-monolith.md`, `ADR-007-auth-tenant-isolation.md`). Do **not** use
lowercase `adr-` or 4-digit numbers, and do **not** lump multiple decisions into
one record. reconcile-alignment flags non-canonical names and lumped ADRs.

## Purpose

An ADR is the **single-decision record** for architecture-significant choices.
Its unique job is to preserve why a decision was made, what alternatives were
considered, what tradeoffs were accepted, and when the decision should be
revisited.

ADRs are not architecture documents. Architecture owns the overall structural
model. ADRs are not solution designs or technical designs; those apply accepted
decisions to narrower scopes. ADRs are not meeting notes; keep only the context
that changes how future readers should evaluate the decision.

## Reference Anchors

Use these local resource summaries as grounding:

- `docs/resources/adr-github-organization.md` grounds ADRs as
  single-decision records with rationale, tradeoffs, and consequences.
- `docs/resources/google-cloud-architecture-decision-records.md` grounds ADR
  traceability to architecture evolution, code, and infrastructure context.

## Focus
- State the context and decision plainly.
- Keep alternatives and tradeoffs honest but brief.
- Note validation and references only if they affect the decision.
- Use one ADR per decision. If the decision has independent parts, split it.
- Treat accepted ADRs as history. New decisions supersede old records instead
  of rewriting them.
- **Do not accept a decision whose design-defining facts are assumed.** A
  decision's design-defining facts (API shape, data model, pricing/cost
  semantics, security/permissions, operational guarantees, or work decomposition)
  must be **evidenced** — by an operator statement, a governing artifact, an
  existing implementation, a docs/API proof, or a completed spike — not by model
  familiarity, and not because a mechanism was picked or a provider named.
  Choosing a provider and deferring its live integration does **not** evidence the
  decision. If a design-defining fact is assumed, the ADR must cite **spike
  evidence**, record a **blocked-spike rationale**, or carry an explicit
  **provisional-risk** note (what is assumed, what could invalidate it, and that
  the assumption is reversible/non-blocking). See the anti-reframe check in
  `workflows/references/concern-resolution.md` (step 3a). An operator-marked
  "spike/unknown" may not be accepted as a settled ADR without **spike evidence, a
  blocked-spike rationale, or an explicit provisional-risk note**. A
  **business/product** unknown a technical spike can't answer (e.g. a pricing
  model) → record **guidance-needed** or a blocked spike rather than forcing a
  technical spike or accepting an assumed decision.

## Boundary Test

| If you are writing... | Put it in... |
|---|---|
| Overall system structure or deployment topology | Architecture |
| One architecture-significant decision and rationale | ADR |
| Feature-specific design applying accepted architecture | Solution Design |
| Story-level component or code plan | Technical Design |
| API schema, event payload, or file format | Contract |
| Work steps or sequencing | Implementation Plan |

## Completion Criteria
- The decision is unambiguous.
- Alternatives are compared clearly.
- Consequences are explicit.
- Status and supersession state are clear.
- Reconsideration triggers are concrete when the decision has uncertainty.
