---
title: "Plan — DDx-reference runtime-neutrality remediation (2026-05-25)"
slug: plan-2026-05-25-runtime-neutrality
weight: 580
activity: "Design"
source: "02-design/plan-2026-05-25-runtime-neutrality.md"
generated: true
---
# Plan — DDx-reference runtime-neutrality remediation (2026-05-25)

## Context

CONTRACT-003 (post-collapse): DDx is **one of three runtimes** (DDx, Claude Code, Genie). HELIX portable
content must be runtime-neutral — `workflows/` is the canonical path, `.ddx/plugins/helix/workflows/` is only
the DDx *install example* (LEAK-4), and SKILL.md's body must have **zero** `ddx `/`.ddx/` hits (PRD R-4
acceptance test). Audit reality: the leak ledger is wrongly marked clean — 53 `workflows/` files + SKILL.md
hardcode `.ddx/plugins/helix/workflows/`; ~200 `ddx bead`/`ddx work`/`ddx run` command literals sit beside the
neutral "runtime tracker" idiom; SKILL.md has 4 `.ddx/` hits; and the `check-workflow-paths` hook ENFORCES the
leak (forces `.ddx/...`, rejects canonical `workflows/`).

## The litmus (operator) — additive vs assumption

> **Would this instruction still make sense on a runtime where DDx does not exist?**

- **KEEP — purely additive DDx metadata.** The `ddx:` frontmatter blocks (id / depends_on / review hashes) on
  the **109** workflow + doc files are optional extension fields a non-DDx runtime ignores (artifact-schema
  §optional extension fields). They do not change artifact meaning. **Do not strip them.** `docs/install/ddx.md`,
  the boundary contracts (CONTRACT-001/003), and HELIX's own `docs/helix/` governance stay DDx-specific.
- **NEUTRALIZE — content that assumes DDx exists.** Cross-ref paths `.ddx/plugins/helix/...`,
  `ddx bead`/`ddx work`/`ddx run`/`ddx try`/`ddx agent` command literals, and any "we skip X because
  `ddx execute-beads` does it" framing. Replace with **optional, runtime-provided** phrasing — NOT a definite
  "the runtime tracker" (CONTRACT-003 says HELIX must not *require* a queue/tracker/execution loop, codex
  fix 4). Prefer "the current work item", "the runtime-provided work-item source", "the tracker, **if** the
  runtime provides one", "the runtime executes work items". Portable docs specify **the action**, not the
  command; **concrete DDx invocations relocate to `docs/install/ddx.md`** (codex fix 5). Use canonical
  `workflows/` for source-relative cross-refs and `<plugin-root>/workflows/...` for runtime-installed neutral
  refs (codex fix 2).

## Changes

| # | Change | File(s) |
|---|--------|---------|
| N1 | **Invert `check-workflow-paths`**: in shipped `skills/`+`workflows/` content, REJECT **any `.ddx/plugins/helix/` layout leak** (not just `/workflows/`, codex fix 3) and accept canonical `workflows/`. Still allow `ddx:` frontmatter. | `lefthook.yml` |
| N2 | **Sweep path refs** `.ddx/plugins/helix/...` → canonical `workflows/` (source-relative) or `<plugin-root>/workflows/...` (runtime-installed neutral) across `skills/`+`workflows/`. Do NOT touch `ddx:` frontmatter, `docs/`, or `docs/install/ddx.md`. | 53 `workflows/` files + SKILL.md |
| N3 | **Zero SKILL.md's 4 `.ddx/` hits** → canonical `workflows/` or the `<plugin-root>/` neutral form the catalog-resolution already defines. SKILL.md body must pass the CONTRACT-003 zero-ddx acceptance test. | `skills/helix/SKILL.md` |
| N4 | **Neutralize command literals + assumption prose** (`ddx bead`/`ddx work`/`ddx run`/`ddx try`/`ddx agent`; "because ddx does X") → optional runtime-provided idiom (specify the action, not the command). Relocate concrete DDx invocations to `docs/install/ddx.md`. **Scope includes root `workflows/` docs (README/EXECUTION), YAML/`meta.yml` examples, and any shipped bench-harness docs** (codex fix 6). | `workflows/actions/*.md`, `workflows/references/*.md`, `workflows/activities/**`, `workflows/{README,EXECUTION}*`, `meta.yml` examples (~200 refs) |
| N5 | **Update the CONTRACT-003 leak ledger** to reflect reality: reopen LEAK-4 (path leak persisted) + add entries for the hook-enforced leak, the command-ref leak, and the SKILL.md hits; mark them resolved as N1–N4 land; refresh the validation-checklist evidence. | `CONTRACT-003-ddx-adapter-boundary.md` |

## Guardrails (the central invariant)

- **PRESERVE every `ddx:` frontmatter block** (109 files) — additive, ignorable. Keep the block and its
  non-hash fields; **review-hash updates are EXPECTED** for files whose body changes (re-bless via
  `ddx doc stamp`) — that is not stripping the block (codex fix 1). Never delete the `ddx:` block itself.
- Neutralize **behavior/logic/paths/commands only** — never the additive metadata.
- `docs/install/ddx.md` is the designated home for any remaining DDx specifics; the boundary contracts and
  `docs/helix/` governance legitimately reference DDx (HELIX dogfooding its own runtime).

## How we'll validate

**Static scans + doc-stamp consistency are the GATE; the re-bench is regression smoke only (codex fix 7).**
1. **CONTRACT-003 acceptance test (GATE)**: `grep -nE 'ddx |\.ddx/|execute-bead|\[ddx-' skills/helix/SKILL.md` → **0 hits**.
2. **Inverted hook green (GATE)**: no `.ddx/plugins/helix/` layout leak in shipped `skills/`+`workflows/`
   content (excluding `ddx:` frontmatter); canonical `workflows/` accepted.
3. **Additive metadata intact (GATE)**: the 109 `ddx:` frontmatter blocks still present (count unchanged —
   only review hashes may differ on changed docs); `ddx doc stale`/`stamp` still works.
4. **No stray command leaks (GATE)**: `ddx bead/work/run/try/agent` literals removed from portable
   `workflows/` content (allowed only in `docs/install/ddx.md` / boundary docs).
5. **Parallel re-bench (SMOKE, not the gate)**: confirm the now-neutral methodology still drives a good build
   (real UI, verified e2e, AC-traceable, sample-data) and the run transcripts no longer instruct ddx use —
   i.e. neutralization didn't degrade outcomes.
6. Leak ledger reflects reality; validation-checklist boxes are checkable.

## Invariants
- "Would it make sense with no DDx?" is the test for every edit.
- Canonical path is `workflows/`; `.ddx/...` appears only as a DDx example in `docs/install/ddx.md` / contracts.
- Runtime neutrality; no `Skill tool_use`; don't flatten the loop. Re-bless ddx hashes on changed governed docs.
- Codex-review this plan BEFORE and the diff AFTER.
