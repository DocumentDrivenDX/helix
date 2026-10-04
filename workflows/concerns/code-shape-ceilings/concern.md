# Concern: Code Shape Ceilings

## Category
quality-attribute

## Areas
all

## Boundary

This concern is the **shape gate**: it bounds how large and how branchy a
function, class, and file may get, so god objects and god functions cannot
form. It is mechanical (a linter or script fails), global (one ceiling, no
per-file exceptions), and runs while the agent edits, not only in CI.

It composes with its neighbors and does not duplicate them:

- **`scope-discipline`** owns *is the change the right size* (no gold-plating,
  no hollow stubs). This concern owns *is the code the right shape*. A change
  can build exactly what was asked and still pile it into one 3,000-line file.
- **`verification`** owns observed evidence that the system runs; **`testing`**
  owns test strategy and the coverage floor. Neither bounds code shape.
- **`python-uv`**, **`typescript-bun`**, and **`react-vite`** own the
  toolchain (ruff, pyright, Biome, ESLint). This concern owns the rule set and
  the strict default values for those tools (see `practices.md`).
- **`architecture-style`** fillers (onion, hexagonal, clean, classic-layered)
  own *where* code lives between layers; this concern owns how big any one
  unit may be inside a layer.
- **`workflows/ratchets.md`** owns the ratchet pattern; this concern is a
  ratchet whose floor is a ceiling.

## Components

- **Complexity ceilings**: cyclomatic complexity, branches, returns,
  statements, and parameters per function, set in the linter config
- **Class ceiling**: a cap on public methods per class
- **File-length ceiling**: one script, with a separate cap for test files
- **Ceilings-only-go-down check**: a script that compares the working tree
  with the merge base and fails a diff that raises a ceiling or adds a
  silencer for one of these rules
- **Editing-time hooks**: a Claude Code `PostToolUse` hook that lints the
  edited file and checks file length, and a `Stop` hook that runs the full
  lint gate before a turn ends
- **Git pre-commit hook**: runs the same lint gate as CI

## Constraints

### Greenfield starts strict

- A new project sets the **strict defaults** in `practices.md` for its stack
  from the first commit. There is no baseline to ratchet from,
  so no value is looser than the default.
- An existing project that adopts this concern sets each ceiling to the worst
  value in its tree today and lowers it as code is split. The adoption is
  recorded in the TD with the starting values.

### Global, no exceptions

- Ceilings apply to the whole tree. No per-file ignore, `noqa`, `eslint-disable`,
  `biome-ignore`, or `# pyright: ignore` for a complexity, size, or
  parameter-count rule. When a unit trips a ceiling, split it.
- Generated code, vendored code, and lockfiles are excluded by path in the
  gate script, once, with a comment saying why. Hand-written code is never
  excluded.

### Ceilings only go down

- A change that raises a ceiling, or adds a silencer for one of these rules,
  fails the ceilings check. The only way to pass is to split the code.
- Lowering a ceiling is always allowed and is encouraged whenever a split
  brings the worst unit in the tree under the next lower value.

### Gates run while the agent edits

- The shape gate is wired into the agent loop (post-edit lint, stop-time full
  lint) and the git pre-commit hook, and CI runs the same recipe. A gate that
  only runs in CI is found after the god object exists.
- One recipe (`just lint` or the stack's equivalent) is the single entry point
  for hooks and CI, so they cannot drift apart.

### Where new code goes

- A new external system, protocol, or integration goes in its own module, not
  into an existing orchestrator. A class that accumulates unrelated
  responsibilities is split by responsibility, not by line count alone.

## Drift Signals (anti-patterns to reject in review)

- A linter config with no complexity or size rules selected (ruff without
  `C901`/`PLR`, ESLint without `complexity` and `max-lines-per-function`) →
  add them at the strict defaults
- A ceiling raised, or a `noqa` / `eslint-disable` / `biome-ignore` for a
  complexity, size, or parameter rule → split the code; revert the change
- A per-file ignore list, or a type-checker `ignore` list of modules → the
  excuse list is the god-object list; remove entries by splitting the files
- A source file past the file ceiling, or one class that owns persistence,
  business rules, and an external client together → split by responsibility
- `harness.py`, `utils.py`, `helpers.ts`, `manager`, `service`, or `index`
  files growing every sprint → a god module; name modules for what they do
- Lint runs only in CI → wire the editing-time and pre-commit hooks
- A lint command that exists but is missing from `just lint` or from the
  hooks → the gate and the hook must run the same recipe

## When to use

Every project with hand-written source code, from the first commit. High
autonomy auto-selects this concern for buildable products, alongside
`scope-discipline` and `verification` (see
`workflows/references/concern-resolution.md`). Library, docs-only, and
non-buildable work with no source code may omit it.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- TD: the ceiling values per stack, the file-size caps, the gate recipe, and the hook wiring
- IMPLEMENTATION_PLAN: scaffold the lint config, the size and ceilings scripts, the hooks, and `just lint` before feature work
- TEST_PLAN: the shape gate (`just lint`) runs in CI and fails the build; a raised ceiling or new silencer is a blocking finding
- ADR: an adoption baseline for an existing project (starting values), or a recorded reason for any value looser than the default
