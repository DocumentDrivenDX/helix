---
title: "Concourse microsite integration"
slug: concourse-integration
weight: 360
activity: "Design"
source: "02-design/concourse-integration.md"
generated: true
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

# Concourse microsite integration

Owner-authorized 2026-10-29. Shared behavior belongs to Concourse CONTRACT-001;
HELIX owns opt-in build wiring. `documentor.concourse.install` consumes a locally
checked-out, immutable Concourse revision, verifies every distribution digest,
then copies its browser assets and Hugo partial. `publish.site.concourse` selects
the site/API/package and enables the component. The default GitHub Pages build
keeps it disabled; the authenticated Cloudflare copy enables it at build time.

The base template calls the generic partial after content. The partial identifies
resource by Hugo source path and revision by RawContent digest; runtime UI sits
next to authored heading IDs. No private comment data enters the build. Documentor
owns installation and site.py owns orchestration; the browser/server protocol
and implementation remain outside HELIX. Concourse has no import of documentor.

Verification: Python installer tests cover disabled/no config, valid copies, bad
digest and non-origin API rejection; a real Hugo build and browser journey must
show marker/base-path integration, signed-out login and section persistence.
Production provider/session/cloud acceptance is a separate deployment gate.

Rollback: disable Concourse and rebuild; immutable source/attestations remain
unchanged. Infrastructure rollback must preserve D1 discussion data.
