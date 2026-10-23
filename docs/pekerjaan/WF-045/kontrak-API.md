# Kontrak API v1

Versi 1 · 23 Oktober 2026 · Penyusun: Codex. Semua contoh sintetis; endpoint belum diimplementasikan. Browser mengakses Laravel, tidak Supabase langsung.

## Context dan envelope

GET tanpa release_id membaca active pointer sekali; request berikut frontend selalu mengirim release_id dan analysis_run_id dari respons. Bila run tidak diminta, pilih default run rilis yang immutable. Run salah pasangan atau unpublished menghasilkan404. Visibility diperiksa sebelum cache. Rilis withdrawn juga404; no active release menghasilkan503 code=NO_PUBLISHED_RELEASE, bukan dataset kosong palsu. `meta` membawa release_id,analysis_run_id,boundary_set_id,source_periods,coordinate_coverage,warnings,generated_at. Daftar `/releases` merupakan katalog publik dengan active_release_id; bukan data yang dicampur dua rilis.

Collections envelope `{data:[],meta:{...}}`, detail `{data:{...},meta:{...}}`, GeoJSON `{type:'FeatureCollection',features:[],meta:{...}}`; error `{error:{code,message,request_id,fields?}}`. Decimal metric JSON number finite atau null; source counts integer; codes string; time RFC3339 UTC. Tidak menampilkan private_path, raw response atau actor audit ke publik.

| GET /api/v1 path | Parameter tambahan allowlist | Data / batas |
|---|---|---|
| /releases | page,per_page | Published metadata sorted published_at desc,id; active flag; withdrawn/draft excluded |
| /regions | level=regency/district, parent_code | Scoped code/name/parent/edition; district parent wajib, bukan district dari set lain |
| /facilities | q,regency_code,district_code,service_type,area_type,coordinate_status,page,per_page,sort | Semua fasilitas termasuk missing; total seluruh filter, pagination terpisah marker |
| /facilities/{code} | context | Detail snapshot+source+quality; code11digit baseline |
| /map/points | filter fasilitas,q,bbox | Semua matching points sampai973 pada baseline; missing tidak geometry; meta filtered_registered/mapped/missing/verified |
| /map/regions | level,parent_code,metric,geometry_detail | Full scoped code set; metric count/density/population_per_facility/indicative_deficit; no service filter agar F tidak ambigu |
| /statistics | regency_code,district_code | Administratif F/P/A/ratios, completeness and years; tidak menerima service/coordinate filters |
| /analysis/buffers | analysis_run_id,radius_m,regency_code,district_code,geometry_detail | Stored run result, eligible/excluded/contributing, areas/percentage/partial label; unavailable geometry null/reason |
| /sources | context | Sanitized source metadata/locator/license_note/limitations; private_path/raw hidden |

Semua data endpoints menerima release_id/analysis_run_id (run tak dipakai untuk raw list tetap divalidasi context dan dikembalikan default). Nomenklatur code dipilih untuk public API agar identitas stabil; proposal awal `_id` internal tidak diekspos sebagai code. Mapping detail ke UUID DB di ReleaseContext/RegionRepository. Jangan menerima `_id` aliases yang ambigu tanpa versioned contract.

Validation: q string≤100 unicode characters, trim, empty equivalent omitted; page≥1,per_page default50 max100; sort enum name,-name,code,-code defaultcode dan secondarycode stabil. Service Rawat Inap/Non Rawat Inap; area Perdesaan/Perkotaan/Terpencil/Sangat Terpencil; coordinate_status enum missing/unverified/verified/rejected. Parent-district mismatch422. bbox exactly4finite numbers xmin,ymin,xmax,ymax dengan geographic bounds dan min<max; antimeridian wrapping unsupported pada Jatim,422. Radius allowlist1000/3000/5000. Unknown parameter400; invalid value422; route/object unavailable404; rate-limit429+Retry-After; dependency timeout503. Public limits kandidat60requests/min/IP dengan config; load test uses dedicated allowlisted test profile, tidak memalsukan normal behavior.

`/map/points` tidak memakai page sehingga 50table rows tidak menghilangkan marker diam-diam. Bbox applies point subset only; meta menyebut view_count vs full filter_count. Missing masuk full filter total, bukan bbox mapped count. Per_page page di luar akhir mengembalikan data[]/total/page yang benar. Search parameterized escaped wildcard sesuai literal search, tidak string SQL concatenation. All sorts allowlist.

Mutations P0 melalui CLI service, bukan public GET. Login/logout web routes dan CSRF dijelaskan WF-035. File validation backend P0 tetap ada. CSV/ranking/dashboard endpoints tidak diekspos pada scope kandidat P0; jika dipilih revisi kontrak dan tes sebelum fitur. Response examples [JSON](contoh-respons-API.json) meliputi semua9paths, missing detail, error dan unavailable buffer. Nilai contoh sintetis, bukan observasi penelitian.
