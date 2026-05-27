# Practices: Frontend Architecture

## Requirements (Frame activity)

- Stories backed by remote data must state which data is **server state**
  (cache of remote data) versus **client state** (UI-only). The two get
  different owners.
- Every story that renders fetched data or runs a mutation must enumerate its
  **loading / empty / error / success** states as acceptance criteria — not
  only the happy path.
- Routes/views must declare their **rendering strategy** signal: is the content
  static, scheduled-refresh, fresh-to-request, or personalized? Is it
  SEO-relevant? Is it behind auth?
- Forms must specify the validation rules once (a shared schema) and note that
  the rules run on both client (UX) and server (authority).

## Design

### Server-state vs client-state split

- Classify each piece of state up front: **server state** (originated on a
  server, can change without this client, needs caching/refetch/invalidation)
  → the server-state layer; **client state** (only ever existed in this UI:
  modal open, wizard step, draft input, selection) → component state / reducer
  / scoped client store.
- The server-state layer is a data-fetching/cache library (TanStack Query /
  SWR) **or** React Server Components fetching on the server. Pick one as the
  primary owner of remote data; do not also keep that data in a client store.
- Client state that is genuinely cross-cutting (theme, auth-session view,
  sidebar) may use a small client store or scoped context. Anything per-subtree
  stays colocated.

### Rendering strategy (per route/segment)

Decide per route from the signals, and record the decision:

| Signal | Strategy |
|--------|----------|
| Content stable, same for all users, SEO matters | **SSG** (static) |
| Content changes on a schedule, same for all users, SEO matters | **ISR** (revalidated static) |
| Content must be fresh-to-the-request or personalized, SEO matters | **SSR** |
| Highly interactive, behind auth, not SEO-relevant | **CSR** |
| Read-mostly, data-heavy tree, want data + deps off the client bundle | **RSC** (server components; interactive leaves `"use client"`) |
| Static shell + dynamic slot on one page | **PPR / streaming** with Suspense boundaries |

- Default toward static (SSG/ISR) where possible; escalate to SSR only for
  freshness/personalization; reach for CSR for interactive non-SEO surfaces.
- (Which framework API expresses each strategy is `react-nextjs`'s; this table
  is the *decision*, not the API.)

### Composition + colocation

- Place state at the **lowest** component that uses it. Lift to the lowest
  common ancestor only when two siblings must share it.
- Solve prop drilling with **composition** (pass `children` / element props)
  before introducing context. Use context only when composition cannot reach,
  and scope each provider tightly.

### Forms + validation

- One schema (e.g. Zod) is the source of truth. Bind it to the form library
  (react-hook-form + resolver) for client-side feedback, and run the **same
  schema** on the server before the data is trusted.
- Validate on **blur or submit**, not on every keystroke; surface schema error
  messages inline next to fields.

### Async UI states

- Model every async view's state as a **status** (a discriminated union, or the
  query layer's `isLoading` / `isError` / `data`), and design a distinct
  surface for **loading**, **empty**, **error**, and **success**. (How each
  surface looks / is keyboard-reachable is `ux-radix`'s.)

## Implementation

### Server-state layer

- Remote reads/writes go through the cache layer (TanStack Query / SWR) or are
  fetched in a server component (RSC). Cache entries are keyed (query keys),
  with `staleTime` / `gcTime` tuned to the data's volatility and background
  revalidation on.
- Mutations invalidate or update the relevant cache keys; the UI re-derives from
  the cache rather than manually patching a separate client copy.
- No `useEffect` + `fetch` + `setData` + `setLoading` hand-rolled for shared
  remote data.

### Client-state layer

- UI-only state uses `useState` / `useReducer` colocated, or a scoped store for
  cross-cutting client concerns. It never holds a copy of server-fetched data.

### Forms

- Form state via react-hook-form (or equivalent) — uncontrolled fields, not a
  `useState` per field. Resolver wired to the shared schema. The server action /
  handler re-validates with the same schema before persisting.

### Async state branching

- Each async view branches on its status and renders the matching surface:
  loading → skeleton/spinner; empty → empty-state surface; error → error surface
  with a retry/way-forward; success → the data. The four branches are present in
  the code, not just the success branch. This is the it.39 guard-branch
  discipline applied to data views.

## Testing

- **Server/client state separation** is reviewer-checkable: grep/scan client
  stores and `useState` for fields that hold server-fetched entities; the
  server-state cache (or RSC) must be the sole owner of remote data.
- **Async-state coverage**: for each async view, a test/visual check exercises
  all four states. The **empty** and **error** states in particular are
  exercised with real seeded data (see `sample-data`: include zero-item and
  failure cases), not just the populated happy path.
- **Forms validate on both ends**: a test submits invalid input and asserts the
  **server** rejects it (the client-only path is not the gate), and asserts the
  client shows the inline error from the shared schema.
- **Rendering strategy** is verified against its recorded signal: a route marked
  SSG/ISR is checked to emit server-rendered HTML; a personalized route is not
  statically cached.

## Quality Gates

- **Server state is not duplicated into client state stores** — remote data
  lives in the query cache (or RSC), never copied into Redux/Zustand/`useState`
  to "keep it locally".
- **No hand-rolled fetch-into-`useState`-with-loading-boolean** for shared
  remote data — the server-state layer owns caching/loading/error/refetch.
- **Every async view renders loading / empty / error / success** — not just the
  happy state (ties to it.39 guard branches). The error branch offers a way
  forward; the empty branch is explicit, not a blank container.
- **Async state is modeled as a status / discriminated union**, not scattered
  booleans that permit impossible combinations (`loading && error && data`).
- **Rendering strategy is recorded per route** with a freshness/SEO/
  personalization rationale — no blind project-wide default; no personalized
  content statically generated (SSG).
- **State is colocated** to the lowest component that uses it; prop drilling is
  solved by composition before context; no monolithic app-wide context holding
  unrelated state.
- **Forms validate on the client for UX AND on the server for trust, from one
  shared schema** — client validation is never the security boundary; client
  and server rules do not diverge.
