# Otorisasi, grants dan identitas operator

Versi 1 · 23 Oktober 2026 · Penyusun: Codex.

Web guest tanpa akun; admin login Laravel session dengan password hash framework, regenerate session, CSRF, cookie secure/HttpOnly/SameSite=Lax, idle30min/absolute8h, throttle5 gagal/menit per identitas+IP. Login pesan generik; logout POST menginvalidasi sesi. Web tanpa auth redirect login, API401; admin tanpa ability403; draft melalui public404. Tidak ada Supabase Auth/auth.uid atau role aplikasi pengelola.

| DB role | Allow | Deny |
|---|---|---|
| runtime | SELECT domain published melalui RLS; SELECT kolom auth users; sessions/job DML seperlunya | Semua domain write, staging, tokens, lifecycle functions, DDL, audit edit |
| worker | Sumber/staging/draft read/write dengan column grants; SELECT shared frozen reference; fungsi review/run/validate terbatas | Status publish/withdraw, active pointer, direct audit edit, mutate validated/published/withdrawn |
| publisher | SELECT candidate/report untuk verifikasi; EXECUTE publish/rollback/withdraw dengan token/expected pointer | Arbitrary data edit, DDL, direct status/pointer/audit DML |
| lifecycle_owner NOLOGIN | Privileges minimum untuk security-definer transitions/validator/audit/outbox | Tidak diberikan sebagai membership runtime/worker/publisher; bukan koneksi harian |
| migrator | DDL/grants sesuai deploy | Tidak dipakai web/job; akses terpisah |
| anon/authenticated Supabase | Tidak ada USAGE schema privat atau table rights | Semua app/gis/staging |

RLS per command mengikuti database role dan release status; source/boundary visibility hanya yang dirujuk release published. ENABLE/FORCE RLS pada domain dengan policy lifecycle_owner yang eksplisit jika owner terkena FORCE, tanpa recursive policy query. Helper visibility membaca release melalui jalur terkontrol; uji recursion/infinite policy dan tidak bocor staging. Security-invoker views (PG15+) mengikuti role caller; tidak mengandalkan view owner untuk melewati RLS. Tidak grant TRUNCATE/CREATE/REFERENCES pada runtime. [PostgreSQL RLS](https://www.postgresql.org/docs/current/ddl-rowsecurity.html) menjelaskan owner/BYPASSRLS dan operasi yang tidak dilindungi RLS; grants tetap wajib.

Security-definer hanya fungsi sempit, static SQL dengan identifier qualified, search_path=pg_catalog dan objek extensions/gis/app qualified. Revoke EXECUTE FROM PUBLIC dalam transaksi create function yang sama; tidak ada dynamic SQL input user. Fungsi memverifikasi capability dan bukan sekadar current role. [CREATE FUNCTION](https://www.postgresql.org/docs/current/sql-createfunction.html) mendasari pengamanan search_path/execute; fungsi tidak menjadi akses query umum.

## Actor CLI yang tidak dapat dipalsukan dengan flag

Operator provisioning membuat token acak minimal256bit, menyimpan SHA256 hash, user_id, abilities, expiry≤8h dan revoke state di app.operator_tokens. Plain token diberikan sekali melalui kanal privat dan file permission terbatas atau prompt tersembunyi; tidak command argument/history/log. `--actor` tidak menjadi autentikasi. CLI membaca token, service/function menghitung hash dan lookup active user, expiry/revoke/ability; actor audit berasal dari row token, bukan nilai kiriman klien. DB function untuk tindakan sensitif memverifikasi token lagi, dalam transaksi; publisher connection sendiri tidak cukup. Token issuance/revocation oleh operator kontrol terpisah, bukan web runtime umum.

Command review/analyze/validate memakai ability khusus; publish/rollback/withdraw memiliki abilities terpisah. Fungsi memeriksa input_revision/expected_active_version dan audit actor/token_id/request_id. Retry idempotent memiliki operation ID; audit tidak menduplikasi efek. Token expired/revoked/wrong ability/actor mismatch ditolak. Service account automation harus terdaftar eksplisit, bukan menyamar sebagai pengguna manusia.

Matriks uji wajib koneksi terpisah runtime/worker/publisher/anon/owner-control: SELECT draft, UPDATE status, UPDATE published child, EXECUTE function tanpa token, token palsu/expired, valid ability, audit deletion, Data API exposure. RLS tidak memakai session GUC actor yang dapat disetel caller sebagai sumber otorisasi. Secret publisher tidak diberikan ke web process. Detail implementasi enforcement diverifikasi pada WF-074/086/116, bukan lulus dari dokumen ini.

Trusted fields: worker tidak mendapat direct write quality_reports.approved_by/approved_at/passed, geocode_reviews keputusan/reviewer, analysis_runs.status succeeded, atau selected_review tanpa jalur fungsi terotorisasi. Function review/run finalization/validate memeriksa token ability, row ownership dan actual checks, lalu menulis trusted fields. Report upload hanyalah input kandidat; validator menghitung ulang checks wajib dan hash, tidak percaya passed=true dari file. Runtime tidak dapat mint operator tokens atau mengubah is_admin/is_active.
