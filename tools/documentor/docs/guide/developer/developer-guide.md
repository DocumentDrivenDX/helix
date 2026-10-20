<!-- helix:publish audience=developer page=developer-guide kind=how-to voice=onboarding budget=1300 written=agent-opus reviewed=2026-10-20/agent-sonnet/82d91760960ada99 -->
<!-- helix:source pyproject.toml sha256:50b33a33c6ff0f5e -->
<!-- helix:source justfile sha256:33d64f77836eb9e1 -->
<!-- helix:source ../../.github/workflows/documentor.yml sha256:d66814968e1608c1 -->
<!-- helix:source ../../.github/workflows/release-tag.yml sha256:cf31b27d56efd66b -->
<!-- helix:source ../../.github/workflows/release-version-guard.yml sha256:31a73cb81eb3e42a -->
<!-- helix:source ../../CONTRIBUTING.md sha256:d0027006597fad67 -->
<!-- helix:source README.md#development sha256:ec26429513feaa3e -->
<!-- helix:source src/documentor/__init__.py sha256:fca11fbda3ce2778 -->
<!-- helix:source src/documentor/cli.py sha256:4181ca3d7fc04669 -->
<!-- helix:source src/documentor/lib.py sha256:093a891d0f8bcf48 -->
<!-- helix:source src/documentor/catalog/ci/github-actions.yml sha256:fa22a42e759b3fda -->
<!-- helix:source tests/validate-package.sh sha256:b1ea61c5ad13ea18 -->
<!-- helix:source tests/validate-publish.sh sha256:978673c6cb51fb8f -->
<!-- helix:source ../../scripts/sync_references.py sha256:019062c512836eb4 -->
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

Inside the HELIX checkout, the output is `documentor 0.18.0 (HELIX catalog live /path/to/helix/workflows)`. A run inside the checkout reads HELIX's `workflows/` directly. An installed wheel reads its packaged copy instead and prints `HELIX catalog packaged`. `--catalog DIR` or the `DOCUMENTOR_CATALOG` variable names another catalog.

To see which optional tools this machine has (hugo, node, Chrome, LibreOffice, the agent CLI):

```sh
uv run documentor doctor
```

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
| `src/documentor/record.py` | Publishes the governed record (the HELIX root) into the site |
| `src/documentor/prose.py` | Prose checks against the voice profile |
| `src/documentor/lib.py` | Shared helpers, including which HELIX catalog a run reads |
| `src/documentor/architecture/` | Architecture views, the estate view, the tour, and the field guide |
| `src/documentor/deliverable/` | Deck and brief renderers behind `documentor deck` and `documentor doc` |
| `src/documentor/catalog/traits/` | One YAML file per trait, such as `significant.yml` |
| `src/documentor/catalog/helix/` | The packaged HELIX catalog: `publish/`, `voice.yml`, `deliverables/`, `references/`, `HELIX_VERSION`; do not edit by hand |
| `src/documentor/catalog/ci/github-actions.yml` | The CI template that target repositories copy |
| `src/documentor/catalog/themes/` | Site themes |
| `tests/` | `validate-*.sh` end-to-end scripts and `tests/python/` unit tests |
| `docs/helix/` | Product vision, PRD, ADRs, and plans |

The CLI's commands are listed in [Command line](cli.md). [Embedding the library](embedding.md) covers calling the package from Python.

## Running the tests

`uv run just test` runs every suite. Each suite also has its own recipe, so you can run only the one that covers your change. The end-to-end scripts call `documentor` from `PATH`, and they fail at once with `documentor is not on PATH` when not run through `uv run`.

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

Run one suite like this:

```sh
uv run just test-write
```

On success the last line starts with `OK:`.

`just test-write` needs no agent credentials. The script writes a fake agent that answers writer and evaluator prompts and logs each call.

`just test-publish` checks the built site only when `hugo` is on `PATH`. Without Hugo, its `OK:` line ends with `(hugo not installed; build skipped)`, and the suite still passes. Install Hugo locally to run the same site checks that CI runs.

`just test-package` builds the wheel with `uv build` and runs the installed CLI with `uv run --isolated`. It checks that the wheel holds the catalog and the deck renderer. It also checks that `--catalog` refuses a directory that is no HELIX catalog.

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

Three kinds of change follow their own path:

- **A new packaged generator** registers under `[project.entry-points."documentor.generators"]` in `pyproject.toml` as `name = "module:function"`. The function takes `(root, page)` and returns `(body, source_globs)`. A repository's own generator needs no entry point: it is a command under `generated:` in its `.helix.yml`.
- **The HELIX catalog** (audiences, voice, deliverables, and the publishing and writing-pass references) comes from HELIX's `workflows/`. Change it there, then copy it instead of editing `src/documentor/catalog/helix/`:

  ```sh
  uv run just sync-helix
  ```

  The script prints `synced documentor floor -> tools/documentor/src/documentor/catalog/helix: N files`. When the copy and `workflows/` differ, `just test-catalog` lists each `stale:` or `extra:` file and fails.
- **The prose checks** in `src/documentor/prose.py` must stay byte-identical to `../../skills/helix/scripts/prose_audit.py`. Change both together, or `just test-catalog` fails.

A change to the CLI's behaviour may also change the pages in `docs/guide/`. `uv run documentor status` lists every page of this repository's guide and what each needs next, such as missing, stale, or unreviewed.

## Releasing

documentor is released with HELIX: a HELIX release tag carries it, and it has no tag of its own. Release work requires a separately authorized release scope. It follows HELIX's [runtime handoff contract](../../../../../workflows/modes/runtime-handoff.md) and the repository release instructions ([CONTRIBUTING.md](../../../../../CONTRIBUTING.md)).

1. Run every suite and the guide check from `tools/documentor`:

   ```sh
   uv run just test
   uv run documentor check --root .
   ```

   Every script ends with an `OK:` line, and `check` exits zero. `just test-catalog` confirms that the packaged catalog matches `workflows/`. `just test-package` confirms that the wheel carries it.

2. Set the release version in all five places. Today each one holds `0.18.0`, and no script in the repository updates them for you.

   | File | Field |
   |---|---|
   | `../../.claude-plugin/plugin.json` | `version` |
   | `../../.codex-plugin/plugin.json` | `version` |
   | `../../.claude-plugin/marketplace.json` | `version` of the `helix` entry under `plugins` |
   | `pyproject.toml` | `version` |
   | `src/documentor/__init__.py` | `__version__` |

   The three plugin manifests decide whether HELIX gets a tag. The two documentor files decide what `documentor --version` prints.

3. Open a pull request to `main` whose title starts with `chore(release): vX.Y.Z`. When it merges, HELIX's `release-tag` workflow reads the three plugin manifests at the merge commit. When all three equal `X.Y.Z`, it creates and pushes the tag, then starts the publish workflows.

   <details>
   <summary>When the manifests and the title disagree</summary>

   The workflow prints one `::error::` line per mismatched manifest, under `manifest version(s) do not match the PR title, refusing to tag:`. It exits without a tag. It also stops when the tag already exists. To recover, merge a new `chore(release):` pull request whose manifests match its title.

   </details>

4. Check the release from the tag:

   ```sh
   uvx --from git+https://github.com/DocumentDrivenDX/helix@vX.Y.Z#subdirectory=tools/documentor documentor --version
   ```

   The output starts with `documentor X.Y.Z`.

Neither release workflow reads documentor's own version. Only the `pyproject.toml` and `__init__.py` edits in step 2 keep `documentor --version` matched to the tag. The `release-version-guard` workflow deletes a pushed tag and its release when the plugin manifests disagree with the tag.

`uv run just sync-helix` writes `in-repo` to `src/documentor/catalog/helix/HELIX_VERSION`. An installed wheel reports that label as `HELIX catalog packaged in-repo`.
