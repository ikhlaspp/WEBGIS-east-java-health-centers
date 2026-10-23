# Pencarian dan review lokasi

Versi 1 · 23 Oktober 2026 · Penyusun: Codex. 565 kandidat+408missing adalah antrean awal, bukan keputusan lokasi.

Prioritas: titik resmi yang dapat ditautkan kode/bangunan → bukti alamat dan POI yang dapat direview → kandidat provider berizin. Query lengkap nama+alamat/desa+kecamatan+kabupaten+JawaTimur+Indonesia; simpan query persis dan provider/object_id. Fallback village/district tetap approximation, tidak eligible radius. Public Nominatim bukan default; [kebijakan](https://operations.osmfoundation.org/policies/nominatim/) harus diperiksa sebelum pemakaian sadar. Tidak ada batch provider baru dijalankan pada desain ini.

Review satu kandidat: cocokkan kode/nama/alamat/sumber→cek object type/building versus centroid→cek lonlat/CRS dan konteks peta→cek parent/pulau/duplikat→simpan evidence dan alasan→reviewer menerima/menolak. Facility accepted membutuhkan bukti bangunan/POI fasilitas yang cocok, bukan kedekatan nama saja. Snapshot verified hanya dipilih secara transaksi melalui accepted review dan source yang sama; lokasi harus ST_Equals candidate.

| Review result | Snapshot | Tindakan |
|---|---|---|
| pending | unverified bila point ada | Belum eligible |
| accepted + facility + bukti lengkap | verified | Eligible hanya setelah quality constraints lolos |
| rejected | rejected atau tetap kandidat lain yang sah | Candidate disimpan pada review; rejected point tidak dipakai radius |
| missing | missing/null | Tetap master dan antrean pencarian |

Lima kelompok duplikat (Kaliwates/JemberKidul, Urangagung/Urangagung2, Ngawi/Paron, PesantrenI/II, Sukorejo/Kepanjenkidul) direview per kode; co-location dapat sah jika bukti mendukung, tidak dedup otomatis. Titik tepat boundary menggunakan ST_Covers dan pemeriksaan kode resmi; tidak diseret ke dalam polygon. Konflik dalam50m batas diberi flag review_near_boundary, bukan auto-accept. Titik lebih jauh juga perlu review, bukan otomatis salah bila batas edisi berbeda. Pulau kecil tetap dalam cakupan tanpa bbox Jawa daratan saja.

Batch≤25 kode, input queue hash, deterministic order, pending/blocked/completed partition; gunakan checkpoint before/after. Bukti yang tidak dapat diakses menjadi blocked. Audit lokasi lama tidak dihapus; revisi setelah published membentuk rilis baru. Tidak ada target throughput yang mengubah standar facility verified. Workflow source→candidate→review decision→selected snapshot→eligibility dievaluasi ulang ketika sumber/edisi berubah.
