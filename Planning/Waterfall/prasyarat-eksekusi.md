# Register prasyarat eksekusi

Register ini menunjukkan keputusan/bukti yang diperlukan, bukan persetujuan yang sudah diberikan. Nilai usulan tetap usulan. Saat melaksanakan tiket penghasil keputusan, catat nilai final, pihak pemutus, tanggal, sumber bukti, dan tiket yang memakai keputusan tersebut pada handoff/log. Jangan memulai pekerjaan yang bergantung pada keputusan yang masih terbuka; pekerjaan menyiapkan pilihan dan bukti dapat dilanjutkan. Ikuti antrean serial yang berlaku.

Keterangan `open` berarti bukti final belum tercatat di paket ini, bukan klaim bahwa pemilik belum memiliki akun atau belum pernah memberi arahan. Periksa instruksi pengguna dan bukti yang tersedia terlebih dahulu. Jangan meminta persetujuan yang sama dua kali.

| ID | Keputusan/bukti yang diperlukan | Penanggung jawab peran | Diselesaikan pada / sebelum | Status awal |
|---|---|---|---|---|
| EXEC-01 | PIC/reviewer sementara, siapa boleh menerima hasil teknis dan siapa penerima gerbang; jangan mengarang tim | Pemilik proyek / PM | Sebelum WF-001; WF-002 memetakan penerima, WF-006 memformalkan tim | open |
| EXEC-02 | Tujuan remote/branch, identitas Git dan akses push. Remote yang terlihat saat review: origin ke ikhlaspp/WEBGIS-east-java-health-centers; branch lokal main. Observasi ini bukan penetapan tujuan push atau bukti autentikasi | Pemilik repo / OP | Sebelum penutupan Git WF-001 | open |
| OPEN-01 | Catat Supabase sebagai revisi MySQL sesuai arahan pengguna; tentukan hanya bila ada persyaratan tambahan dosen yang benar-benar belum diketahui | AN / penerima akademik | WF-001/004; sebelum WF-G1 jika memengaruhi mandat | open untuk persyaratan akademik tambahan |
| OPEN-02 | Edisi kode/polygon, lisensi, cakupan pulau dan crosswalk historis | DG / pemilik kebutuhan | WF-018/019; sebelum WF-G2 dan desain adapter | open |
| OPEN-03 | Tahun observasi, unit, sumber penduduk/luas, kebijakan data campuran | DG / pemilik kebutuhan | WF-019/020; sebelum WF-G2 | open |
| OPEN-04 | Provider geocoding yang mengizinkan batch, batas penggunaan/biaya, standar bukti lokasi facility | DG / pemilik akun | Kelayakan/anggaran WF-007/018, keputusan sebelum WF-G2; detail prosedur WF-039 sebelum WF-G3 | open |
| OPEN-05 | Cakupan penuh atau parsial, batas kelengkapan, label dan kondisi blokir publikasi | DG / penerima penelitian | WF-020/023; sebelum WF-G2 | open |
| OPEN-06 | Kapasitas tim, anggaran, tanggal penyerahan, hosting dan pemilik layanan | PM / pemilik proyek | WF-006/007/008; sebelum WF-G1 | open |
| OPEN-07 | Pilih/tunda empat P1 satu per satu dan pastikan prasyarat fitur terpilih tetap tersedia | AN / pemilik kebutuhan | WF-014/028; sebelum WF-G2 | open |
| EXEC-03 | Versi runtime/lockfile, modul final, runner dan working directory, fixture, metode spasial/toleransi, izin DB dan identitas operator CLI | BE / DG / QA | WF-030/031/035/036/042/049/050; diperiksa WF-052 sebelum WF-G3 | open |
| EXEC-04 | Akun serta environment dev/test PostgreSQL/PostGIS, Colab dan storage; akses produksi terpisah | OP / pemilik akun | Kebutuhan WF-007, desain WF-030; akses Colab sebelum WF-055 dan DB test sebelum WF-056; produksi sebelum WF-129/130 | open |
| EXEC-05 | Peserta, jadwal, instrumen dan penerima UAT nyata | QA / pemilik kebutuhan | Target WF-027; peserta aktual WF-125 sebelum WF-126 | open |
| EXEC-06 | Target deploy, domain bila perlu, operator, akses, jendela rilis dan titik pemulihan | OP / pemilik layanan | WF-129–131 sebelum pemasangan WF-132 | open |
| EXEC-07 | Penerima akses, bukti akses berfungsi, masa dukungan dan owner insiden | PM / penerima operasi | WF-149/150/152; sebelum WF-G7 | open |
| EXEC-08 | Akhir periode dukungan nyata, kewajiban/insiden selesai atau dialihkan, penerimaan penutupan | PM / penerima proyek | WF-160 sebelum WF-G8 | open |

Untuk EXEC-04, WF-056 boleh memakai database PostgreSQL/PostGIS test sementara yang terisolasi sesuai WF-030; WF-072 kemudian memverifikasi provisioning dev/test final. Jangan menunggu WF-072 untuk memenuhi kebutuhan DB test CI WF-056, dan jangan memakai produksi sebagai jalan pintas.

## Format pencatatan keputusan

Simpan pada artefak tiket penghasil keputusan: ID, status `open`/`resolved`/`blocked`/`not_applicable`, nilai final, alasan, owner bernama, sumber arahan/bukti, tanggal aktual, daftar tiket terdampak, dan tindakan berikutnya. `not_applicable` membutuhkan alasan; bukan cara melewati P0. Tautkan artefak itu di handoff konsumen. Perubahan keputusan setelah baseline mengikuti change request yang sudah ditetapkan.

Rujukan: [keputusan awal](../07-sumber-dan-keputusan.md), [indeks tiket](Tiket/README.md), [panduan eksekusi](panduan-eksekusi.md).
