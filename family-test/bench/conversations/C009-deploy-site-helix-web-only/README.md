# C009 — "Let's deploy the site"; helix-web active, build complete (guided, exploratory)

**Category:** conversation library (plan §1.5 row C009)
**Phase:** P5b
**Tier:** exploratory
**Flow classification:** legacy sibling-flow research row. Retained as an
expected-failing router probe for the retired public `helix-web` skill design;
not current HELIX user guidance.

## Scenario

Workspace state:
- `.helix.yml` marker has helix-web only (helix-infra is NOT in the
  marker even though the plugin is installed).
- A built artifact (`services/web/build/index.html`) exists.

Operator says: "Let's deploy the site."

## Expected behaviour

Per plan §1.5 row C009: "deploy" is a verb both helix-web and
helix-infra could claim. But helix-infra is NOT in the marker. Per
SKILL.md §1.5 resolution chain (marker authority is exclusive), the
skill MUST route to helix-web's deploy activity and MUST NOT propose
helix-infra workflows.

The expected route signal is `prose_attribution` mentioning helix-web
in the deploy context (e.g. "I'll use helix-web's deploy flow",
"routing this to helix-web", "helix-web owns deploy here").

## Why exploratory

Multi-flow disambiguation by marker (vs cwd) is one of two routing
discriminants (the other is cwd-under-scope). C009 tests the
marker-only branch — helix-infra is plugin-installed but
marker-excluded, so the marker is the authority. The cwd-disambiguated
variant lives at C010 (must_pass_core per plan §5). C009 is the
exploratory companion that adds the "plugin installed but not in
marker" wrinkle, which can mis-fire if the description-router treats
plugin install as authorisation.

## Negative control

`marker_edit` — swap the marker so helix-infra is added and helix-web
is removed. The skill MUST then route to helix-infra (or refuse and
ask, since the site is at services/web/ which is web-shaped). The
positive matcher (prose attribution naming helix-web in the deploy
context) MUST flip from present → absent.
