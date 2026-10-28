import L from 'leaflet';

export function thematicMap(map, endpoint, get, context) {
    const byId = (id) => document.getElementById(id);
    const metric = byId('thematic-metric');
    const level = byId('thematic-level');
    const names = { count: 'Jumlah fasilitas', density: 'Kepadatan penduduk', population_per_facility: 'Penduduk per fasilitas', indicative_deficit: 'Defisit indikatif' };
    const units = { count: 'fasilitas', density: 'jiwa/km²', population_per_facility: 'jiwa/fasilitas', indicative_deficit: 'fasilitas' };
    const number = new Intl.NumberFormat('id-ID', { maximumFractionDigits: 2 });
    const text = (tag, value) => { const node = document.createElement(tag); node.textContent = value; return node; };
    let layer, request = 0;
    function clear() {
        ++request;
        if (layer) map.removeLayer(layer);
        layer = null;
        byId('thematic-legend').replaceChildren();
        byId('thematic-rows').replaceChildren();
        byId('thematic-status').textContent = '';
        byId('thematic-retry').hidden = true;
        byId('thematic-fit').disabled = true;
    }
    async function load() {
        clear();
        const current = request;
        const selected = metric.value;
        if (!selected) return;
        const { ready, parent } = context();
        if (!ready) { byId('thematic-status').textContent = 'Muat data peta terlebih dahulu.'; return; }
        if (level.value === 'district' && !parent) { byId('thematic-status').textContent = 'Pilih kabupaten/kota dan terapkan filter untuk melihat kecamatan.'; return; }
        byId('thematic-status').textContent = 'Memuat indikator wilayah...';
        try {
            const body = await get(endpoint, { metric: selected, level: level.value, geometry_detail: 'display', ...(level.value === 'district' ? { parent_code: parent } : {}) });
            if (current !== request) return;
            const expectedMetric = selected === 'count' ? 'facility_count' : selected;
            const legend = body.meta?.legend;
            const color = (value) => typeof value === 'string' && /^#[0-9a-f]{6}$/i.test(value);
            if (body.type !== 'FeatureCollection' || !Array.isArray(body.features) || body.meta.metric !== expectedMetric || body.meta.level !== level.value
                || !legend || legend.metric !== expectedMetric || !Array.isArray(legend.colors) || !Array.isArray(legend.labels) || !Array.isArray(legend.upper_bounds)
                || legend.colors.length !== legend.labels.length || legend.colors.length !== legend.upper_bounds.length + 1 || !legend.colors.every(color)
                || !legend.labels.every((label) => typeof label === 'string') || !legend.upper_bounds.every((value, index, bounds) => Number.isFinite(value) && value >= 0 && (index === 0 || value > bounds[index - 1]))
                || !color(legend.special?.no_data?.color) || !color(legend.special?.without_facility?.color)) throw new Error('legend');
            const seen = new Set();
            const entries = body.features.map((feature) => {
                const p = feature.properties;
                if (feature.type !== 'Feature' || !p || feature.id !== p.code || p.metric !== expectedMetric || !(level.value === 'district' ? /^\d{7}$/ : /^\d{4}$/).test(p.code) || seen.has(p.code)
                    || (p.value !== null && (typeof p.value !== 'number' || !Number.isFinite(p.value) || p.value < 0))
                    || !['Polygon', 'MultiPolygon'].includes(feature.geometry?.type)) throw new Error('feature');
                const polygons = feature.geometry.type === 'Polygon' ? [feature.geometry.coordinates] : feature.geometry.coordinates;
                if (!Array.isArray(polygons) || !polygons.length || polygons.some((polygon) => !Array.isArray(polygon) || !polygon.length || polygon.some((ring) => !Array.isArray(ring) || ring.length < 4 || ring.some((point) => !Array.isArray(point) || point.length !== 2 || !point.every(Number.isFinite) || Math.abs(point[0]) > 180 || Math.abs(point[1]) > 90)))) throw new Error('geometry');
                if (polygons.some((polygon) => polygon.some((ring) => ring[0][0] !== ring.at(-1)[0] || ring[0][1] !== ring.at(-1)[1]))) throw new Error('geometry');
                seen.add(p.code);
                const special = p.value === null ? (selected === 'population_per_facility' && p.without_facility ? 'without_facility' : 'no_data') : null;
                if (!special && (!Number.isInteger(p.class) || p.class < 0 || p.class >= legend.colors.length)) throw new Error('class');
                return { feature, fill: special ? legend.special[special].color : legend.colors[p.class], value: p.value === null ? (special === 'without_facility' ? 'Tanpa fasilitas; rasio tidak tersedia' : 'Data tidak tersedia') : `${number.format(p.value)} ${units[selected]}` };
            });
            layer = L.featureGroup();
            for (const entry of entries) {
                const p = entry.feature.properties;
                const popup = document.createElement('div');
                popup.append(text('strong', p.name), text('p', `${names[selected]}: ${entry.value}`), text('p', p.completeness === 'partial' ? 'Data sumber parsial.' : ''));
                L.geoJSON(entry.feature, { style: { color: '#435b55', weight: 1, fillColor: entry.fill, fillOpacity: 0.55 } }).bindPopup(popup).addTo(layer);
                const row = document.createElement('tr');
                row.append(text('td', `${p.name} (${p.code})`), text('td', entry.value));
                byId('thematic-rows').append(row);
            }
            layer.addTo(map);
            byId('thematic-fit').disabled = !entries.length;
            if (entries.length) byId('thematic-fit').click();
            const labels = legend.labels.map((label, index) => [label, legend.colors[index]]);
            labels.push(['Data tidak tersedia', legend.special.no_data.color]);
            if (selected === 'population_per_facility') labels.push(['Tanpa fasilitas; rasio tidak tersedia', legend.special.without_facility.color]);
            for (const [label, fill] of labels) {
                const item = text('li', label.startsWith('Data tidak') || label.startsWith('Tanpa fasilitas') ? label : `${label} ${units[selected]}`);
                const swatch = document.createElement('span'); swatch.className = 'legend-swatch'; swatch.style.backgroundColor = fill; swatch.setAttribute('aria-hidden', 'true'); item.prepend(swatch);
                byId('thematic-legend').append(item);
            }
            byId('thematic-status').textContent = entries.length ? `${names[selected]}: ${entries.length} wilayah. ${entries.filter((entry) => entry.feature.properties.value === null).length} nilai tidak tersedia.` : 'Tidak ada wilayah untuk pilihan ini.';
        } catch {
            if (current !== request) return;
            clear();
            byId('thematic-status').textContent = 'Indikator wilayah belum dapat dimuat. Titik dan daftar fasilitas tetap dapat digunakan.';
            byId('thematic-retry').hidden = false;
        }
    }
    metric.onchange = load;
    byId('thematic-fit').onclick = () => {
        if (layer?.getBounds().isValid()) {
            map.invalidateSize();
            map.fitBounds(layer.getBounds(), { padding: [25, 25], maxZoom: 12, animate: false });
        }
    };
    level.onchange = load;
    byId('thematic-retry').onclick = load;
    return { clear, load };
}
