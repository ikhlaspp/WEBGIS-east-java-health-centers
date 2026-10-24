# Keputusan crosswalk wilayah

Tanggal: 2026-10-24. Review teknis sumber: Codex. Status approved pada mapping berarti identitas sumber telah ditautkan secara teknis pada master referensi; bukan persetujuan dosen, reviewer independen, kualitas observasi atau publikasi.

## Identitas dan bukti

Master BPS 2023 berisi 666 kecamatan dan 38 induk; hash artefak master/bridge/batas diverifikasi terhadap WF-061 sebelum dipakai. Kode tetap teks. Parent, code system BPS, edisi dan jumlah per induk diperiksa. Setiap kode terhubung tepat ke satu objek batas historis BPS/OCHA 2020 yang sudah dipilih; hubungan identitas ini tidak membuktikan keselarasan geometri lintas tahun.

Seluruh 8.502 detail staging mempunyai mapping: 8.101 dengan nama resmi tepat dalam konteks induk, 320 melalui nama dalam bridge resmi BPS/Kemendagri, 72 melalui descriptor eksplisit Kabupaten Pasuruan, 6 melalui dua keputusan pemisahan kata, dan 3 melalui tabel BPS Sumenep. Terdapat 60 keputusan alias unik: 33 bridge, 24 descriptor induk, 2 pemisahan kata dan 1 sumber tambahan. Masing-masing dibatasi dataset, source_id, hash, edisi, periode observasi, parent, nama sumber dan hash boundary set. Tidak ada wildcard alias lintas sumber/edisi.

Keputusan lengkap di alias-decisions.json. Sumberrejo/Sumberejo, Gedeg/Gedek, Pejarakan/Pajarakan, Sumbermanjing Wetan/Sumbermanjing dan Kota/Kota Kediri didukung pasangan nama berkode yang sama pada bridge resmi. Kayenkidul/Kayen Kidul dan Karangpilang/Karang Pilang diperiksa sebagai pemisahan kata yang unik dalam induknya; keputusan eksplisit diperlukan, bukan aturan hapus-spasi global. Kabupaten Pasuruan hanya disamakan dengan induk 3514 dalam 24 konteks yang tercatat; tidak disamakan dengan Kota Pasuruan.

Giligenting ditautkan ke 3529040 berdasarkan [tabel BPS Sumenep tahun 2023](https://sumenepkab.bps.go.id/id/statistics-table/1/MTE0IzE%3D/jumlah-desa-kelurahan-menurut-kecamatan-di-kabupaten-sumenep-2023.html) yang memasangkan kode lokal 040 dengan nama tersebut, serta [katalog publikasi resmi](https://sumenepkab.bps.go.id/id/publication/2018/09/27/26c277363888239134dc720e/giligenteng-subdistrict-in-figures-2018.html) dengan nomor katalog 1102001.3529040. Snapshot HTML lengkap disimpan privat, hash/URL/waktu dalam supplemental-receipts.json. Nama canonical master tetap GILIGENTENG dan bridge menyimpan Giliginting. Ini variasi nama sumber yang terikat kode, bukan tebakan kemiripan.

## Sempol dan Ijen

Master mentah memuat `35 11 151 SEMPOL` pada halaman PDF 149, baris 6. Resolusi WF-059 menunjukkan IJEN pada kode BPS 3511151; bridge periode BPS 2023-S1/Kemendagri 2022 memasangkan kode tersebut dengan kode Kemendagri 351119 bernama Sempol. Kedua nama ditautkan ke satu identitas, dalam induk Bondowoso 3511. Bukti ini tidak menetapkan tanggal hukum perubahan nama atau membuktikan geometri tidak berubah.

Workbook gabungan mempunyai Ijen pada baris 106 dan Sempol pada baris 113. Keduanya dipertahankan, ditandai `quarantined_duplicate_target` pada hasil crosswalk, dan tidak dijumlah/dipilih otomatis. Satu kelompok konflik many-to-one dicatat. Nilai asli staging tetap utuh; pemilihan observasi penduduk/luas dibawa ke kurasi indikator. Nama yang sama lintas kabupaten tidak digabung.

## Coverage dan batas

Semua 973 kode fasilitas mempunyai satu kecamatan resmi yang konsisten di enam salinan fasilitas/koordinat; konflik penugasan 0 dan unmatched 0. Semua 666 kecamatan terwakili pada indikator penduduk/luas. Snapshot fasilitas hanya menugaskan fasilitas ke 665 kecamatan. Pabean Cantian 3578240 tetap dipertahankan dalam master; tidak ada assignment pada snapshot ini bukan bukti tidak adanya pelayanan nyata di wilayah tersebut.

Mode tetap eksplorasi lintas periode: batas 2020, master 2023 dan fasilitas 2024-S1, sedangkan beberapa indikator mengklaim tahun lain. `observation_allocation_verified=false`, `data_quality_accepted=false`, `publication_allowed=false`. Mapping identitas tidak membagi atau menjumlah observasi lintas perubahan wilayah dan tidak mengesahkan koordinat.

Hasil aktual `data/processed/crosswalk.json` memuat master dan mapping per baris. Laporan publik crosswalk-terreview.json memuat ringkasan, konflik dan hash input; output-verification.json mencatat hash output, coverage per dataset serta pengulangan byte-identik. Tahap berikutnya: WF-064 rekonsiliasi master fasilitas setelah push terverifikasi.
