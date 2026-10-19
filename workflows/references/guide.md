# The guide

A repository's guide is every page its readers need: what developers need to change it, what operators need to run it, what users need to work with it, what data consumers need to trust it. HELIX produces it from what the repository is and has, keeps it current on every change, and assembles it into one site. The artifacts stay the system of record (`publishing.md`); the guide is their projection for people.

## What decides the guide

| Input | Where | Decides |
|---|---|---|
| Flows | `workflows/publish/flows/<reader>.yml` | the readers, and the pages each needs, each with a Diátaxis kind, a task, an outline, a budget, and sources |
| Traits | `workflows/publish/traits/<id>.yml` | what this kind of repository adds (pages, generated pages, views, watched files, handling) and what its own tools already publish (delegated pages) |
| The project | `.helix.yml` `publish:` and `handling:` | which flows and traits apply here, extra pages, scope, and what no page may contain |
| The model | `<helix root>/02-design/architecture-model.toml` | the architecture views pages embed: stack, cast, deployment, journeys, DAG |

Detection (`guide.py init`) proposes the traits from the files git tracks; `.helix.yml` records the decision. The registry grows by one trait each time a repository has a significant file no trait claims.

## Four kinds of work

| Work | Made by | Kept current by |
|---|---|---|
| **Generated** pages (settings, jobs, API, packages, workflows, resources) | `publish_generate.py`, from structured sources, deterministically | regeneration: `check` fails when a regenerated page would differ; `build` rewrites it |
| **Views** (stack, cast, deployment, journey, DAG) | `architecture_views.py`, from the model | evidence: each element cites code, so `check` fails when the code moves |
| **Written** pages (overviews, tutorials, how-tos, explanations) | an agent, in `publish` mode, then evaluated by another reader | provenance: each source is digested, so `check` fails when one changes; the page is rewritten and evaluated again |
| **Delegated** pages (tablespec's guidebook) | the repository's own tool | that tool; the guide links its output and the command that builds it |

Exactness wherever a source has structure; judgment only where a reader needs explanation; no duplication of what a repository already publishes.

## Page states

`guide.py status` gives each page one state, from the same checks CI runs: **missing** (not yet made), **stale** (a source changed since it was made), **review** (written, not yet evaluated), **current**, or **delegated**. The written pages that are missing, stale, or unreviewed are the agent's work list, in that order.

A written page's header carries `reviewed=<date>/<who>` once it is evaluated (`guide.py review`). Freshness proves the sources have not moved; evaluation is what says the page was right about them.

## The site

`guide.py build` assembles one site from the pages: a home page with a card per reader, one section per reader with its pages in flow order (each page marked with its kind), delegated pages linked to their tools, every page listing the sources it was built from, and the architecture views drawn in the project's theme. The Markdown pages under `docs/guide/` (beside the HELIX root) stay the record: the repository host renders them with no toolchain, and the site is rebuilt from them, never edited.

## In CI

One job: `guide.py check --root .`. It needs Python 3.11 and PyYAML, no network, no model, and no agent. It fails when the guide is behind the repository, so the pull request that changes a setting, adds a job, exports a new name, or edits a cited section is the one that updates the guide. A scheduled run of `guide.py build --no-site` on the default branch regenerates what is generated and opens a pull request when anything moved.
