@extends('layouts.app')
@section('title', 'Peta puskesmas · Jawa Timur')
@section('content')
<section id="facility-map" class="map-page" data-coverage="{{ route('api.v1.analysis.buffers') }}" data-thematic="{{ route('api.v1.map.regions') }}" data-releases="{{ route('api.v1.releases') }}" data-regions="{{ route('api.v1.regions') }}" data-points="{{ route('api.v1.map.points') }}" data-facilities="{{ route('api.v1.facilities.index') }}" data-detail-base="{{ url('/puskesmas') }}">
    <p class="eyebrow">PERSEBARAN FASILITAS</p><h1>Peta puskesmas Jawa Timur</h1>
    <p>Titik menunjukkan lokasi yang tersedia, termasuk lokasi yang belum terverifikasi. Radius bukan waktu tempuh atau batas layanan.</p>
    <p id="map-status" role="status" aria-live="polite">Memuat rilis peta…</p>
    <button id="map-retry" type="button" hidden>Coba lagi</button>
    <form id="map-filters" class="map-filters">
        <label for="filter-q">Nama atau kode<input id="filter-q" name="q" type="search" maxlength="100"></label>
        <label for="filter-regency_code">Kabupaten/kota<select id="filter-regency_code" name="regency_code"><option value="">Semua kabupaten/kota</option></select></label>
        <label for="filter-district_code">Kecamatan<select id="filter-district_code" name="district_code" disabled><option value="">Semua kecamatan</option></select></label>
        <label for="filter-service_type">Layanan<select id="filter-service_type" name="service_type"><option value="">Semua layanan</option><option>Rawat Inap</option><option>Non Rawat Inap</option></select></label>
        <label for="filter-area_type">Jenis wilayah<select id="filter-area_type" name="area_type"><option value="">Semua jenis wilayah</option><option>Perdesaan</option><option>Perkotaan</option><option>Terpencil</option><option>Sangat Terpencil</option></select></label>
        <label for="filter-coordinate_status">Status lokasi<select id="filter-coordinate_status" name="coordinate_status"><option value="">Semua status</option><option value="verified">Terverifikasi</option><option value="unverified">Belum terverifikasi</option><option value="missing">Tanpa koordinat</option><option value="rejected">Ditolak</option></select></label>
        <button type="submit">Terapkan filter</button><button type="reset">Reset filter</button>
        <p id="region-status" role="status"></p><button id="region-retry" type="button" hidden>Muat ulang wilayah</button>
    </form>
    <p id="map-period"></p><p id="map-counts"></p>
    <a href="#facility-table">Lewati peta ke daftar fasilitas</a>
    <p id="tile-status" role="status" hidden>Peta dasar belum dapat dimuat. Titik dan daftar fasilitas tetap dapat digunakan. <button id="tile-retry" type="button">Muat ulang peta dasar</button></p>
    <div id="map-canvas" aria-label="Peta interaktif puskesmas; gunakan tombol panah untuk menggeser" tabindex="0"></div>
    <section aria-labelledby="thematic-title">
        <h2 id="thematic-title">Indikator wilayah</h2>
        <div class="map-filters">
            <label for="thematic-metric">Indikator<select id="thematic-metric"><option value="">Tanpa warna wilayah</option><option value="count">Jumlah fasilitas</option><option value="density">Kepadatan penduduk</option><option value="population_per_facility">Penduduk per fasilitas</option><option value="indicative_deficit">Defisit indikatif</option></select></label>
            <label for="thematic-level">Tingkat wilayah<select id="thematic-level"><option value="regency">Kabupaten/kota</option><option value="district">Kecamatan dalam kabupaten/kota terpilih</option></select></label>
        </div>
        <p>Warna menggunakan seluruh fasilitas dalam wilayah pada rilis yang sama. Filter nama, layanan, jenis wilayah, status lokasi, dan kecamatan pada daftar tidak mengubah indikator. Untuk tingkat kecamatan, pilih kabupaten/kota lalu terapkan filter.</p>
        <p>Defisit bersifat indikatif, bukan kebutuhan layanan resmi. Kepadatan adalah penduduk per km². Nilai tidak tersedia berbeda dari nol.</p>
        <p id="thematic-status" role="status" aria-live="polite"></p><button id="thematic-retry" type="button" hidden>Coba lagi indikator</button>
        <button id="thematic-fit" type="button" disabled>Tampilkan seluruh wilayah</button>
        <ul id="thematic-legend" class="thematic-legend" aria-label="Legenda indikator"></ul>
        <details><summary>Nilai indikator per wilayah</summary><div class="map-table-scroll"><table><thead><tr><th>Wilayah</th><th>Nilai</th></tr></thead><tbody id="thematic-rows"></tbody></table></div></details>
    </section>
    <div class="map-toolbar"><button id="map-fit" type="button">Tampilkan semua titik</button><span>Hijau: terverifikasi · Jingga: belum terverifikasi · Abu-abu: ditolak. Angka pada kelompok menunjukkan jumlah titik.</span></div>
    <section aria-labelledby="coverage-title">
        <h2 id="coverage-title">Cakupan radius geometris</h2>
        <div class="map-filters"><label for="coverage-radius">Radius analisis<select id="coverage-radius"><option value="">Tanpa lapisan cakupan</option><option value="1000">1 km</option><option value="3000">3 km</option><option value="5000">5 km</option></select></label></div>
        <p>Hanya titik yang memenuhi syarat verifikasi dan presisi yang digunakan. Area cakupan merupakan gabungan radius yang dipotong batas kecamatan; bukan waktu tempuh, akses jalan, atau batas layanan resmi.</p>
        <p>Filter kabupaten/kota dan kecamatan menentukan wilayah hasil. Filter nama, layanan, jenis wilayah, dan status lokasi tidak menghitung ulang analisis. Persentase memakai luas geometri wilayah, bukan luas dari tabel sumber. Cakupan parsial tidak mewakili seluruh fasilitas.</p>
        <p><span class="coverage-swatch" aria-hidden="true"></span>Hijau kebiruan bergaris putus: area tercakup. Tanpa titik layak, hasil ditampilkan sebagai tidak tersedia, bukan 0%.</p>
        <p id="coverage-status" role="status" aria-live="polite"></p>
        <button id="coverage-retry" type="button" hidden>Coba lagi cakupan</button><button id="coverage-fit" type="button" disabled>Tampilkan area cakupan</button>
        <details><summary>Hasil cakupan per kecamatan</summary><div class="map-table-scroll"><table class="coverage-table"><thead><tr><th>Kecamatan</th><th>Cakupan</th><th>Layak / terdaftar</th><th>Dikecualikan</th><th>Kelengkapan</th></tr></thead><tbody id="coverage-rows"></tbody></table></div></details>
    </section>
    <section id="facility-table" aria-labelledby="facility-list-title">
        <h2 id="facility-list-title">Daftar fasilitas</h2><p>Fasilitas tanpa koordinat tetap tercantum di sini, tanpa marker pengganti.</p>
        <p id="table-status" role="status"></p>
        <div class="map-table-scroll"><table><thead><tr><th>Fasilitas</th><th>Layanan</th><th>Status lokasi</th><th>Aksi</th></tr></thead><tbody id="facility-rows"></tbody></table></div>
        <div class="map-toolbar"><button id="previous-page" type="button" disabled>Sebelumnya</button><span id="table-page"></span><button id="next-page" type="button" disabled>Berikutnya</button></div>
    </section>
    <noscript>Aktifkan JavaScript untuk memuat peta dan daftar fasilitas.</noscript>
</section>
@endsection
