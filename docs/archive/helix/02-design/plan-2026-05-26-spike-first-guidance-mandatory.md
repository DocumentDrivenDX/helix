# Plan: it.34 — "defer the vendor" is NOT a spike; a spike must EXERCISE the real provider and prove its economics (+ build the app-side data; unowned business calls → guidance-needed)

Date: 2026-05-26 · Scope: methodology (concern-resolution + evolve + plan + tech-spike & adr artifacts) · Branch: helix-self-improvement-2026-05-24
Runtime-neutral; additive `ddx:` frontmatter preserved. Operator-directed ("push it.32 harder" + the spike-definition clarification below).

## Problem (bench-evidenced + operator clarification)

it.32 added the spike-first ACTIVATION trigger. The clean it.32 re-bench (helix-yolo b8qc8y30w, fair prompt,
billing fully open) showed it still doesn't de-risk the operator's canonical case: codex built a `BillingMeter`
(local metering dimensions) **+ deferred the live vendor**, and treated that as decided.

**Operator's sharpened definition of a spike (the core of it.34):** *"Deferring to some unknown vendor is not
an acceptable response for a spike. If there's a vendor, and you can test that vendor with the spike, and you
can prove the cost and other economic terms are acceptable, then that's a spike."* Concretely for this product:
the billing backend vendor is **known (Recurly)**; the usage **data-collection must be BUILT into the app**;
only the pricing *model* may be an unowned business decision.

**Root cause (the residual hole in it.32):** the agent discharges the anti-reframe check by **picking a local
default + deferring the live integration to an unspecified/"deferred" vendor.** That de-risks integration
*timing* only — NOT the design-defining facts a spike exists to prove (cost, economic/commercial terms,
ingestion/integration contract, correctness). "Provider-behind-abstraction + deferred live integration" is
being mis-used as a spike substitute.

## Change (operator-directed, bounded)

Two linked rules, threaded into the existing it.32 anti-reframe sites:

1. **A spike must EXERCISE the real provider, not defer it.** "Defer to an unknown/unspecified vendor" is NOT a
   valid de-risking of a materially-uncertain external-integration capability. When a provider exists or is
   named (e.g. Recurly for billing), the spike must actually exercise it to prove its **design-defining facts —
   cost, economic/commercial terms, the integration/ingestion contract, correctness** — OR record a **blocked
   spike** (why it could not run: missing creds/sandbox/budget; what was read or simulated; which decisions
   stay provisional). A local default behind a swappable interface + a deferred live vendor does **not**
   discharge the decision; it only sequences the integration. Also: the **app-side data the integration
   requires** (e.g. usage-metering events the app emits) is BUILD work for the slice — build it, don't defer it.

2. **An unevidenced design-defining BUSINESS decision the agent can't settle → mandatory guidance-needed.** For
   a pricing/charge model, what-to-meter-at-what-rate, or commercial terms the agent has no authority/evidence
   to decide, a PICKED runnable default does NOT discharge it: record an explicit **guidance-needed** item
   (what decision, why it's not the agent's, residual risk, provisional default in use) and do NOT mark it
   "Accepted/decided". A spike can't answer a non-technical decision → route it to guidance-needed.

NOT "spike everything": fires only within the existing it.32 scope (unmatched capability / concern-conflict /
operator-named uncertainty). A *technical* mechanism the agent CAN evidence stays low-risk → concern. The new
teeth target the two real failures: (1) faking/deferring a known vendor instead of testing it, (2) silently
baking an unowned business decision.

### Where (runtime-neutral edits)

1. **`workflows/references/concern-resolution.md`** (step 3a, the canonical anti-reframe) — add the
   "picked default ≠ discharged; unevidenced business decision → mandatory guidance-needed (not Accepted)" rule.
2. **`workflows/actions/evolve.md`** — mirror (this is where billing slipped through).
3. **`workflows/actions/plan.md`** (step 4a + the GUIDANCE_NEEDED status) — mirror; and: if any design-defining
   business decision is unevidenced/guidance-needed, the plan status is **GUIDANCE_NEEDED**, not CONVERGED.
4. **`workflows/activities/02-design/artifacts/adr/prompt.md`** (ADR-acceptance guard) — an ADR may not record a
   decision as **Accepted** when its design-defining facts are an unevidenced business decision; it carries a
   **provisional / guidance-needed** status + the residual risk + the open decision, instead.

Where guidance-needed items live: the `risk-register` (residual risk) and/or `parking-lot` (the open decision
with a revisit trigger) — point at those; do not invent a new artifact. Keep each edit short/additive. Re-bless
`concern-resolution` (stamped). Preserve `ddx:` frontmatter; SKILL.md stays 0 ddx hits (only touch SKILL.md if
its verify/route wording needs the same "guidance-needed not silent default" note — check during impl).

## Validation (re-bench)

Re-run the faithful EVOLVE (claude or codex) toward hubspot-hints with billing left fully open. Success: the
agent now records pricing/what-to-meter as an explicit **guidance-needed** item (operator/product decision
required, residual risk noted, provisional default in use) — NOT a silently-accepted ADR; the slice still
builds + verifies on the provisional default. Cross-check no over-firing: technical/known providers
(event-streaming/auth/datastore) still go concern+provider-behind-abstraction, not guidance-needed.

## Over-engineering guard / risks

- Scope is narrow: unevidenced **business/product** design-defining decisions only, within the existing it.32
  trigger scope. A chosen *technical* mechanism with evidence stays low-risk. Avoid turning every deferral into
  a guidance-needed item.
- Codex-review BOTH ends (plan now; diff after). Neutrality preserved.

## OUTCOME (2026-05-26) — mostly ALREADY IMPLEMENTED; residual = one clause

On reaching it.34, an audit found edits #1-#4 of this plan were ALREADY in place
(folded into the it.32/it.33 anti-reframe work): concern-resolution 3a, evolve.md,
plan.md (incl `PLAN_STATUS: GUIDANCE_NEEDED`), and adr/prompt.md all already state
"spike even for a known vendor; choosing+deferring a provider ≠ evidence; a
business/pricing unknown a technical spike can't answer → guidance-needed". So
it.34's core was a no-op (YAGNI — not re-implemented).

The one **residual gap** — the operator's "the data collection must be built into
our apps" — was added: a clause in concern-resolution 3a + evolve.md stating that
deferring the external vendor call does NOT defer the **app-side data it consumes**
(e.g. usage-metering events); that data is build-work for the runnable slice.
That is the entire it.34 delta.
