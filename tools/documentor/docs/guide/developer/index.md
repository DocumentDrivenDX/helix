<!-- helix:publish audience=developer page=index kind=explanation voice=onboarding budget=800 written=agent-opus reviewed=2026-10-21/agent-sonnet/24723d03b99528a5 -->
<!-- helix:gap artifact:architecture -->
<!-- helix:source docs/helix/00-discover/product-vision.md sha256:53b51880ca06cad7 -->
<!-- helix:source docs/helix/02-design/adr/ADR-001-a-repository-guide-is-detected-generated-written-evaluated-and-checked.md#decision sha256:d3fd98aa3f21622b -->
<!-- helix:source src/documentor/cli.py sha256:0707cd738e9b6418 -->
<!-- helix:source src/documentor/lib.py sha256:093a891d0f8bcf48 -->
<!-- helix:source src/documentor/write.py sha256:2118376b2c167085 -->
<!-- helix:source src/documentor/record.py sha256:cecdf2712047484e -->
<!-- helix:source src/documentor/report.py sha256:0f48cfca412184a2 -->
<!-- helix:source src/documentor/theme.py sha256:7e38d9589c728f0b -->
<!-- helix:source src/documentor/deliverable/__init__.py sha256:ad9354803e0dd670 -->
<!-- helix:source src/documentor/catalog/ux-builder/README.md sha256:6b885638317975c7 -->
<!-- helix:source justfile sha256:33d64f77836eb9e1 -->
# Overview

## What it is

documentor is a Python command-line tool that turns a repository into a checked documentation guide for developers, operators, users, and data consumers. It implements the `guide` mode of HELIX. HELIX defines the audiences, page kinds, writing standard, and provenance header; documentor makes the deterministic parts exact and gives CI a gate.

Each page of a guide is one of five kinds of work:

| Work | Who makes the page |
|---|---|
| generated | A generator reads a structured source; nobody edits the page by hand |
| views | Rendered from the project's architecture model |
| written | An agent writes it from artifacts and code; a second reader evaluates it |
| existing | A hand-written page the project already had, adopted with a header |
| delegated | An existing tool of the repository publishes it; the guide links to it |

The `publish:` block of `.helix.yml` sets a guide's traits, audiences, output directory, theme, and the project's own pages.

## The parts

The code is one package, `src/documentor/`, with one module per step of the pipeline. A change belongs in the module that owns its step.

| Module | What it owns |
|---|---|
| `src/documentor/cli.py` | The `documentor` command: tool dispatch and `init`, `status`, `build`, `write`, `check`, `review`, `adopt`, `prompt` |
| `src/documentor/lib.py` | Shared code: the page header, configuration, tracked files, and the plan of pages |
| `src/documentor/detect.py` | Scores traits against the repository's files and proposes a `publish:` block |
| `src/documentor/generate.py` | Generators, registered by name, that write reference pages from structured sources |
| `src/documentor/write.py` | Has a headless agent write a page, checks it, and has a second model evaluate it |
| `src/documentor/check.py` | Checks provenance, links, paths, handling, and prose; stamps source digests |
| `src/documentor/prose.py` | Measures prose against the voice profile and word budget |
| `src/documentor/site.py` | Emits pages into an existing mkdocs or Hugo site, or writes a new one |
| `src/documentor/report.py` | The "How this guide was made" page, the missing HELIX artifacts, and site screenshots |
| `src/documentor/theme.py` | The project's ux-builder theme for the site, views, presentations, and decks |
| `src/documentor/record.py` | Publishes the project's HELIX root into the site as read-only pages |
| `src/documentor/deliverable/` | Renders HELIX present-mode scripts to `.pptx`, HTML, and PDF; reports the host's toolchain |
| `src/documentor/architecture/` | The architecture model, its views, the deployment drawing, presentations, and the estate view |

The deck renderer uses `publish.theme` when the call passes no `--theme`. The deliverable module also installs the Eraser renderer that `documentor tour --render` drives.

The catalog is package data, not code. It holds traits in `src/documentor/catalog/traits/`, site layouts in `src/documentor/catalog/site/`, and the default `plain` theme in `src/documentor/catalog/ux-builder/themes/`. `src/documentor/catalog/ci/github-actions.yml` is the CI template.

`src/documentor/catalog/helix/` copies the audiences, voice rules, and writing pass from HELIX's `workflows/` for installs. Inside the HELIX checkout, documentor reads `workflows/` directly; `--catalog` names another copy.

A new kind of repository usually needs a trait, not code. A new reference page from a structured source needs a generator in `src/documentor/generate.py`. A new check belongs in `src/documentor/check.py`.

## One request

`documentor check`, the CI gate, touches most of the parts and needs no agent or network.

```sh
uv run documentor check
```

The run prints the page list, the views' state, the HELIX artifacts the written pages lacked, and a line such as `checks: 0 blocking, 3 warnings`. It exits 0 when everything is current and 1 when something needs doing.

1. `main` in `src/documentor/cli.py` sees that `check` is not a tool and hands the arguments to `guide_main`.
2. `guide_main` reads `.helix.yml` through `config_of` and exits 2 when `publish.schema` differs from documentor's. It calls `plan` in `src/documentor/lib.py` for one entry per page.
3. `assess` gives each page a state: current, missing, stale, unreviewed, unadopted, delegated, or empty. It regenerates generated pages in memory and checks written pages' source digests.
4. `views` checks the architecture views against the model, when the project has one.
5. `report` prints the page list and the views' state; `gap_lines` in `src/documentor/report.py` adds the missing artifacts, grouped by artifact.
6. `check.run_check` runs every page check over the output directory: links, backticked paths, handling patterns, and prose.
7. The command exits 1 on any blocking finding, unfinished page, or stale view.

`documentor build` follows the same path but writes instead of comparing, then calls `site.build`. With `--write`, it first calls `write.run`, which sends missing or stale written pages to the agent. Unreviewed pages with blocking or prose findings go back to the agent; other unreviewed pages go to the evaluator. `documentor prompt` prints the writer's brief for one page, and `--reviewer` prints the evaluator's.

<details>
<summary>Where each step lives</summary>

- Dispatch and the shared flow: `main`, `guide_main`, `assess`, `views`, `report`, and `regenerate` in `src/documentor/cli.py`.
- The agent loop: `run`, `write_page`, `findings_for`, and `evaluate` in `src/documentor/write.py`.
- The reasons for the five kinds of work: ADR-001, under `docs/helix/02-design/adr/`.

</details>

The project has no architecture document or model, so it has no generated context view; the steps above come from the code.

## Where to go next

- [Architecture](architecture.md) for how the parts depend on each other.
- [Request walkthrough](walkthrough.md) for a longer trace through `build` and `write`.
- [Developer guide](developer-guide.md) to set up, run the tests, and make a first change.
- [Command line](cli.md) for every command.
- [Embedding the library](embedding.md) to call documentor from other Python code.
- [What it is and is not](../user/about.md) for the product's scope.

The tests run under the project's uv environment:

```sh
uv sync && uv run just test
```

Every suite in the `justfile` passes on a sound working copy.
