# Concern: Frontend Architecture

## Category
architecture

> **Why `architecture`, not `ui`.** This concern owns *structural decisions
> within a frontend* — where state lives, who owns the cache, how the page is
> rendered, how data flows through the component tree — the same kind of
> layering/dependency-direction decision an `architecture-style` concern makes
> for a backend, just for the client. `ux-radix` and `a11y-wcag-aa` are the
> `ui` quality-attribute concerns (what the interface looks/behaves like for a
> user); this concern is the *internal architecture* that produces those
> surfaces. Its work items, however, are UI work, so `## Areas` is `ui` — the
> category (what kind of decision) and the area (where the work lands) differ
> on purpose.

## Areas
ui, frontend

## Boundary

This concern owns **the structural decisions WITHIN a frontend application** —
the state/data-fetching/rendering *patterns* a frontend uses, independent of
which framework, component library, or wire contract it sits on. It owns four
load-bearing decisions:

1. **Server-state vs client-state separation** — which state is a *cache of
   remote data* (owned by a data-fetching/cache layer — TanStack Query / SWR,
   or React Server Components fetching on the server) versus which is
   *client-only UI state* (owned by component state, a reducer, or a client
   store like Zustand/Redux). These are different problems and do not share an
   owner.
2. **Rendering strategy** — per-route/per-segment choice of CSR / SSR / SSG /
   ISR / React Server Components (and Partial Prerendering / streaming), driven
   by freshness, personalization, SEO, and interactivity signals.
3. **Component composition + state colocation** — where state lives in the
   tree (colocated as low as possible, lifted only to the lowest common
   ancestor), and composition used to avoid prop drilling before reaching for
   context.
4. **Forms + the mandatory async UI states** — client/server validation split
   and the loading / empty / error / success states every async view must
   render.

Three neighbors must stay distinct — this concern does **not** restate any of
their rules:

- **`react-nextjs`** (the `frontend-framework` **slot**) owns *which framework
  fills the frontend position* — React version, App vs Pages Router, the
  specific component/forms/table libraries, the Tailwind/styling choice, the
  build/test toolchain. That is the **framework choice**; frontend-architecture
  is the **state/data-fetching/rendering PATTERNS practiced inside whatever
  framework fills the slot**. "Use App Router, react-hook-form, TanStack Table"
  is react-nextjs; "server state lives in a query cache and is never copied
  into a client store; this route is RSC because it is read-mostly and
  SEO-relevant; this form validates with one schema on both client and server"
  is frontend-architecture. The patterns here are framework-agnostic in
  principle (they apply to a Remix/SolidStart/Vue frontend too); react-nextjs is
  the reference implementation when that slot is filled by React+Next. Do
  **not** restate React/Next API specifics here — name the *pattern*, defer the
  *API* to the framework concern.
- **`ux-radix`** (and `a11y-wcag-aa`) own the **component library, design
  system, interaction patterns, and accessibility** — the user-facing behavior
  of widgets (combobox keyboard nav, focus trap, `aria-current`, the visual
  empty/error *affordance*). This concern owns the **architecture that feeds
  those surfaces**: that an async view *has* loading/empty/error *states at
  all* and how they are derived from the fetch lifecycle — not how the empty
  state *looks* or which Radix primitive renders it. The seam: ux-radix says
  "the empty state is icon + message + primary action and is keyboard
  reachable"; frontend-architecture says "every async view must branch on
  loading/empty/error, not only render the happy path." They compose on the
  same screen; they do not overlap.
- **`api-style`** owns **the wire contract the frontend consumes** — the
  REST/GraphQL/gRPC/RPC paradigm, the contract/error shape, where input is
  validated *at the service boundary*. This concern owns the **client side of
  that boundary**: how the frontend *fetches against* the contract (the cache
  layer, query keys, invalidation, RSC server-fetch), and that the client
  validates form input for UX **in addition to** — never instead of — the
  server's authoritative validation. api-style says *what the contract is and
  that the server validates*; frontend-architecture says *how the client
  consumes it and that client validation is a UX convenience over the
  server's gate*. Do **not** restate contract/error-shape rules here.

## Components

- **Server-state layer** — the cache of remote data: a data-fetching library
  (TanStack Query / SWR) keyed by query keys with `staleTime`/`gcTime` and
  background revalidation, **or** React Server Components fetching on the server
  and passing data down. This layer owns loading/error/refetch/invalidation for
  remote data; the application does not hand-roll it.
- **Client-state layer** — UI-only state that never existed on a server: form
  draft values, toggles, modal open/close, wizard step, optimistic local
  overrides. Owned by component state / reducers / a client store. Kept
  *separate* from the server-state layer.
- **Rendering strategy (per route/segment)** — the recorded CSR / SSR / SSG /
  ISR / RSC (/ PPR + streaming) choice for each route, derived from freshness,
  personalization, SEO, and interactivity signals rather than a project-wide
  default.
- **Component composition + colocation** — state colocated as low in the tree
  as it is used; lifted only to the lowest common ancestor that needs it;
  composition (passing elements/children) used to avoid prop drilling; context
  used only when composition is insufficient, scoped to small providers.
- **Forms + validation split** — one schema (e.g. Zod) as the validation source
  of truth, run on the client for immediate UX feedback **and** on the server
  as the authoritative gate; react-hook-form (or equivalent) for form state so
  fields are not each a `useState`.
- **Mandatory async UI states** — every view backed by an async fetch or
  mutation renders explicit **loading**, **empty**, **error**, and **success**
  states — modeled as a status (a discriminated union / the query's
  `isLoading`/`isError`/`data` flags), not as scattered boolean flags and a
  bare happy path.

## Constraints

### Server state and client state are separate concerns with separate owners

- Remote data is owned by the **server-state layer** (query cache or RSC
  server-fetch). Client-only UI state is owned by the **client-state layer**.
  They are not the same problem and do not share a store.
- Server state is **not copied into a client state store** (Redux/Zustand/
  `useState`) "to have it locally". Fetched data lives in the cache that owns
  its freshness, loading, and error lifecycle; components read it from there.
  Duplicating it into client state re-introduces the staleness, manual loading
  flags, and refetch wiring the cache layer exists to remove.
- The data-fetching/cache layer (TanStack Query / SWR / RSC) owns caching,
  background revalidation, and invalidation. The application does not hand-roll
  fetch-into-`useState`-with-a-loading-boolean for shared remote data.

### Rendering strategy is a recorded per-route choice on freshness/SEO/personalization signals

- Each route/segment's rendering strategy is a **deliberate, recorded choice**,
  not a project-wide default applied blindly. The decisive signals: data
  **freshness** (build-time-static → request-time-fresh), **personalization**
  (per-user content forces SSR/CSR — SSG cannot personalize), **SEO/first-paint**
  (server-rendered HTML for crawlable/landing routes), and **interactivity**
  (heavy client interaction needs CSR/hydration).
- Prefer static (SSG) and revalidated-static (ISR) where content is stable or
  changes on a schedule; reach for SSR only when content must be fresh-to-the-
  request or personalized; use CSR for highly interactive, behind-auth,
  non-SEO surfaces; use **React Server Components** for read-mostly, data-heavy
  trees to keep data-fetching and large dependencies off the client bundle,
  marking only the interactive leaves `"use client"`. (Which framework API
  expresses each of these is `react-nextjs`'s.)

### State is colocated; composition before context

- State is **colocated** as close to where it is used as possible, and lifted
  **only** to the lowest common ancestor that needs it — not hoisted to a
  global store by default.
- **Prop drilling is solved by composition first** (passing children/elements),
  and by context only when composition is insufficient. Context providers are
  scoped and small, not one monolithic app-wide context. A global client store
  is justified by genuinely cross-cutting *client* state, never by remote data
  (which belongs in the server-state layer).

### Forms validate on the client for UX and on the server for trust — from one schema

- Form input is validated on the **client** for immediate feedback **and** on
  the **server** as the authoritative gate. Client validation is a UX
  convenience; it is **never** the security boundary. (The server-side gate is
  `api-style`'s boundary-validation rule; this concern requires the client to
  mirror it for UX, not replace it.)
- The validation rules are expressed **once** (a shared schema, e.g. Zod) and
  reused on both sides, so client and server cannot drift. Form field state is
  managed by a form library, not a `useState` per field.

### Every async view renders loading / empty / error / success — not just the happy path

- A view backed by an async fetch or mutation **must render all four states**:
  **loading** (initial fetch / pending mutation), **empty** (a successful
  response with zero items), **error** (any non-success outcome, with a way
  forward), and **success** (the data). The happy path alone is incomplete.
- These states are modeled as a **status** (a discriminated union, or the query
  layer's `isLoading`/`isError`/`data`), not as ad-hoc boolean flags that can
  represent impossible combinations. (How each state *looks* and is keyboard-
  reachable is `ux-radix`'s; that the branch *exists* is this concern's, and it
  ties to the it.39 guard-branch discipline.)

## Drift Signals (anti-patterns to reject in review)

- Fetched remote data copied into a Redux/Zustand/`useState` store "to keep it
  locally" → server state belongs in the query cache / RSC, not duplicated into
  client state
- `useEffect` + `fetch` + a `loading` boolean + a `data` `useState`, hand-rolled
  per component for shared remote data → use the server-state layer (TanStack
  Query / SWR / RSC server-fetch)
- One project-wide rendering default applied to every route with no per-route
  rationale → record the per-route strategy on freshness/SEO/personalization
  signals
- A read-mostly, data-heavy page shipped as a fully client-rendered bundle that
  fetches on mount when it has no interactivity / is SEO-relevant → server-render
  it (RSC/SSR/SSG), mark only interactive leaves client
- Personalized / per-user content statically generated (SSG) → SSG cannot
  personalize; use SSR or client fetch behind auth
- State hoisted to a global store when only one subtree uses it → colocate it
- Prop drilling through many intermediate layers when composition (children/
  slots) would pass the data directly → compose before adding context
- One monolithic app-wide context provider holding unrelated state → split into
  small, scoped providers
- Client-only form validation with no server-side check → client validation is
  UX, not the security gate; the server must validate (api-style)
- Separate, divergent validation rules on client and server → express once in a
  shared schema, reuse on both sides
- An async view that renders only the happy path (no loading, no empty, no
  error branch) → render all four states; a silent blank or a thrown error to
  the user is a defect (it.39 guard branches)
- Loading/error tracked with scattered booleans that allow impossible combos
  (e.g. `loading && error && data`) → model state as a status / discriminated
  union

## When to use

Any project with a **non-trivial interactive web frontend** — a UI that fetches
remote data, holds client state, and renders multiple async views (dashboards,
admin consoles, CRUD apps, authenticated product surfaces). It is a
**non-exclusive, composable** concern (no slot): it adds the state/data-fetching/
rendering *patterns* on top of whatever framework fills `frontend-framework`.

**Skip** it for a **static/content site** (marketing pages, docs, a blog — the
rendering decision is trivially "static", there is little client state, and a
content framework like Hugo/Hextra already encodes it) and for an **API-only /
headless backend** with no frontend at all.

Compose with **`react-nextjs`** (the framework whose APIs express these
patterns), **`ux-radix`** + **`a11y-wcag-aa`** (the component library / design
system / accessibility that render the states this concern requires),
**`api-style`** (the wire contract the server-state layer consumes and whose
server-side validation the client mirrors), and **`sample-data`** (the varied
seed data that exercises the empty/populated/edge async states this concern
demands be rendered).

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: per-route rendering strategy (freshness/SEO/personalization) + server-state vs client-state split
- TD: component/state/data-fetching layers, colocation, one-schema form validation, async-state branches
- DESIGN_SYSTEM: mandatory async UI states (loading/empty/error/success) as first-class designed surfaces
- TEST_PLAN: every async view branches on loading/empty/error/success, not only the happy path

## ADR References

Selecting this concern forces three artifact changes (it does **not** edit
slots.yml or concern-resolution.md):

- An **ADR** recording (a) the per-route/segment **rendering strategy** and its
  freshness/SEO/personalization rationale, and (b) the **state + data-fetching
  architecture** — the server-state layer (query cache or RSC) vs client-state
  layer split, and the rule that server state is not duplicated into client
  state.
- The **technical-design** artifact gains explicit **component / state /
  data-fetching layers** — where state is colocated, what the server-state
  layer owns, how forms validate on both sides from one schema, and where each
  async view's loading/empty/error/success branches live.
- The **design-system** artifact (DESIGN.md) gains the **mandatory async UI
  states** as first-class, designed surfaces (loading / empty / error / success
  for each data view), not afterthoughts.

Record an ADR when a route departs from the default rendering strategy, or when
a client store is introduced (justify the cross-cutting *client* state it holds
and confirm it holds no server state). A material uncertainty about the
rendering or data-fetching architecture is a `tech-spike`, not a silent
assumption (see `workflows/references/concern-resolution.md`).
