import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

// Representative sample: homepage, a hand-authored argument page, a how-to
// page, and one of each generated reference type. Design/a11y regressions on
// these page types are the ones worth gating.
const samples = [
  { name: 'homepage', path: '/', hasSidebar: false },
  { name: 'why/the-thesis', path: '/why/the-thesis/', hasSidebar: true },
  { name: 'use/getting-started', path: '/use/getting-started/', hasSidebar: true },
  { name: 'concern (generated)', path: '/concerns/verification/', hasSidebar: true },
  { name: 'artifact-type (generated)', path: '/artifact-types/frame/prd/', hasSidebar: true },
]

test.describe('Accessibility (axe wcag2a/wcag2aa)', () => {
  for (const s of samples) {
    test(`${s.name}: no critical/serious violations`, async ({ page }) => {
      await page.goto(s.path)
      const results = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa']).analyze()
      const blocking = results.violations.filter(
        (v) => v.impact === 'critical' || v.impact === 'serious',
      )
      const summary = blocking.map((v) => ({ id: v.id, impact: v.impact, nodes: v.nodes.length }))
      expect(blocking, `axe blocking violations:\n${JSON.stringify(summary, null, 2)}`).toEqual([])
    })
  }
})

test.describe('Heading hierarchy', () => {
  for (const s of samples) {
    test(`${s.name}: one h1, no skipped levels in content`, async ({ page }) => {
      await page.goto(s.path)
      expect(await page.locator('h1').count(), 'exactly one h1 per page').toBe(1)
      const levels = await page
        .locator('main :is(h1,h2,h3,h4,h5,h6)')
        .evaluateAll((els) => els.map((e) => Number(e.tagName[1])))
      for (let i = 1; i < levels.length; i++) {
        expect(
          levels[i] - levels[i - 1],
          `heading jumps from h${levels[i - 1]} to h${levels[i]}`,
        ).toBeLessThanOrEqual(1)
      }
    })
  }
})

test.describe('Images render', () => {
  for (const s of samples) {
    test(`${s.name}: no broken images`, async ({ page }) => {
      await page.goto(s.path)
      // Trigger any lazy-loaded images.
      await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight))
      await page.waitForLoadState('networkidle')
      const broken = await page
        .locator('img')
        .evaluateAll((imgs) =>
          (imgs as HTMLImageElement[])
            .filter((img) => img.currentSrc && img.naturalWidth === 0)
            .map((img) => img.currentSrc),
        )
      expect(broken, `broken images:\n${broken.join('\n')}`).toEqual([])
    })
  }
})

test.describe('Current-location feedback', () => {
  for (const s of samples.filter((s) => s.hasSidebar)) {
    test(`${s.name}: active nav entry marks the current page`, async ({ page }) => {
      await page.goto(s.path)
      // Hextra marks the active sidebar entry with data-active="true".
      const active = page.locator('[data-active="true"]')
      await expect(active).toHaveCount(1)
      const href = await active.locator('a').first().getAttribute('href')
      expect(href, 'active entry links to the current page').toContain(s.path)
    })
  }
})

test.describe('Responsive layout', () => {
  for (const s of samples) {
    test(`${s.name}: no horizontal overflow at mobile width`, async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 812 })
      await page.goto(s.path)
      const overflow = await page.evaluate(
        () => document.documentElement.scrollWidth - window.innerWidth,
      )
      // Allow 1px for sub-pixel rounding.
      expect(overflow, 'page should not scroll horizontally on mobile').toBeLessThanOrEqual(1)
    })
  }
})
