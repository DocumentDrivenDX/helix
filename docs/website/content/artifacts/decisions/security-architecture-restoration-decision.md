---
title: "Security Architecture — Restoration Decision"
slug: security-architecture-restoration-decision
weight: 280
activity: "Design"
source: "02-design/decisions/security-architecture-restoration-decision.md"
generated: true
collection: decisions
---
# Security Architecture — Restoration Decision

> Historical decision; superseded by the worked example at `docs/helix/02-design/security-architecture.md`.

`security-architecture` is restored as the canonical design-activity artifact for
trust boundaries, controls, and design-level security decisions.

## Decision

This artifact is restored rather than retired. Security requirements and the
threat model define the problem, but they do not replace the architectural
control surface that shapes implementation and testing.

## Why It Exists

- Security requirements say what must be protected.
- The threat model identifies what can go wrong.
- Security architecture decides how the system will prevent, detect, and
  recover from those threats.

## Canonical Inputs

- `docs/helix/01-frame/security-requirements.md`
- `docs/helix/01-frame/threat-model.md`
- `docs/helix/02-design/architecture.md`

## Minimum Prompt Bar

- Start from security requirements and the threat model.
- Define trust boundaries and control points.
- Map threats to controls and controls to tests.
- Make identity, access, data protection, logging, and monitoring decisions
  explicit.
- Stay at the design level and do not drift into implementation code.

## Minimum Template Bar

- scope and decision summary
- trust boundaries
- control mapping
- identity and access
- data protection
- logging and monitoring
- residual risk
- test hooks or verification notes

## Canonical Replacement Status

`security-architecture` is not replaced by `architecture` or `threat-model`.
Those artifacts are upstream inputs. The security architecture remains the
place where the design-level security decisions are made concrete.

The deleted `data-protection` artifact stays retired as a standalone design
document. Its intent is already covered more cleanly by:

- `docs/helix/02-design/security-architecture.md` for design-level data
  protection controls, trust boundaries, encryption decisions, and monitoring
- `docs/helix/01-frame/compliance-requirements.md` for privacy, retention, and
  regulatory obligations
- `docs/helix/02-design/data-design.md` for schema, lifecycle, and storage
  consequences

Reintroducing `data-protection` as its own artifact would recreate the thin
stub that duplicated these responsibilities without a distinct review bar.
