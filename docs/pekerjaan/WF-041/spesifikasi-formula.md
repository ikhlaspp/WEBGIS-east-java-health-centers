# Formula dan presisi

Versi 1 · 23 Oktober 2026 · Penyusun: Codex. Turunan [katalog indikator](../WF-021/katalog-indikator.md); bukan hasil implementasi aplikasi.

P∈integer≥0 atau null, F∈integer≥0 (master administratif lengkap), A∈Decimal>0 atau null, T∈integer>0 default30000. Negative/invalid inputs ditolak, tidak clamp. IND-01 density=P/A; IND-02 ratio=P/F; IND-03 facilities_per_30000=F×30000/P; IND-04 need=ceil(P/T); IND-05 deficit=max(0,need−F); IND-06 without_facility=(F=0); IND-07 coordinate_present/F×100; IND-08 eligible/F×100.

Domain: missing numerator/denominator→null reason; IND-02 F0→null+flag; IND-03 P0→null; need P0→0; density A0 input invalid, setelah kualitas diekspos null reason; F0 kualitas percentage null. T parameter tidak mengubah label tetap30000 pada IND-03; jika kelak skala itu parameterized perlu nama/unit/run change eksplisit.

Arithmetic integer untuk P/F counts dan ceil sebagai `(P+T−1)//T`, bukan floating threshold. Decimal/numeric untuk rasio, tanpa pembulatan internal sebelum serialisasi storage numeric(24,12). SQL/Python absolute difference≤1e-9 before display; values at storage limit harus ditolak overflow, bukan truncate tanpa laporan. Display locale id_ID dua desimal untuk ratio/density/percent; integers without decimals. HALF_UP untuk display, tidak mempengaruhi sorting/computation.

Aggregate P/F=sumP/sumF hanya cakupan anggota lengkap; missing membuat total penuh null dengan optional labeled subset (P dan F scope sama). Deficit aggregate=sum per-district deficit, bukan recompute ceil total. Percent quality dihitung count totals, bukan average percentages. Coverage dihitung luas union clipped wilayah, bukan rata-rata kecamatan atau total area overlap. Service/coordinate filter tidak mengubah F administratif.

Run immutable menyimpan T, method_version, formula_version, input/boundary hashes, code revision dan eligibility. SQL reference independen dan Python canonical dibanding fixture; PHP/API membaca stored results/run. Tidak menulis ulang rumus pada Blade/Folium. A08-PARAM wajib bahkan bila A08-RANK tidak dipilih.
