# Practices: Lakebase (managed Postgres on Databricks)

These practices govern **how a Databricks-hosted app keeps its own state in
Lakebase**. For the boundary (`relational-data-modeling`, `databricks-apps`,
`unity-catalog`, `python-uv`) see `concern.md`.

## Requirements (Frame activity)

- List the state the product owns (sessions, drafts, workflow and job state,
  app content) and, separately, the data it only references from Unity Catalog
  or another system of record.
- State the availability claim (data loss on node failure, failover time,
  region-loss recovery point) so Design can configure for it.
- State whether non-production environments may hold production data.

## Design

- Record in DATA_DESIGN which tables Lakebase holds and which identifiers point
  outside it; no column holds governed records or entitlements.
- Map environments to branches in the TD: protected `production` (high
  availability on), child branches for QA and dev, expiring branches for pull
  requests and CI.
- Choose the Postgres major version at project creation and list required
  extensions (for example `vector`).
- Design the connection path: the app identity that owns the database, a pool,
  a fresh OAuth credential per new connection, and retry on connect.
- Design locks and queues as tables with expiry, not session-level Postgres
  state.

## Implementation

- Read connection settings through the app's one typed settings object, fed by
  the injected `PG*` variables (`databricks-apps`).
- Mint credentials with `generate_database_credential` for each new pooled
  connection; never log a token.
- Keep migrations versioned in the repository; write them expand-then-contract.
- Scope every row the app writes to its principal where the data is
  user-scoped, and enforce it in every query path.

## Testing / Verification

- Run migrations and the integration suite against a fresh branch per pull
  request; the branch expires on its own.
- Run tests locally against an embedded or local Postgres of the same major
  version; never against a shared Lakebase branch from a laptop.
- A negative test shows one principal cannot read another's user-scoped rows.
- Before claiming the availability target, observe a failover and a restore on
  a non-production project and record the evidence (`verification`).

## Quality Gates

- Migrations apply cleanly on a pull-request branch before merge.
- No configuration file or log contains a database password or OAuth token.
- Production branch is protected with high availability enabled when the
  availability claim requires it.
