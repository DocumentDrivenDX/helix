# Practices: AI Design System SDK

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
