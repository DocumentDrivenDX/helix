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
- **Configuration**: `caarlos0/env` (struct tags) for env-only services, or `koanf` for layered sources — one central `Config` struct; NOT scattered `os.Getenv`, NOT `viper` global state
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
- All configuration is declared in one central `Config` struct (single package, e.g. `internal/config`) with typed fields, defaults, and required markers
- `Config` is loaded and validated once in `main` and passed in explicitly; no `os.Getenv`/`os.LookupEnv` outside the config package, and no package-level config globals
- Secrets use a redacting type (`String()`/`MarshalText` returns a mask) so they cannot leak through logs; invalid or missing config fails at startup, not at first use
- Real environment variables take precedence; `.env` (via `godotenv`, dev only) is a local convenience, git-ignored, with a committed `.env.example` listing every variable (no secrets in it)

## Lint Policy (golangci-lint baseline)

Enabled linters:
- `govet` (with `enable-all`, disable `fieldalignment`)
- `staticcheck`
- `ineffassign`
- `misspell`
- `unconvert`
- `gosec` (severity: high, confidence: high)
- `gocritic` (diagnostic, performance, style tags)
- `forbidigo` (ban `os.Getenv`/`os.LookupEnv`, excluded for the config package)

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
- TD: error-wrapping, context-passing, interface-in-consumer conventions; lint baseline, central `Config` struct and its env-var contract
