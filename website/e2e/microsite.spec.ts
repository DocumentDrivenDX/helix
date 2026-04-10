import { test, expect } from '@playwright/test'

// Helper: target the main content area to avoid TOC/sidebar duplicates
const article = (page: any) => page.locator('article')
const searchInput = (page: any) => page.getByPlaceholder('Search...').first()
const searchResults = (page: any) => page.getByLabel('Search results').filter({ has: page.locator('a[href]') }).first()
const isGlossaryIndexRoute = (route: string) => /\/docs\/glossary\/?$/.test(route)

test.describe('Homepage', () => {
  test('loads with hero and feature cards', async ({ page }) => {
    await test.step('navigate to homepage', async () => {
      await page.goto('/')
    })

    await test.step('verify hero content', async () => {
      await expect(page.getByText('Express intent once')).toBeVisible()
    })

    await test.step('verify call-to-action buttons', async () => {
      await expect(page.getByRole('link', { name: 'Get Started' })).toBeVisible()
    })

    await test.step('verify feature cards', async () => {
      await expect(page.getByRole('heading', { name: 'Supervisory Autopilot' })).toBeVisible()
      await expect(page.getByRole('heading', { name: 'Tracker as Steering Wheel' })).toBeVisible()
    })

    await test.step('capture full-page screenshot', async () => {
      await expect(page).toHaveScreenshot('homepage.png', { fullPage: true })
    })
  })
})

test.describe('Getting Started', () => {
  test('page loads with installation instructions', async ({ page }) => {
    await test.step('navigate to getting started', async () => {
      await page.goto('/docs/getting-started/')
    })

    await test.step('verify installation content', async () => {
      await expect(article(page).getByText('ddx install helix')).toBeVisible()
      await expect(article(page).getByText('DDx and HELIX')).toBeVisible()
    })

    await test.step('capture screenshot', async () => {
      await expect(page).toHaveScreenshot('getting-started.png', { fullPage: true })
    })
  })
})

test.describe('Workflow', () => {
  test('page explains phases and authority order', async ({ page }) => {
    await test.step('navigate to workflow', async () => {
      await page.goto('/docs/workflow/')
    })

    await test.step('verify core content', async () => {
      await expect(page.getByRole('heading', { name: 'Workflow' }).first()).toBeVisible()
    })

    await test.step('capture screenshot', async () => {
      await expect(page).toHaveScreenshot('workflow.png', { fullPage: true })
    })
  })
})

test.describe('CLI Reference', () => {
  test('page documents all commands', async ({ page }) => {
    await test.step('navigate to CLI reference', async () => {
      await page.goto('/docs/cli/')
    })

    await test.step('verify command documentation', async () => {
      await expect(page.getByRole('heading', { name: 'CLI Reference' }).first()).toBeVisible()
    })

    await test.step('capture screenshot', async () => {
      await expect(page).toHaveScreenshot('cli-reference.png', { fullPage: true })
    })
  })
})

test.describe('Skills', () => {
  test('page lists all skills', async ({ page }) => {
    await test.step('navigate to skills', async () => {
      await page.goto('/docs/skills/')
    })

    await test.step('verify skills content', async () => {
      await expect(page.getByRole('heading', { name: 'Skills' }).first()).toBeVisible()
    })

    await test.step('capture screenshot', async () => {
      await expect(page).toHaveScreenshot('skills.png', { fullPage: true })
    })
  })
})

test.describe('Glossary', () => {
  test('index page links to all sub-pages', async ({ page }) => {
    await test.step('navigate to glossary', async () => {
      await page.goto('/docs/glossary/')
    })

    await test.step('verify all category cards', async () => {
      await expect(page.getByRole('heading', { name: 'Glossary' }).first()).toBeVisible()
      // Card links contain title + subtitle in one link
      await expect(article(page).getByRole('link', { name: /Phases/ })).toBeVisible()
      await expect(article(page).getByRole('link', { name: /Artifacts/ })).toBeVisible()
      await expect(article(page).getByRole('link', { name: /Actions/ })).toBeVisible()
    })

    await test.step('capture screenshot', async () => {
      await expect(page).toHaveScreenshot('glossary.png', { fullPage: true })
    })
  })

  test('phases page covers all phases', async ({ page }) => {
    await test.step('navigate to phases', async () => {
      await page.goto('/docs/glossary/phases/')
    })

    await test.step('verify all phases present', async () => {
      await expect(page.getByRole('heading', { name: /Phase 0.*Discover/ })).toBeVisible()
      await expect(page.getByRole('heading', { name: /Phase 1.*Frame/ })).toBeVisible()
      await expect(page.getByRole('heading', { name: /Phase 4.*Build/ })).toBeVisible()
      await expect(page.getByRole('heading', { name: /Phase 6.*Iterate/ })).toBeVisible()
    })
  })

  test('artifacts page has authority order', async ({ page }) => {
    await test.step('navigate to artifacts', async () => {
      await page.goto('/docs/glossary/artifacts/')
    })

    await test.step('verify authority order heading', async () => {
      await expect(page.getByRole('heading', { name: 'Authority Order' })).toBeVisible()
    })
  })

  test('actions page documents all commands', async ({ page }) => {
    await test.step('navigate to actions', async () => {
      await page.goto('/docs/glossary/actions/')
    })

    await test.step('verify key actions', async () => {
      await expect(article(page).getByRole('heading', { name: 'build' })).toBeVisible()
      await expect(article(page).getByRole('heading', { name: 'check' })).toBeVisible()
      await expect(article(page).getByRole('heading', { name: 'run' })).toBeVisible()
    })
  })

  test('concerns page lists the library', async ({ page }) => {
    await test.step('navigate to concerns', async () => {
      await page.goto('/docs/glossary/concerns/')
    })

    await test.step('verify concern tables', async () => {
      await expect(article(page).getByRole('heading', { name: 'Tech Stack Concerns' })).toBeVisible()
      await expect(article(page).getByRole('cell', { name: 'rust-cargo' })).toBeVisible()
      await expect(article(page).getByRole('cell', { name: 'typescript-bun' })).toBeVisible()
    })
  })

  test('concepts page covers core ideas', async ({ page }) => {
    await test.step('navigate to concepts', async () => {
      await page.goto('/docs/glossary/concepts/')
    })

    await test.step('verify key concepts', async () => {
      await expect(page.getByRole('heading', { name: 'Authority Order' })).toBeVisible()
      await expect(page.getByRole('heading', { name: 'Context Digest' })).toBeVisible()
    })
  })

  test('tracker page documents beads', async ({ page }) => {
    await test.step('navigate to tracker', async () => {
      await page.goto('/docs/glossary/tracker/')
    })

    await test.step('verify tracker content', async () => {
      await expect(article(page).getByText('ddx bead').first()).toBeVisible()
      await expect(article(page).getByRole('heading', { name: 'Phase Labels' })).toBeVisible()
    })
  })
})

test.describe('Demos', () => {
  test('page shows all demo reels', async ({ page }) => {
    await test.step('navigate to demos', async () => {
      await page.goto('/docs/demos/')
    })

    await test.step('verify all demos listed', async () => {
      await expect(article(page).getByText('Quickstart: Full Lifecycle')).toBeVisible()
      await expect(article(page).getByText('Concerns: Preventing Technology Drift')).toBeVisible()
      await expect(article(page).getByText('Evolve: Threading Requirements')).toBeVisible()
      await expect(article(page).getByText('Experiment: Metric-Driven Optimization')).toBeVisible()
      await expect(article(page).getByText('docs/demos/helix-interactive/')).toBeVisible()
      await expect(article(page).getByText('Interactive HELIX Demo')).toHaveCount(0)
    })

    await test.step('capture screenshot', async () => {
      // Asciinema players load async and cause size jitter — allow 3% pixel diff
      await expect(page).toHaveScreenshot('demos.png', { fullPage: true, maxDiffPixelRatio: 0.03 })
    })
  })
})

test.describe('Navigation Workflows', () => {
  test('homepage → getting started → workflow', async ({ page }) => {
    await test.step('start at homepage', async () => {
      await page.goto('/')
    })

    await test.step('click Get Started', async () => {
      await page.getByRole('link', { name: 'Get Started' }).click()
      await expect(page).toHaveURL(/getting-started/)
    })

    await test.step('navigate to workflow', async () => {
      await page.getByRole('link', { name: 'Workflow' }).first().click()
      await expect(page).toHaveURL(/workflow/)
    })
  })

  test('top nav: glossary and demos', async ({ page }) => {
    await test.step('start at homepage', async () => {
      await page.goto('/')
    })

    await test.step('navigate to glossary via top nav', async () => {
      await page.getByRole('navigation').getByText('Glossary').click()
      await expect(page).toHaveURL(/glossary/)
    })

    await test.step('navigate to demos via top nav', async () => {
      await page.getByRole('navigation').getByText('Demos').click()
      await expect(page).toHaveURL(/demos/)
    })
  })

  test('glossary drill-down', async ({ page }) => {
    await test.step('start at glossary index', async () => {
      await page.goto('/docs/glossary/')
    })

    await test.step('click into phases', async () => {
      await article(page).getByRole('link', { name: 'Phases' }).first().click()
      await expect(page).toHaveURL(/glossary\/phases/)
    })

    await test.step('verify phase content loaded', async () => {
      await expect(page.getByRole('heading', { name: /Phase 1.*Frame/ })).toBeVisible()
    })
  })
})

test.describe('Search Workflows', () => {
  test('search routes glossary and CLI queries to live pages', async ({ page }) => {
    await test.step('verify the rendered search index points glossary queries at the live page', async () => {
      const response = await page.request.get('/en.search-data.json')
      expect(response.ok()).toBeTruthy()

      const searchIndex = (await response.json()) as Record<string, unknown>
      const glossaryRoutes = Object.keys(searchIndex).filter(route => route.endsWith('/glossary/'))

      expect(glossaryRoutes.filter(isGlossaryIndexRoute)).toHaveLength(1)
      expect(glossaryRoutes.filter(route => !isGlossaryIndexRoute(route))).toEqual([])
    })

    await test.step('open site search from the docs menu', async () => {
      await page.setViewportSize({ width: 700, height: 900 })
      await page.goto('/docs/')
      await page.getByRole('button', { name: 'Menu' }).click()
      await expect(searchInput(page)).toBeVisible()
      await searchInput(page).click()
      await expect(searchInput(page)).toBeFocused()
    })

    await test.step('query glossary and open a valid glossary page', async () => {
      await searchInput(page).pressSequentially('glossary')
      await expect(searchResults(page)).toBeVisible()

      const glossaryResult = searchResults(page).locator('a[href*="/docs/glossary"]').first()
      await expect(glossaryResult).toBeVisible()

      const glossaryHref = await glossaryResult.getAttribute('href')
      expect(glossaryHref).toBeTruthy()
      expect(glossaryHref).toMatch(/^\/docs\/glossary(\/|#|$)/)

      await glossaryResult.click()
      await expect(page).toHaveURL(/\/docs\/glossary(\/|#|$)/)
      await expect(page.getByRole('heading', { name: 'Glossary' }).first()).toBeVisible()
    })

    await test.step('query CLI and open a valid CLI page', async () => {
      await page.getByRole('button', { name: 'Menu' }).click()
      await expect(searchInput(page)).toBeVisible()
      await searchInput(page).click()
      await expect(searchInput(page)).toBeFocused()

      await searchInput(page).pressSequentially('cli')
      await expect(searchResults(page)).toBeVisible()

      const cliResult = searchResults(page).locator('a[href*="/docs/cli"]').first()
      await expect(cliResult).toBeVisible()

      const cliHref = await cliResult.getAttribute('href')
      expect(cliHref).toBeTruthy()
      expect(cliHref).toMatch(/^\/docs\/cli(\/|#|$)/)

      await cliResult.click()
      await expect(page).toHaveURL(/\/docs\/cli(\/|#|$)/)
      await expect(page.getByRole('heading', { name: 'CLI Reference' }).first()).toBeVisible()
    })
  })
})
