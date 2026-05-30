---
title: "Internationalization (ICU MessageFormat)"
slug: i18n-icu
generated: true
aliases:
  - /reference/glossary/concerns/i18n-icu
---

**Category:** Quality Attributes · **Areas:** ui, frontend

## Description

## Category
internationalization

## Areas
ui, frontend

## Components

- **Message format**: ICU MessageFormat
- **String management**: Externalized string catalogs (no hardcoded strings)
- **Direction**: Bidirectional text support (LTR and RTL)

## Constraints

- All user-facing strings must go through the i18n system
- No string concatenation for user-facing messages (use ICU plurals, select)
- Date, time, number, and currency formatting must be locale-aware
- Default locale must be explicitly declared

## When to use

Any project that serves users in multiple languages or locales, or any
project that may need localization in the future. Starting with i18n is
far cheaper than retrofitting.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- TD: ICU MessageFormat, externalized string catalogs, locale-aware formatting, declared default locale
- DESIGN_SYSTEM: bidirectional (LTR/RTL) text support

## Practices by activity

Agents working in any of these activities inherit the practices below via the bead's context digest.

## Requirements (Frame activity)

- All user stories involving user-facing text must specify i18n handling
- Target locales must be declared in the project config
- Default locale must be explicitly set

## Design

- All user-facing strings externalized to message catalogs
- Use ICU MessageFormat for plurals, gender, select, and interpolation
- No string concatenation for UI messages — use format patterns
- Design layouts for text expansion (translations are often 30-50% longer)
- RTL layout support from the start if any target locale requires it

## Implementation

- String catalog files per locale (e.g., `messages/en.json`, `messages/ja.json`)
- Use the platform's i18n library (react-intl, next-intl, gettext, etc.)
- Date/time: use `Intl.DateTimeFormat` or equivalent — never manual formatting
- Numbers/currency: use `Intl.NumberFormat` or equivalent
- No hardcoded strings in components — all text comes from catalogs
- ICU message keys should be descriptive: `user.greeting` not `msg_001`

## Testing

- Pseudo-localization testing to catch hardcoded strings and layout issues
- Verify all user-visible text renders correctly in longest target locale
- Test RTL layout if applicable
- Verify date/number formatting respects locale settings
