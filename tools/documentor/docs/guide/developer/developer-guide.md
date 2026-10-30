<!-- helix:publish audience=developer page=developer-guide kind=how-to voice=onboarding budget=1300 written=agent-opus reviewed=2026-10-27/agent-sonnet/dca302513a9bd237 -->
<!-- helix:source pyproject.toml sha256:74a08b4781a32616 -->
<!-- helix:source justfile sha256:33d64f77836eb9e1 -->
<!-- helix:source ../../.github/workflows/documentor.yml sha256:ab2fb8338de1a028 -->
<!-- helix:source ../../.github/workflows/release-tag.yml sha256:cf31b27d56efd66b -->
<!-- helix:source ../../.github/workflows/release-version-guard.yml sha256:31a73cb81eb3e42a -->
<!-- helix:source ../../CONTRIBUTING.md sha256:d0027006597fad67 -->
<!-- helix:source README.md#development sha256:ec26429513feaa3e -->
<!-- helix:source src/documentor/__init__.py sha256:e612d1e2f68f2667 -->
<!-- helix:source src/documentor/cli.py sha256:4fe81cf37df6d5aa -->
<!-- helix:source src/documentor/visuals.py sha256:a800032637b6cd3b -->
<!-- helix:source src/documentor/report.py sha256:0f48cfca412184a2 -->
<!-- helix:source src/documentor/lib.py sha256:7e594138b133286a -->
<!-- helix:source src/documentor/catalog/ci/github-actions.yml sha256:fa22a42e759b3fda -->
<!-- helix:source src/documentor/catalog/ux-builder/README.md sha256:6b885638317975c7 -->
<!-- helix:source tests/validate-package.sh sha256:ddc499febfa0dd79 -->
<!-- helix:source tests/validate-publish.sh sha256:fbe3dede8c6f4a24 -->
<!-- helix:source ../../scripts/sync_references.py sha256:408f8110f448a604 -->
# Developer guide

## Quick start

To get a working copy, clone the HELIX repository, change to `tools/documentor`, sync with uv, and run the tests. You need Python 3.11 or later, [uv](https://docs.astral.sh/uv/), and `just` on your `PATH`. Hugo is optional, and without it the tests skip the site build.

```sh
git clone https://github.com/DocumentDrivenDX/helix
cd helix/tools/documentor
uv sync
uv run just test
```

`uv sync` creates `.venv` with the one runtime dependency (`pyyaml>=6`) and the `dev` group (`pytest>=8`). Each passing test script prints an `OK:` line. A failing script prints `FAIL:` with the reason and stops the run.

To check that the CLI runs:

```sh
uv run documentor --version
```

Inside the HELIX checkout, the output is `documentor <version> (HELIX catalog live /path/to/helix/workflows)`. An installed wheel prints `HELIX catalog packaged <version>`, the release it shipped in. `--catalog DIR` or the `DOCUMENTOR_CATALOG` variable names another catalog.

To see which optional tools the machine has (hugo, node, Chrome, LibreOffice, the agent CLI):

```sh
uv run documentor doctor
```

To run your working copy against another repository:

```sh
uv run documentor check --root ../some-repo
```

`uvx --from /path/to/documentor` caches its build of a local path, so after a change add `--refresh`, or use `uv run --project /path/to/documentor documentor ...`.

## Repository map

The package is in `src/documentor`, the tests are in `tests`, and the design records are in `docs/helix`. [Architecture](architecture.md) explains how the parts fit together.

| Path | What it holds |
|---|---|
| `src/documentor/cli.py` | The `documentor` command and its subcommands; the entry point `documentor.cli:main` |
| `src/documentor/detect.py` | Detects what a repository is (its traits) |
| `src/documentor/generate.py` | Generators for pages whose facts come from a structured source |
| `src/documentor/write.py` | Drives the agent that writes and evaluates written pages (ADR-003) |
| `src/documentor/check.py` | The CI gate: missing, stale, or unreviewed pages |
| `src/documentor/report.py` | The site's "How this guide was made" page, and the missing artifacts the pages name |
| `src/documentor/site.py` | Assembles the pages into a site |
| `src/documentor/record.py` | Publishes the governed record (the HELIX root) into the site |
| `src/documentor/prose.py` | Prose checks against the voice profile |
| `src/documentor/theme.py` | Resolves the theme a project names |
| `src/documentor/visuals.py` | The model's views as `umf.visual` documents, drawn by `@ux-builder/visuals`; behind `documentor visuals` |
| `src/documentor/lib.py` | Shared helpers, including which HELIX catalog a run reads |
| `src/documentor/architecture/` | Architecture views, the estate view, the tour, and the field guide |
| `src/documentor/deliverable/` | Deck and brief renderers behind `documentor deck` and `documentor doc` |
| `src/documentor/catalog/traits/` | One YAML file per trait, such as `significant.yml` |
| `src/documentor/catalog/helix/` | The packaged HELIX catalog: `publish/`, `voice.yml`, `deliverables/`, `references/`; do not edit by hand |
| `src/documentor/catalog/ci/github-actions.yml` | The CI template that target repositories copy |
| `src/documentor/catalog/ux-builder/` | The packaged `plain` theme, copied unchanged from `@ux-builder/tokens` |
| `src/documentor/catalog/site/` | Site layouts and static files |
| `tests/` | `validate-*.sh` end-to-end scripts and `tests/python/` unit tests |
| `docs/helix/` | Product vision, PRD, ADRs, and plans |

documentor uses the `plain` theme when a project names no theme or the named theme cannot be fetched. Other themes come from `@ux-builder/tokens`, through `publish.theme`.

Visuals are on when `.helix.yml` sets `publish.visuals`. Then `documentor views --write` also writes the visuals, and `documentor views` reports the views stale when a visual no longer matches the model. `documentor visuals --check` writes nothing and fails on the same mismatch.

[Command line](cli.md) lists the commands, and [Embedding the library](embedding.md) covers calling the package from Python.

## Running the tests

`uv run just test` runs every suite, and each suite has its own recipe. The end-to-end scripts call `documentor` from `PATH`, so outside `uv run` they fail with `documentor is not on PATH`.

| Recipe | What it exercises |
|---|---|
| `just test-catalog` | The packaged catalog equals HELIX's `workflows/`, and `prose.py` equals the skill's prose audit |
| `just test-guide` | `init`, `build`, `check`, and `review` on a repository with no guide (`tests/validate-guide.sh`) |
| `just test-publish` | Publishing and the site build (`tests/validate-publish.sh`) |
| `just test-traits` | Trait detection and the pages each trait adds (`tests/validate-publish-traits.sh`) |
| `just test-generators` | The generated pages (`tests/validate-publish-generators.sh`) |
| `just test-write` | `write` and `build --write` with a fake agent (`tests/validate-write.sh`) |
| `just test-architecture-views` | Architecture views (`tests/validate-architecture-views.sh`) |
| `just test-architecture-estate` | The estate view (`tests/validate-architecture-estate.sh`) |
| `just test-architecture-tour` | Architecture walkthrough (`tests/validate-architecture-tour.sh`) |
| `just test-python` | Pytest unit tests in `tests/python` |
| `just test-package` | The wheel builds, carries the catalog, and its CLI runs in a clean environment (`tests/validate-package.sh`) |

To run one suite (on success, the last line starts with `OK:`):

```sh
uv run just test-write
```

`just test-write` needs no agent credentials: the script writes a fake agent that answers writer and evaluator prompts and logs each call.

`just test-publish` checks that the built site has an `about` section titled "How this guide was made", with a `## The pages` list. Without Hugo, its `OK:` line ends with `(hugo not installed; build skipped)`.

`just test-package` builds the wheel with `uv build` and runs the installed CLI with `uv run --isolated`. It also checks that `--catalog` refuses a directory that is no HELIX catalog.

CI is HELIX's `documentor` workflow. It runs on pull requests and pushes to `main` that touch documentor, HELIX's publish catalog, or HELIX's voice profiles.

<details>
<summary>The CI job, from HELIX's documentor workflow</summary>

```yaml
- uses: astral-sh/setup-uv@v6
  with: { python-version: "3.12" }
- uses: peaceiris/actions-hugo@v3
  with: { hugo-version: "0.160.0", extended: true }
- run: uv sync
- run: uv run --with rust-just==1.58.0 just test
- run: uv run documentor check --root .
```

</details>

<details>
<summary>The files the wheel must carry, from <code>tests/validate-package.sh</code></summary>

```text
documentor/catalog/helix/voice.yml
documentor/catalog/helix/publish/audiences/developer.yml
documentor/catalog/traits/significant.yml
documentor/catalog/ux-builder/resolved/plain.light.json
documentor/catalog/ci/github-actions.yml
documentor/architecture/js/stage.mjs
documentor/deliverable/render-deck.js
documentor/deliverable/deck-qa.py
documentor/deliverable/lib/script.js
documentor/deliverable/icons/
documentor/deliverable/package.json
```

A new packaged file the CLI needs at run time belongs in this list.

</details>

## Making a change

To make a change, edit the module or catalog file, add an assertion to the matching test script, and run that suite before the full suite. HELIX's [AGENTS.md](../../../../../AGENTS.md) and [CONTRIBUTING.md](../../../../../CONTRIBUTING.md) set the contributor rules.

1. Create a branch from `main`:

   ```sh
   git switch -c my-change
   ```

2. Make the change. For example, to change which files a trait detects, edit its YAML under `src/documentor/catalog/traits/`.

3. Add an assertion to the matching script. Each script builds a scratch repository in a temporary directory, runs the CLI, and calls `fail` when a result is wrong:

   ```sh
   fail() { echo "FAIL: $*" >&2; exit 1; }
   ```

4. Run the suite, then all suites:

   ```sh
   uv run just test-traits
   uv run just test
   ```

5. Try the change on a copy of a real repository. Without a `.helix.yml`, `init` writes one and creates the `docs/helix/` folders, even without `--write`:

   ```sh
   uv run documentor init --root ../some-repo
   ```

   The proposal shows the traits and pages your change adds or removes.

Four kinds of change follow their own path:

- **A new packaged generator** registers under `[project.entry-points."documentor.generators"]` in `pyproject.toml` as `name = "module:function"`. The function takes `(root, page)` and returns `(body, source_globs)`. A repository's own generator is a command under `generated:` in its `.helix.yml` and needs no entry point.
- **A new tool subcommand** joins the `TOOLS` tuple in `src/documentor/cli.py`, and `main` dispatches it to its module's `main`, as `visuals` does. Its usage line belongs in the module docstring of `cli.py`.
- **The HELIX catalog** (audiences, voice, deliverables, and the publishing and writing-pass references) comes from HELIX's `workflows/`. Change it there, then copy it rather than editing `src/documentor/catalog/helix/`:

  ```sh
  uv run just sync-helix
  ```

  The script prints `synced documentor floor -> tools/documentor/src/documentor/catalog/helix: N files`. When the copy and `workflows/` differ, `just test-catalog` lists each `stale:` or `extra:` file and fails.
- **The prose checks** in `src/documentor/prose.py` must stay byte-identical to `../../skills/helix/scripts/prose_audit.py`. Change both together, or `just test-catalog` fails.

A change to the CLI's behaviour may change the pages in `docs/guide/`. `uv run documentor status` lists each page of the guide and what it needs next:

```sh
uv run documentor status
```

When written pages name a HELIX artifact the repository lacks, the report ends with `Artifacts that would improve the guide`. Each line names the artifact and the pages written without it, most pages first. Once HELIX supplies that artifact, the listed pages are rewritten from it.

## Releasing

documentor ships in HELIX releases and has no tag of its own. The steps come from HELIX's `release-tag` and `release-version-guard` workflows, because no contributor file lists release steps.

Release work requires a separately authorized release scope ([CONTRIBUTING.md](../../../../../CONTRIBUTING.md)). No file in the repository defines that scope or says how to get it. The HELIX release owner grants it, and you need it before step 3.

1. Run every suite and the guide check from `tools/documentor`. Every script ends with an `OK:` line, and `check` exits zero:

   ```sh
   uv run just test
   uv run documentor check --root .
   ```

2. Set the release version in all five places, because no script updates them.

   | File | Field |
   |---|---|
   | `../../.claude-plugin/plugin.json` | `version` |
   | `../../.codex-plugin/plugin.json` | `version` |
   | `../../.claude-plugin/marketplace.json` | `version` of the `helix` entry under `plugins` |
   | `pyproject.toml` | `version` |
   | `src/documentor/__init__.py` | `__version__` |

   The three plugin manifests decide whether HELIX gets a tag. The two documentor files decide what `documentor --version` prints, and no release workflow reads them.

3. Open a pull request to `main` whose title starts with `chore(release): vX.Y.Z`. On merge, HELIX's `release-tag` workflow reads the three plugin manifests. When all three equal `X.Y.Z`, it pushes the tag and starts the publish workflows.

   <details>
   <summary>When the manifests and the title disagree</summary>

   The workflow prints one `::error::` line per mismatched manifest, under `manifest version(s) do not match the PR title, refusing to tag:`. It exits without a tag, as it does when the tag already exists. To recover, merge a new `chore(release):` pull request whose manifests match its title.

   </details>

4. Check the release from the tag. The output starts with `documentor X.Y.Z`:

   ```sh
   uvx --from git+https://github.com/DocumentDrivenDX/helix@vX.Y.Z#subdirectory=tools/documentor documentor --version
   ```

The `release-version-guard` workflow deletes a pushed tag and its release when the plugin manifests disagree with the tag.
