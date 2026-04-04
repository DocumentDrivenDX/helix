---
title: Demos
weight: 5
prev: /docs/skills
---

## HELIX Quickstart

A scripted demonstration of the full HELIX lifecycle: install, frame, design,
build, and review. Builds a tiny Node.js temperature converter from scratch,
driven entirely by HELIX artifacts and the tracker.

{{< asciinema src="helix-quickstart" >}}

### What Happens

| Act | Phase | Description |
|-----|-------|-------------|
| 1 | Install | Install HELIX skills and CLI from the repo |
| 2 | Setup | Initialize git repo, tracker, and AGENTS.md |
| 3 | Frame | Agent creates product vision, PRD, and feature spec |
| 4 | Design | Agent creates technical design, then tracker issues |
| 5 | Build | Red: write failing tests. Green: implement to pass. |
| 6 | Verify | Run tests, check acceptance criteria |
| 7 | Review | Agent reviews all work for gaps |

### Run It Yourself

{{< tabs >}}

{{< tab name="Docker" >}}
```bash
# From the helix repo root:
docker build -t helix-demo docs/demos/helix-quickstart/
docker run --rm \
  -v ~/.claude.json:/root/.claude.json:ro \
  -v ~/.claude:/root/.claude \
  -v $(pwd):/helix:ro \
  -v $(pwd)/docs/demos/helix-quickstart/recordings:/recordings \
  helix-demo
```
{{< /tab >}}

{{< tab name="Local" >}}
```bash
cd /tmp
bash /path/to/helix/docs/demos/helix-quickstart/demo.sh
```

Requires: git, jq, node, npm, claude CLI, helix CLI.
{{< /tab >}}

{{< /tabs >}}
