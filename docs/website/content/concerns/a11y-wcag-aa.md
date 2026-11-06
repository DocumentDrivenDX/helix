---
title: "Accessibility (WCAG 2.2 AA)"
slug: a11y-wcag-aa
generated: true
aliases:
  - /reference/glossary/concerns/a11y-wcag-aa
---

**Category:** Quality Attributes · **Areas:** ui, frontend

## Description

## Category
accessibility

## Areas
ui, frontend

## Components

- **Standard**: WCAG 2.2 Level AA
- **Testing**: axe-core automated checks + manual screen reader testing
- **Scope**: All user-facing interfaces
- **Boundary**: `a11y-wcag-aa` owns the accessibility checks; `ux-radix` owns the widgets.

## Constraints

- All interactive elements must be keyboard-navigable
- Color contrast must meet AA ratios (4.5:1 text, 3:1 large text)
- All non-decorative images must have alt text
- Form inputs must have associated labels
- Dynamic content must manage focus appropriately

## When to use

Any project with user-facing web or mobile interfaces. Required for
public-sector, healthcare, finance, and education. Recommended for all
consumer-facing products.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- DESIGN_SYSTEM: keyboard-navigable controls, AA contrast ratios, focus management, labeled inputs; states the WCAG 2.2 AA target, axe-core, and manual screen-reader testing
- TEST_PLAN: axe-core automated checks + manual screen-reader passes

## Practices by activity

Agents working in any of these activities inherit the practices below through runtime work context, such as a DDx bead context digest.

## Requirements (Frame activity)

- All user stories involving UI must include a11y acceptance criteria
- WCAG 2.2 AA is the minimum compliance target
- Accessibility is a requirement, not a nice-to-have

## Design

- All interactive components must be keyboard-navigable
- Color contrast ratios must meet AA (4.5:1 for text, 3:1 for large text)
- ARIA attributes required for custom components
- Semantic heading hierarchy required (h1 > h2 > h3, no skips)
- Focus order must follow visual reading order
- Touch targets minimum 24x24 CSS pixels (SC 2.5.8, AA); 44x44 is the AAA value (SC 2.5.5)

## Implementation

- Use semantic HTML elements over divs with roles
- All images require alt text (decorative images use `alt=""`)
- Form inputs require associated `<label>` elements
- Focus management for modals, drawers, and dynamic content
- Skip navigation link for keyboard users
- `aria-live` regions for dynamic status updates
- No `tabindex` values greater than 0

## Testing

- axe-core in CI for automated a11y checks
- Screen reader testing for critical user flows (VoiceOver, NVDA)
- Keyboard-only navigation testing for all interactive flows
- Color contrast validation in design review
- Test with browser zoom at 200%
