# Concern: React + Next.js

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
