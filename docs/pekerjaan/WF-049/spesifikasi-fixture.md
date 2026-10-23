# Fixture sintetis

Versi 1 · 23 Oktober 2026 · Penyusun: Codex. Semua fixture diberi `synthetic=true`, namespace kode000…, source fixture dan release label TEST; test import menolak mempromosikannya ke produksi. Lokasi final tests/data/wf-NNN dan shared fixtures di tests/data/shared.

| Set | Isi minimal | Tujuan |
|---|---|---|
| F-DATA | duplicate facility_code, code leading zero, raw TOTAL, null/0/negative, unit hectare, angka lokal ambigu | D01/D04/D09/I02; failure terarah bukan silent repair |
| F-CROSS | Dua district bernama sama beda parent; alias rename pending/approved; dua raw observations menunjuk source locator sama | D05/D06/I03; no merge by name/no double P |
| F-RATIO | P30000/30001/60000/90001, F0/1/2/3, A0/null/2, T0/20000/30000 | A01–A08-PARAM, expected independen |
| F-GEO | Dua point≤2km untuk overlap; satu isolated; exactly boundary; outside; centroid village; dua pulau dalam MultiPolygon; invalid bowtie | G01–G11, include/exclude/union/clip/area |
| F-ACCESS | Guest, active admin, disabled admin; runtime/worker/publisher/migrator connections; draft/validated/published/withdrawn | No pengelola app role; allow/deny dan immutable child |
| F-CLI | Valid,expired,revoked,wrong ability tokens; forged actor; actor mismatch; same operation ID | S01/CLI audit/token tests |
| F-RACE | Dua candidate rilis valid, pointer version0, dua koneksi barrier saat publish | Tepat satu winner dan satu409, audit atomik |
| F-IMPORT | Valid CSV,wrong header,21MiBfile,HTML/script,formula-leading text,repeated hash,partial page set | S05-IMPORT P0, S05-EXPORT P1, D11/SRC tests |
| F-FAIL |429+Retry-After,timeout,200loginHTML,malformedPDF,changed schema,missing page,storage hash mismatch | Acquire completeness/retry bounds |
| F-REPRO | Tiny release with input/lock hashes, generated_at variations and deliberately corrupted file | R01–03/S06; deterministic content versus file metadata |

Geometri contoh di `contoh-spasial.json`: WGS84 points dan dua square islands, bukan polygon resmi. Expected area tidak hardcode dari implementasi; derive independent reference geodesic/AEQD, save reference version and analytic checks. Concentric equal-radius duplicate points union area equals one circle within tolerance, far points disjoint sum, clipped area bounded, r1≤r3≤r5. No database mutation dilakukan pada fase desain.

`formula-fixtures.json` berisi expected cases dari WF-041. Validator desain memakai Decimal/fractions independen, bukan source aplikasi. Implementasi kemudian memakai file yang sama dengan assertions expected/actual dan bukti environment; jangan menulis ulang expected supaya sama hasil bug.
