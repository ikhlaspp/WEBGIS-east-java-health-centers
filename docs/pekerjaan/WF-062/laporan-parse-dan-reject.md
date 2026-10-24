# Ekstraksi dan normalisasi sumber

Tanggal: 2026-10-24. Kontrak WF-038/WF-040 diterapkan pada `python/gis_pipeline/etl/normalize.py` melalui CLI `scripts/etl/normalize.py`. Input selalu berasal dari snapshot WF-061 yang hash dan ukurannya diperiksa sebelum parsing. `source-specs.json` menetapkan identitas, format, header, tabel dan jumlah baris; `source-roles.json` mencatat peran seluruh 91 berkas agar referensi tidak disamarkan sebagai tabel yang sudah dinormalisasi.

## Cakupan

Sepuluh dataset diproses: PDF fasilitas resmi dan arsip, CSV/XLSX alamat fasilitas, CSV/XLSX koordinat, workbook penduduk, workbook luas, workbook gabungan historis dan CSV hitungan fasilitas. Dua dataset koordinat menyimpan kandidat, bukan verifikasi lokasi. Dua workbook indikator tetap derivative yang harus dibandingkan terhadap sumber BPS. Ke-38 PDF BPS merupakan bukti untuk kurasi; normalisasi ini tidak mengklaim telah mengesahkan seluruh tabel atau OCR-nya. Referensi kode/geometri dipertahankan untuk crosswalk dan validasi spasial; proposal/notebook tetap konteks, tidak dieksekusi.

Envelope setiap baris mencatat batch, nomor, dataset, locator, hash sumber, versi pipeline, field/cell mentah, field olahan, alasan konversi, disposition dan errors. Nama tampilan memakai NFC/trim luar; collapse spasi dan casefold hanya pada match key. Kode tidak dipotong menjadi kode wilayah dan tidak dipakai untuk fuzzy merge. Sel kode numerik workbook hanya dapat dirender menjadi teks ketika bilangan bulat aman dan panjang 11 digit utuh; leading zero yang telah hilang tidak ditebak/dipad.

Penduduk menjadi integer jiwa, luas menjadi string Decimal km2; unit/locale/faktor tercatat. Null berbeda dari nol. Luas nol, angka negatif, formula tanpa nilai terverifikasi, locale/periode/unit tak dikenal, kolom tidak lengkap dan koordinat berpasangan tidak lengkap ditolak. Label sumber `verified` tidak dapat mempromosikan koordinat. Total dipisahkan dari detail; seluruh 667 detail gabungan, termasuk Ijen/Sempol, tetap ada untuk kurasi.

## Koreksi selama pemeriksaan

Eksplorasi awal menghitung 667 baris bernomor pada workbook gabungan. Pemeriksaan seluruh baris menemukan tambahan 38 subtotal kabupaten/kota dan satu total JAWA TIMUR: total input 706, bukan 667. Guard jumlah baris menolak run dengan expected 667 (`SOURCE_ROW_COUNT_MISMATCH`, exit 1); tidak ada manifest batch baru diterbitkan. Header/sel sumber diperiksa langsung: subtotal mempunyai No kosong dan Kecamatan TOTAL. Spesifikasi final menetapkan 706 raw dengan label TOTAL eksplisit, tanpa menghapus 667 detail. CSV hitungan juga memiliki 38 subtotal dan satu total provinsi, dipisahkan dengan aturan eksplisit yang sama.

Verifikasi dokumen konfigurasi repo juga diperbaiki untuk konversi LF/CRLF oleh Git. Hanya representasi newline yang boleh berbeda; hash dan ukuran harus cocok dengan salah satu representasi persis. Bukti aktual dari `git show HEAD:<path>` untuk ketiga dokumen sumber berhasil diverifikasi. Semua raw dataset tetap memerlukan hash/ukuran byte persis; tes membuktikan toleransi dokumen tidak berlaku pada raw.

## Reproduksibilitas dan batas penerimaan

Batch ID berasal dari versi pipeline, spesifikasi dan fingerprint rencana sumber. Content hash memakai JSON canonical yang tidak tergantung newline OS; hash berkas output tetap mencatat byte artefak aktual. Lokasi output memakai batch/content hash. Parsing semua dataset harus selesai sebelum manifest batch diterbitkan. Uji repeat-run membandingkan seluruh report, hash, lokasi output dan jumlah baris pada input yang sama; perubahan byte sumber atau jumlah yang tidak sesuai gagal.

Disposition accepted berarti berhasil dinormalisasi secara sintaksis, bukan accepted sebagai kualitas/publikasi. Seluruh baris memiliki `data_quality_accepted=false`. Mapping, resolusi alias, pemilihan sumber indikator, validitas geometri dan verifikasi lokasi tetap wajib sebelum promosi. Review ini bersifat teknis oleh agen, tidak mengklaim persetujuan dosen atau reviewer independen.

Hasil final: 8.656 baris sumber = 8.502 accepted + 154 aggregate + 0 quarantined. Ini jumlah baris lintas salinan sumber, bukan fasilitas unik. Enam dataset fasilitas/koordinat masing-masing 973 baris; gabungan 667 detail + 39 total; hitungan historis 665 detail + 39 total; penduduk dan luas masing-masing 666 detail + 38 total. Seluruh hash output dan hash konten dataset dihitung ulang dari berkas yang tersimpan dan cocok. Suite final: 114 passed; compileall exit 0.

Temuan tambahan: CSV koordinat mempunyai 565 pasangan kandidat/408 kosong, sedangkan XLSX mempunyai 568/405. Tepat tiga kode 35770200004, 35770200005, 35770200006 mempunyai pasangan pada XLSX tetapi kosong pada CSV; pasangan lain identik secara Decimal. Locator kedua versi dicatat pada output-verification.json. Kandidat tambahan tidak otomatis mengganti baseline CSV atau menjadi verified; bawa ke rekonsiliasi fasilitas dan review lokasi.

Hasil final dan jumlah aktual tersimpan pada manifest-normalisasi.json dan checkpoint.json. Data staging/quarantine/aggregate tetap private dan diabaikan Git. Berikutnya WF-063 setelah pengiriman Git terverifikasi.
