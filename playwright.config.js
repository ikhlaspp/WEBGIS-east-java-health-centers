import { defineConfig } from '@playwright/test';

export default defineConfig({
    testDir: './tests/browser',
    forbidOnly: Boolean(process.env.CI),
    retries: process.env.CI ? 1 : 0,
    workers: 1,
    reporter: [['list'], ['html', { open: 'never' }]],
    use: {
        baseURL: 'http://127.0.0.1:8001',
        browserName: 'chromium',
        trace: 'retain-on-failure',
    },
    webServer: {
        command: 'php artisan serve --host=127.0.0.1 --port=8001 --no-reload',
        url: 'http://127.0.0.1:8001/up',
        reuseExistingServer: false,
        timeout: 60_000,
        env: { APP_ENV: 'testing', SESSION_DRIVER: 'array', CACHE_STORE: 'array', DB_HOST: '127.0.0.1', DB_DATABASE: 'gis_browser_testing', DB_URL: '' },
    },
});
