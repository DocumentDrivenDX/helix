---
title: "Developer Guide"
linkTitle: "Developer Guide"
slug: developer-guide
activity: "Build"
artifactRole: "supporting"
weight: 90
generated: true
---

## Purpose

Help an unfamiliar developer run the project, locate a change, and verify it.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: helix.developer-guide
  type: developer-guide
  status: draft
  authoring:
    home: repo
---
# HELIX developer guide

## Start here

Your first contribution should leave the canonical content, generated outputs,
and validation consistent. Read the [solution overview](https://github.com/DocumentDrivenDX/helix/blob/main/docs/helix/02-design/solution-overview.md)
and [walkthrough](https://github.com/DocumentDrivenDX/helix/blob/main/docs/helix/02-design/architecture-walkthrough.md) first.
[AGENTS.md](https://github.com/DocumentDrivenDX/helix/blob/main/AGENTS.md) governs repository work;
[Architecture](https://github.com/DocumentDrivenDX/helix/blob/main/docs/helix/02-design/architecture.md) defines system boundaries.

## Prerequisites and setup

Clone the repository and run commands from its root. Use Git, Bash, Python 3.10+
with PyYAML, and `just` for the core content workflow. The full suite also uses
Node with `pptxgenjs`, LibreOffice, and `pdftoppm` for deck rendering; Hugo and
Node support website work. Individual validation scripts expose further lane
requirements; inspect their failure output before claiming full validation.
Host installation is separate: follow [docs/install/README.md](https://github.com/DocumentDrivenDX/helix/blob/main/docs/install/README.md).
For Claude Code, `claude --plugin-dir /path/to/helix` loads the checkout.
Project-local skill symlinks also point at the source skill.

```bash
git clone https://github.com/DocumentDrivenDX/helix.git
cd helix
python3 -c 'import yaml; print("PyYAML available")'
bash tests/validate-skills.sh
```

Success means the skills validator exits zero. This checks content and packaging
contracts; it does not prove that a live model will follow every instruction.
No model credentials are needed for deterministic repository checks.
If `import yaml` fails, install PyYAML in your chosen Python environment and
repeat the check. With `uv` available, `uv run --with pyyaml python3` supplies
that dependency; run the commands below in the same environment, for example
`uv run --with pyyaml just test`. Dependency installation needs package access.
The deck lane reports a skip when its rendering tools are unavailable; retain
that message rather than treating it as rendered evidence.

## Repository map

| Change target | Canonical source | Derived outputs or checks |
|---|---|---|
| Public routing | `skills/helix/SKILL.md` | `tests/validate-skills.sh` |
| Mode behavior | `workflows/modes/`, `workflows/actions/` | `tests/validate-actions.sh` |
| Artifact type | `workflows/activities/*/artifacts/<type>/` | Graph, reference pages, packaged references |
| HELIX's own documents | `docs/helix/` | Published artifact pages |
| Concerns | `workflows/concerns/` | Reference pages and concern-specific tests |
| Packaging | `scripts/build-plugin-package.sh`, `scripts/sync_references.py` | Temporary package validated by package tests |
| Microsite | `docs/website/`, `website/` | Hugo build; generated pages come from scripts |

Generated package references belong in package output, not in source
`skills/helix/references/`. Preserve existing document frontmatter when editing.

## First contribution

1. Pick one confusing instruction in an artifact type you understand. Read its
   `template.md`, `prompt.md`, `meta.yml`, and `example.md` together.
2. Make the instruction concrete and update its example to demonstrate it.
3. Run `python3 scripts/helix_validate_artifact_meta.py` and
   `bash tests/validate-skills.sh`; success is exit zero from both.
4. Inspect the diff for changed meaning, broken paths, and generated drift.
5. Run `just test` and `git diff --check` before submitting; retain any failure
   output and distinguish missing tools from content regressions.

A small wording correction needs no live agent run. A routing behavior change
needs scenario evidence appropriate to the changed contract.

## Common change recipes

### Add or change an artifact type

Keep all four type files consistent. Required sections in `meta.yml` must match
template headings. Define the artifact's authority and explain when it is useful.
For relationship or metadata changes, regenerate the graph:

```bash
python3 scripts/generate_graph.py
python3 scripts/generate-reference.py
python3 scripts/helix_validate_artifact_meta.py
bash tests/validate-skills.sh
```

Review generated changes before staging. A new type needs a concrete example,
not an unfilled copy of the template.

### Change project documentation

Edit the instance under `docs/helix/`, preserving its identity and unknown
frontmatter. Publish updated instances with `python3 scripts/publish-artifacts.py`.
The overview and this guide explain existing authority; structural decisions
belong in Architecture or an architecture decision record (ADR).

### Change routing or packaging

Read `skills/helix/SKILL.md` and the relevant mode contract together. Keep the
single public skill and runtime-neutral workflow content. Run skills, plugin
package, and catalog-resolution validators, then the full gate. Build packages
with `scripts/build-plugin-package.sh`; do not hand-edit generated references.

## Debugging and verification

| Symptom | First check | Next action |
|---|---|---|
| Catalog graph differs | `python3 scripts/generate_graph.py` | Inspect source metadata and generated diff |
| Type sections fail validation | `python3 scripts/helix_validate_artifact_meta.py` | Compare metadata with template headings |
| Packaged behavior differs | `bash tests/validate-plugin-package.sh` | Check generated references against canonical workflows |
| Catalog cannot resolve | `bash tests/validate-plugin-catalog-resolution.sh` | Inspect the skill's catalog fall-through rules |
| Website links look wrong | Local URL includes `/helix/` | Use `bash website/scripts/serve-local.sh` |
| Full gate stops | First failing command in `just test` | Resolve that lane's prerequisite or content failure; rerun it |

Required repository gate: `just test` and `git diff --check`. Pre-commit hooks
remain enabled. Deployment and live host integration have separate install
runbooks; deterministic checks do not prove production or model behavior.

## Maintenance and feedback

Contributors maintain this guide with changes to prerequisites, paths,
generation steps, and validation gates. Before calling onboarding proven,
have an unfamiliar developer follow setup and make the first contribution;
record where they needed help. The current pilot is repository-checked only.
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Build</strong></a> — Implement against the specs and tests. Capture the implementation plan that scopes the work.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/04-build/developer-guide.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Developer Guide authoring prompt&#10;&#10;Help an unfamiliar developer run the project, locate a change, and verify it.&#10;Read the project&#x27;s contributor instructions, build definitions, tests, and&#10;installation guidance before writing commands. State working directory,&#10;prerequisites, supported environment evidence, expected results, and recovery&#10;steps. Separate local deterministic checks from live integrations and deployment.&#10;Map canonical sources to generated outputs and regeneration commands. Provide a&#10;small realistic first contribution plus common change recipes tied to checks.&#10;Link to the solution overview, architecture walkthroughs, and operational runbooks.&#10;Keep architectural decisions in Architecture/ADRs and incident response in runbooks.&#10;Do not claim onboarding is proven from a repository read or passing static tests.&#10;Record a newcomer trial separately: environment, task, observed result, help&#10;needed, and remaining blockers. Mark it pending until a real trial occurs.&#10;Name the maintainer role and update triggers. Verify paths and commands.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: developer-guide&#10;  authoring:&#10;    home: repo&#10;---&#10;&#10;# Developer Guide&#10;&#10;## Start here&#10;&#10;[First developer outcome, solution overview, walkthrough, and contributor-policy links.]&#10;&#10;## Prerequisites and setup&#10;&#10;[Supported environment evidence, prerequisites, working directory, commands, expected success output, and recovery for common failures.]&#10;&#10;## Repository map&#10;&#10;| Change target | Canonical source | Generated output / check |&#10;|---|---|---|&#10;| [Target] | [Path] | [Path or command] |&#10;&#10;## First contribution&#10;&#10;[A small real change, files to read/edit, focused checks, expected results, and review/submission path.]&#10;&#10;## Common change recipes&#10;&#10;[For each recurring change: edit location, dependent/generated files, regeneration command, and verification gate.]&#10;&#10;## Debugging and verification&#10;&#10;| Symptom | First check | Next action |&#10;|---|---|---|&#10;| [Failure] | [Concrete command or evidence] | [Recovery] |&#10;&#10;[Required full gate and limits of what it proves. Link operational runbooks.]&#10;&#10;## Maintenance and feedback&#10;&#10;[Maintainer role and update triggers. Record newcomer trial environment, task, result, help needed, and blockers, or explicitly mark the trial pending.]</code></pre></details></td></tr>
</tbody>
</table>
