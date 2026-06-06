Draft a deprecation-notice artifact during helix-data phase 06-evolve.
Use it when retiring a table, view, feed, contract, dashboard, or old semantic version.
Gather artifact name, successor, owners, consumer list, usage logs, migration steps, and dates.
Good output leaves no ambiguity about what breaks after the final date.
Name consumers affected and the expected replacement for each.
Include a concrete timeline with announcement, migration support, freeze, and decommission.
Escalate when usage logs show unknown or unmanaged consumers.
Refuse to decommission without consumer sign-off for finance, compliance, or operational dashboards.
Do not promise indefinite compatibility.
Call out consumer-side breaking mismatch fixtures when they justify the timeline.
Name the data catalog entry, Slack channel, or ticket where the notice will live.
State how final query or usage checks will prove migration is complete.
Keep the notice concise and suitable for posting to a data catalog and Slack.
Never omit the final decommission date.
Include an exception path only if governance allows it.
