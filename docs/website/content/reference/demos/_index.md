---
title: Demos
weight: 7
prev: /reference/glossary
aliases:
  - /docs/demos
---

# Demos

Eight scenarios show HELIX in motion against the four-step core workflow
Contract from the [PRD](https://github.com/DocumentDrivenDX/helix/blob/main/docs/helix/01-frame/prd.md):
write the brief, check alignment, create the work plan, hand it to the runtime.

Every demo is a **session record**: a committed `session.jsonl`
([source][demos-src]) under `docs/demos/<slug>/`. The asciinema casts on
this page are deterministic re-renders produced at build time by
`scripts/demos/render_session.py`. Capture the session once, verify it,
rebuild the cast whenever you like.

[demos-src]: https://github.com/DocumentDrivenDX/helix/tree/main/docs/demos

---

## Install HELIX in your runtime

Three short reels show runtime install sessions. The committed recordings are
historical session records; the text below names the current install path when
a recording uses an older fallback.

In Claude Code, add the marketplace and install the plugin, then verify
with `claude plugin list`.

{{< asciinema file="/demos/install-claude.cast" autoplay=true speed=1.5 >}}

In Codex, the plugin manager installs HELIX from the configured marketplace.
This recording still shows the Skills CLI fallback.

{{< asciinema file="/demos/install-codex.cast" autoplay=true speed=1.5 >}}

On Databricks Genie, fetch the single-file installer on a dev box and run
it against your workspace.

{{< asciinema file="/demos/install-databricks.cast" autoplay=true speed=1.5 >}}

---

## adopt: Drop HELIX into an existing project

One install, one ask. The skill lands; the agent gains the artifact
catalog and can scan whatever's already in the repo. No CLI to learn.

{{< asciinema file="/demos/helix-adopt.cast" autoplay=true speed=1.5 >}}

[Session record](https://github.com/DocumentDrivenDX/helix/blob/main/docs/demos/helix-adopt/session.jsonl)

---

## brief: Author the governing artifacts

Vision → PRD → concerns → first feature spec, all populated from HELIX
templates by the same skill the agent invokes. The brief is what the
agent will defend code against on day n.

{{< asciinema file="/demos/helix-brief.cast" autoplay=true speed=1.5 >}}

[Session record](https://github.com/DocumentDrivenDX/helix/blob/main/docs/demos/helix-brief/session.jsonl)

---

## align: Detect drift across the artifact graph

PRD says one thing; a recent ADR says another. The `helix` skill walks the
graph from highest authority down and reports an ordered plan to close the gap.

{{< asciinema file="/demos/helix-align.cast" autoplay=true speed=1.5 >}}

[Session record](https://github.com/DocumentDrivenDX/helix/blob/main/docs/demos/helix-align/session.jsonl)

---

## plan: Identify planning gaps

The planning side of the same skill produces authority-ranked gaps. Each gap
names the destination artifact, deliverable shape, next workflow mode, and
evidence references. This demo stops before runtime work exists.

{{< asciinema file="/demos/helix-plan.cast" autoplay=true speed=1.5 >}}

[Session record](https://github.com/DocumentDrivenDX/helix/blob/main/docs/demos/helix-plan/session.jsonl)

---

## evolve: Thread a new requirement through the stack

The product-vision scenario, made concrete: a team adds OAuth alongside
existing API-key auth. One sentence in; six authority-ranked steps out,
spanning security architecture, ADRs, feature specs, designs, tests, and
runtime work.

{{< asciinema file="/demos/helix-evolve.cast" autoplay=true speed=1.5 >}}

[Session record](https://github.com/DocumentDrivenDX/helix/blob/main/docs/demos/helix-evolve/session.jsonl)

---

## concerns: Catch technology drift before it ships

A project declares `typescript-bun` as its stack concern. The agent
writes idiomatic-looking code that nonetheless drifts to Node defaults.
Alignment catches all three drift signals.

{{< asciinema file="/demos/helix-concerns.cast" autoplay=true speed=1.5 >}}

[Session record](https://github.com/DocumentDrivenDX/helix/blob/main/docs/demos/helix-concerns/session.jsonl)

---

## review: Fresh-eyes audit against the same artifacts

A second agent inspects completed work against the artifacts that govern
it. Two blocking findings (missing revocation enforcement, missing test),
one warning (token leak in error log), filed as runtime work.

{{< asciinema file="/demos/helix-review.cast" autoplay=true speed=1.5 >}}

[Session record](https://github.com/DocumentDrivenDX/helix/blob/main/docs/demos/helix-review/session.jsonl)

---

## execute: Hand a bead to DDx

The runtime handoff. DDx selects the bead, routes to the configured harness,
work runs in a worktree, acceptance gates fire, review runs, evidence appends,
and the bead closes. HELIX stays offstage; its job was the artifacts.

{{< asciinema file="/demos/helix-execute.cast" autoplay=true speed=1.5 >}}

[Session record](https://github.com/DocumentDrivenDX/helix/blob/main/docs/demos/helix-execute/session.jsonl)

---

## Rebuilding the casts locally

```
python3 scripts/demos/render_session.py docs/demos/helix-align/session.jsonl
bash tests/validate-demos.sh
```

`validate-demos.sh` asserts schema soundness for every committed
`session.jsonl` and re-renders each into a byte-identical `.cast`. If
your render differs, either the record changed (rebuild + commit) or
the renderer changed (test will fail on every demo).
