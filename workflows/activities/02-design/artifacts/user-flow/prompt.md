# User Flow Generation Prompt

Describe how people move through one feature's views: what each action does,
what they see while it happens, and every way it can go wrong.

## Purpose

User Flow is the **feature-level flow artifact**. Its unique job is to record
the views (screens, modals, panels, voice or chat turns), the actions that
connect them, the decision points, the entry and exit points and every
alternate path, with the feedback the person sees on each transition.

HELIX retired `ux-design` as a monolithic artifact. User Flow does not revive
it: it carries only the flow, in a shape a tool can generate and check. The
solution design links `UF-XXX` instead of restating views and transitions, and
the rationale for choosing this flow over another stays in the solution design.

## Focus

- Create `docs/helix/02-design/flows/UF-XXX-[feature]/UF-XXX.md`, numbered
  after the governing feature. The feature's wireframes go in the same folder.
- List every view once, named by what it is. A modal or panel is its own view.
  A state of a view (loading, empty, error) is not a view; its wireframe's
  States and Events section holds it.
- Name each transition by its action. For each, give the control that triggers
  it, any guard, the target view, the feedback and the changed region. Do not
  number rows; paths and links use the action names.
- Name a decision view for every branch the person or the system takes.
- Give every action that can fail, be cancelled, return nothing or be denied
  its alternate path. If one cannot occur, say why.
- Keep the Mermaid diagram and the Transitions table identical in content.
- Trace every journey to a path of named transitions and the `US-<n>-AC<m>`
  IDs it proves. Name the Task Model row the journey carries out.
- Do not specify layout (the wireframe owns it) or visual values (DESIGN.md
  owns them).

## Boundary Test

| If you are writing... | Put it in... |
|---|---|
| Views, actions, controls, guards, feedback, alternate paths | User Flow |
| Why this flow was chosen over another; component decomposition | Solution Design |
| Exact route, API or event surface behind a transition | Contract |
| Layout, states and events of one view | Wireframe |
| One person's experience across several stories | User Journey Map |
| Which test walks which path | Story Test Plan |

## Completion Criteria

- Entry and exit points named; every view reachable.
- Every transition names its action, control, feedback and target.
- Every action that can fail, be cancelled or return nothing has an alternate
  path.
- Diagram and table agree.
- Every journey traced to named transitions and acceptance criteria.
