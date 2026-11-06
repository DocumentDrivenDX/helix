---
ddx:
  id: ADR-003
  status: accepted
  authoring:
    home: repo
---

# ADR-003: documentor drives the agent that writes and evaluates the written pages

## Problem

ADR-001 split a guide into the parts a tool makes exactly (detection, generated references, views, the check, the site) and the parts that need judgment (the written pages), and left the judgment to an agent in a HELIX session. Nothing starts that session. A developer who runs `documentor init` and `documentor build` on a repository gets the generated pages and a work list: on documentor itself, one page of ten. The written pages wait for someone to open a `/helix guide` session and work the list by hand, and the evaluation ADR-001 requires is a stamp anyone can give, including the writer.

Everything a writer needs is already in the plan: each page's reader task, outline, word budget, voice profile, source hints, and the checks the page must pass. What is missing is the call.

## Decision

We will give documentor a `write` command that works the `status` list with a headless agent, and `build --write`, which runs it between regenerating and building the site. Specifically:

- **Write.** For each written page that is missing or stale (or one named page), documentor builds the writer's prompt from the plan entry and the voice profile, runs the agent command with only read tools on the repository, and takes the page body and the sources it cites from the agent's answer. documentor writes the header (`written=agent-<model>`), stamps the sources, and runs the same checks as `check-pages`. A page with blocking or prose findings goes back to the writer once, with the findings.
- **Evaluate with a separate reader.** A second agent call, in a fresh context and on a different model (`write` refuses one model for both), reads the page and its sources against the task and answers pass or fail with reasons. A pass is stamped with `documentor review --by agent-<model>`; a fail goes back to the writer once, then to a second evaluation. A page still failing is left unreviewed, and `status` lists it.
- **Never the writer's own stamp.** `review` refuses a reviewer whose name equals the page's `written=` field, for agents and people alike.
- **Pages already current are not touched.** `write` acts on missing and stale pages, and evaluates unreviewed ones; a rerun on a current guide makes no agent call.
- **The agent is a command.** The default is Claude Code headless (`claude -p`, read tools only); `publish.agent` in `.helix.yml` or `DOCUMENTOR_AGENT` names another. The prompt goes on standard input, and the answer comes on standard output. documentor gains no Python dependency.
- **CI is unchanged.** `check` needs no agent and no network; `write` is for a developer's machine or a scheduled job with credentials.
- **Gaps are recorded.** When a source hint names a HELIX artifact the repository does not have (no architecture document, no ADRs), the writer works from the code and records the gap in the header (`<!-- helix:gap artifact:architecture -->`). `status` reports the gaps, so a page written from code alone is visible as one.

## Why We Chose This

### Over the interactive session alone
The session stays for a person who wants to steer, and HELIX guide mode can call `documentor write` rather than restate the prompts. Alone it leaves every repository's written pages to whoever has time to open one; the plan already holds the prompt, so the tool can make the call.

### Over writing the pages in each repository that uses documentor
That is the per-repository microsite ADR-001 rejected: each repository would carry its own prompts, and an improvement to one would reach none of the others. The prompts belong with the catalog that defines the pages.

### Over the Anthropic SDK as a dependency
A command keeps documentor's install to PyYAML (R-4, R-8), lets a team pick its agent and model, and lets the tests drive a fake agent with no network.

### Over self-evaluation in the same call
A writer that grades its own page in the same context confirms its own reading. A fresh call on another model, given the page and the repository and not the writer's reasoning, is the cheapest separate reader.

## Consequences

**Good**: One command takes a repository from no documentation to a written, evaluated, checked guide and a site. The evaluation stamp says which model read the page, and the writer can no longer give it. Gaps in the HELIX artifacts are recorded on the pages written around them.

**Trade-offs**: `write` needs credentials and spends tokens; a guide of ten pages is roughly twenty to forty agent calls. An agent's page is a first draft held to the checks and one other reader, not a person's judgment; a person can still review it, and `review --by <name>` replaces the agent's stamp. The default agent command ties the out-of-box path to Claude Code.

**Drift signals to watch**: pages whose only reviewer is an agent on a repository nobody reads; `helix:gap` lines that persist; rewrites of stale pages that change more than the moved source warrants.

## Concern Impact

- **No concern impact**: the decision adds a command and a header field; it selects and overrides no concern.

## Amends

ADR-001 (the **Write** and **Evaluate** steps): the agent is invoked by documentor, and the evaluator is a different reader by rule. The PRD's out-of-scope line "Writing the narrative pages" and its later features "Agent-driven init and write" (the write half) and "Separate-reader evaluation" become requirements R-9 and R-10.
