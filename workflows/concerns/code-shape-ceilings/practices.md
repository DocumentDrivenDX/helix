# Practices: Code Shape Ceilings

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
