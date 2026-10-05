# Practices: databricks-appkit-ui

## Requirements (Frame activity)

- Confirm the app is hosted on Databricks Apps with a React SPA and a non-Node backend; an AppKit TypeScript project follows Databricks' template instead.
- Record the AppKit UI standalone spike as a `tech-spike` and treat UI design that depends on it as provisional until it reports.
- List the data views (charts, tables) the product needs, so the spike checks those components in data mode.
- State whether the product needs both light and dark themes at launch; tokens are maintained for both either way.
- Identify any brand colors that must override AppKit tokens.

## Design

- Choose `@databricks/appkit-ui` at an exact version as the component library; record it in the ADR with the spike result.
- Feed charts and data components in data mode from the server-state layer that calls the project's `/api/*` routes.
- Map each needed widget to an AppKit UI component first; only a gap gets a copied shadcn component themed with AppKit tokens.
- Define token overrides as CSS variables for light and dark together; chart series use `--chart-1` to `--chart-5`.
- Apply `ux-radix` interaction patterns (search, edit, navigation, selection, overlays) to AppKit UI components unchanged.

## Implementation

- Add `@databricks/appkit-ui` with an exact version and commit the lockfile; never add `@databricks/appkit`.
- Import `@databricks/appkit-ui/styles.css` once at the app root, before the app's own styles.
- Put token overrides in one stylesheet, with a light block and a dark block for every overridden variable.
- Pass data to data components as props; do not call AppKit query or stream hooks unless the spike proved them against the project's API.
- Reference tokens in chart options and component classes; no literal colors.
- Keep the Radix keyboard and focus behavior of AppKit UI components intact.

## Testing / Verification

- Run the standalone spike and record bundle size, Tailwind 4 setup, any calls to `/api/<plugin>` or `/health`, and theme switching.
- Component tests (per `react-vite`) cover data components rendering empty, loading, error, and populated data.
- Check affected screens in both light and dark themes for every change that touches tokens or an AppKit UI upgrade.
- Verify keyboard and focus behavior per `ux-radix` on screens built from AppKit UI components.
- Verify in the browser network panel or e2e that the deployed app calls no AppKit server routes.

## Quality Gates

- `package.json` pins `@databricks/appkit-ui` exactly and does not list `@databricks/appkit`.
- The standalone spike result is recorded and cited by the ADR.
- No second component library and no literal colors in components or chart options.
- Every token override exists for both light and dark themes.
- An AppKit UI upgrade lands as its own reviewed change with both themes checked.
- Component code stays under the `code-shape-ceilings` complexity, function-length, and file-size ceilings.
