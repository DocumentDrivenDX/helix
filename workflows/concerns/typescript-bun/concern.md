# Concern: TypeScript + Bun

## Category
tech-stack

## Areas
all

## Components

- **Language**: TypeScript (strict mode)
- **Runtime**: Bun 1.x
- **Package manager**: Bun (not npm, not yarn)

## Constraints

- All code must pass `tsc --noEmit` with strict config
- Use Bun-native APIs where available (Bun.serve, Bun.file, Bun.spawn)
- No Node.js compatibility shims unless unavoidable
- Prefer Bun's built-in tooling over third-party equivalents

## When to use

Projects that need fast startup, built-in test runner, and TypeScript-first
tooling. Good for APIs, CLI tools, and web services where Bun's runtime
performance and built-in bundler are advantages.

## ADR References
