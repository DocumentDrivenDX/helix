---
title: Cross-Cutting Concerns
weight: 3
aliases:
  - /docs/workflow/concerns
---

Cross-cutting concerns are a core concept in HELIX. They capture technology
choices, quality requirements, and conventions that cut across activities,
runtime work items, and artifacts. They do it declaratively, so agents load the right
context without you repeating yourself.

## The Problem Concerns Solve

In a multi-activity, multi-agent workflow, every agent must honor the same
decisions everywhere:

- "We use Bun, not Node" affects build scripts, test runners, CI, and design docs.
- "OWASP Top 10 compliance" affects every endpoint, every input handler, every
  dependency choice.
- "OpenTelemetry tracing" affects middleware, error paths, and deployment config.

Without a mechanism to declare these once and inject them everywhere, each
agent invocation risks rediscovering (or contradicting) a prior decision.
Concerns are that mechanism.

## How They Work

1. **Declare**: during [Frame](/use/workflow/#the-seven-activities), list active concerns
   in `docs/helix/01-frame/concerns.md`
2. **Filter**: each concern declares which areas it applies to (`all`, `ui`,
   `api`, `data`, `infra`, `cli`)
3. **Inject**: at execution time, HELIX loads area-matched concerns and their
   practices into the agent's context
4. **Attach runtime context**: runtime work context carries concern practices
   into individual work items, making each work item self-contained

## Concern Library

HELIX ships a library of concerns under `workflows/concerns/`. Each concern
consists of two files:

| File | Purpose |
|------|---------|
| `concern.md` | Category, areas, components, constraints, quality gates |
| `practices.md` | Activity-specific practices (requirements, design, implementation, testing) |

### Tech Stack Concerns

| Concern | Key Tools |
|---------|-----------|
| **rust-cargo** | Cargo workspace, clippy, cargo-deny, proptest |
| **typescript-bun** | Bun runtime, Biome, bun:test, strict tsconfig |
| **python-uv** | uv, ruff, pyright, pytest + hypothesis |
| **go-std** | gofmt, go vet, golangci-lint, govulncheck |
| **scala-sbt** | sbt-dynver, scalafmt, scalafix, ScalaTest |
| **react-nextjs** | React 19, Next.js, functional components + hooks |

### Quality and Infrastructure Concerns

| Concern | Focus |
|---------|-------|
| **security-owasp** | OWASP Top 10, dependency auditing, secret management |
| **o11y-otel** | OpenTelemetry tracing, structured logging, metrics |
| **a11y-wcag-aa** | WCAG 2.1 AA, semantic HTML, keyboard navigation |
| **i18n-icu** | ICU message format, locale-aware formatting |
| **testing** | Test philosophy, bug-finding over proof, property-based testing |
| **ux-radix** | Radix UI headless primitives, accessible by default |
| **k8s-kind** | Kubernetes with kind, Helm charts, service discovery |

### Testing Concerns

| Concern | Focus |
|---------|-------|
| **e2e-playwright** | Playwright browser automation, visual regression |
| **e2e-kind** | Kind cluster E2E testing for APIs and infrastructure |

### Tooling Concerns

| Concern | Focus |
|---------|-------|
| **hugo-hextra** | Hugo + Hextra theme, GitHub Pages deployment |
| **demo-asciinema** | Scripted terminal recordings, Docker reproducibility |
| **demo-playwright** | Browser demo recordings with Playwright video capture |

See the [full concerns catalog](/concerns/) for detailed
component listings and all available concerns.

## Drift Detection

Tech-stack concerns declare **drift signals**: patterns that indicate the
project is straying from its declared technology choices. For example, the
`typescript-bun` concern flags `npm run` instead of `bun run`, `eslint`
instead of Biome, and `jest` instead of `bun:test`.

HELIX checks for drift signals during [review and alignment](/use/workflow/#review-and-alignment),
reporting findings that keep the project true to its own decisions.

## Artifact-Impact Contract

Each concern declares an **Artifact Impact** section: the artifacts that must
change when you select that concern. Choosing `security-owasp`, for instance,
obligates the corresponding ADR, technical-design, and test-plan updates.
Selecting a concern without making those changes is drift, and the alignment
reconcile check catches it. This makes a concern bite on both
<!-- vale Helix.Hedges = NO -->
generated and hand-edited artifacts, not just on runtime work context.
<!-- vale Helix.Hedges = YES -->

## The Knowledge Chain

Concerns connect to the rest of the HELIX artifact graph through a knowledge
chain:

```
Spike/POC (gather evidence)
  → ADR (record decision with rationale)
    → Concern (index for context assembly)
      → Runtime work context (injected into work items)
```

<!-- vale Helix.PassiveVoice = NO -->
When a referenced ADR is superseded, [review and alignment](/use/workflow/#review-and-alignment)
<!-- vale Helix.PassiveVoice = YES -->
flags the affected concern for re-evaluation, ensuring that decisions
<!-- vale Helix.Hedges = NO -->
propagate forward rather than silently going stale.
<!-- vale Helix.Hedges = YES -->

## Where HELIX Uses Concerns

Every HELIX action that involves technology or quality choices loads active
concerns:

| Action | How it uses concerns |
|--------|---------------------|
| **build** | Loads practices, runs concern-declared quality gates |
| **review** | Checks for drift signals and practice violations |
| **design** | Concerns constrain architecture decisions |
| **evolve** | Detects technology changes conflicting with concerns |
| **align** | Flags concern drift across all layers |
| **frame** | Concern selection happens during framing |

See the [full concerns reference](/concerns/) for the complete
library catalog and project configuration format.
