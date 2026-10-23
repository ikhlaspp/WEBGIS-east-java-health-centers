# Normalisasi dan crosswalk

Versi 1 · 23 Oktober 2026 · Penyusun: Codex.

Pipeline pure functions menerima raw_fields+source_spec dan mengembalikan typed_fields+issues+transform_log. Pertahankan raw original immutable, normalized text hanya untuk matching/display. Unicode normalize NFC, trim outer whitespace, collapse internal whitespace pada match_key; kapitalisasi/casefold hanya match_key. Kode text tidak dikonversi int, tidak dipotong dari facility_code.

| Input / metadata | Expected | Reject/notes |
|---|---|---|
| `30.001`, locale id_ID, integer jiwa | 30001 | Bila locale tidak diketahui: ambiguous_number |
| `1.234,50`, id_ID, km² | Decimal1234.50 | Decimal disimpan presisi penuh |
| `181280`, unit hectare | 1812.80 km² | factor0.01 dan raw unit tercatat |
| blank / `...` (source missing marker) | null + reason | Tidak menjadi0 |
| `0` penduduk | 0 | Sah bila sumber; rasio penduduk/fasilitas memakai domain |
| `0` luas, nilai negatif | quarantined | Jangan abs/clamp agar valid |
| `00123` kode | `00123` | Leading zero dipertahankan |
| Dua nama sama, parent berbeda | Dua entitas | Nama tanpa parent tidak cukup |

Crosswalk key=(source_id,source_system,source_edition,raw_parent,raw_name/raw_code,target_boundary_set). Urutan matching: kode resmi+parent+edisi tepat → alias approved dalam konteks → manual pending. Fuzzy score hanya calon, tidak auto-approve. Mapping evidence memuat sumber perubahan, reviewer/time dan cardinality. Split/merge unit administratif membutuhkan keputusan alokasi observasi; tidak menyebarkan P/A proporsional tanpa data pendukung.

Sempol–Ijen: kumpulkan kode dan catatan edisi→bandingkan parent Bondowoso/masa berlaku→review apakah rename unit yang sama atau unit berbeda→bila rename, satu target distrik, setiap fasilitas berdasarkan kode tetap satu dan hanya satu observasi P/A sumber dipilih→jika konflik, quarantine dan no-data. Jangan menjumlah dua baris gabungan hanya karena alias mirip. Target666 tidak membenarkan menghapus667baris staging.

Dedup fakta memakai source_id+table/row locator+observation_period+target code, bukan angka kebetulan sama. Duplicate identical input boleh idempotent; duplicate conflicting values butuh keputusan prioritas sumber, simpan seluruh raw. Report unmatched, one-to-many, many-to-one, ambiguous/year mismatch beserta affected facilities. Hanya approved dipromosikan; publikasi master mensyaratkan seluruh fasilitas mapped sesuai boundary edition. Fixture F-DATA/F-CROSS membuktikan kasus nama kembar, leading zero, alias dan double-count.
