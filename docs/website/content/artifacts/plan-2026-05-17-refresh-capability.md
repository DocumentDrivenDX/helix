---
title: "Plan: §Refresh as a first-class HELIX skill behavior"
slug: plan-2026-05-17-refresh-capability
weight: 530
activity: "Design"
source: "02-design/plan-2026-05-17-refresh-capability.md"
generated: true
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

> **Source identity** (from `02-design/plan-2026-05-17-refresh-capability.md`):

```yaml
ddx:
  id: plan.refresh-capability
  status: draft
```

# Plan: §Refresh as a first-class HELIX skill behavior

**Date:** 2026-05-17
**Status:** Draft v4, awaiting maintainer sign-off
**Source:** the batch self-validation work performed by seven parallel
sub-agents I dispatched by hand against `docs/helix/` on 2026-05-17.
That capability is currently latent — it exists as my session behavior,
not as anything an operator can invoke through the skill.

**Revision note (v2):** v1 leaked git and DDx assumptions into the
methodology contract (per-instance commits, DDx-worker dispatch,
catalog-refresh mode). Stripped. §Refresh is now strictly methodology:
**what** to do across an instance set. How the runtime persists the
results (commits, notebook saves, PR drafts, in-memory output) is the
runtime's concern, not HELIX's.

**Revision note (v3):** v2 invented "skip entries" as new vocabulary
around an alleged §Validate output that doesn't exist in the current
contract. Removed. The plan now sharpens §Validate first (item 6
clarifies that fix-mode degrades to audit-mode per finding when a
finding can't be auto-fixed), then defines §Refresh as a straight batch
over the sharpened §Validate. The "summary" is just the union of
§Validate's existing §Align handoff entries.

**Revision note (v4):** independent Codex review surfaced three real
issues v3 papered over:
- §Validate's classification list (`ALIGNED`/`INCOMPLETE`/`UNDERSPECIFIED`/`STALE`)
  doesn't match §Align's (`ALIGNED`/`INCOMPLETE`/`DIVERGENT`/`UNDERSPECIFIED`/`STALE_PLAN`/`BLOCKED`).
  Reusing "§Align handoff fields" without unifying the taxonomy creates
  ambiguous findings.
- The skill defines §Catalog Resolution (where to find templates) but
  has no equivalent for *project root resolution* (where to find
  operator instance trees). §Refresh assumes it.
- The boundary between "fix in place" and "file follow-up work" is
  unclear: §Align mandates work-item creation; non-DDx runtimes have
  no tracker. §Refresh needs to say which side it falls on.

v4 promotes the three to first-class prerequisites and adds a Known
Limitations section for the uneven-fan-out concern (deferred).

## Goal

Codify "walk every artifact instance under a project HELIX tree,
validate each against the canonical template + prompt, apply mechanical
fixes in place, and surface human-judgement gaps" as a first-class HELIX
workflow mode that any runtime supporting the umbrella skill can invoke.

Acceptance: an operator on any of the five supported runtimes can say
"refresh HELIX" and the skill executes the same methodology — only the
persistence mechanism (commit per file, notebook save, single PR, chat
report) varies by runtime.

## What §Validate already covers and what §Refresh adds

| Need | Today (§Validate) | Gap (§Refresh fills) |
|---|---|---|
| Validate one instance against template + prompt | yes | — |
| Fix-in-place vs report-only at the *invocation* level | yes | — |
| Classification taxonomy | yes, but inconsistent with §Align (see Prerequisite P1) | — |
| Per-finding degrade inside fix-mode | no — only at invocation level | Prerequisite P2 |
| Project-root discovery for batch operations | no | Prerequisite P3 |
| Enumerate every instance under a project tree | no | **adds** |
| Aggregate findings into one report | no | **adds** |
| Tell runtimes which axis to fan out on (when they can) | no | **adds** |

§Refresh is §Validate applied N times with enumeration, fan-out, and
aggregation around it. It does not redefine §Validate's per-instance
behavior — but it requires three small SKILL.md changes first.

## Prerequisite P1: Unify §Validate and §Align taxonomy

Today the two contracts disagree on the classification set:

| Source | Taxonomy |
|---|---|
| §Align item 3 (SKILL.md:117) | `ALIGNED`, `INCOMPLETE`, `DIVERGENT`, `UNDERSPECIFIED`, `STALE_PLAN`, `BLOCKED` |
| §Validate item 5 (SKILL.md:151) | `ALIGNED`, `INCOMPLETE`, `UNDERSPECIFIED`, `STALE` (and explicitly claims "using the Align taxonomy") |

The mismatch is unintentional — §Validate says it inherits §Align's
taxonomy but lists a subset that uses `STALE` where §Align uses
`STALE_PLAN`, and omits `DIVERGENT` and `BLOCKED`.

Unification: §Validate adopts §Align's taxonomy verbatim. `STALE`
becomes `STALE_PLAN`. `DIVERGENT` (instance contradicts current
template intent) is added. `BLOCKED` is added but used sparingly —
§Validate per-instance work is rarely blocked by external dependencies,
but a `BLOCKED` classification covers cases where the template/prompt
itself is unparseable or missing from the catalog.

Existing instances classified as `STALE` in prior reports are
historically equivalent to `STALE_PLAN` under the unified taxonomy;
no data migration required.

## Prerequisite P2: Sharpen §Validate item 6 (per-finding degrade)

Today §Validate item 6 reads:

> Produce updates: when the user invoked validate to fix, apply the
> edits in place; when they invoked it to audit, surface a plan using
> the §Align gap-to-implementation handoff fields.

Binary at the *invocation* level — operator picks fix-mode or
audit-mode and gets one or the other for the whole instance. Silent on
findings that can't be mechanically fixed inside a fix-mode run.

Sharpening to:

> Produce updates: when the user invoked validate to fix, apply edits
> in place for every finding the template + prompt comparison can
> resolve mechanically — typically `INCOMPLETE` findings (missing
> required sections, stale frontmatter shape, renamed headings). For
> findings classified as `DIVERGENT`, `UNDERSPECIFIED`, `STALE_PLAN`,
> or `BLOCKED` — which need human judgement — surface a §Align gap-to-
> implementation handoff for that specific finding instead of editing.
> When the user invoked validate to audit, surface a §Align handoff
> for every non-`ALIGNED` finding regardless of mechanical
> resolvability.

References P1's unified taxonomy. The classification-to-action mapping
becomes explicit: `INCOMPLETE` → auto-fix; everything else non-aligned
→ handoff.

## Prerequisite P3: Add §Project Root Resolution

§Catalog Resolution defines where the skill finds canonical templates
and prompts (inside the skill bundle or vendored plugin). It does not
define where the skill finds the *operator's instance tree* — the
collection of artifact instances under the operator's working
directory. §Refresh and any future batch operation needs this.

Proposed new top-level section, parallel to §Catalog Resolution:

```markdown
## Project Root Resolution

When a workflow mode needs to enumerate artifact instances within the
operator's project (used by §Refresh and similar batch operations),
resolve the project HELIX root in this order:

1. Explicit path provided by the operator at invocation
   (e.g., `refresh docs/helix/`).
2. Runtime-supplied project-config value when present
   (`helix_root` in DDx project config; equivalent in other runtimes).
3. Convention: `docs/helix/` under the runtime's working directory,
   with sub-directories `00-discover`, `01-frame`, …, `06-iterate`.

If none of the three resolves to a directory containing the expected
activity sub-directories, surface a setup gap rather than improvising.
Batch operations on chat-only runtimes (Databricks Genie Code, GitHub
Copilot) require step 1 — the operator names the root in the prompt.
```

Sits alongside §Catalog Resolution at the same heading level.

## Proposed §Refresh contract

Insert in `skills/helix/SKILL.md` between §Validate and §Evolve:

```markdown
### Refresh

Use to bring every artifact instance under a project HELIX tree up to
date with the current canonical templates and prompts. §Refresh is
§Validate (fix-mode) applied across a whole project in one pass.

1. Resolve the project HELIX root per §Project Root Resolution.
   Enumerate every artifact instance under it. Group instances by
   activity directory (00-discover, 01-frame, …, 06-iterate). Skip
   anything that isn't an artifact instance (READMEs, plan
   sub-directories, generated files).
2. For each instance, run §Validate in fix-mode. When the runtime
   supports sub-agent dispatch, parallelise across the activity groups
   (one agent per activity); otherwise execute the groups in activity
   order.
3. Aggregate the per-instance §Validate outputs into a single report:
   per-classification counts using the unified taxonomy (`ALIGNED` /
   `INCOMPLETE` / `DIVERGENT` / `UNDERSPECIFIED` / `STALE_PLAN` /
   `BLOCKED`) plus the union of every §Align gap-to-implementation
   handoff §Validate produced.
4. §Refresh surfaces handoffs in the report. It does **not** itself
   file work items — that responsibility stays with the runtime: DDx
   runtimes may file beads in response, Claude Code runtimes may emit
   tracker issues, chat-only runtimes may simply display the report.
   This keeps §Refresh runtime-neutral while preserving §Align's
   tracker-mutation rules for runtimes that have a tracker.
5. §Refresh is read-only against templates and prompts in the skill
   catalog. If §Refresh reveals that a template itself needs to change,
   route through `evolve` against the catalog separately.
```

Routing-table row, between `validate` and `evolve`:

```markdown
| Bring every artifact instance up to date with the current templates and prompts | refresh |
```

## What's deliberately not in the contract

| Concept | Why it's excluded |
|---|---|
| Commits, commit-message prefixes | Git is a runtime/project concern. Databricks Genie doesn't have git; in-memory chat surfaces don't persist at all. Telling §Refresh to emit commits would make it Claude-Code/DDx-shaped and unrunnable elsewhere. |
| DDx workers, bead drainage | Workers are a DDx execution model. Other runtimes don't have them. §Refresh defines the methodology; whether DDx breaks a §Refresh into beads and drains them across days, or Claude Code runs it in one session, is a runtime decision. |
| Refreshing the catalog itself | The catalog is the source of truth §Refresh validates *against*. Self-referential refresh has no fixpoint. Catalog change routes through `evolve` against the skill repo, governed by upstream release. |
| Per-runtime persistence shape (one PR vs many commits vs notebook saves) | Same reason as commits — runtime concern. The skill's job is "produce N fixes plus one summary"; the runtime decides how to materialise them. |
| Filing work items in response to handoffs | The handoffs in the §Refresh report are inputs to §Align's tracker-mutation rules. §Refresh stays neutral; the runtime applies tracker rules. |

## Per-runtime fan-out

The skill names the parallelism axis ("one agent per activity directory").
Each runtime supplies the executor — or runs sequentially if it has none.

| Runtime | Fan-out mechanism | Behavior |
|---|---|---|
| DDx | `ddx agent run --harness <name>` per activity | Parallel across 7 activities |
| Claude Code | `Agent` tool (`subagent_type` per activity) | Parallel across 7 activities |
| Codex CLI | `codex agent` sub-runs | Parallel across 7 activities |
| Databricks Genie Code | none | Sequential, activity order |
| GitHub Copilot | none | Sequential, activity order |

This table sits in the install docs (per runtime), not in the SKILL body,
because it describes runtime mechanics rather than HELIX methodology.

## Known limitations (accepted)

- **Uneven work distribution across activities.** `01-frame` owns 16
  artifact types; `04-build` owns 1. "One agent per activity"
  parallelism gives long-tail behavior on real instance trees. A
  finer-grained axis (one agent per artifact type, or per N instances)
  would balance better but adds dispatch complexity. **Deferred** — v1
  ships with activity-level fan-out and the long-tail is acceptable for
  the project sizes we currently support. Re-evaluate if a real project
  shows §Refresh runs dominated by `01-frame` wall time.

## Test fixture

A synthetic doc tree under `tests/refresh/fixture/` containing one
instance per activity with one known drift each. The harness runs
§Refresh against the fixture and diffs against `tests/refresh/expected/`:

- `00-discover/product-vision-missing-checklist.md` — template requires
  `## Review Checklist`; fixture omits it (→ `INCOMPLETE`, auto-fix)
- `01-frame/prd-stale-frontmatter.md` — `ddx.depends_on` points at a
  removed feature id (→ `STALE_PLAN`, handoff)
- `01-frame/feat-renamed-section.md` — template renamed
  `Quality Gates` → `Review Checklist` (→ `INCOMPLETE`, auto-fix)
- `02-design/td-missing-story-ref.md` — template added required
  `## Story Reference` section (→ `INCOMPLETE`, auto-fix)
- `03-test/tp-missing-trailer.md` — template added Testing Strategy +
  canonical trailer (→ `INCOMPLETE`, auto-fix)
- `04-build/impl-plan-old-headings.md` — template renamed Risks table
  headings (→ `INCOMPLETE`, auto-fix)
- `05-deploy/runbook-no-frontmatter.md` — template added `ddx:`
  frontmatter (→ `INCOMPLETE`, auto-fix)
- `06-iterate/improvement-backlog-no-rce.md` — template added
  Rank/Confidence/Effort columns (→ `INCOMPLETE`, auto-fix)
- `06-iterate/improvement-backlog-divergent-rce-meanings.md` — fixture
  has Rank/Confidence/Effort columns but with semantics that contradict
  the current template definition (→ `DIVERGENT`, handoff)

`tests/refresh/expected/` captures the post-refresh shape. The harness
asserts:
1. All `INCOMPLETE` fixtures match `expected/` after refresh.
2. `DIVERGENT` and `STALE_PLAN` fixtures are *unchanged* and appear in
   the report with handoff fields.
3. The report's per-classification counts are correct.
4. No fixture outside `00-`..`06-` was touched.

## Implementation phases

| Phase | Output | Verifies |
|---|---|---|
| **P1. Taxonomy unification** | §Validate item 5 updated to use `ALIGNED`/`INCOMPLETE`/`DIVERGENT`/`UNDERSPECIFIED`/`STALE_PLAN`/`BLOCKED` verbatim | §Validate and §Align taxonomies match |
| **P2. Sharpen §Validate item 6** | §Validate item 6 rewritten per Prerequisite P2 above | Per-finding degrade documented |
| **P3. §Project Root Resolution section** | New top-level section in SKILL.md per Prerequisite P3 | Skill defines how to find operator's instance tree |
| **A. §Refresh body** | §Refresh added to `skills/helix/SKILL.md`; routing row added | §Refresh references P1/P2/P3, no new vocabulary |
| **B. Skill ratchet** | `tests/validate-skills.sh` asserts §Refresh + §Project Root Resolution sections present, and §Validate's taxonomy line matches §Align's | Ratchets all four SKILL.md changes |
| **C. Test fixture + harness** | `tests/refresh/{fixture,expected}/` populated; `tests/refresh/run.sh` wired | Harness fails before §Refresh, passes after. Fixture exercises both auto-fix and handoff paths |
| **D. Per-runtime install docs** | One paragraph per runtime install doc naming the runtime's fan-out behavior (per the table above) | All five install docs reference §Refresh |
| **E. Self-application sanity check** | One-shot §Refresh run on `docs/helix/**` produces output materially equivalent to today's manual batch | Sanity check — no harness, manual review |

P1, P2, P3 must all land before A (each touches a section §Refresh
references). P1/P2 can land in either order; P3 is independent of them.
B, C, D run in parallel after A. E is a smoke test after the rest.

## Proposed bead set

One epic + eight children:

| Bead | Phase | Acceptance |
|---|---|---|
| Epic: §Refresh as first-class HELIX skill behavior | — | All eight children closed |
| Unify §Validate item 5 taxonomy with §Align | P1 | `skills/helix/SKILL.md` §Validate item 5 lists `ALIGNED`/`INCOMPLETE`/`DIVERGENT`/`UNDERSPECIFIED`/`STALE_PLAN`/`BLOCKED` verbatim |
| Sharpen §Validate item 6 for per-finding degrade | P2 | `skills/helix/SKILL.md` §Validate item 6 contains the sharpened wording from this plan and references the unified taxonomy |
| Add §Project Root Resolution section to SKILL.md | P3 | `skills/helix/SKILL.md` has new top-level §Project Root Resolution section parallel to §Catalog Resolution |
| §Refresh contract in SKILL.md + routing row | A | `skills/helix/SKILL.md` contains §Refresh verbatim from this plan; routing table includes the new row |
| Ratchet §Refresh + §Project Root + taxonomy in `tests/validate-skills.sh` | B | Test fails when any of §Refresh, §Project Root Resolution, or unified taxonomy line is missing |
| §Refresh test fixture + harness | C | `bash tests/refresh/run.sh` passes after §Refresh lands; mutating the fixture fails the harness; fixture exercises both auto-fix and handoff paths |
| §Refresh paragraph in five install docs | D | All of `docs/install/{claude-code,codex,databricks-genie,copilot,README}.md` reference §Refresh with the runtime's fan-out note |
| §Refresh self-application sanity check | E | One-shot run on `docs/helix/**` produces output materially equivalent to today's manual batch |

P1, P2, P3 all block A. All beads land under the `helix` repo tracker.
No DDx beads expected — this is HELIX-internal.

## Remaining decision

None pending. The three Codex-surfaced concerns are now first-class
prerequisites; the uneven-fan-out concern is documented as a known
limitation accepted for v1.

If the prerequisites and the §Refresh contract above read correctly,
I'll file the bead set.
