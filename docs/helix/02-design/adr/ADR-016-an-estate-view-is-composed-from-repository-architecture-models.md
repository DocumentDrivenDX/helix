---
ddx:
  id: ADR-016
  status: draft
  authoring:
    home: repo
---

# ADR-016: An estate view is composed from repository architecture models

## Problem

A program that spans repositories has no architecture view of the whole. Each repository's `architecture.md` describes its neighbors from its own side, in its own words, and nothing checks that two repositories agree about the connection between them: one says it calls the other over MCP, the other does not mention it, and both pass their own checks. A hand-drawn landscape goes stale the day a repository changes, and says nothing about which repository to open.

## Decision

We will define one architecture model format in the catalog (`workflows/references/architecture-model.md`), lifted from praxis's checked model (praxis ADR-090), and compose the estate from the repositories' models rather than draw it. Specifically:

- A model names its own system (`[system]`, with its repository) and marks an element that is another repository's system with `system = "<id>"`.
- Each repository keeps its own model checked against its own code, with its own generator and views. The catalog owns the format, not the generator.
- `skills/helix/scripts/architecture_estate.py` reads the models of the systems an estate config lists, from local checkouts or from the repositories through `gh`, and fails when a connection is one-sided: stated by one repository's model and absent from the other's. A system a model names that the estate does not include is a warning, and the list of those is the estate's backlog.
- `render` writes the landscape as a page: one node per system with its repository, one edge per agreed connection, the commit each model was read at, and each connection as both sides state it. The page lives where the estate is governed and is regenerated when a model moves.

## Why We Chose This

### Over a hand-drawn landscape in the program's architecture record
The record's sources are meetings and vendor material, graded by evidence; the built systems' sources are code. A drawn landscape in the record can only restate what someone remembered. A composed one cites a model at a commit, and that model cites the code.

### Over one shared model for all repositories
A shared model is owned by nobody and checked against no code. Keeping each model beside the code it cites keeps the evidence check local and the pull request that changes the code the one that updates the model.

### Over trusting one side's claim
Two models that each pass their own check can still disagree about each other. Requiring both sides to state a connection turns "the diagram is wrong" into a check that names both repositories.

## Consequences

**Good**: A landscape that is right at the commits it names, and a check that fails when two repositories stop agreeing. Adopting the format is the audit each repository needed anyway.

**Trade-offs**: Each repository needs a model, and the first one for a repository is a day's work. The estate reads models only, not evidence: a model that lies about its own code passes the estate and fails its own check. Labels differ between the two sides of a connection, so the page shows both.

**Drift signals to watch**: An estate config that lists repositories with no model; one-sided findings left open; a landscape page edited by hand.

## Concern Impact

- **No concern impact**: the decision adds a reference and a script; it selects and overrides no concern.
