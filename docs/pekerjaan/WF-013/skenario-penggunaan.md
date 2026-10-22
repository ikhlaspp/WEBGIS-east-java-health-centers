# Skenario penggunaan

Versi 1 · 23 Oktober 2026 · Penyusun: Codex · Kandidat kebutuhan untuk review pemilik proyek.

Dasar: proposal (tujuan, batasan, software), revisi pengguna admin/guest, dan matriks FR pada planning lokal. Instruksi terbaru pengguna mengotorisasi pekerjaan folder 02 dan satu commit per item. Otorisasi melanjutkan ini dicatat tanpa mengarang penerimaan akademik WF-G1 atau wawancara pengguna. Skenario merupakan sintesis dokumen dan percakapan; belum hasil observasi/UAT.

## Alur guest

| ID | Pemicu dan input | Langkah dan keluaran | Kondisi gagal / informasi wajib |
|---|---|---|---|
| UC-01 | Mencari fasilitas dengan nama, kode atau alamat | Beranda → peta/tabel → pencarian → pilih fasilitas → detail alamat, layanan, wilayah | Nama sama tetap dibedakan kode/wilayah; hasil kosong memiliki reset; missing tetap ditemukan lewat tabel tanpa marker palsu |
| UC-02 | Membandingkan dua kecamatan | Pilih kabupaten dan kecamatan A, baca detail; buka B pada rilis sama; bandingkan P, F, P/F dan tahun | Tidak menjanjikan layar perbandingan P1; F=0 ditulis tanpa puskesmas dan rasio null; P hilang bukan nol; metadata periode campuran tampil |
| UC-03 | Melihat radius 3 km | Peta → layer radius → 3000 m → baca jumlah input verified, excluded dan luas cakupan | Tidak ada run layak: layer dinonaktifkan dengan alasan; subset diberi label parsial; bukan waktu tempuh atau penduduk terlayani |
| UC-04 | Menelusuri sumber suatu angka | Dashboard/detail → sumber dan metode → identitas sumber, tabel/halaman, periode, release/run | Sumber tak dapat diakses: metadata dan hash tetap tersedia; jangan mengganti otomatis dengan data terbaru |
| UC-05 | Menyaring pelayanan/karakter wilayah | Pilih kabupaten → kecamatan → kategori → daftar/marker sesuai filter | Jumlah hasil filter berbeda dari F administratif, masing-masing berlabel; ganti parent mereset anak yang tidak valid |
| UC-06 | Menjelajah ketika tile/API gagal | Tampilkan pesan, retry terbatas dan tabel alternatif jika API tersedia | Tile gagal tidak menghapus data tabel; API gagal tidak menampilkan 0 sebagai hasil; last-known data hanya boleh dengan label waktu dan rilis |

Guest tidak login dan tidak membuat akun. Semua request satu tampilan dipatok pada release_id yang sama. Jika rilis aktif berubah, tampilkan tawaran muat ulang; jangan mencampur data dua rilis.

## Alur admin

| ID | Pemicu dan input | Langkah dan keluaran | Kondisi gagal / informasi wajib |
|---|---|---|---|
| UC-07 | Akun internal yang sudah disediakan | Login → sesi admin; logout mengakhiri sesi | Login gagal generik dan dibatasi; sesi berakhir meminta login ulang; tidak ada registrasi publik |
| UC-08 | Sumber baru atau kurasi ulang | Operator admin menjalankan pengambilan sumber yang diizinkan → raw immutable/hash → staging → laporan baris gagal | Timeout/perubahan format menghentikan promosi; raw tidak ditimpa; duplicate hash idempotent; file berbahaya ditolak |
| UC-09 | Antrean lokasi/mapping bermasalah | Review bukti per kode → keputusan dan alasan → identitas reviewer/tanggal | Tanpa bukti facility tidak bisa verified; titik identik menjadi antrean, bukan otomatis hapus; bulk ≤25 per checkpoint |
| UC-10 | Kandidat tervalidasi | Jalankan analisis dengan T dan radius allowlist → hasil terikat input hash/run → preview laporan | Gagal/null dependency tetap draft; tidak membuat angka palsu atau mengubah rilis terbit |
| UC-11 | Kandidat memenuhi kriteria publish | Admin berwenang memeriksa laporan → command publish atomik → rilis aktif baru dan audit | Publish bersamaan/validasi gagal tidak memberi rilis campuran; identitas operator CLI harus nyata, bukan actor null |
| UC-12 | Rilis baru bermasalah | Pilih rilis terbit lama → rollback pointer melalui command → audit dan cache rilis | Rilis lama harus tersedia dan valid; tidak menghapus jejak rilis yang dibatalkan; kegagalan tidak mengubah pointer sebagian |

P0 menyediakan login dan command terkontrol. UI dashboard/review-publish, ekspor CSV dan ranking adalah opsi P1 terpisah. Akses shell saja tidak cukup: identitas operator dan kewenangan operasi harus divalidasi serta tercatat.

## Review kebutuhan

Pemeriksaan mandiri: setiap alur memiliki pemicu/input, hasil dan kegagalan; UC-01/02/03 menangani missing/partial; tidak ada role aplikasi pengelola terpisah. Pertanyaan kepada pemilik: pilihan empat P1 dan apakah partial coverage boleh dirilis. Jawaban atau asumsi kerja dicatat pada keputusan scope dan kualitas; tidak ada pernyataan wawancara telah terjadi. Reviewer eksternal: belum tercatat.
