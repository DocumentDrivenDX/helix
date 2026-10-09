# Practices: typescript-bun

## Requirements (Frame activity)
- All user stories involving TypeScript must assume Bun as runtime and package manager
- If a library dependency requires a Node.js adapter, flag it as a concern at framing — it may require a Bun-compatible alternative

## Design
- Centralize configuration in one `zod` schema in `env.ts` (e.g. `z.object({ PORT: z.coerce.number().default(3000), DATABASE_URL: z.url() })`); parse `Bun.env` once with `safeParse` and exit with a readable error on failure
- Source precedence: real environment variables > `.env` (dev only) > schema defaults; production relies on real env vars or the platform secret manager
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
  - Environment: `Bun.env` (read only in the env module)
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
