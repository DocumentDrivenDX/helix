---
title: Databricks HELIX Recipe
weight: 23
---

Use this recipe when Databricks Genie, notebooks, jobs, or agent workflows need
HELIX-governed planning before analytical or data-product implementation. DDx is
not required.

## Install the HELIX skill

HELIX installs as a Genie Code skill that Genie auto-discovers by directory scan.
Start a new Agent-mode chat after installing for it to take effect.

From inside a Databricks notebook the kernel already carries workspace
credentials, so you need no setup. Run this in a Python cell:

```python
%pip install --quiet databricks-sdk PyYAML

import urllib.request, runpy
urllib.request.urlretrieve(
    "https://github.com/DocumentDrivenDX/helix/releases/latest/download/genie-install",
    "/tmp/genie_install.py",
)
g = runpy.run_path("/tmp/genie_install.py")
g["install"]()                # user-scoped; g["install"](shared=True) for workspace-wide
```

From a dev box or CI, set `DATABRICKS_HOST` and `DATABRICKS_TOKEN` (or
`DATABRICKS_PROFILE`), then run the installer:

```bash
curl -fsSL https://github.com/DocumentDrivenDX/helix/releases/latest/download/genie-install -o /tmp/genie-install
chmod +x /tmp/genie-install
/tmp/genie-install            # --shared for workspace-wide
```

The full procedure, including ACLs on shared installs and verification steps, is
in the [GitHub install guide](https://github.com/DocumentDrivenDX/helix/blob/main/docs/install/databricks-genie.md).

## What the runtime must provide

The Databricks runtime must provide:

- Access to the selected HELIX artifacts as governed context.
- A way to distinguish artifact edits from notebook, job, SQL, or pipeline
  implementation.
- Human approval before generated recommendations become source-of-truth
  artifacts.
- Evidence capture for outputs such as notebook results, SQL checks, job runs,
  dashboard screenshots, or model evaluation metrics.

Humans remain responsible for data policy, access boundaries, and acceptance
criteria. Agents should not infer governance decisions from data availability
alone.

## Recipe 1: create the first artifact stack

For a Databricks project, the first stack should make data assumptions explicit:

- Product vision: decision, workflow, or business outcome.
- PRD: target users, datasets, permissions, freshness, and success metrics.
- Feature spec: one analytical workflow, dashboard, pipeline, or agent task.
- Design note: source tables, transformations, quality checks, risks, and
  operational model.
- Implementation handoff: notebooks, jobs, dashboards, SQL files, or pipeline
  assets in scope.

Prompt:

```text
Create a HELIX artifact stack for this Databricks work. Include data sources,
permissions, freshness expectations, quality checks, consumers, and non-goals.
Do not write notebooks, SQL, jobs, or pipeline code yet. Mark unknowns as open
questions for human review.
```

## Recipe 2: run the first alignment pass

Prompt:

```text
Run a HELIX alignment review for these Databricks planning artifacts. Check that
the design and implementation handoff obey the product vision and PRD. Focus on
data authority, access assumptions, freshness, quality checks, metric
definitions, operational ownership, and acceptance criteria. Do not implement.
```

Human review should confirm:

- The agent did not broaden access beyond approved datasets.
- Metric definitions match the PRD.
- Freshness and quality expectations are testable.
- The artifacts name operational ownership.
<!-- vale Helix.Hedges = NO -->
- Unknowns remain visible rather than silently assumed.
<!-- vale Helix.Hedges = YES -->

## Recipe 3: create the first implementation handoff

Prompt:

```text
Create a HELIX implementation handoff for this Databricks work. Include governed
artifact references, allowed notebooks or SQL assets, tables and catalogs in
scope, datasets out of scope, acceptance criteria, validation evidence, and
rollback or follow-up expectations. Do not implement.
```

Implementation prompt:

```text
Implement only this HELIX handoff. Use the named artifacts as authority. Change
only the notebooks, SQL assets, jobs, dashboards, or pipeline files listed in
scope. Do not add new data sources or permissions. Capture evidence from query
results, job runs, data-quality checks, or metric evaluations in the final
response.
```

This keeps Databricks-specific execution inside Databricks while HELIX governs
why the work exists, what artifacts have authority, and what evidence proves
the handoff is complete.
