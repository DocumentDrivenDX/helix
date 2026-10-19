# Guide

Use to give a repository the documentation its readers need, and to keep it current: point HELIX at the repository, and the guide is detected, generated, written, evaluated, checked, and assembled into one site. Engage on: documentation for this repository, a docs site or microsite, a developer or user guide, "document this repo", onboarding docs, a reference that keeps drifting, "the docs are out of date". `publish` (`workflows/modes/publish.md`) is how each written page is made; this mode decides which pages exist and runs everything around them. The model is `workflows/references/guide.md`; the script is `skills/helix/scripts/guide.py`.

## 1. Detect

Run `guide.py init --root .`. It scores the trait registry against the files git tracks and proposes the guide: which readers (flows), which traits, which pages each adds, generates, or delegates, and what no page may contain (`handling`). Read the evidence for each trait before accepting it. Write the confirmed block into `.helix.yml` (`--write` does it when the file has no `publish:` block), following the active autonomy contract. For each significant file no trait claims, propose a trait (`workflows/publish/traits/`) rather than documenting it by guesswork.

## 2. Generate

Run `guide.py build --root . --no-site`. It writes every generated page from the repository's structured sources and renders the architecture views when the repository has a model (`workflows/references/architecture-model.md`). Generated pages and views are never edited by hand. A repository with no model and more than one deployed part gets one: write `architecture-model.toml` from the code, every element citing a file and a string it contains, before the written pages that embed its views.

## 3. Write

Run `guide.py status --root .`. For each page it lists as missing or stale, in the order it lists them, follow `publish`: resolve the sources, write to the page's Diátaxis kind and reader task, follow the code where an artifact disagrees, write the provenance header, stamp, check. A delegated page is not written; link the tool's output, with the command that builds it, from the pages that need it.

## 4. Evaluate

Every written page is evaluated before it counts as current; `status` lists the ones that are not (`REVIEW`). Evaluate as a reader who has only the page and the repository, not as its writer: preferably a separate agent, or a person.

- **Task**: can the page's reader do its task with this page alone? Try the first step of a how-to or tutorial against the code.
- **Kind**: does it keep to its kind? A how-to with a paragraph of theory, or a reference with steps, fails.
- **The task that governs** is the one `guide.py status` shows: a trait can replace a flow's page, with its own task and outline.
- **Claims**: trace each factual claim to a cited source or to code, and the cited file must itself state the claim (a real file cited for behavior that lives elsewhere fails). A claim with neither is removed or sourced; a claim the code contradicts is corrected, and the disagreement goes to the handoff for `align`. A number that depends on the environment (a timing, a port, a count of anything not in the repository) is measured and qualified, or left out.
- **Paths**: every repository path is written as code, so the path check sees it; a file the reader creates is named in the header (`<!-- helix:creates path -->`).
- **Handling**: nothing `handling.never_publish` names, even paraphrased (a pattern catches only the shapes it knows).
- **Words**: the writing pass (`workflows/references/writing-pass.md`), steps 6 and 7.

Fix what fails, restamp, and record the evaluation: `guide.py review <page> --by <agent-or-person>`. `review` refuses a page that has any finding, prose warnings included. The stamp records a digest of the page, so an edit after review (even a fix to the wording) returns the page to review, and a page whose sources change goes stale and is evaluated again after it is rewritten.

## 5. Check and assemble

Run `guide.py check --root .`. It regenerates every generated page in memory and fails when one would change, when a written page's source moved, when a view drifted from the model, when a link or path breaks, when a page matches a handling pattern, or when a page is missing. Add it to CI (`workflows/publish/ci/github-actions.yml` is the template: `check` on every pull request, a weekly regeneration that opens a pull request) so a pull request that makes the guide stale fails until the guide catches up. `guide.py build --root .` assembles the site: one section per reader, pages in kind order, delegated pages as links to their tools, every page showing the sources it was built from.

## Handoff

Report the traits accepted and the evidence for each, the pages generated, written, delegated, and evaluated (with who evaluated them), the artifact-to-code disagreements found (for `align`), significant files no trait claims, and the `check` result.
