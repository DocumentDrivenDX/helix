<!-- helix:publish audience=developer page=index kind=explanation voice=onboarding budget=800 written=codex reviewed=2026-10-29/codex-independent-reader/e68e70caf7cc238f -->
<!-- helix:gap artifact:architecture -->
<!-- helix:source docs/helix/00-discover/product-vision.md sha256:53b51880ca06cad7 -->
<!-- helix:source docs/helix/02-design/adr/ADR-001-a-repository-guide-is-detected-generated-written-evaluated-and-checked.md#decision sha256:d3fd98aa3f21622b -->
<!-- helix:source src/documentor/cli.py sha256:861322ae490496ea -->
<!-- helix:source src/documentor/lib.py sha256:c5e1e41d3141003c -->
<!-- helix:source src/documentor/write.py sha256:208f5a662b7501e4 -->
<!-- helix:source src/documentor/record.py sha256:ab468e2c1eef452a -->
<!-- helix:source src/documentor/report.py sha256:0f48cfca412184a2 -->
<!-- helix:source src/documentor/theme.py sha256:7e38d9589c728f0b -->
<!-- helix:source src/documentor/deliverable/__init__.py sha256:ad9354803e0dd670 -->
<!-- helix:source src/documentor/catalog/ux-builder/README.md sha256:6b885638317975c7 -->
<!-- helix:source justfile sha256:33d64f77836eb9e1 -->
<!-- helix:source src/documentor/schemas.py sha256:9a9548369cb394fa -->
<!-- helix:source src/documentor/umf_tables.py sha256:56c75007b5b2d2de -->
<!-- helix:source src/documentor/detect.py sha256:376f1dd87ec38e48 -->
# Overview

## What it is

documentor turns a repository into a checked guide for developers, operators, users, and data consumers. It implements HELIX guide mode: audiences, page kinds, writing standards, provenance, and a CI gate.

Each guide page is one of five kinds of work:

| Work | Who makes the page |
|---|---|
| generated | A generator reads a structured source; nobody edits the page by hand |
| views | Rendered from the project's architecture model |
| written | An agent writes it from artifacts and code; a second reader evaluates it |
| existing | A hand-written page the project already had, adopted with a header |
| delegated | An existing tool of the repository publishes it; the guide links to it |

The `publish:` block of `.helix.yml` sets a guide's traits, audiences, output directory, theme, and the project's own pages.

## The parts

The code is one package, `src/documentor/`, with one module per pipeline step. A change belongs in the module that owns its step.

| Module | What it owns |
|---|---|
| `src/documentor/cli.py` | The `documentor` command: tool dispatch and `init`, `status`, `build`, `write`, `check`, `review`, `adopt`, `prompt` |
| `src/documentor/lib.py` | Shared code: the catalog location, page header, configuration, tracked files, and page plan |
| `src/documentor/detect.py` | Scores traits against the repository's files and proposes a `publish:` block |
| `src/documentor/generate.py` | Generators, registered by name, that write reference pages from structured sources |
| `src/documentor/write.py` | Has a headless agent write a page, checks it, and has a second model evaluate it |
| `src/documentor/check.py` | Checks provenance, links, paths, handling, and prose; stamps source digests |
| `src/documentor/prose.py` | Measures prose against the voice profile and word budget |
| `src/documentor/site.py` | Emits pages into an existing mkdocs or Hugo site, or writes a new one |
| `src/documentor/report.py` | The "How this guide was made" page, the missing HELIX artifacts, and site screenshots |
| `src/documentor/theme.py` | The project's ux-builder theme for the site, views, presentations, and decks |
| `src/documentor/schemas.py` | Publishes versioned design schemas and the UMF browser |
| `src/documentor/umf_tables.py` | Reads UMF TableSpec tables for generated data references |
| `src/documentor/record.py` | Publishes the project's HELIX root into the site as read-only pages |
| `src/documentor/deliverable/` | Renders HELIX present-mode scripts to `.pptx`, HTML, and PDF; reports the host's toolchain |
| `src/documentor/architecture/` | The architecture model, its views, the deployment drawing, presentations, and the estate view |

Decks use `publish.theme` unless the call passes `--theme`. The deliverable module also installs the Eraser renderer for `documentor tour --render`.

The catalog is package data: traits in `src/documentor/catalog/traits/`, site layouts in `src/documentor/catalog/site/`, and the default `plain` theme in `src/documentor/catalog/ux-builder/themes/`. `src/documentor/catalog/ci/github-actions.yml` is the CI template.

`src/documentor/catalog/helix/` copies the audiences, voice rules, and writing pass from HELIX's `workflows/` for installs. Inside the HELIX checkout, documentor reads `workflows/` directly; `--catalog` names another copy. documentor ships with HELIX at one version, so `helix_version` in `src/documentor/lib.py` labels the packaged copy with `__version__`.

```sh
uv run documentor --version
```

An install prints `documentor <version> (HELIX catalog packaged <version>)`. Inside the HELIX checkout, or with `--catalog`, it reads `HELIX catalog live <path>`.

Applicable site builds publish declared schemas and discovered UMF tables through a pinned browser. Operational data pages use Data Design.

Add traits for new repository kinds and generators in `src/documentor/generate.py` for structured references.

## One request

`documentor check`, the CI gate, touches most of the parts and needs no agent or network.

```sh
uv run documentor check
```

It prints the page list, the views' state, the missing HELIX artifacts, and a line such as `checks: 0 blocking, 3 warnings`. It exits 0 when everything is current and 1 when something needs doing.

1. `main` in `src/documentor/cli.py` sees that `check` is not a tool and hands the arguments to `guide_main`.
2. `guide_main` reads `.helix.yml` through `config_of` and exits 2 when `publish.schema` differs from documentor's. It calls `plan` in `src/documentor/lib.py` for one entry per page.
3. `assess` gives each page a state: current, missing, stale, unreviewed, unadopted, delegated, or empty. It regenerates generated pages in memory and checks written pages' source digests.
4. `views` checks the architecture views against the model, when the project has one.
5. `report` prints the page list and the views' state; `gap_lines` in `src/documentor/report.py` adds the missing artifacts.
6. `check.run_check` runs every page check over the output directory: links, backticked paths, handling patterns, and prose.
7. The command exits 1 on any blocking finding, unfinished page, or stale view.

`documentor build` follows the same path but writes instead of comparing, then calls `site.build`. With `--write`, it first calls `write.run`, which sends missing or stale written pages to the agent. Unreviewed pages with blocking or prose findings go back to the agent; other unreviewed pages go to the evaluator. `documentor prompt` prints the writer's brief for one page, and `--reviewer` prints the evaluator's.

<details>
<summary>Where each step lives</summary>

- Dispatch and the shared flow: `main`, `guide_main`, `assess`, `views`, `report`, and `regenerate` in `src/documentor/cli.py`.
- The agent loop: `run`, `write_page`, `findings_for`, and `evaluate` in `src/documentor/write.py`.
- The reasons for the five kinds of work: ADR-001, under `docs/helix/02-design/adr/`.

</details>

The steps come from the code; this project has no architecture model.

## Where to go next

- [Architecture](architecture.md) for how the parts depend on each other.
- [Request walkthrough](walkthrough.md) to trace `build` and `write`.
- [Developer guide](developer-guide.md) to set up, run the tests, and make a first change.
- [Command line](cli.md) for every command.
- [Embedding the library](embedding.md) to call documentor from other Python code.
- [What it is and is not](../user/about.md) for the product's scope.

Run the tests:

```sh
uv sync && uv run just test
```

Every suite in the `justfile` passes on a sound working copy.
