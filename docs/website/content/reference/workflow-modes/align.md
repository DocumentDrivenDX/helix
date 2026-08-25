---
title: "Align"
slug: align
weight: 40
generated: true
---

Generated from [`skills/helix/SKILL.md`](https://github.com/DocumentDrivenDX/helix/blob/main/skills/helix/SKILL.md), the HELIX skill. Edit the skill, not this page.

Use for reconciliation, traceability audits, drift checks, and artifact content
placement reviews.

1. Start from authority: vision, PRD, features/stories, architecture/ADRs,
   designs, tests, implementation plans, code. The spec stack is the contract;
   code is a projection of it. Traceability is **bidirectional**: every material
   code surface (route/screen/CLI/API/job/migration) traces to a governing
   artifact, and every acceptance criterion traces to an exercising test. Unmapped
   material surfaces and unimplemented criteria are both alignment findings.
2. **Desired-state rule (with intent guard).** Specs describe the **desired**
   future state. Code behind specs → residual work items (beads/tracker), not
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
