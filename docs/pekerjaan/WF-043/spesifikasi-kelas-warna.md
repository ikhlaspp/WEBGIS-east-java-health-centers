# Kelas warna tetap

Versi 1 · 23 Oktober 2026 · Penyusun: Codex. Mengikuti WF-022, tanpa perubahan scope atau quantile dinamis.

| Metric | Predikat ordered | Warna kelas berurutan |
|---|---|---|
| facility_count | =0;1–2;3–5;6–10;≥11 | #eff3ff,#bdd7e7,#6baed6,#3182bd,#08519c |
| population_per_facility | ≤30000;>30000≤60000;>60000 | #deebf7,#9ecae1,#3182bd |
| density | =0;>0≤1000;>1000≤5000;>5000 | #eff3ff,#bdd7e7,#6baed6,#08519c |
| indicative_deficit | =0;=1;2–3;≥4 | #eff3ff,#bdd7e7,#6baed6,#08519c |

Evaluate quality first: missing inputs → no_data #bdbdbd dengan hatch/text; ratio F0+knownP → without_facility #fdae6b; F0+missingP → no_data with secondary without_facility flag. Zero numeric selalu kelas0, bukan no-data. Predikat closed/open tepat seperti tabel; negative values error upstream. Text legend menyebut unit dan definition/period; palette bukan satu-satunya pembeda.

Legend JSON memiliki version `fixed-v1`, metric, unit, ordered breaks, labels dan special classes. Change filter/zoom tidak recalibrate; change metric mengganti legend dan layer atomik. Kabupaten/kecamatan memakai kelas sama agar arti warna stabil; area kabupaten yang terkumpul dalam kelas tinggi bukan alasan mengganti scale diam-diam. Uji boundary29999/30000/30001/60000/60001 dan Fcount0/1/2/3/5/6/10/11, null dan without_facility.
