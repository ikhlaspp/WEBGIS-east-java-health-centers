> Current decision: [WF-G2 accepted](../WF-028/penerimaan-WF-G2.md). The accepted supplement supersedes earlier pending gate/scope statements. Data completeness and source checks remain mandatory before dependent implementation; partial demos are labelled; optional UI/public CSV/ranking tests are out of scope, not passed. Existing P0 checks remain required.

# Pemeriksaan kelayakan sumber

Versi 1 · 23 Oktober 2026 · Penyusun: Codex.

## Bukti aktual

Halaman Kemenkes dan tautan unduh dapat dibaca; PDF web teridentifikasi 239 halaman. Ekstraksi lokal `pdftotext -layout` juga menemukan 239 halaman; kode contoh 35010200001 berada pada halaman PDF 136. Urutan teks beberapa kolom tampak bergeser sehingga parser harus memakai batas kolom dan rekonsiliasi kode, bukan membagi berdasarkan satu spasi. Ekstraksi teks tidak membuktikan seluruh baris benar.

Sampel BPS Bangkalan lokal memiliki 334 halaman. Daftar tabel dan halaman isi memuat tabel 1.1.1 luas dan 3.1.1 penduduk, observasi 2023. Pada Bojonegoro, ekstraksi 244 halaman hanya menghasilkan sekitar 8 KB teks dan tidak menemukan ID tabel tersebut; tandai membutuhkan pemeriksaan gambar/OCR, bukan data kosong. Sampel tersimpan pada `sampel-parser.json` bersama locator/hash dan jumlah teks. Tidak dilakukan OCR penuh atau verifikasi visual seluruh PDF; percobaan screenshot PDF web gagal cache miss, sehingga tidak ada klaim pemeriksaan visual.

Metadata layer BIG menyediakan nama/kode wilayah serta geometry; adapter perlu menangani KDCBPS/KDCPUM sebagai kode dari sistem berbeda dan WADMKK sebagai parent. Edisi 2026 tetap blocker data historis, meskipun format teknis bisa dibaca. Tidak ada polygon yang diunduh atau dinyatakan sah untuk redistribusi.

## Rancangan akuisisi yang dapat dilanjutkan

1. Simpan daftar URL dokumen spesifik, penerbit, tanggal akses dan status izin. Ambil sekali dengan timeout, retry terbatas untuk 429/5xx dan cache; jangan merayapi seluruh portal tanpa kebutuhan.
2. Raw disimpan immutable beserta SHA-256 dan response metadata. Perubahan hash berarti versi sumber baru dan memicu review, bukan overwrite.
3. Parser PDF menemukan header/tabel/halaman, menggabungkan alamat multiline berdasarkan kode, dan memisahkan subtotal. Parser CSV memvalidasi header, encoding, kode teks dan angka lokal. HTML hanya discovery tautan/metadata; tidak menebak link unduhan kadaluwarsa.
4. Untuk sumber gambar, OCR menghasilkan kandidat dengan crop/locator; angka berisiko diperiksa manusia. Kesesuaian total saja tidak mengesahkan baris.
5. Untuk ArcGIS, pilih filter provinsi dari field yang diverifikasi, hitung expected IDs, ambil halaman secara deterministik, bandingkan IDs diterima/unik dan cek exceededTransferLimit. Tahap ini belum dijalankan karena edisi/izin belum diputuskan.
6. Catat error dan halt pada perubahan schema/tabel, unit tidak diketahui, count tak lengkap, atau izin tidak jelas; fallback harus punya definisi dan periode setara serta provenance baru.

## Keputusan kelayakan

Fasilitas: layak prototipe parser. Penduduk/luas: layak bersyarat per publikasi, lima wilayah OCR tetap antrean. Kode: MFD 2023 target dipilih sebagai asumsi teknis, file lengkap belum dibekukan. Polygon: sumber ditemukan tetapi edisi/izin belum memenuhi baseline. Lokasi: review kandidat memungkinkan, provider batch belum dipilih. Penerima kebutuhan perlu menetapkan edisi polygon/hak penggunaan sebelum WF-G2 accepted; format layak bukan data siap analisis.
