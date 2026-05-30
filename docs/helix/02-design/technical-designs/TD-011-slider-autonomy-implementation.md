---
ddx:
  id: TD-011
  depends_on:
    - FEAT-011
    - ADR-003
    - helix.prd
---

# TD-011: Slider Autonomy Implementation

| Date | Status | Deciders | Related | Confidence |
|------|--------|----------|---------|------------|
| 2026-05-24 | Proposed | HELIX maintainers | FEAT-011, ADR-003 | High |

## Context

[[FEAT-011]] governs the `low`/`medium`/`high` autonomy spectrum. This design
specifies how the **content-only** HELIX realizes that policy: through action
prompts, the routing skill, and runtime-neutral artifacts. There is no HELIX
runtime to implement — the runtime supplies agency; HELIX supplies the words
that tell it how often to pause and what it may never skip.

This replaces the pre-collapse TD-011, which designed a `helix input` CLI, an
`execute-loop` queue drainer, and a `.helix/slider-config.yaml` schema. Those
surfaces were removed in 823aa1ac and are out of scope. What survives is the
behavioral contract.

## Requirements summary (from FEAT-011)

1. Three-position spectrum (`low`/`medium`/`high`), default `medium` (FR-1).
2. Resolution precedence: per-invocation → artifact frontmatter / project
   policy → runtime default; no `CLAUDE.md` (FR-2).
3. Concern inference at high autonomy when no `concerns.md` exists (FR-3).
4. Hard-stop invariant at every level (FR-4).
5. Never-collapse-the-loop invariant at every level (FR-5).

## Design decisions

### Decision 1 — Autonomy is resolved per action, not stored in a config file

Each action that can pause (input, frame, evolve, design, build) resolves the
active level at its bootstrap step using the FR-2 precedence chain:

```
level = invocation_override            # e.g. "--autonomy high" or explicit prompt instruction
      ?? governing_artifact.frontmatter.autonomy
      ?? project_policy.autonomy        # runtime-neutral project policy artifact
      ?? "medium"                       # runtime default
```

No file format is mandated beyond a runtime-neutral `autonomy:` key in
frontmatter or a project policy artifact. The level is data the action reads,
not a feature it owns. This keeps autonomy expressible identically across DDx,
Claude Code, Codex, Copilot, and Genie.

**Boundary note**: the runtime may surface the per-invocation override however
it likes (argument, env var, chat instruction). HELIX only fixes the precedence
order and the default, never the runtime mechanism.

### Decision 2 — Checkpoint density is the only thing the level changes

An action's *steps* are fixed by the action; autonomy parameterizes only the
**pause points** between and within them:

| Pause point | low | medium | high |
|-------------|-----|--------|------|
| Before interpreting ambiguous intent | ask | proceed + document | proceed + document |
| Before creating each downstream artifact | ask | create if deterministic | create |
| On a resolvable conflict | ask | ask | record assumption (`kind:speculative`), continue |
| On an ambiguous-scope decision | ask | ask | best-effort + speculative work item |
| On a **hard stop** (Decision 4) | stop | stop | stop |

The set of steps the action runs is identical across columns. Only the "ask"
cells differ. This is the mechanical statement of FEAT-011 FR-5.

### Decision 3 — Concern inference at high autonomy

When an action that touches concerns (frame, input, evolve) runs at `high` and
`docs/helix/01-frame/concerns.md` is absent:

1. Classify the product nature from the vision/PRD/intent (web app, API
   service, CLI, data pipeline, library).
2. Map the nature to candidate library concerns under `workflows/concerns/`
   (e.g. web app → a tech-stack concern + a frontend concern + `a11y-wcag-aa`;
   API service → tech-stack + `o11y-otel` + `security-owasp`).
3. Write `concerns.md` with the inferred selection, marking each as an
   assumption (a recorded inference, not a confirmed choice).
4. Detect conflicts among inferred concerns per `concern-resolution.md`; record
   unresolved ones as assumptions to revisit, never as a silent pick.

At `low`/`medium`, concern selection follows the interactive path in
`concern-resolution.md` §"Concern Selection in /helix frame". Inference never
overwrites an existing `concerns.md`.

### Decision 4 — Hard-stop classification

A hard stop is a condition no autonomy level may pass:

| Condition | Why it is a hard stop |
|-----------|----------------------|
| True contradiction between equal/higher-authority artifacts | The authority hierarchy cannot reconcile it; picking a side fabricates intent. |
| Destructive/irreversible unauthorized action | Cannot be undone; consent is required (mirrors the repo destructive-command guard). |
| Decision only a human can make | Product direction or an external contract change is outside agent authority. |

Everything else is a **resolvable conflict**: high autonomy records an
assumption and continues; low/medium ask. A runtime preserve/abort outcome ends
the current bounded attempt and returns control to HELIX — it is an execution
result, not a hard stop, and must not be re-classified as one.

### Decision 5 — Where the behavior is authored

| Surface | What it carries |
|---------|-----------------|
| `workflows/actions/input.md` | Canonical per-level rules (already present) + precedence note. |
| `workflows/actions/frame.md`, `evolve.md` | Concern inference at high autonomy. |
| `skills/helix/SKILL.md` §Autonomy | Level semantics, precedence, hard-stop, never-collapse-loop — runtime-neutral, no runtime-specific assertions. |
| Governing artifact frontmatter / project policy | The `autonomy:` value the precedence chain reads. |

## Traceability

| FEAT-011 requirement | Realized by |
|----------------------|-------------|
| FR-1 default medium | Decision 1 fallback |
| FR-2 precedence | Decision 1 chain |
| FR-3 concern inference | Decision 3 |
| FR-4 hard stop | Decision 4 |
| FR-5 never collapse loop | Decision 2 |

## Testing strategy

Behavioral, not unit — there is no HELIX code. Verification rides the existing
workflow-coverage harness ([[FEAT-014]]):

- A high-autonomy fixture run on a no-`concerns.md` project produces a
  `concerns.md` with inferred concerns (FR-3 / FEAT-011-AC3).
- A high-autonomy fixture with a planted equal-authority contradiction stops
  rather than picking a side (FR-4 / FEAT-011-AC4).
- An autonomy precedence fixture (invocation override vs frontmatter) resolves
  to the override (FEAT-011-AC2).
- A loop-collapse check confirms every required activity still runs at high
  autonomy (FR-5 / FEAT-011-AC5).

## Risks and mitigations

| Risk | Mitigation |
|------|------------|
| "More autonomy" misread as "skip activities" | FR-5 invariant stated in FEAT-011, ADR-003, skill, and Decision 2 here. |
| Inferred concerns drift from real product needs | Inference is recorded as an assumption and is an alignment-review target. |
| Autonomy leaks into `CLAUDE.md` | FR-2 explicitly excludes it; runtime-neutrality is a PRD-measured metric. |

## References

- [[FEAT-011]] — slider autonomy feature
- [[ADR-003]] — autonomy-spectrum decision
- [Input action](../../../workflows/actions/input.md)
- [Concern resolution reference](../../../workflows/references/concern-resolution.md)
