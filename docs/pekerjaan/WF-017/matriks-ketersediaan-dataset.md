# Ketersediaan dataset

Versi 1 · 23 Oktober 2026 · Penyusun: Codex. Audit ulang baca-saja: [hasil CSV](audit-readonly.json), [hash seluruh arsip](manifest-arsip.json). Seluruh 49 hash cocok manifest audit 22 Oktober; Archives tidak diubah. Perhitungan ulang CSV bukan validasi lapangan atau seluruh tabel PDF/XLSX.

| Data | Bukti tersedia / baseline | Status | Kesenjangan dan tindakan | Owner peran / prioritas |
|---|---|---|---|---|
| Identitas fasilitas | CSV alamat 973 kode unik, 38 kab/kota, 665 pasangan nama mentah; PDF Kemenkes, XLSX salinan | Raw; bukan master final | Rekonsiliasi PDF/salinan dan mapping kode resmi | DG, tinggi |
| Kategori | 616 rawat inap + 357 non; 658 perdesaan + 294 perkotaan + 16 terpencil + 5 sangat terpencil | Hitungan CSV terkonfirmasi ulang | Cocokkan ke sumber primer, pertahankan ejaan/provenance | DG, tinggi |
| Lokasi | 565 pasangan, 408 kosong, 560 pasangan unik, 5 kelompok duplikat | Kandidat; tidak ada bukti verified dalam paket | Review seluruh kandidat; cari missing; jangan menganggap geocoder sukses = akurat | DG, tinggi |
| Rekap fasilitas | 665 detail + 39 agregat; jumlah detail 973, seluruh baris 2919 | Rekonsiliasi raw | Agregat bukan fakta; simpan terpisah | DG, tinggi |
| Penduduk | Workbook catatan menyebut 2023; 38 PDF BPS | Staging dari audit sebelumnya, belum rerun workbook | Locator tabel/halaman per observasi; verifikasi semua nilai OCR berisiko | DG, tinggi |
| Luas statistik | Workbook catatan menyebut 2019/2021/2023/2025 | Staging campuran | Utamakan observasi 2023; jangan relabel angka; hektar → km² punya bukti | DG, tinggi |
| Gabungan | Audit sebelumnya 667 detail, Sempol P/A kosong, Ijen dan Pabean Cantian F=0 | Staging belum tervalidasi | Crosswalk sebelum menggabung; 97 baris antrean bukan 97 wilayah salah | DG, tinggi |
| Kode wilayah | Kandidat MFD BPS 2023 tersedia di web | Belum diarsip/parse sebagai master | Unduh edisi dan hash; kode sebagai teks; cocokkan parent dan masa berlaku | DG, tinggi |
| Polygon | Metadata BIG Juni 2026 tersedia di web; belum ada file polygon dalam Archives | Belum layak baseline historis | Cari edisi sesuai/izin; bila memakai 2026 perlu crosswalk dan keputusan metode | DG, tinggi |
| Crosswalk | Template/antrean lokal planning | Belum disetujui | BPS–Kemendagri–polygon; alias Sempol/Ijen dibuktikan, bukan asumsi | DG/reviewer, tinggi |
| Notebook | GIS.ipynb berisi percobaan geocoding | Prototipe, bukan pipeline reproduksi | Hilangkan fallback centroid untuk analisis; manifest/run dan export perlu dibangun | DG, sedang |
| Fixture | Spesifikasi di rencana uji | Belum implementasi | Fixture sintetis dipisahkan dari dataset penelitian | QA, sebelum implementasi/uji |

Arsip: 1 DOCX, 39 PDF, 3 CSV, 5 XLSX, 1 notebook. Manifest merekam byte/hash, bukan lisensi. Bahan staging di Planning tidak boleh dianggap sumber resmi atau dipublikasikan otomatis. Sumber tambahan, akses dan parser dirinci pada [kelayakan sumber](../WF-018/katalog-sumber-scraping.md).

Kriteria siap: kode/parent/edisi sesuai, provenance tiap observasi, koordinat eligible berbukti, polygon valid lengkap, dan laporan selisih. Angka 666 kecamatan masih baseline pencarian edisi, bukan alasan menghapus 667 baris staging supaya jumlah cocok.
