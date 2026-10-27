<!-- helix:publish audience=developer page=index kind=explanation voice=onboarding budget=800 written=agent-opus reviewed=2026-10-27/agent-sonnet/852c8173bc1977de -->
<!-- helix:gap artifact:architecture -->
<!-- helix:source docs/helix/00-discover/product-vision.md sha256:53b51880ca06cad7 -->
<!-- helix:source docs/helix/02-design/adr/ADR-001-a-repository-guide-is-detected-generated-written-evaluated-and-checked.md#decision sha256:d3fd98aa3f21622b -->
<!-- helix:source src/documentor/cli.py sha256:4fe81cf37df6d5aa -->
<!-- helix:source src/documentor/lib.py sha256:7e594138b133286a -->
<!-- helix:source src/documentor/check.py sha256:784c2473233c0346 -->
<!-- helix:source src/documentor/write.py sha256:2118376b2c167085 -->
<!-- helix:source src/documentor/record.py sha256:cecdf2712047484e -->
<!-- helix:source src/documentor/report.py sha256:0f48cfca412184a2 -->
<!-- helix:source src/documentor/theme.py sha256:17adf6a5c35f2e4d -->
<!-- helix:source src/documentor/visuals.py sha256:daa439fb5d461d15 -->
<!-- helix:source src/documentor/deliverable/__init__.py sha256:ad9354803e0dd670 -->
<!-- helix:source src/documentor/catalog/ux-builder/README.md sha256:6b885638317975c7 -->
<!-- helix:source justfile sha256:33d64f77836eb9e1 -->
# Overview

## What it is

documentor is a Python command-line tool that turns a repository into a checked guide for developers, operators, users, and data consumers. HELIX defines the audiences, page kinds, writing standard, and provenance header. documentor makes the deterministic parts exact and gives CI a gate.

Each planned page has one kind of work, the `work` field of `PagePlan` in `src/documentor/lib.py`:

| Work | Who makes the page |
|---|---|
| generated | A generator writes it from a structured source |
| written | An agent writes it; a second model evaluates it |
| existing | A hand-written page, adopted with a header |
| delegated | A repository tool publishes it; the guide links to it |

The `views` step in `src/documentor/cli.py` renders architecture views from the architecture model.

The `publish:` block of `.helix.yml` sets a guide's traits, audiences, output directory, theme, and own pages.

## The parts

The code is one package, `src/documentor/`, with one module per pipeline step. A change belongs in the module that owns its step.

| Module | What it owns |
|---|---|
| `src/documentor/cli.py` | The `documentor` command: tool dispatch and `init`, `status`, `build`, `write`, `check`, `review`, `adopt`, `prompt` |
| `src/documentor/lib.py` | Shared code: the catalog location, page header, configuration, tracked files, and page plan |
| `src/documentor/detect.py` | Scores traits against the repository's files and proposes a `publish:` block |
| `src/documentor/generate.py` | Named generators that write reference pages from structured sources |
| `src/documentor/write.py` | Has an agent write a page, checks it, and has a second model evaluate it |
| `src/documentor/check.py` | Checks each page against its sources, the repository, and the project's rules |
| `src/documentor/prose.py` | Measures prose against the voice profile and word budget |
| `src/documentor/site.py` | Emits pages into an existing mkdocs or Hugo site, or writes a new one |
| `src/documentor/report.py` | The "How this guide was made" page, the missing HELIX artifacts, and site screenshots |
| `src/documentor/theme.py` | The project's ux-builder theme for the site, views, presentations, and decks |
| `src/documentor/visuals.py` | Projects the model's views into `umf.visual` documents and has `@ux-builder/visuals` draw them |
| `src/documentor/record.py` | Publishes the project's HELIX root into the site as read-only pages |
| `src/documentor/deliverable/` | Renders present-mode scripts to `.pptx`, HTML, and PDF; reports the host's toolchain |
| `src/documentor/architecture/` | The architecture model, its views, the deployment drawing, presentations, and the estate view |

Decks use `publish.theme` unless the call passes `--theme`. The deliverable module installs the Eraser renderer for `documentor tour --render`.

Visuals are on when `.helix.yml` sets `publish.visuals`. `documentor visuals` writes each document and drawing under `<publish.out>/visuals/`; `--check` fails when a document no longer matches the model.

The catalog is package data: traits in `src/documentor/catalog/traits/`, site layouts in `src/documentor/catalog/site/`, and the default `plain` theme in `src/documentor/catalog/ux-builder/themes/`. `src/documentor/catalog/ci/github-actions.yml` is the CI template.

`src/documentor/catalog/helix/` copies the audiences, voice rules, and writing pass from HELIX's `workflows/` for installs. Inside the HELIX checkout, documentor reads `workflows/` directly; `--catalog` names another copy.

```sh
uv run documentor --version
```

An install prints `documentor <version> (HELIX catalog packaged <version>)`. Inside the HELIX checkout, or with `--catalog`, it reads `HELIX catalog live <path>`.

A new kind of repository usually needs a trait, not code. A new reference page from a structured source needs a generator in `src/documentor/generate.py`.

## One request

`documentor check`, the CI gate, touches most of the parts and needs no agent or network.

```sh
uv run documentor check
```

Its report ends in a line such as `checks: 0 blocking, 3 warnings`. It exits 0 when everything is current.

1. `main` in `src/documentor/cli.py` hands `check` to `guide_main`, because `check` is not a tool.
2. `guide_main` reads `.helix.yml` through `config_of`, exits 2 when `publish.schema` differs from documentor's, and calls `plan` in `src/documentor/lib.py` for one entry per page.
3. `assess` gives each page a state: current, missing, stale, unreviewed, unadopted, delegated, or empty. It regenerates generated pages in memory and checks written pages' source digests.
4. `views` checks the architecture views against the model, when one exists, and runs `visuals.check` when visuals are on and the views are current.
5. `report` prints the page list and the views' state; `gap_lines` in `src/documentor/report.py` adds the missing artifacts.
6. `run_check` in `src/documentor/check.py` checks each page in the output directory: its sources, kind, links, backticked paths, and cited tests.
7. With PyYAML installed, `run_check` also checks handling patterns, `publish.scope`, prose, and watched files that no page cites.
8. The command exits 1 on any blocking finding, unfinished page, or stale view.

`documentor build` follows the same path but writes instead of comparing, then calls `site.build`. Its `views` step also calls `visuals.write` when visuals are on. With `--write`, `write.run` first sends missing or stale written pages to the agent.

Unreviewed pages with blocking or prose findings return to the agent; the evaluator reads the rest.

<details>
<summary>Where each step lives</summary>

- Dispatch and the shared flow: `main`, `guide_main`, `assess`, `views`, `report`, and `regenerate` in `src/documentor/cli.py`.
- The page checks: `check_sources`, `check_kind`, `check_links`, `check_tests`, `check_handling`, `check_scope`, `check_prose`, and `check_unmapped` in `src/documentor/check.py`.
- The visuals step: `enabled`, `write`, and `check` in `src/documentor/visuals.py`.
- The agent loop: `run`, `write_page`, `findings_for`, and `evaluate` in `src/documentor/write.py`.
- The pipeline's rationale: ADR-001, under `docs/helix/02-design/adr/`.

</details>

With no architecture model, these steps come from the code.

## Where to go next

Run the tests before a first change:

```sh
uv sync && uv run just test
```

The `test` recipe in the `justfile` runs every suite, including the Python unit tests and the package check.

- [Architecture](architecture.md): how the parts depend on each other.
- [Request walkthrough](walkthrough.md): a trace of `build` and `write`.
- [Developer guide](developer-guide.md): setup, the tests, and a first change.
- [Command line](cli.md): every command.
- [Embedding the library](embedding.md): calling documentor from Python.
- [What it is and is not](../user/about.md): the product's scope.
