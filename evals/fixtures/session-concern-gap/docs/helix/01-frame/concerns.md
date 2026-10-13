---
ddx:
  id: concerns
  authoring:
    home: repo
---

# Project Concerns

## Active Concerns

| Concern | Source | Areas | Why Active | Key Practices |
|---------|--------|-------|------------|---------------|
| twelve-factor | library | `area:api`, `area:infra` | The recipe server is a deployed process. | Externalized configuration, startup validation, graceful shutdown. |

## Area Labels

- `area:api` — recipe server process
- `area:infra` — deployment and lifecycle
