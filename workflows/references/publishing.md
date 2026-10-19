# Publishing

A project's artifacts are the system of record: dense, exact, and written for agents and reviewers who trace intent through them. The people who build on, run, or use the system need something else: a page that answers their question in their vocabulary. `publish` generates those pages from the artifacts and the code, records exactly what each page was built from, and checks on every change that no page has fallen behind its sources. The artifacts are never rewritten for readers.

## Audiences and flows

A flow is the set of pages one kind of reader needs. The catalog ships three, in `workflows/publish/flows/`:

| Flow | Reader | Pages (kind) |
|---|---|---|
| `developer` | someone about to change the code | overview, architecture, request walkthrough (explanation); developer guide (how-to) |
| `operator` | someone who deploys, configures, or runs the system | deployment, operations (how-to); configuration (reference) |
| `user` | someone who uses the product | getting started (tutorial); what it is and is not (explanation); using the product (how-to) |
| `data` | someone who queries, reports on, or changes the project's data | data overview, lineage (explanation); tables, metrics (reference); querying and refreshing (how-to) |

Each page in a flow names its reader task, its kind, its voice (`onboarding` for developers and operators, `public-site` for users), its word budget, and the kinds of source it draws on: artifact types and sections, generated views, the project's own documentation outside HELIX (`docs`), configuration, and code. A project chooses its flows and adds or drops pages in `.helix.yml`:

## Repository traits

What a repository is decides what its documentation needs: a Databricks app has users and operators; a tablespec pipeline has tables, lineage, and metrics; a Python library has a public interface. A **trait** says so as data, in `workflows/publish/traits/<id>.yml`, the way tablespec's domain types say what a column is:

```yaml
id: plugin-manifests
title: Workflows packaged as plug-in manifests
detect:                                  # signals, each a glob, an optional pattern, and a weight
  - {files: "**/plugin.toml", contains: "^\\[workflow\\]", weight: 0.6}
  - {files: "**/plugin.toml", contains: "^\\[evals\\]", weight: 0.2}
flows: [user]                            # the audiences this kind of repository has
pages:                                   # pages the trait adds, or replaces by id
  - flow: user
    id: workflows
    kind: reference
    generated: plugin-workflows          # written by a generator, not by an agent
watch: ["**/plugin.toml"]                # a new one of these, documented by no page, is reported
handling:                                # what this kind of repository puts at risk
  never_publish: ["..."]
```

A trait can also **delegate** a page to a tool the repository already uses, when that tool publishes the reference better than HELIX could:

```yaml
id: tablespec-pipeline
delegates:
  - page: data/tables
    tool: tablespec guidebook
    build: "tablespec guidebook <specs directory> -o guidebook"
    covers: each table's columns, keys, validation rules, and column lineage
```

A delegated page is not written. The pages that would link it link the tool's output instead, with the command that builds it, and HELIX documents what the tool does not: for a tablespec pipeline, the stage-level lineage from sources to dashboards, the jobs, and how to run them.

`skills/helix/scripts/publish_detect.py` scores every trait against the files git tracks; a trait's confidence is the sum of the weights its signals matched. It proposes the traits at or above the threshold (0.5), with the flows, pages, views, and handling they bring, and lists the significant files (`traits/significant.yml`) that no proposed trait claims. Detection proposes; `.helix.yml` decides: the confirmed list is `publish.traits`, so the documentation never changes shape because a file appeared. An unclaimed significant file is the cue to add a trait, and the registry grows one entry per kind of repository met.

**Generated pages.** Where the repository already describes something in a structured source, the page is generated from it, deterministically, by `skills/helix/scripts/publish_generate.py <generator>`: a workflow list from plug-in manifests (`plugin-workflows`). A generated page's header says `generated=<generator>` and cites its inputs as glob sources (`plugins/*/plugin.toml`), each digested over every file it matches, so any provenance check sees the page go stale when an input changes or a new one appears; `publish_check.py` also regenerates it and compares. Generated pages read structure only (names, keys, dependencies, counts, and text written for the page's reader, such as a workflow's description) and are not held to the writing rules, because they are data. An agent writes what needs judgment: explanations, how-tos, tutorials.

## Page kinds

A page has one of the four [Diátaxis](https://diataxis.fr) kinds, and keeps to it. The kind decides what the page does and what it leaves to another page, so a reader who wants steps is not handed theory, and a reader who wants the facts is not walked through a lesson.

| Kind | The reader wants to | The page | The page does not |
|---|---|---|---|
| `tutorial` | learn by doing, the first time | takes them through one worked exercise, step by step, to a visible result; every step works as written | explain alternatives, cover options, or stop to justify |
| `how-to` | get one thing done, already competent | gives the steps for a goal they already have, in order, with the decision points named | teach the basics, or describe everything the system can do |
| `reference` | look something up | states what exists, one entry per thing, in a fixed shape (a table, a list), named as the code names it | instruct, or explain why |
| `explanation` | understand | tells why the system is as it is, what connects to what, and which decision governs each part | give steps, or list every setting |

The kind is recorded in the page's header (`kind=`) and shown on the site. A project page added in `.helix.yml` names its kind beside its title. `publish_check.py` warns when a header names no kind or an unknown one. A page whose task spans two kinds is two pages: the developer guide (how-to) and the request walkthrough (explanation) are separate for this reason.

```yaml
publish:
  out: docs/guide            # where pages are written, one directory per flow (default: guide/ beside the HELIX root)
  scope: docs                # optional: publish writes only under this directory (a coexistence rule)
  flows: [developer, operator, user]
  site:                      # optional: a static site built from the pages
    title: Example
    repo_url: https://github.example/org/example   # links to source files resolve here
    accent: "#2f6f8f"
  pages:                     # optional per-project additions to a flow
    operator:
      - id: data-jobs
        title: Example data jobs
        kind: how-to
        task: Load the example data and run the document pipeline
        sources: [data/*/README.md, data/*/databricks.yml]
```

## Handling

What a page may contain is a project's decision, and some projects cannot afford a mistake: a data pipeline over healthcare claims, a harness over a law firm's matters. `.helix.yml` says so once:

```yaml
handling:
  never_publish:             # read by publish before it reads any source
    - rows, sample values, or identifiers from the data
    - client, matter, or person names from real records
  patterns:                  # regular expressions publish_check blocks on (finding: handling)
    - '\b[0-9]{3}-[0-9]{2}-[0-9]{4}\b'
```

`publish` reads `never_publish` before it reads any source, and describes structure and meaning only. `publish_check.py` blocks any page that matches a pattern. A project that sets `handling` or `publish.scope` needs PyYAML for the check; without it the check fails rather than skip them.

## Provenance

Every generated page starts with a provenance header, an HTML comment block that names the flow and page and every source the page was built from, each with a digest of the exact text read:

```markdown
<!-- helix:publish flow=developer page=architecture kind=explanation voice=onboarding budget=1200 -->
<!-- helix:source docs/helix/02-design/architecture.md#deployment sha256:3f9a0c41d2e8b7a6 -->
<!-- helix:source databricks.yml sha256:91c0e7aa04b3d5f2 -->
# Architecture
```

The header may also name a file the page tells its reader to create, one line each, among the source lines: `<!-- helix:creates tests/test_new.py -->`; the path check accepts that path and no other missing one. A source is a path relative to the project root, optionally with `#<section>`, the slug of a heading (H2 or deeper), to pin one section of a Markdown file: the heading through the line before the next heading of the same or a higher level. The digest is the first 16 hex characters of the SHA-256 of that section (or of the whole file), with trailing whitespace removed from each line. Renderers do not display the comments; a reader of the raw Markdown sees where the page came from.

`skills/helix/scripts/publish_check.py stamp <page>` writes the digests after the page is generated, so the agent names the sources and the script records their state.

## Checks

`publish_check.py check <dir or page>` runs on every change, in CI and before handoff:

| Finding | Meaning | Severity |
|---|---|---|
| `stale` | a source's text changed after the page was stamped | blocking |
| `missing-source` | a source path or section no longer exists | blocking |
| `broken-link` | a relative link resolves to no file | blocking |
| `missing-path` | a backticked repository path (`src/app.py`) does not exist, unless the header names it as a file the reader creates (`<!-- helix:creates tests/test_new.py -->`) | blocking |
| `unmapped` | a file a flow or trait watches (a new ADR, a new runbook) is cited by no page; `publish.ignore` lists globs no page should explain | warning |
| `kind` | the header names no page kind, or one that is not a Diátaxis kind | warning |
| `handling` | a page matches a pattern `handling.patterns` forbids | blocking |
| `outside-scope` | `publish.out` is outside `publish.scope` | blocking |
| `prose.*` | a breach of the page's voice limits or budget (`writing-pass.md`) | warning, blocking with `--strict-prose` |

A stale page is regenerated, not patched: `publish` reads the changed sources again, rewrites the affected sections, runs the writing pass, and stamps. A reviewer sees the source change and the page change in one pull request.

## The site

`skills/helix/scripts/publish_site.py --root <project>` builds a static site from the pages with Hugo, using the self-contained layout in `workflows/publish/site/` (no theme download, no external fonts; Mermaid diagrams render in the browser). Each flow becomes a section with its pages in flow order. Links between pages become site links; links to source files resolve to `site.repo_url` when it is set. Every page shows the sources it was built from. The Markdown pages stay the record: GitHub renders them without the site, and the site is rebuilt from them, never edited.

## What publishing does not do

It does not edit artifacts. A page that finds an artifact out of date with the code follows the code and reports the disagreement; `align` or `refresh` settles it in the artifact, and the page goes stale and is regenerated after.
