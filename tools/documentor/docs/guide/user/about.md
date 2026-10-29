<!-- helix:publish audience=user page=about kind=explanation voice=public-site budget=600 written=codex reviewed=2026-10-29/codex-independent-reader/453c9c3973625d52 -->
<!-- helix:gap artifact:feature-specification -->
<!-- helix:source docs/helix/00-discover/product-vision.md#vision sha256:af72d95c19717f8b -->
<!-- helix:source docs/helix/00-discover/product-vision.md#positioning sha256:925b7219f516bebb -->
<!-- helix:source docs/helix/01-frame/prd.md#goals sha256:5186f9407b38708a -->
<!-- helix:source docs/helix/01-frame/prd.md#requirements sha256:faab177063c3e4e8 -->
<!-- helix:source docs/helix/01-frame/prd.md#out-of-scope-now sha256:3d376634f9a4f887 -->
<!-- helix:source README.md#use sha256:1668b6192a52a5d5 -->
<!-- helix:source README.md#what-it-reads-and-writes sha256:55f9002fc000e454 -->
<!-- helix:source src/documentor/check.py sha256:784c2473233c0346 -->
<!-- helix:source src/documentor/write.py sha256:208f5a662b7501e4 -->
<!-- helix:source src/documentor/generate.py sha256:9ed3906b7fe2bc36 -->
<!-- helix:source src/documentor/cli.py sha256:861322ae490496ea -->
<!-- helix:source src/documentor/schemas.py sha256:9a9548369cb394fa -->
<!-- helix:source src/documentor/umf_tables.py sha256:56c75007b5b2d2de -->
# What it is and is not

documentor is a command-line tool that builds a repository's documentation, its *guide*, and keeps it current. It follows your organisation's data rules.

## What it does for you

documentor plans, makes, and checks a guide with pages for up to four audiences the repository picks: developers, operators, users, and data consumers. Some kinds of repository add extra pages to the standard set.

documentor makes each page in one of five ways:

- **Generated.** Pages about settings, commands, task-runner recipes, API operations, CI pipelines, compose services, database tables, or infrastructure come from their structured source. They cannot drift from it.
- **Written.** An *agent* writes the pages that need explanation. The agent is an AI model that documentor runs as a command. A different model evaluates each page before it counts as finished.
- **Views.** documentor draws the architecture diagrams from your architecture model.
- **Existing.** A hand-written page you already have joins the guide with a short header, unchanged.
- **Delegated.** documentor links to a reference another tool publishes.

Each page records its source files. When one changes, the page is stale, and `documentor check` fails the pull request until someone updates it. The check also catches missing or unevaluated pages, outdated diagrams, broken links, and cited tests that do not exist.

documentor builds an existing or new site. Applicable sites also publish UMF table references and a schema browser with provenance and downloads; browsing does not validate application data.

## How it keeps to the organisation's rules

Your organisation's data rules go in a `handling:` block in `.helix.yml`. *Handling* lists what must never be published, such as data rows or sample values. It also lists text patterns that no page may contain.

documentor applies those rules at four points:

- **Generators copy little free text.** They take names, keys, types, ports, dependencies, and counts, plus the first sentence of docstrings, descriptions, and recipe comments. The database page copies each column's comment whole and reads no rows.
- **The writing agent gets the rules.** Every page request includes them. By default the agent can only read files.
- **The check enforces them.** `documentor check` blocks the pull request when any page or generated diagram matches a handling pattern. For generated pages, the check is the only guard.
- **The guide and the check stay local.** The guide is plain Markdown in your repository, and `documentor check` needs no agent and no network.

Copied text can still contain forbidden content, so write patterns for everything your organisation forbids, not only what agents might write.

`documentor write` is the one step that sends page requests to an outside model service, through the agent command. By default that command is Claude Code (`claude -p`), and any repository files the agent reads also go to the model provider.

First confirm that your organisation allows that provider to see the repository. To use a different command, set `publish.agent.command` in `.helix.yml` or the `DOCUMENTOR_AGENT` variable. `documentor write --dry-run` prints the requests without calling anything, and `documentor prompt PAGE` prints the request for one page.

## What it will not do

- **Host the site.** The repository decides where a private site is served.
- **Write your project's intent from code.** documentor plans pages from the HELIX documents under `docs/helix/`, such as the vision and requirements. documentor does not yet write those documents from your code.
- **Touch a current page unless you name it.** `documentor write` writes missing or stale pages and evaluates unreviewed ones. An unreviewed page that fails its own checks goes back to the writer first. Naming a page rewrites it even when it is current.
- **Need an agent in CI.** `documentor write` runs where the agent's credentials are. `documentor check`, the CI gate, needs no agent.
