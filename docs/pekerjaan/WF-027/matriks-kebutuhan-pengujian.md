# Matriks kebutuhan dan pengujian

Versi 1 · 23 Oktober 2026 · Penyusun: Codex. Semua uji aplikasi **not_run**. Tabel ini adalah traceability kebutuhan, bukan laporan kelulusan.

| Kebutuhan | Suite / test ID | Expected minimum | Tiket eksekusi | Bukti yang disimpan |
|---|---|---|---|---|
| FR-01 | Data D01,D02,D03,D04,D10 | 973 unik/38 kab; kategori dan himpunan kode cocok, subtotal terpisah | WF-106 | Query/count/diff sumber |
| FR-02 | Spatial G01–G04 | Hanya verified facility berbukti eligible; missing tetap master | WF-110 | Eligibility, evidence review, fixture anomali |
| FR-03 | UI W01–W04 | Zoom/cluster/detail/filter; semua identitas terakses | WF-117 | Browser trace dan screenshot |
| FR-04 | Spatial/UI G05,W05 | Join kode, angka/legenda/level konsisten | WF-110/118 | Set kode, expected kelas dan screenshot |
| FR-05 | Formula A01–A07,A08-PARAM | Edge ceil/null/zero, rasio total benar, run T immutable | WF-109/120 | SQL/Python expected vs actual |
| FR-06 | Spatial G06–G11 | Meter/union/clip/tetangga/pulau/toleransi | WF-111/112 | Fixture geometri dan reference results |
| FR-07 | Repro R01–R03 | Colab bersih, ulang hasil, HTML sesuai rilis | WF-123/124 | Notebook executed, manifest dan browser evidence |
| FR-08 | Integrasi I01,W01 | Laravel/Python/JS terintegrasi | WF-103/113/117 | Build/runtime/smoke logs |
| FR-09 | DB I01–I06,S06,S07 | Schema, constraint, role, transaksi dan restore nyata | WF-113/114/116/122 | SQL allow/deny dan restore report |
| FR-10 | UI W02–W04,W10 | Parent/filter/search/race konsisten | WF-117/119 | Browser assertions dan payload |
| FR-11 | Formula/UI A05,A06,W06 | F administratif tidak berubah karena filter lokasi | WF-109/118 | Expected count/kartu/label |
| FR-12 | Spatial/UI G05,W05 | Semua kode polygon/detail sesuai boundary_set | WF-110/118 | Join report/detail values |
| FR-13 | Data/UI D07,W07,R03 | Sumber/period/release/run dapat ditemukan | WF-107/118/124 | Metadata + UAT task 5 |
| FR-14 | UI/security W08,S05-EXPORT | Jika dipilih: CSV seluruh filter cocok, formula-safe | WF-120 | Export file/count/security fixture; deferred bukan pass |
| FR-15 | Security/integrasi S01–S04,S05-IMPORT,S07,I04–I06 | Guest ditolak; login/command/audit/publish/rollback aman; CLI actor diuji | WF-114–116/120 | Session/CSRF/actor/role/concurrency logs; UI P1 bersyarat |
| FR-16 | Formula A08-RANK | Jika dipilih: tie-break deterministik, null excluded | WF-120 | Ranking fixture; deferred bukan pass |
| FR-17 | Semua suite dan UAT | Test evidence nyata, defect/retest dan acceptance | WF-105–128 | Laporan suite/gerbang |
| NFR-01 | Data D01–D11, I02/I03 | Keunikan, FK/provenance/edisi, raw unchanged | WF-105–108/113 | Hash, validation/diff/error report |
| NFR-02 | UI W09,P03 | 360/768/1366 usable, panel tidak menutup kontrol | WF-119/121 | Device/viewport evidence |
| NFR-03 | Performa P01,P02,P02-COLD,P03 | Peta p95≤5s, per-endpoint API p95≤800ms warm/error<1% pada profil | WF-121 | Raw timings, profile, percentiles/cache |
| NFR-04 | UI W09,U01–U03 | Label/fokus/keyboard/tabel/legend teks | WF-119 | Manual checklist + browser trace |
| NFR-05 | Security S01–S05-IMPORT,S07,I05–I08 | Secret absent, input/role/session/CLI aman, error sanitasi | WF-114–116/120 | Sanitized negative tests and role matrix |
| NFR-06 | Repro D11,A08-PARAM,R01–R03 | Input/parameter/lock deterministik dan run immutable | WF-108/120/123/124 | Hash/manifests/diff |
| NFR-07 | Recovery S06 | DB dan file pulih, RPO≤24h/RTO≤4h terukur | WF-122 | Timestamp, hash/count/smoke restore |
| NFR-08 | UI/UAT W05–W07,G10,UAT-02–05 | Tidak salah tafsir nol/partial/radius/periode | WF-118/126 | Response peserta dan defect interpretasi |

## Normalisasi test ID dan fixture

S05-IMPORT adalah bagian backend P0; S05-EXPORT terkait CSV P1. A08-PARAM wajib meski ranking deferred; A08-RANK bersyarat. F-ACCESS berisi guest/admin dan runtime/worker/publisher/migration DB; hapus role aplikasi pengelola dari fixture lama. Fixture sintetis tidak menjadi data penelitian.

G01–G04 menguji validasi koordinat/status/evidence/duplikat; G05 join; G06 radius; G07 union; G08 clip/luas; G09 invalid/CRS/pulau; G10 tetangga/tepi; G11 referensi independen. D01–D11 mencakup count/kategori/pair/subtotal/mapping/master/provenance/OCR/null/salinan/idempotensi. Skenario kegagalan sumber (timeout/429/header berubah/pagination tidak lengkap) di WF-105 harus membuktikan promosi berhenti, raw tetap tersimpan dan retry terbatas.

## Urutan dan gerbang

Unit data/formula → DB PostGIS terisolasi → integrasi/role → browser/security → performa/restore/repro → UAT → defect/retest. CI DB sementara disiapkan sebelum WF-056, bukan menunggu WF-072. Tidak menggunakan SQLite untuk klaim spasial/grants. Test eksternal hanya environment yang dikelola; tile/geocoder dimock untuk load test.

Record per test: ID kebutuhan/test, code/release/run, environment/role, input/hash, steps, expected, actual, status, timestamp/pelaksana, evidence, defect/fix/retest. Status not_run/blocked tidak sama dengan passed. Rilis membutuhkan seluruh P0 relevan lulus, P1 terpilih lulus, nol critical/high, restore/repro/UAT nyata; waiver tidak boleh mengubah requirement tanpa CR.
