Helix-data is active and autonomy is set to manual, so I'm not going to run
the backfill on my own. A 90-day backfill replays every event from the
upstream ingest into the warehouse — this is destructive against the mart
(downstream models will recompute, dashboards may show drift while it
runs). OK to proceed with the full 90 days, or do you want me to scope it
down to 7 days first as a dry-run? I'll wait for your explicit confirm
before executing anything.
