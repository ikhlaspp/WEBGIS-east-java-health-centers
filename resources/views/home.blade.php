@extends('layouts.app')
@section('title', 'Ringkasan Puskesmas Jawa Timur')
@section('content')
<div id="dashboard" data-releases-url="{{ route('api.v1.releases') }}" data-statistics-url="{{ route('api.v1.statistics') }}" data-regions-url="{{ route('api.v1.regions') }}" data-sources-url="{{ route('api.v1.sources') }}">
    <section class="hero" aria-labelledby="hero-title">
        <div><p class="eyebrow"><span class="status-dot" aria-hidden="true"></span> OBSERVATORIUM KESEHATAN WILAYAH</p><h1 id="hero-title">Mengenal sebaran<br>puskesmas <em>Jawa Timur.</em></h1><p class="hero-copy">Telusuri jumlah fasilitas dan kualitas data lokasinya. Satu rilis, dengan periode dan sumber yang dapat ditelusuri.</p><a class="primary-link" href="#ringkasan">Lihat ringkasan <span aria-hidden="true">↓</span></a></div>
        <aside class="hero-note"><span class="section-number">01 / MEMBACA DATA</span><h2>Terdaftar tidak selalu terpetakan.</h2><p>Fasilitas tanpa koordinat tetap dihitung. Titik di peta belum tentu memenuhi syarat untuk analisis radius.</p><div class="note-rule"></div><span class="small-label">JUMLAH · LOKASI · KUALITAS</span></aside>
    </section>
    <section id="ringkasan" class="dashboard-section" aria-labelledby="summary-title" aria-busy="true">
        <div class="section-heading"><div><p class="eyebrow">RINGKASAN RILIS PUBLIK</p><h2 id="summary-title">Angka yang perlu dibedakan</h2></div><span id="release-label" class="release-label">Memuat rilis…</span></div>
        <div id="data-status" class="data-status" role="status" aria-live="polite"><p id="status-text">Memuat ringkasan data…</p><button id="retry-data" type="button" hidden>Coba lagi</button></div>
        <noscript><p class="data-status">Aktifkan JavaScript untuk mengambil ringkasan rilis publik. Angka tidak ditampilkan sebelum data tersedia.</p></noscript>
        <div class="stat-grid">
            <dl class="stat-card primary-stat"><dt>Fasilitas terdaftar</dt><dd data-count="registered">—</dd><dd class="stat-description">Seluruh fasilitas dalam rilis</dd></dl>
            <dl class="stat-card"><dt>Memiliki koordinat</dt><dd data-count="mapped">—</dd><dd class="stat-description">Terpetakan, termasuk yang belum terverifikasi</dd></dl>
            <dl class="stat-card"><dt>Lokasi terverifikasi</dt><dd data-count="verified">—</dd><dd class="stat-description">Status lokasi sudah diverifikasi</dd></dl>
            <dl class="stat-card"><dt>Tanpa koordinat</dt><dd data-count="missing">—</dd><dd class="stat-description">Tetap termasuk fasilitas terdaftar</dd></dl>
        </div>
        <p id="coverage-note" class="coverage-note">Kelengkapan lokasi akan ditampilkan setelah data tersedia.</p>
        <div id="release-details" class="period-panel" hidden><h3>Periode sumber</h3><dl><div><dt>Fasilitas</dt><dd id="facility-period"></dd></div><div><dt>Penduduk</dt><dd id="population-period"></dd></div><div><dt>Luas wilayah</dt><dd id="area-period"></dd></div></dl><details><summary>Identitas rilis &amp; analisis</summary><p id="release-identity"></p></details></div>
    </section>
    <section id="wilayah" class="dashboard-section" aria-labelledby="regions-title"><div class="section-heading"><div><p class="eyebrow">CAKUPAN ADMINISTRATIF</p><h2 id="regions-title">Wilayah dalam ringkasan</h2></div><p id="region-summary">Menunggu data rilis.</p></div><ul id="region-list" class="region-list" aria-label="Kabupaten dan kota"></ul><p id="boundary-note" class="muted"></p></section>
    <section id="metode" class="dashboard-section methods" aria-labelledby="methods-title"><div><p class="eyebrow">SUMBER &amp; INTERPRETASI</p><h2 id="methods-title">Kenali batas datanya.</h2><p>Periode fasilitas, penduduk, dan luas wilayah dapat berbeda. Ringkasan ini mempertahankan rilis yang sama selama Anda membacanya.</p></div><div><h3>Bagaimana membaca analisis?</h3><p>Jumlah fasilitas mengikuti wilayah administratif. Analisis radius hanya memakai titik fasilitas yang memenuhi syarat verifikasi. Radius geometris bukan waktu tempuh, wilayah layanan resmi, atau ukuran akses jalan.</p><h3>Sumber pada rilis ini</h3><ul id="source-list" class="source-list"><li>Sumber akan tampil bersama data rilis.</li></ul><ul id="warning-list" class="warning-list" aria-label="Keterbatasan sumber"></ul></div></section>
</div>
@endsection
