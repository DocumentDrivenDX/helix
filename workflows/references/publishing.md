# Publishing

A project's artifacts are the system of record: dense, exact, and written for agents and reviewers who trace intent through them. The people who build on, run, or use the system need something else: a page that answers their question in their vocabulary. The `guide` mode generates those pages from the artifacts and the code, records on each page exactly what it was built from, and checks on every change that no page has fallen behind its sources. The artifacts are never rewritten for readers. documentor (`tools/documentor/` in the HELIX repository) is the host tool for the deterministic parts, kept in this repository outside the skill; this reference is the contract both the mode and the tool follow.

## Audiences

An audience is the set of pages one kind of reader needs. The catalog ships four, in `workflows/publish/audiences/`:

| Audience | Reader | Pages (kind) |
|---|---|---|
| `developer` | someone about to change the code | overview, architecture, request walkthrough (explanation); developer guide (how-to) |
| `operator` | someone who deploys, configures, or runs the system | deployment, operations (how-to); configuration (reference) |
| `user` | someone who uses the product | getting started (tutorial); what it is and is not (explanation); using the product (how-to) |
| `data` | someone who queries, reports on, or changes the project's data | data overview, lineage (explanation); tables, metrics (reference); querying and refreshing (how-to) |

Each page in an audience names its reader task, its kind, its voice (`onboarding` for developers, operators, and data; `public-site` for users), its word budget, its outline, and the kinds of source it draws on: artifact types and sections, generated views, the project's own documentation outside HELIX (`docs`), configuration, and code. Which audiences a project has follows from what it is:

| Evidence | Audiences |
|---|---|
| always | `developer` |
| the `infra` lane, a deploy bundle, CI deploy jobs | `operator` |
| the `product` or `web` lane, a user-facing screen | `user` |
| the `data` lane, pipelines, tables, dashboards | `data` |

Clients, sponsors, and executives are `present`'s readers (a deck or a brief), not an audience of the guide.

## Page kinds

A page has one of the four [Diátaxis](https://diataxis.fr) kinds, and keeps to it. The kind decides what the page does and what it leaves to another page, so a reader who wants steps is not handed theory, and a reader who wants the facts is not walked through a lesson.

| Kind | The reader wants to | The page | The page does not |
|---|---|---|---|
| `tutorial` | learn by doing, the first time | takes them through one worked exercise, step by step, to a visible result; every step works as written | explain alternatives, cover options, or stop to justify |
| `how-to` | get one thing done, already competent | gives the steps for a goal they already have, in order, with the decision points named | teach the basics, or describe everything the system can do |
| `reference` | look something up | states what exists, one entry per thing, in a fixed shape (a table, a list), named as the code names it | instruct, or explain why |
| `explanation` | understand | tells why the system is as it is, what connects to what, and which decision governs each part | give steps, or list every setting |

The kind is recorded in the page's header (`kind=`) and shown on the site. A page whose task spans two kinds is two pages: the developer guide (how-to) and the request walkthrough (explanation) are separate for this reason.

## Kinds of work

| Work | Made by | Kept current by |
|---|---|---|
| **Generated** pages (settings, jobs, public interfaces, packages, resources, screens, workflows, API operations, commands, MCP tools) | a generator, from structured sources, deterministically: documentor's, a Python distribution's, or a command the project owns | regeneration: the check fails when a regenerated page would differ |
| **Views** (stack, cast, deployment, journey, DAG) | documentor, from the architecture model, under the guide | evidence: each element cites code, so the check fails when the code moves |
| **Written** pages (overviews, tutorials, how-tos, explanations) | an agent in `guide` mode, then evaluated by another reader | provenance: each source is digested, so the check fails when one changes; the page is rewritten and evaluated again |
| **Existing** pages the project already had | their authors; adopted with a header, text untouched | links, paths, handling, and prose are checked; staleness only for sources they name |
| **Delegated** pages (a table reference from tablespec's guidebook, components from Storybook, an API from mkdocstrings) | the repository's own tool | that tool; the guide links its output and the command that builds it |

Exactness wherever a source has structure; judgment only where a reader needs explanation; no duplication of what a repository already publishes.

## The project's decision

The `publish:` block in `.helix.yml` is the repository's documentation plan: who reads it (`audiences`), what it is (`traits`), which pages it has beyond the catalog's (`pages`, `existing`, `delegate`, `skip`), and how the site is assembled (`site`). Detection proposes it; `.helix.yml` decides, so the documentation never changes shape because a file appeared:

```yaml
publish:
  schema: 1                  # the configuration contract this block follows
  traits: [databricks-app, plugin-manifests]   # what the repository is: each adds pages, generators, delegations, handling
  audiences: [developer, operator, user]       # who reads it
  out: docs/guide            # where pages are written, one directory per audience (default: guide/ beside the HELIX root)
  scope: docs                # optional: the guide is written only under this directory (a coexistence rule)
  traits_dir: .helix/traits  # optional: the project's own trait files, merged with the catalog's
  pages:                     # optional: project pages, written or generated by a command
    operator:
      - id: data-jobs
        title: Example data jobs
        kind: how-to
        task: Load the example data and run the document pipeline
        sources: [data/*/README.md, data/*/databricks.yml]
      - id: resources
        title: Infrastructure
        kind: reference
        generated: {command: "terraform-docs markdown table infra", sources: ["infra/*.tf"]}
  delegate:                  # optional: a page a tool the repository has already publishes
    data/tables: {tool: tablespec guidebook, build: "tablespec guidebook specs -o guidebook", url: guidebook/index.html}
  existing:                  # optional: hand-written pages to adopt, by audience
    developer: ["docs/how-to/*.md"]
  skip: [user/about]         # optional: catalog pages this repository does not publish
  watch: ["databricks.yml"]  # optional: files a new one of which, cited by no page, is reported
  ignore: []                 # optional: globs no page should explain
  views: guide               # optional: architecture views under the guide (default), or `artifact` (between markers in the model's own documents)
  theme:                     # optional: the project's look, from DocumentDrivenDX/ux-builder (`@ux-builder/tokens`)
    name: synaptiq           # a theme in the tokens' manifest; the site, the architecture views, presentations, and decks wear it
    appearance: system       # light | dark | system (the site follows the reader; drawings use light unless dark)
    tokens: 1.6.0            # optional: another published version, or a path to a local tokens build
  agent:                     # optional: the agent `documentor write` drives; DOCUMENTOR_AGENT overrides the command
    command: "my-agent --model {model}"   # the prompt on stdin, the page on stdout
    writer: opus
    reviewer: sonnet         # must differ from the writer
  site:                      # optional: how the site is assembled
    title: Example
    description: One line under the title
    repo_url: https://github.example/org/example   # links to repository files resolve here
    branch: main
    accent: "#2f6f8f"        # without `publish.theme`: the site's one color
    target: static           # mkdocs | hugo (the repository's own site) | static (default with no site) | hextra
    site_dir: website        # optional: where the repository's Hugo site lives, when detection should not guess
    content_root: docs/website/content   # optional: the Hugo content directory, when the site mounts it elsewhere
    content_dir: guide       # the section the guide is written into, inside an existing site
    record: true             # optional: also publish the governed artifacts (the HELIX root), read-only, with their sources
    record_dir: record       # the record's section (default `record`)
    sections:                # optional: sections the project generates itself
      - {id: reference, title: Reference, generated: {command: "uv run scripts/generate-reference.py", out: reference}}
```

**Theme.** With `publish.theme`, every rendering wears one theme: the site loads the theme's CSS, fonts, and brand artwork, and maps its roles onto the theme's `--piq-*` tokens; the architecture views and presentations draw in its colors (a model's own `[theme]` still overrides a role); a deck takes its colors and keeps typefaces every presentation program has. The tokens are fetched once from the npm registry; without the network, or without `publish.theme`, the look is the packaged neutral theme. An existing Hugo or mkdocs site keeps its own look.

**Schema.** `publish.schema` names the version of this contract the block follows. A block without it is version 1. A key whose meaning changes raises the version; a new optional key does not. documentor refuses a block whose schema it does not read, rather than misread it, and `documentor init` writes the version it reads.

A **trait** says, as data, what a kind of repository is (signals over the files git tracks) and what its readers need: the audiences it implies, pages it adds or replaces by id, pages it generates, pages it delegates, views, watched files, and handling. documentor carries the catalog of traits and grows it by one each time a repository has a significant file no trait claims; a project's own traits live under `publish.traits_dir`.

## Handling

What a page may contain is a project's decision, and some projects cannot afford a mistake: a data pipeline over healthcare claims, a harness over a law firm's matters. `.helix.yml` says so once:

```yaml
handling:
  never_publish:             # read before any source is read
    - rows, sample values, or identifiers from the data
    - client, matter, or person names from real records
  patterns:                  # regular expressions the check blocks on (finding: handling)
    - '\b[0-9]{3}-[0-9]{2}-[0-9]{4}\b'
```

The agent reads `never_publish` before it reads any source, and describes structure and meaning only. Generators read structure only (names, keys, dependencies, counts), never a value. The check blocks any page or generated drawing that matches a pattern.

## Provenance

Every page starts with a provenance header, an HTML comment block that names the audience and page and every source the page was built from, each with a digest of the exact text read:

```markdown
<!-- helix:publish audience=developer page=architecture kind=explanation voice=onboarding budget=1200 -->
<!-- helix:source docs/helix/02-design/architecture.md#deployment sha256:3f9a0c41d2e8b7a6 -->
<!-- helix:source databricks.yml sha256:91c0e7aa04b3d5f2 -->
# Architecture
```

The header may also name a file the page tells its reader to create (`<!-- helix:creates tests/test_new.py -->`); the path check accepts that path and no other missing one. A generated page says `generated=<id>` (or `generated=command`) and cites its inputs as glob sources, each digested over every file it matches. An adopted page says `existing=yes`. An evaluated page carries `reviewed=<date>/<who>/<body digest>`; an edit after review lapses it. (`flow=` is the older spelling of `audience=` and is still read.)

A source is a path relative to the project root, optionally with `#<section>`, the slug of a heading (H2 or deeper), to pin one section of a Markdown file: the heading through the line before the next heading of the same or a higher level. The digest is the first 16 hex characters of the SHA-256 of that section (or of the whole file), with trailing whitespace removed from each line. Renderers do not display the comments; a reader of the raw Markdown sees where the page came from.

## Budgets and words

A page's `budget` is a count of prose units: words in paragraphs, list items, and table cells. Headings, code fences, HTML comments, generated views, and `<details>` blocks do not count, so a reference a reader opens only to check a claim can sit under a `<details>` block without spending the budget. The voice profile's `limits` (words per sentence, sentences per paragraph, words per cell) and the shared `prose` lists in `workflows/voice.yml` are measured the same way; the writing pass resolves each finding.

## Diagrams

A page's diagram comes from the project's architecture model when it has one (a generated view, embedded by link from under the guide), else from the diagram in the artifact the page cites, trimmed to at most fifteen nodes whose labels match the page's own words, placed under a one-sentence takeaway, and cited by section so it goes stale with the artifact. One diagram per page: a context or container flowchart for an overview, a sequence for a walkthrough, a deployment view for operators. No theme directives in the Markdown; the site renders Mermaid.

## Checks

The check runs on every change, in CI and before handoff:

| Finding | Meaning | Severity |
|---|---|---|
| `stale` | a source's text changed after the page was stamped, or a generated page would differ when regenerated | blocking |
| `missing-source` | a source path or section no longer exists, or a written page names no source | blocking |
| `broken-link` | a relative link resolves to no file | blocking |
| `missing-path` | a backticked repository path (`src/app.py`) does not exist, unless the header names it as a file the reader creates | blocking |
| `unmapped` | a file an audience, a trait, or the project watches (a new ADR, a new runbook) is cited by no page; `publish.ignore` lists globs no page should explain | warning |
| `kind` | the header names no page kind, or one that is not a Diátaxis kind | warning |
| `handling` | a page or drawing matches a pattern `handling.patterns` forbids | blocking |
| `outside-scope` | `publish.out` is outside `publish.scope` | blocking |
| `prose.*` | a breach of the page's voice limits or budget | warning, blocking with `--strict-prose` |

The guide as a whole is behind the repository when any page is missing, stale, or unreviewed, or a view drifted from its model; `documentor check` exits non-zero then. A stale page is regenerated, not patched: the agent reads the changed sources again, rewrites the affected sections, runs the writing pass, and stamps. A reviewer sees the source change and the page change in one pull request.

## What publishing does not do

It does not edit artifacts. A page that finds an artifact out of date with the code follows the code and reports the disagreement; `align` or `refresh` settles it in the artifact, and the page goes stale and is regenerated after. It does not replace a reference a better tool publishes, nor a site the repository has: those are delegated and emitted into.

## Design schema browser

Schema references use `ddx.schemas`, defined in
`workflows/references/umf-schemas.md`. `documentor site` automatically collects
references under the active HELIX root and the guide output for Hugo, static,
and Hextra targets.
It generates `/schemas/`, original source downloads, provenance with SHA-256
digests, and an embedded UMF schema browser. Published artifacts and referenced
guide pages gain links to the selected schema and optional definition. Relative
URLs preserve deployment prefixes such as `/helix/`. No references means no
browser dependency or generated section. Existing sources are never rewritten.

Install `@documentdrivendx/umf-schema-browser@2.0.0` with the site's package
manager and commit its lockfile. The publisher looks under `node_modules/` and
`website/node_modules/`. `publish.schemas.browser_package` may instead name a
repository-relative installed package directory; the release identity and file
hashes are checked before copying it. The site serves the complete asset tree
and required license notices locally. No remote catalog is implicitly fetched.

```sh
documentor schemas --root .          # regenerate only the schema section/assets
documentor schemas --root . --check  # fail on changed sources, metadata or assets
```

`--content` and `--static` can select output directories for another site build.
For Hugo, defaults follow its content mount and static directory; static and
Hextra use `.helix/site/content` and `.helix/site/static`. Run generation before
plain Hugo builds. Source drift belongs to the generated-site gate; the schema
check compares a previously generated publication with current inputs.
A missing source, conflicting identity, nonexistent selected definition, syntax
error, transport limit violation, or missing browser package fails the build.
Rendering and syntax checks establish no native semantic or instance-validation
claim; run the appropriate pinned UMF/native validator separately. The browser
loads only selected sources; full-text search of unloaded sources is not implied.

The schema publisher records ownership in its manifest and index marker. It
refuses to replace unowned schema directories or indexes, preserves unrelated
files added beside generated output, and retires only unchanged generated files
listed by its previous inventory. Retirement leaves an unrelated index alone.
