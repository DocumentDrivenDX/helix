# Concern: Rust + Cargo

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
- **Configuration**: `figment` (layered sources) deserialized into one `serde` `Config` struct; `secrecy` for secrets — NOT scattered `std::env::var`, NOT `dotenvy` called from library code
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
- All configuration is declared in one central `Config` struct (single module/crate, e.g. `config.rs`) deserialized with `figment`; every field is typed with a default or is required
- The `Config` is built once in the binary's `main` and passed in; no `std::env::var`/`env::vars` reads outside the config module, and no global config singletons in library crates
- Secrets use `secrecy::SecretString` (no `Debug`/`Display` leakage); invalid or missing config fails at startup, not at first use
- Config is layered by owner per `twelve-factor`: ops-injected values (env vars, mounted files, secret manager) over a committed `config/<env>.toml` over committed defaults (`Default` impl plus `config/default.toml`), merged with `figment`; ops-owned keys (hosts, credentials) have no default and never appear in committed files
- Real environment variables take precedence over files; `.env` (via `dotenvy`, dev builds only) is a local convenience, git-ignored, with a committed `.env.example` listing every variable (no secrets in it)
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
- TD: workspace lints, error-handling (thiserror/anyhow), unsafe policy, profile conventions, central `Config` struct and its config-key contract (owner and source per key)
