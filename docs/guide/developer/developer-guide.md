<!-- helix:publish audience=developer page=developer-guide kind=how-to voice=onboarding existing=yes reviewed=2026-10-20/agent-sonnet/0aa16539e0c776e0 -->
<!-- helix:source docs/helix/02-design/solution-overview.md sha256:98c59b6843712495 -->
<!-- helix:source CONTRIBUTING.md sha256:d0027006597fad67 -->
<!-- helix:source justfile sha256:d3e5861049a16f1f -->
# HELIX developer guide

## Start here

Your first contribution should leave the canonical content, generated outputs,
and validation consistent. Read the [solution overview](../../helix/02-design/solution-overview.md)
and [walkthrough](../../helix/02-design/architecture-walkthrough.md) first.
[AGENTS.md](../../../AGENTS.md) governs repository work;
[Architecture](../../helix/02-design/architecture.md) defines system boundaries.

## Prerequisites and setup

Clone the repository and run commands from its root. Use Git, Bash, Python 3.11+
with PyYAML, `uv`, and `just` for the core content workflow. The full suite also renders
decks through documentor; `uv run --project tools/documentor documentor doctor` lists the Node, LibreOffice, and
`pdftoppm` it needs. Hugo and Node support website work.

Individual validation scripts expose further lane requirements. Inspect their
failure output before claiming full validation.

Host installation is separate: follow [docs/install/README.md](../../install/README.md).
For Claude Code, `claude --plugin-dir /path/to/helix` loads the checkout; in that
session, invoke a mode with `/helix <mode>`, for example `/helix align`.
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

Generated package references belong in package output, never in the skill's
source tree. Preserve existing document frontmatter when editing.

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
frontmatter. Publish updated instances with `uv run --project tools/documentor documentor record --root .`.
The overview and the developer guide explain existing authority; structural decisions
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
| Website links look wrong | Local URL includes `/helix/` | Use `bash website/scripts/serve-local.sh` (needs Hugo; serves `http://eitri:1315/helix/`) |
| Full gate stops | First failing command in `just test` | Resolve that lane's prerequisite or content failure; rerun it |

Required repository gate: `just test` and `git diff --check`. Pre-commit hooks
remain enabled. Deployment and live host integration have separate install
runbooks; deterministic checks do not prove production or model behavior.
