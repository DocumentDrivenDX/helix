# Practices: react-vite

## Requirements (Frame activity)

- Confirm no page needs server rendering for SEO or first-paint data; if one does, the slot filler is `react-nextjs`, not this concern.
- Name the backend that serves the build and confirm it can serve a static directory with an `index.html` fallback on the same origin as its `/api/*` routes.
- Set `build.outDir` to the backend's static directory with `emptyOutDir: true`; the backend owns serving it.
- Configure `server.proxy` to forward `/api` to the backend's local port; all API calls use relative `/api/...` URLs.
- State the initial-load JavaScript budget if the HELIX default (250 KB gzipped) does not fit the product.
- User stories involving UI must specify which routes or components are affected.
- Acceptance criteria for UI features must include browser e2e coverage per `e2e-playwright`.

## Design

- Keep the SPA in a `frontend/` directory with `vite.config.ts`, `tsconfig.json`, `index.html`, and `src/`; its `package.json` sits where the host's build installs from (`frontend/`, or the repo root).
- Define routes with React Router's `createBrowserRouter` as a client-side library; lazy-load each route module.
- Fetch server state with TanStack Query; keep client-only UI state in components (patterns per `frontend-architecture`).
- Validate forms with react-hook-form and Zod; mirror, never replace, the backend's validation.
- Reference design tokens through Tailwind 4 theme variables; UI primitives and component library come from `ux-radix` (and `databricks-appkit-ui` when selected).
- Expose to the client only `VITE_`-prefixed variables that are safe to publish; serve runtime configuration from an `/api/*` route.

## Implementation

- Write function components with typed props (`type Props = { ... }`); no class components, no `React.FC`.
- Component files are `ComponentName.tsx` in PascalCase; hooks use the `use` prefix, one per file in `hooks/`.
- Read client configuration only from `import.meta.env.VITE_*`; never reference `process.env` in client code.
- Wrap each lazy route in a Suspense boundary and an error boundary, so every route renders loading and error states.
- Keep `tsconfig.json` at `strict: true` with `noUncheckedIndexedAccess: true`; no `any` in props or hook return types.
- Commit the package manager's lockfile; never commit the build output.
- Use a `cn()` helper for conditional Tailwind classes; no inline styles.

## Testing / Verification

- Component and hook tests use Vitest + Testing Library in jsdom (`bun:test` under `typescript-bun`), querying by role, label, and text.
- Mock the network at the fetch boundary with MSW; do not mock TanStack Query or the router.
- Test each route's loading, empty, error, and success states.
- Verify a production build served by the real backend: a deep link to a client route loads the SPA, and `/api/*` reaches the backend.
- Browser e2e of core flows runs per `e2e-playwright` against the running backend, not the Vite dev server alone.

## Quality Gates

- `tsc --noEmit` passes for the frontend.
- The lint gate passes (Biome under `typescript-bun`, otherwise ESLint with the React hooks rules).
- The ESLint config sets the complexity, function-length, parameter, and depth ceilings and a file-size cap per `code-shape-ceilings`; no ceiling is raised and no `eslint-disable` is added for them.
- The component test suite passes (`vitest run`, or `bun test` under `typescript-bun`).
- `vite build` succeeds and the initial-load JavaScript stays within the TD budget.
- No `VITE_` variable holds a secret, and no client code references `process.env`.
- No absolute API host in client code; all API calls are relative `/api/...`.
