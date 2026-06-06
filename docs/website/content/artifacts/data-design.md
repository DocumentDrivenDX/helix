---
title: "Data Design — HELIX Bead Tracker"
slug: data-design
weight: 380
activity: "Design"
source: "02-design/data-design.md"
generated: true
---
# Data Design — HELIX Bead Tracker

**Scope**: The `.ddx/beads.jsonl` issue tracker that anchors HELIX execution.
**Status**: Complete

## Data Summary

- Scope: The bead tracker — HELIX's only durable execution-state store. Beads
  are work units (issues, tasks, epics, planning notes) governed by upstream
  artifacts and consumed by `ddx agent execute-bead` / `ddx agent ddx work`.
- Storage systems: Append-friendly JSON Lines file (`.ddx/beads.jsonl`) with
  per-record locking enforced by the `ddx bead` CLI. No database, no daemon
  required for reads.
- Main concerns: Concurrent writer safety (operator and supervisor may both
  mutate during a live `ddx work`), stale-claim recovery, deterministic
  ready/blocked queries, append history preserved in `events`, and forward-
  compatible schema evolution without breaking existing tooling.
- Authority: [CONTRACT-001](/artifacts/contracts/contract-001-ddx-helix-boundary/)
  (`ddx bead` and `.ddx/beads.jsonl` belong to DDx; HELIX consumes via the
  CLI), [ADR-002](/artifacts/adr/) (tracker write safety model — referenced where
  available), and [API-001](/artifacts/contracts/api-001-helix-tracker-mutation/)
  (HELIX-side mutation surface).

## Entities and Stores

| Entity or Store | Purpose | Key Fields | Volume / Growth | Notes |
|-----------------|---------|------------|-----------------|-------|
| `beads.jsonl` (record per line) | Durable issue/work-unit state | `id`, `title`, `description`, `status`, `priority`, `issue_type`, `labels[]`, `parent`, `dependencies[]`, `acceptance`, `spec-id`, `events[]`, claim metadata, `created_at`, `updated_at` | Hundreds to low thousands of records over a project lifetime; one file per repo | Append/rewrite via `ddx bead`; never edit by hand during a live run |
| `events[]` (embedded array per bead) | Append-only audit trail of state transitions and execution attempts | `event_type`, `timestamp`, `actor`, `payload` | 10s–100s per bead over its lifetime | Bounded by execution count; older events may be summarized but never silently truncated |
| Claim metadata (embedded fields) | Single-writer guard for active execution | `claimed-at` (ISO-8601 UTC), `claimed-pid`, `claimed-machine`, `owner` | One slot per in-progress bead | Cleared by `--unclaim`, `close`, or orphan-recovery sweep |
| Execution-eligibility metadata | Distinguishes execution-ready beads from refinement/superseded ones | `execution-eligible`, `superseded-by`, `replaces` | Sparse — most beads do not need it | Drives `ddx bead list --execution-ready` |

## Relationships

| From | To | Type | Cardinality | On Delete |
|------|----|------|-------------|-----------|
| Bead | Bead (`parent`) | epic-child | N:1 (optional) | RESTRICT — close epics only after children resolve |
| Bead | Bead (`dependencies[]`) | depends-on | N:M (optional) | RESTRICT — closing a dep does not auto-close dependents; readiness recomputes |
| Bead | Governing artifact (`spec-id`) | governed-by | N:1 (optional path string) | No delete propagation — `spec-id` is a path, not a foreign key; drift is surfaced via review |
| Bead | Bead (`superseded-by` / `replaces`) | supersession | N:1 (optional) | Supersession redirects readiness queries; original bead remains for audit |

## Access Patterns and Constraints

| Access Pattern | Frequency | Performance Need | Supporting Index or Cache |
|----------------|-----------|------------------|---------------------------|
| `ddx bead list --status open --json` (full read) | Every supervisor cycle | Sub-second on thousand-record stores | Sequential scan of JSONL — acceptable at this scale |
| `ddx bead ready` (filter open + deps satisfied + not superseded) | Every supervisor cycle | Sub-second | Computed in-memory after full read |
| Single-bead update (`update`, `claim`, `close`) | Every build cycle (many per `ddx work`) | Strict atomicity — no torn writes | Exclusive file lock around read-modify-rewrite; `events[]` append captures intent before status changes |
| Orphan-recovery sweep (claims older than `HELIX_ORPHAN_THRESHOLD`, default 7200s) | Periodic during long runs | Bounded; touches only stale claims | Filter on `claimed-at` age + dead-PID check |
|  snapshot (counts by status, focused-epic view) | Operator-initiated, ad hoc | Sub-second | Reuses the open-list scan |

## Validation and Security

| Field or Data Type | Rules / Classification | Protection or Error Handling |
|--------------------|------------------------|------------------------------|
| `id` | Required; opaque (`helix-<8hex>`); unique within file | Generator rejects duplicates; corrupt IDs surface as parse failures |
| `status` | Enum: `open`, `in_progress`, `blocked`, `closed`, `superseded` | Mutations validated by `ddx bead`; raw JSONL edits during a live run risk torn state |
| `claimed-at` | ISO-8601 UTC; cleared on `--unclaim` and `close` | Orphan recovery uses age threshold + dead-PID check before clearing |
| `claimed-pid`, `claimed-machine` | Free-form identifiers | Dead-PID check is part of orphan recovery; recovery never destroys unrelated worktree state |
| `labels[]` | Free-form strings; `helix`, `activity:*`, `kind:*`, `area:*`, `story:US-*` are conventional | Convention enforced by HELIX skills; tracker accepts any label |
| `description`, `acceptance`, `title` | Free-form text — may include rendered context digests | No secret-bearing fields by contract; the tracker is checked into the repo by default. Operators must keep secrets out of bead bodies. |
| `events[]` payloads | Append-only history | Never rewritten by HELIX; corruption is recoverable from git history |
| File-level access | Repo-relative; readable by anyone with repo read access | Treat as public-ish: do not store secrets, customer data, or credentials |

## Migration Strategy

- Tooling: `ddx bead` is the only sanctioned writer. Schema evolution is
  managed downstream in DDx; HELIX consumes through the published CLI
  contract per CONTRACT-001.
- Approach: Additive fields land first (new optional metadata is ignored by
  older readers). Status enum extensions require a coordinated reader update
  before the new value is emitted. Removed fields go through a deprecation
  cycle — the writer stops emitting first, then a later major version drops
  read tolerance.
- Backfill or cleanup: Historical migration from the legacy `.helix/issues.jsonl`
  store is captured in `docs/helix/02-design/plan-2026-03-27-supervisory-concurrency.md`
  and the surrounding planning beads. The migration was a one-shot rewrite
  with the legacy file retired; no live rollback path is supported.
- Rollback: Because the file is plain JSONL under git, any unintended schema
  drift is recoverable by reverting the offending commit. Live tracker writes
  during a `ddx work` are audited via `events[]` so a torn write can be
  reconstructed without fully reverting the file.
