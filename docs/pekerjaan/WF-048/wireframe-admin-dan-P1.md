# Login admin dan alur operasi

Versi 1 · 23 Oktober 2026 · Penyusun: Codex. Kandidat scope P0-first; empat P1 belum dipilih secara eksplisit, sehingga tidak dibuat desain layar opsional seolah telah disetujui.

```text
LOGIN (desktop card420px / mobile width100% minus32px)
┌ Admin ─ kembali ke situs publik ┐
│ Label email                     │
│ [email........................] │
│ Label password                  │
│ [password.....................] │
│ [Masuk]                         │
│ Error generik / coba lagi nanti │
└─────────────────────────────────┘

ADMIN P0 LANDING
┌ Identitas admin | [Logout POST] ┐
│ Sesi aktif; operasi via CLI     │
│ [Panduan operator]              │
│ Tidak ada dashboard P1 palsu    │
└────────────────────────────────┘
```

Login gagal tidak menyebut email ada/tidak, throttle status429/time retry. Sesi expired→login+pesan, bukan otomatis mengulang tindakan tulis lama; admin denied403 dengan kembali publik. Logout menginvalidasi sesi server/token CSRF; admin CLI token terpisah tidak dianggap sesi browser. Tidak ada registrasi publik atau reset email yang belum dirancang.

Padanan command P0 (nama target): `gis:import`, `gis:review-location`, `gis:analyze`, `gis:validate-release`, `gis:publish`, `gis:rollback`, `gis:audit`. Semua meminta operator token dari prompt/file protected, bukan argument plaintext; identity/ability diperiksa WF-035. `gis:publish --release=<uuid> --expected-active-version=<n>` menampilkan preview release/run, input hash, kualitas/partial, source periods, exclusions, artefact inventory dan target pointer. Operator memasukkan alasan dan konfirmasi preview hash; konfirmasi bukan mengganti auth/validator. CLI noninteractive hanya dengan approved input manifest/operation ID dan token ability yang tepat.

Rollback preview menampilkan from/to release/run, availability/hash, expected pointer version dan reason; stale pointer409. Analyze tidak publish otomatis; review tidak auto-verify centroid. Audit read command hanya authorized admin dan output disanitasi.

P1 dashboard batch, review/publish UI, CSV public dan ranking ditahan. Bila pemilik memilihnya, WF-097/098 memakai service/policy/preview/token-web auth terotorisasi yang sama, WF-099 memakai filter export dan S05-EXPORT, WF-100 memakai A08-RANK dan null/tie-break. Tidak menunda P0 login, command lifecycle, file validation atau A08-PARAM.
