# Concern: AI Design System SDK

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
