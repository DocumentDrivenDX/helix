# Practices: TypeScript + Bun

## TypeScript Config

- `strict: true`
- `noUncheckedIndexedAccess: true`
- `exactOptionalPropertyTypes: true`
- `verbatimModuleSyntax: true`
- `noEmit: true` (Bun handles execution directly)

## Linting & Formatting

- Linter: ESLint with `@typescript-eslint/strict-type-checked`
- Formatter: Biome (not Prettier)
- Run: `bunx biome check --write .`

## Testing

- Framework: `bun:test` (built-in, not Jest or Vitest)
- Use `Bun.mock()` for module mocking
- Fake data with `@faker-js/faker`, not static fixtures
- Prefer stubs to mocks — verify behavior, not call sequences

## Imports & Modules

- Use Bun-native imports, not Node compat layer
- Prefer explicit file extensions in imports
- Use `Bun.file()` for file I/O, not `fs`

## Dependencies

- Add with `bun add`, not `npm install`
- Prefer zero-dependency or Bun-native packages
- Lock file: `bun.lockb` (binary, committed to git)
