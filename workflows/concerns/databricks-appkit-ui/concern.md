# Concern: Databricks AppKit UI (React component layer)

## Category
tech-stack

## Areas
ui

## Platform

**Platform-specific (Databricks).** `@databricks/appkit-ui` is the React
component library Databricks publishes for Databricks Apps, alongside the
`@databricks/appkit` Node/Express server SDK. This concern covers the component
library used **standalone**: inside a `frontend-framework` filler (typically
`react-vite`) with a non-Node backend such as Python on `databricks-apps`. It
does **not** cover `@databricks/appkit`. Facts below are as of 2026-10-01.

## Boundary

This concern owns **the choice and use of `@databricks/appkit-ui` as the
product's React component layer**: the package (and the exclusion of the Node
SDK), version pinning, what the library brings and which parts a standalone
app uses, the token and theme posture, and the open question of standalone
support. It must not duplicate its neighbors:

- **`ux-radix`** owns the interaction patterns, keyboard contracts, and focus
  rules, and the shadcn/ui + Radix component-library prescription (ADR-011).
  AppKit UI is Databricks' distribution of that same shadcn/Radix pattern, so
  every `ux-radix` interaction rule applies to its components unchanged. Where
  `ux-radix` says shadcn is copied into `components/ui/` rather than installed,
  this concern makes AppKit UI the installed library and copies shadcn only for
  components AppKit UI lacks; record that resolution as a project override (see
  Conflict Detection in `workflows/references/concern-resolution.md`).
- **`frontend-framework`** (`react-vite`) owns the build, routing, environment
  exposure, and component tests; **`frontend-architecture`** owns the
  server-state pattern that feeds AppKit UI's data components.
- **`databricks-apps`** owns hosting, identity, and the backend's `/api/*`
  routes. This concern never assumes AppKit server routes exist.
- **`a11y-wcag-aa`** owns accessibility compliance; AppKit UI's Radix base is a
  starting point, not evidence of compliance.
- **`@databricks/appkit`** (the Node/Express SDK with plugins, `/api/<plugin>`
  routes, and `/health`) is out of scope. A project that adopts it is choosing a
  different backend and records that in an ADR.

## Components

- **Package**: `@databricks/appkit-ui`, version 0.82.0 as of 2026-10-01; 0.x and
  fast-moving. Peer dependency: React 18 or 19.
- **UI primitives**: shadcn/Radix-based components.
- **Styling**: Tailwind CSS 4; `@databricks/appkit-ui/styles.css` defines OKLCH
  CSS variables (`--background`, `--primary`, `--destructive`, `--success`,
  `--warning`, `--chart-1` to `--chart-5`, `--sidebar-*`, `--radius`) for light
  and dark themes.
- **Data components**: ECharts-based data components with two modes: **data
  mode** (the app passes data in) and **query mode** (bound to AppKit server
  queries).
- **Hooks**: query and stream hooks; whether they work without the AppKit server
  is part of the standalone spike.
- **Not included**: `@databricks/appkit`, its plugins, and its generated types.

## Constraints

### The component layer only, never the Node SDK
- `package.json` lists `@databricks/appkit-ui` and does not list
  `@databricks/appkit`. Nothing in the frontend imports from `@databricks/appkit`.

### Pin exactly; upgrade as a reviewed change
- The version is exact (`"0.82.0"`, no `^` or `~`) and the lockfile is committed,
  because a 0.x minor release may break the API.
- An upgrade is its own change: read the release notes, run the component tests,
  and check affected screens in both themes before merging.

### Data mode, fed by the project's API
- Charts and data components run in data mode, receiving data from the
  frontend's server-state layer, which calls the project's own `/api/*` routes.
- Query-mode components are not used, because query mode is bound to AppKit
  server queries. The query/stream hooks are not used unless the standalone
  spike shows a hook works against the project's API.

### Tokens and themes
- Import `@databricks/appkit-ui/styles.css` once at the app root. Brand or
  product changes override the CSS variables, never component internals.
- Every token override is made for **both** light and dark themes; components and
  charts reference tokens (`--chart-1` to `--chart-5` for series), never raw
  color values.
- DESIGN_SYSTEM records the token overrides and the theme switch mechanism.

### One component library
- AppKit UI is the component library. A component it lacks is a shadcn component
  copied and themed with AppKit tokens; never a second library (MUI, Chakra,
  Mantine, Ant Design) and never a parallel token set.

### Standalone use is undocumented
- Databricks documents AppKit UI together with the AppKit server; standalone use
  with a non-Node backend is plausible (data mode exists; the peer dependencies
  are only React) but neither documented nor endorsed as of 2026-10-01.
- Selecting this concern requires the **AppKit UI standalone spike** before the
  design commits: build a `react-vite` app with AppKit UI and no AppKit server;
  record the bundle size, the Tailwind 4 integration steps, which components or
  hooks call `/api/<plugin>` or `/health`, and whether theme switching works.

## Drift Signals (anti-patterns to reject in review)

- `import ... from "@databricks/appkit"` or the package in `package.json` →
  `@databricks/appkit-ui` only; the backend is the project's own
- `"@databricks/appkit-ui": "^0.82.0"` or `~` → an exact version
- An upgrade bundled into a feature change → a separate reviewed change
- A query-mode component or AppKit hook calling `/api/<plugin>/...` the backend
  does not serve → data mode fed by the project's `/api/*`
- A second component library alongside AppKit UI → AppKit UI, plus copied shadcn
  for gaps
- A copied shadcn component duplicating one AppKit UI ships → use AppKit UI's
- Hex, `rgb()`, or literal `oklch()` colors in components or chart options → CSS
  variables from `styles.css`
- A token overridden for light only → override light and dark together
- Custom keyboard or focus handlers on AppKit UI components → keep the Radix
  behavior, per `ux-radix`
- Standalone support treated as settled with no spike result → run and record
  the spike

## When to use

A Databricks-hosted app (`databricks-apps` selected) with a React frontend
(`react-vite`) and a non-Node backend, where the UI should look native to
Databricks and needs data components and charts. **Selection signal:** a React
SPA on Databricks Apps whose backend is Python or another non-Node runtime.

Do **not** select it for apps hosted off Databricks, for AppKit TypeScript
projects scaffolded with `databricks apps init` (Databricks' own template
governs the package and server there), or for Streamlit, Dash, or Gradio apps.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: `@databricks/appkit-ui` (exact pin, no Node SDK) as the component library, citing the standalone spike result
- TD: data-mode components fed by the project's `/api/*` through the server-state layer; no AppKit server routes assumed
- IMPLEMENTATION_PLAN: the AppKit UI standalone spike before UI build-out; exact pin and upgrade procedure
- DESIGN_SYSTEM: AppKit OKLCH tokens, overrides for light and dark, chart series tokens, shadcn gap components themed with AppKit tokens
- TEST_PLAN: affected screens checked in both themes; keyboard and focus behavior per `ux-radix`

## ADR References

- ADR-011: ux-radix owns the Radix and shadcn component-library prescription;
  this concern names AppKit UI as the installed distribution of that pattern
  and records the copy-vs-install resolution as a project override
