<!-- helix:publish audience=developer page=developer-guide kind=how-to voice=onboarding budget=1300 written=agent-opus reviewed=2026-10-20/second-reader-move-review/2b4138b705c511f1 -->
<!-- helix:source pyproject.toml sha256:95efaa59d25e6f0a -->
<!-- helix:source justfile sha256:8b9f44abbdc7b4e0 -->
<!-- helix:source ../../.github/workflows/documentor.yml sha256:06f939b8b1b71ec1 -->
<!-- helix:source README.md#development sha256:ec26429513feaa3e -->
<!-- helix:source src/documentor/__init__.py sha256:b5853dda7e0aef19 -->
<!-- helix:source src/documentor/cli.py sha256:63fa5bcbdc82b569 -->
<!-- helix:source src/documentor/catalog/ci/github-actions.yml sha256:fa22a42e759b3fda -->
<!-- helix:source tests/validate-package.sh sha256:69be8ff75ae2184c -->
<!-- helix:source tests/validate-publish.sh sha256:b8d3606d22ab7013 -->
<!-- helix:source scripts/sync-helix-catalog.py sha256:d626e57d6a7c91b6 -->
# Developer guide

## Quick start

To get a working copy, clone the HELIX repository, change to `tools/documentor`, run `uv sync`, and then run the full test suite through `just`. You need Python 3.11 or later, [uv](https://docs.astral.sh/uv/), and `just` on your `PATH`. Hugo is optional. Without it, the tests skip the site build.

```sh
git clone https://github.com/DocumentDrivenDX/helix
cd helix/tools/documentor
uv sync
uv run just test
```

`uv sync` creates `.venv` with the one runtime dependency (`pyyaml>=6`) and the `dev` group (`pytest>=8`). Each test script prints an `OK:` line when it passes. A failing script prints `FAIL:` with the reason and stops the run.

To check that the working copy's CLI runs:

```sh
uv run documentor --version
```

The output is `documentor 0.1.0 (HELIX catalog in-repo)`. The catalog label comes from `src/documentor/catalog/helix/HELIX_VERSION`.

To run your working copy against another repository:

```sh
uv run documentor check --root ../some-repo
```

`uvx --from /path/to/documentor` caches the build it makes from a local path. After a change, add `--refresh`, or use `uv run --project /path/to/documentor documentor ...` instead.

## Repository map

The package is in `src/documentor`, the shell and Python tests are in `tests`, and the design records are in `docs/helix`. [Architecture](architecture.md) explains how the parts fit together.

| Path | What it holds |
|---|---|
| `src/documentor/cli.py` | The `documentor` command and its subcommands; the entry point `documentor.cli:main` |
| `src/documentor/detect.py` | Detects what a repository is (its traits) |
| `src/documentor/generate.py` | Generators for pages whose facts come from a structured source |
| `src/documentor/write.py` | Drives the agent that writes and evaluates written pages (ADR-003) |
| `src/documentor/check.py` | The CI gate: missing, stale, or unreviewed pages |
| `src/documentor/site.py` | Assembles the pages into a site |
| `src/documentor/prose.py` | Prose checks against the voice profile |
| `src/documentor/lib.py` | Shared helpers |
| `src/documentor/architecture/` | Architecture views, the estate view, and the field guide |
| `src/documentor/catalog/traits/` | One YAML file per trait, such as `python-cli.yml` |
| `src/documentor/catalog/helix/` | Audiences and voice copied from HELIX; do not edit by hand |
| `src/documentor/catalog/ci/github-actions.yml` | The CI template that target repositories copy |
| `src/documentor/catalog/themes/` | Site themes |
| `scripts/sync-helix-catalog.py` | Copies the audiences and voice from the HELIX repository's own `workflows/` |
| `tests/` | `validate-*.sh` end-to-end scripts and `tests/python/` unit tests |
| `docs/helix/` | Product vision, PRD, ADRs, and plans |

The CLI's commands are listed in [Command line](cli.md). [Embedding the library](embedding.md) covers calling the package from Python.

## Running the tests

`uv run just test` runs every suite. Each suite also has its own recipe, so you can run only the one that covers your change. The end-to-end scripts call `documentor` from `PATH`, and they fail at once with `documentor is not on PATH` when not run through `uv run`.

| Recipe | What it exercises |
|---|---|
| `just test-guide` | `init`, `build`, `check`, and `review` on a repository with no guide (`tests/validate-guide.sh`) |
| `just test-publish` | Publishing and the site build (`tests/validate-publish.sh`) |
| `just test-traits` | Trait detection and the pages each trait adds (`tests/validate-publish-traits.sh`) |
| `just test-generators` | The generated pages (`tests/validate-publish-generators.sh`) |
| `just test-write` | `write` and `build --write` with a fake agent (`tests/validate-write.sh`) |
| `just test-architecture-views` | Architecture views (`tests/validate-architecture-views.sh`) |
| `just test-architecture-estate` | The estate view (`tests/validate-architecture-estate.sh`) |
| `just test-architecture-present` | Architecture presentation (`tests/validate-architecture-present.sh`) |
| `just test-python` | Pytest unit tests in `tests/python` |
| `just test-package` | The wheel builds, carries the catalog, and its CLI runs in a clean environment |

Run one suite like this:

```sh
uv run just test-write
```

On success the last line starts with `OK:`.

`just test-write` needs no agent credentials. The script writes a fake agent that answers writer and evaluator prompts and logs each call.

`just test-publish` checks the built site only when `hugo` is on `PATH`. Without Hugo, its `OK:` line ends with `(hugo not installed; build skipped)`, and the suite still passes. Install Hugo locally to run the same site checks that CI runs.

CI is HELIX's `documentor` workflow. It runs on pull requests and pushes to `main` that touch documentor, HELIX's publish catalog, or HELIX's voice profiles. From `tools/documentor`, it installs uv with Python 3.12 and Hugo 0.160.0 extended. It then runs `uvx --from rust-just==1.58.0 just test` and `uv run documentor check --root .`.

<details>
<summary>The CI job, from HELIX's documentor workflow</summary>

```yaml
- uses: astral-sh/setup-uv@v6
  with: { python-version: "3.12" }
- uses: peaceiris/actions-hugo@v3
  with: { hugo-version: "0.160.0", extended: true }
- run: uv sync
- run: uvx --from rust-just==1.58.0 just test
- run: uv run documentor check --root .
```

</details>


## Making a change

To make a change, edit the module or catalog file, add an assertion to the test script that covers it, and run that suite before the full suite. HELIX's [AGENTS.md](../../../../../AGENTS.md) and [CONTRIBUTING.md](../../../../../CONTRIBUTING.md) set the contributor rules. Commit messages in the history state the resulting behaviour in one sentence.

1. Create a branch from `main`:

   ```sh
   git switch -c my-change
   ```

2. Make the change. For example, to change which files a trait detects, edit its YAML under `src/documentor/catalog/traits/`.

3. Add an assertion to the matching script. Each script builds a scratch repository in a temporary directory, runs the CLI, and calls `fail` with a message when a result is wrong:

   ```sh
   fail() { echo "FAIL: $*" >&2; exit 1; }
   ```

4. Run the suite, then everything:

   ```sh
   uv run just test-traits
   uv run just test
   ```

   Every script ends with an `OK:` line.

5. Try the change on a copy of a real repository. For a trait change, `init` detects what the repository is and proposes its guide. When the repository has no `.helix.yml`, `init` writes one and creates the `docs/helix/` folders, even without `--write`:

   ```sh
   uv run documentor init --root ../some-repo
   ```

   The proposal should show the traits and pages your change adds or removes.

Two kinds of change follow their own path:

- **A new packaged generator** registers under `[project.entry-points."documentor.generators"]` in `pyproject.toml` as `name = "module:function"`. The function takes `(root, page)` and returns `(body, source_globs)`.
- **HELIX audiences and voice** come from the HELIX repository's own `workflows/`. Change them there, then copy them instead of editing `src/documentor/catalog/helix/`:

  ```sh
  uv run just sync-helix
  ```

  The script prints `synced N audiences and voice.yml from HELIX in-repo`. `just test-catalog` fails when the copy and `workflows/` differ.

A change to the CLI's behaviour may also change the pages in `docs/guide/`. `uv run documentor status` lists every page of this repository's guide and what each needs next, such as missing, stale, or unreviewed.

## Releasing

documentor is released with HELIX. Users install it from a HELIX release tag, and it has no tag of its own. When HELIX's release process moves the version, bump `version` in `pyproject.toml` and `__version__` in `src/documentor/__init__.py` to match. HELIX's `CONTRIBUTING.md` and `AGENTS.md` describe that process.
