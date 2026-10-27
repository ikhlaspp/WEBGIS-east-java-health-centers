import L from 'leaflet';
import 'leaflet.markercluster';
import 'leaflet/dist/leaflet.css';
import 'leaflet.markercluster/dist/MarkerCluster.css';
import 'leaflet.markercluster/dist/MarkerCluster.Default.css';
import '../../css/map.css';

const root = document.querySelector('#facility-map, #facility-detail');
const byId = (id) => document.getElementById(id);
const uuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const search = new URLSearchParams(location.search);
let release = search.get('release_id');
let run = search.get('analysis_run_id');
const statusNames = { verified: 'Terverifikasi', unverified: 'Belum terverifikasi', rejected: 'Ditolak', missing: 'Tanpa koordinat' };
const text = (tag, value) => { const element = document.createElement(tag); element.textContent = value ?? 'Belum tersedia'; return element; };
const pinned = (endpoint, parameters = {}) => {
    const url = new URL(endpoint, location.origin);
    for (const [key, value] of Object.entries({ release_id: release, analysis_run_id: run, ...parameters })) {
        if (value !== null && value !== undefined) url.searchParams.set(key, value);
    }
    return url;
};
async function get(endpoint, parameters = {}, check = true) {
    const response = await fetch(pinned(endpoint, parameters), { headers: { Accept: 'application/json' }, signal: AbortSignal.timeout(15000), cache: 'no-store' });
    if (!response.ok) throw new Error('api');
    const body = await response.json();
    if (check) {
        if (body.meta?.release_id !== release || !uuid.test(body.meta?.analysis_run_id) || (run && body.meta.analysis_run_id !== run)) throw new Error('identity');
        run = body.meta.analysis_run_id;
    }
    return body;
}
async function selectRelease() {
    if ((release && !uuid.test(release)) || (run && (!release || !uuid.test(run)))) throw new Error('identity');
    if (!release) {
        const catalog = await get(root.dataset.releases, {}, false);
        if (catalog.meta?.active_release_id === null) return false;
        if (!uuid.test(catalog.meta?.active_release_id)) throw new Error('identity');
        release = catalog.meta.active_release_id;
    }
    return true;
}
function remember() { history.replaceState(null, '', pinned(location.href)); }
function fields(container, data) {
    for (const [label, value] of [['Nama', data.name], ['Kode', data.code], ['Alamat', data.address], ['Layanan', data.service_type], ['Wilayah', [data.district_name, data.regency_name].filter(Boolean).join(', ')], ['Status lokasi', statusNames[data.coordinate_status]], ['Presisi', data.precision_level]]) {
        container.append(text('dt', label), text('dd', value || 'Belum tersedia'));
    }
}
let map, clusters, tiles, tablePage = 1, pageRequest = 0, loadRequest = 0, regionRequest = 0;
let filters = {};
const form = byId('map-filters');
function options(select, rows, label) {
    select.replaceChildren(new Option(label, ''));
    for (const row of rows) select.add(new Option(row.name, row.code));
}
async function loadRegions() {
    const request = ++regionRequest;
    const parent = form.elements.regency_code.value;
    const district = form.elements.district_code;
    district.disabled = true;
    options(district, [], 'Semua kecamatan');
    byId('region-retry').hidden = true;
    byId('region-status').textContent = 'Memuat wilayah...';
    try {
        const body = await get(root.dataset.regions, parent ? { level: 'district', parent_code: parent } : { level: 'regency' });
        if (request !== regionRequest) return;
        if (!Array.isArray(body.data) || body.data.some((row) => !(parent ? /^\d{7}$/ : /^\d{4}$/).test(row.code))) throw new Error('regions');
        options(parent ? district : form.elements.regency_code, body.data, parent ? 'Semua kecamatan' : 'Semua kabupaten/kota');
        district.disabled = !parent;
        byId('region-status').textContent = '';
    } catch {
        if (request !== regionRequest) return;
        byId('region-status').textContent = 'Wilayah belum dapat dimuat.';
        byId('region-retry').hidden = false;
    }
}
const markers = new Map();
if (root.id === 'facility-map') {
    map = L.map('map-canvas', { maxZoom: 19 }).setView([-7.5, 112.5], 7);
    tiles = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' }).addTo(map);
    tiles.on('tileerror', () => { byId('tile-status').hidden = false; });
    byId('tile-retry').onclick = () => { byId('tile-status').hidden = true; tiles.redraw(); };
    clusters = L.markerClusterGroup({ showCoverageOnHover: false, animate: !matchMedia('(prefers-reduced-motion: reduce)').matches }).addTo(map);
    L.control.layers({ OpenStreetMap: tiles }, { Puskesmas: clusters }, { collapsed: false }).addTo(map);
    L.control.scale({ imperial: false }).addTo(map);
    byId('map-fit').onclick = () => { if (markers.size) map.fitBounds(clusters.getBounds(), { padding: [35, 35], maxZoom: 14, animate: false }); };
    form.onsubmit = (event) => {
        event.preventDefault();
        filters = Object.fromEntries([...new FormData(form)].map(([key, value]) => [key, value.trim()]).filter(([, value]) => value));
        load();
    };
    form.onreset = () => {
        ++regionRequest;
        options(form.elements.district_code, [], 'Semua kecamatan');
        form.elements.district_code.disabled = true;
        filters = {};
        load();
    };
    form.elements.regency_code.onchange = loadRegions;
    byId('region-retry').onclick = loadRegions;
    byId('previous-page').onclick = () => loadTable(tablePage - 1);
    byId('next-page').onclick = () => loadTable(tablePage + 1);
}
function detailLink(code) {
    const link = text('a', 'Lihat detail');
    link.href = pinned(`${root.dataset.detailBase}/${encodeURIComponent(code)}`).href;
    return link;
}
function popup(feature) {
    const box = document.createElement('div');
    box.append(text('strong', feature.properties.name), text('p', statusNames[feature.properties.coordinate_status]));
    const services = text('p', 'Memuat layanan…');
    box.append(services, detailLink(feature.properties.code));
    get(`${root.dataset.facilities}/${encodeURIComponent(feature.properties.code)}`).then((body) => {
        services.textContent = `Layanan: ${body.data.service_type || 'Belum tersedia'}`;
    }).catch(() => { services.textContent = 'Layanan belum dapat dimuat. Coba buka detail.'; });
    return box;
}
async function loadTable(page) {
    const request = ++pageRequest;
    byId('previous-page').disabled = byId('next-page').disabled = true;
    byId('facility-rows').replaceChildren();
    byId('table-status').textContent = 'Memuat daftar…';
    try {
        const body = await get(root.dataset.facilities, { ...filters, page, per_page: 50 });
        if (request !== pageRequest) return;
        if (!Array.isArray(body.data) || !Number.isSafeInteger(body.meta.total) || body.meta.total < 0) throw new Error('shape');
        for (const facility of body.data) {
            if (!/^\d{11}$/.test(facility.code)) throw new Error('code');
            const row = document.createElement('tr');
            row.append(text('td', `${facility.name} (${facility.code})`), text('td', facility.service_type), text('td', statusNames[facility.coordinate_status]));
            const actions = document.createElement('td');
            actions.append(detailLink(facility.code));
            if (markers.has(facility.code)) {
                const button = text('button', 'Lihat titik'); button.type = 'button';
                button.onclick = () => {
                    map.addLayer(clusters);
                    const marker = markers.get(facility.code);
                    const [longitude, latitude] = marker.feature.geometry.coordinates;
                    map.stop();
                    map.setView([latitude, longitude], map.getMaxZoom(), { animate: false });
                    L.popup().setLatLng([latitude, longitude]).setContent(popup(marker.feature)).openOn(map);
                    byId('map-canvas').focus({ preventScroll: true });
                    byId('map-canvas').scrollIntoView({ block: 'center' });
                };
                actions.append(button);
            }
            row.append(actions); byId('facility-rows').append(row);
        }
        tablePage = page;
        byId('table-page').textContent = `Halaman ${page} / ${Math.max(1, Math.ceil(body.meta.total / 50))}`;
        byId('table-status').textContent = `${body.meta.total} fasilitas terdaftar. ${body.data.length} ditampilkan.`;
        byId('previous-page').disabled = page <= 1;
        byId('next-page').disabled = page * 50 >= body.meta.total;
    } catch {
        if (request !== pageRequest) return;
        byId('facility-rows').replaceChildren();
        byId('table-page').textContent = '';
        byId('table-status').textContent = 'Daftar belum dapat dimuat. Gunakan Coba lagi untuk memuat ulang.';
        byId('map-retry').hidden = false;
    }
}
async function load() {
    const request = ++loadRequest;
    byId('map-retry').hidden = true;
    byId('map-status').textContent = 'Memuat data…';
    if (map) {
        map.closePopup();
        ++pageRequest; clusters.clearLayers(); markers.clear();
        for (const id of ['facility-rows', 'map-counts', 'map-period', 'table-status', 'table-page']) byId(id).replaceChildren();
        byId('previous-page').disabled = byId('next-page').disabled = true;
    } else byId('facility-fields').replaceChildren();
    try {
        if (!await selectRelease()) { byId('map-status').textContent = 'Belum ada rilis publik.'; return; }
        if (!map) {
            const body = await get(root.dataset.endpoint);
            fields(byId('facility-fields'), body.data); remember();
            byId('map-status').textContent = `Periode fasilitas: ${body.meta.source_periods?.facilities || 'Belum tersedia'}. Rilis: ${release}`;
            return;
        }
        const body = await get(root.dataset.points, filters);
        if (request !== loadRequest) return;
        if (body.type !== 'FeatureCollection' || !Array.isArray(body.features)) throw new Error('shape');
        for (const feature of body.features) {
            const coordinates = feature.geometry?.coordinates;
            const properties = feature.properties;
            if (feature.geometry?.type !== 'Point' || !Array.isArray(coordinates) || coordinates.length !== 2 || !coordinates.every(Number.isFinite)
                || Math.abs(coordinates[0]) > 180 || Math.abs(coordinates[1]) > 90 || !/^\d{11}$/.test(properties?.code)
                || !['verified', 'unverified', 'rejected'].includes(properties.coordinate_status) || markers.has(properties.code)) throw new Error('geometry');
            const marker = L.marker([coordinates[1], coordinates[0]], { title: properties.name, alt: properties.name, icon: L.divIcon({ className: `facility-marker ${properties.coordinate_status}`, html: '<span aria-hidden="true">+</span>', iconSize: [28, 28] }) });
            marker.feature = feature;
            marker.bindPopup(() => popup(feature)); markers.set(properties.code, marker);
        }
        for (const key of ['filtered_registered', 'filtered_mapped', 'filtered_missing']) if (!Number.isSafeInteger(body.meta[key]) || body.meta[key] < 0) throw new Error('counts');
        if (body.meta.filtered_mapped !== markers.size || body.meta.filtered_registered !== body.meta.filtered_mapped + body.meta.filtered_missing) throw new Error('counts');
        clusters.addLayers([...markers.values()]);
        byId('map-fit').click(); remember();
        byId('map-counts').textContent = `${body.meta.filtered_registered} terdaftar · ${body.meta.filtered_mapped} memiliki koordinat · ${body.meta.filtered_missing} tanpa koordinat`;
        byId('map-period').textContent = `Periode fasilitas: ${body.meta.source_periods?.facilities || 'Belum tersedia'} · Rilis: ${release}`;
        byId('map-status').textContent = markers.size ? 'Peta siap. Pilih kelompok titik untuk memperbesar; titik bertumpuk dapat dibuka satu per satu.' : 'Tidak ada titik yang dapat dipetakan. Periksa daftar fasilitas.';
        await loadTable(1);
        if (request === loadRequest && form.elements.regency_code.options.length === 1) loadRegions();
    } catch {
        if (request !== loadRequest) return;
        clusters?.clearLayers(); markers.clear();
        byId('map-status').textContent = 'Data belum dapat dimuat. Rilis tidak diganti otomatis. Coba lagi.';
        byId('map-retry').hidden = false;
    }
}
byId('map-retry').onclick = load;
load();
