---
title: "Guide"
slug: guide
weight: 130
generated: true
---

Generated from [`workflows/modes/guide.md`](https://github.com/DocumentDrivenDX/helix/blob/main/workflows/modes/guide.md), the mode contract the HELIX skill loads. Edit that file, not this page.

Use to give a repository the documentation its readers need, and to keep it current: pages for developers, operators, users, and data consumers, each a projection of the artifacts and the code, never an edit to them. Engage on: documentation for this repository, a docs site, a developer, operator, user, or data guide, onboarding or getting started, "document this repo", one page of the guide, "the docs are out of date". The model is `workflows/references/publishing.md`; the writing standard is `workflows/references/writing-pass.md`.

The host tool is documentor (`tools/documentor/` in the HELIX repository), released with HELIX: it detects, generates, writes through an agent, checks, and assembles. Install it once from the HELIX release the project uses:

```sh
uv tool install "git+https://github.com/DocumentDrivenDX/helix@<tag>#subdirectory=tools/documentor"
```

`documentor doctor` says what the host has. The whole guide is then four commands: `documentor init --write`, `documentor build --write`, `documentor check`, and `documentor review` for a page a person evaluated. Each step below names its command and its by-hand form; without documentor, do each step by hand. Nothing is skipped silently, and the handoff names the steps done by hand.

## 1. Decide the guide

With documentor: run `documentor init --root .`. It scores the trait registry against the files git tracks and proposes the `publish:` block: which audiences, which traits, which pages each adds, generates, or delegates, and what no page may contain (`handling`). Read the evidence for each trait before accepting it. By hand: read the build and deploy files and the marker's lanes, and propose the block from the audience table in `publishing.md`.

Either way, the agent writes the confirmed block into `.helix.yml` under the `marker_edit` stop trigger. A repository with no marker gets one first (`documentor init` scaffolds it with the activity directories; by hand, write the minimal marker from `docs/install/README.md`). For each significant file no trait claims, propose a trait rather than documenting the file by guesswork; a project keeps its own traits under `publish.traits_dir`. Pages the repository already has go under `publish.existing` and are adopted, never rewritten; a reference a tool of the repository already publishes goes under `publish.delegate` and is linked, never duplicated.

## 2. Generate

With documentor: run `documentor build --root . --no-site`. It writes every generated page from the repository's structured sources and renders the architecture views under the guide when the repository has a model. Generated pages and views are never edited by hand. By hand: write each generated page as a reference in the fixed shape its trait names, citing its structured files as glob sources; it is regenerated exactly once documentor runs.

## 3. Write

With documentor: `documentor write --root .` (or `documentor build --write`, which also generates and assembles) writes every missing or stale page through the project's agent, holds each to the checks below, and has a second model evaluate it (step 4). Each page's brief is `documentor prompt <page>`: the audience entry, the writing pass, and the handling rules, the same brief an agent in this session follows.

By hand, or in this session: `documentor status --root .` lists the pages that are missing, stale, unreviewed, or unadopted, in that order, each with its reader task and sources. Without documentor, the list is every written page the audiences and traits name that does not exist or whose cited sources changed. For each page, in order:

1. **Resolve the sources.** Map each source kind the audience names to concrete files in this project: an artifact type to its instances under the HELIX root, a section to its heading (H2 or deeper), `docs` to the project's own documentation outside HELIX, `code` to the build files, configuration, entry points, and tests that settle the page's claims. Read them. A page draws only on what it cites. A source kind the project lacks (no architecture, no stories) is left out and named in the handoff; a page none of whose sources exist is written from the code and the README and says so in the handoff.
2. **Write for the reader.** Follow the page's outline and the writing pass, steps 1 to 5, in the page's voice, and keep to the page's kind (`publishing.md`, Page kinds). What belongs to another kind goes on that page, with a link. Do not copy an artifact's tables or prose. Diagrams come from the project's architecture model when it has one (generated views), else from the diagram in the artifact the page cites, trimmed to the page's reader and cited by section.
3. **Follow the code.** Where an artifact and the code disagree, the page states what the code does and the disagreement goes to the handoff for `align`. Never edit an artifact from this mode.
4. **Write the provenance header** at the top of the page: one `helix:publish` line (`audience`, `page`, `kind`, `voice`, `budget`) and one `helix:source` line per source, with `#<section>` when only one section was read. Then stamp: `documentor stamp <page>`, or by hand the first 16 hex characters of the SHA-256 of each source's text with trailing whitespace stripped from each line, or `sha256:-` with a note in the handoff that the host could not stamp.
5. **Check.** `documentor check-pages <out>` (by hand: reread every cited source against its digest, every relative link and backticked path, every handling pattern) and resolve every finding; finish the writing pass (steps 6 and 7).

A delegated page is not written; link the tool's output, with the command that builds it, from the pages that need it.

## 4. Evaluate

Every written page is evaluated before it counts as current. Evaluate as a reader who has only the page and the repository, not as its writer: a separate agent or a person, never the one who wrote it.

- **Task**: can the page's reader do its task with this page alone? Try the first step of a how-to or tutorial against the code.
- **Kind**: does it keep to its kind? A how-to with a paragraph of theory, or a reference with steps, fails.
- **Claims**: trace each factual claim to a cited source or to code, and the cited file must itself state the claim. A claim with neither is removed or sourced; a claim the code contradicts is corrected, and the disagreement goes to the handoff for `align`. A number that depends on the environment is measured and qualified, or left out.
- **Paths**: every repository path is written as code, so the path check sees it; a file the reader creates is named in the header (`<!-- helix:creates path -->`).
- **Handling**: nothing `handling.never_publish` names, even paraphrased.
- **Words**: the writing pass, steps 6 and 7.

Fix what fails, restamp, and record the evaluation: `documentor review <page> --by <agent-or-person>`, which refuses a page with any finding and records a digest of the body so an edit after review returns the page to review. By hand, add `reviewed=<date>/<who>/-` to the header and the evaluation to the handoff; documentor replaces the stamp when it next runs.

## 5. Check and assemble

`documentor check --root .` is the gate: it regenerates every generated page in memory and fails when one would change, when a written page's source moved, when a page is unreviewed, when a view drifted from the model, when a link or path breaks, when a page matches a handling pattern, or when a page is missing. Put it in CI (documentor ships the workflow: `check` on every pull request, a weekly regeneration that opens a pull request) so the pull request that makes the guide stale fails until the guide catches up. `documentor build --root .` assembles the site: into the repository's mkdocs or Hugo site when it has one, else a self-contained site under `.helix/site` (Hextra with `site.target: hextra`), one section per audience, the governed artifacts as a read-only record when `site.record` is set, delegated pages as links to their tools, every page showing the sources it was built from. By hand, the Markdown pages under the guide directory are the site: the repository host renders them.

## Handoff

Report the traits accepted and the evidence for each, the pages generated, written, adopted, delegated, and evaluated (with who evaluated them), the artifact-to-code disagreements found (for `align`), source kinds the project lacks, significant files no trait claims, the steps done by hand, and the check result. Commit the pages with the change that made them stale, so a reviewer sees source and page together.
