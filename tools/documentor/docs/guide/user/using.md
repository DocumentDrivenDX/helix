<!-- helix:publish audience=user page=using kind=how-to voice=public-site budget=1500 written=codex reviewed=2026-10-29/codex-independent-reader/cf297cc06fff6db1 -->
<!-- helix:gap artifact:feature-specification -->
<!-- helix:gap artifact:user-stories -->
<!-- helix:source README.md#use sha256:1668b6192a52a5d5 -->
<!-- helix:source src/documentor/cli.py sha256:861322ae490496ea -->
<!-- helix:source src/documentor/write.py sha256:208f5a662b7501e4 -->
<!-- helix:source src/documentor/site.py sha256:3016a940e892ea14 -->
<!-- helix:source src/documentor/report.py sha256:0f48cfca412184a2 -->
<!-- helix:source src/documentor/catalog/ci/github-actions.yml sha256:9f8ec1f2b471f001 -->
<!-- helix:source src/documentor/schemas.py sha256:85cb75a98dd24995 -->
<!-- helix:source src/documentor/catalog/ci/github-pages.yml sha256:010c78c212500279 -->
# Using the product

documentor builds and maintains the repository's *guide*. Follow these tasks in order.

Run from the repository root or pass `--root DIR`. Start with [Getting started](index.md) for a new guide.

Settings live in `.helix.yml` under `publish:`. Its `schema` must match documentor: `status`, `build`, `write`, `check`, and `prompt` reject mismatches; `init`, `review`, and `adopt` do not check it.

## See what the guide needs

```sh
documentor status
documentor status --format json
```

`status` lists every page of the guide under its audience, with the page's state and what it needs next. [Getting started](index.md#your-first-task-one-worked-session-step-by-step) explains each state mark.

`For the agent` orders work: adopt, write missing pages, update stale pages, evaluate.

A *written page* needs explanation, so an AI agent writes it. If the agent lacked a planning document it was told to read, the page's row says `written without` and names that document.

`status` groups those missing documents under `Artifacts that would improve the guide`, the one that would improve the most pages first. Add that document under `docs/helix/` and rewrite its pages to cover more.

## Write the missing and stale pages

```sh
documentor write
documentor write docs/guide/user/about.md     # one page only, rewritten whatever its state
documentor write --dry-run                    # print the prompts, call nothing
```

With no page named, `write` works through the written pages that are missing, stale, or not yet evaluated. It leaves current pages alone. A *stale* page cites a source file that has changed since the page was written.

Missing and stale pages are written. A page not yet evaluated is only evaluated, unless its own checks find problems, such as a broken link or a banned phrase. Those send it back to the writer first, because they would block an evaluation. Naming a page forces a rewrite and replaces its earlier evaluation.

For each page, `write` does this:

1. One agent call writes the page from its plan: the reader's task, the sections, the word budget, and where to look.
2. documentor adds the header, records the sources, and runs the page checks. If a check fails, the agent revises the page once.
3. A second call, on a different model, evaluates the page against its task and sources.
4. A pass is recorded on the page. A fail sends the evaluator's notes back for one revision, then a second evaluation.

An existing page is revised, not replaced. The agent gets the current page, which sources moved, and what the checks found. A link to a guide page not yet written does not count as a finding.

Every page is written before any is evaluated, so links between new pages resolve first. The run ends with `wrote or evaluated N of M pages`. Unfinished pages are listed under `LEFT` with their problems, and the command exits with status 1.

### See what the agent is told

```sh
documentor prompt docs/guide/user/about.md
documentor prompt docs/guide/user/about.md --reviewer
```

`prompt` prints the brief the writing agent gets for one written page, and calls no agent. Name the page by its path or as audience/id. The brief includes the voice rules and HELIX's writing-pass rules. Add `--reviewer` to print the evaluator's brief, which names the repository folder and the page by their full paths.

### Why it asks for two models

A page never counts as evaluated by its own writer. `write` stops at once if the writer and the evaluator are the same model. By default the writer is `opus` and the evaluator is `sonnet`.

| Option | What it changes |
|---|---|
| `--model M` | The model that writes pages. |
| `--reviewer-model M` | The model that evaluates pages. It must differ from the writer. |
| `--agent CMD` | The agent command. `{model}` in it is replaced by the model name. |
| `--dry-run` | Prints each prompt and calls no agent. |

The default agent is Claude Code run headless, allowed only to read files. The `DOCUMENTOR_AGENT` environment variable names another command. So does `publish.agent` in `.helix.yml`, with the keys `command`, `writer`, and `reviewer`.

The agent needs credentials, so run `write` on a machine that has them. If the agent command is not installed, `write` names both places to set it, and `documentor doctor` reports it. Each agent call has a limit of 900 seconds.

## Evaluate a page yourself

```sh
documentor review docs/guide/user/about.md --by your-name
```

Use `review` when a person, not the evaluating agent, reads a page against its sources and task. It records your name, the date, and a fingerprint of the page's text in the page header.

`review` refuses in three cases:

- **You wrote the page.** If `--by` matches the page's writer, another reader must evaluate it.
- **A check still fails.** It prints each finding and records nothing until you fix them.
- **The page has no header.** Only pages that belong to the guide can be evaluated.

The evaluation lapses as soon as the page's text changes.

## Bring in a page you already wrote

```sh
documentor adopt docs/how-to/deploy.md --audience operator --kind how-to --source infra/main.tf
```

`adopt` brings a hand-written page into the guide without changing its text. It adds a header naming the audience, the page kind, and any sources given with `--source`, which you can repeat.

A change to a named source makes the page stale, so `check` reminds you to update it. Without `--kind`, the command tells you to add the kind to the header yourself.

`status` marks pages to adopt with `ADOPT` and prints the exact `adopt` command.

## Build the site

```sh
documentor doctor               # which site and agent tools this machine has
documentor build                # regenerate, check, and build the site
documentor build --no-site      # everything except the site
documentor build --write        # also write and evaluate pages first, as in `write`
documentor build --site DIR     # put a new site somewhere other than the default
```

`build` regenerates every generated page and the architecture drawings, then shows the same list as `status`. It reports the count of blocking findings and warnings, then builds the site.

The site goes where your repository already publishes:

| Your repository has | What documentor does |
|---|---|
| A `mkdocs.yml` | Copies the pages under its docs folder and writes a `nav.yml` fragment for you to include. |
| A Hugo site | Adds the pages as a section of the folder the site reads its content from. |
| No site | Writes a new site in documentor's own layout, by default into `.helix/site` under the repository root. |

A new site needs only Hugo. For the Hextra theme, set `site.target: hextra` under `publish:` in `.helix.yml`; it also needs Go, and the network once. `documentor doctor` marks each tool `ok` or `missing`.

For an existing Hugo site, the content folder is the one its `module.mounts` maps to `content`, or else its `content/` folder. Set `site_dir` or `content_root` under `publish.site` to choose another. Files a guide page links go beside the pages. Schema publication separately writes the browser, catalog, and source downloads into the site's static folder.

A Hugo site and a new site also get a page named "How this guide was made", rebuilt at every build. In a new site it is its own section; in an existing Hugo site it sits inside the guide's section. It shows:

- the repository traits detection found, with the evidence for each
- every page, with its kind, who made and evaluated it, its source count, and its state
- the architecture views and the site's other sections
- the HELIX planning documents that would improve the guide, as `status` lists them

Two more settings under `publish.site` add sections the guide does not write:

| Setting | What it adds |
|---|---|
| `record` | The HELIX planning documents, published into the site. |
| `sections` | Generated sections; each runs its `command` from the repository root. |

A section's command gets `DOCUMENTOR_SECTION_OUT`, set to that section's folder in the site. If the command fails, `build` stops.

In a new site, `build` lists the record and each generated section in the navigation, ahead of "How this guide was made". A section appears only once its folder exists in the site. The record's navigation title is `Record` unless `record_title` under `publish.site` names another.

### Look at the built pages

```sh
documentor site --shots
```

`documentor site --shots` builds the site, then screenshots each page on a desktop, in dark mode, and at phone width. It writes an `index.html` to browse them and reports any page wider than its screen. It needs `node` and `npm`.

The screenshots go into `shots` beside a new site, or into `.helix/shots` for an existing Hugo site. For a `mkdocs.yml` site, `--shots` takes no screenshots.

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

To run the gate on every pull request, copy the CI template into your repository as `guide.yml` in the .github/workflows folder. The template ships inside the `documentor` package at `src/documentor/catalog/ci/github-actions.yml`. It is also in the [HELIX repository](https://github.com/DocumentDrivenDX/helix/blob/main/tools/documentor/src/documentor/catalog/ci/github-actions.yml). Set its `DOCUMENTOR` variable to the HELIX release you use.

## Publish design schemas

Install the browser at the site root: Hugo, static, and Hextra assembly publishes declared schemas and discovered UMF tables with provenance and downloads. For plain Hugo, run:

```sh
npm install --save-exact @documentdrivendx/umf-schema-browser@2.0.0
```

Declare existing sources using the [schema-reference format](../../../src/documentor/catalog/helix/references/umf-schemas.md).

```sh
documentor schemas --root .
documentor schemas --root . --check
```

Publication rejects missing or conflicting references and stale output; browsing does not validate application data. Adapt `src/documentor/catalog/ci/github-pages.yml` for deployment.

## Keep the guide current

The same workflow file also runs every Monday. It regenerates the generated pages and drawings and opens a pull request with the changes on a branch named `guide/refresh`.

The weekly job does not write pages, because writing needs an agent and credentials. When a written page goes stale, run `documentor write` on your machine to revise it, then push the result.
