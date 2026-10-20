<!-- helix:publish audience=user page=using kind=how-to voice=public-site budget=1500 written=agent-opus reviewed=2026-10-20/second-reader-move-review/4c959653c125ec36 -->
<!-- helix:gap artifact:feature-specification -->
<!-- helix:gap artifact:user-stories -->
<!-- helix:source README.md#use sha256:1668b6192a52a5d5 -->
<!-- helix:source src/documentor/cli.py sha256:63fa5bcbdc82b569 -->
<!-- helix:source src/documentor/write.py sha256:8ad5661054a3cc34 -->
<!-- helix:source src/documentor/site.py sha256:099a21eeb38e1388 -->
<!-- helix:source src/documentor/catalog/ci/github-actions.yml sha256:fa22a42e759b3fda -->
# Using the product

documentor builds a repository's documentation and keeps it current. That documentation is the repository's *guide*. Each task below is one you do regularly after your first session. They come in the order you are likely to meet them.

First you see what the guide needs, then write, evaluate, and bring in pages. Last, you build the site, pass the check, and keep the guide current.

Every command runs from the repository's root folder. You can also add `--root DIR` to run it against another folder. If the repository has no guide yet, start with [Getting started](index.md).

## See what the guide needs

```sh
documentor status
documentor status --format json
```

`status` lists every page of the guide under its audience. Each row shows the page's state and what it needs next. [Getting started](index.md#your-first-task-one-worked-session-step-by-step) explains what each state mark means.

The list ends with `For the agent`, an ordered work list. Pages to adopt come first, then missing pages, then stale ones, then ones nobody has evaluated. Work the list from the top.

A *written page* is one that needs explanation, so an AI agent writes it. Sometimes the agent writes a page without a planning document it was told to read. That page's row then says `written without` and names the document. Add that document under `docs/helix/` and rewrite the page if you want it to cover more.

`--format json` prints the same information as JSON, for scripts.

## Write the missing and stale pages

```sh
documentor write
documentor write docs/guide/user/about.md     # one page only, rewritten whatever its state
documentor write --dry-run                    # print the prompts, call nothing
```

Without a page named, `write` works through the written pages that are missing, stale, or not yet evaluated. It leaves current pages alone. A *stale* page is one where a file it cites as a source has changed since it was written.

Missing and stale pages are written. A page not yet evaluated is only evaluated, unless its own checks find problems. A broken link or a banned phrase, for example, sends it back to the writer first, because those findings would block an evaluation.

Naming a page forces a rewrite, whatever its state. A current page is revised and evaluated again, so its earlier evaluation is replaced. A page that only needed evaluating is revised as well. Name a page when you want it rewritten, not to evaluate it.

For each page it writes, the command does this:

1. One agent call writes the page from its plan: the reader's task, the sections, the word budget, and where to look.
2. documentor adds the header, records the sources, and runs the page checks. If a check fails, the agent revises the page once.
3. A second call, on a different model, evaluates the page against its task and sources.
4. A pass is recorded on the page. A fail sends the evaluator's notes back to the writer for one revision, then a second evaluation.

A page that already exists is revised, not replaced. The agent gets the current page and keeps the rest. It is also told which sources moved and what the page's checks found. A link to a guide page not yet written does not count as a finding.

Every page is written before any page is evaluated. Links between new pages then resolve before the evaluator reads them.

The run ends with `wrote or evaluated N of M pages`. Any page that could not be finished is listed under `LEFT`, with its problems. The command then exits with status 1. Fix the problems the list names, or run `write` again for that page.

### Why it asks for two models

A page never counts as evaluated by its own writer. `write` stops at once if the writer and the evaluator are the same model. By default the writer is `opus` and the evaluator is `sonnet`.

| Option | What it changes |
|---|---|
| `--model M` | The model that writes pages. |
| `--reviewer-model M` | The model that evaluates pages. It must differ from the writer. |
| `--agent CMD` | The agent command. `{model}` in it is replaced by the model name. |
| `--dry-run` | Prints each prompt and calls no agent. |

The default agent is Claude Code run headless, allowed only to read files. You can name another command with the `DOCUMENTOR_AGENT` environment variable. You can also set it in `.helix.yml` under `publish.agent`, with the keys `command`, `writer`, and `reviewer`. The agent needs credentials, so run `write` on a machine that has them.

If the agent command is not installed, `write` says so and names the two places to set it. Each agent call has a limit of 900 seconds.

## Evaluate a page yourself

```sh
documentor review docs/guide/user/about.md --by your-name
```

Use `review` when a person, not the evaluating agent, reads a page against its sources and task. It records your name, the date, and a fingerprint of the page's text in the page header.

`review` refuses in three cases, each for a reason:

- **You wrote the page.** If `--by` matches the page's writer, another reader must evaluate it.
- **A check still fails.** It prints each finding and records nothing until you fix them.
- **The page has no header.** Only pages that belong to the guide can be evaluated.

The evaluation lapses as soon as the page's text changes. `status` then shows the page as changed after its evaluation, and it needs evaluating again.

## Bring in a page you already wrote

```sh
documentor adopt docs/how-to/deploy.md --audience operator --kind how-to --source infra/main.tf
```

`adopt` brings a hand-written page into the guide without changing its text. It only adds a header at the top. That header names the audience, the page kind, and any sources you list with `--source`. You can repeat `--source`.

Name a source when the page describes that file. A change to the file then makes the page stale, so `check` reminds you to update it. Without `--kind`, the command tells you to add the kind to the header yourself.

`status` marks pages to adopt with `ADOPT` and prints the exact `adopt` command to run. A page that already has a header is refused. The path in the example above stands for your own page.

## Build the site

```sh
documentor build                # regenerate, check, and build the site
documentor build --no-site      # everything except the site
documentor build --write        # also write and evaluate pages first, as in `write`
documentor build --site DIR     # put a new site somewhere other than the default
```

`build` regenerates every generated page and the architecture drawings, then shows the same list as `status`. It then reports how many blocking findings and warnings the checks found, and builds the site.

The site goes where your repository already publishes:

| Your repository has | What documentor does |
|---|---|
| A `mkdocs.yml` | Copies the pages under its docs folder and writes a `nav.yml` fragment for you to include. |
| A Hugo site | Adds the pages as a section of its content. |
| No site | Writes a new Hextra site, by default into `.helix/site` under the repository root. |

A new Hextra site needs Hugo and Go to build, and the network once. To choose the target yourself, set `site.target` in `.helix.yml`.

The Markdown pages in the guide folder are the record. Whatever documentor writes into a site is rebuilt from them each time, so edit the pages, not the site.

## Pass the check before a pull request

```sh
documentor check
```

`check` is the gate. It regenerates the generated pages in memory and compares them with the files. It needs no agent and no network.

It exits with status 1 when any of these hold:

- a blocking finding, such as a broken link or text matching a pattern your `handling:` rules forbid
- a page that is missing, stale, not yet evaluated, or not yet adopted
- architecture drawings that no longer match their model

It prints up to ten unfinished pages, each with what it needs. Run `build` for generated pages and `write` for written ones, then check again.

To run the gate on every pull request, copy the CI template into your repository as `guide.yml` in the .github/workflows folder. Install documentor once, then copy `github-actions.yml` from the catalog's ci folder inside the installed `documentor` package. You can also take it from the [HELIX repository](https://github.com/DocumentDrivenDX/helix/blob/main/tools/documentor/src/documentor/catalog/ci/github-actions.yml). Set its `DOCUMENTOR` variable to the HELIX release you use.

## Keep the guide current

The same workflow file also runs once a week, on Mondays. It regenerates the generated pages and drawings and opens a pull request with the changes on a branch named `guide/refresh`.

The weekly job does not write pages, because writing needs an agent and credentials. When a written page goes stale, run `documentor status` on your machine to see which. Then run `documentor write` to revise them and push the result.

The full list of commands and options is in [Command line](../developer/cli.md).
