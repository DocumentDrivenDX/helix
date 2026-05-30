# Concern: Kubernetes + kind

## Category
infrastructure

## Areas
infra

## Boundary

This concern is a **runtime implementation** that hosts whatever deployables
`deployment-topology` chose to ship (one modular monolith or many
microservices — both run here). It owns cluster / Helm chart / image-build /
local-kind workflow mechanics. It does **not** decide the deployable count
or seams (`deployment-topology`), the per-process operational contract each
deployable honors (`twelve-factor`), or the telemetry the deployables emit
(`o11y-otel`).

## Components

- **Local cluster**: `kind` (Kubernetes in Docker) — NOT docker-compose
- **Package manager**: Helm for application deployment
- **Manifests**: Helm charts with `values.yaml`, `values-dev.yaml`, `values-prod.yaml`
- **Image builds**: Docker with multi-stage builds; image tagged from git SHA or semver
- **Local dev workflow**: `kind create cluster` + `helm install` + port-forward

## Constraints

- Local development uses a kind cluster, not docker-compose
- Services packaged as Helm charts with environment-specific values files
- Image builds must be reproducible (deterministic tags, no `latest` in production)
- Secrets managed via Kubernetes Secrets or external secret manager — not in values files
- `values-dev.yaml` overrides for local kind cluster; `values-prod.yaml` for production

## When to use

Projects with services that deploy to Kubernetes in production. Kind provides
a local cluster that mirrors production closely enough to catch config and
networking issues before deployment. Prefer kind over docker-compose when
services need service discovery, ingress, or multi-container orchestration.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: Kubernetes + kind (Helm, reproducible images) as deployment topology — not docker-compose
- IMPLEMENTATION_PLAN: Helm charts + env values files, image-build/tag, kind create + install + port-forward workflow
