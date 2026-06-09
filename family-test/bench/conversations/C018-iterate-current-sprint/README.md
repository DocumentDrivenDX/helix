# C018 — "Let's iterate on the current sprint" (guided, exploratory)

**Category:** conversation library (plan §1.5 row C018)
**Phase:** P5b
**Tier:** exploratory

## Scenario

Workspace state:
- `.helix.yml` marker has helix active.
- Three approved PRDs (PRD-001, PRD-002, PRD-003) in
  `docs/helix/01-frame/`.

Operator says: "Let's iterate on the current sprint."

## Expected behaviour

Per plan §1.5 row C018: the verb "iterate" routes to helix's
06-iterate activity (per the helix workflow phases). The skill must
engage, name the 06-iterate phase (or its artifacts:
metrics-dashboard, improvement-backlog), and offer to draft one of
those as the next action.

## Why exploratory

The 06-iterate phase is downstream of the canonical create-cascade
(vision → PRD → FEAT → story → build) and its observability is less
crisp than upstream phases. The verb "iterate" can mean many things
("iterate on the design", "iterate on tests"); only the
sprint-context disambiguator (multiple approved PRDs, no current
work-in-progress story) anchors it to 06-iterate. Marked exploratory
per plan §5 row C018.

## Negative control

Plugin removed (`plugins_remove: [methodology-product]`). Without the
helix methodology plugin, "iterate" no longer anchors to a specific
HELIX phase; the agent will not name "06-iterate" or its canonical
artifacts. The literal_or_banner_text matcher (which requires
06-iterate or metrics-dashboard or improvement-backlog) flips to
absent.
