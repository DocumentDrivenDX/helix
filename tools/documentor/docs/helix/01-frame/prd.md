---
ddx:
  id: documentor.prd
  authoring:
    home: repo
---
# documentor PRD

## Summary

documentor implements HELIX's `guide` mode as a Python package with one command line. It detects
what a repository is, generates the pages a structured source already states, renders
architecture views from a checked model, lists the pages an agent must write, records their
evaluation, checks all of it in CI without an agent, and assembles the pages into a site.

## Goals

1. **Consistent across repositories.** Every repository gets the same audiences and page shapes
   from HELIX's catalog; a repository adds a trait, a generator, or a page, never a new scheme.
2. **Exact where a source has structure.** Settings, jobs, public interfaces, packages, resources,
   workflows, API operations, commands, and tools are generated, never written, and cannot drift.
3. **A gate, not a complaint.** `documentor check` fails the pull request that leaves the guide
   behind: a stale source, a missing page, an unreviewed page, a drifted view, a broken link, a
   handling breach.
4. **The repository's own tools first.** A reference another tool publishes better is delegated
   and linked; a site the repository has is emitted into, not replaced.
5. **Safe for regulated data.** `handling` is read before any source and enforced by pattern;
   generators read structure only.

## Requirements

- R-1 `init` proposes the `publish:` block from the catalog's traits and the project's own
  (`publish.traits_dir`), with the evidence for each; on a repository with no HELIX it scaffolds
  the marker and the activity directories and names the HELIX install step.
- R-2 `build` regenerates every generated page (packaged generators, entry-point generators, or a
  project command) and the architecture views under the guide, never into an artifact.
- R-3 `status` lists every page with one state (missing, stale, unreviewed, unadopted, current,
  delegated) and the agent's ordered work list.
- R-4 `check` exits non-zero on any blocking finding or unfinished page and needs no agent, no
  network, and no tool beyond Python 3.11 and PyYAML.
- R-5 `review` stamps an evaluation that lapses when the page's body changes; `adopt` brings a
  hand-written page under the guide unchanged.
- R-6 `site` emits into an existing mkdocs or Hugo site, else scaffolds Hextra; the Markdown pages
  stay the record.
- R-7 The HELIX half of the catalog (audiences, voice) is copied from the HELIX repository's own
  `workflows/`, a test fails when the copy differs, and `--version` reports it; `publish.schema` versions the configuration contract.
- R-8 documentor lives in the HELIX repository under `tools/documentor/` and is released with HELIX;
  a repository's CI runs it from a HELIX release tag through `uvx` (`#subdirectory=tools/documentor`);
  nothing is vendored.
- R-9 `write` (and `build --write`) writes each missing or stale written page with a headless
  agent command, from the plan entry and the voice profile, and holds it to the checks; it never
  touches a current page, and it records a HELIX artifact the page had to do without (ADR-003).
- R-10 A written page is evaluated by a separate reader: `write` stamps a pass from a fresh agent
  call, and `review` refuses a reviewer who is the page's writer (ADR-003).

## Out of scope (now)

- Agent-driven bootstrap of HELIX artifacts from code (`init --backfill`): a later feature, after
  the hand-driven flow has worked on three repositories.
- Hosting: where a private site is served is the repository's decision.

## Later features and open questions

- **Agent-driven init** through a headless HELIX session (`claude -p --plugin-dir`), local only,
  never in CI. (Agent-driven write is R-9.)
- **Design-system theme** for the Hextra scaffold and the diagrams, taking a design system's
  tokens when its repository publishes under DocumentDrivenDX.
- **Coverage**: notebooks, changelog and what's new, versioned docs for libraries, a security and
  access-model page for operators, glossary, per-package sections for monorepos, screenshots for
  user tutorials (the design system's audit already captures screens), Dockerfile, compose, dbt,
  Go, Rust, JVM, Django traits.
- **Rewrite churn**: a page that cites a busy code file goes stale on every edit; guidance is to
  cite the file whose content the page states; symbol-level anchors are a possible refinement.
- **Executable checks for tutorials**: `verify:` commands run in CI.
- **Search and versioning** come from the site the repository already has; the scaffold has
  Hextra's search and no versioning.
- **A newcomer-trial metric** for "easy to read": no trial has been run yet.
