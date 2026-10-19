# Publish

Use to generate, refresh, or check the pages people read about a project: what developers need to change the code, what operators need to run it, and what users need to work with it. The pages are projections of the project's artifacts and code, never edits to them. Engage on: developer guide, onboarding, getting started, architecture overview for a newcomer, operator or deployment docs, user guide, README-level explanation, documentation site, "the docs are out of date". The model, provenance format, and checks are `workflows/references/publishing.md`; the writing standard is `workflows/references/writing-pass.md`.

## Intake

Run `skills/helix/scripts/publish_detect.py --root .` first: it says which traits the repository has (`publishing.md`, Repository traits), with the evidence for each, and which significant files no trait claims. Confirm the traits into `.helix.yml` `publish.traits`; propose a new trait for an unclaimed file rather than documenting it by guesswork. Then read the project's `.helix.yml` `publish:` block: `out` (where pages are written; default `guide/` beside the HELIX root, so `idrflow/docs/helix/` publishes to `idrflow/docs/guide/`), `scope` (optional: the one directory `publish` may write under), `flows` (which audiences), `site` (optional), and `pages` (project additions to a flow). With no block, propose one from the project's lanes and evidence, and follow the active autonomy contract before writing it:

| Evidence | Flows |
|---|---|
| always | `developer` |
| the `infra` lane, a deploy bundle, CI deploy jobs | `operator` |
| the `product` or `web` lane, a user-facing screen | `user` |
| the `data` lane, pipelines, tables, dashboards | `data` |

Read `.helix.yml` `handling:` before reading any source: `never_publish` says in words what no page may contain (for a project over regulated data: rows, sample values, and identifiers), and `patterns` are regular expressions the check blocks on. A page describes structure and meaning, never the data itself. Where a project has a coexistence rule (a legacy tree `publish` must not touch), set `scope` so the check enforces it. Load each chosen flow from `workflows/publish/flows/<id>.yml` (floor `references/publish/flows/`).

## Generate a page

A page a trait marks `generated:` is written by `skills/helix/scripts/publish_generate.py <generator> --page <path>`, never by hand; regenerate it when the check says it is stale. A page a trait delegates (`delegates:`) is not written at all: the repository's own tool publishes it, so link that tool's output, with the command that builds it, from the pages that need it. Every other page is written as below.

For each page of each flow:

1. **Resolve the sources.** Map each source kind the flow names to concrete files in this project: an artifact type to its instances under the HELIX root, a section to its heading (H2 or deeper), `docs` to the project's own documentation outside HELIX (a README, a data dictionary, an existing `docs/` tree), `code` to the build files, configuration, entry points, and tests that settle the page's claims. Read them. A page draws only on what it cites.
2. **Write for the reader.** Follow the page's outline and the writing pass, steps 1 to 5, in the page's voice, and keep to the page's kind (`publishing.md`, Page kinds): a tutorial walks one exercise to a result, a how-to gives the steps for a goal, a reference states what exists in a fixed shape, an explanation says why. What belongs to another kind goes on that page, with a link. Do not copy an artifact's tables or prose. Diagrams come from the project's architecture model when it has one (generated views), never redrawn by hand.
3. **Follow the code.** Where an artifact and the code disagree, the page states what the code does and the disagreement goes to the handoff report for `align`. Never edit an artifact from this mode.
4. **Write the provenance header** at the top of the page: one `helix:publish` line (`flow`, `page`, `kind`, `voice`, `budget`) and one `helix:source` line per source, with `#<section>` when only one section was read. Then run `skills/helix/scripts/publish_check.py stamp <page>`.
5. **Check.** Run `publish_check.py check <out>` and resolve every finding; finish the writing pass (steps 6 and 7).

## Refresh

Run `publish_check.py check <out>`. Regenerate each `stale` page from its changed sources: reread them, rewrite only the sections the change affects, rerun the writing pass, and stamp. Remove or replace a `missing-source`. Consider each `unmapped` file: cite it from the page whose task it serves, or add a project page in `.helix.yml`. `refresh` mode runs this for every flow in the project.

## Site

When `.helix.yml` sets `publish.site`, build it with `skills/helix/scripts/publish_site.py`. The site is rebuilt from the pages and never edited.

## Handoff

Report the pages written or regenerated, the sources each draws on, the artifact-to-code disagreements found (for `align`), and the check result. Commit the pages with the change that made them stale, so a reviewer sees source and page together.
