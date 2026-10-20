<!-- helix:publish audience=developer page=index kind=explanation voice=onboarding budget=800 written=agent-opus reviewed=2026-10-20/agent-sonnet/8c10b76d26f330ae -->
<!-- helix:gap artifact:architecture -->
<!-- helix:source docs/helix/00-discover/product-vision.md sha256:53b51880ca06cad7 -->
<!-- helix:source docs/helix/02-design/adr/ADR-001-a-repository-guide-is-detected-generated-written-evaluated-and-checked.md#decision sha256:d3fd98aa3f21622b -->
<!-- helix:source src/documentor/cli.py sha256:4181ca3d7fc04669 -->
<!-- helix:source src/documentor/lib.py sha256:093a891d0f8bcf48 -->
<!-- helix:source src/documentor/write.py sha256:2118376b2c167085 -->
<!-- helix:source src/documentor/record.py sha256:cecdf2712047484e -->
<!-- helix:source src/documentor/deliverable/__init__.py sha256:d7e4bcda6da1fbdf -->
<!-- helix:source justfile sha256:33d64f77836eb9e1 -->
# Overview

## What it is

documentor is a Python command-line tool that turns a repository into a checked documentation guide for its developers, operators, users, and data consumers. It implements the `guide` mode of HELIX. HELIX defines a guide: the audiences, the page kinds, the writing standard, and the provenance header. documentor makes the deterministic parts exact and gives CI a gate.

Each page of a guide is one of five kinds of work:

| Work | Who makes the page |
|---|---|
| generated | A generator reads a structured source; nobody edits the page by hand |
| views | Rendered from the project's architecture model |
| written | An agent writes it from artifacts and code, and a second reader evaluates it |
| existing | A hand-written page the project already had, adopted with a header |
| delegated | A tool the repository already has publishes it; the guide links to it |

The `publish:` block of `.helix.yml` decides a guide's shape. It names the traits, the audiences, the output directory, and the project's own pages.

## The parts

The code is one package, `src/documentor/`, with one module per step of the pipeline. A change belongs in the module that owns its step.

| Module | What it owns |
|---|---|
| `src/documentor/cli.py` | The `documentor` command: dispatches to each tool, and runs `init`, `status`, `build`, `write`, `check`, `review`, `adopt`, `prompt` |
| `src/documentor/lib.py` | What every command shares: the page header, configuration, tracked files, and the plan of pages |
| `src/documentor/detect.py` | Scores each trait against the repository's files and proposes a `publish:` block |
| `src/documentor/generate.py` | The generators, each registered by name, that write reference pages from structured sources |
| `src/documentor/write.py` | Has a headless agent write a page, checks it, and has a second model evaluate it |
| `src/documentor/check.py` | Checks provenance, links, paths, handling, and prose; stamps source digests |
| `src/documentor/prose.py` | Measures a page's prose against its voice profile and word budget |
| `src/documentor/site.py` | Emits the pages into an existing mkdocs or Hugo site, or writes a new one |
| `src/documentor/record.py` | Publishes the project's governed record, its HELIX root, into the site as read-only pages |
| `src/documentor/deliverable/` | Renders HELIX present-mode scripts to `.pptx`, HTML, and PDF, and reports the host's toolchain |
| `src/documentor/architecture/` | The architecture model, its views, the deployment drawing, presentations, and the estate view |

The catalog is package data, not code. `src/documentor/catalog/traits/` holds the traits. `src/documentor/catalog/themes/` and `src/documentor/catalog/ci/github-actions.yml` hold the site themes and the CI template.

`src/documentor/catalog/helix/` holds the audiences, voice rules, and writing pass, copied from HELIX's `workflows/` for installs. Inside the HELIX checkout, documentor reads `workflows/` directly, and `--catalog` names another copy.

A new kind of repository usually needs a trait, not code. A new reference page from a structured source needs a generator in `src/documentor/generate.py`. A new check belongs in `src/documentor/check.py`.

## One request

`documentor check`, the CI gate, touches most of the parts and needs no agent or network.

```sh
uv run documentor check
```

The run prints the page list, the architecture views' state, and a line such as `checks: 0 blocking, 3 warnings`. It exits 0 when everything is current, and 1 when something needs doing.

1. `main` in `src/documentor/cli.py` finds that `check` is not a tool and hands the arguments to `guide_main`.
2. `guide_main` reads `.helix.yml` through `config_of` and exits 2 when `publish.schema` differs from documentor's. It calls `plan` in `src/documentor/lib.py`, which returns one entry per page.
3. `assess` gives each page a state: current, missing, stale, unreviewed, unadopted, delegated, or empty. It regenerates generated pages in memory and checks written pages' source digests.
4. `views` checks the architecture views against the model when the project has one.
5. `check.run_check` runs every page check over the output directory, including links, backticked paths, handling patterns, and prose.
6. The command exits 1 when any finding is blocking, any page is unfinished, or the views are stale.

`documentor build` follows the same path, writes instead of comparing, and ends by calling `site.build`. With `--write`, it first calls `write.run`, which sends each missing or stale written page to the agent. An unreviewed page with blocking or prose findings goes back to the agent with them; other unreviewed pages go to the evaluator. `documentor prompt` prints the writer's brief for one page, and `--reviewer` prints the evaluator's brief.

<details>
<summary>Where each step lives</summary>

- Dispatch and the shared flow: `main`, `guide_main`, `assess`, `views`, and `regenerate` in `src/documentor/cli.py`.
- The plan of pages: `plan` in `src/documentor/lib.py`.
- The agent loop: `run`, `write_page`, `findings_for`, and `evaluate` in `src/documentor/write.py`.
- The reasons for the five kinds of work: ADR-001, under `docs/helix/02-design/adr/`.

</details>

The project has no architecture document or model, so it has no generated context view, and the steps above come from the code. The project's maintainers own adding the model.

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

Every suite in the `justfile` passes on a sound working copy. The `test-catalog` suite runs inside the HELIX checkout. It checks that the packaged catalog equals `workflows/`, and that `src/documentor/prose.py` equals the HELIX skill's prose audit.
