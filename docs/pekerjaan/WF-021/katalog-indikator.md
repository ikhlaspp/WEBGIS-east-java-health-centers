# Katalog indikator dan agregasi

Versi 1 · 23 Oktober 2026 · Penyusun: Codex. Formula kandidat yang harus diuji pada fixture sebelum implementasi diterima.

P = penduduk jiwa; A = luas statistik km²; F = jumlah fasilitas administratif dalam snapshot setelah mapping; T = parameter jiwa/fasilitas, default 30000, bilangan positif. F tidak dihitung dari marker atau hasil filter layanan. Tahun P/A/fasilitas disimpan terpisah. Parameter T bersifat analitis dan bukan penetapan kepatuhan hukum.

| ID | Indikator / unit | Formula | Null/nol/validasi |
|---|---|---|---|
| IND-01 | Kepadatan, jiwa/km² | P/A | P null atau A null/≤0 → null beralasan; P=0,A>0 → 0 |
| IND-02 | Penduduk per fasilitas, jiwa/fasilitas | P/F | F=0 → null dan tanpa_puskesmas; P null → null; tanpa Infinity |
| IND-03 | Fasilitas per 30000 jiwa | F×30000/P | P≤0/null → null; skala 30000 tetap, berbeda dari parameter T |
| IND-04 | Kebutuhan indikatif, fasilitas | ceil(P/T) | P null → null; P=0 → 0; T≤0/noninteger ditolak |
| IND-05 | Defisit indikatif, fasilitas | max(0, IND-04−F) | Input tidak lengkap → null; tidak negatif |
| IND-06 | Tanpa puskesmas, boolean | F==0 | Berlaku terpisah dari P, termasuk P=0; F unknown bukan false |
| IND-07 | Koordinat tersedia, persen | coordinate_present/F×100 | Pair lengkap bukan bukti verified; F=0 → null dengan denominator 0 |
| IND-08 | Lokasi eligible, persen | verified_facility/F×100 | Review bukti dan precision facility wajib; F=0 → null |

## Agregasi

Jumlah F berasal dari semua fasilitas scope administratif. Rasio kabupaten/provinsi = sum(P)/sum(F) untuk pasangan wilayah yang lengkap dan konsisten, bukan rata-rata rasio kecamatan. Jika ada P missing, indikator total populasi/rasio penuh null; boleh tampilkan subtotal lengkap dengan label subset, kode wilayah yang masuk, P dan F pada subset yang sama, serta jumlah wilayah excluded. Dilarang membagi sum(P known) dengan F seluruh wilayah tanpa menjelaskan denominator.

Kepadatan agregat = sum(P)/sum(A) pada cakupan lengkap; subset hanya bila P/A tiap anggota lengkap dan berlabel. Defisit kabupaten = sum(defisit kecamatan); jika ada anggota null, total penuh null dan subtotal diberi label. Jangan mengganti dengan max(0,ceil(sum(P)/T)−sum(F)). Persentase kualitas dihitung dari total count, bukan rata-rata persentase kecamatan. Perubahan filter layanan/koordinat tidak mengubah IND-01–06 administratif.

## Acuan hitung

| Input sintetis | Expected |
|---|---|
| P=30000,F=1,T=30000 | rasio 30000, kebutuhan 1, defisit 0 |
| P=30001,F=1,T=30000 | kebutuhan 2, defisit 1 |
| P=10000,F=0 | rasio null, flag true, kebutuhan 1, defisit 1 |
| P=0,F=0 | rasio null, kebutuhan 0, defisit 0, flag true |
| P=null,F=1 | rasio/kebutuhan/defisit null; F tetap 1 |
| P=10000,A=2 | kepadatan 5000 |
| A: P=30000,F=1; B: P=90000,F=2 | rasio gabungan 40000, bukan 37500 |
| A: P=30001,F=1; B: P=29999,F=1 | jumlah defisit kecamatan 1; defisit dari total 0, jangan dipertukarkan |

Hitung dengan presisi penuh, integer untuk count/ceil, tampilkan rasio/kepadatan dua desimal dan persen dua desimal. Pembulatan tidak boleh masuk kembali ke kalkulasi. Uji kesetaraan count tepat dan rasio SQL/Python selisih ≤1e-9 sebelum format. Run menyimpan T, metode, input hash dan versi kode; perubahan T menghasilkan run baru, termasuk bila ranking P1 ditunda.

Setiap nilai API/artefak menyertakan unit, scope, observation_periods, source_ids, completeness/reason, release_id, run_id dan parameter. Kebutuhan/defisit adalah indikator penelitian, bukan rekomendasi lokasi pembangunan atau ukuran kualitas layanan.
