@extends('layouts.app')
@section('title', 'Peta puskesmas · Jawa Timur')
@section('content')
<section id="facility-map" class="map-page" data-releases="{{ route('api.v1.releases') }}" data-points="{{ route('api.v1.map.points') }}" data-facilities="{{ route('api.v1.facilities.index') }}" data-detail-base="{{ url('/puskesmas') }}">
    <p class="eyebrow">PERSEBARAN FASILITAS</p><h1>Peta puskesmas Jawa Timur</h1>
    <p>Titik menunjukkan lokasi yang tersedia, termasuk lokasi yang belum terverifikasi. Radius bukan waktu tempuh atau batas layanan.</p>
    <p id="map-status" role="status" aria-live="polite">Memuat rilis peta…</p>
    <button id="map-retry" type="button" hidden>Coba lagi</button>
    <p id="map-period"></p><p id="map-counts"></p>
    <a href="#facility-table">Lewati peta ke daftar fasilitas</a>
    <p id="tile-status" role="status" hidden>Peta dasar belum dapat dimuat. Titik dan daftar fasilitas tetap dapat digunakan. <button id="tile-retry" type="button">Muat ulang peta dasar</button></p>
    <div id="map-canvas" aria-label="Peta interaktif puskesmas; gunakan tombol panah untuk menggeser" tabindex="0"></div>
    <div class="map-toolbar"><button id="map-fit" type="button">Tampilkan semua titik</button><span>Hijau: terverifikasi · Jingga: belum terverifikasi · Abu-abu: ditolak. Angka pada kelompok menunjukkan jumlah titik.</span></div>
    <section id="facility-table" aria-labelledby="facility-list-title">
        <h2 id="facility-list-title">Daftar fasilitas</h2><p>Fasilitas tanpa koordinat tetap tercantum di sini, tanpa marker pengganti.</p>
        <p id="table-status" role="status"></p>
        <div class="map-table-scroll"><table><thead><tr><th>Fasilitas</th><th>Layanan</th><th>Status lokasi</th><th>Aksi</th></tr></thead><tbody id="facility-rows"></tbody></table></div>
        <div class="map-toolbar"><button id="previous-page" type="button" disabled>Sebelumnya</button><span id="table-page"></span><button id="next-page" type="button" disabled>Berikutnya</button></div>
    </section>
    <noscript>Aktifkan JavaScript untuk memuat peta dan daftar fasilitas.</noscript>
</section>
@endsection
