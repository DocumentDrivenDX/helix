---
title: "Align"
slug: align
weight: 10
generated: true
---

Generated from [`workflows/modes/align.md`](https://github.com/DocumentDrivenDX/helix/blob/main/workflows/modes/align.md), the mode contract the HELIX skill loads. Edit that file, not this page.

Use for reconciliation, traceability audits, drift checks, and artifact content
placement reviews.

1. Start from authority: vision, PRD, features/stories, architecture/ADRs,
   designs, tests, implementation plans, code. The spec stack is the contract;
   code is a projection of it. Traceability is **bidirectional**: every material
   code surface (route/screen/CLI/API/job/migration) traces to a governing
   artifact, and every acceptance criterion traces to an exercising test. Unmapped
   material surfaces and unimplemented criteria are both alignment findings.
2. **Desired-state rule (with intent guard).** Specs describe the **desired**
   future state. Code behind specs → residual tracker work items, not
   silent requirement shrinks. Code ahead of docs → classify as plan-to-code
   honesty (`STALE_PLAN` / honesty evolve). Evolving specs to match code
   requires **operator intent** (explicit request or approved handoff) — do
   not auto-bless unapproved implementation as plan authority. Code reflects
   state; it does not redefine plan alone.
3. Reconstruct intent from planning artifacts before inspecting lower layers.
4. Classify each gap as `ALIGNED`, `INCOMPLETE`, `DIVERGENT`,
   `UNDERSPECIFIED`, `STALE_PLAN`, or `BLOCKED`.
5. Produce one durable alignment report when the action is more than a
   conversational review. The report must remain reviewable by a human in
   under ten minutes. Prefer the alignment-review template under the catalog
   (`workflows/templates/alignment-review.md` or the package
   `references/templates/` path when present).
6. For every non-aligned gap (`INCOMPLETE`, `UNDERSPECIFIED`, `DIVERGENT`,
   `STALE_PLAN`), the handoff to implementation must name all four of:
   - **Destination artifact type** (e.g. PRD, FEAT, US, ADR, TD, TP) where
     the gap is resolved.
   - **Deliverable shape**: the concrete content to add (e.g. "a TD section
     answering X", "a US covering Y", "an ADR recording the Z choice").
   - **Suggested next workflow mode** (`frame`, `design`, `polish`,
     `validate`, `evolve`, `backfill`) or runtime handoff when execution is
     already governed — never a CLI command.
   - **Evidence references**: artifact paths plus line numbers (or section
     anchors) supporting the finding.
7. Create or identify follow-up work for every non-aligned gap using the
   handoff fields above. **Evidence-gated implement work:** before filing
   build/implement items, require concrete residual evidence (paths, tests,
   commands). Prefer story/AC floor items when only docs/traceability lag.
   "Residual already green" means a governing AC is exercised by a passing
   test (or a recorded exception). Close or re-scope only with that evidence.

## Content migration ledger

If a user asks whether content belongs in the right HELIX document, use align
mode. The alignment output must include a content migration ledger for every
misplaced content unit:

| Field | Required content |
|---|---|
| Source | Artifact path and line references |
| Content unit | Small named chunk of content |
| Classification | `keep`, `move`, `split`, `delete`, `needs-new-artifact`, or `decision-needed` |
| Destination | Exact destination artifact path or artifact type |
| Content to add | Destination-shaped draft content |
| Template fit | Destination section and blocking/warning checks |
| Destination risks | Any template check the proposed addition would fail |
| Follow-up | Tracker issue ID or explicit issue to create |

Do not remove content from one artifact unless the destination content and
follow-up work are captured durably.

Procedure: `workflows/actions/reconcile-alignment.md` (deeper step detail; this file is the contract).
