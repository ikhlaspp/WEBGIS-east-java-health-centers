# Strategi UAT

Versi 1 · 23 Oktober 2026 · Penyusun: Codex. Target minimal lima peserta; belum ada peserta atau hasil yang diklaim tersedia. QA merekrut pada WF-125, mencatat persetujuan partisipasi dan memakai kode peserta anonim pada bukti publik.

Komposisi target: pengguna umum/mahasiswa dan calon penilai; usahakan satu peserta memahami SIG/data kesehatan, tanpa mengasumsikan dinas tersedia. Gunakan kandidat staging yang sama release/run untuk seluruh peserta. Orientasi singkat menjelaskan navigasi umum, bukan jawaban tugas. Tidak menampilkan data pasien atau merekam credential.

| ID | Instruksi tugas | Kriteria berhasil mandiri | Batas salah tafsir |
|---|---|---|---|
| UAT-01 | Temukan fasilitas yang diberikan dengan nama/kode dan baca alamat/layanan; ulangi satu missing | Kode yang dipilih benar, detail terbaca, missing tetap ditemukan dari tabel | Tidak menganggap missing berarti fasilitas tidak ada |
| UAT-02 | Bandingkan dua kecamatan pada rilis yang sama | Menyebut P,F,rasio,periode dengan benar dari detail | Tidak menganggap F hasil filter marker sebagai F administratif |
| UAT-03 | Aktifkan radius 3 km dan jelaskan arti hasilnya | Memilih 3000 m, menemukan x/y eligible dan batas interpretasi | Tidak menyebut waktu tempuh atau persen penduduk terlayani |
| UAT-04 | Temukan wilayah no-data dan satu nilai nol | Membedakan missing, nol dan tanpa_puskesmas | Tidak mengubah null menjadi nol dalam jawaban |
| UAT-05 | Temukan sumber dan versi hasil | Menyebut snapshot fasilitas, tahun indikator, release/run dan batas data campuran | Tidak menganggap seluruh angka berasal dari tahun publikasi |

Setiap peserta mengerjakan kelima tugas; completion mandiri = berhasil tanpa petunjuk langkah/jawaban setelah orientasi. Catat start/end, successful_independent, successful_assisted, failed, not_attempted, bantuan, kesalahan, komentar dan defect. Bantuan teknis akibat staging gagal tetap dicatat, tidak menghapus kegagalan dari denominator diam-diam. Peserta tidak selesai dicatat terpisah; minimum lima sesi lengkap diperlukan untuk target utama.

Target kandidat ≥80% dari seluruh tugas pada minimal lima sesi lengkap (minimal 20/25 tugas mandiri bila tepat lima peserta). Laporkan juga per-tugas dan per-peserta agar rata-rata tidak menutupi tugas bermasalah. Semua peserta harus dapat menemukan sumber setelah orientasi. Salah tafsir kritis pada radius, no-data, partial coverage atau tahun wajib diperbaiki dan diuji ulang sebelum rilis, walaupun angka 80% tercapai.

Waktu tugas dicatat deskriptif, bukan target kelulusan yang diciptakan sesudah pengujian. Pertanyaan kepuasan 1–5 boleh ditambah tetapi bukan skor SUS. Retest menyebut versi baru, peserta dan perubahan; hasil awal tidak dihapus. Penerima proyek meninjau laporan, QA mencatat accepted/rework aktual; rencana ini tidak menandakan UAT telah berlangsung.

Template baris: participant_code, task_id, release_id, run_id, browser/device, started_at, duration_seconds, outcome, assistance, observed_error, interpretation_answer, defect_id, retest_reference. Nama/kontak peserta disimpan privat bila diperlukan, bukan dalam repository publik.
