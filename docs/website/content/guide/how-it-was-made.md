---
title: How this guide was made
weight: 900
type: docs
---

Every page of this site was made from the repository by documentor, and is rebuilt when the repository changes. This page says how each one was made.

## What the repository is

| Trait | Chosen | Confidence | Evidence |
|---|---|---:|---|
| A HELIX methodology catalog | yes | 1.00 | `workflows/activities/*/artifacts/*/meta.yml`; `skills/helix/SKILL.md`; `workflows/modes/*.md` |
| Continuous integration on GitHub Actions | no | 0.60 | `.github/workflows/*.yml ~ /^jobs:/` |
| Tasks in a justfile, a Makefile, or npm scripts | no | 0.60 | `justfile` |
| A command line installed from pyproject (Typer or Click) | no | 0.40 | `**/pyproject.toml ~ /^\[project\.scripts\]/` |

## The pages

| Reader | Page | Kind | Made by | Evaluated by | Sources | State |
|---|---|---|---|---|---:|---|
| developer | Overview | explanation | agent-opus | agent-sonnet | 8 | stale |
| developer | Architecture | explanation | agent-opus | agent-sonnet | 14 | stale |
| developer | Developer guide | how-to | a person (adopted) | agent-sonnet | 3 | stale |
| developer | Documentor | reference | documentor's own guide | — | — | delegated |

## The architecture views

Drawn from `docs/helix/02-design/architecture-model.toml`: 7 parts and 7 connections, each citing the file that shows it.

| View | Type | Parts |
|---|---|---:|
| HELIX in a repository | flowchart | 7 |
| Where HELIX runs | deployment | 7 |
| request | journey | 0 |
| The pieces | cast | 7 |
