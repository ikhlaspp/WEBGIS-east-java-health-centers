import { expect, test } from '@playwright/test';

const release = '00000000-0000-4000-8000-000000000006';
const run = '00000000-0000-4000-8000-000000000007';
const meta = {
    release_id: release, analysis_run_id: run,
    coordinate_coverage: { registered: 973, mapped: 565, verified: 240, missing: 408, eligible: 230 },
    source_periods: { facilities: '2024-S1', population_years: [2023], area_years: [2022, 2023] },
    boundary_edition: { name: 'Batas sintetis', version: 'uji-1' },
    warnings: ['Contoh sintetis untuk pengujian antarmuka.'],
};

async function fixtures(page, options = {}) {
    const requests = [];
    await page.route('**/api/v1/**', async (route) => {
        const url = new URL(route.request().url());
        requests.push(url);
        let body;
        if (url.pathname.endsWith('/releases')) {
            body = { data: options.empty ? [] : [{ release_id: release, analysis_run_id: run, label: 'Rilis uji sintetis' }], meta: { active_release_id: options.empty ? null : release } };
        } else if (url.pathname.endsWith('/statistics')) {
            if (options.error?.()) return route.fulfill({ status: 503, json: { error: 'unavailable' } });
            if (options.delay) await new Promise((resolve) => setTimeout(resolve, options.delay));
            body = { data: { district_count: 666, population: 300000, area_km2: 120.5, density: 2489.63, population_per_facility: 308.32, indicative_deficit: 0, T: 30000, completeness: 'complete', ...options.metrics }, meta: options.zero ? { ...meta, coordinate_coverage: { registered: 0, mapped: 0, verified: 0, missing: 0, eligible: null }, source_periods: { facilities: '2024', population_years: [], area_years: [null] } } : meta };
        } else if (url.pathname.endsWith('/regions')) {
            body = { data: [{ code: '3501', name: 'Kabupaten uji' }, { code: '3571', name: 'Kota uji' }], meta: options.mismatch ? { ...meta, release_id: '00000000-0000-4000-8000-000000000099' } : meta };
        } else {
            body = { data: [{ publisher: 'Sumber sintetis', title: options.unsafeSource ? '<img src=x onerror=alert(1)>' : 'Sensus fasilitas sintetis', observation_period: '2024', source_url: options.unsafeSource ? 'javascript:alert(1)' : 'https://example.test/source' }], meta };
        }
        await route.fulfill({ json: body });
    });
    return requests;
}

for (const width of [360, 768, 1366]) {
    test(`dashboard keeps counts, periods and navigation readable at ${width}px`, async ({ page }, testInfo) => {
        await page.setViewportSize({ width, height: 900 });
        const requests = await fixtures(page);
        await page.goto('/');
        await expect(page.locator('[data-count="registered"]')).toHaveText('973');
        await expect(page.locator('[data-count="mapped"]')).toHaveText('565');
        await expect(page.locator('[data-count="verified"]')).toHaveText('240');
        await expect(page.locator('[data-count="missing"]')).toHaveText('408');
        await expect(page.locator('#coverage-note')).toContainText('230 dari 973');
        await expect(page.locator('#facility-period')).toHaveText('2024-S1');
        await expect(page.locator('#population-period')).toHaveText('2023');
        await expect(page.locator('#area-period')).toHaveText('2022, 2023');
        await expect(page.locator('#region-summary')).toHaveText('2 kabupaten/kota · 666 kecamatan');
        await expect(page).toHaveURL(new RegExp(`release_id=${release}.*analysis_run_id=${run}`));
        for (const url of requests.filter((url) => !url.pathname.endsWith('/releases'))) {
            expect(url.searchParams.get('release_id')).toBe(release);
            expect(url.searchParams.get('analysis_run_id')).toBe(run);
        }
        await expect(page.locator('#source-list img')).toHaveCount(0);
        await expect(page.locator('#source-list a')).toHaveAttribute('href', 'https://example.test/source');
        expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
        await page.getByRole('link', { name: 'Wilayah', exact: true }).click();
        await expect(page.locator('#regions-title')).toBeInViewport();
        await page.screenshot({ path: testInfo.outputPath(`dashboard-${width}.png`), fullPage: true });
    });
}

test('no published release leaves counts unavailable instead of zero', async ({ page }) => {
    const requests = await fixtures(page, { empty: true });
    await page.goto('/');
    await expect(page.getByRole('status')).toContainText('Belum ada rilis publik');
    await expect(page.locator('[data-count="registered"]')).toHaveText('—');
    expect(requests).toHaveLength(1);
    await expect(page.locator('#ringkasan')).toHaveAttribute('aria-busy', 'false');
});

test('source labels remain text and unsafe links are not rendered', async ({ page }) => {
    await fixtures(page, { unsafeSource: true });
    await page.goto('/');
    await expect(page.locator('#source-list')).toContainText('<img src=x');
    await expect(page.locator('#source-list img')).toHaveCount(0);
    await expect(page.locator('#source-list a')).toHaveCount(0);
});

test('API failure retries the pinned release and loading never displays zero', async ({ page }) => {
    let fail = true;
    const requests = await fixtures(page, { error: () => fail, delay: 200 });
    await page.goto('/');
    await expect(page.getByRole('status')).toContainText('Data belum dapat dimuat');
    await expect(page.locator('[data-count="registered"]')).toHaveText('—');
    fail = false;
    await page.getByRole('button', { name: 'Coba lagi' }).click();
    await expect(page.locator('#ringkasan')).toHaveAttribute('aria-busy', 'true');
    await expect(page.locator('[data-count="registered"]')).toHaveText('—');
    await expect(page.locator('[data-count="registered"]')).toHaveText('973');
    expect(requests.filter((url) => url.pathname.endsWith('/releases'))).toHaveLength(1);
});

test('mixed release responses are rejected without showing partial counts', async ({ page }) => {
    await fixtures(page, { mismatch: true });
    await page.goto('/');
    await expect(page.getByRole('status')).toContainText('Data belum dapat dimuat');
    await expect(page.locator('[data-count="registered"]')).toHaveText('—');
    await expect(page.locator('#region-list li')).toHaveCount(0);
});

test('a pinned release bypasses active selection and preserves real zero and missing periods', async ({ page }) => {
    const requests = await fixtures(page, { zero: true });
    await page.goto(`/?release_id=${release}&analysis_run_id=${run}`);
    await expect(page.locator('[data-count="registered"]')).toHaveText('0');
    await expect(page.locator('#population-period')).toHaveText('Belum tersedia');
    await expect(page.locator('#coverage-note')).toContainText('belum tersedia');
    expect(requests.some((url) => url.pathname.endsWith('/releases'))).toBe(false);
});

test('keyboard navigation exposes a skip link and invalid pinned identities fail safely', async ({ page }) => {
    const requests = await fixtures(page);
    await page.goto('/?release_id=invalid');
    await page.keyboard.press('Tab');
    await expect(page.getByRole('link', { name: 'Lewati ke konten' })).toBeFocused();
    await expect(page.getByRole('status')).toContainText('Data belum dapat dimuat');
    expect(requests).toHaveLength(0);
});


test('analysis summary uses units, distinguishes null from zero and identifies partial sources', async ({ page }) => {
    await fixtures(page, { metrics: { population: null, density: null, completeness: 'partial' } });
    await page.goto('/');
    await expect(page.locator('#analysis-summary')).toBeVisible();
    await expect(page.locator('[data-metric="population"]')).toHaveText('Tidak tersedia');
    await expect(page.locator('[data-metric="density"]')).toHaveText('Tidak tersedia');
    await expect(page.locator('[data-metric="indicative_deficit"]')).toHaveText('0 fasilitas');
    await expect(page.locator('[data-metric="area_km2"]')).toContainText('120,5');
    await expect(page.locator('[data-metric="population_per_facility"]')).toHaveText('308,32 jiwa/fasilitas');
    await expect(page.locator('#analysis-note')).toContainText('30.000 jiwa per fasilitas');
    await expect(page.locator('#analysis-note')).toContainText('Data sumber parsial');
});

test('invalid analysis values leave no partial dashboard results', async ({ page }) => {
    await fixtures(page, { metrics: { density: -1 } });
    await page.goto('/');
    await expect(page.getByRole('status')).toContainText('Data belum dapat dimuat');
    await expect(page.locator('#analysis-summary')).toBeHidden();
    await expect(page.locator('[data-metric="density"]')).toBeEmpty();
    await expect(page.locator('#region-list li')).toHaveCount(0);
});
