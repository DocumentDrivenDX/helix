import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './schema-tests',
  timeout: 60000,
  use: {
    baseURL: 'http://127.0.0.1:1317/helix/', headless: true,
    launchOptions: { executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH },
  },
  webServer: {
    command: 'npm run serve:schemas',
    url: 'http://127.0.0.1:1317/helix/schemas/',
    reuseExistingServer: false,
    timeout: 60000,
  },
})
