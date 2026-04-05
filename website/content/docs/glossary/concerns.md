---
title: Concerns
weight: 4
prev: /docs/glossary/actions
next: /docs/glossary/concepts
---

# Concerns

Concerns are composable cross-cutting declarations from a shared library. They encode technology choices, quality requirements, and conventions that apply across multiple beads and phases.

## How Concerns Work

1. **Select** — During [Frame](/docs/glossary/phases#phase-1-frame), declare active concerns in `docs/helix/01-frame/concerns.md`
2. **Filter** — Each concern declares which areas it applies to (`all`, `ui`, `api`, `data`, `infra`, `cli`)
3. **Inject** — At execution time, area-matched concerns and their practices are loaded into context
4. **Digest** — [Context digests](/docs/glossary/concepts#context-digest) carry concern practices into beads, making them self-contained

## Project Concerns File

Every HELIX project declares its concerns in `docs/helix/01-frame/concerns.md`:

```markdown
# Project Concerns

## Active Concerns
- rust-cargo (tech-stack)
- security-owasp (security)

## Area Labels
| Label | Applies to |
|-------|-----------|
| all   | Every bead |
| api   | Server, endpoints |
| cli   | CLI tool |

## Project Overrides
### rust-cargo
- **MSRV**: 1.75 (lower than library default)
```

Project overrides take full precedence over library defaults.

## Concern Library

The library lives at `workflows/concerns/`. Each concern has two files:

- `concern.md` — Category, areas, components, constraints, quality gates
- `practices.md` — Phase-specific practices (requirements, design, implementation, testing)

### Tech Stack Concerns

| Concern | Category | Key Tools |
|---------|----------|-----------|
| **rust-cargo** | tech-stack | Cargo workspace, clippy (pedantic+nursery), cargo-deny, cargo-machete, thiserror/anyhow, proptest |
| **typescript-bun** | tech-stack | Bun runtime (NOT Node), Biome (NOT ESLint/Prettier), bun:test (NOT Vitest/Jest), strict tsconfig |
| **python-uv** | tech-stack | uv package manager, ruff linter/formatter, pyright type checker, hatchling builds, pytest + hypothesis |
| **go-std** | tech-stack | gofmt, go vet, golangci-lint, govulncheck, error wrapping with context, build tags for test levels |
| **scala-sbt** | tech-stack | sbt-dynver, scalafmt, scalafix, ScalaTest, multi-project builds |

### Quality Concerns

| Concern | Category | Focus |
|---------|----------|-------|
| **security-owasp** | security | OWASP Top 10, per-language dependency auditing, secret management, TLS, input validation, parameterized queries |
| **o11y-otel** | observability | OpenTelemetry tracing, structured logging, metrics, dashboards |
| **a11y-wcag-aa** | accessibility | WCAG 2.1 AA compliance, semantic HTML, keyboard navigation, screen reader support |
| **i18n-icu** | internationalization | ICU message format, locale-aware formatting, translation workflow |

### Infrastructure Concerns

| Concern | Category | Focus |
|---------|----------|-------|
| **k8s-kind** | infrastructure | Kubernetes with kind for local dev, Helm charts, service discovery, image tagging |

### Tooling Concerns

| Concern | Category | Focus |
|---------|----------|-------|
| **hugo-hextra** | microsite | Hugo + Hextra theme, content structure, Playwright e2e, GitHub Pages deployment |
| **demo-asciinema** | demo | Scripted terminal recordings, Docker reproducibility, narrative structure, microsite embedding |

## Drift Signals

Tech-stack concerns can declare **drift signals** — patterns that indicate the project is straying from its declared technology choices. For example, the `typescript-bun` concern flags:

- `npm run` instead of `bun run`
- `prettier` or `eslint` instead of Biome
- `vitest` or `jest` instead of `bun:test`
- `@hono/node-server` instead of `Bun.serve()`
- `engines.node` in package.json

[Review](/docs/glossary/actions#review) and [align](/docs/glossary/actions#align) check for drift signals and report them as findings.

## Concerns in the Knowledge Chain

Concerns connect to other HELIX artifacts in a knowledge chain:

```
Spike/POC (gather evidence)
  → ADR (record decision with rationale)
    → Concern (index for context assembly)
      → Context Digest (injected into beads)
```

When a referenced ADR is superseded, [polish](/docs/glossary/actions#polish) flags the affected concern for re-evaluation.

## Where Concerns Are Used

Every HELIX action that involves technology or quality choices loads active concerns:

| Action | How it uses concerns |
|--------|---------------------|
| **build** | Loads practices, runs concern-declared quality gates |
| **review** | Checks for drift signals and practice violations |
| **design** | Concerns constrain architecture decisions |
| **evolve** | Detects technology changes conflicting with concerns |
| **align** | Flags concern drift across all layers (docs, designs, code) |
| **polish** | Enforces area labels, refreshes context digests, fixes tool references |
| **frame** | Concern selection happens during framing |
| **check** | Detects missing area labels, stale digests, missing concerns.md |
| **backfill** | Discovers concerns from project evidence |
