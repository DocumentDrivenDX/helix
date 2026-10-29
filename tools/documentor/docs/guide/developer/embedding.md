<!-- helix:publish audience=developer page=embedding kind=how-to voice=onboarding budget=1100 written=codex reviewed=2026-10-29/codex-astra-independent-reader/bb6276d19ee44b28 -->
<!-- helix:gap artifact:examples -->
<!-- helix:source README.md#install sha256:11003d4123be1f55 -->
<!-- helix:source README.md#what-it-reads-and-writes sha256:55f9002fc000e454 -->
<!-- helix:source src/documentor/__init__.py sha256:e612d1e2f68f2667 -->
<!-- helix:source src/documentor/cli.py sha256:8b7a0be0b2efb9cb -->
<!-- helix:source src/documentor/report.py sha256:0f48cfca412184a2 -->
<!-- helix:source src/documentor/generate.py sha256:9ed3906b7fe2bc36 -->
<!-- helix:source src/documentor/write.py sha256:208f5a662b7501e4 -->
<!-- helix:source src/documentor/lib.py sha256:5db149c5af59118b -->
<!-- helix:source src/documentor/catalog/ci/github-actions.yml sha256:9f8ec1f2b471f001 -->
<!-- helix:source pyproject.toml sha256:74a08b4781a32616 -->
<!-- helix:source src/documentor/schemas.py sha256:6db23e6c01b889bc -->
<!-- helix:source src/documentor/detect.py sha256:376f1dd87ec38e48 -->
<!-- helix:source src/documentor/umf_tables.py sha256:56c75007b5b2d2de -->
<!-- helix:source src/documentor/site.py sha256:1d8a815021485d27 -->
# Embedding the library

A host can embed documentor in three ways. It can run the `documentor` command, call `documentor.cli.main` from Python, or ship a generator that documentor loads. The package exports only `__version__`, so `main` and the generator entry point are the contract.

## Install

Install documentor as a tool to run the command, or as a dependency to call `main` or register a generator. `<tag>` is a HELIX release that contains documentor. The host's CI runs documentor through `uvx` and does not vendor it (`src/documentor/catalog/ci/github-actions.yml`).

```sh
uv tool install "git+https://github.com/DocumentDrivenDX/helix@<tag>#subdirectory=tools/documentor"
# or, one-off:
uvx --from "git+https://github.com/DocumentDrivenDX/helix@<tag>#subdirectory=tools/documentor" documentor --version
```

Expected result, from an install:

```text
documentor <version> (HELIX catalog packaged <version>)
```

`<version>` is the release: documentor and the catalog it carries ship together.

For Python imports, install into the host environment too:

```sh
uv add "documentor @ git+https://github.com/DocumentDrivenDX/helix@<tag>#subdirectory=tools/documentor"
# or, without uv:
pip install "git+https://github.com/DocumentDrivenDX/helix@<tag>#subdirectory=tools/documentor"
```

```sh
python -c "import documentor; print(documentor.__version__)"
```

Requires Python 3.11+.

## Configure

The host configures documentor in the `publish:` block of its `.helix.yml`, and `documentor init` proposes that block:

| Host state | What `documentor init` does |
|---|---|
| No `.helix.yml` | Writes `.helix.yml` with the HELIX marker and the block, and creates the `docs/helix/` activity folders. |
| `.helix.yml` without `publish:` | Prints the block; `--write` appends it. |
| `publish.traits` already set | Prints the proposal and changes nothing. |

```sh
documentor init --root /path/to/host
```

The smallest working block names the schema, the traits, and the audiences. documentor's own block is:

```yaml
publish:
  schema: 1
  traits: [python-cli, python-library]
  audiences: [developer, user]
  out: docs/guide
  skip: [developer/api, user/whats-new]
```

The README lists every key under [What it reads and writes](../../../README.md#what-it-reads-and-writes).

`write` calls an agent the host chooses. The command comes from `--agent`, `DOCUMENTOR_AGENT`, `publish.agent.command`, or the default, in that order. The models come from `--model` and `--reviewer-model`, then `publish.agent.writer` and `publish.agent.reviewer`.

```yaml
publish:
  agent:
    command: "claude -p --model {model} --allowedTools Read,Glob,Grep --output-format text"   # the default
    writer: opus      # the default
    reviewer: sonnet  # the default
```

The agent reads its prompt on standard input and answers on standard output. Any `{model}` in the command becomes the model name.

The HELIX catalog supplies the audiences and the voice. documentor takes it from `--catalog DIR`, `DOCUMENTOR_CATALOG`, a HELIX checkout that contains the tool, or the packaged copy, in that order. The directory is laid out like HELIX's `workflows` folder.

```sh
documentor --catalog /path/to/helix/workflows check --root /path/to/host
```

Init proposes design-stage skips or operational data pages when applicable; existing publish settings remain authoritative. The `umf-tablespec` trait adds table references and browser sources; tablespec pipelines coexist separately.

## First call

The first call is `check`, because it changes no files and reports every page's state. After `init`, no written pages exist, so `check` returns 1.

```sh
documentor check --root /path/to/host; echo "exit $?"
```

The report lists each page under its audience with its state: `ok`, `MISSING`, `STALE`, `REVIEW`, `ADOPT`, `->`, or `EMPTY`. The views' state follows. When a page records a gap, the HELIX artifacts that would improve the guide come next, with the pages each would rewrite.

Then come the written pages in `documentor write` order and a count line, such as `checks: 0 blocking, 0 warnings`. Up to ten `BLOCKING` lines follow, then up to ten `MISSING`, `STALE`, `UNREVIEWED`, or `UNADOPTED` lines.

To bring a new host to exit 0, write the pages, then build:

```sh
documentor write --root /path/to/host --dry-run   # print the prompts; call no agent
documentor write --root /path/to/host             # write the missing and stale pages; evaluate the unreviewed ones
documentor build --root /path/to/host             # regenerate the generated pages, check, build the site
documentor check --root /path/to/host
```

`prompt` prints one page's writer brief, and `--reviewer` prints the evaluator's:

```sh
documentor prompt developer/embedding --root /path/to/host
documentor prompt developer/embedding --reviewer --root /path/to/host
```

From Python, `main` takes the same arguments as a list and returns the exit code. It prints its report to standard output and its errors to standard error.

```python
from documentor.cli import main

code = main(["check", "--root", "/path/to/host"])
```

`status --format json` returns JSON:

```python
main(["status", "--root", "/path/to/host", "--format", "json"])
```

A Python distribution adds a generator by registering a function in the `documentor.generators` entry-point group. The function takes the root and a page dictionary, and returns the body and the source globs:

```toml
[project.entry-points."documentor.generators"]
my-tables = "my_package.guide:tables"
```

```python
from pathlib import Path

def tables(root: Path, page: dict) -> tuple[str, list[str]]:
    """One line for `documentor generate --list`."""
    return "| Table | Columns |\n|---|---|\n", ["specs/*.yml"]
```

Use `generated: my-tables`; an empty body marks it empty. Avoid packaged names listed by `documentor generate --list`. Non-Python hosts can use `generated: {command: ..., sources: [...]}`.

## Publish design schemas

Install the browser at the site root: `src/documentor/schemas.py` defines its version and reference fields; `publish.schemas.browser_package` overrides its location.

```sh
npm install --save-exact @documentdrivendx/umf-schema-browser@2.0.0
```

Declare existing sources using the [schema-reference format](../../../src/documentor/catalog/helix/references/umf-schemas.md).

```python
from documentor.cli import main

code = main(["schemas", "--root", "/path/to/host"])
code = main(["schemas", "--root", "/path/to/host", "--check"])
```

Site assembly publishes schemas; Hugo needs generation first. Unowned collisions fail; unrelated files survive. Browsing proves no semantic conformance.

## Errors and their meaning

Guide commands return 0, 1, or 2. Tools have their own codes; `views` always returns 0.

| Code | Meaning | Host's response |
|---|---|---|
| 0 | Done; for `check`, nothing blocks and every page is current. | Continue. |
| 1 | Work remains: a blocking finding, stale views, or a missing, stale, unreviewed, or unadopted page. | Fail the pull request; `status` lists the work. |
| 2 | Usage or configuration error. | Fix the call or `.helix.yml`; retrying will not help. |

These messages go to standard error with exit code 2:

| Message (standard error) | Cause |
|---|---|
| `documentor: .helix.yml publish.schema is …; this documentor reads schema 1. …` | `publish.schema` is not the schema this release reads. |
| `No guide yet: run \`documentor init\` first.` | `.helix.yml` names no audiences. |
| `documentor: "unknown trait(s) in .helix.yml publish.traits: …"` | A trait is in neither the catalog nor the project's trait directory. |
| `documentor write: the writer and the evaluator must be different models` | Both models resolved to the same name. |
| `documentor write: … is not a written page of the guide` | `write PAGE` named a generated, delegated, or unknown page. |
| `documentor prompt: name one written page, as audience/id or its path (…)` | `prompt` named no page, or no written page. |
| `documentor: --catalog needs a directory laid out like HELIX's workflows/` | `--catalog` is the last argument. |

`write` returns a page to the writer when its checks would block the stamp. It reports each unfinished page on standard error as a `LEFT <page>:` line with up to eight indented problems, then returns 1:

```text
LEFT docs/guide/developer/embedding.md:
  agent call timed out after 900s
```

| Indented problem | Cause |
|---|---|
| `agent command not found: …` | The agent command is not on the path. |
| `agent call timed out after 900s` | One agent call ran past its limit. |
| `agent exited N: …` | The agent failed; the first 400 characters of its output follow. |
| A check finding | The writer's checks found problems in the returned page. |
| `the evaluator failed it twice: …` | The evaluator rejected the page and its revision. |
| `passed the evaluation, but its checks block the stamp (above)` | `review` refused to stamp a page the evaluator passed. |

These exceptions escape `main`, and a Python host must catch them:

- `SystemExit(2)` from the argument parser: an unknown command or flag, or a missing argument to `review` or `adopt`.
- `SystemExit` with `documentor: … is not a HELIX catalog (no voice.yml and publish/audiences)`, when `--catalog` or `DOCUMENTOR_CATALOG` names another directory.
- A YAML error from a malformed `.helix.yml`.
- Any exception from importing or running a plug-in generator.

A project command that exits non-zero or prints nothing is not an error. documentor marks its page empty, and `status` says to add the source or skip the page.

<details>
<summary>Where each code and message comes from</summary>

- `src/documentor/cli.py` holds the exit codes, the report order, `init`, the schema check, `prompt`, `--catalog`, `--version`, and the tools' codes, in its docstring, `report`, `guide_main`, `init`, and `main`.
- In `src/documentor/lib.py`, `SCHEMA`, `helix_catalog`, and `helix_version` set the schema, the catalog order, the `packaged` and `live` forms, and the not-a-catalog exit. `config_of` and `load_yaml` read `.helix.yml` without a guard.
- `call`, `findings_for`, and `run` in `src/documentor/write.py` hold the agent errors, the 900-second limit, and the `LEFT` problems.
- In `src/documentor/generate.py`, `load_plugins` adds a plug-in only under a name no packaged generator holds. Neither it nor the generator call has a guard, and `render_command` runs command generators.

</details>

## Upgrading

To upgrade, move `<tag>` to the new HELIX release, then run `check`. The tag appears in the tool install, the dependency, the `uvx` calls, and the `DOCUMENTOR` variable of the CI workflow copied from `src/documentor/catalog/ci/github-actions.yml`.

```sh
uvx --from "git+https://github.com/DocumentDrivenDX/helix@<new-tag>#subdirectory=tools/documentor" documentor --version
uvx --from "git+https://github.com/DocumentDrivenDX/helix@<new-tag>#subdirectory=tools/documentor" documentor check --root .
```

A new catalog can add pages or tighten prose limits, so `check` can start returning 1 with no host change.

`publish.schema` versions the configuration contract, and this release reads schema 1. A missing `schema` counts as 1. Against any other schema, a guide command returns 2 and says to use the documentor from the block's HELIX release.
