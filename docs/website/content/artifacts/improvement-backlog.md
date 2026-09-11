---
title: "Improvement Backlog — HELIX 2026-Q3"
slug: improvement-backlog
weight: 490
activity: "Iterate"
source: "06-iterate/improvement-backlog.md"
generated: true
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

> **Source identity** (from `06-iterate/improvement-backlog.md`):

```yaml
ddx:
  id: improvement-backlog
  authoring:
    home: repo
  depends_on:
    - metrics-dashboard
  review:
    self_hash: 93bc23d6894a3f1b6bf89ff43a0d200421e332c1b40ab8d4ec1b94ff1256f1b4
    deps:
      metrics-dashboard: 0934ca6e0913a5da11bb822adb4b4a5e343aaefdf6444af11690eab218a52c6c
    reviewed_at: "2026-05-15T04:11:24Z"
```

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
| P1 | Build the evaluation the PRD promises: fixed corpus, headless run per host, `validate-instance.py` plus a rubric, results published; retire the 922-file `family-test/` scaffold that does not run | PRD success metrics "alignment quality" and "authoring quality" have no measurement path; `docs/archive/helix/02-design/bench-build-results-2026-06-06-first-run.md` says a full run is "structurally unbuildable" | pending bead | The present mode and the deliverable gate now give the eval something concrete to grade | open |
| P1 | Rasterize `.pptx` renders in the deliverable gate on the authoring host (LibreOffice, or PowerPoint automation permission) | DEL-001 Render section: the `.pptx` passed structural validation but no one has looked at its slides | pending bead | A deck nobody looked at is not finished; the gate says so | open |
| P2 | Sub-agent fan-out in align, review, and converge: one agent per review dimension or artifact family, fan-in through `workflows/modes/_report.md` | `workflows/actions/reconcile-alignment.md` STEP 3 has eight review dimensions run single-threaded; PRD success criterion "alignment plan reviewable in under 10 minutes" | pending bead | The report shape now exists, so fan-in has a contract | open |
| P2 | Read governing artifacts that live in a connector-backed tool (Google Docs, Notion, Jira) directly, instead of only through the checkout stub | `workflows/conventions.md` Authoring Home: `external-tool` documents are read only as check-in copies | pending bead | Hosts now expose document connectors; read-only access removes a manual copy step | open |
| P2 | Consolidate the six install guides (1,946 lines) into one guide plus per-host deltas, and test `.github/copilot-instructions.md` against the router | `docs/install/*.md` line counts; `copilot-instructions.md` is a fourth normative surface no test compares | pending bead | The router split changed what every guide must describe | open |
| P3 | Prune overlapping catalog types: fold `test-suites` and `test-procedures` into `test-plan`; decide whether `market-analysis` stays separate from `competitive-analysis` | 03-test carries six types; discover carries four market documents | pending bead | The catalog table and graph regenerate cleanly now, so a prune is mechanical | open |
| P3 | Sloptimizer adapter section for the `human-facing` profile | `workflows/voice.yml` `human-facing`; the sloptimizer HELIX adapter hard-codes `artifact-signal` | pending bead (easel repo) | Without it a prose rewrite fights the deck voice | open |
| P3 | Add `ddx.type` to every catalog `example.md` so type resolution never falls back to the directory heuristic | `tests/validate-instance.sh` asserts the heuristic; every example emits a `frontmatter.type` warning | pending bead | Cheap once, removes 53 warnings | open |

## Selection for Next Iteration

- **Chosen item**: P1 — build the evaluation. It is the only item that
  turns two PRD success metrics from prose into numbers, and it decides
  whether the router split and the present mode moved anything.
- **Why it wins the next slot**: highest evidence leverage; the deliverable
  gate, the executable validator, and the report shape were the
  prerequisites, and all three shipped on this branch.

## Review Checklist

- [x] Each item cites evidence
- [x] Tracker references are included (or marked as "pending bead" where
      not yet filed)
- [x] Ordering is deterministic (priority + position within priority)
