# Constraints dan indeks

Versi 1 · 23 Oktober 2026 · Penyusun: Codex. Spesifikasi migration, belum SQL dijalankan.

## Identitas dan relasi

- UQ dataset_releases(id,boundary_set_id), districts(id,boundary_set_id), regencies(id,boundary_set_id). Fakta memiliki FK komposit ke release dan district menggunakan boundary_set_id yang sama; district parent juga FK komposit regency/set. I03 harus gagal sebelum publish, bukan hanya diperiksa UI.
- Geocode review FK(release_id,facility_code)→snapshot; UQ(id,release_id,facility_code). Snapshot selected_review memakai ketiga kolom ke review sehingga tidak dapat menunjuk review fasilitas/rilis lain. Tambahkan FK siklik sesudah create tables, DEFERRABLE INITIALLY DEFERRED untuk transaksi insert/select review.
- Analysis run UQ(id,release_id); coverage/indicator/artifact/default pointer memakai composite FK. Quality report UQ(id,release_id) dan release quality_report FK sama release.
- Published/withdrawn pernah terbit tidak dapat delete; sumber/boundary/alias shared yang dirujuk rilis frozen juga dilindungi. RESTRICT untuk seluruh FK penelitian; tidak cascade data historis.

## CHECK dan trigger

P≥0, A>0 bila nonnull; population/area yang terisi wajib year/source/locator/raw. facility_code text panjang11 digit untuk baseline ini; aturan per sumber/period tidak menjadi hukum semua data masa depan. Missing → location null, selected_review null. Verified → location valid/nonempty/Point4326, precision facility, coordinate_source dan selected review nonnull. Deferred constraint trigger memeriksa selected review accepted, bukti/reviewer/time, ST_Equals(candidate,selected location), coordinate_source_id=review.source_id dan pemilik; perubahan review juga memvalidasi snapshot terkait.

Semua geometry SRID4326, ST_IsValid dan nonempty; MultiPolygon untuk wilayah dan hasil area. Koordinat global finite, longitude[-180,180]/latitude[-90,90]; polygon containment/ketelitian tetap quality review, bukan bbox sempit yang membuang pulau. Invalid geometry di raw boleh disimpan private, bukan tabel domain. Radius IN(1000,3000,5000); count≥0; eligible+excluded=registered; available coverage mensyaratkan denominator>0, 0≤covered≤denominator dalam toleransi sebelum pembulatan dan pct[0,100]. JSON tidak mengandung NaN/Infinity.

Trigger immutability mengunci parent release FOR UPDATE sebelum setiap perubahan anak; hanya draft dapat berubah. Validate mengambil lock yang sama sehingga concurrent edit vs validate tidak lolos race. Setiap input edit menaikkan input_revision dan membatalkan report/run lama. Worker tidak diberi UPDATE status/published_by/default_run/input_revision secara bebas; increment oleh trigger. Trigger memeriksa OLD dan NEW release IDs saat perpindahan, bukan hanya NEW. Validated dapat kembali draft hanya melalui fungsi khusus yang mencabut validation, tanpa pernah published.

## Indeks terpilih

B-tree: facilities(release_id,district_id), (release_id,service_type,area_type), geocode_reviews(release_id,facility_code), districts(set,regency), runs(release,status), artifacts(release,run), batches(status,due_at), audit(created_at,actor_id). Unique keys menyediakan indeks PK/FK pencarian; tambah indeks FK yang belum tercakup prefix. GiST: wilayah geom, facility location, geography(location) untuk ST_DWithin; coverage geom hanya jika query spasial diperlukan. Nama/alamat search awal ILIKE pada973 baris + exact code; pg_trgm hanya setelah EXPLAIN menunjukkan kebutuhan, bukan dependency wajib.

Tes negatif: duplicate code, cross-boundary FK, review milik fasilitas lain, accepted tanpa evidence, selected location beda, P negatif, A0, SRID3857, empty polygon, child mutate setelah published/withdrawn, run beda release, audit delete, worker status update, stale validation dan dua publish bersamaan. Expected constraint/permission error dan transaksi rollback; bukan bypass constraint agar import selesai.
