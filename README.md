# HELIX

A supervisory autopilot for AI-assisted software delivery. HELIX enforces
specification-first, test-first discipline through structured phases — framing
the problem, designing the solution, writing failing tests, building the
implementation, and iterating with real feedback. Humans set direction and make
judgment calls; AI agents do the heavy lifting under HELIX's supervision.

HELIX is built on [DDx](https://documentdrivendx.github.io/ddx/) (Document-Driven
Development eXperience), a local-first platform for AI-assisted development. DDx
provides the foundation that HELIX runs on: a document library for governing
artifacts, a work tracker for issue management, an agent harness for dispatching
AI models, and an execution engine for recording what happened. HELIX adds the
methodology layer — the phases, the authority order, the bounded execution loop,
and the skills that turn governing documents into working software.

**[Documentation](https://documentdrivendx.github.io/helix/)** · **[Demo Reels](https://documentdrivendx.github.io/helix/docs/demos/)** · **[Getting Started](https://documentdrivendx.github.io/helix/docs/getting-started/)**

![HELIX Quickstart Demo](docs/demos/helix-quickstart/recordings/helix-quickstart.gif)

## Install

First, install [DDx](https://documentdrivendx.github.io/ddx/):

```bash
curl -fsSL https://raw.githubusercontent.com/DocumentDrivenDX/ddx/main/install.sh | bash
```

Then install HELIX:

```bash
ddx install helix
```

You'll also need an AI agent CLI — either `claude` (Claude Code) or `codex`
(OpenAI Codex) — plus `bash`, `jq`, and `git`.

## Quick Start

```bash
cd your-project
ddx init                    # Set up document library and tracker
helix frame                 # Create vision, PRD, feature specs
helix run                   # Autopilot: build → review → check → repeat
```

Or run individual commands:

```bash
helix build                 # One bounded build pass
helix check                 # What should happen next?
helix design auth           # Design a subsystem
helix review                # Fresh-eyes review
helix status                # Queue health and lifecycle snapshot
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
- Tracker: `ddx bead --help` (conventions in DDx FEAT-004)
- [Reference Card](workflows/REFERENCE.md)

## Tracker

HELIX uses a built-in file-backed tracker for execution tracking. Canonical
issues live in `.ddx/beads.jsonl`. Run `ddx bead` to manage issues,
`ddx bead import` to pull compatible JSONL into the canonical store, and
`ddx bead export` to write JSONL for interop or recovery.

## Documentation

- [DDx — Document-Driven Development Experience](workflows/DDX.md)
- [Workflow Contract](workflows/README.md)
- [Quality Ratchets](workflows/ratchets.md)
- [Conventions](workflows/conventions.md)

## DDx Platform

HELIX is built on [DDx](https://documentdrivendx.github.io/ddx/) — the
local-first platform for AI-assisted development. DDx provides the document
library, work tracker, agent harness, and execution engine. HELIX provides the
methodology, phases, authority order, and supervisory skills.

See [DDx Methodology](workflows/DDX.md) for the artifact graph, authority
hierarchy, evolution model, and agent context model.
