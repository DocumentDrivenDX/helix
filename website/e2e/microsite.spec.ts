import { test, expect } from '@playwright/test'

// Helper: target the main content area to avoid TOC/sidebar duplicates
const article = (page: any) => page.locator('article')
const searchInput = (page: any) => page.getByPlaceholder('Search...').first()
const searchResults = (page: any) =>
  page.getByLabel('Search results').filter({ has: page.locator('a[href]') }).first()
const isGlossaryIndexRoute = (route: string) => /\/reference\/glossary\/?$/.test(route)

test.describe('Homepage', () => {
  test('loads with image hero and refreshed homepage IA', async ({ page }) => {
    await test.step('navigate to homepage', async () => {
      await page.goto('/')
    })

    await test.step('verify hero content', async () => {
      await expect(page.getByRole('heading', { name: 'Product lifecycle for AI.' })).toBeVisible()
      await expect(page.getByText('Agents do better work with context they can trust.')).toBeVisible()
      await expect(page.locator('.helix-hero-image-panel img.helix-hero-image-light')).toBeVisible()
    })

    await test.step('verify adoption and proof paths', async () => {
      await expect(page.getByRole('link', { name: 'Start with HELIX' })).toBeVisible()
      await expect(page.getByRole('link', { name: 'Browse the catalog' })).toBeVisible()
    })

    await test.step('verify refreshed IA sections', async () => {
      await expect(page.getByRole('heading', { name: 'How it works' })).toBeVisible()
      await expect(page.getByRole('heading', { name: 'Artifact spine' })).toBeVisible()
      await expect(page.getByRole('heading', { name: 'Use more than one flow scope' })).toBeVisible()
      await expect(page.getByRole('heading', { name: 'Use HELIX where your team already works' })).toBeVisible()
      await expect(page.getByRole('heading', { name: 'Inspect the foundations' })).toBeVisible()
    })

    await test.step('verify the hero image renders and worked example is firewalled', async () => {
      await expect(page.locator('.helix-hero-image-panel')).toHaveCount(1)
      await expect(page.getByText('HELIX example docs').first()).toBeVisible()
      await expect(page.locator('.helix-graph-visual svg')).toHaveCount(0)
    })

    await test.step('capture full-page screenshot', async () => {
      // Asciinema embed loads async, allow some pixel jitter
      await expect(page).toHaveScreenshot('homepage.png', {
        fullPage: true,
        maxDiffPixelRatio: 0.03,
      })
    })
  })
})

test.describe('Why HELIX', () => {
  test('section landing has the four subpages', async ({ page }) => {
    await page.goto('/why/')
    await expect(article(page).getByRole('link', { name: /The Problem/ })).toBeVisible()
    await expect(article(page).getByRole('link', { name: /The Thesis/ })).toBeVisible()
    await expect(article(page).getByRole('link', { name: /Principles/ })).toBeVisible()
    await expect(article(page).getByRole('link', { name: /Who it's for/ })).toBeVisible()
  })

  test('principles page covers all eight', async ({ page }) => {
    await page.goto('/why/principles/')
    await expect(page.getByRole('heading', { name: /1\.\s+Planning and execution/ })).toBeVisible()
    await expect(page.getByRole('heading', { name: /3\.\s+The artifact authority hierarchy/ })).toBeVisible()
    await expect(page.getByRole('heading', { name: /6\.\s+Autonomy is supervised/ })).toBeVisible()
    await expect(page.getByRole('heading', { name: /8\.\s+Least power wins/ })).toBeVisible()
  })

  test('thesis page describes the document method', async ({ page }) => {
    await page.goto('/why/the-thesis/')
    await expect(article(page).getByText(/document method/i).first()).toBeVisible()
    await expect(article(page).getByText(/seven activities/i).first()).toBeVisible()
  })
})

test.describe('Artifacts', () => {
  test('index lists artifacts grouped by activity', async ({ page }) => {
    await page.goto('/artifacts/')
    await expect(page.getByText(/Generated examples from the HELIX project.s own HELIX documents/)).toBeVisible()
    await expect(page.getByText(/artifact-type catalog/).first()).toBeVisible()
    // Artifacts are grouped under plain activity-name headings (h2)
    await expect(page.getByRole('heading', { name: /^Discover/ })).toBeVisible()
    await expect(page.getByRole('heading', { name: /^Frame/ })).toBeVisible()
    await expect(page.getByRole('heading', { name: /^Iterate/ })).toBeVisible()
  })

  test('generated artifact wrappers explain source and examples', async ({ page }) => {
    await page.goto('/artifacts/prd/')
    await expect(page.getByText(/Example from HELIX.s own docs/)).toBeVisible()
    await expect(page.getByText(/Source identity/)).toBeVisible()

    await page.goto('/artifacts/adr/')
    await expect(page.getByText(/Examples from HELIX.s own docs/)).toBeVisible()
  })

  test('artifact type pages render generation prompt and template', async ({ page }) => {
    await page.goto('/artifact-types/frame/prd/')
    await expect(page.getByRole('heading', { name: /Purpose/ }).first()).toBeVisible()
    await expect(page.getByRole('heading', { name: /Authoring guidance/ })).toBeVisible()
    // Prompt and template are wrapped in <details> with summary toggles
    await expect(article(page).getByText(/Show the full generation prompt/i)).toBeVisible()
    await expect(article(page).getByText(/Show the template structure/i)).toBeVisible()
  })

  test('artifact type leaf pages keep parent activity navigation', async ({ page }) => {
    await page.setViewportSize({ width: 1800, height: 1000 })
    const sidebar = page.locator('aside').first()
    const artifactTypeLink = (path: string) => sidebar.locator(`a[href$="${path}"]`)

    await page.goto('/artifact-types/frame/prd/')
    await expect(artifactTypeLink('/artifact-types/frame/')).toBeVisible()
    await expect(artifactTypeLink('/artifact-types/frame/prd/')).toBeVisible()
    await expect(artifactTypeLink('/artifact-types/frame/feature-specification/')).toBeVisible()
    await expect(artifactTypeLink('/artifact-types/frame/pr-faq/')).toBeVisible()
    await expect(artifactTypeLink('/artifact-types/frame/prd/')).toHaveClass(
      /hextra-sidebar-active-item/,
    )
    await expect(
      artifactTypeLink('/artifact-types/frame/prd/')
        .locator('xpath=ancestor::li[1]')
        .locator('a[href^="#"]')
        .first(),
    ).toBeHidden()

    await page.goto('/artifact-types/frame/pr-faq/')
    await expect(artifactTypeLink('/artifact-types/frame/')).toBeVisible()
    await expect(artifactTypeLink('/artifact-types/frame/prd/')).toBeVisible()
    await expect(artifactTypeLink('/artifact-types/frame/feature-specification/')).toBeVisible()
    await expect(artifactTypeLink('/artifact-types/frame/pr-faq/')).toBeVisible()
    await expect(artifactTypeLink('/artifact-types/frame/pr-faq/')).toHaveClass(
      /hextra-sidebar-active-item/,
    )
    await expect(
      artifactTypeLink('/artifact-types/frame/pr-faq/')
        .locator('xpath=ancestor::li[1]')
        .locator('a[href^="#"]')
        .first(),
    ).toBeHidden()
  })
})

test.describe('Concerns', () => {
  test('index lists concerns by category', async ({ page }) => {
    await page.goto('/concerns/')
    await expect(page.getByRole('heading', { name: 'Tech Stack' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Quality Attributes' })).toBeVisible()
    // Sample concern cards
    await expect(article(page).getByRole('link', { name: /TypeScript/ })).toBeVisible()
    await expect(article(page).getByRole('link', { name: /a11y|Accessibility/i })).toBeVisible()
  })

  test('concern detail page shows description and practices', async ({ page }) => {
    await page.goto('/concerns/typescript-bun/')
    await expect(page.getByRole('heading', { name: /Description/ })).toBeVisible()
    await expect(page.getByRole('heading', { name: /Practices by activity/ })).toBeVisible()
    await expect(article(page).getByText(/Bun 1\.x/)).toBeVisible()
  })
})

test.describe('Use HELIX', () => {
  test('section landing introduces the how-to layer', async ({ page }) => {
    await page.goto('/use/')
    await expect(article(page).getByRole('link', { name: /Getting Started/ })).toBeVisible()
    await expect(article(page).getByRole('link', { name: /Multiple Flows and Microsites/ })).toBeVisible()
    await expect(article(page).getByRole('link', { name: /Artifact Types/ })).toBeVisible()
    await expect(article(page).getByText(/Artifact types are reusable HELIX document patterns/)).toBeVisible()
    await expect(article(page).getByText(/HELIX Example Docs/)).toBeVisible()
  })

  test('Getting Started page has installation instructions', async ({ page }) => {
    await page.goto('/use/getting-started/')
    await expect(article(page).getByText(/Start with documents, not tooling/)).toBeVisible()
    await expect(article(page).getByText('ddx install helix')).toBeVisible()
    await expect(
      article(page).getByText('DDx is the reference runtime integration for HELIX'),
    ).toBeVisible()
  })

  test('Workflow page explains activities', async ({ page }) => {
    await page.goto('/use/workflow/')
    await expect(page.getByRole('heading', { name: 'Workflow' }).first()).toBeVisible()
  })

  test('Multiple flows page explains microsite scope without sibling public skills', async ({
    page,
  }) => {
    await page.goto('/use/multiple-flows/', { waitUntil: 'domcontentloaded' })
    await expect(page.getByRole('heading', { name: 'Multiple Flows and Microsites' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Microsite-docs Template' })).toBeVisible()
    await expect(article(page).locator('pre').getByText('kind: helix')).toHaveCount(2)
    await expect(article(page).getByText('They are not separate domain-specific skills')).toBeVisible()
  })
})

test.describe('Reference', () => {
  test('section landing lists subsections', async ({ page }) => {
    await page.goto('/reference/')
    await expect(article(page).getByRole('link', { name: /Glossary/ })).toBeVisible()
    await expect(article(page).getByRole('link', { name: /Skills/ })).toBeVisible()
    await expect(article(page).getByRole('link', { name: /Demos/ })).toBeVisible()
  })

  test('Skills page lists agent skills', async ({ page }) => {
    await page.goto('/reference/skills/')
    await expect(page.getByRole('heading', { name: 'Skills' }).first()).toBeVisible()
  })

  test('Demos page shows reels', async ({ page }) => {
    await page.goto('/reference/demos/')
    await expect(article(page).getByText('adopt: Drop HELIX into an existing project')).toBeVisible()
    await expect(
      article(page).getByText('concerns: Catch technology drift before it ships'),
    ).toBeVisible()
  })

  test.describe('Glossary', () => {
    test('index lists categories (without Artifacts/Concerns — those are top-level now)', async ({
      page,
    }) => {
      await page.goto('/reference/glossary/')
      await expect(article(page).getByRole('link', { name: /Activities/ })).toBeVisible()
      await expect(article(page).getByRole('link', { name: /Actions/ })).toBeVisible()
      await expect(article(page).getByRole('link', { name: /Concepts/ })).toBeVisible()
      await expect(article(page).getByRole('link', { name: /Tracker/ })).toBeVisible()
    })

    test('activities page covers all seven activities with artifact links', async ({ page }) => {
      await page.goto('/reference/glossary/activities/')
      await expect(page.getByRole('heading', { name: /^Discover/ })).toBeVisible()
      await expect(page.getByRole('heading', { name: /^Frame/ })).toBeVisible()
      await expect(page.getByRole('heading', { name: /^Build/ })).toBeVisible()
      await expect(page.getByRole('heading', { name: /^Iterate/ })).toBeVisible()
      // Artifact links inside activity tables
      await expect(article(page).getByRole('link', { name: 'PRD' })).toBeVisible()
      await expect(article(page).getByRole('link', { name: /ADR/ })).toBeVisible()
    })

    test('concepts page covers core ideas', async ({ page }) => {
      await page.goto('/reference/glossary/concepts/')
      await expect(page.getByRole('heading', { name: 'Artifact Authority Hierarchy' })).toBeVisible()
      await expect(page.getByRole('heading', { name: 'Runtime Work Context' })).toBeVisible()
    })

    test('tracker page documents DDx beads as reference-runtime concepts', async ({ page }) => {
      await page.goto('/reference/glossary/tracker/')
      await expect(page.getByRole('heading', { name: 'DDx Tracker' }).first()).toBeVisible()
      await expect(article(page).getByText('ddx bead').first()).toBeVisible()
      await expect(article(page).getByRole('heading', { name: 'Activity Labels' })).toBeVisible()
    })
  })
})

test.describe('Backward-compat aliases', () => {
  // Hugo aliases are typically HTML-meta redirects (200 with refresh) or 3xx
  const acceptable = [200, 301, 302, 308]

  test('legacy /docs/* URLs still resolve', async ({ page }) => {
    for (const url of [
      '/docs/',
      '/docs/background/',
      '/docs/getting-started/',
      '/docs/workflow/',
      '/docs/skills/',
      '/docs/glossary/',
      '/docs/glossary/activities/',
      '/docs/demos/',
    ]) {
      const response = await page.request.get(url)
      expect(acceptable, `${url} should be reachable`).toContain(response.status())
    }
  })
})

test.describe('Navigation Workflows', () => {
  test('homepage → Start with HELIX → use/getting-started', async ({ page }) => {
    await page.goto('/')
    await page.getByRole('link', { name: 'Start with HELIX' }).click()
    await expect(page).toHaveURL(/\/use\/getting-started/)
  })

  test('top nav: Why / Use / Types / Concerns / Platforms / Reference', async ({ page }) => {
    await page.goto('/')
    const nav = page.getByRole('navigation').first()

    await test.step('Why HELIX', async () => {
      await nav.getByRole('link', { name: 'Why HELIX' }).first().click()
      await expect(page).toHaveURL(/\/why\/?$/)
    })

    await test.step('Use HELIX', async () => {
      await page.goto('/')
      await nav.getByRole('link', { name: 'Use HELIX' }).first().click()
      await expect(page).toHaveURL(/\/use\/?$/)
    })

    await test.step('Types', async () => {
      await page.goto('/')
      await nav.getByRole('link', { name: 'Types' }).first().click()
      await expect(page).toHaveURL(/\/artifact-types\/?$/)
    })

    await test.step('Concerns', async () => {
      await page.goto('/')
      await nav.getByRole('link', { name: 'Concerns' }).first().click()
      await expect(page).toHaveURL(/\/concerns\/?$/)
    })

    await test.step('Platforms', async () => {
      await page.goto('/')
      await nav.getByRole('link', { name: 'Platforms' }).first().click()
      await expect(page).toHaveURL(/\/platforms\/?$/)
    })

    await test.step('Reference', async () => {
      await page.goto('/')
      await nav.getByRole('link', { name: 'Reference' }).first().click()
      await expect(page).toHaveURL(/\/reference\/?$/)
    })
  })

  test('artifacts → individual artifact drill-down', async ({ page }) => {
    await page.goto('/artifacts/')
    await article(page).getByRole('link', { name: /^Product Requirements Document/ }).first().click()
    await expect(page).toHaveURL(/\/artifacts\/prd\/?$/)
    await expect(
      page.getByRole('heading', { name: 'Product Requirements Document' }).first(),
    ).toBeVisible()
  })
})

test.describe('Search Workflows', () => {
  test('search index points glossary queries at /reference/glossary/', async ({ page }) => {
    const response = await page.request.get('/en.search-data.json')
    expect(response.ok()).toBeTruthy()

    const searchIndex = (await response.json()) as Record<string, unknown>
    const glossaryRoutes = Object.keys(searchIndex).filter(route => route.endsWith('/glossary/'))

    // Exactly one glossary index, at the new location
    expect(glossaryRoutes.filter(isGlossaryIndexRoute)).toHaveLength(1)
    expect(glossaryRoutes.filter(route => !isGlossaryIndexRoute(route))).toEqual([])
  })

  test('search opens from menu and surfaces glossary results', async ({ page }) => {
    await page.setViewportSize({ width: 700, height: 900 })
    await page.goto('/use/')

    await page.getByRole('button', { name: 'Menu' }).click()
    await expect(searchInput(page)).toBeVisible()
    await searchInput(page).click()
    await expect(searchInput(page)).toBeFocused()

    await searchInput(page).pressSequentially('glossary')
    await expect(searchResults(page)).toBeVisible()

    const result = searchResults(page).locator('a[href*="/reference/glossary"]').first()
    await expect(result).toBeVisible()
    await result.click()
    await expect(page).toHaveURL(/\/reference\/glossary(\/|#|$)/)
  })
})
