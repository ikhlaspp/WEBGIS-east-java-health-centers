const root = document.querySelector('#dashboard');

if (root) {
    const byId = (id) => document.getElementById(id);
    const number = new Intl.NumberFormat('id-ID');
    const uuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    const search = new URLSearchParams(location.search);
    let release = search.get('release_id');
    let run = search.get('analysis_run_id');
    let controller;
    let requestNumber = 0;

    function state(kind, message) {
        byId('data-status').hidden = kind === 'ready';
        byId('data-status').dataset.state = kind;
        byId('status-text').textContent = message;
        byId('retry-data').hidden = kind !== 'error';
        byId('ringkasan').setAttribute('aria-busy', String(kind === 'loading'));
    }

    function clear() {
        document.querySelectorAll('[data-count]').forEach((element) => { element.textContent = '—'; });
        byId('release-details').hidden = true;
        byId('region-list').replaceChildren();
        byId('source-list').replaceChildren();
        byId('warning-list').replaceChildren();
        byId('boundary-note').textContent = '';
        byId('region-summary').textContent = 'Ringkasan wilayah belum tersedia.';
        byId('coverage-note').textContent = 'Kelengkapan lokasi belum tersedia.';
    }

    async function get(endpoint, params, signal) {
        const url = new URL(endpoint);
        Object.entries(params).forEach(([key, value]) => { if (value) url.searchParams.set(key, value); });
        const response = await fetch(url, { signal, headers: { Accept: 'application/json' }, cache: 'no-store' });
        if (!response.ok) throw new Error('api');
        return response.json();
    }

    function sameIdentity(payload) {
        if (payload?.meta?.release_id !== release || payload.meta.analysis_run_id !== run) throw new Error('identity');
    }

    const periods = (values) => Array.isArray(values) && values.filter((value) => value !== null).length
        ? [...new Set(values.filter((value) => value !== null))].join(', ') : 'Belum tersedia';

    async function load() {
        const request = ++requestNumber;
        controller?.abort();
        const currentController = new AbortController();
        controller = currentController;
        const timeout = setTimeout(() => currentController.abort(), 15000);
        clear();
        state('loading', 'Memuat ringkasan data…');
        byId('release-label').textContent = 'Memuat rilis…';
        try {
            if ((release && !uuid.test(release)) || (run && (!release || !uuid.test(run)))) throw new Error('identity');
            let label = 'Rilis publik terpilih';
            if (!release) {
                const catalog = await get(root.dataset.releasesUrl, {}, currentController.signal);
                if (!catalog.meta || !Array.isArray(catalog.data)) throw new Error('shape');
                release = catalog.meta.active_release_id;
                if (release === null) {
                    byId('release-label').textContent = 'Belum ada rilis';
                    state('empty', 'Belum ada rilis publik. Ringkasan akan tersedia setelah data diterbitkan.');
                    return;
                }
                if (!uuid.test(release)) throw new Error('identity');
                const selected = catalog.data.find((item) => item.release_id === release);
                if (selected) { label = selected.label; run = selected.analysis_run_id; }
            }
            const stats = await get(root.dataset.statisticsUrl, { release_id: release, analysis_run_id: run }, currentController.signal);
            if (stats?.meta?.release_id !== release || !uuid.test(stats.meta.analysis_run_id) || (run && stats.meta.analysis_run_id !== run)) throw new Error('identity');
            run = stats.meta.analysis_run_id;
            const [regions, sources] = await Promise.all([
                get(root.dataset.regionsUrl, { release_id: release, analysis_run_id: run, level: 'regency' }, currentController.signal),
                get(root.dataset.sourcesUrl, { release_id: release, analysis_run_id: run }, currentController.signal),
            ]);
            sameIdentity(regions);
            sameIdentity(sources);
            if (request !== requestNumber) return;
            const counts = stats.meta.coordinate_coverage;
            for (const key of ['registered', 'mapped', 'verified', 'missing']) {
                if (!Number.isSafeInteger(counts?.[key]) || counts[key] < 0) throw new Error('counts');
            }
            if (counts.mapped + counts.missing !== counts.registered || counts.verified > counts.mapped
                || (counts.eligible !== null && (!Number.isSafeInteger(counts.eligible) || counts.eligible < 0 || counts.eligible > counts.verified))
                || !Array.isArray(regions.data) || !Array.isArray(sources.data)) throw new Error('counts');
            const dates = stats.meta.source_periods;
            if (!dates || !Number.isSafeInteger(stats.data?.district_count)) throw new Error('shape');
            document.querySelectorAll('[data-count]').forEach((element) => { element.textContent = number.format(counts[element.dataset.count]); });
            byId('release-label').textContent = label;
            byId('facility-period').textContent = dates.facilities || 'Belum tersedia';
            byId('population-period').textContent = periods(dates.population_years);
            byId('area-period').textContent = periods(dates.area_years);
            byId('release-identity').textContent = `Rilis: ${release} · Analisis: ${run}`;
            byId('release-details').hidden = false;
            byId('coverage-note').textContent = counts.eligible === null ? 'Kelayakan titik untuk analisis radius belum tersedia.'
                : `${counts.eligible < counts.registered ? 'Analisis parsial' : 'Kelengkapan titik'}: ${number.format(counts.eligible)} dari ${number.format(counts.registered)} fasilitas layak untuk analisis radius. Memiliki koordinat tidak otomatis berarti layak analisis.`;
            byId('region-summary').textContent = `${number.format(regions.data.length)} kabupaten/kota · ${number.format(stats.data.district_count)} kecamatan`;
            for (const region of regions.data) {
                const item = document.createElement('li');
                item.textContent = region.name;
                const code = document.createElement('span');
                code.textContent = region.code;
                item.append(code);
                byId('region-list').append(item);
            }
            byId('boundary-note').textContent = `Batas wilayah: ${stats.meta.boundary_edition?.name ?? 'Tidak tersedia'} · Edisi ${stats.meta.boundary_edition?.version ?? 'tidak tersedia'}`;
            for (const source of sources.data) {
                const item = document.createElement('li');
                item.textContent = `${source.publisher} — ${source.title}. Periode: ${source.observation_period || 'belum tersedia'}. `;
                try {
                    const url = new URL(source.source_url);
                    if (['https:', 'http:'].includes(url.protocol)) {
                        const link = document.createElement('a');
                        link.href = url.href;
                        link.textContent = 'Buka sumber';
                        link.rel = 'noopener noreferrer';
                        item.append(link);
                    }
                } catch { /* Sources without a public URL remain visible as text. */ }
                byId('source-list').append(item);
            }
            if (!sources.data.length) byId('source-list').textContent = 'Belum ada sumber publik yang tercantum pada rilis ini.';
            for (const warning of stats.meta.warnings ?? []) {
                const item = document.createElement('li');
                item.textContent = warning;
                byId('warning-list').append(item);
            }
            const pinned = new URL(location.href);
            pinned.searchParams.set('release_id', release);
            pinned.searchParams.set('analysis_run_id', run);
            history.replaceState(null, '', pinned);
            state('ready', 'Ringkasan data siap.');
        } catch {
            if (request !== requestNumber) return;
            clear();
            byId('release-label').textContent = 'Data belum tersedia';
            state('error', 'Data belum dapat dimuat. Periksa koneksi atau coba lagi. Rilis yang dipilih tidak akan diganti otomatis.');
        } finally {
            clearTimeout(timeout);
        }
    }

    byId('retry-data').addEventListener('click', load);
    load();
}
