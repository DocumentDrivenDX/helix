<!-- helix:publish audience=developer page=developer-guide kind=how-to voice=onboarding budget=1300 written=codex reviewed=2026-10-29/release-guide-independent-reader/4371ecc29c9f0645 -->
<!-- helix:source pyproject.toml sha256:c46e99a7fc3955ad -->
<!-- helix:source justfile sha256:33d64f77836eb9e1 -->
<!-- helix:source ../../.github/workflows/documentor.yml sha256:ab2fb8338de1a028 -->
<!-- helix:source ../../scripts/release-version.py sha256:ad55a7fa2e9e59a7 -->
<!-- helix:source ../../.github/workflows/release-ui.yml sha256:5ce416ac09060351 -->
<!-- helix:source ../../.github/workflows/release-genie-bundle.yml sha256:b0eea61fd244e8c7 -->
<!-- helix:source ../../.github/workflows/release-tag.yml sha256:5c17d163a7d2e7bd -->
<!-- helix:source ../../.github/workflows/release-version-guard.yml sha256:7a2f0f022c0b36b5 -->
<!-- helix:source ../../CONTRIBUTING.md sha256:d0027006597fad67 -->
<!-- helix:source README.md#development sha256:ec26429513feaa3e -->
<!-- helix:source src/documentor/__init__.py sha256:85f093e9f32ee453 -->
<!-- helix:source src/documentor/cli.py sha256:803cf572bdc9acb7 -->
<!-- helix:source src/documentor/report.py sha256:0f48cfca412184a2 -->
<!-- helix:source src/documentor/lib.py sha256:5db149c5af59118b -->
<!-- helix:source src/documentor/catalog/ci/github-actions.yml sha256:9f8ec1f2b471f001 -->
<!-- helix:source src/documentor/catalog/ux-builder/README.md sha256:6b885638317975c7 -->
<!-- helix:source tests/validate-package.sh sha256:ddc499febfa0dd79 -->
<!-- helix:source tests/validate-publish.sh sha256:7db3a03534402d2f -->
<!-- helix:source ../../scripts/sync_references.py sha256:97cfc74fe156811e -->
<!-- helix:source src/documentor/schemas.py sha256:6db23e6c01b889bc -->
<!-- helix:source src/documentor/umf_tables.py sha256:56c75007b5b2d2de -->
<!-- helix:source tests/python/test_schemas.py sha256:fed68ae9a073185b -->
<!-- helix:source tests/python/test_tempo_gaps.py sha256:270fdda9944cc658 -->
<!-- helix:source src/documentor/catalog/ci/github-pages.yml sha256:5656014516fa3a2d -->
# Developer guide

## Quick start

Clone HELIX and enter `tools/documentor`. Use Python 3.11+, [uv](https://docs.astral.sh/uv/), and `just`; Hugo enables the optional site-build tests.

```sh
git clone https://github.com/DocumentDrivenDX/helix
cd helix/tools/documentor
uv sync
uv run just test
```

`uv sync` creates `.venv` with the one runtime dependency (`pyyaml>=6`) and the `dev` group (`pytest>=8`). Each passing test script prints an `OK:` line. A failing script prints `FAIL:` with the reason and stops the run.

To check that the working copy's CLI runs:

```sh
uv run documentor --version
```

Inside the HELIX checkout, the output is `documentor <version> (HELIX catalog live /path/to/helix/workflows)`. An installed wheel reads its packaged copy and prints `HELIX catalog packaged`. `--catalog DIR` or the `DOCUMENTOR_CATALOG` variable names another catalog.

To see which optional tools the machine has (hugo, node, Chrome, LibreOffice, the agent CLI):

```sh
uv run documentor doctor
```

To run your working copy against another repository:

```sh
uv run documentor check --root ../some-repo
```

`uvx --from /path/to/documentor` caches its build of a local path. After a change, add `--refresh`, or use `uv run --project /path/to/documentor documentor ...`.

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
| `src/documentor/schemas.py` | Publishes referenced schemas and the pinned UMF browser |
| `src/documentor/umf_tables.py` | Reads UMF TableSpec sources for data references |
| `src/documentor/record.py` | Publishes the governed record (the HELIX root) into the site |
| `src/documentor/prose.py` | Prose checks against the voice profile |
| `src/documentor/theme.py` | Resolves the theme a project names |
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

documentor uses the `plain` theme when a project names no theme, or when the named theme cannot be fetched. Every other theme comes from `@ux-builder/tokens`, through `publish.theme`.

[Command line](cli.md) lists the CLI's commands. [Embedding the library](embedding.md) covers calling the package from Python.

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

Run one suite like this; on success the last line starts with `OK:`:

```sh
uv run just test-write
```

`just test-write` needs no agent credentials. The script writes a fake agent that answers writer and evaluator prompts and logs each call.

`just test-publish` checks that the built site has an `about` section titled "How this guide was made", with a `## The pages` list. Without Hugo, its `OK:` line ends with `(hugo not installed; build skipped)`, and the suite still passes.

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

To make a change, edit the module or catalog file, add an assertion to the matching test script, and run that suite before the full suite. HELIX's [AGENTS.md](../../../../../AGENTS.md) and [CONTRIBUTING.md](../../../../../CONTRIBUTING.md) set the contributor rules. Commit messages state the resulting behaviour in one sentence.

1. Create a branch from `main`:

   ```sh
   git switch -c my-change
   ```

2. Make the change. For example, to change which files a trait detects, edit its YAML under `src/documentor/catalog/traits/`.

3. Add an assertion to the matching script. Each script builds a scratch repository in a temporary directory, runs the CLI, and calls `fail` when a result is wrong:

   ```sh
   fail() { echo "FAIL: $*" >&2; exit 1; }
   ```

4. Run the suite, then everything. Every script ends with an `OK:` line:

   ```sh
   uv run just test-traits
   uv run just test
   ```

5. Try the change on a copy of a real repository. `init` detects what the repository is and proposes its guide. Without a `.helix.yml`, `init` writes one and creates the `docs/helix/` folders, even without `--write`:

   ```sh
   uv run documentor init --root ../some-repo
   ```

   Review the proposed traits and pages.

Three kinds of change follow their own path:

- **A new packaged generator** registers under `[project.entry-points."documentor.generators"]` in `pyproject.toml` as `name = "module:function"`. The function takes `(root, page)` and returns `(body, source_globs)`. A repository's own generator is a command under `generated:` in its `.helix.yml` and needs no entry point.
- **The HELIX catalog** (audiences, voice, deliverables, and the publishing and writing-pass references) comes from HELIX's `workflows/`. Change it there, then copy it rather than editing `src/documentor/catalog/helix/`:

  ```sh
  uv run just sync-helix
  ```

  The script prints `synced documentor floor -> tools/documentor/src/documentor/catalog/helix: N files`. When the copy and `workflows/` differ, `just test-catalog` lists each `stale:` or `extra:` file and fails.
- **The prose checks** in `src/documentor/prose.py` must stay byte-identical to `../../skills/helix/scripts/prose_audit.py`. Change both together, or `just test-catalog` fails.

A change to the CLI's behaviour may change the pages in `docs/guide/`. `uv run documentor status` lists every page of the repository's guide and what each needs next, such as missing, stale, or unreviewed:

```sh
uv run documentor status
```

When written pages name a HELIX artifact the repository lacks, the report ends with `Artifacts that would improve the guide`. Each line names the artifact and the pages written without it, most pages first. Once HELIX supplies that artifact, the listed pages are rewritten from it.

## Checking schema publication

Run schema, adoption, and full tests:

```sh
uv run python -m pytest -q tests/python/test_schemas.py tests/python/test_tempo_gaps.py
uv run just test
```

These cover schema and adoption behavior. Configure the release placeholder in `src/documentor/catalog/ci/github-pages.yml` before deployment.

## Releasing

documentor ships under HELIX release tags.

Obtain a separately authorized release scope from the HELIX release owner before step 2 ([CONTRIBUTING.md](../../../../../CONTRIBUTING.md)).

1. Run the suites and guide check from `tools/documentor`:

   ```sh
   uv run just test
   uv run documentor check --root .
   ```

2. In GitHub's Releases UI, create a new `vX.Y.Z` tag on current `main`, write
   the release notes, and publish. The UI preparation workflow returns the
   release to draft and opens a version bump PR. GitHub Actions must have
   permission to create PRs in the repository.

3. Review and merge that `chore(release): vX.Y.Z` PR. The shared version script
   updates the three plugin manifests, documentor's package and runtime
   versions, and lockfile. It refreshes current guide source fingerprints;
   stale fingerprints still require review.

   The tag workflow checks all six versions. It corrects an existing draft's
   tag only when the intervening changes contain version metadata and guide
   source fingerprints alone. If unrelated changes land meanwhile, it stops
   for the release owner to resolve the scope.

   It then dispatches bundle
   publication, which validates versions before any build or upload and
   publishes the draft with new assets. The original release notes survive.

   For local preparation, run from the HELIX root and open a
   `chore(release): vX.Y.Z` PR:

   ```sh
   python3 scripts/release-version.py vX.Y.Z --write
   ```

4. Check the release from the tag. The output starts with `documentor X.Y.Z`:

   ```sh
   uvx --from git+https://github.com/DocumentDrivenDX/helix@vX.Y.Z#subdirectory=tools/documentor documentor --version
   ```

The version guard checks the requested tag on manual runs. It returns invalid
UI releases to draft without deleting tags. A valid published release is not
retagged automatically; corrections normally use a new patch version.

An installed wheel reports its catalog as `HELIX catalog packaged <version>`, the release it shipped in.
