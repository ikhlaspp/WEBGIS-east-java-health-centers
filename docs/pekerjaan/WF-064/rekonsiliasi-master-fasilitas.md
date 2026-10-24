# Rekonsiliasi master fasilitas

Tanggal: 2026-10-24. Implementasi: scripts/etl/reconcile_facilities.py dan python/gis_pipeline/etl/reconcile_facilities.py. Input adalah artefak normalisasi WF-062, crosswalk WF-063 yang hash dan batch-nya cocok, serta baseline audit independen WF-017. Arsip asli tidak diubah.

## Hasil aktual

Enam sumber (PDF resmi, PDF arsip, CSV alamat, XLSX alamat, CSV koordinat, XLSX koordinat) mempunyai set kode yang sama: 973 identitas unik. Tidak ada perbedaan atribut substantif maupun formatting pada field yang dibandingkan. Setiap identitas memiliki satu wilayah resmi yang konsisten. Master keluaran memakai atribut PDF resmi dan menyimpan referensi locator/hash keenam salinan; tidak ada fasilitas dihapus karena koordinat kosong.

Kategori cocok dengan baseline: 616 Rawat Inap + 357 Non Rawat Inap. Karakteristik: 658 Perdesaan + 294 Perkotaan + 16 Terpencil + 5 Sangat Terpencil. Jumlah induk 38; master wilayah tetap 666 kecamatan. Assignment fasilitas menjangkau 665 kecamatan; Pabean Cantian tetap ada dengan jumlah assignment snapshot nol, bukan klaim ketiadaan pelayanan nyata.

## Detail dan agregat

| Sumber | Detail | Agregat terpisah | Jumlah detail | Subtotal induk | Total provinsi |
|---|---:|---:|---:|---:|---:|
| CSV hitungan historis | 665 | 39 | 973 | 973 | 973 |
| Workbook gabungan | 667 | 39 | 973 | 973 | 973 |

Agregat terdiri dari 38 subtotal induk dan satu total provinsi. Ketiganya direkonsiliasi terpisah, bukan dijumlah sebagai fasilitas. Penjumlahan naif seluruh baris menghasilkan 2.919; master tetap 973. Semua subtotal induk sesuai jumlah identitas fasilitas primer pada induk yang sama.

Workbook gabungan memuat Ijen bernilai hitungan fasilitas 0 pada baris 106 dan Sempol bernilai 1 pada baris 113. Keduanya menunjuk 3511151 menurut crosswalk. Jumlah fasilitas resmi pada kode tersebut adalah 1. Dua observasi derivative tetap ditahan sebagai konflik alias dan tidak dipilih/digabung otomatis. Pemeriksaan aritmetika total sumber bukan promosi observasi gabungan. Penduduk/luas mengikuti kurasi berikutnya.

## Koordinat dan keputusan perbedaan

Baseline CSV tetap 565 pasangan kandidat + 408 kosong, 560 pasangan unik dan 5 kelompok koordinat sama. Identitas berbeda pada titik sama tidak dideduplicate. XLSX memiliki 568 pasangan kandidat; tepat tiga tambahan untuk 35770200004, 35770200005, 35770200006. Semua versi/evidence dipertahankan sebagai kandidat; tidak mengganti baseline CSV atau mengubah status menjadi verified. Jika mempertimbangkan keberadaan kandidat dari kedua sumber, 405 fasilitas belum mempunyai pasangan apa pun. Ini berbeda dari 408 kosong pada baseline CSV.

`daftar-perbedaan-master.json` mencatat ketiga perbedaan koordinat dan dua baris Ijen/Sempol, beserta locator/hash dan keputusannya. Tidak diperlukan koreksi atribut fasilitas. Nol lokasi dipromosikan menjadi verified; `public_eligible=false`, `data_quality_accepted=false`, dan `publication_allowed=false` tetap berlaku.

## Verifikasi dan handoff

Keluaran privat: data/processed/facility-master.json. Memuat 973 fasilitas, referensi keenam sumber, kandidat koordinat, seluruh master wilayah, count assignment termasuk nol, dan temuan rekonsiliasi. Hash pada output-verification.json. Dua eksekusi menghasilkan byte identik; hitungan unik, jumlah assignment dan seluruh flag lokasi diperiksa dari berkas tersimpan.

Suite Python final: 142 passed; compileall exit 0. Sebelas kasus khusus menguji exclusion agregat, kode duplikat/hilang, mapping gagal, subtotal salah, kategori melenceng, perbedaan atribut, koordinat bersama, missing points, konflik alias, pengulangan deterministik dan proteksi hash.

Status selesai untuk rekonsiliasi identitas dan hitungan. Review teknis agen; tidak mengklaim reviewer independen/dosen/UAT. Berikutnya WF-065 kurasi penduduk dan luas setelah commit/push terverifikasi; keputusan kualitas indikator, geometri dan lokasi tetap terpisah.
