# ERD kandidat implementasi

Versi 1 · 23 Oktober 2026 · Penyusun: Codex. Finalisasi teknis untuk review, belum deployment atau accepted eksternal. Semua kolom dan FK dijelaskan dalam [kamus](kamus-data-final.md).

```mermaid
erDiagram
  data_sources ||--o{ boundary_sets : documents
  boundary_sets ||--o{ regencies : contains
  regencies ||--o{ districts : contains
  data_sources ||--o{ region_aliases : identifies
  districts ||--o{ region_aliases : resolves
  boundary_sets ||--o{ dataset_releases : used_by
  dataset_releases ||--o{ release_sources : records
  data_sources ||--o{ release_sources : referenced
  dataset_releases ||--o{ facility_snapshots : freezes
  districts ||--o{ facility_snapshots : locates
  dataset_releases ||--o{ district_indicators : observes
  districts ||--o{ district_indicators : measured
  facility_snapshots ||--o{ geocode_reviews : has
  geocode_reviews |o--o{ facility_snapshots : selected
  dataset_releases ||--o{ analysis_runs : analyzes
  analysis_runs ||--o{ indicator_results : computes
  analysis_runs ||--o{ coverage_results : covers
  analysis_runs ||--o{ artifacts : emits
  dataset_releases ||--o{ import_batches : receives
  import_batches ||--o{ staging_rows : parses
  dataset_releases ||--o{ quality_reports : validates
  analysis_runs |o--o{ dataset_releases : default_run
  dataset_releases |o--o{ active_release : points_to
  users ||--o{ sessions : authenticates
  users ||--o{ operator_tokens : owns
  users ||--o{ geocode_reviews : reviews
  users ||--o{ audit_logs : acts
  audit_logs ||--o{ outbox_events : notifies
```

Cardinalité optionnelle selected/default digambarkan sebagai relasi nullable; FK komposit mengikat review→fasilitas→rilis dan run→rilis. Hubungan sumber observasi memakai FK source_id dan locator, bukan manifest JSON saja. Regencies/districts membawa boundary_set_id eksplisit agar constraint lintas edisi dapat ditegakkan. Alur draft memiliki siklus review terpilih/default run; FK ditambahkan sesudah tabel ada, deferrable bila transaksi insert membutuhkan.

Tambahan terhadap planning awal: release_sources, indicator_results per run, quality_reports immutable, singleton active_release, operator_tokens dan outbox_events. Tujuannya menghilangkan rasio tanpa parameter, FK lintas rilis, audit terpisah transaksi dan actor CLI yang dapat dipalsukan dengan flag. Bukan fitur produk baru. Nama tabel teknis app.jobs/failed_jobs mengikuti driver queue framework pada migration, tidak mengubah model penelitian.
