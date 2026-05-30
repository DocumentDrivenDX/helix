---
title: "Rust + Cargo"
slug: rust-cargo
generated: true
aliases:
  - /reference/glossary/concerns/rust-cargo
---

**Category:** Tech Stack · **Areas:** all

## Description

## Category
tech-stack

## Areas
all

## Slot
language-runtime

## Components

- **Language**: Rust (latest stable; MSRV pinned in `rust-toolchain.toml`)
- **Build system**: Cargo workspace (resolver = "2")
- **Edition**: 2024
- **Toolchain pinning**: `rust-toolchain.toml` and `workspace.package.rust-version` must stay in lockstep

## Constraints

- All code must pass `cargo clippy --workspace --all-targets --no-deps -- -D warnings`
- All code must pass `cargo fmt --all -- --check`
- Workspace lints (`[workspace.lints]`) are authoritative; every crate opts in via `[lints] workspace = true`
- `unsafe_code = "deny"` at the workspace level; any `unsafe` block requires a `// SAFETY:` comment and a local `#[allow(unsafe_code)]`
- No `.unwrap()` in library crates — use `?` or explicit error handling
- Use `thiserror` for library error types; use `anyhow` for application/binary error handling
- Public API items must have `///` doc comments
- All dependencies declared in `[workspace.dependencies]`; crates reference with `{ workspace = true }`
- `cargo deny check` must pass (licenses, advisories, registry sources)
- `cargo machete` must pass (no unused dependencies)
- Repo-owned Rust commands run through a pinned-toolchain wrapper; do not rely on ambient `rustc`/`cargo` from PATH

## Clippy Lint Policy

Workspace-level `[workspace.lints.clippy]`:
- `all`, `pedantic`, `nursery` at `warn` (lint group baseline)
- `unwrap_used`, `todo`, `unimplemented`, `dbg_macro`, `print_stdout` at `deny`
- Selected pedantic/nursery lints may be `allow`-listed project-wide when they produce excessive noise; each allow must be documented in the workspace `Cargo.toml`

Workspace-level `[workspace.lints.rust]`:
- `unsafe_code = "deny"`
- `unused_must_use = "deny"`
- `missing_docs = "warn"`
- `dead_code = "warn"`

## Profile Conventions

- `[profile.dev]`: fast builds, `debug = 1`, deps at `opt-level = 1`
- `[profile.release]`: `lto = "thin"`, `codegen-units = 8`, `strip = true`
- `[profile.release-dist]` (CI only): `lto = "fat"`, `codegen-units = 1`, `panic = "abort"`
- `[profile.profiling]`: inherits release, `debug = 1`, `strip = false`

## When to use

Performance-critical systems, CLI tools, infrastructure software, and projects
where memory safety and zero-cost abstractions matter. The workspace lint policy
above is the minimum bar; projects may tighten further via `[profile]` or
additional deny-level lints.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: Rust + Cargo workspace (clippy, fmt, cargo-deny/machete, pinned toolchain) as the language-runtime
- TD: workspace lints, error-handling (thiserror/anyhow), unsafe policy, profile conventions

## Practices by activity

Agents working in any of these activities inherit the practices below via the bead's context digest.

## Requirements (Frame activity)
- Specify MSRV explicitly; it must be stable enough for CI and local dev
- Identify crates that are libraries vs binaries — error handling strategy differs
- If concurrency correctness is a requirement, plan for `loom`-based testing

## Design
- Organize as a Cargo workspace; every logical component is its own crate
- All inter-crate dependencies declared in `[workspace.dependencies]`
- Separate `crates/` (libraries) from `tools/` or `bin/` (binaries/CLIs) in workspace layout
- Design error types using `thiserror` for library crates; surface errors with `anyhow` in binaries
- Prefer newtypes and strong typing over stringly-typed parameters
- Concurrent state: prefer `Arc<Mutex<T>>` or `dashmap` for shared state; use `loom` for model-checking critical sections

## Implementation
- Run all commands through the pinned-toolchain wrapper script (e.g. `scripts/with-pinned-rust.sh cargo ...`)
- Every new crate must include `[lints] workspace = true` in its `Cargo.toml`
- Style: inline format args (`format!("{x}")`), method refs over closures (`.map(String::as_str)`), explicit match arms over wildcards, collapse nested ifs
- No `println!`/`eprintln!` for operational output — use `tracing` events
- No `.unwrap()` or `.expect()` in library code; in binary code, only at startup with a clear message
- `unsafe` blocks: add `// SAFETY:` comment explaining invariants, add local `#[allow(unsafe_code)]`, document in PR
- Adding a dependency: add to `[workspace.dependencies]` first, reference with `{ workspace = true }`, then run `cargo deny check` and `cargo machete`

## Testing
- Unit tests in `#[cfg(test)]` modules within the source file
- Integration tests in `tests/integration/`; contract/E2E tests in separate crates
- Use `proptest` for property-based testing of pure functions and data invariants
- Use `loom` for model-checking concurrent code (mutex invariants, atomic correctness)
- Use `rstest` for parameterized test cases
- Use `insta` for snapshot testing of complex outputs
- Use `testcontainers` for tests requiring real external services (databases, message queues)
- Use `tempfile` for filesystem fixtures; never hard-code paths
- Run focused tests first: `cargo test -p <crate> <test_name>`, then full suite
- Coverage: `cargo llvm-cov` for source-line coverage gating

## Quality Gates (pre-commit / CI)
- `cargo fmt --all -- --check`
- `cargo clippy --workspace --all-targets --no-deps -- -D warnings -D clippy::todo -D clippy::unimplemented -D clippy::dbg_macro -D clippy::print_stdout -D clippy::unwrap_used`
- `cargo deny check`
- `cargo machete crates tools` (or workspace equivalent)
- `cargo test --workspace` (excluding infra-dependent suites in pure-unit CI)

## Performance
- Benchmark with `criterion` (statistical) or a custom bench harness
- Profile with `[profile.profiling]` + `cargo flamegraph` or `pprof`
- Do not claim performance improvements without exact benchmark command and output
- Local storage/throughput targets take precedence over remote-tier optimizations until explicitly promoted
