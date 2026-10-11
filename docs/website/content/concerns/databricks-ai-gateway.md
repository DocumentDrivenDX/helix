---
title: "Databricks AI Gateway (model access on Databricks)"
slug: databricks-ai-gateway
generated: true
aliases:
  - /reference/glossary/concerns/databricks-ai-gateway
---

**Category:** Infrastructure · **Areas:** api, infra

## Description

## Category
infrastructure

## Areas
api, infra

## Platform

**Platform-specific (Databricks).** The Databricks realization of
`model-gateway`: how that concern's constraints are met when a Databricks App
calls models through the workspace AI Gateway. The generic constraints (alias,
owner, deploy gate, capability, eval-gated rebinds, attribution) live in
`model-gateway` and are not restated here.

## Boundary

Owns only the Databricks mechanics below. Identity (service principal vs
on-behalf-of) and how settings reach the app belong to `databricks-apps`; access
to a gateway service is a Unity Catalog grant governed by `unity-catalog`.

## Constraints

- **A gateway service name is an ordinary per-target setting.** It is required
  and validated at deploy like any other; how settings reach the app is
  `databricks-apps`'s rule.
- **Access to a gateway service is a Unity Catalog grant**, issued by the module
  that creates the service (see `unity-catalog`).
- **The first deploy is two steps.** The app's service principal exists only
  after its first deploy, so grant it access after that deploy, then verify with a
  real call.
- **Send W3C `traceparent` on every model call** so the product's spans and the
  gateway's land in one trace in the workspace's trace table. Span content rules
  are `o11y-otel`'s.

## Drift Signals (anti-patterns to reject in review)

- A gateway grant applied by hand or from the product's repository rather than
  by the module that owns the service
- A first deploy treated as complete before the service principal has access
- Model calls that carry no `traceparent`, leaving the gateway's records
  unjoinable to the product's

## When to use

A product that calls models through the Databricks AI Gateway. Composable (no
slot). Select it with `model-gateway`, `databricks-apps` and `unity-catalog`.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- TD: states how access to each gateway service is granted and in what order on first deploy
- deployment-checklist: grants verified by a real call after the first deploy

## ADR References

Selecting this concern needs no ADR; `concerns.md` records it. Write an ADR only
when the project deviates from a constraint here.

## Practices by activity

Agents working in any of these activities inherit the practices below through runtime work context, such as a DDx bead context digest.

The Databricks specifics only; the generic practices are in `model-gateway`.

## Design

- Name who creates each gateway service and issues its Unity Catalog grants.
- Decide the identity per call path in `databricks-apps`; the gateway's usage
  record should name the real caller.

## Implementation

- Send `traceparent` on every model call.

## Deploy

- Confirm the owning module applied the services and grants before the app that
  depends on them. The app's service principal exists only after its first
  deploy, so a first deploy is two steps: deploy, then grant it access.
- Verify by a real call, not by a merged grant.
