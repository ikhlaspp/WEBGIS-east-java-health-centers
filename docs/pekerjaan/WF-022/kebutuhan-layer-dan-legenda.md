# Layer peta dan legenda

Versi 1 · 23 Oktober 2026 · Penyusun: Codex. Kandidat kebutuhan visual; kelas tetap disimpan pada run agar perbandingan tidak berubah diam-diam.

| Layer | Isi / default | Legenda dan perilaku |
|---|---|---|
| Basemap | Provider yang diizinkan, attribution selalu terlihat | Tile bukan sumber kebenaran atribut; error tile tidak meniadakan tabel |
| Titik verified | Facility points terverifikasi, cluster bila berdekatan; on | Simbol solid, popup kode/nama/layanan/precision/status/release; dua fasilitas di titik sama tetap dapat dipilih |
| Titik kandidat | Pair unverified jika layak ditampilkan; off | Simbol outline dan label belum diverifikasi; rejected/missing tidak dijadikan marker |
| Batas kab/kecamatan | Polygon sesuai boundary_set; parent/edisi tampil | Outline, tooltip kode/nama; geometri simplified hanya untuk display |
| Choropleth | Satu metrik aktif per level; jumlah fasilitas default | Nilai administratif seluruh scope; sumber/tahun/unit dan kelas selalu tampil |
| Buffer | Run/radius publik yang eligible; off | 1/3/5 km dengan label radius; coverage parsial dan jumlah excluded terlihat |

## Kelas warna tetap

| Metrik | Batas kelas | Makna |
|---|---|---|
| F fasilitas | 0; 1–2; 3–5; 6–10; ≥11 | Count administratif; kelas berlaku pada semua wilayah/level, dapat kurang kontras pada kabupaten tetapi tetap jujur |
| P/F jiwa/fasilitas | ≤30000; >30000–60000; >60000 | Kelas tampilan, bukan ambang hukum tambahan; F=0 memakai kategori tanpa_puskesmas terpisah |
| Kepadatan jiwa/km² | 0; >0–1000; >1000–5000; >5000 | Batas awal engineering; perubahan hanya melalui versi legenda/run baru |
| Defisit indikatif | 0; 1; 2–3; ≥4 | Semakin gelap berarti defisit lebih besar; bukan mutu layanan |

Palet sequential biru terang→gelap untuk kelas numerik; nilai nol memakai warna terang yang jelas. No-data abu-abu berarsir/berlabel “Belum tersedia”; tanpa_puskesmas memakai simbol/warna amber dengan label, bukan Infinity. Jika P hilang dan F=0, tooltip menampilkan kedua kondisi; warna rasio no-data tetap dibedakan dari kasus P diketahui/F=0. Jangan mengandalkan warna saja: legenda teks dan tabel angka wajib.

Pergantian metrik/level mengubah judul, unit dan legenda serentak. Tidak ada quantile otomatis berdasarkan viewport/filter. Bila quantile dipilih lewat perubahan desain, simpan breakpoints, populasi pembentuk kelas dan metode pada run; tampilkan pemberitahuan skala berubah.

Filter layanan/karakter hanya mengubah daftar/marker. Pilihan wilayah menentukan scope statistik administratif. Tooltip polygon memuat nama/kode, nilai/unit, periode P/A/fasilitas, kelengkapan, release/run, jumlah eligible/excluded dan tautan detail. Zoom/pan tidak mengubah nilai administratif; missing dapat diakses lewat tabel, bukan dihitung nol fasilitas.

Kriteria penerimaan: uji batas kelas tepat di 0/1/2/3/5/10/11 dan 30000/60000, no-data vs zero, F=0, perubahan filter, dua level, serta legenda mobile/keyboard. Semua visual harus dapat dijelaskan melalui tabel alternatif.
