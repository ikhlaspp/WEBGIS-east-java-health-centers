<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="Ringkasan data puskesmas Jawa Timur, periode sumber, dan kualitas lokasi pada rilis publik.">
    <title>@yield('title', 'Puskesmas Jawa Timur')</title>
    @vite(['resources/css/app.css', 'resources/js/app.js'])
</head>
<body>
    <a class="skip-link" href="#konten">Lewati ke konten</a>
    <header class="site-header">
        <div class="shell header-inner">
            <a class="brand" href="{{ route('home') }}" aria-label="Puskesmas Jawa Timur — beranda"><span class="brand-symbol" aria-hidden="true"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" focusable="false"><path d="M12 3v18M3 12h18" stroke="currentColor" stroke-width="2"/></svg></span><span>PUSKESMAS<span class="brand-region">JAWA TIMUR</span></span></a>
            <nav aria-label="Navigasi utama"><a data-release-link href="{{ route('home') }}#ringkasan">Ringkasan</a><a data-release-link href="{{ route('map') }}">Peta</a><a data-release-link href="{{ route('home') }}#wilayah">Wilayah</a><a data-release-link href="{{ route('home') }}#metode">Sumber &amp; metode</a></nav>
            <a class="admin-link" href="{{ route('login') }}">Masuk admin <span aria-hidden="true">↗</span></a>
        </div>
    </header>
    <main id="konten" class="shell">@yield('content')</main>
    <footer class="shell site-footer"><span>WebGIS Puskesmas · Jawa Timur</span><p>Data untuk eksplorasi dan penelitian. Bukan penilaian mutu layanan atau waktu tempuh.</p><a href="#konten">Kembali ke atas ↑</a></footer>
</body>
</html>
