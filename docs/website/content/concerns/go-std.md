---
title: "Go + Standard Toolchain"
slug: go-std
generated: true
aliases:
  - /reference/glossary/concerns/go-std
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

## Practices by activity

Agents working in any of these activities inherit the practices below via the bead's context digest.

## Requirements (Frame activity)
- Specify minimum Go version in `go.mod`
- Identify test levels needed: unit, integration (VCR/stubbed), functional (binary), E2E (live)
- If the project hits external HTTP APIs, plan for VCR recording in integration tests

## Design
- Package layout: `cmd/` for CLI entry points, `internal/` for application logic
- Define interfaces in the consumer package; return concrete types where practical
- Use minimal, consumer-driven interfaces
- Guard shared state explicitly; prefer immutable data; use `errgroup` for concurrent work
- Embed version metadata: `Version`, `BuildTime`, `GitCommit` via `-ldflags`

## Implementation
- Formatting: `go fmt ./...` (run before every commit — enforced by `gofmt -l .` check)
- Error wrapping: `fmt.Errorf("context: %w", err)` — always add context
- Sentinel errors: define with `errors.New` for expected conditions; compare with `errors.Is`
- Concurrency: pass `context.Context` first; use `errgroup.WithContext` for fan-out; avoid goroutine leaks
- Logging: structured with `log/slog` (stdlib) or project-chosen structured logger; no `fmt.Print*` in library code
- No `panic` outside startup; in `main()`, convert panics to fatal log + exit

## Testing
- Run with: `go test ./...`
- Race detection: `go test -race ./...` for concurrent code
- Build tags for test levels:
  - (no tag): fast unit tests, no external deps
  - `-tags=integration`: VCR playback, no live APIs
  - `-tags=functional`: built binary CLI tests
  - `-tags=e2e`: live API tests (requires credentials)
- Table-driven tests for pure functions
- HTTP stubs: VCR cassette recording (`VCR_MODE=record` to capture, `VCR_MODE=playback` for CI)
- Use `testify/assert` or `testify/require` for assertions; not bare `t.Fatal` comparisons
- Coverage: `go test -coverprofile=coverage.out ./...` + `go tool cover -func`; 80% threshold

## Quality Gates (pre-commit / CI)
- `go fmt ./...` (or `gofmt -l .` check)
- `go vet ./...`
- `golangci-lint run`
- `gosec ./...` (high severity/confidence)
- `govulncheck ./...`
- `go test -race ./...` (unit + integration tags)

## Dependency Management
- `go mod tidy` after any dependency change
- `go mod download` for reproducible builds
- No vendoring unless required by deployment constraints
- `govulncheck ./...` before releases
