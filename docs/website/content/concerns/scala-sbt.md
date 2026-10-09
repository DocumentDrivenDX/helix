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
- **Configuration**: `zio-config` 4.x (typesafe/magnolia modules) feeding ZIO's `ConfigProvider` — one central config case class per application; `pureconfig` for non-ZIO code — NOT scattered `sys.env`/`System.getenv`
- **Versioning**: `sbt-dynver` with `-SNAPSHOT` suffix for dirty/non-tagged commits

## Constraints

- All code must pass `scalafmtCheckAll` (zero diff)
- All code must pass `scalafixAll OrganizeImports`
- No uncommitted changes should reach CI with a clean version string
- Concurrent task limits: derived from CPU count (`(nproc / 2) - 1`, min 2)
- Remote build cache: `pushRemoteCacheTo` configured for incremental CI builds
- Library dependency schemes must be explicit to avoid eviction noise
- All configuration is declared in one central config case class (single module, e.g. `AppConfig.scala`) with a derived `Config` (zio-config `deriveConfig`) and typed fields, defaults, and required markers
- Config is loaded once as a `ZLayer` at the application edge and provided by dependency injection; no `sys.env`/`System.getenv` or ad hoc `ConfigProvider` reads outside the config module
- Secrets use `Config.Secret` (zio) or an equivalent redacting type; invalid or missing config fails at startup (layer construction), not at first use
- Config is layered by owner per `twelve-factor`: ops-injected values (env vars, mounted files, secret manager) over a committed `application-<env>.conf` over committed defaults (`reference.conf`/`application.conf`); ops-owned keys (hosts, credentials) are required with no default and never appear in committed files
- Real environment variables take precedence over files; local-development values come from the IDE/sbt run configuration, not a `.env` file; a committed `.env.example` lists every variable (no secrets in it)

## When to use

Existing Scala projects on the sbt ecosystem. New Scala services should
evaluate ZIO + sbt as the default stack. Note: projects actively migrating
from Scala to TypeScript should prefer `typescript-bun` for new code and
maintain `scala-sbt` only for the remaining Scala surface.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: Scala + sbt (scalafmt, scalafix, ScalaTest, ZIO where applicable) as the language-runtime
- TD: sbt-dynver versioning, format/lint gates, build-cache and concurrency conventions, central config case class and its config-key contract (owner and source per key)

## Practices by activity

Agents working in any of these activities inherit the practices below through runtime work context, such as a DDx bead context digest.

## Requirements (Frame activity)
- Identify whether the project is greenfield Scala or has a migration plan to another runtime
- If mid-migration, scope new work to the target stack and minimize new Scala surface

## Design
- Organize as an sbt multi-project build; each logical module is a subproject
- Depend on ZIO for effect management, ZIO JSON for serialization where applicable
- Centralize configuration in one case class with `deriveConfig` (zio-config-magnolia) and load it via `ConfigProvider` as a `ZLayer`; sources layered as environment / secret files > `application-<env>.conf` > `application.conf` / `reference.conf` (zio-config-typesafe) > case-class defaults; ops-owned keys have no default; production relies on real env vars or the platform secret manager
- Commit `.env.example`; git-ignore `.env`
- Define portable contracts at service seams to enable incremental migration

## Implementation
- Format before commit: run `scalafmtAll` + `scalafixAll OrganizeImports` (or the combined alias)
- Use `sbt-dynver` for versioning; do not hardcode version strings
- `dynverSeparator := "-"` for Docker compatibility
- `packageTimestamp := Package.gitCommitDateTimestamp` for reproducible artifacts
- Read configuration only by depending on the config layer; ban `sys.env`/`System.getenv` outside the config module (scalafix `DisableSyntax.regex` with patterns for `System\\.getenv`, `sys\\.env`, and `ConfigProvider\\.envProvider`; it is syntactic, so the config module opts out with `// scalafix:off DisableSyntax` (closed with `// scalafix:on`))
- Exclude `.bloop`, `.cache`, `.targets`, `.hydra`, `.metals` from IDE indexing

## Testing
- Framework: ScalaTest
- Config in tests: provide `ConfigProvider.fromMap(...)` or a test `ZLayer`; never depend on a developer's `.env`
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
