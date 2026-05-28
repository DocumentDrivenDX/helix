import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  timeout: 30000,

  use: {
    baseURL: 'http://127.0.0.1:1313',
    headless: true,
    video: 'on',
    trace: 'retain-on-failure',
    screenshot: 'on',
  },

  reporter: [
    ['list'],
    ['html', { open: 'never' }],
  ],

  webServer: {
    command: 'hugo server --port 1313 --baseURL http://127.0.0.1:1313/ --appendPort=false',
    port: 1313,
    // Reuse a running server locally for speed, but always build fresh in CI so
    // a stale dev server cannot mask content drift (it did: see git history).
    reuseExistingServer: !process.env.CI,
    timeout: 30000,
  },
})
