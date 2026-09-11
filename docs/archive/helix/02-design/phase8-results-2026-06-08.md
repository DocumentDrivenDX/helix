# Phase 8 results — bench infra + 5 surgical fixes

## Headline

| Metric | Phase 7 baseline | Phase 8 result | Delta |
|---|---|---|---|
| Stable_pass on the 14-row failure subset | 0/14 | **6/14 (43%)** | **+6** |
| Broken (docker eviction) | 2/17 (Phase 7 ran 17, 2 broken) | **0/14** | infra fixed |

Spend: ~$25 (Sonnet, 14 rows × 3 passes, ~$0.60/probe avg).

## Wins (6)

| Row | Fix attribution | Phase 7 → Phase 8 |
|---|---|---|
| `CF-02-pipeline-needs-dns` | sibling-skill name fix: `expected_flow_instance: helix-data` → `helix` (post canonical-skill collapse) | F/F/F → P/P/P |
| `CF-03-whats-blocked-multi-flow` | same fix: `skill_id: helix-data` → `helix` | F/F/F → P/P/P |
| `EA-01-prd-feat-candidates-guided` | `[^\n]{0,80}` → `[\s\S]{0,200}` — confirmation_marker_pattern now tolerates newlines in Sonnet's bulleted FEAT enumeration | F/F/T → P/P/P |
| `EA-02-prd-feat-candidates-guided-named` | same newline fix | F/T/F → P/P/P |
| `EA-03-prd-feat-candidates-autonomous` | same newline fix | T/F/F → P/P/P |
| `G5-upstream-discovery` | bench infra (image survival): full conversation completes now instead of failing at docker pull | broken → P/P/P |

## Near-misses — flake (4 rows)

| Row | Phase 7 | Phase 8 | Note |
|---|---|---|---|
| `C011-what-methodologies-active` | [P/F/F] (1/3) | [T/F/T] (2/3) | Inconsistent reading of marker — sometimes engages, sometimes uses training knowledge |
| `C017-plan-rollout-ambiguous-autonomous` | [F/F/F] | [T/T/F] (2/3) | The autonomous-routing prose-attribution hint is biting on 2/3 samples; one more iteration of the SKILL.md wording might land it |
| `G3-artifact-canonicalization` | [F/F/F] | [F/T/T] (2/3) | Discriminator widening from Tier 1 + Phase 7 + Phase 8 cumulatively helping; close to stable |
| `EA-04-prd-feat-candidates-autonomous-many` | [P/F/F] (1/3) | [F/F/T] (1/3) | Newline regex helped EA-01..03 but EA-04's 4-FEAT case still inconsistent — Sonnet doesn't reliably name all 4 candidates |

## Stable fails (4)

| Row | Why | Recommended next |
|---|---|---|
| `C014-reject-unauthorized-flow` [T/F/F] | The `[^\n]` → `[\s\S]` regex fix landed; pass0 PASS confirms it works. But Sonnet doesn't always emit the marker-pointing refusal — sometimes it just refuses generically. The skill body §5 wording could be tighter, OR the row's prompt needs framing that makes the marker-citation more natural | SKILL.md §5 wording iteration |
| `CD-02-positive-control-no-edge` | `file_read` matcher needs both `read_indices` AND `surfaced` to fire. Sonnet surfaces "market-validation-brief" from training memory without reading graph.yml | Workspace-fixture defense: change the edge signature to something unmistakably project-local (e.g. `prd requires snake-oil-validation`) that can't be guessed |
| `CD-04-robustness-variant` | Same `file_read` defect as CD-02 with `regulatory-impact-assessment` edge | Same fixture-defense approach |
| `G4-orchestration-with-gates` | Prompt rewrite from Phase 7 added "FEAT-X (Receipt export, spec at docs/...)" but the workspace has no docs/helix/01-frame/FEAT-X-receipt-export.md file. Sonnet correctly asks for it | Add the FEAT-X fixture file to the workspace |

## Infra fix (8.1) — validated end-to-end

`family-test/docker/run-probe.sh` now rebuilds `family-test-claude:latest` on demand if docker has evicted it. Verified by deleting the image and running a probe — image rebuilt automatically, probe succeeded. Phase 8 re-bench (14 rows over ~80 min) completed with zero docker evictions.

## Aggregate scoreboard across all phases

**27 unique stable_pass rows confirmed:**

- AM-01..04 (4 rows — autonomy matrix, Phase 5a)
- C003, C008, C013, C015, C016, C018, C024 (7 rows — marker edges, prompt rewrites, discriminator widenings)
- CD-01, CD-03 (2 rows — Phase 7 discriminator widenings)
- CF-02, CF-03 (2 rows — Phase 8 sibling-skill fixes)
- EA-01, EA-02, EA-03 (3 rows — Phase 8 newline tolerance)
- G1 (Phase 5a — new gap row, scope_write_path discriminator)
- G2 (Phase 6 — discriminator widening)
- G5 (Phase 8 — bench infra fix)
- MI-01..06 (6 rows — Phase 6 matcher_change for multi-instance disambiguation)

## Stage 5b recommendation

**Conditional YES** — the floor is now substantially clean:

- 27 rows confirmed stable_pass (up from ~0 measurable at session start)
- Docker eviction issue resolved (8.1)
- 5 known remaining defects (4 stable_fail, 4 near-miss flake) are characterized and either small skill-body iteration OR workspace fixture work — they're not architectural

If the goal is **clean ratchet seeding**, Stage 5b (~$107 at current per-probe rates, ~3-4h wall-clock) is now safe to run. Expect:
- Routing baseline ~0.7-0.8 (vs current 0.6667; the v0.2.4 → v0.2.5 description tweaks may have nudged it)
- Stable_pass on full 71 conv set probably 0.45-0.55 (extrapolating from the 27 confirmed wins + new rows that haven't yet been Phase-8-touched)

If the goal is **finalize the remaining 8 rows first**, Phase 9 would be:
1. SKILL.md §5 sharpening for C014 stable-emission
2. Workspace fixture defense for CD-02/CD-04
3. Add FEAT-X file to G4 workspace
4. EA-04 4-FEAT regex one more iteration
5. Then Stage 5b on a near-clean bench

I'd suggest **proceed with Stage 5b NOW** for the ratchet reset — the Phase 9 work is iterative refinement on a bench that's already broadly clean. Ratchets seeded now provide a useful baseline; refinements move them up, not down.
