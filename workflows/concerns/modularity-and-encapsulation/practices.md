# Practices: Modularity and Encapsulation

## Frame

Resolve the source-code baseline in `workflows/references/concern-resolution.md`
at every autonomy level. Select this composable concern for handwritten source,
including libraries. Record applicability, source, and `areas: all`; source-free
projects record why it does not apply. Do not force an architecture-style filler.

## Design

Write `## Module Boundaries` in Architecture. Use this structural evidence format:

- `**Source Applicability**: source; <reason>` or `source-free; <reason>`.
- For source projects, a table with columns `Module`, `Responsibility / Owned Types`,
  `Public API`, `Allowed Dependencies`, and `Forbidden Dependencies`. Each row
  names actual packages/files and has nonempty values. Explicit `None; <reason>`
  is valid; a small project may have one row.
- `**Integration Owners**: <external system -> owning module; translation location>`.
  If absent, state `None; <reason>`.
- `**Construction Policy**: <wiring owner/location and approach>`. Local construction
  is valid under classic-layered; inversion styles retain their composition rules.
- `**Boundary Check**: <concrete project-local command>`; it must enforce the map.

Source-free documents need only applicability and reason in this section. Legacy
artifacts without the section remain structurally valid; current source feature
work requires adoption before execution readiness. The instance validator checks
structure and populated fields when the section exists. Review checks correctness,
including type ownership, API visibility, invariants, translation, and style fit.

Do not copy normative signatures into Architecture or TD. Shared interface details
belong in Contracts; module maps may name APIs and reference their Contract IDs.

## Build

Establish the map and a stack-appropriate dependency checker before dependent
feature work. Use one command in local checks, pre-commit, and CI; prove both an
allowed dependency passes and a forbidden dependency fails. Test the real checker,
not a test-only clone. Use compiler/package visibility where available; supplement
unsupported checks with explicitly named review evidence.

Changes add code to its owning module, not whichever orchestrator is convenient.
New external integrations get a named module. Preserve minimal exports and avoid
passing mutable internal state across public interfaces.

## Test

- Run the actual import checker against allowed and forbidden edges; prove cycle
  and private-access detection where the chosen tool supports them.
- Test invariants through public APIs, including mutation/invalid-state rejection
  where applicable. Check vendor/ORM/transport shapes do not leak into APIs unless
  deliberately accepted by the selected architecture style.
- Where isolation or substitution is promised, run core behavior without live
  integrations and exercise the adapter contract with a fake implementation.
- Record unsupported static checks as semantic review obligations. Do not claim
  regex presence checks prove dependency direction or runtime behavior.

## Existing-project adoption

Inventory specific violations by source and target, with owner and remediation
work. Baseline only existing violations; unchanged debt may remain while new edges
fail. Baseline/adoption/checker work may execute before the gate exists; dependent
feature work is not ready. Tighten the baseline as remediation lands.

Overrides may adapt enforcement mechanisms. Departures require an exception with
exact scope, owner, governing authority, rationale, alternative verification, and
review/removal trigger. A blanket directory exclusion or larger baseline used to
hide new violations is not valid adoption.

## Review and Align

Compare current imports and public surfaces with the map and Contracts within the
requested scope. Report missing baseline, incomplete boundary evidence, unmeasured
checker gates, and new violations as blocking readiness findings. Preserve legacy
artifact validity and report adoption gaps separately from structural validation.
