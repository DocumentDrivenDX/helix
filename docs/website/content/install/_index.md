---
title: Install HELIX
weight: 1
---

Pick the install guide for the tool that will run HELIX, such as Claude Code,
Codex, DDx, or Databricks. For what HELIX is, see [the thesis](/why/the-thesis/).

## Minimal runtime contract

A HELIX-compliant runtime can:

1. **Read markdown files** from the project's filesystem.
2. **Write markdown files** to the project's filesystem.
3. **Search files** by path or pattern across the project.
4. **Optionally execute a shell command** for runtime-owned verification.

That is the full contract. HELIX assumes nothing else: no tracker, no queue,
no execution loop, no IDE integration, no language toolchain. Items 1 through 3
<!-- vale Helix.PassiveVoice = NO -->
are required; item 4 is optional and belongs to the runtime, not the HELIX
<!-- vale Helix.PassiveVoice = YES -->
methodology contract.

## Per-runtime install guides

Each guide names the file layout, install steps, invocation, and verification
for one runtime. Pick the one that matches your environment; install more than
one if you use more than one.

{{< cards >}}
  {{< card link="../use/claude-code-recipe" title="Claude Code" subtitle="Install HELIX as a Claude Code plugin through the marketplace or a local plugin directory." icon="code" >}}
  {{< card link="../use/codex-recipe" title="Codex CLI + Copilot" subtitle="Covers the OpenAI Codex CLI plugin path and GitHub Copilot Workspace editor-scoped instructions." icon="chip" >}}
  {{< card link="../use/databricks-recipe" title="Databricks Code Genie" subtitle="Upload the skill bundle to workspace storage and register it as a Genie skill. Shared across the workspace." icon="database" >}}
{{< /cards >}}

## Source of truth

Runtime install guides are packaging notes. The normative HELIX content lives
in two places:

- **[Skills](/skills)**: the HELIX skill with one public entry point (`helix`),
  one routing table, and one set of per-mode workflow contracts.
  There are no separate public `helix-*` skills.
- **[Artifact types](/artifact-types)**: HELIX document patterns, including
  templates, prompts, quality criteria, and examples for PRDs, ADRs, test plans,
  runbooks, and related documents.

When a per-runtime guide and the skill or catalog disagree, the skill and
catalog govern.

## No-fork policy

The per-runtime guides exist so adopters can install HELIX. They do not exist
to localize, dialect, or rewrite the methodology.

- The normative skill body lives in `skills/helix/SKILL.md` and nowhere else.
- The artifact-type catalog lives in `workflows/` and nowhere else.
- If a runtime requires a shim (a manifest, wrapper, or packaging document),
  that shim lives inside the per-runtime guide, explicitly marked as
  runtime-specific. It does not get pushed back into `skills/` or `workflows/`.

Three runtime guides, one HELIX source.
