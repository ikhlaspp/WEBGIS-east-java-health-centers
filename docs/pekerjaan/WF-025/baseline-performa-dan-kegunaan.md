# Target performa dan kegunaan

Versi 1 · 23 Oktober 2026 · Penyusun: Codex. Baseline engineering kandidat untuk NFR-02/03/04; tidak ada hasil pengukuran aplikasi saat ini.

## Profil yang harus direkam

Staging terpisah, dataset 973 fasilitas, seluruh polygon edisi terpilih, hasil radius precomputed. Catat jumlah vertex, byte compressed/uncompressed dan detail simplifikasi sebelum run. Klien desktop profil minimum 4 core/8 GB; Chrome dan Edge stabil dengan versi aktual direkam. Jaringan 10 Mbps down/2 Mbps up, latency 100 ms, tanpa packet loss buatan. Viewport 360×800, 768×1024, 1366×768. Emulasi 360 px bukan bukti performa perangkat mobile nyata; satu perangkat Android aktual dengan spesifikasi dicatat diperlukan saat uji kegunaan.

| ID | Target | Prosedur / batas pengukuran |
|---|---|---|
| P01 | p95 peta operasional ≤5 detik | 30 navigasi cold browser cache; server cache dicatat, bukan disembunyikan. Dari navigationStart sampai kontrol, data/legenda dan tabel alternatif siap. Tile diukur terpisah; harness tile lokal untuk repeatability, satu smoke provider nyata tanpa load test |
| P02 | p95 tiap kelompok API baca ≤800 ms warm; error <1% | 20 VU, ramp 1 menit, steady 5 menit; minimal 100 respons per kelompok facilities/statistics/map-points/map-regions, bila kurang tambah durasi. Think time 1 detik; mix 30/25/25/20%; catat percentiles per endpoint agar endpoint lambat tidak tertutup agregat |
| P02-COLD | Laporkan cold cache tanpa klaim warm | Satu rangkaian cold API terpisah; catat query/cache warm-up dan latensi. Target warm tidak diberlakukan retroaktif sebagai hasil cold |
| P03 | Interaksi tidak kehilangan input/hasil | 20 kali buka/tutup filter, zoom/pan/ganti wilayah; ukur long tasks dan input response. Target kandidat respons kontrol p95≤200 ms, request data mengikuti P02; catat perangkat aktual |
| U01 | Layout terpakai di ketiga viewport | Tidak ada tombol terpotong; panel/modal bisa ditutup; tabel boleh horizontal scroll terkendali, halaman utama tidak overflow |
| U02 | Keyboard dan label | Semua kontrol berlabel, fokus terlihat/logis, Escape menutup panel, fokus kembali ke tombol; tidak ada keyboard trap |
| U03 | Informasi tanpa warna/peta | Legenda teks dan tabel alternatif; status loading/error diumumkan; no-data tidak sama dengan 0 |

Uji hanya layanan yang dikelola tim; tile/geocoder publik tidak menjadi target load test. Geocoder tidak dipanggil saat request peta. Ukuran produksi yang melampaui fixture harus diuji ulang dengan data rilis penuh; simplifikasi tidak boleh mengubah geometri analisis.

Target 800 ms dan 5 detik mempertahankan usulan planning dengan profil konkret. Tambahan p95/30 navigasi/per-endpoint membuat penilaian terukur; belum janji SLA hosting. Hosting/budget belum dikonfirmasi: ukur pada staging yang nantinya dipilih, dan bila target perlu berubah catat CR sebelum penerimaan hasil, bukan setelah tes gagal. QA merekam environment, jumlah sampel, actual, trace, dan defect; gate rilis memerlukan bukti nyata.
