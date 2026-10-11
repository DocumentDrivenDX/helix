# Practices: Packaged Design System

## Requirements

- Use the available applicable npm design system and installed-version documentation; its components/tokens own presentation. Run supplied quality checks (or project-defined checks when absent) plus separate UX interaction proof.
- Record actual package versions, documented component/token mappings, concrete check commands/reports and scoped findings; no specific client, vendor, package API or audit tool is prescribed.
- Record availability and compatibility evidence before adoption. Resolve competing component owners and styling/toolchain defaults in project overrides before handoff.

## Design

- DESIGN.md names the installed package versions, supported themes/appearances,
  token roles and component mappings verified in package documentation. It
  references externally owned values rather than duplicating them.
- Follow documented stylesheet/provider/theme integration. If a host supplies
  resolved tokens or owns branding, record that actual contract. Do not invent
  a theme switcher, mandatory dark mode, bundled fonts or provider semantics.
- Missing widgets/tokens need a recorded owner and reviewed contribution,
  extension or accessible alternative. An npm package does not prove fit for
  every interaction pattern.

## Implementation

- Add the selected packages and commit the lockfile. Registry access uses the
  project's secret handling; never put credentials in tracked configuration.
  A starter is optional and cannot overwrite an existing app.
- Use exported APIs and documented customization points, not unsupported widget
  internals. Apply package-supplied quality tools where available and relevant;
  adapt framework lint/styling defaults explicitly instead of bypassing them.
- If the package supplies no lint/audit tooling, the project defines concrete
  presentation/accessibility checks and evidence commands in the test plan.
  CI retains the reports actually produced; no fixed command or output path.

## Testing and Quality Gates

- Apply ux-interaction-patterns and the STP UX Coverage map. Presentation or
  accessibility audits do not replace actual keyboard, focus, duplicate-action,
  validation and recovery tests.
- The project's declared checks and acceptance criteria govern completion.
  Record command exits, affected routes and supported themes/appearances,
  actual report paths, finding ownership and reviewed exception dispositions.
- No ignored finding without scope, rationale, owner, alternative observed
  evidence and review/removal trigger. HELIX catalog tests establish no
  consumer-app runtime result.
