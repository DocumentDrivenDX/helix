# Grill

Use to stress-test a plan, design, or change via a decision-tree interview
until shared understanding. Distills the grilling technique (one question at a
time, recommended answers, facts vs decisions). Full procedure:
`workflows/actions/grill.md` in source checkouts; this section is normative for
all installs.

**Why a mode (not only `input`):** grill is stop-before-act interview discipline;
`input` converts intent into governed work items. Operators must be able to
invoke interview-only without drafting PRDs or filing implementation work.

1. Bind marker and catalog; load governing artifacts; explore the environment
   for **facts**.
2. Build a decision tree of open choices (dependency-ordered), not a bulk
   questionnaire.
3. **Interactive:** ask **one question at a time**; wait for the answer. Each
   question includes a **recommended answer** and short rationale (cite
   path:line when known). Decisions go to the operator; facts are looked up.
4. **Headless / non-interactive** (a runtime's headless dispatch, CI,
   one-shot): emit in one response the full decision tree, recommended
   answers, assumptions for unresolved operator-only decisions, and the
   §Align handoff. Do **not** block waiting for answers.
5. **Hard floor (all autonomy levels):** until the operator confirms shared
   understanding (interactive) or the headless one-shot completes, do **not**
   Write/Edit product source, file implementation work items, or apply/deploy.
   This is a `stop_at`-style checkpoint; it does not rewrite autonomy source
   precedence for other pauses.
6. Do **not** create a free-floating `CONTEXT.md` as authority. After confirm,
   durable decisions land via handoff into existing catalog types (PRD, FEAT,
   ADR, technical-design, concerns, etc.).
7. On confirm (or headless completion), emit a §Align handoff with all four
   fields: destination artifact type, deliverable shape, next mode
   (`frame` | `design` | `evolve` | `polish` | `validate` | `backfill` | runtime
   handoff when already governed), evidence references.
8. Do not silently start frame/design/build in the same turn unless the
   operator asks.

Procedure: `workflows/actions/grill.md` (deeper step detail; this file is the contract).
