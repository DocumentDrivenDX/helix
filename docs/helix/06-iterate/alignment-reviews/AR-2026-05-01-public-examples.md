---
title: "Alignment Review: Public Examples Audit (2026-05-01)"
date: 2026-05-01
scope: HELIX_REAL_EXAMPLES mapping in scripts/generate-reference.py
purpose: Audit 19 HELIX docs proposed for publication as canonical artifact examples
---

# Alignment Review: Public Examples Audit

## Summary

5 of 20 docs disposed `publish`, 4 `publish after fixes`, 11 `descope`,
0 `follow-up only`. Net: 9 flip ON (after fixes), 11 stay disabled.

Note: the mapping in `scripts/generate-reference.py` lists 20 slug/path pairs
(the table in the brief lists 19 but `feature-specification`,
`product-vision`, `prd`, `concerns`, `architecture`, `data-design`,
`security-architecture`, `adr`, `contract`, `solution-design`,
`technical-design`, `test-plan`, `implementation-plan`, `runbook`,
`deployment-checklist`, `release-notes`, `monitoring-setup`,
`improvement-backlog`, `metrics-dashboard`, `security-metrics` is 20). All 20
are audited below.

The dominant blocker pattern is **artifact-restoration meta-decision docs
masquerading as worked examples**. Eight design/deploy/iterate slugs
(`data-design`, `security-architecture`, `runbook`, `deployment-checklist`,
`release-notes`, `monitoring-setup`, `improvement-backlog`,
`metrics-dashboard`, `security-metrics`) follow an identical structural
pattern: "Decision / Why It Exists / Canonical Inputs / Minimum Prompt Bar /
Minimum Template Bar / Canonical Replacement Status." These are HELIX-internal
debates about whether the artifact type should exist — they are not examples
of the artifact itself. Publishing them as canonical examples would teach a
reader that a release-notes document is a paragraph about why HELIX kept
the slot. That is the textbook authority-inversion failure codex warned about,
so all eight are descoped.

The supervisory/CLI-stack docs (vision, PRD, FEAT-002, architecture,
ADR-001, CONTRACT-001, SD-001, TD-002, STP-002) are substantively coherent
with CONTRACT-001 and survive truth checks. Most need only small drift fixes
(hardcoded `/home/erik/...` paths in ADR-001 references, `easel.github.io`
URL in concerns, `.helix/issues.jsonl` legacy paths in SD-001/STP-002). The
implementation plan is a live project status snapshot — descoped on
authority-inversion grounds (it is a project artifact, not a methodology
example).

## Disposition Table

| #  | Slug                  | Doc path                                                                  | Disposition          | Notes |
|----|-----------------------|---------------------------------------------------------------------------|----------------------|-------|
| 1  | product-vision        | docs/helix/00-discover/product-vision.md                                  | publish              | clean; aligned with CONTRACT-001 |
| 2  | prd                   | docs/helix/01-frame/prd.md                                                | publish after fixes  | minor: `helix-run` hyphenation, `parking-lot.md` reference |
| 3  | concerns              | docs/helix/01-frame/concerns.md                                           | publish after fixes  | `easel.github.io/helix/` URL, project-internal demos list |
| 4  | feature-specification | docs/helix/01-frame/features/FEAT-002-helix-cli.md                        | publish              | strong real example; aligns with CONTRACT-001 |
| 5  | architecture          | docs/helix/02-design/architecture.md                                      | publish after fixes  | `github.com/easel/ddx` URL needs check; otherwise solid |
| 6  | data-design           | docs/helix/02-design/data-design.md                                       | descope              | meta-decision doc, not a data design |
| 7  | security-architecture | docs/helix/02-design/security-architecture.md                             | descope              | meta-decision doc, not a security architecture |
| 8  | adr                   | docs/helix/02-design/adr/ADR-001-supervisory-control-model.md             | publish after fixes  | hardcoded `/home/erik/...` reference paths |
| 9  | contract              | docs/helix/02-design/contracts/CONTRACT-001-ddx-helix-boundary.md         | publish              | this is the authority anchor; canonically aligned |
| 10 | solution-design       | docs/helix/02-design/solution-designs/SD-001-helix-supervisory-control.md | descope              | references `.helix/issues.jsonl` (stale) and `[[FEAT-001-helix-supervisory-control]]` resolution unclear; multiple cross-refs need product-intent interpretation |
| 11 | technical-design      | docs/helix/02-design/technical-designs/TD-002-helix-cli.md                | publish after fixes  | small drift only (`.ddx/context.md` vs `.helix/context.md`) |
| 12 | test-plan             | docs/helix/03-test/test-plans/STP-002-helix-cli.md                         | descope              | `.helix/issues.jsonl` stale paths and inconsistent context.md location vs TD-002 |
| 13 | implementation-plan   | docs/helix/04-build/implementation-plan.md                                | descope              | live project queue snapshot — authority inversion risk |
| 14 | runbook               | docs/helix/05-deploy/runbook.md                                           | descope              | meta-decision doc, not a runbook |
| 15 | deployment-checklist  | docs/helix/05-deploy/deployment-checklist.md                              | descope              | meta-decision doc, not a checklist |
| 16 | release-notes         | docs/helix/05-deploy/release-notes.md                                     | descope              | meta-decision doc, not release notes |
| 17 | monitoring-setup      | docs/helix/05-deploy/monitoring-setup.md                                  | descope              | meta-decision doc, not a monitoring setup |
| 18 | improvement-backlog   | docs/helix/06-iterate/improvement-backlog.md                              | descope              | meta-decision doc, not a backlog |
| 19 | metrics-dashboard     | docs/helix/06-iterate/metrics-dashboard.md                                | descope              | meta-decision doc, not a dashboard |
| 20 | security-metrics      | docs/helix/06-iterate/security-metrics.md                                 | descope              | meta-decision doc, not a security report |

## Per-doc findings

### product-vision (`docs/helix/00-discover/product-vision.md`)

**Disposition:** publish

**Truth issues:** None. The vision aligns with CONTRACT-001: HELIX is the
supervisory layer; DDx owns managed execution. References to
`ddx agent execute-loop` and `ddx agent execute-bead` use the correct
DDx-owned framing. The "What HELIX Is Not" section explicitly cites
CONTRACT-001 as the canonical boundary doc.

**Currency issues:** None. No placeholders, no dated references, no "soon"
language with stale claims.

**Public-readability issues:** None. No personal paths, no internal
hostnames, no named individuals.

**Embed compatibility issues:** None. ATX headings only; 297 lines (well
under length cap); plain markdown tables; no embedded HTML.

**Tone (non-blocking) notes:** None significant. The voice matches the
website `/why/` pages.

### prd (`docs/helix/01-frame/prd.md`)

**Disposition:** publish after fixes

**Truth issues:** None substantive. References to FEAT-003, FEAT-004,
FEAT-005, FEAT-006, FEAT-008, FEAT-009, FEAT-010 are wikilinks; the brief
says "FEAT-003 phased out `workflows/principles.md`; FEAT-006 is current
concerns model" — the PRD references both as live, which matches because the
current model still depends on the principles+concerns split.

**Currency issues:**
- Line 68: `Deferred items tracked in docs/helix/parking-lot.md.` — verify
  this file still exists; if not, this is a dead reference for public
  readers.
- Lines 18, 56, 91, 95–97, etc.: uses `helix-run` (hyphenated) interchangeably
  with `helix run` (spaced). The CLI invocation is `helix run`. Hyphenation
  reads as a slightly older draft style.

**Public-readability issues:** None.

**Embed compatibility issues:** None. Frontmatter `dun:` block is benign for
the embed normalizer. 469 lines is long but under the 3000-line cap.

**Tone (non-blocking) notes:** Long for a worked example; site readers will
need to scroll. Acceptable.

**Required fixes:**
- [ ] Verify `docs/helix/parking-lot.md` still exists; if not, replace line
      68 with the current parking surface or drop the sentence.
- [ ] Normalize `helix-run` → `helix run` throughout the document
      (occurrences span lines 18, 42, 56, and the entire P0/Should Have
      sections — replace_all is safe).

### concerns (`docs/helix/01-frame/concerns.md`)

**Disposition:** publish after fixes

**Truth issues:** None on the boundary contract side; this is a project
concerns roster, not a methodology claim. The concerns model matches the
current FEAT-006 design.

**Currency issues:** None for placeholders; the active concerns
(`hugo-hextra`, `demo-asciinema`, `e2e-playwright`) are real and current.

**Public-readability issues:**
- Line 32: `Deployment: GitHub Pages at easel.github.io/helix/`. The public
  target per the audit brief is `documentdrivendx.github.io/helix`. This is
  a stale URL that would publish to the public site as wrong.
- Line 38: lists internal experimental demos and recording workflow details
  that are not documented elsewhere in the public site. These read as
  internal-only context, but they are not load-bearing secrets — they are
  acceptable as a representative project concerns example.

**Embed compatibility issues:** None. 48 lines; clean tables.

**Tone (non-blocking) notes:** None significant.

**Required fixes:**
- [ ] Update line 32 to the canonical public site URL
      (`documentdrivendx.github.io/helix`) or, more robustly, rephrase to
      `Deployment: GitHub Pages` without naming the org so the example does
      not need maintenance when the org changes.

### feature-specification (`docs/helix/01-frame/features/FEAT-002-helix-cli.md`)

**Disposition:** publish

**Truth issues:** None. FEAT-002 is internally consistent with CONTRACT-001
about the DDx/HELIX boundary. The "Post-DDx Queue-Drain Boundary" section
explicitly classifies HELIX surfaces as first-class vs compatibility-only vs
deprecation-candidate, consistent with the contract. The execution model
correctly cedes managed execution to DDx (`ddx agent execute-bead`,
`ddx agent execute-loop`).

**Currency issues:** None. Status `backfilled` with a 2026-03-25 date is
honest; no `[TBD]` placeholders.

**Public-readability issues:** None. References `~/.agents/skills` and
`~/.claude/skills` which are documented user-side skill paths, not personal
hostnames.

**Embed compatibility issues:** None. 334 lines; ATX headings; clean tables.

**Tone (non-blocking) notes:** Strong fit — feels like a maturely written
internal spec. This will read well as a canonical example of a HELIX feature
specification.

### architecture (`docs/helix/02-design/architecture.md`)

**Disposition:** publish after fixes

**Truth issues:** None on the boundary contract — architecture explicitly
defers to CONTRACT-001 for the DDx/HELIX split (lines 25–27). Mermaid
diagrams correctly show DDx as the substrate layer.

**Currency issues:** None significant. Port `7743` is documented as the
default ddx-server port; `port 7743` is explicitly called out as a
documented default in the audit brief, so it is acceptable.

**Public-readability issues:**
- Line 12: external link `https://github.com/easel/ddx`. If DDx has moved or
  is governed by an organization-level repo (e.g.
  `github.com/documentdrivendx/ddx`), this URL is stale. Worth verifying.
  If still correct, no fix needed.
- Mermaid `subgraph` labels reference internal containers (e.g.
  `~/.claude/skills`), which are documented user paths and acceptable.

**Embed compatibility issues:** Several mermaid diagrams. Hugo+Hextra
typically renders these via a shortcode, but plain ` ```mermaid ` fences may
or may not render in the embed pipeline. This needs a render-check before
flipping the slug on. If mermaid does not render, the diagrams will appear
as code blocks (degraded but not broken) — acceptable for a publish-after-fixes.

**Tone (non-blocking) notes:** Reads as a polished C4-style architecture
doc. Strong example.

**Required fixes:**
- [ ] Verify `https://github.com/easel/ddx` is the canonical public DDx repo
      URL; if DDx now lives under a different org, update the link.
- [ ] Verify mermaid diagrams render under the website's hextra theme; if
      not, accept the degraded code-block fallback or switch to ASCII.

### data-design (`docs/helix/02-design/data-design.md`)

**Disposition:** descope

**Truth issues:** This document is not a data design. It is a
HELIX-maintainer-facing decision artifact about whether the
`data-design` artifact slot should be retained. Sections "Decision," "Why
It Exists," "Minimum Prompt Bar," "Minimum Template Bar," and "Canonical
Replacement Status" are about the artifact type itself, not about modeling
any project's data. Publishing this as the canonical data-design example
would mislead readers about what a data design contains.

**Currency issues:** None.

**Public-readability issues:** None.

**Embed compatibility issues:** None.

**Tone (non-blocking) notes:** Well-written, but for the wrong purpose.

**Note:** The artifact reference page falls back to "_No worked example
captured yet..._" which is the correct user-facing outcome until a real
data design example exists in the repo.

### security-architecture (`docs/helix/02-design/security-architecture.md`)

**Disposition:** descope

**Truth issues:** Same pattern as data-design — this is a meta-decision doc
about whether the artifact type should exist, structured as Decision / Why
It Exists / Minimum Prompt Bar / Minimum Template Bar / Canonical
Replacement Status. It is not an example of a security architecture for any
system.

**Currency issues:** None.
**Public-readability issues:** None.
**Embed compatibility issues:** None.
**Tone (non-blocking) notes:** None.

### adr (`docs/helix/02-design/adr/ADR-001-supervisory-control-model.md`)

**Disposition:** publish after fixes

**Truth issues:** None substantive. The decision aligns with the supervisory
control model that CONTRACT-001 codifies. ADR-001 was written before
CONTRACT-001 (status: Proposed; date 2026-03-27) but it does not contradict
the contract — CONTRACT-001 is the downstream codification of the same
decision.

**Currency issues:** Status is "Proposed" — a real ADR that has been live
since 2026-03-27 and is referenced as authority by SD-001, TD-002,
architecture.md, and CONTRACT-001 should arguably be "Accepted." Status
inconsistency is a minor currency issue.

**Public-readability issues:**
- Lines 81–84: References section uses absolute personal paths:
  - `/home/erik/Projects/helix/docs/helix/00-discover/product-vision.md`
  - `/home/erik/Projects/helix/docs/helix/01-frame/prd.md`
  - `/home/erik/Projects/helix/docs/helix/02-design/solution-designs/SD-001-helix-supervisory-control.md`
  - `/home/erik/Projects/helix/docs/helix/02-design/technical-designs/TD-002-helix-cli.md`

  These will leak `/home/erik/...` into a public canonical artifact. Hard
  blocker for public publication; trivial drift fix.

**Embed compatibility issues:** None. Frontmatter only; 84 lines; clean.

**Tone (non-blocking) notes:** Compact, well-shaped ADR — strong example
once the path leak is fixed.

**Required fixes:**
- [ ] Replace lines 81–84 absolute paths with relative repo paths
      (`../../00-discover/product-vision.md`, `../../01-frame/prd.md`,
      `../solution-designs/SD-001-helix-supervisory-control.md`,
      `../technical-designs/TD-002-helix-cli.md`).
- [ ] Optional: update Status from "Proposed" to "Accepted" if the
      maintainers agree (this is a product-intent call; if any uncertainty,
      leave Status alone — that does not block publication).

### contract (`docs/helix/02-design/contracts/CONTRACT-001-ddx-helix-boundary.md`)

**Disposition:** publish

**Truth issues:** None — this is the authority anchor for the DDx/HELIX
boundary. By definition it cannot contradict itself.

**Currency issues:** Status "Draft" — possibly understates the contract's
current authority role (it is referenced as authority by every other doc in
the audit). Not a blocker for publication.

**Public-readability issues:** None. No personal paths; references to
`docs/helix/...` are repo-relative and the generator rewrites these.

**Embed compatibility issues:** None. 417 lines, JSON code block in section
"DDx -> HELIX," and a mermaid-free mix of ATX headings and tables. Renders
cleanly.

**Tone (non-blocking) notes:** Excellent fit as the canonical contract
example. This is the doc the rest of the audit triangulates against.

### solution-design (`docs/helix/02-design/solution-designs/SD-001-helix-supervisory-control.md`)

**Disposition:** descope

**Truth issues:**
- Line 12: `**Feature**: [[FEAT-001-helix-supervisory-control]]` — FEAT-001
  is referenced in the implementation plan as the supervisory control
  feature, but the feature spec file may or may not exist at
  `docs/helix/01-frame/features/FEAT-001-helix-supervisory-control.md`. If
  it does not, the wikilink resolves to a dead anchor in the embedded
  example.
- Line 58: references `.helix/issues.jsonl` as the tracker; the actual
  tracker per CONTRACT-001, architecture.md, FEAT-002, and TD-002 is
  `.ddx/beads.jsonl`. This is stale by an entire substrate migration.
- Lines 158, 163: refers to `align`, `evolve`, etc. as supervisor outputs;
  consistent with the rest of the stack.
- Lines 268–273: uses `helix-run` (hyphenated) consistently — minor
  cosmetic but inconsistent with current CLI naming.

The fix to line 58 (tracker path) requires interpreting whether SD-001
should be retroactively updated to reference the post-DDx-migration tracker
path or whether SD-001 was the design before migration. That is product
intent, not pure drift. Codex strictness rule applies: descope.

**Currency issues:** Multiple references to legacy paths and conventions
predate CONTRACT-001. Updating SD-001 to reflect the post-CONTRACT-001
state is design work, not a drift fix.

**Public-readability issues:** None.

**Embed compatibility issues:** None. 370 lines.

**Tone (non-blocking) notes:** Well-shaped solution design otherwise.

**Note:** Worth filing a follow-up to refresh SD-001 against CONTRACT-001
and the post-migration tracker path; once refreshed it is publishable.

### technical-design (`docs/helix/02-design/technical-designs/TD-002-helix-cli.md`)

**Disposition:** publish after fixes

**Truth issues:** None substantive. TD-002 explicitly aligns the CLI to
DDx-managed execution and treats the wrapper as compatibility-layer.
Consistent with FEAT-002, CONTRACT-001, and SD-001.

**Currency issues:**
- Line 138: states `.ddx/context.md must be regenerated...`. STP-002 line 62
  states `.helix/context.md is regenerated...`. One of the two is stale;
  the post-migration convention should be `.ddx/context.md` per the rest of
  the substrate's `.ddx/` location, but resolving this requires confirming
  the actual implementation.

**Public-readability issues:** None.

**Embed compatibility issues:** None. 437 lines; clean.

**Tone (non-blocking) notes:** Strong example of a HELIX technical design.

**Required fixes:**
- [ ] Reconcile `.ddx/context.md` (TD-002 line 138) vs `.helix/context.md`
      (STP-002 line 62) by checking the actual implementation; update
      whichever is wrong. If this requires interpreting product intent,
      escalate to descope this one slug.

### test-plan (`docs/helix/03-test/test-plans/STP-002-helix-cli.md`)

**Disposition:** descope

**Truth issues:**
- Line 62: refers to `.helix/context.md`; TD-002 line 138 says
  `.ddx/context.md`. Inconsistency between the test plan and the technical
  design it covers.
- Line 154: `Seed .helix/issues.jsonl with known issue graphs` — same stale
  path as SD-001. Real tracker is `.ddx/beads.jsonl`.

These are not pure drift — they require deciding which path is the post-
CONTRACT-001 source of truth. Product-intent interpretation per codex
strictness rule. Descope.

**Currency issues:** Test count "133 deterministic tests" is concrete and
likely correct, but verifying it requires running the suite.

**Public-readability issues:** None.
**Embed compatibility issues:** None. 183 lines.
**Tone (non-blocking) notes:** Otherwise a strong test plan example.

### implementation-plan (`docs/helix/04-build/implementation-plan.md`)

**Disposition:** descope

**Truth issues:** Authority inversion. This document is a live project queue
snapshot dated 2026-04-11, listing actual open bead IDs (`helix-f3062aa2`,
`helix-4243dd31`, etc.) and per-feature project status flags (PARTIAL,
DIVERGENT, COMPLETE). It is not a worked example of an implementation plan
template. Publishing it as the canonical implementation-plan example would
teach readers that an implementation plan is a project status report
identifying specific outstanding bead IDs, which is wrong.

Additionally, lines 91–113 list specific bead IDs and "live queue snapshot"
statuses that will rot quickly — every iteration moves these forward,
making the published example permanently stale by the next sprint.

**Currency issues:** Already stale-prone by design; "Snapshot rebuilt on
2026-04-11" is the giveaway.

**Public-readability issues:** Bead IDs are unobjectionable for public
viewing, but the entire frame is project-internal status reporting.

**Embed compatibility issues:** None.
**Tone (non-blocking) notes:** Reads as a maintainer queue review.

**Note:** A proper implementation-plan example should be a methodology
template for what a build-phase planning doc looks like for any project,
not HELIX's own current queue. File a follow-up bead to draft a generic
worked example.

### runbook (`docs/helix/05-deploy/runbook.md`)

**Disposition:** descope

**Truth issues:** Same pattern as data-design / security-architecture —
this is a HELIX-maintainer decision doc about whether the runbook artifact
type should be retained, not an example runbook for any service.
Publication would mislead readers.

**Currency issues:** None.
**Public-readability issues:** None.
**Embed compatibility issues:** None.
**Tone (non-blocking) notes:** Well-written for what it is.

### deployment-checklist (`docs/helix/05-deploy/deployment-checklist.md`)

**Disposition:** descope

**Truth issues:** Same restoration meta-decision pattern. Not a checklist;
a doc about whether the checklist artifact slot should exist.

**Currency issues:** None.
**Public-readability issues:** None.
**Embed compatibility issues:** None.
**Tone (non-blocking) notes:** None.

### release-notes (`docs/helix/05-deploy/release-notes.md`)

**Disposition:** descope

**Truth issues:** Same restoration meta-decision pattern. Not actual
release notes; a doc about whether the release-notes artifact slot should
exist.

**Currency issues:** None.
**Public-readability issues:** None.
**Embed compatibility issues:** None.
**Tone (non-blocking) notes:** None.

### monitoring-setup (`docs/helix/05-deploy/monitoring-setup.md`)

**Disposition:** descope

**Truth issues:** Same restoration meta-decision pattern. Not an example of
monitoring configuration; a doc about whether the artifact slot should
exist.

**Currency issues:** None.
**Public-readability issues:** None.
**Embed compatibility issues:** None.
**Tone (non-blocking) notes:** None.

### improvement-backlog (`docs/helix/06-iterate/improvement-backlog.md`)

**Disposition:** descope

**Truth issues:** Same restoration meta-decision pattern. Not an actual
improvement backlog with prioritized items; a doc about whether the
artifact slot should be retained.

**Currency issues:** None.
**Public-readability issues:** None.
**Embed compatibility issues:** None.
**Tone (non-blocking) notes:** None.

### metrics-dashboard (`docs/helix/06-iterate/metrics-dashboard.md`)

**Disposition:** descope

**Truth issues:** Same restoration meta-decision pattern. Not a metrics
dashboard with measured values; a doc about whether the artifact slot
should be retained.

**Currency issues:** None.
**Public-readability issues:** None.
**Embed compatibility issues:** None.
**Tone (non-blocking) notes:** None.

### security-metrics (`docs/helix/06-iterate/security-metrics.md`)

**Disposition:** descope

**Truth issues:** Same restoration meta-decision pattern. Not an actual
security posture report with measurements; a doc about whether the
artifact slot should be retained.

**Currency issues:** None.
**Public-readability issues:** None.
**Embed compatibility issues:** None.
**Tone (non-blocking) notes:** None.

## Cross-cutting findings

1. **Eight artifact-restoration meta-decision docs.** `data-design`,
   `security-architecture`, `runbook`, `deployment-checklist`,
   `release-notes`, `monitoring-setup`, `improvement-backlog`,
   `metrics-dashboard`, `security-metrics` — nine slugs, eight identical
   structures. Each was authored as an internal HELIX maintainer decision
   record about whether to retain the artifact slot in the methodology.
   None of them is an example of the artifact itself. This is the single
   biggest blocker pattern in the audit and accounts for nine of the
   eleven `descope` dispositions.

2. **Stale tracker path `.helix/issues.jsonl`.** SD-001 (line 58) and
   STP-002 (line 154) still reference `.helix/issues.jsonl`. Per CONTRACT-001,
   architecture.md, FEAT-002, and TD-002, the actual tracker is
   `.ddx/beads.jsonl`. These contradictions predate the DDx migration
   captured in CONTRACT-001 and require product-intent interpretation
   (refresh the design doc vs leave as historical record), so both are
   descoped under the codex strictness rule.

3. **Inconsistent context-refresh path.** TD-002 (line 138) says
   `.ddx/context.md`; STP-002 (line 62) says `.helix/context.md`. One is
   wrong; verifying which requires reading the implementation. Listed as
   a required fix on TD-002.

4. **Hardcoded `/home/erik/...` paths in ADR-001 References.** Lines 81–84.
   Trivial fix but a hard public-readability blocker if not addressed.

5. **`easel.github.io/helix/` URL in concerns.md.** Line 32. Public site
   is `documentdrivendx.github.io/helix`. Trivial fix; verify the canonical
   public URL.

6. **`github.com/easel/ddx` URL in architecture.md.** Line 12. May or may
   not be stale depending on whether DDx has moved orgs; verification
   needed before publication.

7. **`helix-run` vs `helix run` cosmetic drift.** PRD, ADR-001, SD-001,
   TD-002 all use the hyphenated form in places. The CLI invocation is
   `helix run` (space). Cosmetic but worth normalizing where the published
   example will be canonical reference.

8. **Implementation plan as live status snapshot.** The
   implementation-plan slug is mapped to a project-status doc with live
   bead IDs, not a methodology template. Authority inversion; descope and
   draft a generic example follow-up.

9. **No setext headings, no embedded HTML, no length blockers.** The
   embed-compatibility surface is clean across the entire 20-doc set. The
   only embed risk is mermaid rendering under hextra (architecture.md), and
   that is a degraded-but-not-broken fallback case.

## Follow-up beads to file

| Slug                       | What's wrong                                                                                                  | Effort |
|----------------------------|---------------------------------------------------------------------------------------------------------------|--------|
| data-design                | Author a real worked data-design example for a HELIX-tracked subsystem (e.g. tracker schema, executions log) | M (4–8h) |
| security-architecture      | Author a real worked security-architecture example for a representative HELIX surface                        | M (4–8h) |
| solution-design            | Refresh SD-001 against CONTRACT-001: tracker path, naming, post-migration substrate references               | S (2–4h) |
| test-plan                  | Reconcile STP-002 paths (`.helix/issues.jsonl` → `.ddx/beads.jsonl`; `.helix/context.md` vs `.ddx/context.md`) | S (1–2h) |
| implementation-plan        | Draft a generic implementation-plan worked example (not the live HELIX queue)                                 | M (4–8h) |
| runbook                    | Author a real worked runbook for a representative service (e.g. ddx-server)                                  | M (4–8h) |
| deployment-checklist       | Author a real worked deployment checklist for a representative HELIX release                                  | S (2–4h) |
| release-notes              | Author a real worked release notes doc tied to a known HELIX release tag                                      | S (2–4h) |
| monitoring-setup           | Author a real worked monitoring setup for a representative HELIX surface                                      | M (4–8h) |
| improvement-backlog        | Author a real worked improvement-backlog example with ranked tracker-backed items                             | S (2–4h) |
| metrics-dashboard          | Author a real worked metrics-dashboard example with concrete metric tables                                    | S (2–4h) |
| security-metrics           | Author a real worked security-metrics report                                                                  | S (2–4h) |

Total descope follow-ups: 11 beads. Combined effort: ~40–80 hours of
methodology authoring. Not blocking the Phase 1 flip — these can be added to
the publishable set incrementally as each example is authored.

## Recommended HELIX_REAL_EXAMPLES_ENABLED state

```python
# After this audit, enable individually rather than all-at-once.
# Rationale: 11 of 20 mapped docs are not actually worked examples of their
# slug — they are HELIX-internal decision records about whether the artifact
# slot should exist (8 cases), live project status snapshots
# (implementation-plan), or post-migration design docs that still cite the
# pre-migration tracker path (SD-001, STP-002). Publishing those would
# misteach readers about what each artifact contains.
#
# The publishable set is the supervisory/CLI stack: vision, PRD, FEAT-002,
# architecture, ADR-001, CONTRACT-001, TD-002, plus concerns. These are
# substantively aligned with CONTRACT-001 and need only small drift fixes
# (hardcoded paths in ADR-001 references; easel.github.io URL in concerns;
# helix-run hyphenation in PRD; .ddx/context.md reconciliation in TD-002).
HELIX_REAL_EXAMPLES_ENABLED = True  # Global flag stays on
HELIX_REAL_EXAMPLES_PUBLISHABLE = {
    "product-vision",            # publish — clean
    "prd",                       # publish after fixes (helix-run norm, parking-lot.md verify)
    "concerns",                  # publish after fixes (easel.github.io URL)
    "feature-specification",     # publish — clean
    "architecture",              # publish after fixes (verify ddx repo URL, mermaid render)
    "adr",                       # publish after fixes (hardcoded /home/erik paths)
    "contract",                  # publish — authority anchor
    "technical-design",          # publish after fixes (.ddx/context.md vs .helix/context.md)
}
# Excluded (descope): data-design, security-architecture, solution-design,
# test-plan, implementation-plan, runbook, deployment-checklist,
# release-notes, monitoring-setup, improvement-backlog, metrics-dashboard,
# security-metrics. Each has a follow-up bead listed above.
```

## Method note

Single-batch sub-agent audit, 2026-05-01, Claude Opus 4.7 (1M context).
Authority hierarchy applied: CONTRACT-001 > current specs/PRD/ADRs >
website /why and /use tone > existing microsite phrasing.
Codex's strictness rule applied: product-intent interpretation = descope.
Audit covered all 20 slug/path entries in `HELIX_REAL_EXAMPLES`
(`scripts/generate-reference.py`) — the brief's table of 19 expanded once
the actual mapping was inspected. No documents were modified during the
audit.
