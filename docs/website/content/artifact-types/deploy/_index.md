---
title: "Deploy"
linkTitle: "Deploy"
weight: 60
generated: true
---

Ship to users with appropriate operational support, monitoring, and rollback plans.

Deploy artifacts cover four first-class surfaces in the current HELIX contract: `deployment-checklist`, `monitoring-setup`, `runbook`, and `release-notes`.

## Core Artifacts

{{< cards >}}
  {{< card link="/artifact-types/deploy/deployment-checklist/" title="Deployment Checklist" subtitle="Short, execution-ready release readiness checklist that captures the technical go/no-go checks, rollout verification, and rollback triggers for a service deplo…" >}}
  {{< card link="/artifact-types/deploy/release-notes/" title="Release Notes" subtitle="Release-scoped communication artifact that summarizes shipped user-visible and operator-visible changes, required actions, and known caveats for one rollout." >}}
{{< /cards >}}

## Supporting Artifacts

{{< cards >}}
  {{< card link="/artifact-types/deploy/monitoring-setup/" title="Monitoring Setup" subtitle="Service-specific observability and alerting setup required before or during rollout." >}}
  {{< card link="/artifact-types/deploy/runbook/" title="Runbook" subtitle="Service-specific operational procedures for on-call response, rollback, recovery, and routine maintenance tied to a deployed system." >}}
{{< /cards >}}
