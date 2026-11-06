# Design Plan: documentor writes and evaluates the written pages (ADR-003)

**Date**: 2026-10-20
**Status**: CONVERGED
**Refinement Rounds**: 1

## Problem Statement

`documentor build` makes the generated pages and lists the written ones; a person then has to open
a HELIX session to write them. A developer should get the whole guide from one command:
`documentor init --write && documentor build --write`. ADR-003 decides that documentor calls the
agent; this plan says how.

## Requirements

### Functional

- `documentor write [PAGE]` writes every written page in state missing or stale, or the one page
  named (`audience/id` or its path), and evaluates every page left unreviewed.
- `documentor build --write` regenerates, then writes, then checks and builds the site.
- The writer gets the page's audience, kind, title, task, outline, budget, source hints, voice
  limits and moves, the shared phrase lists, the other pages' paths (for links), and the
  project's handling rules. On a stale page it also gets the current text and the sources that
  moved, and is told to change only what they moved.
- The writer answers with `helix:gap` lines, `helix:source` lines, then the Markdown body.
  documentor writes the header, stamps the sources, and checks the page; blocking or `prose.*`
  findings go back to the writer once.
- The evaluator answers `VERDICT: pass` or `VERDICT: fail` and its reasons. A pass is stamped
  through `review`; a fail goes back to the writer once, then to one more evaluation.
- `review` refuses `--by` equal to the page's `written=`.
- `status` shows a page's gaps.

### Non-Functional

- No new dependency; the tests run with a fake agent and no network.
- A rerun on a current guide makes no agent call.

### Constraints

- `check` is unchanged and needs no agent (R-4).

## Architecture Decisions

### Decision 1: how the agent is called

- **Question**: SDK, HTTP, or a command?
- **Alternatives**: the Anthropic SDK (a dependency, one vendor); raw HTTP (no tools for reading
  the repository); a command (any agent, testable with a script).
- **Chosen**: a command, prompt on stdin, answer on stdout, `{model}` substituted. Default
  `claude -p --model {model} --allowedTools Read,Glob,Grep --output-format text`, run from the
  root. Overridden by `publish.agent.command` or `DOCUMENTOR_AGENT`.
- **Rationale**: ADR-003.

### Decision 2: who chooses the sources

- **Question**: the catalog's hints are abstract (`artifact: architecture`, `code: build
  definitions`); a page's header needs paths.
- **Chosen**: the writer resolves the hints to paths with its read tools and names them; documentor
  drops any that do not exist and refuses a page with none.
- **Rationale**: the agent already reads the files to write about them; a resolver in documentor
  would guess worse.

### Decision 3: models

- **Chosen**: writer `opus`, evaluator `sonnet` by default; `--model`, `--reviewer-model`, and
  `publish.agent.writer` / `.reviewer`.

## Interface Contracts

```text
documentor write [PAGE] [--root DIR] [--model M] [--reviewer-model M] [--agent CMD] [--dry-run]
documentor build --write [same agent flags] [--no-site]
```

`.helix.yml`:

```yaml
publish:
  agent: {command: "claude -p --model {model} ...", writer: opus, reviewer: sonnet}
```

Header of a written page:

```text
<!-- helix:publish audience=developer page=index kind=explanation voice=onboarding budget=800 written=agent-opus -->
<!-- helix:gap artifact:architecture -->
<!-- helix:source src/documentor/cli.py sha256:... -->
```

Gap lines sit before the source lines, so they are outside the body the evaluation vouches for.

## Error Handling

- Agent command missing or non-zero exit: report it, skip the page, continue, exit 1 at the end.
- An answer with no body or no existing source: one retry with the reason, then skip.
- `--dry-run` prints each prompt and calls nothing.

## Security

- The writer and evaluator get read tools only; documentor writes the files.
- Handling patterns are in the prompt and enforced by the check before any stamp.

## Test Strategy

- **Integration** (`tests/validate-write.sh`): a fixture repository and a fake agent script that
  answers by prompt type. Covers: a missing page is written, stamped, checked, and reviewed by
  the reviewer model; a rerun calls nothing; a failing first answer is revised; an evaluator
  fail leaves the page unreviewed; gaps reach `status`; `review` refuses the writer;
  `--dry-run` calls nothing; `build --write` writes.
- Existing suites stay green.

## Implementation Plan

1. `lib.py`: `GAP` pattern; `PagePlan` carries outline and budget from the entry.
2. `write.py`: prompts, the agent call, answer parsing, write-check-revise, evaluate-revise.
3. `cli.py`: `write` command, `build --write`, agent flags; `review` refuses the writer; `assess`
   reports gaps.
4. Tests and `justfile`.
5. README "Use" section.
6. Run on documentor itself with the real agent.

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| The writer cites a busy file and the page goes stale on every edit | M | M | prompt: cite the file whose content the page states |
| The evaluator passes weak pages | M | M | different model, fresh context; a person's `review` still overrides |
| The answer format drifts | L | M | strict parse; one retry with the reason |

## Governing Artifacts

ADR-001, ADR-003; PRD R-4, R-9, R-10.
