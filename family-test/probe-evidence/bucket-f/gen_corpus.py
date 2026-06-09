#!/usr/bin/env python3
"""Generate a synthetic perf corpus of N PRD instances.

Each corpus is a fully self-contained consumer workspace:
  perf-corpus-N/
    .helix.yml              (marker)
    docs/helix/01-frame/    (N PRD-XXXXX.md instances, fan-in chain)

The PRDs form a chain: PRD-00000 informs PRD-00001, PRD-00001 informs PRD-00002, etc.
The last PRD has no outgoing edges. Every edge is intra-methodology and resolvable
under the scope. Frontmatter is exact-shape matching consumer/clean.
"""
from __future__ import annotations
import sys
from pathlib import Path

MARKER = """\
helix_version: 1
methodologies:
  - id: helix
    root: docs/helix/
defaults:
  methodology: helix
"""

PRD_TEMPLATE = """\
---
ddx:
  id: PRD-{n:05d}
  type: prd
  methodology: helix
  library_type_version: 1.0.0
  links:{links_block}
---

# Synthetic PRD {n:05d}

## Summary
Synthetic PRD generated for perf corpus position {n}.

## Problem
Validator perf measurement requires a synthetic corpus of realistic shape.

## Users
- perf harness.

## Functional Requirements
- FR-1: parse frontmatter.
- FR-2: resolve one outgoing edge.

## Non Functional Requirements
- NFR-1: walk under wall-clock budget.

## Success Metrics
- 0 errors under helix_check.py marker.

## Out of Scope
- Anything beyond shape compliance.
"""

def gen(n_docs: int, root: Path) -> None:
    if root.exists():
        # remove to keep generation deterministic
        import shutil
        shutil.rmtree(root)
    frame = root / "docs/helix/01-frame"
    frame.mkdir(parents=True)
    (root / ".helix.yml").write_text(MARKER)

    # Build a graph node "feature-specification" target with one node per PRD?
    # Simpler: most PRDs are leaf (no edges). Half the PRDs declare one outgoing
    # `informs` edge to the next PRD in the chain. But edge `prd --[informs]--> prd`
    # is NOT in the graph (only prd→feature-specification). So we must keep PRDs
    # leaf. The methodology graph allows: prd→feature-specification.
    #
    # To get a realistic working corpus that the validator walks cleanly,
    # we keep all PRDs leaf (no links). The validator will still walk every
    # one, parse frontmatter, and check sections — that's the cost we measure.

    for i in range(n_docs):
        links_block = " []"
        (frame / f"PRD-{i:05d}.md").write_text(PRD_TEMPLATE.format(n=i, links_block=links_block))


if __name__ == "__main__":
    n = int(sys.argv[1])
    out = Path(sys.argv[2]).resolve()
    gen(n, out)
    print(f"generated {n} docs in {out}")
