---
ddx:
  id: US-001
---

# US-001: Create Search

## Acceptance Criteria

- [ ] **US-001-AC1** - Given a valid tenant, when the client sends POST
  /api/v1/search with this payload, then HTTP status 201 is returned.

```json
{"query": "term", "limit": 10}
```
