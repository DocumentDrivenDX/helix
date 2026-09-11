# Plan: spike-first ACTIVATION trigger (close the reframe-and-defer escape hatch)

Date: 2026-05-26 · Scope: methodology (concern-resolution + evolve + plan/design route + tech-spike artifact)
Branch: helix-self-improvement-2026-05-24 · Runtime-neutral (no ddx assumptions; additive `ddx:` frontmatter preserved)

## Problem (evidence-backed)

it.31 added a risk-based unmatched-capability rule (S1/S2/S3): material uncertainty → `tech-spike`;
clear/low-risk → concern (provider-behind-abstraction) or ADR. The faithful HubSpot **evolve** bench
(helix-yolo bq95almg1, 2026-05-26) is the first run to exercise it on a genuinely-unknown capability —
**usage-based billing**, which the operator named as THE spike case.

**Result: spike-first did NOT fire. 0 spikes.** The agent handled all 6 evolve capabilities — including
billing — via provider-behind-abstraction + ADR + deferred-live. ADR-012 decided billing as a KNOWN pattern
(a `UsageMeter` consuming the event stream, idempotent per `event_id`, behind a `BillingProvider` with Stripe
deferred) and even invented a `billing` concern — the exact opposite of "billing is unknown → spike, don't
invent a concern."

**Root cause (refined): the reframe-and-defer escape hatch.** The S1 rule already names billing as a
material-uncertainty example, but the agent never reaches that branch because it:
1. **Reframes** the unknown into a known sub-problem — "billing" becomes "event-metering mechanism", which IS
   a standard pattern → classified low-risk → concern.
2. **Defers** the genuinely design-defining uncertainty (what to meter, the pricing model, marketplace billing
   integration) behind the "deferred-live provider" — without flagging it as needing investigation.

So choosing a mechanism + naming a provider makes the whole capability *feel* known, and the design-defining
decisions get silently assumed. Deferring the live provider de-risks **integration timing**; it does NOT
de-risk the **design-defining decision**. The rule's risk *examples* aren't enough — agents need an explicit
check that defeats the reframe. (Same pattern, lower stakes, in greenfield: adapter + defer.)

This is recurring + operator-aligned ("spiking is a key activity"; the hints rule names billing→spike).

## Proposed change (LIGHT, targeted — not "spike everything")

The evolve's handling of the 5 KNOWN providers (event-streaming, auth, operational-store, entity-graph,
analytics) was EXEMPLARY — concern + provider-behind-abstraction is correct there. Do **not** push those toward
spikes. Target only the reframe-and-defer hole. Add an **anti-reframe activation check** to the existing
risk-based rule:

> Before routing a capability to a concern/ADR as "low-risk", name the decisions the **design depends on**
> (for billing: what to meter + the pricing/charge model; for a queue: throughput/ordering/delivery semantics;
> for an integration: the provider's actual API shape/limits). **Choosing a mechanism or naming a provider does
> not make the capability low-risk if any of those design-defining decisions is being ASSUMED rather than
> known.** If a design-defining decision is assumed → that is material uncertainty → `tech-spike` (bounded-
> runnable, else blocked), **even when a provider is chosen and its live integration is deferred**. Deferring
> the live provider de-risks integration timing, not the design-defining decision. The alternative to a spike
> is not "concern + defer" — it is a **recorded assumption + residual-risk note** stating what was assumed and
> what could invalidate it.

### Where (runtime-neutral edits)

1. **`workflows/references/concern-resolution.md`** (step 3a) — the canonical anti-reframe check.
2. **`workflows/actions/evolve.md`** (unmatched-tech point, ~line 156) — mirror it (evolve is where it failed).
3. **`workflows/actions/plan.md`** (step 4a, the design route) — same at design time.
4. **`workflows/activities/02-design/artifacts/tech-spike/meta.yml`** (`relationships.triggers`) — add the
   activation triggers (selection-time, stronger than prompt.md alone).
5. **`workflows/activities/02-design/artifacts/tech-spike/prompt.md`** — one-line "create me when…" pointer.
6. **`workflows/activities/02-design/artifacts/adr/prompt.md`** — ADR-acceptance guard (this is where ADR-012
   slipped through): an ADR must not accept a decision whose design-defining facts are assumed without spike
   evidence, a blocked-spike rationale, or an explicit provisional-risk note.

Keep it additive and short. Re-bless stamped docs (`concern-resolution`). Preserve all `ddx:` frontmatter.

## Codex review (before implementation): VERDICT **SOUND-WITH-FIXES** — all 5 incorporated

1. **Operator-marked unknown is AUTHORITATIVE.** A capability the operator flagged "spike/unknown" is evidence
   of uncertainty the agent may NOT demote (defeats the billing demotion directly).
2. **Tighten the escape hatch.** "Recorded assumption + residual risk" is NOT an equal substitute for a spike
   when the design COMMITS to the assumption — it's acceptable only when the assumption is reversible/
   non-blocking, explicitly provisional, or the spike is blocked/infeasible.
3. **Bound over-spiking by SCOPE + definition.** Run the check ONLY for: unmatched capabilities, active-concern
   conflicts, or operator-named uncertainty. Name only the **top 1-3 design-defining decisions**, where
   *design-defining* = could change API shape, data model, pricing/cost semantics, security/permissions,
   operational guarantees, or work decomposition.
4. **6 sites, not 4** (prompt.md is read *after* selection → weak): add `tech-spike/meta.yml`
   `relationships.triggers` + an **ADR-acceptance guard** in `adr/prompt.md`.
5. **Define "known" = EVIDENCED, not model-familiarity** — evidenced by operator statement, governing artifact,
   existing implementation, docs/API proof, or a completed spike. (This is the crux defeating the reframe.) Use
   runtime-neutral terms (work item / artifact / runtime-provided work source). For **business** unknowns
   (pricing): allow "guidance needed" or a blocked spike rather than forcing a *technical* spike to answer a
   non-technical decision.

### Canonical anti-reframe clause (the text to thread, condensed per site)

> A capability is **"known/low-risk"** only when its design-defining facts are **evidenced** (operator
> statement, governing artifact, existing implementation, docs/API proof, or a completed spike) — **not** model
> familiarity, and **not** because you picked a mechanism or named a provider. Before routing an unmatched
> capability / concern-conflict / operator-named-uncertain capability to a concern or ADR, name its **top 1-3
> design-defining decisions** (anything that could change API shape, data model, pricing/cost, security/
> permissions, operational guarantees, or decomposition). If any is **assumed** rather than evidenced → that is
> material uncertainty → **`tech-spike`** (bounded-runnable, else blocked), **even when a provider is chosen and
> its live integration is deferred** (deferring integration ≠ de-risking the decision). An operator-marked
> "spike/unknown" is authoritative — do not demote it. The only alternative to a spike is a **recorded
> assumption + residual-risk note**, and only when the assumption is reversible/non-blocking, explicitly
> provisional, or the spike is blocked. For a **business/product** unknown (e.g. pricing model) a technical
> spike may not answer it — record **guidance-needed** or a blocked spike instead.

## Validation (re-bench)

Re-run the faithful EVOLVE (claude, in-place on a fresh copy of the faithful claude ws) toward the same
hubspot-hints. Success = the agent now, for **billing**, either (a) creates a `tech-spike` (bounded or blocked)
that de-risks what-to-meter/pricing, OR (b) records an explicit assumption + residual-risk note instead of
silently picking a metering scheme — while STILL handling the 5 known providers via provider-behind-abstraction
(no regression to over-spiking). Cross-check codex too.

## Risks / over-engineering guard

- **Over-gating** (CLAUDE.md YAGNI/KISS): the check must not turn every deferral into a spike. It targets
  *design-defining* uncertainty only; a chosen mechanism with all design-defining decisions known stays
  low-risk → concern. The "recorded assumption + residual risk" alternative keeps the bar light.
- **Codex-review BOTH ends** (per practice) — review THIS plan before implementing; review the diff after.
- Neutrality: no `.ddx/` paths, no `ddx <verb>` literals; additive `ddx:` frontmatter preserved.
