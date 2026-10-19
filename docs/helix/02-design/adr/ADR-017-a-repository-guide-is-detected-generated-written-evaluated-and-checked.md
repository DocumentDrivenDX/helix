---
ddx:
  id: ADR-017
  status: draft
  authoring:
    home: repo
---

# ADR-017: A repository's guide is detected, generated, written, evaluated, and checked by HELIX

## Problem

Every repository HELIX governs needs documentation for people, and each builds it by hand in its own shape: HELIX's microsite generates its reference sections and writes its narrative; tablespec's microsite does the same and publishes a guidebook besides; UMF plans a generated reference with a drift gate (its FEAT-032). Each rebuilt the same pattern (hand-written narrative, generated reference, a drift gate, a Hextra site), and none of it carries to the next repository. ADR-015 made a page a projection with provenance; nothing yet decides which pages a repository needs, makes the ones that need no judgment, or says when a written page was right rather than merely unchanged.

## Decision

We will give HELIX a `guide` mode and `skills/helix/scripts/guide.py`, which take a repository from no documentation to a checked site. Specifically:

- **Detect.** A registry of traits (`workflows/publish/traits/`) says, as data, what a kind of repository is (signals over the files git tracks) and what its readers need (flows, pages, views, watched files, handling). `guide.py init` proposes; `.helix.yml` records the decision. A significant file no trait claims is reported, and the registry grows by one trait per kind of repository met.
- **Generate** what a structured source already states (`publish_generate.py`: settings, jobs, public interfaces, packages, workflows, resources), and **delegate** what a repository's own tool already publishes (tablespec's guidebook) rather than duplicating it.
- **Write** what needs judgment with an agent (`publish`), and **evaluate** it with another reader before it counts as current (`guide.py review` stamps `reviewed=` in the page's header).
- **Check** all of it with one deterministic command that needs no agent and no network (`guide.py check`), for CI; **assemble** one site with the self-contained layout or Hextra, the theme HELIX's and tablespec's microsites use.

## Why We Chose This

### Over a per-repository microsite
The three microsites show the pattern is general and the hand-built versions are not shared. A mode and a registry make the pattern HELIX's, and each repository adds only what is particular to it: a trait, a generator, a page.

### Over agent judgment alone
An agent can write any page, but not the same page twice, and not one that is exact. Generated pages are exact and current by construction; detection makes the choice of pages repeatable; evaluation makes "written" mean "checked against its sources by another reader".

### Over a declared catalog file per repository
A declared catalog never notices a repository changing shape. Detection proposes from the files and reports what it cannot place; the recorded decision keeps the guide stable between deliberate changes.

## Consequences

**Good**: Any HELIX repository gets a guide from `guide.py init` and `build`, an agent work list from `status`, and a CI gate from `check`. References that come from structure never drift. The registry is the place to improve every repository's documentation at once.

**Trade-offs**: Each generator is code, reviewed like code; a trait or generator that misreads a kind of repository misdocuments every repository of that kind until fixed. Evaluation is a stamp a person or agent gives; the check proves only that it was given after the sources last moved. Hextra needs Go and the network to build; the self-contained layout stays the default.

**Drift signals to watch**: generated pages edited by hand; pages reviewed by their own writer; traits accepted without reading their evidence; significant files left unclaimed for long.

## Concern Impact

- **No concern impact**: the decision adds a mode, scripts, and catalog data; it selects and overrides no concern.
