# Implementation Notes — HELIX self-improvement (plan rev 2, 2026-05-24)

Implements `docs/helix/02-design/plan-2026-05-24-helix-self-improvement.md` in
full across the three buckets (docs/ specs, workflows/, skill). No git commit
performed, per instructions.

## Verification summary

- `git diff --check`: **CLEAN**.
- New/edited YAML frontmatter and edited `meta.yml` files: parse OK.
- `skills/helix/SKILL.md`: contains no `compatibility` token and no
  runtime-specific assertions (`tool_use`, `ddx …`, `claude -p`, `codex exec`);
  all `validate-skills.sh` SKILL.md assertions pass (the suite reaches the later
  beads block, i.e. it got past every SKILL.md assertion).
- ddx review graph: cycles I introduced via bidirectional `[[ID]]` links were
  removed (see Assumption 4). `ddx doc validate` shows only **pre-existing**
  warnings (the `data-architecture` template cycle; `ADR-001`/`ADR-003`/`TP-XXX`
  duplicate-id warnings across example/fixture dirs; `FEAT-004→FEAT-002` /
  `SD-002→SD-001` missing-dep warnings).
- `just test`: three failures, **all proven pre-existing** by running `just
  test` on a pristine `HEAD` worktree (same `test-skills` failure point, no
  edits of mine). See "Pre-existing test failures" below.

## Files created

| File | Why |
|---|---|
| `docs/helix/01-frame/features/FEAT-011-slider-autonomy.md` | L2 — restore the slider-autonomy feature (resolves dangling refs in `input.md`, CONTRACT-001/002). Reuses `low/medium/high` semantics; extends with concern-inference at high autonomy (FR-3), resolution precedence (FR-2), hard-stop invariant (FR-4), never-collapse-loop invariant (FR-5). Re-scoped to content-only methodology (no CLI). |
| `docs/helix/02-design/technical-designs/TD-011-slider-autonomy-implementation.md` | L2 — implementation design realizing FEAT-011 through action prompts + skill + runtime-neutral artifacts. Replaces the pre-collapse CLI/slider-config design. |
| `docs/helix/02-design/adr/ADR-003-autonomy-spectrum.md` | L2 — ADR recording the three-position autonomy decision, precedence chain, and the two invariants. Cited by FEAT-011 and the skill. |
| `docs/helix/01-frame/features/FEAT-016-artifact-honesty.md` | L1 — new feature for claims-vs-reality / `ASSERTED_UNBACKED` + zero-floor phantom-claim ratchet. Global artifact honesty; cross-referenced by FEAT-008 + FEAT-014. |

## Files modified

### Bucket 1 — docs/ specs

| File | Change |
|---|---|
| `docs/helix/01-frame/features/FEAT-006-...md` | L3 — FR-14 (concern selection is a required Frame step + high-autonomy inference) and FR-15 (propagation is a gate owned by check/polish, not selection). Re-stamped. |
| `docs/helix/01-frame/features/FEAT-008-...md` | L6 — FR-6 (AC↔test traceability: stable `US-<n>-AC<m>` IDs, story-level matrix, test-plan aggregation + layer allocation) + AC#5; cross-ref to FEAT-016. Re-stamped. |
| `docs/helix/01-frame/features/FEAT-014-workflow-coverage.md` | L4/L5 — new "Self-Validation Meta-Gates and Convergence" section (MG-01 mode-gates, MG-02 convergence = "verified + finding-classes folded into gates", MG-03 cross-ref FEAT-016) + two AC rows. |
| `docs/helix/02-design/contracts/CONTRACT-002-...md` | Re-stamped so the recorded `FEAT-011` dependency hash matches the restored FEAT-011 (the specific "dependency changed: FEAT-011" staleness is resolved). |
| `docs/install/claude-code.md` | L7a — "Interactive vs headless activation" note: `/helix` slash is interactive-only; headless `claude -p` runs activate by skill name/description. Cross-ref FEAT-013. |
| `docs/install/codex.md` | L7a — "Activation phrasing (by name, not slash)" note for `codex exec`. Cross-ref FEAT-013. |
| `docs/helix/01-frame/prd.md` | Pre-existing reword at `:97` (autonomy spectrum) / `:98` (no loop flattening) / `:90` (zero runtime-specific commands metric) — verified present; not edited this session. |

### Bucket 2 — workflows/

| File | Change |
|---|---|
| `workflows/actions/input.md` | Autonomy semantics extended with resolution precedence (FR-2), all-levels invariants (hard stop + never-collapse-loop), and high-autonomy concern inference. |
| `workflows/actions/frame.md` | L3 — STEP 0a makes concern selection a required step with `low/medium` interactive vs `high` inferred paths; STEP 6 measure gate now requires concern selection to have happened. |
| `workflows/references/concern-resolution.md` | L3/L7b — selection-vs-propagation-gate distinction; high-autonomy inferred-selection path; "Composed-concern runtime friction" (typescript-bun + react-nextjs / `bun:sqlite` under `next build`). Re-stamped. |
| `workflows/actions/implementation.md` | L4 — Step 7 self-validation mode-gate (acceptance SATISFIED + claims-vs-reality clean / zero `ASSERTED_UNBACKED`), framed as a verify-activity gate not a literal validate/align/check command list. |
| `workflows/actions/evolve.md` | L4/L5 — "Evolve Default and Convergence" section (progressive evolve over re-splat; convergence ≠ reviewer SHIP) + STEP 8 self-validation mode-gate. |
| `workflows/actions/measure.md` | L4 — STEP 2.5 Claims-vs-Reality check (`ASSERTED_UNBACKED`, zero floor). |
| `workflows/actions/report.md` | L4 — `phantom-claim` follow-on category. |
| `workflows/actions/fresh-eyes-review.md` | L5 — "Convergence" section (clean verdict necessary-not-sufficient; finding-classes folded into gates; progressive evolve). |
| `workflows/actions/reconcile-alignment.md` | L5 — convergence criterion in STEP 10. (The L1 `ASSERTED_UNBACKED` classification at Step 3 was already present pre-session and is kept.) |
| `workflows/activities/01-frame/artifacts/user-stories/{template,prompt,example}.md`, `meta.yml` | L6 — stable `US-<n>-AC<m>` AC IDs in Given/When/Then; example uses `US-001-AC1..3`; meta adds a blocking check + `US-[0-9]+-AC[0-9]+` pattern check; test-scenario tables gain an AC-ID column. |
| `workflows/activities/03-test/artifacts/story-test-plan/{template,prompt,example}.md`, `meta.yml` | L6 — AC↔test matrix re-keyed on the stable AC ID (new `AC ID` column); meta adds an AC-ID pattern check; prompt/example state STP owns the matrix and TP aggregates. Example re-stamped. |
| `workflows/activities/03-test/artifacts/test-plan/{template,prompt}.md` | L6 — "Acceptance Criteria Layer Allocation" section: aggregates strategy + allocates AC classes to layers without duplicating the per-AC story matrix. |
| `workflows/concerns/typescript-bun/practices.md` | L7b — "Composed-Concern Friction": `bun:*` built-ins (incl. `bun:sqlite`) need the Bun runtime; `next build` runs under Node → use `bun --bun` or isolate; record as project override. |
| `workflows/concerns/react-nextjs/practices.md` | L7b — friction with typescript-bun: run Next.js under `bun --bun` so `bun:sqlite` resolves, or isolate the data layer; record as project override. |
| `workflows/ratchets.md` | Pre-existing L1 phantom-claim zero-floor sub-ratchet — kept (not edited this session). |

### Bucket 3 — skill

| File | Change |
|---|---|
| `skills/helix/SKILL.md` | New `## Autonomy` section (low/medium/high + precedence + hard-stop + never-collapse-loop, runtime-neutral); Frame route makes concern selection a prominent required step with high-autonomy inference and adds the stable-AC-ID step; Evolve/Review/Build routes reference the self-validation/convergence gates (claims-vs-reality, finding-classes folded into gates, progressive evolve). No runtime-specific assertions; no `compatibility` token. |

## ddx re-blessing

Re-stamped (`ddx doc stamp`) the documents I content-edited that carry a review
block, in dependency order, plus CONTRACT-002:
`FEAT-006`, `FEAT-008`, `concern-resolution.md`,
`user-stories/example.md`, `story-test-plan/example.md`, `CONTRACT-002`.
The new draft features/design/ADR are left without their own review block
(matching the existing `FEAT-014` precedent); the repo's review graph is broadly
unblessed at the root (`helix.prd` carries no review block), so a full re-bless
was intentionally not cascaded.

## Pre-existing test failures (NOT caused by this work)

Proven by running `just test` on a pristine `HEAD` git worktree — it fails at the
identical point with none of my edits present:

1. **`test-skills`** (`validate-skills.sh` execution-ready beads block): the
   installed `ddx v0.6.2-alpha103` CLI now returns the ready epic `hx-ready-epic`
   from `bead ready --execution`, while `scripts/validate_execution_ready_beads.py`
   excludes epics. CLI-vs-validator version drift. The failing files
   (`validate-skills.sh`, the validator, the fixture) are unmodified by me.
2. **`test-context-digests`**: bead `helix-e3c7d0e4` (integration-test epic) is
   missing a `<context-digest>` — present in committed HEAD `.ddx/beads.jsonl`.
   I did not touch `.ddx/beads.jsonl`.
3. **`test-demo-fixtures`**: `docs/demos/helix-concerns/demo.sh` is absent (the
   dir predates this session). I did not touch `docs/demos/`.

Per the project guidance "do not add workaround flags for others' bugs," I did
not patch the validators or fixtures to mask these.

## Assumptions recorded

1. **FEAT-011 / TD-011 were rewritten, not byte-restored.** The pre-collapse
   versions governed a removed CLI surface (`helix run`, `execute-loop`,
   `.helix/slider-config.yaml`) and were marked superseded; restoring them
   verbatim would contradict the current PRD. I reused the `low/medium/high`
   semantics from `input.md` and extended per the plan, scoped to the
   content-only methodology.
2. **ADR number = ADR-003** (next free in `docs/helix/02-design/adr/` after
   ADR-002; ADR-001 was deleted in the collapse). The duplicate-id warning vs
   `docs/examples/crm/.../ADR-003-database-orm.md` is the same tolerated class
   as the existing `ADR-001` duplicates across example/fixture dirs.
3. **Graph cycles avoided.** Bidirectional `[[ID]]` links create ddx graph
   cycles. To honor the plan's cross-ref direction (FEAT-008/014 **→** FEAT-016;
   autonomy deps point up), I trimmed `FEAT-016` `depends_on` to `helix.prd` and
   made the back-references plain text: `FEAT-016`→FEAT-008/014, FEAT-011→ADR-003,
   FEAT-006→FEAT-011. Forward `[[ ]]` cross-refs (FEAT-008/014 → FEAT-016) are kept.
4. **Website mirrors untouched.** `website/content/artifacts/...` is generated by
   `scripts/publish-artifacts.py`; the new FEAT-011/016, TD-011, ADR-003 were not
   hand-mirrored there.
5. **L7a scope = headless runtimes.** Added the by-name-activation note to
   `claude-code.md` and `codex.md` (where slash inertness in `-p`/`exec` runs
   matters). Copilot (repo-instructions file) and Genie (browser-only) do not
   have the same slash surface, so they were left unchanged.
6. **`reconcile-alignment.md` and `ratchets.md`** already carried the L1
   `ASSERTED_UNBACKED` ratchet (Phase 0, uncommitted before this session). I kept
   them and only added the L5 convergence note to `reconcile-alignment.md`.
