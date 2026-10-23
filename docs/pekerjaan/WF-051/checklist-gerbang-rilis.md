# Checklist gerbang rilis

Versi 1 · 23 Oktober 2026 · Penyusun: Codex. Semua kotak belum merupakan bukti lulus.

- [ ] Data: master/kode/count/kategori direkonsiliasi; parent/edition/izin/provenance valid; quarantine blockers terselesaikan; raw immutable.
- [ ] Analisis: P/A/F/T/null/zero/agregasi lulus; eligibility facility verified berbukti; union/clip/pulau/tetangga/denominator/toleransi benar; full/partial diputuskan dan dilabeli.
- [ ] Aplikasi: P0 seluruhnya lulus, identity/run consistent di API/UI/HTML; missing accessible via table; no-data/zero dan mobile/keyboard benar.
- [ ] Security: role non-owner/anon deny, login/CSRF/session/CLItoken/input/XSS lulus; immutable published; publish race/failure atomic; audit dan cache/withdraw visibility benar.
- [ ] Operasi: staging performance sesuai profil, DB+artifact restore RPO/RTO terukur, monitoring/backup/owner nyata, reproducible Colab clean dan lockfiles.
- [ ] P1: setiap item selected/deferred memiliki keputusan; selected punya test lulus; deferred bukan passed. S05-IMPORT dan A08-PARAM tetap P0.
- [ ] Akademik/UAT: minimal peserta dan80%mandiri, no unresolved critical misunderstanding, sources/metode/limitations ditinjau, artefak satu revision/release/run.
- [ ] Delivery: commit identitas pengguna, diff tepat, SHA remote verified; release manifest dan handoff lengkap.
- [ ] Penerima: nama/kewenangan,tanggal,versi/hash,accepted/rework dan alasan nyata; bukan tanda tangan pelaksana script menggantikan stakeholder.

Severity critical: secret exposure, public write, corrupt publish/data, kesimpulan utama salah; high: core function/formula/join/buffer/auth salah; medium: gangguan dengan workaround aman; low: kosmetik. Nol critical/high untuk rilis. Medium/low waiver harus memuat impact/owner/deadline dan keputusan penerima tanpa melanggar P0. Tidak ada waiver yang menyulap blocked menjadi passed.

Retest failed cases setelah fix; regresi suite modul terpengaruh dan integration smoke; perubahan metode/DB/grants memerlukan cross-implementation/role/race sesuai area. Expected/threshold dibekukan sebelum tes; perubahan sesudah hasil membutuhkan CR dan rerun, tidak menimpa bukti lama. Record actual status setiap kotak pada WF-G4/5/6 yang relevan; gerbang desain WF-G3 hanya menilai kesiapan desain, bukan penerimaan aplikasi.
