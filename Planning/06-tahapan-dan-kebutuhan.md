# Tahapan pengerjaan dan kebutuhan pendukung

## Asumsi kapasitas

Rencana memakai 3 anggota tim sebagaimana proposal, dengan perkiraan 12–15 jam per orang per minggu selama 8 minggu: kapasitas 288–360 jam orang. Pembagian di bawah adalah peran yang disarankan, bukan penetapan nama atau komitmen anggota. Peran A menangani data/GIS, B backend/Supabase, dan C frontend/pengujian; semua ikut memeriksa sumber dan UAT.

Cadangan waktu diperlukan terutama untuk 408 lokasi kosong, 565 kandidat yang belum terverifikasi, pembuktian kode wilayah dan pencarian polygon historis. Bila pemeriksaan manual belum selesai, kurangi klaim hasil analisis dan labeli cakupan parsial; jangan menggantikan koordinat yang hilang dengan centroid agar target terlihat terpenuhi.

## Jadwal delapan minggu

| Minggu | Fokus dan pekerjaan | Penanggung jawab peran | Hasil/gerbang |
|---|---|---|---|
| 1 | Tetapkan ruang lingkup; periksa master; cari kode/polygon; keputusan tahun; buat repo dan environment | A+B+C | FR baseline, katalog sumber, sampel polygon, keputusan dataset; G0 |
| 2 | ETL awal, mapping alias, review OCR/unit; mulai geocoding review; schema dan migration test | A+B; C bantu QA sumber | Master wilayah dan staging tervalidasi strukturnya; G1 |
| 3 | Lanjut verifikasi lokasi; indikator dan buffer fixture; API daftar/detail/statistik; wireframe interaktif | A+B+C | Slice satu kabupaten dari sumber ke peta; review metode |
| 4 | Cakupan kab/kota penuh; Leaflet marker/filter/detail; choropleth; uji formula/join | B+C; A review data | Fitur inti membaca satu release_id; G2 |
| 5 | Buffer hasil batch; kualitas data di UI; Colab/Folium HTML; kurasi lokasi dan metadata | A+C; B job/import | P0 analisis dan notebook end-to-end dengan cakupan dinyatakan |
| 6 | Admin/ekspor P1 bila kapasitas cukup; keamanan, idempotensi dan rollback; perbaikan data | B+C; A finalisasi data | Kandidat rilis, izin akses dan audit; G3 |
| 7 | Pengujian penuh, performance, restore, UAT; perbaikan defect | C koordinator, semua reviewer | Bukti uji, daftar defect dan retest; G4 |
| 8 | Finalisasi laporan, deployment, demo, panduan, backup dan serah terima | A+B+C | Paket akademik dan aplikasi sesuai cakupan; G5 |

G0 = kebutuhan/metode dipahami; G1 = kode/sumber/struktur tersedia; G2 = alur aplikasi inti berjalan; G3 = kualitas data dan rilis jelas; G4 = uji P0 serta UAT lulus; G5 = deployment dan penyerahan terverifikasi. Pekerjaan UI dapat memakai fixture saat polygon resmi menunggu, tetapi hasil fixture tidak boleh dipresentasikan sebagai hasil penelitian.

## Backlog yang dapat langsung dijadikan issue

| ID | Pekerjaan dan definisi selesai | Dependensi | Peran | Estimasi jam orang |
|---|---|---|---|---:|
| BK-01 | Finalisasi matriks FR dan keputusan sumber/tahun; dokumentasikan perubahan MySQL | — | Semua | 8 |
| BK-02 | Buat repo, Laravel, dependency lock, CI dan environment test | BK-01 | B+C | 12 |
| BK-03 | Lengkapi katalog 49 berkas, sumber primer dan locator | BK-01 | A | 12 |
| BK-04 | Ambil kode/polygon dan periksa lisensi/edisi/CRS/pulau | BK-03 | A | 20 |
| BK-05 | Alias/crosswalk, Sempol–Ijen, wilayah nol dan perbedaan nama selesai | BK-04 | A+B | 20 |
| BK-06 | Verifikasi penduduk/luas berisiko, tahun, unit dan OCR | BK-03 | A+C | 24 |
| BK-07 | Cari 408 lokasi, review 565 kandidat, bukti dan mutu lokasi | BK-03, BK-04 | Semua | 60 |
| BK-08 | Migration domain, role, constraint, GiST, staging dan impor idempotent | BK-02, BK-04 | B | 24 |
| BK-09 | Rumus, buffer, manifest run dan notebook reproduktif | BK-05, BK-06, data lokasi terverifikasi | A | 24 |
| BK-10 | API release, wilayah, fasilitas, statistik dan error contract | BK-08 | B | 20 |
| BK-11 | Dashboard, peta, filter, cluster, popup dan tabel | BK-10 | C | 24 |
| BK-12 | Choropleth, buffer, detail indikator dan sumber | BK-09, BK-11 | A+C | 18 |
| BK-13 | HTML Folium dan kesetaraan rilis dengan aplikasi | BK-09 | A | 10 |
| BK-14 | Admin/ekspor P1; audit, izin dan publish rollback | BK-08, BK-10 | B+C | 20 |
| BK-15 | Uji terintegrasi, keamanan, performa, restore dan retest | Slice implementasi tersedia | Semua | 28 |
| BK-16 | UAT dan perbaikan hasil | BK-12, BK-15 | C+semua | 12 |
| BK-17 | Hosting, dokumentasi, laporan akhir, demo dan backup | BK-15, BK-16 | Semua | 16 |
| | **Total estimasi awal** | | | **352** |

352 jam berada dekat batas atas kapasitas 8 minggu. BK-07 dapat membesar: 973 pemeriksaan × rata-rata 3 menit saja mendekati 49 jam, belum termasuk pencarian kasus sulit. Bila throughput aktual tidak cukup, prioritaskan P0 dan jadwalkan P1 sesudahnya atau tambah durasi. Jangan mengurangi validasi sumber penting untuk mengejar antarmuka tambahan.

## Bahan dan akun yang dibutuhkan

| Kebutuhan | Status sekarang | Cara menyiapkan | Kapan |
|---|---|---|---|
| Proposal dan data sumber | Tersedia di Archives | Pertahankan berkas; hash sudah disiapkan | Selesai untuk inventaris |
| Master kode 2023/2024 dan crosswalk | Belum tersedia lokal | Unduh sumber resmi yang cocok; review nama/kode | Minggu1–2 |
| Polygon administrasi historis | Belum tersedia lokal | Cari BIG/instansi resmi; catat lisensi, edisi, CRS dan coverage pulau | Minggu1–2 |
| Koordinat fasilitas yang bisa dibuktikan | 565 kandidat, 408 kosong | Registri/dinas/POI berizin dan verifikasi | Minggu1–6 |
| Sumber angka alternatif/OCR | Catatan ada, bukti per nilai belum lengkap | Lengkapi URL dan tabel/halaman; cek ulang | Minggu1–3 |
| Akun Supabase | Belum diperiksa/dibuat | Project dev/test/prod, region, password dan backup policy | Minggu2 |
| PHP/Composer/Laragon | Folder proyek ada; kompatibilitas runtime belum diaudit | PHP≥8.3 untuk Laravel 13, PDO PostgreSQL, OpenSSL dan ekstensi Laravel | Minggu1 |
| Node dan package manager | Dibutuhkan untuk build frontend | Pilih versi yang didukung toolchain lalu lock | Minggu1 |
| Python/Colab dan QGIS | Colab sesuai proposal; QGIS opsional untuk QA | Lock environment, simpan notebook, cek proyeksi secara visual | Minggu1–2 |
| Hosting Laravel dan HTTPS | Belum dipilih | PHP, public document root, worker/cron, env rahasia, outbound DB | Minggu6–8 |
| Provider tile | Belum dipilih untuk produksi | Sesuaikan penggunaan, atribusi, cache, kuota dan biaya | Minggu3 |
| Provider geocoding | Notebook memakai Nominatim; belum dipilih ulang | Pilihan sadar sesuai kebijakan batch, lisensi penyimpanan dan anggaran | Minggu1–2 |
| Repository remote dan CI | Belum ada konfigurasi proyek | Branch, review, secret test, lint/unit tests | Minggu1 |
| Peserta UAT dan alat pencatatan | Belum dijadwalkan | Minimal5 peserta sebagai target, instrumen dan bukti | Minggu6–7 |

Supabase tidak menggantikan hosting PHP. Notebook dan file HTML hanya memenuhi bagian penelitian/artefak; aplikasi Laravel tetap memerlukan server. Untuk tile OSM publik, tampilkan atribusi, patuhi cache serta identifikasi, dan jangan prefetch/download massal untuk offline. Provider produksi harus mendukung beban yang diharapkan. [Kebijakan tile OSM](https://operations.osmfoundation.org/policies/tiles/).

## Anggaran yang perlu ditentukan

Belum ada budget dalam proposal. Karena harga dan kuota dapat berubah, tabel ini berisi komponen perhitungan, bukan harga yang dibuat-buat.

| Komponen | Rumus/perkiraan kebutuhan |
|---|---|
| Supabase | Paket database + storage + egress + backup/PITR bila diperlukan; ukur polygon/artefak setelah impor |
| Hosting Laravel | Biaya bulanan hosting/VPS yang mendukung queue/cron dan PostgreSQL remote |
| Domain | Opsional untuk demo; biaya tahunan bila memakai domain sendiri |
| Geocoding | Jumlah query unik setelah cache × tarif provider; beberapa kandidat per 408 data kosong dapat menambah permintaan |
| Tile | Pengguna × sesi × perkiraan request tile per sesi, mengikuti kebijakan provider |
| Backup | Ukuran database dan berkas × salinan × retensi |
| Verifikasi data | Jam orang, komunikasi sumber, atau survei bila disetujui dalam lingkup penelitian |

Paket gratis dapat dievaluasi untuk prototipe setelah batas paket diperiksa; jangan menjanjikan seluruh hosting/backup/geocoding selalu gratis. Pembelian layanan belum diperlukan untuk menyelesaikan perencanaan ini.

## Register risiko

| Risiko | Dampak | Mitigasi dan pemicu tindakan |
|---|---|---|
| Koordinat hanya 58,07% terisi dan belum diverifikasi | Buffer bias, banyak fasilitas tidak terpetakan | Tampilkan coverage, review lokasi, analisis parsial berlabel sampai data lengkap |
| Sempol/Ijen dan alias lain | Double-count atau jumlah0 palsu | Master kode/edisi, crosswalk dengan bukti, uji join |
| Tahun indikator bercampur | Perbandingan historis menyesatkan | Tahun per nilai, cari pengganti, batasi klaim dan analisis campuran |
| Polygon yang tersedia edisi 2026 | Batas berbeda dari 2023/2024 | Cari historis atau dokumentasikan harmonisasi secara eksplisit |
| OCR salah meskipun total cocok | Rasio dan prioritas salah | Cek setiap nilai wilayah berisiko terhadap tabel asli |
| Puskesmas dekat kab/provinsi tetangga | Coverage tepi terpotong | Sertakan tetangga dalam dataset dan nyatakan keterbatasan luar provinsi |
| Tile/geocoder dibatasi | Demo gagal, kuota habis | Cache, provider pengganti, retry, tabel tetap bisa dipakai |
| Secret atau grants salah | Akses data/admin tak sah | Server-only, runtime non-owner, uji role dan Data API |
| Colab reset dan versi paket bergeser | Hasil tidak dapat direproduksi | Lock paket, artefak berhash, notebook Run all |
| Jadwal verifikasi melebihi estimasi | Rilis terlambat | Ukur throughput minggu 2, pangkas P1 atau tambah durasi |
| Penggunaan buffer dianggap waktu tempuh | Kesimpulan aksesibilitas keliru | Tulisan metode jelas, UAT pemahaman, routing hanya P2 |

## Paket penyerahan akhir implementasi

1. Source Laravel, migration, dependency lock dan dokumentasi environment tanpa secret.
2. Dataset rilis terkurasi beserta sumber, hash, crosswalk, metadata periode dan laporan kualitas.
3. Notebook Colab, script ETL, manifest analisis dan HTML Folium.
4. WebGIS terpasang, panduan pengguna/admin, cara impor/publish/rollback.
5. Matriks FR ke test, hasil pengujian aktual, bukti UAT, defect/retest, hasil restore dan performa.
6. Laporan akademik: data, metode, hasil peta/tabel, keterbatasan, pembahasan rasio/coverage dan saran penelitian lanjutan.
7. Demo 5–10 menit dengan alur pencarian, filter, choropleth, buffer, sumber dan contoh data belum lengkap; durasi ini usulan presentasi.

Urutan tindakan pertama saat implementasi: tetapkan edisi/tahun → dapatkan master kode dan polygon → bereskan alias dan sumber indikator → bangun schema/import → kerjakan satu kabupaten lengkap → perluas ke seluruh provinsi → verifikasi lokasi dan metode → uji → rilis.
