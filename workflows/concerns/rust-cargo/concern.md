# Concern: Rust + Cargo

## Category
tech-stack

## Areas
all

## Components

- **Language**: Rust (latest stable)
- **Build system**: Cargo
- **Edition**: 2024

## Constraints

- All code must pass `cargo clippy -- -D warnings`
- All code must pass `cargo fmt --check`
- No `unsafe` without documented justification and `// SAFETY:` comments

## When to use

Performance-critical systems, CLI tools, infrastructure software, and
projects where memory safety and zero-cost abstractions matter.

## ADR References
