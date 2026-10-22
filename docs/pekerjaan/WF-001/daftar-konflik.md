# Konflik sumber dan keputusan pengendali

Versi 1, 23 Oktober 2026. Status: hasil telaah teknis; keputusan terbuka tetap menunggu owner. Proposal/arsip tidak ditulis ulang agar jejak asal terjaga.

| ID | Konflik atau ketidakjelasan | Bukti | Perlakuan untuk pekerjaan berikutnya | Owner / batas keputusan |
|---|---|---|---|---|
| CF-01 | MySQL pada proposal, Supabase pada revisi | Proposal paragraf 36; Planning/07 ADR-01 | Ikuti Supabase PostgreSQL/PostGIS. Kebutuhan akademik untuk MySQL, bila benar ada, menjadi perubahan scope tersendiri | Pemilik proyek / sebelum mandat final |
| CF-02 | Tiga role pada planning lama, dua role pada revisi | Planning/01 tabel pemakai; Planning/04 bagian users; Planning/05 F-ACCESS; revisi.txt | Hanya admin/guest. Pengelola adalah aktivitas admin, bukan akun baru; fixture pengelola lama tidak digunakan | AN/BE/QA / SRS dan desain |
| CF-03 | Impor arsip versus scraping | Planning/02 ETL; revisi.txt; WBS dasar | Adapter mengambil sumber yang dipilih, raw/hash/locator disimpan. Arsip adalah pembanding historis; hasil terbaru tidak mengganti 2024-S1 diam-diam | DG / WF-018–020 |
| CF-04 | Admin P1 versus login/command P0 | Planning/01 FR-15; WBS dasar dan fase 4 | Login/logout, otorisasi, command review/analisis/publish/rollback wajib; dashboard/review UI opsional | AN/BE / WF-014/028 |
| CF-05 | Nama file 2024 versus tahun observasi campuran | Planning/02 tahun sumber | Metadata per observasi; tidak memberi label seluruh indikator sebagai 2024 | DG / WF-019 |
| CF-06 | Kandidat ditemukan versus lokasi valid | Planning/02 baseline 565/408; notebook lama | 565 belum otomatis verified; centroid tidak boleh menjadi titik buffer | DG / WF-039/068–071 |
| CF-07 | 665 pasangan fasilitas, 667 detail workbook, target wilayah berbeda | Planning/02 dan Planning/04 | Master kode/edisi menentukan cakupan; selesaikan Sempol–Ijen berbukti; tidak memaksa jumlah dengan menghapus baris | DG / WF-063/066 |
| CF-08 | Jadwal 8 minggu dan G0–G5 versus waterfall WF-G1–G8 | Planning/06; WBS | Gunakan antrean WF dan gerbang WF-G1–G8; hitung bottom-up. Delapan minggu tetap pembanding usulan, bukan deadline | PM / WF-008 |
| CF-09 | Pemilihan P1 berpotensi menghapus uji parameter | Planning/05 A08-PARAM/RANK; WF-120 | A08-PARAM dan S05 backend tetap wajib walaupun semua P1 deferred | QA / seluruh baseline uji |
| CF-10 | CI perlu PostGIS sebelum provisioning final | WF-056 dan WF-072; register prasyarat EXEC-04 | DB test sementara terisolasi boleh untuk CI, kemudian verifikasi dev/test final; tidak memakai produksi | BE/OP / WF-030/056 |

## Urutan otoritas

Instruksi pengguna terbaru yang jelas mengendalikan revisi. Setelah itu gunakan keputusan baseline yang benar-benar diterima, WBS/tiket waterfall yang menjelaskan revisi, lalu planning awal dan proposal sebagai sumber asal. Ketidakcocokan substantif dicatat dan ditelusuri; tidak diselesaikan dengan mengarang penerimaan pihak lain.

## Keputusan masih terbuka

Penugasan tim/kapasitas, penilai akademik, tenggat, anggaran dan layanan menjadi input fase 1. Edisi polygon/kode, provider geocoding, tahun indikator, cakupan penuh/parsial dan pilihan P1 menjadi keputusan fase 2 sesuai register prasyarat. Tidak semua keputusan fase 2 harus dipaksakan selesai dalam WF-001.

Penerimaan WF-G1 harus mengacu paket fase 1 yang sudah tersedia. Permintaan mulai bekerja tidak dicatat sebagai penerimaan hasil yang belum dibaca.
