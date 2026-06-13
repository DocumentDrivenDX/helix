---
title: "Scala + sbt"
slug: scala-sbt
generated: true
aliases:
  - /reference/glossary/concerns/scala-sbt
---

**Category:** Tech Stack · **Areas:** all

## Description

## Category
tech-stack

## Areas
all

## Slot
language-runtime

## Components

- **Language**: Scala 2.x (pinned per project)
- **Build system**: sbt with `sbt-dynver` for git-tag-based versioning
- **Formatter**: `scalafmt`
- **Linter / refactoring**: `scalafix` with `OrganizeImports`
- **Testing**: ScalaTest (primary)
- **Effect system**: ZIO (where applicable)
- **Versioning**: `sbt-dynver` with `-SNAPSHOT` suffix for dirty/non-tagged commits

## Constraints

- All code must pass `scalafmtCheckAll` (zero diff)
- All code must pass `scalafixAll OrganizeImports`
- No uncommitted changes should reach CI with a clean version string
- Concurrent task limits: derived from CPU count (`(nproc / 2) - 1`, min 2)
- Remote build cache: `pushRemoteCacheTo` configured for incremental CI builds
- Library dependency schemes must be explicit to avoid eviction noise

## When to use

Existing Scala projects on the sbt ecosystem. New Scala services should
evaluate ZIO + sbt as the default stack. Note: projects actively migrating
from Scala to TypeScript should prefer `typescript-bun` for new code and
maintain `scala-sbt` only for the remaining Scala surface.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: Scala + sbt (scalafmt, scalafix, ScalaTest, ZIO where applicable) as the language-runtime
- TD: sbt-dynver versioning, format/lint gates, build-cache and concurrency conventions

## Practices by activity

Agents working in any of these activities inherit the practices below through runtime work context, such as a DDx bead context digest.

## Requirements (Frame activity)
- Identify whether the project is greenfield Scala or has a migration plan to another runtime
- If mid-migration, scope new work to the target stack and minimize new Scala surface

## Design
- Organize as an sbt multi-project build; each logical module is a subproject
- Depend on ZIO for effect management, ZIO JSON for serialization where applicable
- Define portable contracts at service seams to enable incremental migration

## Implementation
- Format before commit: run `scalafmtAll` + `scalafixAll OrganizeImports` (or the combined alias)
- Use `sbt-dynver` for versioning; do not hardcode version strings
- `dynverSeparator := "-"` for Docker compatibility
- `packageTimestamp := Package.gitCommitDateTimestamp` for reproducible artifacts
- Exclude `.bloop`, `.cache`, `.targets`, `.hydra`, `.metals` from IDE indexing

## Testing
- Framework: ScalaTest
- Property-based: ScalaCheck (if used)
- Run: `sbt test`
- CI: separate unit and integration suites; integration tests may require Docker services

## Quality Gates (pre-commit / CI)
- `sbt scalafmtCheckAll` — format check
- `sbt scalafixAll OrganizeImports` — import organization
- `sbt test` — unit test suite
- `sbt compile` — compile all subprojects

## Dependency Management
- Declare in `project/Dependencies.scala` or `build.sbt` with explicit `libraryDependencySchemes` for version conflicts
- Use `VersionScheme.Always` sparingly (only for known-safe upgrades)
- Remote cache: `pushRemoteCacheTo` reduces incremental CI time
