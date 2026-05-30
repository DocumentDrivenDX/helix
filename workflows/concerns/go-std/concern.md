# Concern: Go + Standard Toolchain

## Category
tech-stack

## Areas
all

## Slot
language-runtime

## Components

- **Language**: Go (version pinned in `go.mod`)
- **Build system**: `go build` / `go test` (standard toolchain)
- **Formatter**: `gofmt` (non-negotiable)
- **Linter**: `golangci-lint` with `.golangci.yml` config
- **Security scanner**: `gosec` + `govulncheck`
- **CLI framework**: Cobra (for CLI projects)
- **Testing**: `go test` with build tags for test levels

## Constraints

- All code must pass `gofmt -l .` (zero diff)
- All code must pass `go vet ./...`
- All code must pass `golangci-lint run` with project `.golangci.yml`
- Errors must be wrapped with context: `fmt.Errorf("context: %w", err)` — no naked `return err`
- No `panic` outside of `main()` or initialization — return errors
- Pass `context.Context` as first parameter to functions that do I/O or may be cancelled
- Define interfaces in the consuming package, not the providing package
- Version metadata embedded at build time via `-ldflags "-X main.Version=..."`
- `govulncheck ./...` must pass (no known vulnerabilities)

## Lint Policy (golangci-lint baseline)

Enabled linters:
- `govet` (with `enable-all`, disable `fieldalignment`)
- `staticcheck`
- `ineffassign`
- `misspell`
- `unconvert`
- `gosec` (severity: high, confidence: high)
- `gocritic` (diagnostic, performance, style tags)

Disabled linters (too opinionated):
- `wsl`, `wrapcheck`, `varnamelen`, `nlreturn`, `exhaustruct`
- `paralleltest`, `testpackage`, `mnd`, `funlen`

Generated files (`.pb.go`, `.gen.go`, `mock_*.go`) excluded from linting.

## When to use

All Go projects — CLIs, services, libraries. The standard toolchain and
`go fmt` are universal; golangci-lint + gosec are the quality layer on top.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: Go + standard toolchain (gofmt, golangci-lint, gosec, govulncheck) as the language-runtime
- TD: error-wrapping, context-passing, interface-in-consumer conventions; lint baseline
