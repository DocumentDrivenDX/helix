# Wireframe Generation Prompt

Lay out one view of a user flow at each size class it supports, annotate every
element a person can act on, and name every state the view can be in.

## Purpose

Wireframe is the **view-level layout and state artifact**. Its unique job is
to record what is in one view, where, what each element does, and which states
the view moves through, so builders and reviewers share one picture. States
left implicit are the states that ship broken, so the wireframe names them
all. The solution or technical design links the wireframe by ID.

## Focus

- Create `docs/helix/02-design/flows/UF-XXX-[feature]/UF-XXX-NN-[view].md`
  beside its user flow. NN is a two-digit number given once, when the
  wireframe is created: the next number not yet used in that folder. Keep it
  when views are added, removed or reordered; never renumber an existing
  wireframe, and do not reuse a retired number. Put images in the folder's
  `assets/`. Set `ddx.type: wireframe`.
- Take the view's name, actions and transitions from the user flow.
- State the modality (screen, voice or chat) and the fidelity first, and
  annotate to the fidelity's depth:
  - **sketch**: the idea each region serves;
  - **low**: layout decisions: regions, order, what is primary;
  - **mid**: functionality: what each control does, validation, destination;
  - **high**: interaction, exact content, every state, accessibility.
- Draw one layout per supported size class. For voice or chat, the layout is
  the turn: what the system says, what the person can say or choose, and the
  confirmation.
- Label elements on the drawing by name and keep the words in the Annotations
  table. Give every interactive element a row that names the transition it
  triggers. Do not number rows.
- Fill the States table first. Each of ideal, empty, loading, partial, error,
  offline, slow, permission-denied and success either applies or is excluded
  with a concrete reason. Add view-specific states such as saving or
  streaming.
- For every state, give what the person sees, the available actions, the
  announcement (text and politeness, or the focus move that carries it) and the
  events that leave it. Say whether an error keeps what the person entered.
- Draw a Mermaid `stateDiagram-v2`, and keep it, the States table and the
  Events table in agreement.
- Note focus order, accessible names, headings and landmarks, and target size.
- Reference DESIGN.md tokens; do not define colors, type or spacing.

## Boundary Test

| If you are writing... | Put it in... |
|---|---|
| Layout, element purpose, states, events, announcements of one view | Wireframe |
| Movement between views | User Flow |
| The app-wide convention for how a loading or error state looks | DESIGN.md |
| Exact error codes or payloads that trigger a state | Contract |
| Component props, files, state management | Technical Design |
| Which test drives which state | Story Test Plan |

## Completion Criteria

- Modality and fidelity stated; annotation depth matches the fidelity.
- One layout per supported size class.
- Every interactive element annotated and linked to the flow.
- Every standard state applies or is excluded with a reason.
- Every state has an exit, and an announcement where focus does not carry it.
- Statechart and tables agree.
- Accessibility notes present.
