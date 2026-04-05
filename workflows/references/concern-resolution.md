---
dun:
  id: helix.workflow.concern-resolution
  depends_on:
    - helix.workflow.principles-resolution
    - FEAT-006
---
# Concern and Practices Resolution

This reference defines the shared pattern that HELIX action prompts follow
to load the active project concerns and their associated practices.

## Resolution Logic

### Concerns

1. Check: does `docs/helix/01-frame/concerns.md` exist and have content?
   - Yes -> load it as the active concerns document.
   - No -> no active concerns. Omit concerns and practices from context.

There are no default concerns. Unlike principles, concerns are always
project-specific. A project without a concerns file simply has no declared
cross-cutting context beyond principles.

### Area Filtering

Each concern declares an `areas` field in its `concern.md`:

- `all` — applies to every bead
- `ui`, `frontend` — applies to UI work
- `api`, `backend` — applies to API/service work
- `data` — applies to data-layer work
- `infra` — applies to infrastructure work
- Comma-separated list for multiple areas

When assembling context for a bead, match the bead's `area:*` labels against
each concern's `areas` field. Only include concerns that match.

If a bead has no `area:*` labels, only concerns with `areas: all` are included.

### Practices

1. Parse the active concerns document for selected concerns (listed under
   `## Active Concerns`).
2. Filter to concerns matching the current bead's area scope.
3. For each matched concern, load
   `workflows/concerns/<concern-name>/practices.md` from the library.
4. Apply project overrides (listed under `## Project Overrides` in the
   concerns document) on top of library practices.

Project overrides take full precedence.

## Injection Preamble

After resolving active concerns and merged practices, include them in
your working context:

```markdown
## Active Concerns

{area-matched concern names and key constraints}

## Active Practices

{merged practices from matched concerns with project overrides applied}

Use the declared concerns and practices when making choices.
When a concern specifies a tool, convention, or quality requirement,
follow it rather than choosing an alternative.
```

## When to Apply

Action prompts that involve technology or quality choices must resolve and
inject concerns at their Phase 0 or Bootstrap step, alongside principles.

| Action | Injection Point |
|--------|----------------|
| `implementation.md` | Phase 0 (Bootstrap) — alongside principles and quality gates |
| `fresh-eyes-review.md` | Phase 0 — verify implementation follows concern conventions |
| `plan.md` | Before first refinement round — concerns constrain architecture |
| `evolve.md` | Phase 1 — concerns affect scope of downstream changes |
| `reconcile-alignment.md` | Phase 0 — concern drift is an alignment finding |
| `polish.md` | Bootstrap — verify beads reference correct concern context |
| `frame.md` | Bootstrap — concern selection happens during framing |
| `experiment.md` | Bootstrap — experiments must use declared concerns |

**Not injected**: `check.md` (mechanical queue evaluation),
`backfill-helix-docs.md` (reconstructs what exists).

## Concern Selection in helix frame

When `helix frame` runs and no `docs/helix/01-frame/concerns.md` exists:

1. List available concerns from `workflows/concerns/` grouped by category.
2. Ask the user about each category:
   - Tech stack: "What language, runtime, and package manager?"
   - Data: "What database or data layer?"
   - Infrastructure: "Where will this deploy?"
   - Quality: "Do you need a11y, i18n, o11y?"
3. Match answers to available concerns.
4. If custom needs exist, document them as project overrides.
5. Write `docs/helix/01-frame/concerns.md`.

## Conflict Detection

When a project selects multiple concerns, check for conflicting practices:

1. For each practice category (linter, formatter, testing, etc.), check
   whether multiple concerns declare different values.
2. If a conflict exists and no project override resolves it, flag it to
   the user with a concrete example.
3. Conflicts must be resolved via project overrides before the concerns
   file is considered complete.

## Relationship to ADRs and Spikes

Concerns are the index; ADRs provide the rationale; spikes provide the
evidence:

```
Spike/POC (gather evidence)
  → ADR (record decision with rationale)
    → Concern (index for context assembly)
      → Context Digest (injected into beads)
```

- A spike or POC investigates a question.
- An ADR records the decision with rationale, citing the spike.
- The concern references the ADR in its `## ADR References` section.
- Project overrides that depart from library defaults must cite the
  governing ADR.

When a referenced ADR is superseded, `helix polish` must flag the
affected concern for re-evaluation.
