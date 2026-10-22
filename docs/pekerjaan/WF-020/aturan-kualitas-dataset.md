# Aturan kualitas dataset

Versi 1 · 23 Oktober 2026 · Penyusun: Codex. Kebutuhan publikasi dan eligibility, bukan laporan dataset telah lulus.

| ID | Pemeriksaan | Respons bila gagal | Bukti penerimaan |
|---|---|---|---|
| DQ-01 | 973 kode unik tidak kosong, 38 kab/kota; count kategori sesuai sumber | Blokir kandidat bila duplicate/identitas hilang; koreksi count hanya dengan bukti sumber | Laporan D01/D02 dan diff koreksi |
| DQ-02 | Semua fasilitas memiliki parent/kode/edisi valid | Mapping ambiguous masuk quarantine dan blokir rilis master | Crosswalk reviewed; unmatched 0 pada master final |
| DQ-03 | Fakta terisi memiliki sumber, locator, unit, periode | Jangan hitung indikator terkait; keluaran no-data beralasan | D07/D09; tidak ada nilai terisi tanpa provenance |
| DQ-04 | Detail terpisah dari subtotal/grand total | Jangan menjumlah 2919 sebagai fasilitas; raw total tetap disimpan untuk cek | Detail 665 raw keys berjumlah 973, lalu mapping resmi |
| DQ-05 | Null, nol dan negatif berbeda | Null tetap null; negatif ditolak; nol sah memerlukan sumber | Fixture null/zero/negative dan error report |
| DQ-06 | Alias/nama sama/Sempol–Ijen | Tahan merge sampai kode+parent+edisi dan bukti cocok | Tidak menggandakan penduduk/luas/fasilitas |
| DQ-07 | Angka OCR atau konversi berisiko | Review per nilai/locator; total cocok tidak cukup | Lima wilayah OCR dan delapan sumber luas alternatif direview |
| DQ-08 | Pasangan titik lengkap, valid range, precision/status/bukti | Missing/unverified/rejected tidak masuk radius | Verified hanya facility dengan bukti dan reviewer |
| DQ-09 | Titik identik, di luar batas atau di boundary | Antrean review; jangan delete/move otomatis | Lima kelompok duplikat dan konflik spasial punya keputusan |
| DQ-10 | Polygon valid/nonempty, CRS/edisi/izin dan pulau lengkap | Blokir layer/analisis wilayah terkait; geometri repair harus diaudit | Kode master/polygon konsisten dan tidak kehilangan komponen |
| DQ-11 | release/run/input hash dan parameter konsisten | Blokir publish; hasil gagal tetap draft | Semua artefak/pointer satu versi dan audit atomik |

## Cakupan penuh dan parsial

Asumsi kerja yang direkomendasikan: rilis analisis parsial boleh dipersiapkan, menggunakan hanya titik verified facility; pemilik kebutuhan diminta mengonfirmasi sebelum gerbang kebutuhan diterima. Penuh mensyaratkan seluruh 973 fasilitas eligible dan boundary lengkap sesuai cakupan. Ketidakpastian sumber tidak berubah menjadi persetujuan parsial.

Setiap wilayah/run mencatat registered_count, coordinate_present_count, verified_facility_count, eligible_count, excluded_count dan alasan eksklusi yang saling eksklusif; eligible + excluded = registered untuk scope master input. Untuk kontribusi tetangga, catat contributors_count terpisah agar denominator administratif tidak berubah. Minimal satu titik eligible diperlukan untuk menerbitkan hasil radius parsial; bila tidak ada, hasil coverage adalah unavailable/null, bukan bukti cakupan 0%. Bila scope master benar-benar F=0 dan sumber lengkap, hasil geometri dapat 0 dengan alasan valid.

Label tetap “Analisis parsial: x dari y fasilitas terverifikasi” pada layer, tabel dan artefak. Tidak ada target persentase yang membenarkan titik perkiraan sebagai verified. Wajib laporkan distribusi missing per wilayah untuk menghindari kesan subset representatif. F administratif tetap seluruh master, bukan eligible_count.

## Blokir dan pengecualian

Identitas tidak konsisten, akses draft terbuka, provenance palsu, operasi publish tidak atomik, unit tidak diketahui untuk nilai yang ditampilkan, titik tanpa bukti dalam buffer dan geometri/edisi tak disetujui adalah blocker. Kekurangan koordinat dapat diterima hanya dalam mode parsial yang diputuskan; indikator P/A missing boleh no-data dengan alasan eksplisit. Reviewer data memeriksa bukti, penerima rilis memutuskan pengecualian per ID/versi/owner/tanggal; tidak ada blanket waiver. Defect kritis/tinggi tetap menghalangi rilis. Pilihan parsial bukan pengesahan dataset saat ini.
