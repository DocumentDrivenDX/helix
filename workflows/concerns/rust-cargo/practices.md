# Practices: Rust + Cargo

## Linting & Formatting

- Linter: `cargo clippy -- -D warnings -W clippy::all`
- Formatter: `cargo fmt`
- Run both before every commit

## Testing

- Framework: built-in `#[test]` + `cargo test`
- Integration tests in `tests/` directory
- Use `proptest` or `quickcheck` for property-based testing where applicable
- Fake data: derive test fixtures, avoid static data files

## Error Handling

- Use `thiserror` for library errors, `anyhow` for application errors
- No `.unwrap()` in library code — always propagate with `?`
- Document error conditions in public API docs

## Dependencies

- Prefer crates with `#![forbid(unsafe_code)]` when available
- Check `cargo audit` for known vulnerabilities
- Minimize dependency count — prefer standard library

## Documentation

- All public items must have `///` doc comments
- Include examples in doc comments (`/// # Examples`)
- Run `cargo doc --no-deps` to verify docs build
