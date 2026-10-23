# Bukti lokasi dan manifest review

Versi 1 · 23 Oktober 2026 · Penyusun: Codex.

Required setiap candidate: review_id, release_id, facility_code, source_id, provider, query, candidate_lon/candidate_lat atau null pair, provider_object_id nullable, precision_level, raw_response_private_path/hash, retrieved_at atau unknown reason. Evidence: URL/locator, evidence_note, evidence_sha256 bila salinan boleh disimpan, tanggal observasi/review, reviewer_id, decision_reason, result_status.

Precision enum facility/street/village/district/regency/unknown. Review result pending/accepted/rejected/missing; snapshot status missing/unverified/verified/rejected adalah konsep berbeda. Accepted wajib facility, point, source, reviewer/time dan bukti setidaknya URL atau note+hash valid. Bukti bukan string “verified by script”. Raw response privat bisa berlisensi terbatas; public metadata menyajikan ringkasan yang diizinkan, bukan credential/cache provider.

Contoh sintetis:

```json
{"review_id":"synthetic-review-1","release_id":"synthetic-draft","facility_code":"00000000001","source_id":"synthetic-source","provider":"fixture","query":"Synthetic clinic address","candidate_lon":112.0,"candidate_lat":-7.0,"provider_object_id":"fixture-building-1","precision_level":"facility","evidence_note":"Synthetic test evidence only","evidence_url":null,"evidence_sha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","reviewer_id":"synthetic-admin","reviewed_at":"2026-10-23T00:00:00Z","decision_reason":"Fixture acceptance path","result_status":"accepted","synthetic":true}
```

Contoh memakai label ID sintetis untuk menjelaskan bentuk; fixture DB menggantinya dengan UUID valid yang tetap ditandai sintetis. Snapshot selected review harus memiliki release/code/source/point sama; accepted review fasilitas lain ditolak meskipun koordinat identik. JSON evidence format dipisahkan dari database UUID contract. Hash valid bentuk tidak membuktikan bukti benar: reviewer memeriksa konten nyata.
