# Halaman, konten dan navigasi

Versi 1 · 23 Oktober 2026 · Penyusun: Codex. Inventaris kebutuhan P0, bukan wireframe final.

| Halaman | Isi minimum dan tindakan | Navigasi / skenario |
|---|---|---|
| Beranda | Tujuan penelitian, snapshot 2024-S1, periode indikator, F terdaftar/mapped/verified/missing, kualitas, tombol peta/tabel/metode | Awal UC-01/02/04; angka bukan kondisi layanan hari ini |
| Peta | Pencarian nama/kode/alamat; filter kab/kecamatan/pelayanan/karakter; layer/basemap; legenda; ringkasan hasil; daftar alternatif | UC-01/03/05; klik marker/daftar menuju detail; reset filter |
| Tabel fasilitas | Kode teks, nama, kab/kecamatan, alamat, layanan, karakter, kualitas koordinat; pagination/total; urut allowlist | UC-01/05; tautan detail selalu tersedia meskipun tanpa titik |
| Detail fasilitas | Semua atribut, status/precision lokasi dan sumber, snapshot, kode wilayah, tautan kecamatan | UC-01/04; tombol fokus peta hanya jika koordinat ada dan status tampil |
| Detail kecamatan | Kode/parent/boundary edisi, P jiwa/tahun, A km²/tahun, F, rasio jiwa/fasilitas, defisit, registered/mapped/verified, sumber, daftar fasilitas | UC-02/03; pindah kecamatan via selector; bandingkan melalui detail rilis sama |
| Sumber dan metode | Katalog URL/penerbit/judul/locator, tahun observasi/publikasi, formula/T, radius, partial coverage, definisi no-data, release/run, akses artefak | UC-04; setiap kartu/peta/detail punya tautan kontekstual |
| Login admin | Label identitas/password, tombol masuk, error generik, status sesi | UC-07; tanpa tombol daftar atau janji reset email yang belum dirancang |

Header konsisten menyediakan beranda/peta/tabel/metode; login admin terpisah. Breadcrumb detail mempertahankan filter dan rilis melalui back/navigation. Perubahan kabupaten mereset kecamatan, perubahan kategori hanya menyaring fasilitas. Label ringkasan membedakan “hasil filter” dan “semua fasilitas administratif di wilayah”.

## Keadaan wajib

- Loading: status dapat dibaca assistive technology; kontrol yang bergantung data dinonaktifkan sementara, bukan angka 0 sementara.
- Empty filter: “Tidak ada hasil untuk filter ini”, tampilkan reset; ini berbeda dari dataset belum terbit.
- Dataset belum terbit: penjelasan belum tersedia; tidak memanggil data draft sebagai fallback.
- No-data indikator: “Belum tersedia” plus sebab (P/A/periode/mapping); nol yang sah tampil 0.
- Titik missing/rejected: alamat, status dan tabel tetap ada; jangan menyisipkan centroid. Unverified dapat menjadi layer kandidat terpisah yang default off; tidak masuk buffer.
- Tile gagal: pesan basemap, data/tabel tetap dapat dipakai. API gagal: retry dan pesan; jangan memperlihatkan data rilis lama tanpa label.
- Request berurutan cepat: hanya hasil request terbaru untuk filter/rilis aktif yang boleh mengubah tampilan.
- Mobile: filter menjadi panel yang dapat ditutup, fokus kembali ke pemicu; legenda dan tombol tidak menutup seluruh peta, tabel dapat digulir dengan header jelas.

Konten P1 bersyarat: dashboard job/status, layar kandidat/review/publish, tombol CSV dan daftar ranking. Jika ditunda, kontrol tersebut tidak tampil sebagai tombol rusak. Command backend, audit dan validasi impor tetap P0. Seluruh UC-01–06 memiliki jalur halaman; UC-08–12 memakai command dan laporan operator sampai UI dipilih.
