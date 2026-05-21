---
title: Using HELIX with DDx
weight: 2
prev: /use/getting-started
next: /use/workflow
---

DDx is the reference runtime integration for HELIX. Use it when you want HELIX's
artifact discipline connected to a dependency-aware tracker, an agent harness,
and recorded execution evidence.

DDx is not required to use HELIX. It is one runtime that knows how to execute
HELIX-shaped work.

## Install the Reference Runtime

Install DDx, then install the HELIX package into DDx:

```bash
curl -fsSL https://raw.githubusercontent.com/DocumentDrivenDX/ddx/main/install.sh | bash
ddx install helix
```

You will also need an agent CLI supported by your local DDx setup, such as
Claude Code or Codex.

## Shape Work

Start by asking your agent to frame your intent into governed artifacts and
work items. In an agent session with HELIX skills installed:

```text
Use /helix-input to frame "Build a REST API for managing bookmarks".
```

That skill turns sparse intent into Markdown artifacts plus tracked work that
DDx can claim and execute.

You can also create DDx work items directly:

```bash
ddx bead create "Add OAuth login flow" --type task \
  --labels helix,activity:build --set spec-id=FEAT-001 \
  --acceptance "OAuth login redirects to provider and returns a session token"
```

## Execute with DDx

Once the artifacts and work items are ready, use DDx to drain the queue:

```bash
ddx work
```

DDx claims ready work, dispatches the configured agent harness, records
execution evidence, and closes completed items.

For one bounded pass:

```bash
ddx work --once
```

## Interactive Agent Use

In an agent session with HELIX skills installed, you can steer DDx-backed work
with natural language:

```text
Use HELIX to frame OAuth support, create the governed work items, and then run
one bounded DDx execution pass.
```

Or invoke integration commands directly if your agent exposes them:

| Command | What it does in the DDx integration |
|---------|-------------------------------------|
| `/helix-input "build a bookmarks API"` | Shape intent into governed artifacts and DDx work items |
| `/helix-align` | Run a top-down alignment review over the artifact stack |
| `/helix-review` | Fresh-eyes review of recent work |
| `/helix-frame` | Create or refine product vision, PRD, feature specs |
| `/helix-evolve "requirement"` | Thread a change through the artifact stack |

## Related Reading

- Start with the runtime-neutral [Getting Started](../getting-started/) guide.
- Browse the [artifact-type catalog](/artifact-types/) for HELIX templates.
- Review the projected [HELIX self-artifacts](/artifacts/) for a worked example.
