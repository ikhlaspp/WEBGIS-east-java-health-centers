# Matriks penerima gerbang

Versi 1, 23 Oktober 2026. Seluruh penerima di bawah adalah peran yang perlu dipetakan ke orang berwenang. Belum ada gerbang accepted.

| Gerbang | Paket yang diterima | Reviewer teknis yang dibutuhkan | Penerima keputusan |
|---|---|---|---|
| WF-G1 | Charter, WBS, penugasan, estimasi dan kendali | PM/AN dan pemeriksa konsistensi dokumen | Pemilik proyek, nama/mandat menunggu konfirmasi |
| WF-G2 | SRS, sumber/periode, cakupan, P1 dan target uji | AN/DG/BE/QA | Pemilik kebutuhan; penilai akademik bila ditunjuk |
| WF-G3 | Desain schema/API/metode/UI/test | BE/DG/FE/QA, reviewer selain pembuat bila tersedia | Pemilik proyek/penerima desain yang ditunjuk |
| WF-G4 | Kandidat kode/data/run dan smoke | QA/DG/BE | Pemilik proyek/penerima kandidat uji |
| WF-G5 | Hasil uji aktual, UAT, defect/retest | QA dan reviewer data/keamanan | Pemilik proyek; penerima UAT yang ditunjuk |
| WF-G6 | Produksi, smoke, backup, akses | OP/QA | Pemilik layanan produksi |
| WF-G7 | Paket, akses berfungsi, dukungan | OP/QA/PM | Penerima operasi dan hasil akademik sesuai mandat |
| WF-G8 | Kewajiban dukungan, arsip, transisi | PM/OP | Penerima operasi/pemilik proyek |

Satu orang boleh merangkap beberapa peran dengan catatan eksplisit. Pemeriksaan Codex dicatat sebagai self-review teknis, tidak sebagai reviewer manusia independen. Untuk menerima gerbang, catat nama, waktu, keputusan, versi/hash paket, dan sumber persetujuan. Bila penerima menolak, status rework dan daftar koreksi menahan fase berikutnya. Bila belum menjawab, status pending; jangan mengarang accepted atau rework.
