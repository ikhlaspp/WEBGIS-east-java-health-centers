# Prosedur perubahan

Versi 1 — 23 Oktober 2026. Usulan baseline untuk review WF-G1.

Perubahan kebutuhan, rumus, periode sumber, polygon, kriteria kelayakan data, target uji, biaya, tenggat, atau prioritas fitur setelah baseline diterima harus memiliki CR. Koreksi penulisan tanpa perubahan makna cukup dicatat pada riwayat dokumen.

1. Pelapor mengisi template CR dengan kondisi awal, alasan, alternatif, dan bukti. PM memberi ID serta status `proposed`.
2. PIC menelusuri kebutuhan → desain → tiket → uji → dokumentasi. Estimasi ulang usaha, biaya, waktu tunggu dan risiko; pisahkan yang belum diketahui.
3. Reviewer memeriksa dampak. Penerima baseline memutuskan `accepted`, `rejected`, atau `needs_information`, dengan nama, tanggal, versi, dan alasan. Diam atau keterlambatan bukan persetujuan.
4. Untuk keputusan accepted, perbarui register keputusan dan dokumen terdampak. Naikkan versi mayor bila mengubah baseline, minor untuk klarifikasi kompatibel. Pertahankan versi lama melalui Git.
5. Buka kembali tiket terdampak menjadi in_progress atau blocked; jangan mempertahankan done apabila buktinya tidak lagi berlaku. Jalankan retest dan review gerbang yang terdampak sebelum meneruskan antrean.

Sebelum baseline pertama diterima, ketidakpastian masuk register keputusan. Simulasi berikut tidak mengubah scope proyek.

## Simulasi CR-SIM-001: analisis spasial penuh menjadi parsial

Pemicu hipotetis: beberapa fasilitas tidak memiliki titik terverifikasi pada batas waktu kurasi. Alternatif: lanjut kurasi; tunda rilis; atau analisis subset terverifikasi dengan keterbatasan eksplisit. Tidak boleh mengganti titik dengan centroid.

Dampak: WF-020/023/024 merevisi aturan kelengkapan dan klaim; WF-039/042 mendesain eligibility; WF-068–071 membekukan jumlah eligible/excluded beserta sebab; WF-079/080 menghitung hanya titik eligible; WF-090 menampilkan cakupan parsial; WF-110/112/126 menguji denominator, subset, serta pemahaman pengguna; WF-145 menyatakan batas kesimpulan. Statistik tabular tetap menggunakan master tervalidasi dan tidak diam-diam mengikuti subset spasial.

Usaha dan jadwal: perlu menghitung ulang berdasarkan hasil kurasi nyata, belum ada nilai penghematan yang sah. Risiko bias spasial harus dicatat. Dokumen calon revisi: SRS versi 2, spesifikasi analisis versi 2, matriks uji versi 2, manifest eligibility baru. Versi tersebut **contoh**, belum dibuat atau diterima.

Keputusan simulasi: `needs_information`; bukti yang dibutuhkan adalah laporan WF-071, jumlah excluded per wilayah, serta opsi jadwal. Pihak pemutus: penerima SRS/gerbang terkait yang masih perlu ditetapkan. Penelusuran permintaan → dampak → keputusan → revisi → retest tersedia tanpa mengarang persetujuan.
