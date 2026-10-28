import { expect, test } from '@playwright/test';
import { readFileSync } from 'node:fs';
const legends = JSON.parse(readFileSync(new URL('../../resources/analysis-legends.json', import.meta.url), 'utf8'));

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
        if (url.pathname.endsWith('/map/regions')) {
            if (options.themeError?.()) return route.fulfill({ status: 503, json: {} });
            const metric = url.searchParams.get('metric') === 'count' ? 'facility_count' : url.searchParams.get('metric');
            const level = url.searchParams.get('level');
            const codes = level === 'district' ? ['3501010'] : ['3501', '3502'];
            const features = codes.map((code, index) => ({ type: 'Feature', id: code, geometry: { type: 'Polygon', coordinates: [[[112 + index, -7], [112.5 + index, -7], [112.5 + index, -7.5], [112 + index, -7]]] }, properties: { code, name: index ? '<img src=x onerror="window.injected=1">' : 'Wilayah uji', metric, value: index ? null : 0, class: index ? 'no_data' : 0, without_facility: Boolean(index), completeness: index ? 'partial' : 'complete' } }));
            return route.fulfill({ json: { type: 'FeatureCollection', features, meta: { ...meta, ...(options.themeMismatch ? { analysis_run_id: release } : {}), metric, level, legend: legends[metric] } } });
        }
        if (url.pathname.endsWith('/regions')) return route.fulfill({ json: { data: url.searchParams.get('level') === 'district' ? [{ code: '3501010', name: 'Kecamatan uji' }] : [{ code: '3501', name: 'Kabupaten uji' }, { code: '3502', name: 'Kabupaten lain' }], meta } });
        const selected = options.filters ? facilities.filter((f) => (!url.searchParams.get('q') || f.name.includes(url.searchParams.get('q'))) && (!url.searchParams.get('coordinate_status') || f.coordinate_status === url.searchParams.get('coordinate_status'))) : facilities;
        if (url.pathname.endsWith('/map/points')) {
            if (options.error?.()) return route.fulfill({ status: 503, json: {} });
            const features = selected.filter((f) => f.location).map((f) => ({ type: 'Feature', geometry: f.location, properties: f }));
            if (options.invalid) features[0] = { ...features[0], geometry: { type: 'Point', coordinates: [-7.3, 112.7] } };
            return route.fulfill({ json: { type: 'FeatureCollection', features, meta: { ...meta, filtered_registered: selected.length, filtered_mapped: features.length, filtered_missing: selected.length - features.length } } });
        }
        if (url.pathname.endsWith('/facilities')) return route.fulfill({ json: { data: url.searchParams.get('page') === '2' ? [facilities[3]] : selected, meta: { ...meta, ...(options.mismatch ? { release_id: run } : {}), total: options.pages ? 51 : selected.length } } });
        return route.fulfill({ json: { data: options.detail || facilities.find((f) => url.pathname.endsWith(f.code)), meta } });
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


test('facility detail shows provenance, safe source links and missing coordinates', async ({ page }) => {
    const detail = { ...facilities[3], area_type: 'Perdesaan', source: { title: '<img src=x onerror="window.injected=1">', publisher: 'Penerbit uji', observation_period: '2024-S1', publication_year: 2025, license_note: 'Lisensi uji', limitations: 'Koordinat belum tersedia', source_url: 'https://example.test/source' }, coordinate_source: { title: 'Kandidat', source_url: 'javascript:alert(1)' } };
    await fixture(page, { detail });
    await page.goto(`/puskesmas/${detail.code}?release_id=${release}&analysis_run_id=${run}`);
    await expect(page.locator('#facility-fields')).toContainText('Perdesaan');
    await expect(page.locator('#facility-location-note')).toContainText('belum memiliki koordinat');
    await expect(page.locator('#facility-sources')).toContainText(detail.source.title);
    await expect(page.locator('#facility-sources')).toContainText('2024-S1');
    await expect(page.locator('#facility-sources')).toContainText('Koordinat belum tersedia');
    await expect(page.locator('#facility-sources img')).toHaveCount(0);
    await expect(page.locator('#facility-sources a')).toHaveCount(1);
    await expect(page.locator('#facility-sources a')).toHaveAttribute('href', 'https://example.test/source');
    expect(await page.evaluate(() => window.injected)).toBeUndefined();
    await page.getByRole('link', { name: 'Kembali ke peta' }).click();
    await expect(page).toHaveURL(new RegExp(`release_id=${release}.*analysis_run_id=${run}`));
});

test('facility detail rejects mismatched identity and invalid coordinates without partial data', async ({ page }) => {
    const detail = { ...facilities[0], location: { type: 'Point', coordinates: [-7.3, 112.7] } };
    await fixture(page, { detail });
    await page.goto(`/puskesmas/${detail.code}?release_id=${release}&analysis_run_id=${run}`);
    await expect(page.locator('#map-status')).toContainText('belum dapat dimuat');
    await expect(page.locator('#facility-fields')).toBeEmpty();
    detail.location = facilities[0].location;
    detail.code = facilities[1].code;
    await page.getByRole('button', { name: 'Coba lagi', exact: true }).click();
    await expect(page.locator('#map-status')).toContainText('belum dapat dimuat');
    await expect(page.locator('#facility-sources')).toBeEmpty();
    detail.code = facilities[0].code;
    await page.getByRole('button', { name: 'Coba lagi', exact: true }).click();
    await expect(page.locator('#facility-fields')).toContainText('112.7, -7.3');
    await expect(page.locator('#facility-sources')).toContainText('Informasi sumber belum tersedia.');
});


test('thematic metrics show fixed legends, real zero, missing values and safe region text', async ({ page }, testInfo) => {
    const requests = await fixture(page);
    await page.goto('/peta');
    await expect(page.locator('#map-status')).toContainText('Peta siap');
    for (const metric of ['count', 'density', 'population_per_facility', 'indicative_deficit']) {
        await page.locator('#thematic-metric').selectOption(metric);
        await expect(page.locator('#thematic-status')).toContainText('2 wilayah. 1 nilai tidak tersedia.');
        await expect(page.locator('#thematic-legend')).toContainText('Data tidak tersedia');
        await page.getByText('Nilai indikator per wilayah', { exact: true }).evaluate((element) => { element.parentElement.open = true; });
        await expect(page.locator('#thematic-rows tr')).toHaveCount(2);
        await expect(page.locator('#thematic-rows tr').first()).toContainText('0 ');
        await expect(page.locator('#thematic-rows tr').last()).toContainText(metric === 'population_per_facility' ? 'Tanpa fasilitas; rasio tidak tersedia' : 'Data tidak tersedia');
        await expect(page.locator('#thematic-rows img')).toHaveCount(0);
    }
    await page.screenshot({ path: testInfo.outputPath('thematic-desktop.png'), fullPage: true });
    await page.setViewportSize({ width: 360, height: 800 });
    await page.locator('#thematic-fit').click();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBeTruthy();
    await page.screenshot({ path: testInfo.outputPath('thematic-mobile.png'), fullPage: true });
    const queries = requests.filter((url) => url.pathname.endsWith('/map/regions'));
    expect(queries).toHaveLength(4);
    expect(queries.every((url) => url.searchParams.get('analysis_run_id') === run && url.searchParams.get('release_id') === release)).toBeTruthy();
    await page.locator('#thematic-metric').selectOption('');
    await expect(page.locator('#thematic-legend')).toBeEmpty();
    await expect(page.locator('#thematic-rows')).toBeEmpty();
});

test('district thematic view requires applied parent and failure preserves facility data', async ({ page }) => {
    let failure = false;
    const requests = await fixture(page, { themeError: () => failure });
    await page.goto('/peta');
    await expect(page.locator('#table-status')).toContainText('4 fasilitas');
    await page.locator('#thematic-level').selectOption('district');
    await page.locator('#thematic-metric').selectOption('count');
    await expect(page.locator('#thematic-status')).toContainText('Pilih kabupaten/kota');
    await page.locator('#filter-regency_code').selectOption('3501');
    await page.getByRole('button', { name: 'Terapkan filter' }).click();
    await expect(page.locator('#thematic-status')).toContainText('1 wilayah');
    expect(requests.filter((url) => url.pathname.endsWith('/map/regions')).at(-1).searchParams.get('parent_code')).toBe('3501');
    failure = true;
    await page.locator('#thematic-metric').selectOption('density');
    await expect(page.locator('#thematic-status')).toContainText('belum dapat dimuat');
    await expect(page.locator('#thematic-legend')).toBeEmpty();
    await expect(page.locator('#facility-rows tr')).toHaveCount(4);
    failure = false;
    await page.locator('#thematic-retry').click();
    await expect(page.locator('#thematic-status')).toContainText('1 wilayah');
});

test('thematic responses from another run are rejected', async ({ page }) => {
    await fixture(page, { themeMismatch: true });
    await page.goto('/peta');
    await expect(page.locator('#map-status')).toContainText('Peta siap');
    await page.locator('#thematic-metric').selectOption('count');
    await expect(page.locator('#thematic-status')).toContainText('belum dapat dimuat');
    await expect(page.locator('#thematic-rows')).toBeEmpty();
    await expect(page.locator('#thematic-legend')).toBeEmpty();
    await expect(page.locator('#facility-rows tr')).toHaveCount(4);
});


test('switching thematic metrics ignores a delayed failure from the previous selection', async ({ page }) => {
    await fixture(page);
    await page.goto('/peta');
    await expect(page.locator('#map-status')).toContainText('Peta siap');
    let delayed;
    await page.route('**/api/v1/map/regions?**', (route) => {
        if (new URL(route.request().url()).searchParams.get('metric') === 'count') { delayed = route; return; }
        return route.fallback();
    });
    await page.locator('#thematic-metric').selectOption('count');
    await expect.poll(() => Boolean(delayed)).toBeTruthy();
    await page.locator('#thematic-metric').selectOption('density');
    await expect(page.locator('#thematic-status')).toContainText('Kepadatan penduduk: 2 wilayah');
    await delayed.fulfill({ status: 503, json: {} });
    await expect(page.locator('#thematic-status')).toContainText('Kepadatan penduduk: 2 wilayah');
    await expect(page.locator('#thematic-retry')).toBeHidden();
    await expect(page.locator('#thematic-rows tr')).toHaveCount(2);
});
