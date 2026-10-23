# Skrip fasilitator UAT

Versi 1 · 23 Oktober 2026 · Penyusun: Codex. Minimal5peserta target, bukan daftar peserta tersedia. Semua tugas memakai release/run kandidat yang sama. Nama/kontak/consent disimpan privat, repository hanya participant_code.

Pembukaan: jelaskan tujuan menilai kemudahan membaca informasi, bukan menguji kemampuan peserta. Partisipasi sukarela, boleh berhenti, catat data apa yang direkam dan izin rekaman bila digunakan. Orientasi umum2menit menunjukkan tujuan situs, tanpa menunjukkan langkah solusi. Fasilitator tidak memberi petunjuk navigasi selama bagian mandiri; setiap bantuan dicatat.

## Instruksi dibacakan kepada peserta

1. “Temukan fasilitas dengan kode yang diberikan pada kartu tugas. Sebutkan alamat dan jenis pelayanannya.” Ulangi kartu fasilitas yang tidak mempunyai titik peta. Kartu ditetapkan QA dari fixture/staging sebelum sesi.
2. “Bandingkan dua kecamatan pada kartu tugas. Sebutkan jumlah penduduk, jumlah fasilitas, rasio, dan tahun data masing-masing.” Jangan beri tahu halaman/selector yang harus diklik.
3. “Tampilkan radius3km dan jelaskan apa yang dapat dan tidak dapat disimpulkan dari peta itu.” Tidak menyebutkan jawaban geometris pada instruksi.
4. “Cari contoh wilayah dengan data belum tersedia dan contoh nilai nol. Jelaskan perbedaannya.” Fasilitator tidak mengarahkan ke warna tertentu.
5. “Temukan sumber dan versi hasil yang sedang Anda lihat. Jelaskan periode fasilitas dan penduduknya.”

Rubrik fasilitator (tidak dibacakan sebelum respons): kode/detail tepat termasuk missing; P/F/ratio/period tepat; radius bukan travel time/penduduk terlayani dan partial x/y dikenali; null dibedakan nol; source/release/run dapat ditemukan. Salah tafsir kritis radius/no-data/partial/tahun adalah defect meskipun semua tombol ditemukan.

Form per task: participant_code,task_id,start/end,duration_seconds,independent_success,assisted_success,failed,not_attempted,assistance_text,observed_errors,interpretation_answer,comments,release/run,device/browser,defect_id. Outcomes mutually exclusive. Task01 dua pencarian berhasil baru task sukses, sehingga denominator tetap5tugas/peserta; jangan menghitung subtask sebagai peserta tambahan.

Target≥80% tugas mandiri dari minimal5sesi lengkap (20/25 untuk5peserta), laporkan per task dan per participant. Semua peserta dapat menemukan sumber setelah orientasi; salah tafsir kritis diselesaikan+retest sebelum accepted. Not_attempted/withdrawal dilaporkan, bukan diam-diam dibuang untuk menaikkan skor; rekrut pengganti untuk mencapai5sesi lengkap. Durasi deskriptif, bukan target baru setelah melihat hasil. Kepuasan1–5 opsional, tidak disebut SUS.

Retest: catat versi/fix dan ulang tugas terkait dengan kasus berbeda; simpan hasil awal, bantuan dan perubahan. Reviewer/penerima memberi keputusan nyata setelah laporan; desain ini tidak mengklaim wawancara, peserta, atau UAT telah dilakukan.
