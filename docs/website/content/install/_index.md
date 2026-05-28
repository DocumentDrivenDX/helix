---
title: Install HELIX
weight: 1
---

HELIX is a methodology, an artifact-type catalog, and a single routing skill.
It is not a CLI, a tracker, or a runtime. To use HELIX you make its content
discoverable from the runtime you already use. Pick the guide that matches your
environment.

## Minimal runtime contract

A HELIX-compliant runtime can:

1. **Read markdown files** from the project's filesystem.
2. **Write markdown files** to the project's filesystem.
3. **Search files** by path or pattern across the project.
4. **Optionally execute a shell command** for verification or build/run modes.

That is the full contract. HELIX assumes nothing else — no tracker, no queue,
no execution loop, no IDE integration, no language toolchain. Items 1–3 are
required; item 4 is optional and only some routes (`build`, `run`, `commit`,
`release`) make use of it.

## Per-runtime install guides

Each guide is self-contained: file layout, install steps, invocation, and
verification for one runtime. Pick the one that matches your environment;
install more than one if you use more than one.

{{< cards >}}
  {{< card link="/use/claude-code-recipe" title="Claude Code" subtitle="Install HELIX as a Claude Code skill, user-global or per-repo. Supports every HELIX route including build and run." icon="code" >}}
  {{< card link="/use/codex-recipe" title="Codex CLI + Copilot" subtitle="Covers the OpenAI Codex CLI (AGENTS.md discovery) and GitHub Copilot Workspace (editor-scoped instructions)." icon="chip" >}}
  {{< card link="/use/databricks-recipe" title="Databricks Code Genie" subtitle="Upload the skill bundle to workspace storage and register it as a Genie skill. Shared across the workspace." icon="database" >}}
{{< /cards >}}

## Source of truth

The runtime install guides are packaging notes. The normative HELIX content
lives in two places:

- **[Skills](/skills)** — the single routing skill with one public entry point
  (`helix`), one routing table, and one set of per-mode workflow contracts.
  There are no separate public `helix-*` skills.
- **[Artifact types](/artifact-types)** — the artifact-type catalog and
  methodology specification. Templates, prompts, quality criteria, and examples
  for every artifact type.

When a per-runtime guide and the skill or catalog disagree, the skill and
catalog win.

## No-fork policy

The per-runtime guides exist so adopters can install HELIX. They do not exist
to localize, dialect, or rewrite the methodology.

- The normative skill body lives in `skills/helix/SKILL.md` and nowhere else.
- The artifact catalog lives in `workflows/` and nowhere else.
- If a runtime requires a shim — a manifest, wrapper, or packaging document —
  that shim lives inside the per-runtime guide, clearly marked as
  runtime-specific. It does not get pushed back into `skills/` or `workflows/`.

Three install paths, one HELIX.
