# HELIX Action: E2E Ladder

You are building up end-to-end coverage as a **ladder** of scenarios of
increasing complexity, each rung a durable automated test that drives the real
runtime boundary. This replaces the operator running one manual scenario per chat
session ("can I test it now?" → set it up by hand → throw it away) with a climbing
sequence of committed tests that stay in CI.

The ladder's discipline is twofold: a **progression spec** (the rungs, in order,
so the loop has durable state) and the **real runtime boundary** (each rung drives
a real client, not a unit stub — the `verification` concern's evidence gate).

## Action Input

You may receive:

- a **product/surface** to build the ladder for (an MCP server, an HTTP API, a
  web flow, a CLI)
- an existing **ladder spec** to continue, or a prompt to define one
- `--client <kind>`: the real client that exercises the boundary (a real agent for
  an MCP server, an HTTP client for an API, a browser for web, a shell for a CLI)

## Authority Hierarchy

1. Product Requirements / Feature Specs (the flows the ladder must cover)
2. Acceptance Criteria (each rung satisfies one or more)
3. Test Plans (where the ladder is recorded)
4. Source / running system (what the rungs exercise)

## STEP 0 - Bootstrap

0. **Context Recovery**: Re-read AGENTS.md so the start command, test runner, and
   real-client harness are fresh.
1. Confirm the running system is reachable by the real client: a start command
   (with seed data) the test can launch and a real client can connect to. If the
   boundary cannot be driven by a real client, this action is blocked — report it
   (the unit suite is not a substitute; that is exactly the gap this catches).

## STEP 1 - Define (or load) the Ladder

Record the rungs as a **progression spec** — the durable state the loop owns, so
the `DONE` list is never re-typed into a prompt. Order rungs by increasing
complexity, each building on the last:

1. **Setup-only** — the simplest real interaction: connect, discover, set up state
   without executing the terminal action.
2. **Single happy path** — one complete flow end-to-end (setup → the one core
   action → observe the result).
3. **Multi-step** — a sequence (e.g. step → wait/branch → step) exercising
   composition.
4. **Scheduled / deferred / edge** — time, retries, blackouts, recycling, and the
   guard/negative branches (rejection, idempotency, unauthorized) the
   `verification` concern requires.

Each rung names the acceptance criteria it covers. Record the spec and its `DONE`
list in the test plan.

## STEP 2 - Climb One Rung (iterate)

Take the lowest **unbuilt** rung and make it a committed, automated test:

1. Implement the scenario as a test that **drives the real client** against the
   running system (`--client`), not a unit stub. For an MCP server that means a
   real agent completing the handshake and invoking the tools; for an API a real
   request client; for web a browser; for a CLI a real shell invocation.
2. Run it green against the running system. Capture the per-rung evidence
   (command + exit, target env, the observed outcome) — the rung's slice of the
   `verification` evidence. The full project-level verification gate (its five
   artifacts, including the adversarial re-review and selection↔build coherence)
   still applies when the work is claimed done; a green rung is not by itself the
   whole gate.
3. Commit the rung as one durable test and mark it `DONE` in the spec. It now runs
   in CI forever — it is not a throwaway manual session.

## STEP 3 - Loop or Stop

- If unbuilt rungs remain: go to STEP 2 for the next.
- When every rung is a committed green test: **DONE** — the ladder is the e2e suite.
- If a rung cannot be driven by a real client (a genuinely infeasible boundary):
  record the `verification`-concern exception with the substitute evidence; do not
  silently downgrade it to a unit test.

## Output

Report:

1. The ladder spec: the rungs, in order, with `DONE` status and covered ACs.
2. Per rung climbed: the scenario, the real client used, and the green evidence.
3. Final disposition (full ladder green, or recorded infeasible-boundary
   exceptions).

Then emit the machine-readable trailer:

```
E2E_LADDER_STATUS: DONE|IN_PROGRESS|BLOCKED
RUNGS_TOTAL: N
RUNGS_DONE: N
CLIENT: <real-client-kind>
GATE: green|red
```

- `DONE`: every rung a committed green test driving the real boundary.
- `IN_PROGRESS`: rungs remain; the spec holds the durable state to resume.
- `BLOCKED`: the running system is not reachable by a real client — report; a
  unit suite does not substitute.

## Runtime Integration Appendix

- The real-client harness is surface-specific (the `testing` concern's *surface →
  real-path harness* mapping; the `e2e-framework` slot owns the web runner). The
  ladder applies that mapping rung by rung.
- This action composes the `verification` evidence gate and the test plan; it does
  not restate how to write tests. It is the progression loop that turns
  one-off manual scenarios into a durable, climbing e2e suite.
