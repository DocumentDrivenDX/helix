---
title: "TP-014 Appendix A: Real-World Intent Patterns From Session Logs"
slug: TP-014-appendix-real-world-patterns
weight: 880
activity: "Test"
source: "03-test/test-plans/TP-014-appendix-real-world-patterns.md"
generated: true
collection: test-plans
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

> **Source identity** (from `03-test/test-plans/TP-014-appendix-real-world-patterns.md`):

```yaml
ddx:
  id: TP-014-A
  depends_on:
    - TP-014
    - FEAT-013
  status: draft
```

# TP-014 Appendix A: Real-World Intent Patterns From Session Logs

**Status:** Draft (appendix; not yet folded into TP-014)
**Depends on:** TP-014, `skills/helix/SKILL.md` (§Routing, §Workflow Contracts)
**Purpose:** Replace invented prompt shapes in TP-014's scenarios with the
prompt shapes the maintainer actually issues, derived from Claude Code and
OpenAI Codex CLI session transcripts on disk.

## 1. Source and methodology

**Claude Code** — `~/.claude/projects/-home-erik-Projects-helix/*.jsonl`.
All three on-disk sessions: `2f92aad5` (18 prompts), `18d1ccc5` (11),
`e777b993` (4). **33 prompts / 3 sessions.**

**Codex CLI** — `~/.codex/sessions/2026/<MM>/<DD>/rollout-*.jsonl`. Four
conversational sessions: `2026-05-11T16-06` (125), `2026-04-29T22-47`
(77), `2026-04-20T11-13` (33), `2026-03-07T20-10` (29). **264 prompts /
4 sessions.** Three other large rollouts (51 MB / 33 MB / 4 MB) were
worker-only (≤2 user prompts) and discarded.

**Extraction:** `jq` on each runtime's `user`-role records, filtering
AGENTS.md preambles, `<environment_context>`, `<subagent_notification>`,
`<task-notification>`, slash-command stubs, and tool-result arrays.
Claude Code prompts live at `.message.content` (string); Codex prompts
live at `.payload.content[].text` where `item.type=="input_text"`.

**Caveat:** Codex sessions were authored against DDx / Fizeau / Axon
(not HELIX itself); Claude Code sessions were on this repo. Most prompts
predate HELIX adoption — mined for **what users actually ask**, not for
HELIX traces.

## 2. Pattern catalog

The 297 prompts roll up into 14 pattern groups keyed to HELIX modes.
Frequency is approximate. "HELIX engaged?" reports whether the recorded
session actually invoked a HELIX workflow.

| # | Category | Freq | Example real prompt (paraphrased only for length) | HELIX engaged? | Expected mode + contract | Test-case shape |
|---|---|---|---|---|---|---|
| 1 | `input` (sparse intent) | ~38 / 13% | `"Work the queue."`; `"Check the outstanding work — we added a bunch of code to improve the beads interface. Review it."`; `"What's the status of the project? In particular, the microsite?"` | No | §Input — clarify only when unsafe; identify governing artifacts; produce planning work, not implementation | Given `"Work the queue."` against empty `docs/helix/`, expect mode `input`, no files written, response names missing governing artifact and routes to `frame` |
| 2 | `frame` (vision/PRD/feat/US) | ~12 / 4% | `"Do we have a user story for 'when I create a database, I can also create a collection in it'?"`; `"Make sure to bring the specs fully up to date with the solution."` | No | §Frame — read existing Frame; load template + prompt; validate blocking checks | Given a FEAT with no story for collection-create, expect a new `US-*.md` with `depends_on: [helix.feat-*]` and template-conformant sections |
| 3 | `design` (ADR/TD) | ~27 / 9% | `"Thoroughly design this approach and capture it as beads."`; `"Make a comprehensive plan to effect this rename across the codebase."`; `"Focus on research and planning first."` | No | §Design — load governing artifacts; draft + self-critique; derive ordered work | Given an authorized PRD-named change, expect new TD/ADR + ≥1 work item naming exact files, commands, checks, observable state |
| 4 | `evolve` (thread a change) | ~24 / 8% | `"We're renaming 'phases' to activities. Make a comprehensive plan."`; `"Drop the named providers, they will cause us problems."`; `"reframe this request completely in terms of vale and make it dependent on it."` | Once (`/helix-evolve`) | §Evolve — walk graph both ways; updates from the highest-authority artifact down; surface conflicts via §Align handoff | Extends TP-014 Scenario 3 — add `change-request-rename.txt` modeling vocabulary-rename evolve, distinct from substitution |
| 5 | `align` (reconciliation) | ~21 / 7% | `"Did we finish the fizeau rename? Is it pushed? Did we rename the repo? Did we push a release?"`; `"Check the specs on disk, there should have been major changes to TD-026."` | No | §Align — authority-first; classify gaps; produce findings with destination + deliverable + suggested mode + path:line evidence | Given drift-injected ADR ≠ TD, expect alignment report with ≥1 `DIVERGENT` finding citing path:line, next mode `evolve` |
| 6 | `review` (fresh-eyes) | ~47 / 16% | `"Review this plan with fresh eyes."`; `"Re-review the plan, particularly taking into account necessary frame and design artifact changes."`; `"Check for new beads — there's a new one about the prose handler. Review it with fresh eyes."` | Occasionally | §Review — scope narrow; findings first; severity-ordered; follow-ups for MEDIUM+ | TP-014 Scenario 6 plus a `"Review this plan with fresh eyes"` variant (no scope hint) — runtime must scope from open diff/work |
| 7 | `polish` (work-item refine) | ~15 / 5% | `"All the beads should be broken down to the minimal scope possible as a dependency graph."`; `"Split it up and review again with claude, particularly noting the need for granular and atomic tasks."` | No | §Polish — multi-pass; require execution-ready (files, commands, checks, observable state); route back if unsharpenable | Given 3 beads with mixed AC quality, expect vague beads either edited to satisfy step-3 or flagged not-ready with destination + mode; well-formed bead untouched |
| 8 | `check`/`next` (status) | ~33 / 11% | `"What's left?"`; `"Is there more work in the queue?"`; `"What remaining work is there regarding auto-routing/fiz integration?"`; `"How's the queue?"` | No | §Check And Next — inspect queue + governing artifacts; conservative pick; never dispatch silently; use §Align handoff for gaps | Given 4 beads (2 ready, 1 in-progress, 1 blocked-on-missing-ADR), expect response names ready + in-progress + blocker + next mode `design`, **no** CLI invocation |
| 9 | `build`/`run` (execute now) | ~31 / 10% | `"do it"`; `"Start a worker."`; `"Loop over this work. Pick up each bead in order…"`; `"Apply the fixes."` | No | §Build And Run — one bounded pass / bounded operator loop; stay in named work; verify gate | Given one execution-ready bead + complete HELIX, `"do it"` claims, edits named files only, runs named gate, closes bead. Negative twin: `"do it"` with no bead → refuse |
| 10 | `commit`/`release` | ~28 / 9% | `"commit and push"`; `"commit, push and tag a release."`; `"tag an alpha build and install ddx"`; `"Do the release."` | Rarely | §Commit / §Release — separate scope; gate; preserve execution history (no squash/rebase/amend on bead branches) | Given dirty worktree mixing bead + unrelated changes, expect bead-scoped commit naming `[ddx-<id>]`; unrelated changes uncommitted or separate; pre-push gate passes |
| 11 | `validate` (one artifact) | ~6 / 2% | `"It seems like a lot of the helix artifacts are missing prompts? Why?"`; `"Check the specs on disk, does TD-026 look right?"` | No | §Validate — load instance + template/prompt/meta; structural + prompt-section conformance; Align taxonomy | Given a TD with 2 missing required sections, expect both named by exact heading + classified `INCOMPLETE`; template path cited |
| 12 | `backfill` (reconstruct) | ~3 / 1% | `"Review the beads queue. Which are necessary for us to make the next minor release?"` (reconstructs implicit release scope) | No | §Backfill — separate confirmed vs inferred; mark uncertainty; follow-up work for gaps | Given code + tests + no `02-design/`, expect new TD with `[confirmed]`/`[inferred]` markers and an uncertainty list naming missing evidence |
| 13 | Negative (should refuse) | ~14 / 5% | `"Just start coding."`; `"Add a feature spec that requires MongoDB"` (vs ADR-001 SQLite); `"do it"` (no plan in prior turn); `"What is this BS?"` (cleanup invite); `"wtf are you claiming blockers"` (escalation) | **No, runtime improvised** | §Operating Discipline — don't silently implement planning/alignment/review; use `check` when unclear | Covered by TP-014 7a/7b/7c; see §5 for extensions |
| 14 | Out-of-scope (no HELIX) | ~28 / 9% | `"pull and install"`; `"Use gpt-5.4-mini."`; `"Manually unblock that bead."`; `"Stop the worker."` | N/A | None — must **not** match | Routing returns "no match"; no file under `docs/helix/` is written; runtime falls back to direct tool dispatch |

## 3. Patterns not covered by TP-014's existing scenarios

Map onto existing scenarios: `input` → 1, 7c; `frame` → 1, 2; `design` →
2, 5; `evolve` → 3; `align` → 3 tail; `polish` → 5; `review` → 6;
`build`/`run` → 7a (refusal).

Observed patterns **not** covered, with proposed extensions:

1. **`check` / `next` positive case** (~11%). TP-014 fires `check` only
   in 7a refusal. **Proposed Scenario 5b:** status query against
   populated queue — response names next-ready + in-progress + blocked
   + §Align handoff for unblockers; no CLI command.
2. **`commit` / `release`** (~9%). Modes declared but never exercised.
   **Proposed Scenario 8:** dirty worktree with mixed bead + unrelated
   changes — assert scope separation, bead-id traceability, pre-push
   gate.
3. **`validate`** (~2%) — distinct from `align`. **Proposed
   Scenario 2-variant:** single-artifact validation against
   template/prompt/meta triple, with `INCOMPLETE` keyed to template
   sections.
4. **`backfill`** (~1%) omitted. **Proposed Scenario 9:** TD from code
   + tests, with `[confirmed]`/`[inferred]` markers and uncertainty list.
5. **Negative match** (~9% out-of-scope). **Proposed Scenario 7d:**
   assert HELIX does **not** match on `"pull and install"`,
   `"Use gpt-5.4-mini"`, etc.

## 4. Most frequent intents to prioritize

Ranked by observed frequency. TP-014's implementation sequencing
(§10) should align with this.

| Rank | Pattern | ~Count | ~% | TP-014 home |
|---|---|---|---|---|
| 1 | `review` (fresh-eyes) | 47 | 16% | Scenario 6 |
| 2 | `input` (sparse intent) | 38 | 13% | Scenarios 1, 7c |
| 3 | `check` / `next` (status) | 33 | 11% | **New: Scenario 5b** |
| 4 | `build` / `run` (execute now) | 31 | 10% | Scenario 7a (negative); positive case missing |
| 5 | `commit` / `release` | 28 | 9% | **New: Scenario 8** |

TP-014's current sequencing (1 → 7a → 6 → 3 → 2/4/5 → 7b/7c) is right at
scenario-level. **Per-scenario fixtures** should match this ranking:
Scenario 6 needs ≥3 prompt variants (no-scope, named-scope, post-change)
because `review` is by far the most common single shape. Add 5b and 8
before 7b/7c refinements.

## 5. Negative-path observations — runtime improvised when HELIX should have refused

Real cases mirroring TP-014 7a/7b/7c where the runtime did **not** refuse.

**Case A — `"do it"` without a plan.** Prior assistant turn surfaced
three branches and asked the user to choose; user replied `"do it"`;
runtime silently picked branch one. HELIX expected: route `check`, name
the selected branch verbatim or ask one focused question. **TP-014 7a
extension:** add a sub-scenario where the prior turn offered ≥2
alternatives.

**Case B — cleanup invitation.** `"What is this BS? Obviously not going to scale too well: <paste>"`. Runtime patched code. HELIX expected:
route `evolve` / `align` — the complaint is about design, paste is
evidence for re-scoping. **TP-014 7b extension:** scope/scaling complaint
plus paste; assert routing to `evolve` and naming the upstream artifact.

**Case C — operator-attention escalation.** `"wtf are you claiming blockers, you were supposed to create a complete plan"`. Runtime retried
without diagnosis. HELIX expected: `align` surfaces the blocker by
artifact:line, then `evolve` revises the plan. **TP-014 7b/7c extension:**
user pushes back on a reported blocker; assert alignment finding, not a
retry.

**Case D — `check` improvising design.** `"What's the situation with 'blocked no-changes'. Is that because it's unneeded work?"`. Runtime
answered descriptively **and** proposed a design change in the same turn.
HELIX expected: `check` returns status + §Align handoff; design changes
belong to a follow-up turn. **Scenario 5b (proposed) covers this.**

## 6. Open questions for maintainer judgment

1. **`review` vs `align` boundary.** `"Make sure these transitions are properly specified in the state machine"` could route either way.
   Does `align` win for "is X consistent" framing, or does `review` win
   when a specific artifact is named?
2. **Single-word affirmations (`"yes"`, `"do it"`).** Route at all, or
   inherit the prior assistant turn's mode? Suggest: inherit; do not
   re-route.
3. **Sub-agent dispatch prompts** (`"Use sub-agents to review every bead closed in the last 5 days"`) blend `review` + `polish` + operator
   directives. Suggest: HELIX returns the mode; runtime owns dispatch.
4. **`"How's the queue?"` heartbeats** appeared >10× in one session.
   Should each trigger a fresh `check` artifact, or degrade to a cheap
   status read? The skill should at least not write a fresh durable
   artifact each time.
5. **Codex `<turn_aborted>` recovery.** Restated identical prompts after
   interrupts (`"Ok schedule this all out"` ×3). Assert HELIX routing is
   idempotent for identical prompts.
6. **AGENTS.md residue.** Both runtimes inject preambles before the
   first user prompt. Assert routing is unchanged with and without the
   preamble — HELIX must not be biased by AGENTS.md content.

**End of appendix.** Fold into TP-014 when adopting the proposed
extensions (5b, 7d, 8, 9) and reweighting §10 per the §4 frequency
ranking.
