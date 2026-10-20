<!-- helix:publish audience=developer page=embedding kind=how-to voice=onboarding budget=1100 written=agent-opus reviewed=2026-10-20/second-reader-site-check/ccc7acaf587b0fd5 -->
<!-- helix:gap artifact:examples -->
<!-- helix:source README.md#install sha256:11003d4123be1f55 -->
<!-- helix:source README.md#what-it-reads-and-writes sha256:55f9002fc000e454 -->
<!-- helix:source src/documentor/__init__.py sha256:b5853dda7e0aef19 -->
<!-- helix:source src/documentor/cli.py sha256:63fa5bcbdc82b569 -->
<!-- helix:source src/documentor/generate.py sha256:92dcfeb4e275656d -->
<!-- helix:source src/documentor/write.py sha256:8ad5661054a3cc34 -->
<!-- helix:source src/documentor/lib.py sha256:651c08a95ae80112 -->
<!-- helix:source pyproject.toml sha256:95efaa59d25e6f0a -->
<!-- helix:source docs/helix/01-frame/prd.md#requirements sha256:faab177063c3e4e8 -->
# Embedding the library

A host embeds documentor in one of three ways: it runs the `documentor` command, calls `documentor.cli.main` from Python, or ships a generator that documentor loads. The package exports only `__version__`, so `main` and the generator entry point are the contract.

## Install

To run the command, install documentor as a tool. To call `main` or register a generator, add it as a dependency. Either way, set `<tag>` to the HELIX release that contains documentor (v0.19.0 or later). The host's CI reaches documentor through `uvx`, without vendoring it (PRD R-8).

```sh
uv tool install "git+https://github.com/DocumentDrivenDX/helix@<tag>#subdirectory=tools/documentor"
# or, one-off:
uvx --from "git+https://github.com/DocumentDrivenDX/helix@<tag>#subdirectory=tools/documentor" documentor --version
```

Expected result:

```text
documentor 0.1.0 (HELIX catalog in-repo)
```

A tool install is isolated, so the host's interpreter cannot import documentor from it. To call it from Python, add the same URL to the host's own environment:

```sh
uv add "documentor @ git+https://github.com/DocumentDrivenDX/helix@<tag>#subdirectory=tools/documentor"
# or, without uv:
pip install "git+https://github.com/DocumentDrivenDX/helix@<tag>#subdirectory=tools/documentor"
```

```sh
python -c "import documentor; print(documentor.__version__)"
```

Expected result:

```text
0.1.0
```

The host needs Python 3.11 or later, and the only runtime dependency is PyYAML. Hugo is needed only to build a new site, and Go only for the Hextra theme.

## Configure

The host's configuration is the `publish:` block in its `.helix.yml`. `documentor init` detects what the repository is and proposes that block. What it writes depends on the state of `.helix.yml`:

| Host state | What `documentor init` does |
|---|---|
| No `.helix.yml` | Writes `.helix.yml` with the HELIX marker and the block, and creates the `docs/helix/` activity folders. No `--write` is needed. |
| `.helix.yml` without `publish:` | Prints the block. With `--write`, appends it to the file. |
| `publish.traits` already set | Prints the proposal for comparison and changes nothing. |

```sh
documentor init --root /path/to/host
```

The smallest working block names the schema, the traits, and the audiences. This is the block documentor uses for itself:

```yaml
publish:
  schema: 1
  traits: [python-cli, python-library]
  audiences: [developer, user]
  out: docs/guide
  skip: [developer/api]
```

The full set of keys is in the README under [What it reads and writes](../../../README.md#what-it-reads-and-writes).

The `write` command calls an agent that the host chooses. The command comes from `--agent`, then `DOCUMENTOR_AGENT`, then `publish.agent.command`, then the default. The models come from `--model` and `--reviewer-model`, then `publish.agent.writer` and `publish.agent.reviewer`.

```yaml
publish:
  agent:
    command: "claude -p --model {model} --allowedTools Read,Glob,Grep --output-format text"   # the default
    writer: opus      # the default
    reviewer: sonnet  # the default
```

The agent reads its prompt on standard input and answers on standard output. Any `{model}` in the command is replaced by the model name.

## First call

The first call is `check`, because it changes no files and reports the state of every page. After `init`, no written pages exist yet, so expect `check` to return 1.

```sh
documentor check --root /path/to/host; echo "exit $?"
```

The report comes in this order:

1. Each page under its audience, with its state (`ok`, `MISSING`, `STALE`, `REVIEW`, `ADOPT`, `->`, or `EMPTY`).
2. The architecture views' state, then the written pages for the agent, in order.
3. The count line, for example `checks: 0 blocking, 0 warnings`.
4. Up to ten `BLOCKING` lines, then up to ten `MISSING`, `STALE`, `UNREVIEWED`, or `UNADOPTED` lines.

The exit code is 0 only when nothing is unfinished. To get from a new host to a passing `check`, write the pages and then build:

```sh
documentor write --root /path/to/host --dry-run   # print the prompts; call no agent
documentor write --root /path/to/host             # write the missing and stale pages; evaluate the unreviewed ones
documentor build --root /path/to/host             # regenerate the generated pages, check, build the site
documentor check --root /path/to/host
```

`write` sends an unreviewed page back to the writer when its own checks find a blocking or prose problem, and the writer receives those findings.

From Python, `main` takes the same arguments as a list and returns the exit code:

```python
from documentor.cli import main

code = main(["check", "--root", "/path/to/host"])
```

`main` prints its report to standard output and its errors to standard error. For output a host can parse, `status --format json` prints every page and the views' state as JSON:

```python
main(["status", "--root", "/path/to/host", "--format", "json"])
```

A Python distribution can add a generator by registering a function in the `documentor.generators` entry-point group. The function takes the root and a page dictionary, and returns the body and the source globs:

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

A page then names it with `generated: my-tables`. An empty body marks the page empty, and a packaged generator of the same name wins. A host that would rather not ship Python can name a command: `generated: {command: ..., sources: [...]}`.

## Errors and their meaning

The guide commands (`init`, `status`, `build`, `write`, `check`, `review`, `adopt`) return 0, 1, or 2, and the host branches on that code. The tools (`generate`, `site`, `present`, `estate`, and the rest) return their own codes, and `views` always returns 0.

| Code | Meaning | Host's response |
|---|---|---|
| 0 | Done; for `check`, nothing blocks and every page is current. | Continue. |
| 1 | Something needs doing: a blocking finding, a missing, stale, unreviewed, or unadopted page, or stale views. | Fail the pull request; `status` lists the work in order. |
| 2 | Usage or configuration error. | Fix the call or `.helix.yml`; retrying will not help. |

The guide commands print these lines to standard error and return 2:

| Message (standard error) | Cause |
|---|---|
| `No guide yet: run \`documentor init\` first.` | `.helix.yml` names no audiences. |
| `documentor: "unknown trait(s) in .helix.yml publish.traits: …"` | A trait is in neither the catalog nor the project's trait directory. |
| `documentor write: the writer and the evaluator must be different models` | Both models resolved to the same name. |
| `documentor write: … is not a written page of the guide` | `write PAGE` named a generated, delegated, or unknown page. |

`write` reports every page it could not finish, then returns 1. Each page gets a `LEFT <page>:` line on standard error, followed by up to eight indented problems:

```text
LEFT docs/guide/developer/embedding.md:
  agent call timed out after 900s
```

| Indented problem | Cause |
|---|---|
| `agent command not found: …` | The agent command is not on the path. |
| `agent call timed out after 900s` | One agent call ran past its limit. |
| `agent exited N: …` | The agent failed; the first 400 characters of its output follow. |
| A check finding | The page the writer returned has problems the writer's checks found. |
| `the evaluator failed it twice: …` | The evaluator rejected the page, and the revision too. |
| `passed the evaluation, but its checks block the stamp (above)` | The evaluator passed the page, but `review` refused to stamp it. |

Some failures escape `main` as exceptions, so a host that calls `main` from Python must catch them:

- `SystemExit(2)` from the argument parser, when a command or flag is unknown, or `review` and `adopt` miss a required argument.
- A YAML error from a malformed `.helix.yml`, which `config_of` reads without a guard.
- Any exception from importing a plug-in generator, because `load_plugins` calls `entry.load()` without a guard.
- Any exception raised inside a plug-in generator, which is called without a guard.

A project command that exits non-zero, or prints nothing, is not an error. Its page is marked empty, and `status` says to add the source or skip the page.

<details>
<summary>Where each code and message comes from</summary>

- Exit codes, the report order, and the tools' own codes: the docstring, `report`, `guide_main`, and `main` in `src/documentor/cli.py`.
- What `init` writes in each case: `init` in `src/documentor/cli.py`.
- The unknown-trait message: `src/documentor/lib.py`, printed through `print(f"documentor: {error}")`; the quotes come from the `KeyError`.
- The unguarded YAML read: `config_of` and `load_yaml` in `src/documentor/lib.py`.
- Agent errors, the 900-second limit, the `LEFT` problems, and which unreviewed pages go back to the writer: `call`, `findings_for`, and `run` in `src/documentor/write.py`.
- Plug-in loading with `entry.load()` and `setdefault`, and command generators: `load_plugins` and `render_command` in `src/documentor/generate.py`.

</details>

## Upgrading

To upgrade, move `<tag>` to the new HELIX release everywhere the host names it, then run `check`. The host names the tag in its tool install, its dependency, its `uvx` calls, and the CI workflow copied from `src/documentor/catalog/ci/github-actions.yml`.

```sh
uvx --from "git+https://github.com/DocumentDrivenDX/helix@<new-tag>#subdirectory=tools/documentor" documentor --version
uvx --from "git+https://github.com/DocumentDrivenDX/helix@<new-tag>#subdirectory=tools/documentor" documentor check --root .
```

`--version` reports the package and the HELIX catalog it carries. The audiences and the voice come from that catalog, so a new catalog can add pages or tighten prose limits. A host's passing `check` can then return 1 with no change to the host.

`publish.schema` versions the configuration contract, and this release reads schema 1 without rejecting other values.

The [Command line](cli.md) reference lists every command.
