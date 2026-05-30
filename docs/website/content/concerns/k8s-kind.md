---
title: "Kubernetes + kind"
slug: k8s-kind
generated: true
aliases:
  - /reference/glossary/concerns/k8s-kind
---

**Category:** Infrastructure · **Areas:** infra

## Description

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

## Practices by activity

Agents working in any of these activities inherit the practices below via the bead's context digest.

## Requirements (Frame activity)
- Identify all services that need to run locally together
- Confirm production target is Kubernetes (not serverless/PaaS)
- Plan for secrets management strategy before first deployment

## Design
- One Helm chart per deployable service
- Chart structure: `Chart.yaml`, `templates/`, `values.yaml` (defaults), `values-dev.yaml`, `values-prod.yaml`
- Use chart dependencies (e.g., bitnami/postgresql) for stateful services
- Service discovery via Kubernetes DNS (`<svc>.<namespace>.svc.cluster.local`)
- Expose services locally via `kubectl port-forward` or kind ingress

## Implementation
- Create local cluster: `kind create cluster --config kind-config.yaml`
- Load local images: `kind load docker-image <image>:<tag>`
- Install/upgrade: `helm upgrade --install <release> ./deploy/helm/<chart> -f values-dev.yaml`
- Image tagging: use git SHA for dev (`$(git rev-parse --short HEAD)`), semver for releases
- Multi-stage Dockerfile: builder stage (full toolchain) → runtime stage (minimal base)
- Do not use `latest` tag in Helm values — pin to a specific tag

## Testing
- Smoke test after `helm install`: run `kubectl get pods` and verify all pods are `Running`
- Integration tests can target services via port-forward
- Use `helm template` to validate rendered manifests before applying

## Quality Gates
- `helm lint ./deploy/helm/<chart>` — chart syntax check
- `helm template ./deploy/helm/<chart> -f values-dev.yaml | kubectl apply --dry-run=client -f -` — manifest validation
- Docker image must build successfully before helm install

## Local Dev Workflow
```bash
kind create cluster --config deploy/kind-config.yaml
docker build -t myapp:local .
kind load docker-image myapp:local
helm upgrade --install myapp ./deploy/helm/myapp -f deploy/helm/myapp/values-dev.yaml
kubectl port-forward svc/myapp 8080:80
```
