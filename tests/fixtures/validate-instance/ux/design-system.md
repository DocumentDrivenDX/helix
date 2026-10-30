---
ddx:
  id: design-system
  type: design-system
  authoring:
    home: repo
---

# DESIGN.md — DepositMatch

## Modalities, Size Classes and App Frame

- **Supported modalities**: screen
- **Size classes**: compact below 600 px, expanded at 600 px and above
- **App frame**: side-nav on expanded, top-bar on compact

## Navigation and Active State

A side nav lists the client workspaces and Imports.

| Surface | Component | Active cue (visible) | Semantic |
|---|---|---|---|
| Primary nav | side nav links | tinted background and left border | `aria-current="page"` |

### Destinations by Size Class

| Destination | Compact | Medium | Expanded |
|---|---|---|---|
| Clients | menu | not supported | side nav |
| Imports | menu | not supported | side nav |

## Visual Hierarchy

- **Layout**: the mapping table first, actions in a bar at the bottom

## Interaction States

| State | Applies to | Convention |
|---|---|---|
| Loading | Confirm mapping | busy button and double-submit guard |

## Tokens

### Color
Primary `#1F5AA6`; danger `#B42318`.

## Non-Goals

- Runtime architecture, data flow, component internals and ADRs.
