# Concern: Scala + sbt

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
