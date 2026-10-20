<!-- helix:publish audience=user page=about kind=explanation voice=public-site budget=600 written=agent-opus reviewed=2026-10-20/second-reader-move-review/d97e00b36548df2d -->
<!-- helix:gap artifact:feature-specification -->
<!-- helix:source docs/helix/00-discover/product-vision.md#vision sha256:af72d95c19717f8b -->
<!-- helix:source docs/helix/00-discover/product-vision.md#positioning sha256:925b7219f516bebb -->
<!-- helix:source docs/helix/01-frame/prd.md#goals sha256:5186f9407b38708a -->
<!-- helix:source docs/helix/01-frame/prd.md#out-of-scope-now sha256:3d376634f9a4f887 -->
<!-- helix:source README.md#use sha256:1668b6192a52a5d5 -->
<!-- helix:source README.md#what-it-reads-and-writes sha256:55f9002fc000e454 -->
<!-- helix:source src/documentor/check.py sha256:dd7449d66da8b7ec -->
<!-- helix:source src/documentor/write.py sha256:8ad5661054a3cc34 -->
<!-- helix:source src/documentor/generate.py sha256:92dcfeb4e275656d -->
# What it is and is not

documentor is a command-line tool that builds a repository's documentation and keeps it current. That documentation is called its *guide*.

## What it does for you

A guide has pages for up to four audiences: developers, operators, users, and data consumers. Each repository chooses its audiences, and what the repository is adds pages. An audience gets the same page shapes in every repository.

documentor makes each page in one of five ways:

- **Generated.** Pages about settings, commands, API operations, or infrastructure are built from their structured source, so they cannot drift from it.
- **Written.** An agent, an AI model run as a command, writes pages that need explanation. A second, different model evaluates each page before it counts as finished.
- **Views.** Architecture drawings are rendered from your architecture model.
- **Existing.** A hand-written page you already have joins the guide with a short header, unchanged.
- **Delegated.** When a tool you already use publishes a better reference, documentor links to it instead of copying it.

Each page records the files it was built from. When one changes, the page is stale, and `documentor check` fails the pull request until someone updates it. The check also catches missing or unevaluated pages, drifted architecture drawings, and broken links.

documentor also writes the pages into your existing mkdocs or Hugo site, and creates a site only if you have none. The Markdown pages in the repository stay the record.

## How it keeps to the firm's rules

Your firm's data rules live in a `handling:` block in `.helix.yml`. *Handling* lists what must never be published, such as data rows or sample values. It also lists text patterns that no page may contain.

documentor applies those rules at several points:

- **Generators copy little free text.** They take names, keys, dependencies, and counts, plus the first sentence of docstrings and of spec, workflow, and API descriptions. That sentence can still hold what handling forbids.
- **The writing agent is told the rules.** Every page request includes them. By default the agent can only read files, not change them.
- **The check enforces them.** `documentor check` blocks the pull request when any page, generated ones included, or a generated drawing matches a handling pattern. For generated pages, the check is the only guard.
- **The guide and the check stay local.** The guide is plain Markdown in your repository, and `documentor check` needs no agent.

So write handling patterns that catch what your firm forbids, not only what you expect agents to write.

`documentor write` is the one step that uses an outside model service. It sends each page request, with the handling and voice rules, to the agent command. By default that command is Claude Code (`claude -p`), and repository files the agent reads also go to the model provider.

Before you write, confirm that your firm allows that provider to see the repository. `publish.agent.command` in `.helix.yml`, or the `DOCUMENTOR_AGENT` variable, names a different command. `documentor write --dry-run` prints the prompts without calling anything.

## What it will not do

- **Host the site.** Where the site is served is your decision.
- **Write your project's intent.** documentor plans pages from your HELIX documents under `docs/helix/`, such as the vision and requirements. It does not yet draft them from code.
- **Rewrite a current page unasked.** By default, `documentor write` writes missing or stale pages and evaluates unreviewed ones. An unreviewed page that fails its own checks goes back to the writer first, with those findings. Naming one page rewrites it, even when it is current.
- **Run an agent in CI.** Writing needs the agent's credentials, and the CI gate runs without them.

Start with [Getting started](index.md) for a first session, or [Using the product](using.md) for everyday tasks.
