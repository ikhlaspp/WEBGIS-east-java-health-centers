# Laporan kualitas kandidat

Versi 1 · 23 Oktober 2026 · Penyusun: Codex.

Report header: report_id,release_id,input_revision,input_hash,policy_version,generated_at,pipeline_version,source_manifest hashes. Summary: raw/accepted/quarantined/aggregate, expected/received pages/IDs, source status, severity counts. Per-check entries: check_id,expected,actual,passed,affected_codes,locators,evidence paths dan resolution. `passed` laporan tidak boleh diisi hanya berdasarkan parser exit0.

Checks mandatory: 973unique/38kab dan kategori baseline; matching facility code sets; subtotal separation; mapping/code/edition completeness; duplicate/negative/unknown year-unit; OCR/alternative area review; polygon count/set/validity/pulau; selected review ownership/evidence/precision; registered/coordinate-present/eligible/excluded per wilayah; source license/edition decision; run/artefact hashes dan release consistency. Error code names: DUPLICATE_ID, UNMAPPED_REGION, SOURCE_INCOMPLETE, UNKNOWN_PERIOD, INVALID_UNIT, OCR_REVIEW_REQUIRED, INVALID_GEOMETRY, REVIEW_NOT_OWNED, LOCATION_UNVERIFIED, STALE_INPUT.

Setiap missing reason saling eksklusif untuk eligibility partition; jangan menghitung satu fasilitas dalam dua excluded buckets. Report per wilayah menyebut missing distribution dan contributors tetangga terpisah dari F administratif. Null/zero/unavailable ditampilkan eksplisit. Quality report immutable; approved_by/at nyata hanya saat review diberikan, tidak otomatis pelaksana script.

Promotion gate: blocker identitas/izin/edisi/constraint/security → reject; missing P/A → indikator no-data beralasan jika scope membolehkan; missing lokasi → hanya partial yang diputuskan, no zero-coverage untuk no eligible. Report boleh selesai namun passed=false. Validator pusat pada WF-036 memeriksa report cocok input_revision dan output run, bukan menerima path JSON yang dikirim operator tanpa verifikasi.
