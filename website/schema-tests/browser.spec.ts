import { test, expect } from '@playwright/test'
import { createHash } from 'node:crypto'

test('a published design opens its UMF definition under /helix/', async ({ page, request }) => {
  const errors: string[] = []
  const failed: string[] = []
  page.on('response', response => { if (response.status() >= 400) failed.push(response.url()) })
  await page.goto('artifacts/design-umf-schemas/')
  await page.getByRole('link', { name: 'Explore schema: Design schema reference' }).click()
  await expect(page).toHaveURL(/\/helix\/schemas\/explorer.html#schema=helix.schema-reference%401.0.0/)
  // Check the schema host and iframe after leaving the site's navigation.
  // Hextra's existing hidden-search mousedown handler is outside this integration.
  page.on('pageerror', error => errors.push(error.stack || error.message))
  const browser = page.frameLocator('#schema-view iframe')
  await expect(browser.getByRole('heading', { name: 'Schema Reference', exact: true })).toBeVisible()
  await expect(browser.getByText('publishing / SchemaReference · /modules/0/elements/0')).toBeVisible()
  await expect(page.locator('#status')).toBeEmpty()
  expect(errors).toEqual([])
  expect(failed).toEqual([])
  await page.screenshot({ path: 'test-results/schema-definition.png', fullPage: true })
  await browser.getByRole('link', { name: 'Overview', exact: true }).click()
  await expect(page).not.toHaveURL(/definition=/)
  await browser.getByRole('link', { name: 'SchemaReference', exact: true }).click()
  await expect(page).toHaveURL(/definition=%5B%22publishing%22%2C%22SchemaReference%22%5D/)

  const manifest = await (await request.get('schemas/manifest.json')).json()
  const entry = manifest.schemas.find((e: {id: string}) => e.id === 'helix.schema-reference@1.0.0')
  const source = await request.get(`schemas/${entry.url}`)
  expect(source.ok()).toBeTruthy()
  expect(createHash('sha256').update(await source.body()).digest('hex')).toBe(entry.sha256)
  expect(entry.owners).toContain('docs/helix/02-design/design-umf-schemas.md')

  await page.goto('schemas/')
  await expect(page.getByRole('link', { name: 'Download source' })).toBeVisible()
  const embedded = page.frameLocator('iframe[title="UMF design schema browser"]')
    .frameLocator('#schema-view iframe')
  await expect(embedded.getByRole('heading', { name: 'Explore the shape and the meaning.' })).toBeVisible()
  expect(errors).toEqual([])
  expect(failed).toEqual([])
  await page.screenshot({ path: 'test-results/schema-index.png', fullPage: true })
  await page.setViewportSize({ width: 390, height: 844 })
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBeTruthy()
  await page.goto('schemas/explorer.html#schema=helix.schema-reference%401.0.0&definition=%5B%22publishing%22%2C%22SchemaReference%22%5D')
  await expect(page.frameLocator('#schema-view iframe').getByRole('heading', { name: 'Schema Reference', exact: true })).toBeVisible()
  await page.screenshot({ path: 'test-results/schema-mobile.png', fullPage: true })
})
