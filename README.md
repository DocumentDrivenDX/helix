# HELIX

A test-driven development workflow for AI-assisted software development.

HELIX enforces specification-first, test-first discipline through a structured
phase approach where tests are written BEFORE implementation. Human creativity
and AI capabilities collaborate throughout, with tests serving as the contract
between design and implementation.

## Quick Start

```bash
# Install skills and CLI
scripts/install-local-skills.sh

# Run the execution loop
helix run --agent claude

# Or run individual commands
helix implement
helix check
helix plan auth
helix experiment --close
```

## Phases

0. **Discover** (optional) — Validate the opportunity
1. **Frame** — Define the problem and establish context
2. **Design** — Architect the solution approach
3. **Test** — Write failing tests that define behavior
4. **Build** — Implement code to make tests pass
5. **Deploy** — Release to production with monitoring
6. **Iterate** — Learn and improve for the next cycle

## CLI Commands

| Command | Purpose |
|---------|---------|
| `helix run` | Loop: implement ready issues, check, decide, repeat |
| `helix implement [issue]` | Execute one ready issue end-to-end |
| `helix check [scope]` | Decide next action (IMPLEMENT/ALIGN/BACKFILL/WAIT/STOP) |
| `helix align [scope]` | Top-down reconciliation review |
| `helix backfill [scope]` | Reconstruct missing HELIX docs |
| `helix plan [scope]` | Create design document through iterative refinement |
| `helix polish [scope]` | Refine issues before implementation |
| `helix next` | Show recommended next issue |
| `helix review [scope]` | Fresh-eyes post-implementation review |
| `helix experiment [issue]` | One metric-optimization iteration |

## Skills

HELIX publishes its agent-compatible skill surface from the repo at
`./.agents/skills` and installs those same skills into the canonical user path
`~/.agents/skills`.

Temporary compatibility mirror:
- `~/.claude/skills`

Installed skill set:

- `helix-run` <-> `helix run`
- `helix-implement` <-> `helix implement`
- `helix-check` <-> `helix check`
- `helix-align` <-> `helix align`
- `helix-backfill` <-> `helix backfill`
- `helix-plan` <-> `helix plan`
- `helix-polish` <-> `helix polish`
- `helix-next` <-> `helix next`
- `helix-review` <-> `helix review`
- `helix-experiment` <-> `helix experiment`

The contract is strict: public skill names are `helix-<command>` and must
mirror the CLI subcommand exactly.

The `skills/` tree remains the implementation source for skill content and
shared references. The project-level package surface that agents should consume
is `./.agents/skills`.

Required skill metadata:

- every published `SKILL.md` must declare `name` and `description`
- skills whose mirrored CLI command accepts a trailing scope, selector, or goal
  must also declare `argument-hint`
- `name` must match the skill directory basename exactly

Deterministic validation:

```bash
bash tests/validate-skills.sh
```

This validator checks directory-name to skill-name alignment, required
frontmatter, and the canonical `.agents/skills -> skills/` symlink contract.

## Tracker

HELIX uses a built-in file-backed bead tracker for execution tracking.
Canonical issues live in `.helix/issues.jsonl`. Run `helix tracker` to manage
issues, `helix tracker import` to pull beads in from `bd`/`br` or JSONL, and
`helix tracker export` to write bead-compatible JSONL for interop.

## Documentation

- [Workflow Overview](workflows/README.md)
- [Execution Guide](workflows/EXECUTION.md)
- [Tracker Guide](workflows/TRACKER.md)
- [Reference Card](workflows/REFERENCE.md)
- [Quality Ratchets](workflows/ratchets.md)
- [Conventions](workflows/conventions.md)

## Origin

HELIX is the reference implementation of Document-Driven Development (DDx).
Originally developed in [ddx-library](https://github.com/easel/ddx-library),
it was extracted to its own repository to reflect the reality that HELIX is
the primary value and warrants its own identity.
