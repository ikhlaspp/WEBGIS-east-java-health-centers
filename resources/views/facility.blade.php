@extends('layouts.app')
@section('title', 'Detail puskesmas · Jawa Timur')
@section('content')
<section id="facility-detail" class="map-page" data-releases="{{ route('api.v1.releases') }}" data-endpoint="{{ route('api.v1.facilities.show', ['code' => $code]) }}">
    <p class="eyebrow">IDENTITAS FASILITAS</p><h1>Detail puskesmas</h1>
    <p id="map-status" role="status" aria-live="polite">Memuat detail…</p><button id="map-retry" type="button" hidden>Coba lagi</button>
    <dl id="facility-fields"></dl>
    <p id="facility-location-note"></p>
    <section aria-labelledby="facility-sources-title">
        <h2 id="facility-sources-title">Sumber dan keterbatasan</h2>
        <div id="facility-sources"></div>
    </section>
    <a data-release-link href="{{ route('map') }}">Kembali ke peta</a>
    <noscript>Aktifkan JavaScript untuk memuat detail fasilitas.</noscript>
</section>
@endsection
