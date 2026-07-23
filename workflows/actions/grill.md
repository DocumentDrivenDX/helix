# HELIX Action: Grill

You are running a **grill** session: a relentless, single-question interview
that walks a **decision tree** until the operator and the agent share the same
understanding of a plan, design, or change.

This action distills Matt Pocock's grilling technique into the HELIX workflow.
It is **not** a second public skill. Normative rules also live in
`skills/helix/SKILL.md` §Grill so marketplace installs without
`references/actions/` still work.

## Goal

Surface and resolve open decisions **before** frame/design/evolve/polish
mutations and **before** implement beads. Do not build until the operator
confirms shared understanding.

## Non-goals

- Replacing `align`, `review`, or `converge`.
- Creating a free-floating `CONTEXT.md` as a second authority.
- Filing implement/build beads during the interview.
- Editing product source code during the interview.
- Overriding the operator's declared autonomy level (only the confirm gate is a hard floor).

## Inputs

- Scope: plan, design, PRD, FEAT, change request, or free-form intent.
- Autonomy: resolved per HELIX (does not change which activities run).
- Interactive channel: present (TUI/chat) or absent (headless/`-p`/`codex exec`/`ddx agent run`).

## Hard floor (all autonomy levels)

Until the operator **explicitly confirms** shared understanding:

1. **Do not** Write/Edit product source code.
2. **Do not** file implement/build tracker items.
3. **Do not** run apply/deploy/merge actions.
4. **Do not** mass-rewrite PRD/FEAT/ADR/TD as a substitute for the interview.

This floor is a `stop_at`-style checkpoint: it survives `autonomous` and
`aggressive`. It does **not** rewrite autonomy source precedence (per-prompt
override still controls pause density for non-floor actions).

After confirm, follow the §Align handoff into the next HELIX mode; those modes
own catalog authoring under normal HELIX rules.

## Interactive procedure

1. Engage HELIX (dual-path) and bind marker + catalog before any mutation.
2. Load governing artifacts for scope (vision, PRD, features, ADRs, designs as
   present). Explore the codebase for **facts**.
3. Build a **decision tree** of open choices (dependencies between decisions).
   Prefer few, high-leverage nodes over a laundry list of clarifications.
4. Ask **one question at a time**. Wait for the operator's answer before the
   next. Multiple questions in one turn is a contract violation.
5. For each question, include:
   - the decision (what is being chosen),
   - a **recommended answer**,
   - a short rationale with evidence (artifact path:line or code path when known).
6. **Facts** → look up in the environment; do not ask the operator.
   **Decisions** → put to the operator and wait.
7. Track resolved decisions in the conversation. Prefer routing durable capture
   to existing catalog types **after** confirm (not a parallel grill-log
   authority).
8. When the tree is resolved (or residual decisions are explicitly parked),
   ask the operator to confirm **shared understanding**.
9. On confirm, emit a §Align handoff with all four fields:
   - **Destination artifact type** (PRD, FEAT, US, ADR, TD, TP, concerns, …)
   - **Deliverable shape** (concrete content to add)
   - **Suggested next mode**: `frame` | `design` | `evolve` | `polish` |
     `validate` | `backfill` | runtime handoff when already governed
   - **Evidence references** (paths + line numbers or grill answer anchors)
10. Stop. Do not silently enter frame/design/build in the same turn unless the
    operator asks.

## Headless / non-interactive procedure

When there is no interactive answer channel (`claude -p`, `codex exec`,
`ddx agent run`, CI, Grok one-shot, etc.):

1. Still engage, bind catalog, load artifacts, explore facts.
2. Emit in **one response**:
   - the decision tree (nodes + dependencies),
   - recommended answer per open node with rationale/evidence,
   - recorded assumptions for unresolved operator-only decisions,
   - a complete §Align four-field handoff (or multiple handoffs if needed).
3. Do **not** block waiting for answers.
4. Do **not** Write product code or file implement beads in that run.
5. Operator applies answers in a later interactive turn or explicitly authorizes
   the next HELIX mode.

## Autonomy spectrum note

| Situation | Behavior |
|-----------|----------|
| Interactive + any autonomy | One question at a time; confirm gate before act |
| `autonomous` / `aggressive` interactive | May propose denser recommended trees, still one Q, still confirm gate |
| Headless | One-shot tree + recommendations + assumptions + handoff |
| Explicit operator "act now / skip grill" | Honor; route to appropriate mode with recorded skip |

## Decision → destination map (after confirm)

| Decision kind | Typical destination type | Typical next mode |
|---------------|--------------------------|-------------------|
| Product scope / non-goals | PRD / FEAT | `frame` or `evolve` |
| Hard-to-reverse technical trade-off | ADR | `design` |
| Story-level approach | technical-design / solution-design | `design` |
| Term / concern filler | concerns | `frame` |
| Residual implementation | beads via polish/runtime | `polish` or runtime handoff |
| Missing tests / AC | test-plan / story | `frame` or `validate` |

Glossary terms go into **concerns** (or an existing in-stack glossary), never a
standalone `CONTEXT.md` as governing authority.

## Exit criteria

- Operator confirmed shared understanding **or** headless one-shot completed.
- Four-field handoff emitted.
- No implement beads filed; no product code mutated by this action.
