# CONTRACT-001 Audit: DDx-Owned Responsibilities vs DDx Implementation

Audit date: 2026-04-17

Scope audited from `CONTRACT-001`:
- Agent execution substrate
- Execution and metric substrate
- Git-context execution mechanics
- Always-on runtime metrics and provenance
- DDx-owned rows in the Post-Cycle HELIX Behavior table

Resolution legend:
- `code-link` means the claimed DDx capability exists in `~/Projects/ddx/cli` and the cited file:line is the implementation anchor.
- `new-DDx-bead` means the capability is still DDx-owned but not fully shipped; the cited DDx tracker bead carries deterministic acceptance.
- `HELIX-backport` would mean the capability should move back to HELIX with a contract amendment diff. No row required that outcome in this audit.

This audit does **not** amend CONTRACT-001 ownership. No amendment-notification bead was filed in HELIX because every unresolved DDx-owned claim was resolved by a new DDx-side bead instead of changing ownership or deleting a DDx responsibility.

## Agent execution substrate

| DDx-owned responsibility | Actual DDx implementation audit | Terminal resolution |
|---|---|---|
| `ddx agent run` as the general harness interface | DDx ships a top-level `agent` surface plus `agent run`, with harness dispatch, profile routing, quorum, session logging, and prompt execution. | `code-link`: `~/Projects/ddx/cli/cmd/agent_cmd.go:28`, `~/Projects/ddx/cli/cmd/agent_cmd.go:109` |
| `ddx agent execute-bead <bead-id> [--from <rev>] [--no-merge]` as the canonical git-aware single-bead execution primitive | DDx ships the CLI entrypoint, the isolated-worktree worker, and the landing path that merges or preserves the result. | `code-link`: `~/Projects/ddx/cli/cmd/agent_execute_bead.go:26`, `~/Projects/ddx/cli/internal/agent/execute_bead.go:360`, `~/Projects/ddx/cli/internal/agent/execute_bead_land.go:557` |
| `ddx agent execute-loop [--once] [--poll-interval <duration>]` as the canonical single-project queue-drain primitive | DDx ships execute-loop, the queue-drain worker, and the server worker submission path for background execution. | `code-link`: `~/Projects/ddx/cli/cmd/agent_cmd.go:1255`, `~/Projects/ddx/cli/internal/agent/execute_bead_loop.go:174`, `~/Projects/ddx/cli/internal/server/workers.go:180` |
| Standard harness/model/effort/preset controls available through the DDx agent surface | DDx exposes harness/model/provider/model-ref/effort/profile controls on `agent run`, `execute-bead`, and `execute-loop`. | `code-link`: `~/Projects/ddx/cli/cmd/agent_cmd.go:32`, `~/Projects/ddx/cli/cmd/agent_cmd.go:118`, `~/Projects/ddx/cli/cmd/agent_cmd.go:1324`, `~/Projects/ddx/cli/cmd/agent_execute_bead.go:73` |
| Session capture, transcript capture, and runtime evidence capture | DDx writes per-run session logs, emits execute-bead prompt/manifest/result artifacts, and records worker/event logs for managed loop workers. | `code-link`: `~/Projects/ddx/cli/internal/agent/agent_runner.go:132`, `~/Projects/ddx/cli/internal/agent/execute_bead.go:756`, `~/Projects/ddx/cli/internal/server/workers.go:218` |

## Execution and Metric Substrate

| DDx-owned responsibility | Actual DDx implementation audit | Terminal resolution |
|---|---|---|
| Graph-authored execution documents as authoritative definitions | DDx parses `ddx.execution` frontmatter into `DocExecDef`, projects it into the doc graph, and validates/runs execution definitions against graph artifacts. | `code-link`: `~/Projects/ddx/cli/internal/docgraph/frontmatter.go:23`, `~/Projects/ddx/cli/internal/docgraph/docgraph.go:76`, `~/Projects/ddx/cli/internal/exec/store.go:130` |
| Immutable execution runs stored in the DDx execution substrate | DDx persists run manifests and result bundles under `.ddx/exec/runs` plus attachment directories with atomic bundle writes. | `code-link`: `~/Projects/ddx/cli/internal/exec/store.go:52`, `~/Projects/ddx/cli/internal/exec/store.go:171`, `~/Projects/ddx/cli/internal/exec/store.go:407` |
| Metric projection over execution runs | DDx aggregates execution evidence into per-bead metrics and broader process metrics/cost reports. | `code-link`: `~/Projects/ddx/cli/cmd/bead_metrics.go:33`, `~/Projects/ddx/cli/internal/processmetrics/processmetrics.go:24`, `~/Projects/ddx/cli/internal/processmetrics/processmetrics.go:133` |
| Required execution semantics sufficient to decide merge vs preserve | DDx has dormant gate machinery (`evaluateRequiredGates`, `checks.json`), but managed execute-bead/execute-loop paths do not currently wire governing IDs/worktree context into pre-land gate evaluation. | `new-DDx-bead`: `ddx-3e7f8213` |
| Metric ratchet evaluation sufficient to decide merge vs preserve | DDx stores metric definitions, comparisons, and thresholds, but managed bead landing does not yet preserve attempts based on ratchet outcomes. | `new-DDx-bead`: `ddx-b3e942d6` |

## Git-Context Execution Mechanics

| DDx-owned responsibility | Actual DDx implementation audit | Terminal resolution |
|---|---|---|
| Dirty-tree checkpointing before managed execution | DDx ships a manual `ddx checkpoint` command, but managed execute-bead/execute-loop do not automatically checkpoint a dirty parent tree before spawning the worker worktree. | `new-DDx-bead`: `ddx-91bc770a` |
| Isolated worktree execution | DDx creates per-attempt worktrees under `$TMPDIR/ddx-exec-wt/.execute-bead-wt-*` and runs the harness inside that isolated tree. | `code-link`: `~/Projects/ddx/cli/internal/agent/execute_bead.go:193`, `~/Projects/ddx/cli/internal/agent/execute_bead.go:207`, `~/Projects/ddx/cli/internal/agent/execute_bead.go:394` |
| Preserved hidden refs for non-landed attempts | DDx preserves failed/conflicted/no-merge results under `refs/ddx/iterations/...`. | `code-link`: `~/Projects/ddx/cli/internal/agent/execute_bead_orchestrator.go:19`, `~/Projects/ddx/cli/internal/agent/execute_bead_orchestrator.go:170`, `~/Projects/ddx/cli/internal/agent/execute_bead_land.go:654` |
| Rebase only to prepare fast-forward landing | DDx actually lands by fast-forward-or-merge and explicitly preserves replay fidelity by avoiding worker-commit rewrite. The shipped implementation satisfies the git-safety intent without a rebase phase. | `code-link`: `~/Projects/ddx/cli/internal/agent/execute_bead_land.go:11`, `~/Projects/ddx/cli/internal/agent/execute_bead_land.go:31`, `~/Projects/ddx/cli/internal/agent/execute_bead_land.go:606` |
| Fast-forward landing when merge-eligible | DDx fast-forwards the target ref directly when the current tip still equals `BaseRev`. | `code-link`: `~/Projects/ddx/cli/internal/agent/execute_bead_land.go:606` |
| Guaranteed worktree cleanup after landing or preservation | DDx removes per-attempt worker worktrees with deferred cleanup and prunes orphaned worktrees before subsequent runs. | `code-link`: `~/Projects/ddx/cli/internal/agent/execute_bead.go:399`, `~/Projects/ddx/cli/internal/agent/execute_bead_orchestrator.go:330`, `~/Projects/ddx/cli/internal/agent/execute_bead_land.go:649` |

## Always-On Runtime Metrics and Provenance

| DDx-owned responsibility | Actual DDx implementation audit | Terminal resolution |
|---|---|---|
| harness | Captured on execute-bead results and session entries. | `code-link`: `~/Projects/ddx/cli/internal/agent/execute_bead.go:625`, `~/Projects/ddx/cli/internal/agent/types.go:111` |
| model | Captured on execute-bead results and session entries. | `code-link`: `~/Projects/ddx/cli/internal/agent/execute_bead.go:627`, `~/Projects/ddx/cli/internal/agent/types.go:114` |
| session ID | Generated per managed execute-bead attempt and persisted in result/session records. | `code-link`: `~/Projects/ddx/cli/internal/agent/execute_bead.go:441`, `~/Projects/ddx/cli/internal/agent/execute_bead.go:628`, `~/Projects/ddx/cli/internal/agent/types.go:104` |
| elapsed duration | Captured as `duration_ms` on execute-bead results and session entries. | `code-link`: `~/Projects/ddx/cli/internal/agent/execute_bead.go:521`, `~/Projects/ddx/cli/internal/agent/execute_bead.go:629`, `~/Projects/ddx/cli/internal/agent/types.go:129` |
| token usage | Captured from harness results and persisted in execute-bead results, usage artifacts, and session entries. | `code-link`: `~/Projects/ddx/cli/internal/agent/execute_bead.go:464`, `~/Projects/ddx/cli/internal/agent/execute_bead.go:541`, `~/Projects/ddx/cli/internal/agent/types.go:125` |
| cost | Captured from harness results and persisted in execute-bead results, usage artifacts, and session entries. | `code-link`: `~/Projects/ddx/cli/internal/agent/execute_bead.go:468`, `~/Projects/ddx/cli/internal/agent/execute_bead.go:546`, `~/Projects/ddx/cli/internal/agent/types.go:128` |
| base revision | Captured before worktree creation and persisted in execute-bead results, manifests, and session entries. | `code-link`: `~/Projects/ddx/cli/internal/agent/execute_bead.go:388`, `~/Projects/ddx/cli/internal/agent/execute_bead.go:623`, `~/Projects/ddx/cli/internal/agent/types.go:133` |
| result revision | Captured from the worker or land step and persisted in execute-bead results and session entries. | `code-link`: `~/Projects/ddx/cli/internal/agent/execute_bead.go:508`, `~/Projects/ddx/cli/internal/agent/execute_bead.go:624`, `~/Projects/ddx/cli/internal/agent/execute_bead_land.go:743`, `~/Projects/ddx/cli/internal/agent/types.go:134` |

## Post-Cycle HELIX Behavior Table: DDx-Owned Rows

| DDx-owned responsibility | Actual DDx implementation audit | Terminal resolution |
|---|---|---|
| Closing SHA sync | Execute-loop closes merged work with the landed `result_rev` as `closing_commit_sha`. | `code-link`: `~/Projects/ddx/cli/internal/agent/execute_bead_loop.go:406`, `~/Projects/ddx/cli/internal/bead/store.go:787` |
| Build gate (pre-merge check) | DDx has gate-evaluation scaffolding but the managed landing paths do not currently enforce a pre-merge build gate before land. | `new-DDx-bead`: `ddx-3e7f8213` |
| Retry suppression | DDx writes `execute-loop-retry-after`, filters retry-parked beads out of `ReadyExecution()`, and returns `retry_after` in execute-loop results. The remaining gap is blocker surfacing, not cooldown creation/filtering. | `code-link`: `~/Projects/ddx/cli/internal/bead/store.go:624`, `~/Projects/ddx/cli/internal/bead/store.go:1015`, `~/Projects/ddx/cli/internal/agent/execute_bead_loop.go:545` |
| Orphan worktree recovery | DDx recovers stale execute-bead worktrees before spawning a new worker. | `code-link`: `~/Projects/ddx/cli/cmd/agent_execute_bead.go:147`, `~/Projects/ddx/cli/internal/agent/execute_bead_orchestrator.go:330` |

## Notes

- DDx blocker surfacing is the only audited item where cooldown state exists in the substrate but is not yet fully surfaced through the operator query surface; that gap is tracked as `ddx-4802a7b3`.
- The known gap "no structured event when HELIX injects a supervisory bead" is outside this matrix because queue injection is HELIX-owned in CONTRACT-001's Post-Cycle table, not a DDx-owned responsibility row.
- Existing DDx/HELIX contract ownership remains unchanged by this audit pass.
