---
title: "React + Next.js"
slug: react-nextjs
generated: true
aliases:
  - /reference/glossary/concerns/react-nextjs
---

**Category:** Tech Stack · **Areas:** web, ui

## Description

## Category
tech-stack

## Areas
web, ui

## Slot
frontend-framework

## Components

- **UI Framework**: React 19 — functional components and hooks only
- **Meta-framework**: Next.js 15 — App Router (not Pages Router)
- **UI primitives / component library**: see `ux-radix` concern (canonical
  owner of the Radix + shadcn/ui prescription) — this concern does NOT
  prescribe a component library directly
- **Styling**: Tailwind CSS 4 — utility-first, no CSS-in-JS
- **Forms**: react-hook-form + @hookform/resolvers with Zod schemas
- **Data tables**: TanStack React Table 8 — headless, sortable, filterable, virtualizable
- **Validation**: Zod — shared schemas between frontend and backend
- **E2E testing**: Playwright

## Constraints

- Use App Router (`app/` directory) — not Pages Router (`pages/`)
- Prefer React Server Components for data-heavy pages; use `"use client"` only where interactivity is required
- No class components — functional components with hooks only
- No `React.FC` type annotation — use plain function signatures with typed props
- Forms must use react-hook-form with uncontrolled components — no `useState` per field
- Validation schemas live in the shared package and are reused on frontend and backend
- UI primitives and component-library choice are governed by the `ux-radix`
  concern (canonical owner of shadcn/ui + Radix); compose `ux-radix` when this
  concern is selected for UI work
- Tailwind config extends the design system tokens (colors, spacing, typography)
- E2E tests use Playwright, not Cypress or Selenium

## Drift Signals (anti-patterns to reject in review)

- `pages/` directory for routing → must use `app/` (App Router)
- `class extends React.Component` → must use functional components
- `React.FC` or `React.FunctionComponent` → use plain typed functions
- `useState` for every form field → must use react-hook-form
- `styled-components`, `emotion`, or `css-modules` → use Tailwind utility classes
- Re-prescribing shadcn/ui or Radix primitives here → defer to `ux-radix`
  (canonical owner); this concern only references that prescription
- `cypress` or `selenium` → use Playwright
- `getServerSideProps` or `getStaticProps` → use Server Components or route handlers
- Inline `fetch` in components without error/loading states → use data fetching pattern with Suspense boundaries

## When to use

React + Next.js frontend applications. Compose with `typescript-bun` for the
base TypeScript and Bun runtime concern, and compose with `ux-radix` for UI
primitives and component-library prescription (shadcn/ui + Radix). This
concern adds React-specific framework patterns (App Router, Server Components,
forms, data tables) and E2E testing requirements; it does NOT prescribe a
component library.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: React 19 + Next.js App Router as the frontend-framework slot; Tailwind for styling (component-library prescription is owned by `ux-radix`)
- TD: App Router + Server Components, react-hook-form + Zod, shared validation schemas
- DESIGN_SYSTEM: Tailwind config extends design-system tokens (component-library conventions live with `ux-radix`)
- TEST_PLAN: Playwright E2E (not Cypress/Selenium)

## ADR References

- ADR-010: Frontend validation architecture (Zod shared schemas)
- ADR-011: ux-radix owns the Radix and shadcn component-library prescription;
  this concern references rather than re-prescribing

## Practices by activity

Agents working in any of these activities inherit the practices below through runtime work context, such as a DDx bead context digest.

## Requirements (Frame activity)
- User stories involving UI must specify which pages or components are affected
- Acceptance criteria for UI features must include Playwright E2E coverage
- Data-heavy views (tables, dashboards) must specify expected row counts for virtualization decisions

## Design
- Use Next.js App Router: layouts in `app/layout.tsx`, pages in `app/page.tsx`, route groups with `(groupName)/`
- Default to React Server Components — add `"use client"` only for interactive components (forms, modals, dropdowns, client state)
- Component hierarchy: page (server) → layout (server) → interactive widget (client)
- UI primitives and component library: see the `ux-radix` concern — it is the
  canonical owner of the shadcn/ui + Radix prescription (copy-not-install,
  customization, primitive selection). Compose `ux-radix` when this concern
  is selected for UI work.
- Design tokens (colors, spacing, typography) in `tailwind.config.ts` — components reference tokens, not raw values
- Forms: one Zod schema per entity in `@apogee/shared`, resolved via `@hookform/resolvers/zod`
- Data tables: TanStack React Table with column definitions typed against shared schemas
- State management: server state via TanStack Query (when added), client state via Zustand (when added), form state via react-hook-form — no Redux

## Implementation
- Component files: `ComponentName.tsx` in PascalCase
- Props: define inline or as `type Props = { ... }` — no `interface` for props, no `React.FC`
- Hooks: `use` prefix, one file per hook in `hooks/` directory
- Server Components: default export async functions, fetch data directly
- Client Components: `"use client"` directive at top of file, minimize scope
- Tailwind classes: use a `cn()` utility for conditional classes — no
  `classnames` or `clsx` used separately
- Forms pattern:
  ```tsx
  const form = useForm<SchemaType>({ resolver: zodResolver(schema) });
  ```
- Error boundaries: wrap route segments with `error.tsx` files
- Loading states: use `loading.tsx` files or Suspense boundaries
- Images: use `next/image` with explicit width/height — no unoptimized `<img>` tags
- Links: use `next/link` — no `<a>` tags for internal navigation

## Testing
- Unit tests: `bun:test` for component logic, hooks, and utilities
- E2E tests: Playwright in `tests/e2e/` directory
- Playwright config: headless Chromium, 30s timeout, screenshots on failure
- Test naming: `feature-name.spec.ts`
- Use page object pattern for complex flows
- Run E2E: `bun run test:e2e` (headless) or `bun run test:e2e:headed` (visible browser)
- Do not mock API responses in E2E — test against real backend with seeded data

## Quality Gates (pre-commit / CI)
- `bun run typecheck` — tsc passes for web package (includes JSX type checking)
- `bun run lint` — Biome passes (includes JSX/TSX rules)
- `bun test` — unit tests pass
- `bun run test:e2e` — Playwright E2E tests pass (CI only, requires running backend)
- No `any` in component props or hook return types
- No inline styles — use Tailwind classes

## Composed-Concern Friction with typescript-bun (known)
- **`next build`/`next start` run under Node, not Bun.** Even when launched with
  `bun run`, Next.js hands execution to Node. Any Bun-native import in a path
  Next.js builds or runs — most commonly `import { Database } from "bun:sqlite"`
  for a colocated data layer — fails to resolve at build time.
- **Fix: run Next.js under `bun --bun`.** Use `bun --bun run next build` /
  `bun --bun run dev` so `bun:*` built-ins resolve in the Next.js process.
  Wire this into the package scripts (e.g. `"dev": "bun --bun next dev"`) so it
  is not forgotten on CI.
- **Alternative**: keep `bun:sqlite` (and other `bun:*` built-ins) out of the
  Next.js runtime — put the data layer in a separate Bun service the Next.js app
  calls over an API, leaving the frontend free to build under plain Node.
- Record the chosen resolution as a project override in
  `docs/helix/01-frame/concerns.md` when both `react-nextjs` and `typescript-bun`
  are active. See the `typescript-bun` practices "Composed-Concern Friction"
  section for the runtime-side detail.

## Accessibility
- All interactive elements must have accessible labels (aria-label, aria-labelledby, or visible text)
- Accessible UI-primitive behavior (keyboard, focus, screen reader) is
  governed by the `ux-radix` concern — do not override Radix/shadcn handlers
  in ways that break the WAI-ARIA contract
- Color contrast must meet WCAG AA (4.5:1 for normal text, 3:1 for large text)
- Forms must associate labels with inputs and display validation errors accessibly
