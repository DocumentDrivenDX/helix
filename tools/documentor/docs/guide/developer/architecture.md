<!-- helix:publish audience=developer page=architecture kind=explanation voice=onboarding budget=1500 written=agent-opus reviewed=2026-10-20/agent-sonnet/50659a370f4305b9 -->
<!-- helix:gap artifact:architecture -->
<!-- helix:source src/documentor/cli.py sha256:4181ca3d7fc04669 -->
<!-- helix:source src/documentor/lib.py sha256:093a891d0f8bcf48 -->
<!-- helix:source src/documentor/write.py sha256:2118376b2c167085 -->
<!-- helix:source src/documentor/site.py sha256:ed1edc72665fd7da -->
<!-- helix:source src/documentor/record.py sha256:cecdf2712047484e -->
<!-- helix:source src/documentor/deliverable/__init__.py sha256:d7e4bcda6da1fbdf -->
<!-- helix:source src/documentor/architecture/model.py sha256:374937f3d7f4c2ec -->
<!-- helix:source src/documentor/architecture/views.py sha256:9217c09b8a9d2262 -->
<!-- helix:source src/documentor/architecture/estate.py sha256:df42ad94a5c41c74 -->
<!-- helix:source src/documentor/architecture/tour.py sha256:091c1607b7c3ec64 -->
<!-- helix:source pyproject.toml sha256:50b33a33c6ff0f5e -->
<!-- helix:source justfile sha256:33d64f77836eb9e1 -->
<!-- helix:source ../../.github/workflows/documentor.yml sha256:d66814968e1608c1 -->
<!-- helix:source src/documentor/catalog/ci/github-actions.yml sha256:fa22a42e759b3fda -->
<!-- helix:source tests/validate-package.sh sha256:b1ea61c5ad13ea18 -->
<!-- helix:source docs/helix/01-frame/prd.md#requirements sha256:faab177063c3e4e8 -->
<!-- helix:source docs/helix/02-design/adr/ADR-001-a-repository-guide-is-detected-generated-written-evaluated-and-checked.md sha256:f430157a0b1cbc34 -->
<!-- helix:source docs/helix/02-design/adr/ADR-002-an-estate-view-is-composed-from-repository-architecture-models.md sha256:b612bb9b14aab618 -->
<!-- helix:source docs/helix/02-design/adr/ADR-003-documentor-drives-the-agent-that-writes-and-evaluates-the-written-pages.md sha256:46908679adfaa9f5 -->
# Architecture

documentor is one Python package with one command line, `documentor`. It reads a repository, plans the pages its readers need, and makes or checks each page. It runs no server. It runs wherever the command runs: on a developer's machine, or in a CI job.

The repository has no HELIX architecture document and no architecture model (`architecture-model.toml`) of its own. The facts below come from the code, the PRD, and the three ADRs.

## Context

documentor connects five outside systems: a target repository, the HELIX catalog, an optional agent command, an optional site generator, and GitHub through `gh`.

| Neighbour | How documentor reaches it | Needed by |
|---|---|---|
| The target repository | Reads the files git tracks and `.helix.yml`; writes pages under `publish.out` | Every command |
| The HELIX catalog | Audiences, voice profiles, the writing pass, and deliverable themes, laid out like HELIX's `workflows/` | Planning, the prose checks, the writer's brief, deliverables |
| An agent command | Prompt on standard input, page on standard output; Claude Code headless by default | `write` and `build --write` only |
| A site generator | mkdocs or Hugo when the repository has one; else documentor's own layout, or Hextra on request | `site` and `build` |
| GitHub, through `gh` | `gh api` fetches other repositories' architecture models | `estate --fetch` only |

documentor looks for the HELIX catalog in three places, in order (`helix_catalog()` in `src/documentor/lib.py`):

1. The directory named by `--catalog` or `DOCUMENTOR_CATALOG`. A directory with no `voice.yml` and no `publish/audiences` is refused.
2. The `workflows/` directory of the HELIX checkout that documentor sits in, read live.
3. The copy packaged under `src/documentor/catalog/helix/`.

`just sync-helix` refreshes the packaged copy from HELIX's `workflows/`. `just test-catalog` fails when the two differ, or when `src/documentor/prose.py` differs from the HELIX skill's prose audit. `--version` names the catalog a run reads:

```sh
uv run documentor --version
# inside the HELIX checkout:  documentor 0.18.0 (HELIX catalog live <checkout>/workflows)
# from an installed wheel:    documentor 0.18.0 (HELIX catalog packaged <release>)
```

`check` reaches only the repository and the catalog, so CI can run it with no agent and no network.

## Containers

The containers are Python modules under `src/documentor/`, plus the catalog and the deliverable renderers as package data. `cli.py` dispatches each subcommand to one of them.

| Module | What it owns |
|---|---|
| `src/documentor/cli.py` | The guide commands (`init`, `status`, `build`, `write`, `check`, `review`, `adopt`, `prompt`) and the dispatch to each tool |
| `src/documentor/lib.py` | What every command shares: the page header, root and catalog lookup, `.helix.yml`, tracked files, the page plan |
| `src/documentor/detect.py` | Scores the catalog's traits against the repository and proposes a `publish:` block |
| `src/documentor/generate.py` | Writes the pages a structured source already states; also runs a project's own generator command |
| `src/documentor/write.py` | Builds the writer's brief, calls the agent, then has a second model evaluate |
| `src/documentor/check.py` | `check-pages` and `stamp`: stale sources, broken links, missing paths, cited tests, handling patterns, prose limits |
| `src/documentor/prose.py` | Measures a page's prose against its voice profile and word budget |
| `src/documentor/site.py` | Emits the pages into an mkdocs or Hugo site, or writes a new site in its own layout or Hextra |
| `src/documentor/record.py` | `record`: publishes the HELIX root into the site as a read-only record section |
| `src/documentor/deliverable/` | `deck`, `doc`, and `doctor`: renders deck and brief scripts to .pptx, HTML, and PDF |
| `src/documentor/architecture/` | The architecture model and its checks, the views, the deployment drawing, the field guide, the estate, the `tour` player |
| `src/documentor/catalog/` | Package data: `helix/` (synced), `traits/`, `themes/`, `site/`, and `ci/` (the CI template) |

Each guide page is one of five kinds of work, and the kind decides which module makes it. The page plan in `lib.py` assigns four of them:

- `generated`: `generate.py` writes the page from a structured source, or runs the project's own generator command.
- `written`: `write.py` has the agent write the page.
- `existing`: the project's own page stands in for the guide page, adopted unchanged.
- `delegated`: the page links to another tool's output.

The fifth kind is `views`. `cli.py` renders them from the architecture model into an `architecture-views` directory under `publish.out`. A project that sets `publish.views: artifact` keeps them inside its architecture record instead.

The page header is the contract between the modules. `lib.py` defines the `helix:publish`, `helix:source`, and `helix:gap` comment lines, and `check.py` reads them back. `stamp` records each source's digest, so a page goes stale when the text of one of its sources changes.

`cli.py` refuses a `.helix.yml` whose `publish.schema` differs from the schema it reads, and exits with code 2. The documentor from the same HELIX release as the block must read it.

`write.py` builds the writer's brief from the page plan, the voice profile, and the catalog's writing pass (`src/documentor/catalog/helix/references/writing-pass.md` in the packaged copy). `documentor prompt PAGE` prints that brief, and `--reviewer` prints the evaluator's brief. Before it writes, `write.py` adds the page's own blocking and prose findings from `check.py` to the feedback. It skips a broken link to another written page, because that page may not exist yet.

`write.py` runs both agent calls from the repository root. The evaluator's brief names that root and the page by absolute path, and resolves every other path against the root.

The architecture subpackage loads only when one of its subcommands runs. Several of its modules use only the standard library, so a project can vendor them unchanged. `tour` is the exception: its render step needs Node and Chromium.

## Deployment

documentor ships as a wheel. hatchling builds the wheel, and a repository installs it through `uv` from the HELIX release that contains it. The package version, 0.18.0, follows HELIX's. Nothing is vendored into the target repository.

```sh
uv tool install "git+https://github.com/DocumentDrivenDX/helix@<tag>#subdirectory=tools/documentor"
```

The wheel must carry the catalog and the deliverable renderers, because an installed documentor reads them from package data. The package test builds the wheel and runs the CLI from a clean environment. It also checks that `--catalog` switches to a live catalog and refuses a directory that is not one:

```sh
bash tests/validate-package.sh
# OK: the wheel carries the catalog and the CLI answers from a clean environment
```

documentor runs in three places:

- **A pull request in a target repository.** The template at `src/documentor/catalog/ci/github-actions.yml` runs `documentor check --root .` through `uvx`. It needs Python, plus network access to github.com to fetch the HELIX tag it names (v0.19.0).
- **A weekly job in that repository.** The same template runs `documentor build --root . --no-site`, then opens a pull request with the regenerated pages and views. It leaves stale written pages for `status` to list.
- **A machine with agent credentials.** `documentor write` runs here, never in the CI template. The default agent command is `claude -p` with read tools only.

A site build needs more. The default layout needs only Hugo; Hextra also needs Go, plus network access the first time. A new site goes to a `site` directory under `.helix`, unless `--site` names another directory. For a Hugo site, `publish.site.site_dir` names the site, and `site` writes the pages where its content mount points.

Before the guide pages, `site` adds the sections the guide does not write. `publish.site.record` adds the record that `record.py` publishes. Each entry under `publish.site.sections` runs the project's own generator command. The renderers behind `deck` and `doc` need Node, LibreOffice, or Chrome; `documentor doctor` reports which of these the host has.

documentor's CI is HELIX's `documentor` workflow. It runs when documentor changes. It also runs when a part of HELIX that documentor packages changes: the publish catalog, voice profiles, writing pass, deliverables, or prose audit. It works from `tools/documentor` with Python 3.12 and Hugo 0.160.0:

```sh
uv sync
uvx --from rust-just==1.58.0 just test
uv run documentor check --root .
```

## Quality targets

The quality targets are the PRD's requirements, and the tests and the CI gate enforce them. None of them is a speed or size target.

| Target | Where it is held |
|---|---|
| `check` needs no agent, no network, and nothing beyond Python 3.11 and PyYAML | R-4; `dependencies = ["pyyaml>=6"]` in `pyproject.toml` |
| A generated page cannot drift: `check` regenerates it in memory and compares | `check.py`, `generate.py` |
| A written page counts only after another reader evaluates it | R-10; `review` refuses a reviewer equal to the page's writer |
| A page reaches the evaluator only once its own checks are clean | `write.py` sends a page with blocking or prose findings back to the writer first |
| A rerun on a current guide makes no agent call | R-9; `write` acts only on missing, stale, or unreviewed pages |
| Regulated data stays out of pages: `handling` patterns block a page, and generators read structure only | PRD goal 5; `check.py`, `generate.py` |
| A repository reaches documentor at a HELIX release tag, never vendored | R-8; the CI template's `DOCUMENTOR` variable |
| The packaged catalog matches HELIX's `workflows/` | `just test-catalog` |

The PRD lists "easy to read" without a measure, because no one has run a newcomer trial yet. The product owner owns that open question.

<details>
<summary>Exit codes the commands share</summary>

| Code | Meaning |
|---|---|
| 0 | No blocking findings, or the command ran |
| 1 | Something needs doing (`check`), or a page could not be read or built (`site`) |
| 2 | Usage error, or a `publish.schema` this documentor does not read |

</details>

## Decisions that shape the code

Three ADRs govern the code, and each one shapes named modules.

- [ADR-001](../../helix/02-design/adr/ADR-001-a-repository-guide-is-detected-generated-written-evaluated-and-checked.md): a guide is detected, generated, written, evaluated, checked, and assembled. It gives `detect.py`, `generate.py`, `check.py`, and `site.py` their roles.
- [ADR-002](../../helix/02-design/adr/ADR-002-an-estate-view-is-composed-from-repository-architecture-models.md) (status: draft): an estate view is composed from each repository's architecture model. It shapes `src/documentor/architecture/estate.py` and the model format in `src/documentor/catalog/helix/references/architecture-model.md`.
- [ADR-003](../../helix/02-design/adr/ADR-003-documentor-drives-the-agent-that-writes-and-evaluates-the-written-pages.md): documentor calls the agent that writes the pages, then calls a second model to evaluate them. It shapes `write.py`, the `helix:gap` header line, and the agent-as-a-command interface.

Before you add a dependency, read ADR-003's reasons for keeping the agent a command. Before you change a generator, read ADR-001's trade-offs, because a wrong generator documents every repository of that kind wrongly. The [command line reference](cli.md) lists each subcommand, and the [developer guide](developer-guide.md) covers a first change.
