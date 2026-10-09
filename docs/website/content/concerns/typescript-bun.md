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
- **Configuration**: `zod` schema parsed over merged layers (committed JSON files + `process.env`, which Bun aliases as `Bun.env`) in one `env.ts` — NOT scattered `process.env`/`Bun.env` reads, NOT `dotenv` (Bun loads `.env` natively)
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
- All configuration is declared in one central `zod` schema (single module, e.g. `env.ts`) that parses the merged layers (files + env) once at startup and exports a frozen, typed config object; invalid or missing config fails at startup, not at first use
- `process.env` (or `Bun.env`) is read only inside the env module — use `process.env` so the module also runs under Next.js on Node or Edge, where `Bun.env` is undefined; the config object is built at the entrypoint and passed in
- Secrets are never logged or serialized (wrap in a redacting type or omit from log output)
- Config is layered by owner per `twelve-factor`: ops-injected values (`process.env`, mounted files, secret manager) over a committed `config/<env>.json` over committed defaults (schema `.default()`s plus `config/default.json`), deep-merged then parsed by the one `zod` schema; ops-owned keys (hosts, credentials) are required with no default and never appear in committed files
- Real environment variables take precedence over files; `.env.<env>`/`.env.local` files are not used (Bun loads them natively; set `--env-file` explicitly or none) and plain `.env` is local-development only, git-ignored, with a committed `.env.example` listing every variable (no secrets in it)

## Drift Signals (anti-patterns to reject in review)

- `npm run` in scripts → must be `bun run`
- `prettier` or `eslint` dependencies → replace with Biome
- `vitest` or `jest` → replace with `bun:test`
- `tsx` or `ts-node` → remove; Bun executes TypeScript natively
- `@hono/node-server` or any `*-node-*` HTTP adapter → use `Bun.serve()`
- `node dist/` start command → use `bun src/`
- `engines.node` constraint → remove
- `process.env.X` / `Bun.env.X` outside the env module → read from the typed config object

## When to use

TypeScript projects using Bun as the runtime and package manager. Applies to
monorepos and single-package projects alike. If a project historically drifted
to Node.js tooling (npm, tsx, prettier, vitest), the concern documents the
target state and the drift signals above identify what needs correction.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: TypeScript + Bun (Biome, bun:test) as the language-runtime — not Node/npm/ESLint/Vitest
- TD: strict tsconfig, Bun-native APIs, workspace layout, Biome config, central env schema and its config-key contract (owner and source per key)

## ADR References

## Practices by activity

Agents working in any of these activities inherit the practices below through runtime work context, such as a DDx bead context digest.

## Requirements (Frame activity)
- All user stories involving TypeScript must assume Bun as runtime and package manager
- If a library dependency requires a Node.js adapter, flag it as a concern at framing — it may require a Bun-compatible alternative

## Design
- Centralize configuration in one `zod` schema in `env.ts` (e.g. `z.object({ LOG_LEVEL: z.enum(["info", "debug"]).default("info"), DATABASE_URL: z.string().url() })`); parse `process.env` once (not `Bun.env`, so the module also runs under Next.js on Node or Edge) with `safeParse` and exit with a readable error on failure
- Source precedence: real environment variables / secret files > `.env` (dev only) > `config/<env>.json` > `config/default.json` > schema defaults (plain deep-merge of the objects, then `safeParse`; use flat `UPPER_SNAKE` keys in the JSON files so env vars map one-to-one); ops-owned keys are required, dev-owned keys carry defaults; production relies on real env vars or the platform secret manager
- Commit `.env.example`; git-ignore `.env`
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
  - Environment: `process.env`/`Bun.env` (read only in the env module)
- TypeScript config: `strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `verbatimModuleSyntax`
- No `any` — TypeScript strict mode is enforced
- Formatting: Biome with tabs, line width 100
- Linting: Biome recommended rules + `noUnusedImports: error`, `noUnusedVariables: warn`
- Imports: use `type` keyword for type-only imports (`import type { Foo }`)

## Testing
- Framework: `bun:test` (built-in)
- Config in tests: parse an explicit object through the env schema; never depend on a developer's `.env`
- Run: `bun test`
- Use `mock()` from `bun:test` for module mocking
- Fake data: `@faker-js/faker` or equivalent — not static fixtures
- Prefer stubs to mocks; verify behavior, not call sequences
- Integration tests can use real databases via `docker compose up -d` or testcontainers

## Quality Gates (pre-commit / CI)
- `bun test` — all tests pass
- `bun run typecheck` — `tsc --noEmit` passes for all packages
- `bun run lint` — Biome lint + format check passes
- No `process.env`/`Bun.env` outside the env module (Biome `noProcessEnv` covers `process.env`; add a grep gate for `Bun.env`, which the rule does not cover; the env module opts out with `biome-ignore`)
- Biome `noExcessiveCognitiveComplexity` and the file-size cap are set per `code-shape-ceilings`; no ceiling is raised and no `biome-ignore` is added for them
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
