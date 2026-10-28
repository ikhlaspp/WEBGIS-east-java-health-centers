import L from 'leaflet';

export function coverageMap(map, endpoint, get, context) {
    const byId = (id) => document.getElementById(id);
    const radius = byId('coverage-radius');
    const number = new Intl.NumberFormat('id-ID', { maximumFractionDigits: 2 });
    const text = (tag, value) => { const node = document.createElement(tag); node.textContent = value; return node; };
    let layer, request = 0;
    function clear() {
        ++request;
        if (layer) map.removeLayer(layer);
        layer = null;
        byId('coverage-rows').replaceChildren();
        byId('coverage-status').textContent = '';
        byId('coverage-retry').hidden = true;
        byId('coverage-fit').disabled = true;
    }
    async function load() {
        clear();
        const current = request;
        const selected = Number(radius.value);
        if (!selected) return;
        const { ready, regency, district } = context();
        if (!ready) { byId('coverage-status').textContent = 'Muat data peta terlebih dahulu.'; return; }
        byId('coverage-status').textContent = 'Memuat cakupan radius...';
        try {
            const body = await get(endpoint, { radius_m: selected, geometry_detail: 'full', ...(regency ? { regency_code: regency } : {}), ...(district ? { district_code: district } : {}) });
            if (current !== request) return;
            if (body.type !== 'FeatureCollection' || !Array.isArray(body.features) || body.meta?.radius_m !== selected) throw new Error('identity');
            const seen = new Set();
            let unavailable = 0, partial = 0, eligible = 0, excluded = 0;
            const entries = body.features.map((feature) => {
                const p = feature.properties;
                if (feature.type !== 'Feature' || !p || !/^\d{7}$/.test(p.code) || feature.id !== p.code || seen.has(p.code) || p.radius_m !== selected || !['complete', 'partial', 'unavailable'].includes(p.completeness)) throw new Error('feature');
                seen.add(p.code);
                for (const key of ['registered_count', 'eligible_count', 'excluded_count', 'contributing_count']) if (!Number.isSafeInteger(p[key]) || p[key] < 0) throw new Error('counts');
                if (p.registered_count !== p.eligible_count + p.excluded_count) throw new Error('counts');
                eligible += p.eligible_count; excluded += p.excluded_count;
                if (p.completeness === 'unavailable') {
                    if (p.coverage_pct !== null || p.covered_area_m2 !== null || p.geometry_area_m2 !== null || feature.geometry !== null || p.eligible_count !== 0 || p.contributing_count !== 0 || p.reason !== 'no_eligible_points') throw new Error('unavailable');
                    unavailable++;
                } else {
                    if (p.completeness === 'partial') partial++;
                    for (const key of ['coverage_pct', 'covered_area_m2', 'geometry_area_m2']) if (typeof p[key] !== 'number' || !Number.isFinite(p[key]) || p[key] < 0) throw new Error('value');
                    if (p.coverage_pct > 100 || p.geometry_area_m2 <= 0 || p.covered_area_m2 > p.geometry_area_m2 || (p.covered_area_m2 > 0 && !feature.geometry)) throw new Error('value');
                    if (Math.abs(p.coverage_pct - p.covered_area_m2 / p.geometry_area_m2 * 100) > 0.000001) throw new Error('value');
                }
                if (feature.geometry !== null) {
                    const geometry = feature.geometry;
                    if (!['Polygon', 'MultiPolygon'].includes(geometry?.type)) throw new Error('geometry');
                    const polygons = geometry.type === 'Polygon' ? [geometry.coordinates] : geometry.coordinates;
                    if (!Array.isArray(polygons) || !polygons.length || polygons.some((polygon) => !Array.isArray(polygon) || !polygon.length || polygon.some((ring) => !Array.isArray(ring) || ring.length < 4 || ring.some((point) => !Array.isArray(point) || point.length !== 2 || !point.every(Number.isFinite) || Math.abs(point[0]) > 180 || Math.abs(point[1]) > 90)))) throw new Error('geometry');
                    if (polygons.some((polygon) => polygon.some((ring) => ring[0][0] !== ring.at(-1)[0] || ring[0][1] !== ring.at(-1)[1]))) throw new Error('geometry');
                }
                return { feature, value: p.coverage_pct === null ? 'Tidak tersedia' : `${number.format(p.coverage_pct)}%`, status: { complete: 'Lengkap', partial: 'Parsial', unavailable: 'Tidak tersedia: belum ada titik layak analisis' }[p.completeness] };
            });
            layer = L.featureGroup();
            for (const { feature, value, status } of entries) {
                const p = feature.properties;
                const row = document.createElement('tr');
                row.append(text('td', `${p.name} (${p.code})`), text('td', value), text('td', `${p.eligible_count} / ${p.registered_count}`), text('td', p.excluded_count), text('td', status));
                byId('coverage-rows').append(row);
                if (feature.geometry) {
                    const popup = document.createElement('div');
                    popup.append(text('strong', p.name), text('p', `Radius ${selected / 1000} km: ${value}`), text('p', status), text('p', `${p.contributing_count} titik berkontribusi, termasuk dari luar wilayah bila beririsan.`));
                    L.geoJSON(feature, { style: { color: '#087f8c', weight: 2, dashArray: '5 3', fillColor: '#49c5b6', fillOpacity: 0.35 } }).bindPopup(popup).addTo(layer);
                }
            }
            layer.addTo(map);
            byId('coverage-fit').disabled = !layer.getLayers().length;
            byId('coverage-status').textContent = entries.length ? `Radius ${selected / 1000} km: ${entries.length} kecamatan; ${unavailable} tidak tersedia, ${partial} parsial. Fasilitas dalam wilayah terpilih: ${eligible} layak analisis, ${excluded} dikecualikan.` : 'Tidak ada hasil cakupan untuk wilayah ini.';
        } catch {
            if (current !== request) return;
            clear();
            byId('coverage-status').textContent = 'Cakupan belum dapat dimuat. Tidak ada nilai nol pengganti. Titik dan daftar tetap dapat digunakan.';
            byId('coverage-retry').hidden = false;
        }
    }
    radius.onchange = load;
    byId('coverage-retry').onclick = load;
    byId('coverage-fit').onclick = () => {
        if (layer?.getBounds().isValid()) { map.invalidateSize(); map.fitBounds(layer.getBounds(), { padding: [25, 25], maxZoom: 13, animate: false }); }
    };
    return { clear, load };
}
