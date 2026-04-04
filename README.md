# HELIX

HELIX has two public layers:

- a portable Agent Skills package surface published at `./.agents/skills`
- a stricter HELIX workflow and CLI contract for planning, execution, and
  tracker-driven delivery

The workflow layer enforces specification-first, test-first discipline through
a structured phase approach where tests are written before implementation.
Humans and AI agents collaborate throughout, with tests serving as the
contract between design and implementation.

## Demo

![HELIX Quickstart Demo](docs/demos/helix-quickstart/recordings/helix-quickstart.gif)

## Quick Start

```bash
# Install skills and CLI
scripts/install-local-skills.sh

# Run the bounded execution loop
helix run

# Or run individual commands
helix build
helix check
helix design auth
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
| `helix build [issue]` | Execute one ready issue end-to-end |
| `helix check [scope]` | Decide next action (BUILD/DESIGN/ALIGN/BACKFILL/WAIT/STOP) |
| `helix align [scope]` | Top-down reconciliation review |
| `helix backfill [scope]` | Reconstruct missing HELIX docs |
| `helix design [scope]` | Create design document through iterative refinement |
| `helix status` | Show tracker health and queue summary |
| `helix evolve [requirement]` | Thread requirement through the artifact stack |
| `helix triage [title]` | Create well-structured tracker issues |
| `helix polish [scope]` | Refine issues before implementation |
| `helix next` | Show recommended next issue |
| `helix review [scope]` | Fresh-eyes post-implementation review |
| `helix experiment [issue]` | One metric-optimization iteration |

## Skills

HELIX publishes its portable skill surface from the repo at
`./.agents/skills` and installs those same skills into the canonical user path
`~/.agents/skills`.

Temporary compatibility mirror:
- `~/.claude/skills`

Installed skill set:

- `helix-run` <-> `helix run`
- `helix-build` <-> `helix build`
- `helix-check` <-> `helix check`
- `helix-align` <-> `helix align`
- `helix-backfill` <-> `helix backfill`
- `helix-design` <-> `helix design`
- `helix-polish` <-> `helix polish`
- `helix-next` <-> `helix next`
- `helix-review` <-> `helix review`
- `helix-experiment` <-> `helix experiment`
- `helix-evolve` <-> `helix evolve`
- `helix-triage` <-> `helix triage`

The contract is strict: public skill names are `helix-<command>` and must
mirror the CLI subcommand exactly.

The `skills/` tree remains the implementation source for skill content and
shared references. The project-level package surface that agent clients should
consume is `./.agents/skills`.

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

## Workflow Contract

The HELIX-specific operating contract lives in `workflows/` and covers:

- authority order and canonical documentation
- bounded actions such as `implement`, `check`, `align`, and `backfill`
- the built-in tracker and queue-control rules
- the `helix` wrapper CLI used to run those actions consistently

Start with:

- [Workflow Overview](workflows/README.md)
- [Execution Guide](workflows/EXECUTION.md)
- Tracker: `helix tracker --help` (conventions in DDx FEAT-004)
- [Reference Card](workflows/REFERENCE.md)

## Tracker

HELIX uses a built-in file-backed tracker for execution tracking. Canonical
issues live in `.helix/beads.jsonl`. Run `helix tracker` to manage issues,
`helix tracker import` to pull compatible JSONL into the canonical store, and
`helix tracker export` to write JSONL for interop or recovery.

## Documentation

- [DDx — Document-Driven Development Experience](workflows/DDX.md)
- [Workflow Contract](workflows/README.md)
- [Quality Ratchets](workflows/ratchets.md)
- [Conventions](workflows/conventions.md)

## Document-Driven Development Experience (DDx)

HELIX is the reference implementation of DDx — the tooling and methodology
layer that keeps governing documents current and uses them to drive AI agents
through software development.

See [DDx Methodology](workflows/DDX.md) for the artifact graph, authority
hierarchy, evolution model, and agent context model.

Originally developed in [ddx-library](https://github.com/easel/ddx-library),
HELIX was extracted to its own repository because it is the primary value:
DDx is the methodology, HELIX is the machine that runs it.
