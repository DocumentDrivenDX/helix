# HELIX

A document discipline for AI-assisted software development. HELIX is a
methodology and artifact catalog: templates for the documents your project
needs at every level — vision, requirements, design, tests, deploy, metrics —
plus a single alignment skill that keeps them in sync as the work moves.

HELIX runs on runtimes. [DDx](https://documentdrivendx.github.io/ddx/) is
the reference runtime: it owns the agent runtime, tracker, and execution loop
that turn aligned artifacts into code. Claude Code, Codex CLI, GitHub Copilot,
and Databricks Genie are target runtimes. HELIX itself is content (templates,
prompts, methodology spec) plus the alignment skill. HELIX ships no checkout
CLI; alignment, queue control, tracker behavior, and the broader historical
command surface belong to runtimes like DDx.

**[Documentation](https://documentdrivendx.github.io/helix/)** · **[Demo Reels](https://documentdrivendx.github.io/helix/demos/)** · **[Getting Started](https://documentdrivendx.github.io/helix/use/getting-started/)**

![HELIX Quickstart Demo](docs/demos/helix-quickstart/recordings/helix-quickstart.gif)

## Local Microsite Review

Use the standard startup script when reviewing the Hugo site locally:

```bash
bash website/scripts/serve-local.sh
```

The local review site lives at `http://eitri:1315/helix/`. Keep `/helix` in
review URLs; root paths such as `http://eitri:1315/artifact-types/...` are not
the local site shape and should be treated as invalid.

Regenerate published site content after changing artifact types, project
artifacts, or resource summaries:

```bash
python3 scripts/generate-reference.py
python3 scripts/publish-artifacts.py
python3 scripts/publish-resources.py
```

## The Seven Activities

HELIX names seven kinds of work in software development:

| Activity | Owns artifact types like… |
|---|---|
| **Discover** | Product vision, business case, competitive analysis, opportunity canvas |
| **Frame** | PRD, feature specifications, user stories, principles, cross-cutting requirements |
| **Design** | Architecture, ADRs, solution designs, technical designs, contracts |
| **Test** | Test plans, story test plans, security tests |
| **Build** | Implementation plan, executed work in the runtime's tracker |
| **Deploy** | Runbook, deployment checklist, monitoring setup, release notes |
| **Iterate** | Metric definitions, metrics dashboard, improvement backlog |

Activities are connected by an **artifact authority hierarchy**: vision governs PRD,
PRD governs features, features govern designs, designs govern tests, tests
govern code. When two artifacts disagree, the higher-authority artifact governs. Work moves
between activities in every direction: a failing test reveals a missing
requirement; a production metric revises the PRD; a vision update propagates
downstream.

## Install

HELIX runs on several runtimes. Pick the one you already use; each install guide
under [`docs/install/`](docs/install/) has the full procedure.

### DDx Runtime

The fastest path to running HELIX is the DDx runtime.

First, install [DDx](https://documentdrivendx.github.io/ddx/):

```bash
curl -fsSL https://raw.githubusercontent.com/DocumentDrivenDX/ddx/main/install.sh | bash
```

Then install HELIX as a DDx plugin:

```bash
ddx install helix
```

This adds HELIX's artifact-type catalog and alignment skill to your DDx
project. You'll also want an agent runtime —
[Claude Code](https://claude.ai/claude-code) or `codex` — plus `git`.

### Claude Code (plugin)

The HELIX repo is itself a Claude Code plugin. Inside a Claude Code session, add
the marketplace and install the plugin:

```text
/plugin marketplace add https://github.com/DocumentDrivenDX/helix
/plugin install helix@helix
```

For automation or a Dockerfile, use the scripted CLI equivalent:

```bash
claude plugin marketplace add https://github.com/DocumentDrivenDX/helix
claude plugin install helix@helix --scope user -y
```

Full procedure: [`docs/install/claude-code.md`](docs/install/claude-code.md).

### Codex (plugin)

HELIX installs into Codex as a plugin from the HELIX marketplace:

```bash
codex plugin marketplace add DocumentDrivenDX/helix
codex plugin add helix@helix
```

The plugin carries the same agentskills.io-compliant routing skill and
artifact catalog. Full procedure, including the Skills CLI and filesystem-copy
fallbacks: [`docs/install/codex.md`](docs/install/codex.md).

### Databricks Genie

From inside a Databricks notebook, the kernel already carries workspace
credentials. Run this in a Python cell:

```python
%pip install --quiet databricks-sdk PyYAML

import urllib.request, runpy
urllib.request.urlretrieve(
    "https://github.com/DocumentDrivenDX/helix/releases/latest/download/genie-install",
    "/tmp/genie_install.py",
)
g = runpy.run_path("/tmp/genie_install.py")
g["install"]()                # user-scoped; g["install"](shared=True) for workspace-wide
```

From a dev box or CI, set `DATABRICKS_HOST` + `DATABRICKS_TOKEN` (or
`DATABRICKS_PROFILE`) and run the [`genie-install`](https://github.com/DocumentDrivenDX/helix/releases/latest/download/genie-install)
release asset directly. Full procedure:
[`docs/install/databricks-genie.md`](docs/install/databricks-genie.md).

## Quick Start

Shape intent into governed work, then let DDx drain the ready queue:

```bash
/helix input "Build a REST API for managing bookmarks"
ddx work
```

The first slash command invokes the HELIX skill against your project's
artifacts, computes the artifact changes required by the new intent, and
emits work items in the DDx tracker. The second runs DDx's bounded execution
loop, dispatching agents to drain the queue. As work happens, the alignment
skill keeps the governing artifacts in sync.

Inside a Claude Code session, HELIX is available through a single skill that
routes to the appropriate mode:

| Command | What it does |
|---|---|
| `/helix input "build a bookmarks API"` | Shape intent into governed work items |
| `/helix align` | Reconcile the artifact tree top-down; emit a plan |
| `/helix frame` | Create or refine vision, PRD, feature specs |
| `/helix design auth` | Iteratively design a subsystem |
| `/helix evolve "add OAuth"` | Thread a new requirement through the artifacts |
| `/helix review` | Fresh-eyes review of recent work |

## Where the Artifacts Live

HELIX project artifacts live under `docs/helix/`:

```
docs/helix/
├── 00-discover/    # Vision, business case, competitive analysis
├── 01-frame/       # PRD, feature specs, user stories
├── 02-design/      # Architecture, ADRs, solution designs, technical designs
├── 03-test/        # Test plans
├── 04-build/       # Implementation plans, executed work evidence
├── 05-deploy/      # Runbooks, monitoring, release notes
└── 06-iterate/     # Metrics, improvement backlog, alignment reviews
```

Numeric prefixes are a reading-order convention. They do not imply that
activities run in sequence — they don't.

## Where to Read Next

- [The Thesis](https://documentdrivendx.github.io/helix/why/the-thesis/) — what HELIX is and what it's for
- [Activities](https://documentdrivendx.github.io/helix/reference/glossary/activities/) — the seven kinds of work, with examples
- [Artifact Types](https://documentdrivendx.github.io/helix/artifact-types/) — the catalog of templates and prompts
- [Artifacts](https://documentdrivendx.github.io/helix/artifacts/) — this project's own governing documents, as a worked example
- [Workflow](https://documentdrivendx.github.io/helix/use/workflow/) — how the alignment loop runs

## DDx as Runtime

[DDx](https://documentdrivendx.github.io/ddx/) is where execution lives. DDx
owns the work tracker (beads), agent dispatch harness, execution-evidence
store, document graph, and queue-drain loop. HELIX carries the methodology,
artifact catalog, and alignment skill that run on top.

The split is intentional: HELIX is portable methodology + content. DDx is one
runtime that knows how to run that content. Other runtimes can run the
same content with their own per-runtime packages.
