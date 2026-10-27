import { expect, test } from '@playwright/test';

const release = '00000000-0000-4000-8000-000000000006';
const run = '00000000-0000-4000-8000-000000000007';
const meta = { release_id: release, analysis_run_id: run, source_periods: { facilities: '2024-S1' } };
const facilities = [
    { code: '10300000001', name: 'Fasilitas A', service_type: 'Rawat Inap', coordinate_status: 'verified', location: { type: 'Point', coordinates: [112.7, -7.3] } },
    { code: '10300000002', name: '<img src=x onerror="window.injected=1">', service_type: 'Non Rawat Inap', coordinate_status: 'unverified', location: { type: 'Point', coordinates: [112.7, -7.3] } },
    { code: '10300000003', name: 'Pulau uji', service_type: 'Rawat Inap', coordinate_status: 'verified', location: { type: 'Point', coordinates: [115.5, -6.9] } },
    { code: '10300000004', name: 'Tanpa titik', service_type: 'Non Rawat Inap', coordinate_status: 'missing', location: null },
];
async function fixture(page, options = {}) {
    const requests = [];
    await page.route('https://tile.openstreetmap.org/**', (route) => options.tileError ? route.abort() : route.fulfill({ contentType: 'image/png', body: Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=', 'base64') }));
    await page.route('**/api/v1/**', (route) => {
        const url = new URL(route.request().url()); requests.push(url);
        if (url.pathname.endsWith('/releases')) return route.fulfill({ json: { data: [], meta: { active_release_id: options.empty ? null : release } } });
        if (url.pathname.endsWith('/regions')) return route.fulfill({ json: { data: url.searchParams.get('level') === 'district' ? [{ code: '3501010', name: 'Kecamatan uji' }] : [{ code: '3501', name: 'Kabupaten uji' }, { code: '3502', name: 'Kabupaten lain' }], meta } });
        const selected = options.filters ? facilities.filter((f) => (!url.searchParams.get('q') || f.name.includes(url.searchParams.get('q'))) && (!url.searchParams.get('coordinate_status') || f.coordinate_status === url.searchParams.get('coordinate_status'))) : facilities;
        if (url.pathname.endsWith('/map/points')) {
            if (options.error?.()) return route.fulfill({ status: 503, json: {} });
            const features = selected.filter((f) => f.location).map((f) => ({ type: 'Feature', geometry: f.location, properties: f }));
            if (options.invalid) features[0] = { ...features[0], geometry: { type: 'Point', coordinates: [-7.3, 112.7] } };
            return route.fulfill({ json: { type: 'FeatureCollection', features, meta: { ...meta, filtered_registered: selected.length, filtered_mapped: features.length, filtered_missing: selected.length - features.length } } });
        }
        if (url.pathname.endsWith('/facilities')) return route.fulfill({ json: { data: url.searchParams.get('page') === '2' ? [facilities[3]] : selected, meta: { ...meta, ...(options.mismatch ? { release_id: run } : {}), total: options.pages ? 51 : selected.length } } });
        return route.fulfill({ json: { data: facilities.find((f) => url.pathname.endsWith(f.code)), meta } });
    });
    return requests;
}

test('map clusters colocated facilities, includes islands and provides safe popups and detail', async ({ page }, testInfo) => {
    const errors = []; page.on('pageerror', (error) => errors.push(error.message));
    const requests = await fixture(page);
    await page.goto('/peta');
    await expect(page.locator('#map-status')).toContainText('Peta siap');
    await expect(page.locator('#map-counts')).toHaveText('4 terdaftar · 3 memiliki koordinat · 1 tanpa koordinat');
    await expect(page.locator('.marker-cluster')).toHaveCount(1);
    await expect(page.locator('.marker-cluster')).toContainText('2');
    await expect(page.locator('.leaflet-marker-icon[title="Pulau uji"]')).toBeVisible();
    await expect(page.locator('.leaflet-control-attribution')).toContainText('OpenStreetMap');
    await page.screenshot({ path: testInfo.outputPath('map-desktop.png'), fullPage: true });
    await page.locator('.marker-cluster').click();
    await expect(page.locator('.facility-marker[title="Fasilitas A"]')).toBeVisible();
    await page.locator('.facility-marker[title="Fasilitas A"]').click();
    await expect(page.locator('.leaflet-popup')).toContainText('Rawat Inap');
    await expect(page.getByRole('row').filter({ hasText: 'Tanpa titik' }).getByRole('button', { name: 'Lihat titik' })).toHaveCount(0);
    await page.getByRole('row').filter({ hasText: facilities[1].name }).getByRole('button', { name: 'Lihat titik' }).click();
    expect(errors).toEqual([]);
    await expect(page.locator('.leaflet-popup')).toHaveCount(1);
    await expect(page.locator('.leaflet-popup')).toContainText(facilities[1].name);
    await expect(page.locator('.leaflet-popup')).toContainText('Non Rawat Inap');
    await expect(page.locator('.leaflet-popup img')).toHaveCount(0);
    expect(await page.evaluate(() => window.injected)).toBeUndefined();
    await page.locator('.leaflet-popup').getByRole('link', { name: 'Lihat detail' }).click();
    await expect(page.locator('#facility-fields')).toContainText(facilities[1].name);
    await expect(page).toHaveURL(new RegExp(`release_id=${release}.*analysis_run_id=${run}`));
    expect(requests.filter((url) => !url.pathname.endsWith('/releases')).every((url) => url.searchParams.get('release_id') === release)).toBeTruthy();
    expect(errors).toEqual([]);
});

test('tile failure preserves the table, paging, marker controls and mobile layout', async ({ page }, testInfo) => {
    await page.setViewportSize({ width: 360, height: 800 });
    await fixture(page, { tileError: true, pages: true });
    await page.goto('/peta');
    await expect(page.locator('#table-status')).toContainText('51 fasilitas');
    await expect(page.locator('#tile-status')).toBeVisible();
    await page.getByRole('button', { name: 'Berikutnya', exact: true }).click();
    await expect(page.locator('#table-page')).toHaveText('Halaman 2 / 2');
    await expect(page.locator('#facility-rows tr')).toHaveCount(1);
    await page.getByRole('button', { name: 'Sebelumnya', exact: true }).click();
    await expect(page.locator('#table-page')).toHaveText('Halaman 1 / 2');
    await page.getByRole('checkbox', { name: 'Puskesmas', exact: true }).uncheck();
    await expect(page.locator('.leaflet-marker-icon')).toHaveCount(0);
    await page.getByRole('checkbox', { name: 'Puskesmas', exact: true }).check();
    await expect(page.locator('.leaflet-marker-icon').first()).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBeTruthy();
    await page.screenshot({ path: testInfo.outputPath('map-mobile.png'), fullPage: true });
});

test('API retry stays pinned and navigation retains the same release', async ({ page }) => {
    let failed = true;
    const requests = await fixture(page, { error: () => failed });
    await page.goto(`/peta?release_id=${release}&analysis_run_id=${run}`);
    await expect(page.locator('#map-status')).toContainText('belum dapat dimuat');
    failed = false; await page.getByRole('button', { name: 'Coba lagi', exact: true }).click();
    await expect(page.locator('#map-status')).toContainText('Peta siap');
    expect(requests.some((url) => url.pathname.endsWith('/releases'))).toBeFalsy();
    await page.getByRole('link', { name: 'Ringkasan', exact: true }).click();
    await expect(page).toHaveURL(new RegExp(`release_id=${release}.*analysis_run_id=${run}#ringkasan`));
});

test('no published release and invalid coordinates never create fallback markers', async ({ page }) => {
    await fixture(page, { empty: true });
    await page.goto('/peta');
    await expect(page.locator('#map-status')).toHaveText('Belum ada rilis publik.');
    await expect(page.locator('.leaflet-marker-icon')).toHaveCount(0);
    await page.unroute('**/api/v1/**');
    await fixture(page, { invalid: true });
    await page.reload();
    await expect(page.locator('#map-status')).toContainText('belum dapat dimuat');
    await expect(page.locator('.leaflet-marker-icon')).toHaveCount(0);
});

test('table responses from another release are rejected', async ({ page }) => {
    await fixture(page, { mismatch: true });
    await page.goto('/peta');
    await expect(page.locator('#table-status')).toContainText('belum dapat dimuat');
    await expect(page.locator('#facility-rows tr')).toHaveCount(0);
});


test('filters keep points and list aligned, include missing locations, and clear child selection', async ({ page }) => {
    const requests = await fixture(page, { filters: true });
    await page.goto('/peta');
    await expect(page.locator('#table-status')).toContainText('4 fasilitas');
    await page.getByRole('combobox', { name: 'Kabupaten/kota', exact: true }).selectOption('3501');
    await expect(page.getByRole('combobox', { name: 'Kecamatan', exact: true })).toBeEnabled();
    await page.getByRole('combobox', { name: 'Kecamatan', exact: true }).selectOption('3501010');
    await page.getByRole('combobox', { name: 'Status lokasi', exact: true }).selectOption('missing');
    await page.getByRole('button', { name: 'Terapkan filter' }).click();
    await expect(page.locator('#map-counts')).toContainText('1 terdaftar');
    await expect(page.locator('#facility-rows')).toContainText('Tanpa titik');
    await expect(page.locator('.leaflet-marker-icon')).toHaveCount(0);
    for (const endpoint of ['/map/points', '/facilities']) {
        const url = requests.filter((url) => url.pathname.endsWith(endpoint)).at(-1);
        expect(url.searchParams.get('district_code')).toBe('3501010');
        expect(url.searchParams.get('coordinate_status')).toBe('missing');
        expect(url.searchParams.get('analysis_run_id')).toBe(run);
    }
    await page.getByRole('combobox', { name: 'Kabupaten/kota', exact: true }).selectOption('3502');
    await expect(page.getByRole('combobox', { name: 'Kecamatan', exact: true })).toHaveValue('');
    await page.getByRole('button', { name: 'Reset filter' }).click();
    await expect(page.locator('#table-status')).toContainText('4 fasilitas');
    await expect(page.getByRole('combobox', { name: 'Kecamatan', exact: true })).toBeDisabled();
    await page.getByLabel('Nama atau kode').fill('Tidak ditemukan');
    await page.getByRole('button', { name: 'Terapkan filter' }).click();
    await expect(page.locator('#map-counts')).toContainText('0 terdaftar');
    await expect(page.locator('#table-status')).toContainText('0 fasilitas');
    await expect(page.locator('#facility-rows tr')).toHaveCount(0);
});


test('late filter responses cannot replace the current map or table', async ({ page }) => {
    await fixture(page, { filters: true });
    await page.goto('/peta');
    await expect(page.locator('#table-status')).toContainText('4 fasilitas');
    let delayed;
    await page.route('**/api/v1/map/points?**', (route) => {
        if (new URL(route.request().url()).searchParams.get('q') === 'Lama') { delayed = route; return; }
        return route.fallback();
    });
    await page.getByLabel('Nama atau kode').fill('Lama');
    await page.getByRole('button', { name: 'Terapkan filter' }).click();
    await expect.poll(() => Boolean(delayed)).toBeTruthy();
    await page.getByLabel('Nama atau kode').fill('Tanpa titik');
    await page.getByRole('button', { name: 'Terapkan filter' }).click();
    await expect(page.locator('#facility-rows')).toContainText('Tanpa titik');
    await delayed.fulfill({ status: 503, json: {} });
    await expect(page.locator('#map-status')).toContainText('Tidak ada titik');
    await expect(page.locator('#map-counts')).toContainText('1 terdaftar');
    await expect(page.locator('#facility-rows tr')).toHaveCount(1);
    await expect(page.locator('#map-retry')).toBeHidden();
});


test('shared filter URLs restore controls and survive refresh without changing release', async ({ page }) => {
    const requests = await fixture(page, { filters: true });
    const query = new URLSearchParams({ release_id: release, analysis_run_id: run, q: 'Tanpa titik', regency_code: '3501', district_code: '3501010', service_type: 'Non Rawat Inap', area_type: 'Perdesaan', coordinate_status: 'missing' });
    await page.goto(`/peta?${query}`);
    await expect(page.locator('#facility-rows')).toContainText('Tanpa titik');
    await expect(page.locator('#filter-district_code')).toBeEnabled();
    await expect(page.locator('#filter-regency_code')).toHaveValue('3501');
    await expect(page.locator('#filter-district_code')).toHaveValue('3501010');
    await expect(page.locator('#filter-q')).toHaveValue('Tanpa titik');
    await expect(page.locator('#filter-service_type')).toHaveValue('Non Rawat Inap');
    await expect(page.locator('#filter-area_type')).toHaveValue('Perdesaan');
    await page.reload();
    await expect(page.locator('#filter-district_code')).toBeEnabled();
    await expect(page.locator('#map-counts')).toContainText('1 terdaftar');
    await page.getByRole('button', { name: 'Reset filter' }).click();
    await expect(page.locator('#table-status')).toContainText('4 fasilitas');
    const reset = new URL(page.url());
    expect([...reset.searchParams.keys()].sort()).toEqual(['analysis_run_id', 'release_id']);
    expect(reset.searchParams.get('release_id')).toBe(release);
    expect(requests.some((url) => url.pathname.endsWith('/releases'))).toBeFalsy();
});

test('invalid shared filters fail visibly and can be cleared', async ({ page }) => {
    const requests = await fixture(page, { filters: true });
    await page.goto(`/peta?release_id=${release}&analysis_run_id=${run}&coordinate_status=invented`);
    await expect(page.locator('#map-status')).toContainText('belum dapat dimuat');
    expect(requests.some((url) => url.pathname.endsWith('/map/points'))).toBeFalsy();
    await page.getByRole('button', { name: 'Reset filter' }).click();
    await expect(page.locator('#table-status')).toContainText('4 fasilitas');
    expect(new URL(page.url()).searchParams.has('coordinate_status')).toBeFalsy();
});
