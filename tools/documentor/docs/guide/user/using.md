<!-- helix:publish audience=user page=using kind=how-to voice=public-site budget=1500 written=agent-opus reviewed=2026-10-27/agent-sonnet/f8672c964070da49 -->
<!-- helix:gap artifact:feature-specification -->
<!-- helix:gap artifact:user-stories -->
<!-- helix:source README.md#use sha256:1668b6192a52a5d5 -->
<!-- helix:source src/documentor/cli.py sha256:4fe81cf37df6d5aa -->
<!-- helix:source src/documentor/write.py sha256:2118376b2c167085 -->
<!-- helix:source src/documentor/site.py sha256:c715ad483398775f -->
<!-- helix:source src/documentor/visuals.py sha256:a800032637b6cd3b -->
<!-- helix:source src/documentor/report.py sha256:0f48cfca412184a2 -->
<!-- helix:source src/documentor/catalog/ci/github-actions.yml sha256:fa22a42e759b3fda -->
# Using the product

documentor builds a repository's documentation, its *guide*, and keeps it current.

Every command runs from the repository's root folder, or from the folder given with `--root DIR`. If the repository has no guide yet, start with [Getting started](index.md).

The guide's settings live in the `publish:` block of `.helix.yml`. Its `schema` number must match the schema your documentor reads. On a mismatch, `status`, `build`, `write`, `check`, and `prompt` stop and tell you to use the documentor from the block's HELIX release. `init`, `review`, and `adopt` do not check the schema.

## See what the guide needs

```sh
documentor status
documentor status --format json
```

`status` lists every page under its audience, with the page's state and what it needs next. [Getting started](index.md#your-first-task-one-worked-session-step-by-step) explains each state mark.

The list ends with `For the agent`, an ordered list of work: pages to adopt, then missing pages, then stale ones, then ones nobody has evaluated.

A *written page* needs explanation, so an AI agent writes it. When the agent lacked a planning document it was told to read, the page's row says `written without` and names it. `status` groups those documents under `Artifacts that would improve the guide`, most useful first. Add that document under `docs/helix/` and rewrite its pages.

## Write the missing and stale pages

```sh
documentor write
documentor write docs/guide/user/about.md     # one page only, rewritten whatever its state
documentor write --dry-run                    # print the prompts, call nothing
```

With no page named, `write` works through the written pages that are missing, stale, or not yet evaluated. A *stale* page cites a source file that has changed since the page was written. Current pages are left alone.

A page not yet evaluated is only evaluated, unless its own checks find problems, such as a broken link or a banned phrase. Those problems send it back to the writer first. Naming a page forces a rewrite and replaces its earlier evaluation.

For each page, `write` does this:

1. One agent call writes the page from its plan: the reader's task, the sections, the word budget, and where to look.
2. documentor adds the header, records the sources, and runs the page checks. If a check fails, the agent revises the page once.
3. A second call, on a different model, evaluates the page against its task and sources.
4. A pass is recorded on the page. A fail sends the evaluator's notes back for one revision, then a second evaluation.

An existing page is revised, not replaced: the agent gets the current page, the moved sources, and the check findings. A link to a guide page not yet written is not a finding.

Every page is written before any is evaluated, so links between new pages resolve first. The run ends with `wrote or evaluated N of M pages`. Unfinished pages are listed under `LEFT` with their problems, and the command exits with status 1.

### See what the agent is told

```sh
documentor prompt docs/guide/user/about.md
documentor prompt docs/guide/user/about.md --reviewer
```

`prompt` prints the brief the writing agent gets for one written page, and calls no agent. Name the page by its path or as audience/id. Add `--reviewer` to print the evaluator's brief instead.

### Why it asks for two models

A page never counts as evaluated by its own writer. `write` stops at once if the writer and the evaluator are the same model. By default the writer is `opus` and the evaluator is `sonnet`.

| Option | What it changes |
|---|---|
| `--model M` | The model that writes pages. |
| `--reviewer-model M` | The model that evaluates pages. It must differ from the writer. |
| `--agent CMD` | The agent command. `{model}` in it is replaced by the model name. |
| `--dry-run` | Prints each prompt and calls no agent. |

The default agent is Claude Code, run headless and allowed only to read files. The `DOCUMENTOR_AGENT` environment variable or `publish.agent` in `.helix.yml` names a different command. `publish.agent` takes the keys `command`, `writer`, and `reviewer`.

The agent needs credentials, so run `write` on a machine that has them. If the agent command is missing, `write` names both places to set it, and `documentor doctor` reports it. Each agent call has a limit of 900 seconds.

## Evaluate a page yourself

```sh
documentor review docs/guide/user/about.md --by your-name
```

Use `review` when a person evaluates a page against its sources and task. It records your name, the date, and a fingerprint of the page's text in the page header.

`review` refuses in three cases:

- **You wrote the page.** If `--by` matches the page's writer, another reader must evaluate it.
- **A check still fails.** It prints each finding and records nothing.
- **The page has no header.** Only guide pages can be evaluated.

The evaluation lapses as soon as the page's text changes.

## Bring in a page you already wrote

```sh
documentor adopt docs/how-to/deploy.md --audience operator --kind how-to --source infra/main.tf
```

`adopt` brings a hand-written page into the guide without changing its text. It adds a header naming the audience, the page kind, and the sources you give with `--source`, which you can repeat.

When a named source changes, the page becomes stale and `check` reminds you to update it. Without `--kind`, the command tells you to add the kind to the header yourself. `status` marks pages to adopt with `ADOPT` and prints the exact `adopt` command.

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

A new site needs only Hugo. For the Hextra theme, set `site.target: hextra` under `publish:`; Hextra also needs Go, and the network once. `documentor doctor` marks each tool `ok` or `missing`.

For an existing Hugo site, the content folder is the one its `module.mounts` maps to `content`, otherwise its `content/` folder. Set `site_dir` or `content_root` under `publish.site` to choose another.

A Hugo site and a new site also get a page named "How this guide was made", rebuilt at every build. It shows:

- the repository traits that detection found, with evidence
- every page, with its kind, maker, evaluator, source count, and state
- the architecture views and the site's other sections
- the planning documents that would improve the guide

Two more settings under `publish.site` add sections the guide does not write:

| Setting | What it adds |
|---|---|
| `record` | The HELIX planning documents, published into the site. |
| `sections` | Generated sections. Each one runs its `command` from the repository root. |

A section's command gets `DOCUMENTOR_SECTION_OUT`, set to that section's folder in the site. If the command fails, `build` stops. In a new site, the record and each section whose folder exists appear in the navigation. The record's title is `Record` unless `record_title` under `publish.site` names another.

### Draw the architecture as visuals

A *visual* is a drawing of one view of the repository's architecture model, in the site's theme. Turn visuals on with `publish.visuals` in `.helix.yml`:

```yaml
publish:
  visuals: ux-builder                # or {renderer: ux-builder, command: "node …/cli.mjs"}
```

```sh
documentor visuals              # write and draw every visual
documentor visuals --check      # write nothing; fail when a visual no longer matches its source
documentor visuals --no-draw    # write the visual documents but do not draw them
```

With visuals on, `build` writes and draws them too. `check` and `status` report a visual that is missing, stale, not drawn, or left without a source, and tell you to run `documentor visuals`. Each visual goes into the `visuals` folder of the guide's output folder, as an `.svg` drawing and an `.mmd` Mermaid copy.

To show a visual on a page, add a fenced block that opens with ```` ```visual id=<id> ````. In the built site, that block becomes the drawing inline, and the drawing also replaces each generated architecture view.

The figure carries the visual's takeaway as its caption and "The picture in words" as a text list. The Markdown files keep their Mermaid for readers outside the site.

The renderer is `@ux-builder/visuals`. `publish.visuals.command` or the `DOCUMENTOR_VISUALS` environment variable names its command. Otherwise documentor installs the tested release into its cache.

### Look at the built pages

```sh
documentor site --shots
```

`documentor site --shots` builds the site, then screenshots each page on a desktop, in dark mode, and at phone width. It writes an `index.html` to browse them and reports any page wider than its screen. It needs `node` and `npm`.

The screenshots go into `shots` beside a new site, or into `.helix/shots` for an existing Hugo site. A `mkdocs.yml` site gets no screenshots.

## Pass the check before a pull request

```sh
documentor check
```

`check` is the gate for a pull request. It regenerates the generated pages in memory and compares them with the files, with no agent and no network.

It exits with status 1 when any of these hold:

- a blocking finding, such as a broken link or text that your `handling:` rules forbid
- a page that is missing, stale, not yet evaluated, or not yet adopted
- architecture drawings, or visuals, that no longer match their model

It prints up to ten unfinished pages, each with what it needs. Run `build` for generated pages and `write` for written ones, then check again.

To run the gate on every pull request, copy the CI template into the .github/workflows folder as `guide.yml`. The template ships in the `documentor` package at `src/documentor/catalog/ci/github-actions.yml`, and in the [HELIX repository](https://github.com/DocumentDrivenDX/helix/blob/main/tools/documentor/src/documentor/catalog/ci/github-actions.yml). Set its `DOCUMENTOR` variable to your HELIX release.

## Keep the guide current

The same workflow file runs every Monday. It regenerates the generated pages and drawings, then opens a pull request on a branch named `guide/refresh`.

The weekly job does not write pages, because writing needs an agent and credentials. When a written page goes stale, run `documentor write` on your machine, then push the result.
