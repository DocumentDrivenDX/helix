# Plan — complex-brief robustness: verification ENFORCEMENT + spike-first for unknowns (2026-05-26)

## Context

The HubSpot complex-brief bench (helix-yolo it.30) ran the same hard brief on claude + codex and exposed two
methodology gaps via their cross-runtime divergence:

- **V — the verification gate is STATED but not ENFORCED, unevenly across runtimes.** Both runs *selected*
  react-nextjs + e2e-playwright + verification. codex HONORED them (built a react SPA, browser e2e VERIFIED);
  claude DROPPED them under load (built server-rendered, 0 tsx, e2e ABSENT). The methodology says "done = whole
  stack exercised" but nothing makes the agent reconcile the BUILT app against the SELECTED slots/gate before
  declaring done — so a runtime under load silently retreats.
- **S — no spike for unknowns.** NEITHER runtime spiked the genuinely-unknown capabilities (usage-based
  billing, Seventh Sense send-time optimization, priority-queue design, multi-cloud marketplace) — 0 spikes
  total. evolve.md *detects* "a technology not covered by any active concern" but doesn't say what to DO.

Both are HELIX-artifact fixes that benefit one-shot AND evolution, and are runtime-neutral.

## V — Verification ENFORCEMENT (close the selection↔build gap)

A closing self-gate, in the methodology (not a harness): before "done", the agent must reconcile the BUILT
implementation against the SELECTED concerns/slots and produce evidence.

| # | Change | File(s) | Done when |
|---|--------|---------|-----------|
| V1 | `verification` "done" ENFORCES selection↔build coherence: the **selected `frontend-framework` slot is actually honored** (react-nextjs ⇒ a real React/Next app exists — **SSR/RSC is fine**; the defect is selecting react-nextjs then building *no* React/Next, codex fix 1) AND **a core-flow e2e runs GREEN when a UI slot is selected/applicable**. Verification only **refuses-done + requires evidence**; it does NOT restate Playwright mechanics — runner choice stays in `e2e-framework` (codex fix 5). A selected-slot↔build mismatch with no recorded decision is a blocking finding. | `workflows/concerns/verification/practices.md` | practices require selected-slot-honored + green-e2e-when-applicable before done, without duplicating e2e tooling |
| V2 | Implementation done-gate reconciles selected concerns/slots vs the built app. A **silent retreat** (built a different stack, no recorded decision, no evidence) is a defect. A **justified deviation** is allowed only with the full recorded shape (codex fix 2): the slot/concern selection is **updated**, the reason is tied to an acceptance constraint, the **verification plan is updated**, and **substitute evidence is run**. Honor existing verification **exceptions** (docs-only / non-buildable / infeasible-e2e) (codex fix 6). | `workflows/actions/implementation.md` | done-gate distinguishes silent-retreat (defect) from recorded-deviation (allowed) + honors exceptions |
| V3 | SKILL.md build/verify guidance: "not done until the built app honors the selected slots + (for a UI slot) a core-flow e2e runs green; changing a selected stack mid-build requires a recorded decision + updated evidence, never a silent swap." (runtime-neutral) | `skills/helix/SKILL.md` | SKILL reflects the enforcement + the recorded-deviation rule |

## S — Spike-first for unmatched/unknown capabilities

| # | Change | File(s) | Done when |
|---|--------|---------|-----------|
| S1 | Unmatched-capability **decision rule** (risk-based, not binary — codex fix 3): a required capability with no matching concern → **clear, low-risk pattern** (known provider, well-understood integration) → add a concern (provider-behind-abstraction / fill the slot) or a plain ADR; **material uncertainty/cost/permissions/correctness/operational risk** (even with a known vendor — billing, marketplaces, send-time optimization, queue design) → define a `tech-spike` and de-risk it. Don't fabricate a concern for the not-yet-understood; don't silently ignore it. | `workflows/references/concern-resolution.md` (extend the "technology not covered" detection) | rule states the risk-based split |
| S2 | Spike feasibility (codex fix 4): prefer a **bounded runnable** spike (small, time/scope-boxed) **when feasible**; if running is infeasible/unsafe (external/paid APIs, missing creds, long benchmarks) record a **blocked-spike** artifact — why it couldn't run, what was read/simulated instead, and which decisions stay **provisional**. evolve.md applies the same rule at its unmatched-tech decision point (it detects ~line 155 but doesn't act). | `workflows/actions/evolve.md` + tech-spike artifact prompt | evolve routes unmatched-risky → bounded spike (run or recorded-blocked) |
| S3 | The planning/design action treats **spiking as a first-class path to good design** — a hard/unknown choice is de-risked by a (bounded) spike before the ADR/technical-design commits. | `workflows/actions/plan.md` (the design route; + tech-spike/proof-of-concept artifact cross-ref) | plan/design guidance elevates spike-then-decide |

## Validate (re-bench via the real TUI — validation only, not required for every downstream change, codex fix 6)

Re-run the HubSpot brief via the TUI driver on BOTH runtimes and check: (a) claude no longer silently
retreats — the built app honors the selected react-nextjs slot (SSR/RSC fine) + a core-flow e2e runs GREEN, or
a deviation is recorded with updated slot + evidence; (b) the risky/unknown capabilities (billing, send-time
optimization, marketplace, queue) are routed to a bounded spike (run, or recorded-blocked) rather than ignored
or fabricated. Compare to the baseline pair. Keep only what moves a metric.

## Invariants
- Runtime-neutral; no `Skill tool_use` in the skill body; no ddx reintroduced. Don't flatten the loop.
- Enforcement is a *floor* (honor what you selected; spike what you don't understand), not new ceremony.
- Spiking is first-class, not a fallback. Keep `check-workflow-paths` green; re-bless ddx hashes;
  codex-review BOTH ends.
