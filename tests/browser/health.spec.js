import { expect, test } from '@playwright/test';

test('the application serves its health and landing pages', async ({ page, request }) => {
    const health = await request.get('/up');
    expect(health.status()).toBe(200);
    const response = await page.goto('/');
    expect(response.status()).toBe(200);
    await expect(page.locator('body')).toBeVisible();
});
