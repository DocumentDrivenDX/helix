---
title: "AI Design System SDK"
slug: ai-design-system
generated: true
aliases:
  - /reference/glossary/concerns/ai-design-system
---

**Category:** Tech Stack · **Areas:** ui, frontend

## Description

## Category
tech-stack

## Areas
ui, frontend

## Boundary

Owns use of the ai-design-system SDK as the component and presentation layer.
Current package scope is @skadden; do not invent synaptiq-ai-template package
names. Framework, routing, backend and hosting remain with their concerns.
Composes ux-interaction-patterns for behavior and a11y-wcag-aa for compliance
when selected. Evidence source: SDK CONTRACT-004 (app integration), CONTRACT-001
(tokens), CONTRACT-003 (themes) and installed catalogue/guidance, inspected
2026-10-11. Library behavior beyond those sources is unproven.

## Components

- @skadden/ui and @skadden/tokens; @skadden/audit as development tooling
- Installed @skadden/ui/AGENTS.md and catalogue.json as the widget/prop authority
- Optional @skadden/create-app starter and @skadden/mcp discovery; neither required

## Constraints

- Record exact installed package versions and commit the lockfile. Current SDK
  requires React 19 and Node 20+; verify compatibility against installed guidance
  before adopting a different runtime or upgrade.
- Import selected themes and bundled fonts, then ui.css once at the root.
  Use ThemeProvider; persist user choice only through the app's recorded policy.
  Embedded resolved-token views follow CONTRACT-004 and do not draw duplicate branding.
- Use SDK widgets, icons and branding where available. Layout uses --piq-* role
  tokens. No literal colors/fonts/radii, theme-specific restyling, app writes to
  --piq-* or overrides of .piq-* widget internals.
- Read installed guidance before building; never invent props or components.
  A missing dialog/tab/combobox or other widget requires a documented gap and
  SDK contribution or reviewed alternative with ownership and verification.
- Use SDK ESLint and Stylelint checks even when the runtime concern defaults to
  Biome. Record additive lint and Tailwind/token resolutions as project overrides;
  Tailwind utilities cannot bypass the SDK's presentation rules.
- Run lint and the audit on declared affected routes and supported themes and
  appearances, and interaction tests separately. Preserve JSON/HTML reports and
  screenshots. SDK-owned warnings route to its owner; document dispositions.
- Scope allow lists, data-audit-ignore, disabled checks or relaxed fail thresholds
  with rationale, owner, alternative verification and review trigger. Never use
  them to hide new debt. Default audit error failures block completion.

## Conflict Detection

Do not select ux-radix or databricks-appkit-ui automatically alongside this
concern. They prescribe competing component libraries. Choose one owner and
record the governing ADR and project override before readiness; disable the
competing prescription for the affected scope explicitly. A databricks theme
is a visual theme, not proof that @databricks/appkit-ui is installed. React/Vite
and Databricks hosting do not decide the component library.

## When to use

An app explicitly adopting the SDK, or an existing consumer. Do not infer
adoption solely from a React frontend, hosting target, or brand. Package access
is a prerequisite; unavailable registry access is a recorded blocker, not
permission to replace the SDK silently. Keep credentials out of source/evidence.

## Artifact Impact

- ADR: library conflicts or deviations and their scoped rationale (no ceremony ADR for normal adoption)
- DESIGN_SYSTEM: versioned theme/token references, component mapping and app behavior
- TD: root CSS/provider integration and any widget gaps, citing SDK contracts
- TEST_PLAN: source lint, route/theme audit and separate interaction evidence
- IMPLEMENTATION_PLAN: package access, lockfile, CI report upload and observed gate results

## Practices by activity

Agents working in any of these activities inherit the practices below through runtime work context, such as a DDx bead context digest.

## Requirements

- Use installed @skadden/ui/AGENTS.md and catalogue.json; SDK widgets and --piq-* role tokens own presentation, not copied palettes or a second UI kit; require SDK lint/skadden-audit plus separate interaction proof.
- Run SDK ESLint/Stylelint, skadden-audit and separate UX interaction tests; record versions, routes/themes, commands, exits, reports and scoped warning/exception dispositions.
- Record adoption explicitly in concerns.md. Resolve ux-radix/AppKit conflicts and Biome/Tailwind differences through project overrides before handoff.

## Design

- DESIGN.md references exact package versions from the lockfile, selected theme,
  supported appearances, token roles and component mappings. Do not copy palette
  values or override SDK tokens/widgets in app CSS.
- Load theme/font CSS before ui.css at the root and integrate ThemeProvider per
  the installed contract. Embedded views consume resolved tokens from the host.
- Read the installed catalogue before mapping components. Missing widgets need
  an explicit owner and a reviewed SDK contribution/alternative; do not assume
  Radix/shadcn is an authorized fallback.

## Implementation

- Add SDK dependencies and registry configuration without credentials; commit
  the lockfile. Starter use is optional and cannot overwrite an existing app.
- Configure skadden/no-hard-coded-values, skadden/no-foreign-ui and
  skadden/no-inline-svg plus the SDK Stylelint rule; inspect supported file
  extensions in installed guidance rather than copying a JSX-only glob into TSX.
- Run npm run lint and npm run audit using the app's concrete scripts. For a
  running app the audit command is npx skadden-audit <base-url> <route>...;
  select supported themes/appearances using installed CLI options. Install
  Chromium as required. Record startup/config errors separately from findings.
- CI uploads audit-report/report.json, index.html and screenshots. Credentials
  stay in the secret store. Treat SDK-owned warnings as owner-assigned findings,
  not a reason to modify widget internals.

## Testing and Quality Gates

- UX behavior follows ux-interaction-patterns and its STP evidence mapping.
  Audit checks token/theme adoption and contrast, not keyboard completion,
  modal focus return, duplicate submission or recovery behavior.
- Lint and audit error failures block completion. Record warning dispositions;
  stricter warning policies are project choices. No ignored finding without
  scope, rationale, owner, alternative evidence and review/removal trigger.
- Verification evidence includes installed versions, route/theme coverage,
  audit report paths, command exits and separate observed interaction results.
  HELIX catalog tests alone never establish a consumer app passed these gates.
