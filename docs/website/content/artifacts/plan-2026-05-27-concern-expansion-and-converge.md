---
title: "Plan — concern-library expansion + make-concerns-bite + iterate-to-convergence (2026-05-27)"
slug: plan-2026-05-27-concern-expansion-and-converge
weight: 680
activity: "Design"
source: "02-design/plan-2026-05-27-concern-expansion-and-converge.md"
generated: true
---
# Plan — concern-library expansion + make-concerns-bite + iterate-to-convergence (2026-05-27)

Plan-of-record for the current program (dogfoods the plan-as-file model). Captured as a file
by default; under DDx this would be a bead. Status markers: [x] done · [~] in flight · [ ] queued.

## Goal
1. Expand the HELIX concern library with architecture, platform, and cross-cutting concerns
   (operator: "do all tier 1-3" + databricks + MCP + usage-tracking).
2. Make concerns **bite** — a selected concern must change the ADR / FEAT / TD / SD / plan, not
   just exist as prose.
3. Operationalize "go check your work again" — a bounded evolve-until-converged loop.
4. Re-bench the 6 one-shots under it.39 + the new concerns, iterating until ACs met + specs align.

## Concern inventory
Reviewed (codex SOUND-WITH-FIXES, minor):
- [x] domain-driven-design, onion-architecture, design-patterns-gof, enterprise-integration-patterns, event-sourcing
- [x] classic-layered, hexagonal-architecture, clean-architecture (fill `architecture-style` slot)
- [x] multi-tenancy, deployment-topology (guide), api-style (guide)
- [x] unity-catalog, databricks-apps (→ deploy-target), databricks-declarative-pipelines
- [x] mcp-server, usage-metering (+ api-style edited to add MCP as the agent-facing style)

In flight (Tier 2/3 — review pending):
- [~] cqrs, resilience, enterprise-application-patterns, authorization-model
- [~] relational-data-modeling, caching-strategy, frontend-architecture, twelve-factor, concurrency-model

## Slotting decisions (reconciled)
- [x] New exclusive slot `architecture-style` (members: onion/classic-layered/hexagonal/clean) — **no default**, select-on-signal.
- `databricks-apps` fills the existing `deploy-target` slot. All other new concerns are **non-exclusive** (no slot) — deployment-topology + api-style are decision-guides, not slots.

## Consolidation (queued — after all land + reviewed)
- [ ] Format fixes (from review): `unity-catalog` + `databricks-declarative-pipelines` DELETE their `## Slot` block; `databricks-apps` → bare `## Slot: deploy-target`; `api-style` MCP typing (only *tools* are JSON-Schema-typed).
- [ ] `concern-resolution.md` §2: add selection bullets for every non-exclusive/guide concern + the `architecture-style` resolution rule (resolve only when an architecture-style member is selected). `authorization-model` now exists → resolves multi-tenancy's forward reference.
- [ ] Commit the whole batch on `helix-self-improvement-2026-05-24`.

## Make-concerns-bite (methodology iteration — it.40)
- [ ] Thread concern-resolution into the **feature-specification, technical-design, and implementation-plan** prompts (today only ADR/solution-design/design-system/principles reference concerns — verified gap).
- [ ] Add a `reconcile-alignment` **concern→artifact realization** check: a selected concern must appear in its governing artifacts (codex gave the per-concern "selecting X must change artifact Y" map — use it). Empirically tested by the re-bench (diff artifacts with/without a concern).

## Operationalize "check your work again" (methodology iteration — it.41)
- [ ] A bounded **evolve-until-converged** loop: build → reconcile-alignment + it.39 verification gate → if findings, evolve against them → re-review → repeat (max-iterations cap) until all ACs SATISFIED (guard branches), zero blocking findings, specs aligned. it.39 set the EXIT criteria; this is the LOOP. File default; DDx → bead.

## Re-bench (after the above)
- [ ] 6 one-shots = (claude,codex,ddx) × (invoicing,hubspot), each iterating to convergence under: the new concerns (DDD-minimum, both projects), the it.39 verification exit gate, and the converge loop. ddx via `ddx plugin install helix --local /Users/erik/Projects/helix --force` (symlink — verified; picks up the new concerns automatically).

## Parked (operator-gated, unprompted = no)
- [ ] push `origin/main` (local main at 38dffac; branch ahead with it.39 + this batch).
- [ ] INT-CC release-gate slice (needs the `ANTHROPIC_API_KEY` repo secret).
