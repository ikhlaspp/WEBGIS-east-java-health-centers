# Register risiko proyek

Versi kandidat 1, 23 Oktober 2026. Skala kemungkinan (K) dan dampak (D): 1 rendah, 2 sedang, 3 tinggi. Skor K×D; 6–9 prioritas tinggi, 3–4 sedang, 1–2 rendah. Penilaian ini estimasi, bukan frekuensi insiden terukur. Owner bernama mengikuti penugasan WF-006 setelah dikonfirmasi.

| ID | Risiko dan tiket terdampak | K | D | Skor | Pemicu | Pencegahan dan respons | Owner |
|---|---|---|---|---|---|---|---|
| R01 | 565 kandidat/408 missing membutuhkan usaha besar; WF-067–071 | 3 | 3 | 9 | Median review/pencarian melebihi asumsi atau batch blocked menumpuk | Batch ≤25, ukur waktu sampel, cache, tambah durasi/kapasitas atau CR parsial; jangan centroid | DG/PM |
| R02 | Polygon historis tidak tersedia; WF-018/019/059/066 | 3 | 3 | 9 | Edisi/lisensi/coverage tidak cocok | Cari sumber primer/cadangan, harmonisasi berbukti; tahan indikator terkait | DG |
| R03 | Sempol–Ijen/nama kembar menggandakan fakta; WF-063/107 | 2 | 3 | 6 | Mapping many-to-one tanpa bukti atau parent berbeda | Crosswalk kode+parent+edisi, reviewer dan fixture; quarantine konflik | DG |
| R04 | Tahun/unit/OCR salah; WF-065/107 | 3 | 3 | 9 | Tidak ada locator/tahun atau selisih nilai berisiko | Periksa sumber asli, pertahankan raw/null, konversi berjejak; jangan paksa total | DG/QA |
| R05 | Sumber berubah/akses dibatasi; WF-057–061/105 | 2 | 3 | 6 | Header/pagination/hash tidak sesuai atau rate limit | Kontrak parser, snapshot/cache, retry terbatas; alternatif bersumber | DG |
| R06 | Kebocoran/grants terlalu luas; WF-074/085/116 | 2 | 3 | 6 | Runtime owner, draft terbaca, rahasia dalam bundle/log | Non-owner, allow/deny aktual, sanitasi bukti; perbaiki dan ganti credential bila bocor | BE/QA |
| R07 | Publish bersaing atau cache campur rilis; WF-084/086/114 | 2 | 3 | 6 | Dua command aktif atau metadata endpoint berbeda | Lock/transaksi, uji dua koneksi, audit atomik, cache setelah commit | BE |
| R08 | Colab reset/dependency berubah; WF-093–096/123 | 2 | 2 | 4 | Run all gagal dari runtime baru | Lock/manifest/checkpoint, artefak tersimpan; rerun input sama | DG |
| R09 | Budget/kapasitas belum cukup; WF-006–008/129 | 3 | 3 | 9 | Estimasi melebihi kapasitas/deadline atau biaya belum disetujui | Skenario P0/P0+P1, pilot throughput, tetapkan owner; jangan beli tanpa keputusan | PM/OP |
| R10 | Tile/geocoder tidak tersedia; WF-088/121 | 2 | 2 | 4 | 429/error/kuota habis | Provider dapat diganti, cache sesuai izin, fallback tabel, mock load test | FE/OP |
| R11 | Radius disalahartikan sebagai waktu tempuh; WF-092/126/145 | 2 | 3 | 6 | Peserta UAT salah tafsir atau narasi laporan berlebih | Label metode dan coverage, uji pemahaman, koreksi narasi; routing P2 | AN/DG/QA |
| R12 | Reviewer/UAT/akses penerima tertunda; WF-012/125/150 | 2 | 3 | 6 | Tidak ada penerima/jadwal atau akses belum bisa digunakan | Konfirmasi awal, dokumen reviewable, owner follow-up; jangan catat persetujuan palsu | PM/QA |
| R13 | Backup hanya DB tanpa artefak; WF-122/136 | 2 | 3 | 6 | Restore tidak menemukan HTML/GeoJSON/input | Manifest DB+file, restore terpisah, verifikasi hash/RPO/RTO | OP |
| R14 | Git gagal menghambat antrean serial; semua tiket | 2 | 2 | 4 | Push ditolak, credential/network error | Simpan hasil lokal, cek remote/identity, retry setelah akses pulih; tanpa force push | OP |

Cadangan effort WF-008 dipisahkan dari base/review/rework; bukan izin mengurangi kualitas. Owner meninjau risiko setelah setiap tiket terdampak dan pada laporan mingguan. Skor 6–9 atau insiden yang mengubah scope/biaya/tenggat dieskalasikan ke pemilik proyek dengan opsi dan bukti. Risiko sumber/periode yang belum selesai tetap menjadi blocker gerbang terkait.
