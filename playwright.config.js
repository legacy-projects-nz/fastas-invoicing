// Playwright config for FASTAS smoke tests.
// Serves the static site locally and runs the tests in tests/.
const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  timeout: 30000,
  expect: { timeout: 10000 },
  fullyParallel: true,
  retries: process.env.CI ? 1 : 0,
  use: {
    baseURL: 'http://localhost:8080',
    headless: true,
    actionTimeout: 10000,
  },
  webServer: {
    command: 'python3 -m http.server 8080',
    url: 'http://localhost:8080/index.html',
    reuseExistingServer: !process.env.CI,
    timeout: 30000,
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
});
