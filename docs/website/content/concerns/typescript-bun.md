---
title: "TypeScript + Bun"
slug: typescript-bun
generated: true
aliases:
  - /reference/glossary/concerns/typescript-bun
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

- **Language**: TypeScript (strict mode)
- **Runtime**: Bun 1.x — NOT Node.js
- **Package manager**: Bun (`bun install`, `bun add`) — NOT npm, NOT yarn, NOT pnpm
- **Linter + Formatter**: Biome — NOT ESLint, NOT Prettier
- **Test runner**: `bun:test` — NOT Vitest, NOT Jest
- **Workspace layout**: Bun workspaces (`workspaces` in root `package.json`)
- **TypeScript config**: strict, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`

## Constraints

- All code must pass `tsc --noEmit` (or `bun run typecheck`) with strict config
- All code must pass Biome lint + format check (`bun run lint`)
- Scripts use `bun run`, not `npm run`
- Use Bun-native APIs: `Bun.serve()` for HTTP (not `@hono/node-server` or similar Node adapters), `Bun.file()` for file I/O, `Bun.spawn()` for subprocesses
- Do not use `tsx`, `ts-node`, or other TypeScript transpilers — Bun runs `.ts` natively
- Do not add an `engines.node` field — this project targets Bun, not Node.js
- No `package-lock.json` or `yarn.lock` — use `bun.lock`
- No `node dist/index.js` start commands — use `bun src/index.ts`
- Biome config: indent style tabs, line width 100, `noUnusedImports: error`

## Drift Signals (anti-patterns to reject in review)

- `npm run` in scripts → must be `bun run`
- `prettier` or `eslint` dependencies → replace with Biome
- `vitest` or `jest` → replace with `bun:test`
- `tsx` or `ts-node` → remove; Bun executes TypeScript natively
- `@hono/node-server` or any `*-node-*` HTTP adapter → use `Bun.serve()`
- `node dist/` start command → use `bun src/`
- `engines.node` constraint → remove

## When to use

TypeScript projects using Bun as the runtime and package manager. Applies to
monorepos and single-package projects alike. If a project historically drifted
to Node.js tooling (npm, tsx, prettier, vitest), the concern documents the
target state and the drift signals above identify what needs correction.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: TypeScript + Bun (Biome, bun:test) as the language-runtime — not Node/npm/ESLint/Vitest
- TD: strict tsconfig, Bun-native APIs, workspace layout, Biome config

## ADR References

## Practices by activity

Agents working in any of these activities inherit the practices below through runtime work context, such as a DDx bead context digest.

## Requirements (Frame activity)
- All user stories involving TypeScript must assume Bun as runtime and package manager
- If a library dependency requires a Node.js adapter, flag it as a concern at framing — it may require a Bun-compatible alternative

## Design
- Use Bun workspaces for monorepos: `"workspaces": ["packages/*"]` in root `package.json`
- Separate packages by concern: `shared` (types/schemas), `server` (API), `web` (frontend)
- Use workspace references (`workspace:*`) for cross-package dependencies
- HTTP servers: `Bun.serve()` — not Express, Fastify with Node adapter, or `@hono/node-server`
- For Hono: use `hono` directly with `Bun.serve()` export, not the node-server adapter

## Implementation
- Run TypeScript directly: `bun src/index.ts` — no build step required for server/CLI
- Scripts in `package.json` must use `bun run` / `bun test` / `bun add`, not `npm run`
- Use Bun-native APIs:
  - File I/O: `Bun.file()`, `Bun.write()`
  - Subprocesses: `Bun.spawn()`, `Bun.spawnSync()`
  - HTTP: `Bun.serve()`
  - Environment: `Bun.env`
- TypeScript config: `strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `verbatimModuleSyntax`
- No `any` — TypeScript strict mode is enforced
- Formatting: Biome with tabs, line width 100
- Linting: Biome recommended rules + `noUnusedImports: error`, `noUnusedVariables: warn`
- Imports: use `type` keyword for type-only imports (`import type { Foo }`)

## Testing
- Framework: `bun:test` (built-in)
- Run: `bun test`
- Use `mock()` from `bun:test` for module mocking
- Fake data: `@faker-js/faker` or equivalent — not static fixtures
- Prefer stubs to mocks; verify behavior, not call sequences
- Integration tests can use real databases via `docker compose up -d` or testcontainers

## Quality Gates (pre-commit / CI)
- `bun test` — all tests pass
- `bun run typecheck` — `tsc --noEmit` passes for all packages
- `bun run lint` — Biome lint + format check passes
- No `package-lock.json` committed (indicates npm was used)
- `bun.lock` committed and up to date

## Dependency Management
- Add: `bun add <pkg>` (not `npm install`)
- Dev deps: `bun add -d <pkg>`
- Workspace deps: reference with `"workspace:*"` in package.json
- Lock file: `bun.lock` (text format, committed)
- Audit: `bun audit` for known vulnerabilities

## Composed-Concern Friction (known)
- **Bun-native APIs require the Bun runtime at execution, not just at install.**
  Modules like `bun:sqlite`, `Bun.serve()`, and `Bun.file()` resolve only when
  the process is the Bun runtime. A tool that shells out to Node — notably
  `next build`/`next start` from the `react-nextjs` concern — fails to resolve
  `import { Database } from "bun:sqlite"` because the Next.js build/runtime is
  Node, not Bun.
- **Fix: force the Bun runtime with `bun --bun`.** Run Next.js (and any tool
  that would otherwise spawn Node) under `bun --bun run <script>` so `bun:*`
  built-ins resolve. Without `--bun`, `bun run next build` still hands execution
  to Node and the import fails.
- **Alternative**: keep `bun:sqlite` out of the Next.js build/runtime path —
  isolate it in a separate Bun-runtime service/process and reach it over an
  interface the Next.js layer can call. Choose `--bun` for a single-process app;
  choose isolation when the frontend must build/run under plain Node.
- When both `typescript-bun` and `react-nextjs` are active, declare which
  resolution the project uses as a **project override** in `concerns.md` so the
  choice is explicit rather than rediscovered at build time.
