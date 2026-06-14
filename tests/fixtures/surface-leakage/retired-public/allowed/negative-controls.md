# Retired Public Surface Negative Controls

Docker mounts can contain `/helix` as a container path without invoking a
HELIX selector:

```bash
docker run -v "$(pwd):/helix:ro" image
```

Graph edge addresses are not slash-command selectors:

```yaml
links:
  - to: helix.admin:PRD-007
```

YAML keys named after the product are not routing selectors:

```yaml
helix:
  version: 1
```

Raw library helper paths are not globally banned:

```text
family-test/library/scripts/helix_check.py
```
