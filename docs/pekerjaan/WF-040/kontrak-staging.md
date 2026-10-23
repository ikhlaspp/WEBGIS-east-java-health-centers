# Kontrak staging dan promosi

Versi 1 · 23 Oktober 2026 · Penyusun: Codex.

CSV UTF-8 (BOM diterima/ditandai), delimiter comma dan RFC4180 quoting; newline dinormalisasi hanya untuk parsing, raw bytes/hash tetap asli. Gagal encoding/duplicate headers/unknown required field → batch fail, bukan menggeser kolom. File import operator≤20MiB, acquisition PDF jalur berbeda berlimit konfigurasi50MiB default dengan content-type/magic check; perubahan limit berdasar ukuran sumber tercatat. Tidak mengekstrak archive path traversal.

| Dataset | Header wajib raw | Normalized output |
|---|---|---|
| fasilitas | kode_puskesmas,nama_puskesmas,alamat,kecamatan,kabupaten,provinsi,kemampuan_pelayanan,karakteristik_wilayah | facility_code text, attributes, raw region names, source row/hash; district_id baru setelah mapping |
| koordinat | kode_puskesmas,latitude,longitude | Pair decimal nullable, candidate evidence/status; unggahan tidak dapat set verified |
| indikator | source_code/raw_name,parent,metric,value,unit,observation_period,locator | P bigint/A Decimal, source identity, raw/transform log; format adapter boleh berbeda sebelum canonical staging |
| polygon | source_code,parent_code,code_system,edition,geometry,source_crs | WGS84 MultiPolygon valid plus original CRS/hash; transform bukan relabel CRS |

Envelope row: batch_id,row_no,source_locator,source_hash,pipeline_version,raw_fields,normalized_fields,disposition,errors[]. Raw immutable. Disposition accepted/quarantined/aggregate mutually exclusive. Total rows = ketiganya; metadata/header lines counted separately in parser report. Quarantine menyimpan raw/locator dan issue codes, bukan hanya log exception. Corrected row creates revision/new batch preserving original.

Promosi satu draft dalam transaksi per consistent chunk dan final gate: code set/master/subtotals reconcile; mapping approved; source/unit/year complete untuk fakta terisi; geometry valid; no fake verified. Rilis tetap draft ketika quarantine memengaruhi identitas/master; nullable indikator boleh diekspos no-data sesuai keputusan scope/quality. Promote staging to draft bukan publish. Report/input_revision invalidated pada perubahan; repeat same batch idempotent, different hash/revision new record.
