---
title: "Code Shape Ceilings"
slug: code-shape-ceilings
generated: true
aliases:
  - /reference/glossary/concerns/code-shape-ceilings
---

**Category:** Quality Attributes · **Areas:** all

## Description

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

## Practices by activity

Agents working in any of these activities inherit the practices below through runtime work context, such as a DDx bead context digest.

These practices bound function, class, and file size so god objects cannot
form. They sit beside `scope-discipline` (right-sized change) and name the
toolchain only through the selected stack concern's linter.

## Requirements (Frame activity)

- Select this concern for every project with hand-written source code.
- Record in `concerns.md` whether the project is greenfield (strict defaults)
  or adopting (starting values measured from the tree).

## Design

- Record the ceiling values, the file-size caps, and the excluded paths (with a
  reason each) in the TD.
- Design modules by responsibility. A new external system, protocol, or
  integration gets its own module; an orchestrator delegates to it.

## Implementation

Scaffold the gate before feature work: the lint config, the two scripts, one
`lint` recipe, the Claude hooks, and the git hook. Then write features.

### Strict defaults for greenfield

| Rule | Python (ruff) | TypeScript (ESLint) | TypeScript (Biome, `typescript-bun`) |
|---|---|---|---|
| Complexity per function | `mccabe.max-complexity = 10` | `complexity: 10` | `noExcessiveCognitiveComplexity` at 15 |
| Function length | `pylint.max-statements = 40` | `max-lines-per-function: 60` (skip blanks, comments) | none; file cap only |
| Parameters | `pylint.max-args = 5` | `max-params: 4` | none; review |
| Returns / branches | `max-returns = 6`, `max-branches = 12` | `max-depth: 4` | none; review |
| Public methods per class | `pylint.max-public-methods = 15` (needs `PLR0904`, a preview rule) | `max-classes-per-file: 1` | none; review |
| File length | `SOURCE_MAX = 500`, `TEST_MAX = 800` | same script | same script |

Python also selects `C901` and `PLR` (ignore only `PLR2004`), sets
`preview = true` with `explicit-preview-rules = true` and
`extend-select = ["PLR0904"]`, and runs pyright with `strict` on application
code. TypeScript also sets `strict: true` and `noUncheckedIndexedAccess: true`,
and enables `@typescript-eslint/strict`, `no-floating-promises`, and
`no-misused-promises`. Under `typescript-bun`, enable the Biome rule in
`biome.json`; Biome has no function-length, parameter, or depth rule, so those
fall to the file cap and review.

Adopting projects replace each number with the worst value in the tree today,
then lower it.

### Python config

```toml
[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "UP", "S", "SIM", "RUF", "PT", "C901", "PLR"]
preview = true
explicit-preview-rules = true
extend-select = ["PLR0904"]
ignore = ["PLR2004"]

# Global ceilings. No per-file exceptions; lower them, never raise them.
[tool.ruff.lint.mccabe]
max-complexity = 10

[tool.ruff.lint.pylint]
max-args = 5
max-returns = 6
max-branches = 12
max-statements = 40
max-public-methods = 15

[tool.pyright]
typeCheckingMode = "standard"
strict = ["src"]
```

### ESLint config (flat)

```js
{
  // Global ceilings. No per-file exceptions; lower them, never raise them.
  files: ["**/*.{ts,tsx}"],
  rules: {
    complexity: ["error", 10],
    "max-lines-per-function": ["error", { max: 60, skipBlankLines: true, skipComments: true }],
    "max-params": ["error", 4],
    "max-depth": ["error", 4],
    "max-classes-per-file": ["error", 1],
  },
}
```

### File-size script

`scripts/check_file_size.py`: fails when a hand-written file passes the cap.

```python
import sys
from pathlib import Path

SOURCE_MAX = 500
TEST_MAX = 800
SUFFIXES = {".py", ".ts", ".tsx", ".js", ".mjs"}
# Generated or vendored paths only, each with a reason. Never hand-written code.
SKIP_DIRS = {".git", ".venv", "node_modules", "dist", "coverage"}


def is_test(path: str) -> bool:
    return path.startswith(("tests/", "e2e/")) or ".test." in path or ".spec." in path


def main() -> int:
    failures = []
    for file in sorted(Path().rglob("*")):
        if file.suffix not in SUFFIXES or SKIP_DIRS & set(file.parts) or not file.is_file():
            continue
        lines = len(file.read_text(encoding="utf-8").splitlines())
        limit = TEST_MAX if is_test(file.as_posix()) else SOURCE_MAX
        if lines > limit:
            failures.append(f"{file.as_posix()}: {lines} lines, ceiling {limit}")
    if failures:
        print("Files over the size ceiling; split them:\n" + "\n".join(failures))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### Ceilings-only-go-down script

`scripts/check_ceilings.py`: compares the tree with the merge base. Fails when
a ceiling value rose or a diff adds a silencer for a shape rule. List every file
that holds a ceiling in `CEILINGS`, with a regex that captures `name` and value.

```python
import re
import subprocess
import sys
from pathlib import Path

CEILINGS = {
    "pyproject.toml": re.compile(
        r"^(max-(?:complexity|args|returns|branches|statements|public-methods))\s*=\s*(\d+)", re.M
    ),
    "eslint.config.js": re.compile(r"(complexity|max-[\w-]+)\W+(\d+)"),
    "biome.json": re.compile(r'"(maxAllowedComplexity)"\s*:\s*(\d+)'),
    "scripts/check_file_size.py": re.compile(r"^(SOURCE_MAX|TEST_MAX)\s*=\s*(\d+)", re.M),
}
# Built from parts so this file's own definition is not read as a silencer.
_RULES = r"(?:C901|PLR\w+|complexity|max-[\w-]+|noExcessive\w+)"
SILENCER = re.compile(
    rf"^\+.*(?:{'no' + 'qa'}:?[\w, ]*{_RULES}|(?:{'eslint' + '-disable'}|{'biome' + '-ignore'})[^\n]*{_RULES})",
    re.M,
)


def git(*args: str) -> str:
    done = subprocess.run(["git", *args], capture_output=True, text=True, check=False)
    return done.stdout if done.returncode == 0 else ""


def values(text: str, pattern: re.Pattern[str]) -> dict[str, int]:
    return {f"{k}#{i}": int(v) for i, (k, v) in enumerate(pattern.findall(text))}


def main() -> int:
    base = sys.argv[1] if len(sys.argv) > 1 else git("merge-base", "HEAD", "origin/main").strip()
    if not base:
        print("check_ceilings: no origin/main to compare with; skipped")
        return 0
    problems = []
    for path, pattern in CEILINGS.items():
        if not Path(path).is_file():
            continue
        before = values(git("show", f"{base}:{path}"), pattern)
        after = values(Path(path).read_text(encoding="utf-8"), pattern)
        problems += [
            f"{path}: {key.split('#')[0]} raised {before[key]} -> {after[key]}"
            for key in before.keys() & after.keys()
            if after[key] > before[key]
        ]
    problems += [f"new silencer: {m[1:].strip()}" for m in SILENCER.findall(git("diff", base, "--unified=0"))]
    if problems:
        print("Ceilings only go down; split the code instead:\n" + "\n".join(problems))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### One recipe, three callers

```make
lint:
	uv run ruff check . && uv run ruff format --check .
	python3 scripts/check_file_size.py
	python3 scripts/check_ceilings.py
	uv run pyright
```

Add the stack's own lines (`npm run lint`, `tsc --noEmit`, `biome check`). CI,
the git hook, and the Claude `Stop` hook all call this one recipe.

### Claude Code hooks

`.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      { "matcher": "Edit|Write",
        "hooks": [{ "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/scripts/hooks/claude_hook.py\" post-edit", "timeout": 120 }] }
    ],
    "Stop": [
      { "hooks": [{ "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/scripts/hooks/claude_hook.py\" stop", "timeout": 600 }] }
    ]
  }
}
```

`scripts/hooks/claude_hook.py` takes `post-edit` or `stop` as its argument.
`post-edit` reads the edited path from the hook JSON on stdin, lints that one
file (ruff for `.py`, ESLint or Biome for `.ts`/`.tsx`), and runs
`check_file_size.py`. `stop` returns 0 when `stop_hook_active` is set (avoids a
loop), otherwise runs `just lint`. A failure prints the last 4,000 characters
to stderr and exits 2, which hands the output back to the agent to fix.

### Git pre-commit hook

`.githooks/pre-commit`:

```sh
#!/bin/sh
exec just lint
```

Install it with a `just hooks` recipe: `git config core.hooksPath .githooks`.

## Testing

- Prove the gate works once at scaffold time: add a function over the
  complexity ceiling and confirm `just lint` fails, then remove it.
- Prove `check_ceilings.py` works: raise a ceiling in a scratch branch and
  confirm it fails.

## Quality Gates

- The lint config selects the complexity, statement, argument, and
  public-method rules at or below the strict defaults (or the adoption
  baseline recorded in the TD).
- `just lint` runs the linter, formatter check, type check,
  `check_file_size.py`, and `check_ceilings.py`; CI runs the same recipe.
- The Claude `PostToolUse` and `Stop` hooks and the git pre-commit hook are
  committed and run that recipe.
- No ceiling was raised, and no `noqa`, `eslint-disable`, `biome-ignore`, or
  per-file ignore was added for a complexity, size, or parameter rule.
- No source file is over `SOURCE_MAX` and no test file over `TEST_MAX`.
- No type-checker ignore list of modules.
