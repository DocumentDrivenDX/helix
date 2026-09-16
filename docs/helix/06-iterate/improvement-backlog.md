---
ddx:
  id: improvement-backlog
  authoring:
    home: repo
  depends_on:
    - metrics-dashboard
  review:
    self_hash: 952df3e5bbb6e967cd0e3d485ae7106893c464008ecda327e9c0c6a33527e2cd
    deps:
      metrics-dashboard: 486cd18a01712b15850ce7dd808d432a8a52cc56d1db22a8939ed31b633191c0
    reviewed_at: "2026-09-16T03:20:07Z"
---
# Improvement Backlog — HELIX 2026-Q3

**Iteration**: 2026-Q3 (post-`v0.12.0`; the human-outputs branch
`feat/helix-human-outputs`)
**Source Learnings**: the 2026-09-10 top-to-bottom evaluation that produced
the human-outputs plan (`docs/helix/01-frame/prd.md` non-goals and R-4;
`docs/helix/00-discover/product-vision.md` success definition), the first
`present` run (`docs/helix/06-iterate/deliverables/DEL-001-helix-evaluation-deck.md`
Assumptions and gaps), and `docs/helix/06-iterate/metrics-dashboard.md`.

## Prioritization Rules

- Rank by **authority leverage**: items that keep the skill inside the PRD's
  non-goals (content plus one skill, no execution engine, no imposed
  technology) rank above cosmetic improvements.
- Rank by **evidence leverage**: items that make a success metric measurable
  rank above items that add surface.
- Rank by **public-surface impact**: items that make the published
  reference more accurate rank above internal cleanups.
- Items without tracker references stay at the bottom until they are
  filed; the backlog does not retain unsourced ideas.

## Backlog Items

| Priority | Item | Evidence | Tracker Ref | Why Now | Status |
|----------|------|----------|-------------|---------|--------|
| P1 | Build the evaluation the PRD promises: fixed corpus, headless run per host, `validate-instance.py` plus a rubric, results published; retire the 922-file `family-test/` scaffold that does not run | `evals/results/20260915-2202/summary.md`: nine briefs at commit `20315d5c`, 33/36 checks, rubric 57/62, about $32 per full run; `family-test/` removed | this branch | The present mode and the deliverable gate gave the eval something concrete to grade | done |
| P1 | Rasterize `.pptx` renders in the deliverable gate on the authoring host (LibreOffice, or PowerPoint automation permission) | `skills/helix/scripts/deck-qa.py` rasterizes through LibreOffice and writes a contact sheet; DEL-001 Render section records the inspection | this branch | A deck nobody looked at is not finished; the gate says so | done |
| P2 | Sub-agent fan-out in align, review, and converge: one agent per review dimension or artifact family, fan-in through `workflows/modes/_report.md` | `workflows/modes/align.md` Fan-out section; review and converge likewise | this branch | The report shape exists, so fan-in has a contract | done |
| P2 | Read governing artifacts that live in a connector-backed tool (Google Docs, Notion, Jira) directly, instead of only through the checkout stub | `workflows/conventions.md` Reading through a connector; `authoring.connector` in the schema | this branch | Hosts expose document connectors; read-only access removes a manual copy step | done |
| P2 | Consolidate the install index and six host guides (1,946 lines across seven files on `main`) into one guide plus per-host deltas, and test `.github/copilot-instructions.md` against the router | `docs/install/README.md` (886 lines across three files); `tests/validate-install-consistency.sh` keeps the Copilot file a pointer | this branch | The router split changed what every guide must describe | done |
| P2 | Port Sloptimizer's slide target into the deliverable gate: `shape.slop` and `restatement` checks on bullets, labels, captions, and verdicts, kept in sync with the upstream fixture | `skills/helix/scripts/check-deliverable.py`; `tests/validate-headline-sync.sh`; DEL-001 Render, Gate | this branch | The headline port left shapes unchecked; the deck rebuild showed the same slop below the titles | done |
| P2 | Add a healthy-set `align` brief (a fixture with no seeded drift, or `docs/helix/` itself) so the PRD's fewer-than-three-findings target has a reading | `docs/helix/06-iterate/metrics-dashboard.md` alignment row: the only sample is the seeded `recipe-app/baseline` fixture (28 findings) | pending bead | The eval runs; one brief closes the only PRD metric still unmeasured | open |
| P3 | One-pagers, briefs, and HTML: the present mode and the `deliverable` type name three kinds and two render targets, but only decks are built end to end. Gap: no document flow in `deck-flows.yml`, no section patterns in `slide-patterns.yml`, no renderer for `.docx` or HTML (`render-deck.js` produces `.pptx` only), and no kind-aware checks in `check-deliverable.py` beyond deck ordering and length (pattern limits, density, and coverage run with deck assumptions for every kind; no one-pager or brief check exists) | `workflows/modes/present.md` Kinds table and step 7; `workflows/deliverables/deck-flows.yml`; `skills/helix/scripts/render-deck.js`; `skills/helix/scripts/check-deliverable.py` | pending bead | The deck pipeline is in place, so each gap is a bounded addition to a file that exists | open |
| P3 | Prune overlapping catalog types: fold `test-suites` and `test-procedures` into `test-plan`; decide whether `market-analysis` stays separate from `competitive-analysis` | 03-test carries six types; discover carries four market documents | pending bead | The catalog table and graph regenerate cleanly now, so a prune is mechanical | open |
| P3 | Sloptimizer adapter section for the `human-facing` profile | `workflows/voice.yml` `human-facing`; the sloptimizer HELIX adapter hard-codes `artifact-signal` | pending bead (easel repo) | Without it a prose rewrite fights the deck voice | open |
| P3 | Add `ddx.type` to every catalog `example.md` so type resolution never falls back to the directory heuristic | `tests/validate-instance.sh` asserts the heuristic; every example emits a `frontmatter.type` warning | pending bead | Cheap once, removes 53 warnings | open |

## Selection for Next Iteration

- **Chosen item**: P3 — the Sloptimizer adapter section for the
  `human-facing` profile, together with pushing the `headline` target from
  the easel-skills branch so hosts with Sloptimizer installed get the same
  title rules the HELIX gate ports.
- **Why it wins the next slot**: both P1 items closed on this branch; the
  first eval run scored the `present` brief 6/8 on the rubric, and both
  lost points were voice (investor-unfriendly source references, intake
  fields not named), which is what the adapter fixes.

## Review Checklist

- [x] Each item cites evidence
- [x] Tracker references are included (or marked as "pending bead" where
      not yet filed)
- [x] Ordering is deterministic (priority + position within priority)
