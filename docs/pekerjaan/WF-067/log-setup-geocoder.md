# Setup antrean dan bukti geocoding

Tanggal 2026-10-25; versi location-queue-1.0. Pelaksana/review teknis mandiri Codex berdasarkan instruksi pemilik untuk meneruskan implementasi mandiri. Ini bukan review lapangan atau penerimaan independen.

## Antrean aktual

Master WF-064 dipatok hash dan keluaran geometri WF-066 diperiksa hash/ukuran sebelum antrean dibuat. data/staging/location_queue.json menyimpan 973 kode fasilitas unik, alamat lengkap, kode kecamatan/parent, query lengkap, kandidat per sumber, status snapshot, status kerja dan wadah keputusan. Hash publik terdapat dalam antrean-review-lokasi.json; respons dan antrean rinci tetap lokal.

Baseline CSV tetap 565 kandidat dan 408 missing. Tiga fasilitas mempunyai kandidat tambahan dari XLSX sehingga 405 tidak memiliki kandidat dari sumber mana pun. Total 1133 record kandidat (565 CSV + 568 XLSX) tetap ditautkan sumber masing-masing; koordinat sama tidak menghapus fasilitas atau audit sumber. Timestamp dan precision historis tidak diketahui, disimpan null/unknown dengan alasan. Semua 973 masih tidak verified dan tidak eligible radius.

## Pemilihan provider terbatas

OPEN-04 sebelumnya belum dipilih. Untuk setup ini dipilih Photon/komoot dalam lingkup uji kecil satu kali tanpa biaya/akun. Keputusan teknis oleh Codex memakai kewenangan implementasi mandiri pengguna; bukan klaim pemilik menyetujui kontrak berbayar. README resmi https://github.com/komoot/photon#demo-server mengizinkan proyek dengan jumlah request wajar, dapat membatasi penggunaan berlebihan, dan tidak menjamin availability. Interpretasi konservatif untuk setup: satu query aktual, satu mesin/thread, interval dua detik, cache privat, maksimal 25 query unik kumulatif untuk konfigurasi trial. Ini tidak memberi izin untuk seluruh 973 pencarian atau batch rutin. Skala lanjutan memerlukan pemilihan deployment/provider yang sesuai. OSM attribution/ODbL disimpan; lisensi kode Photon berbeda dari lisensi data OSM.

Konfigurasi dapat diganti tanpa mengubah kode. Adapter Photon tersedia bersama adapter Nominatim untuk deployment berizin yang dipilih secara eksplisit. Endpoint Nominatim publik tidak diaktifkan. Kebijakan publik: https://operations.osmfoundation.org/policies/nominatim/. API Photon: https://github.com/komoot/photon/blob/master/docs/api-v1.md.

Trial kode 35010200001 menggunakan query nama/alamat/kecamatan/kabupaten/provinsi/Indonesia. Respons asli 42 byte, no_match, tersimpan privat dan ber-hash. Ulang langsung melalui adapter menghasilkan cache_hit=true. Tidak ada titik diimputasi dari centroid. Bukti: provider-smoke.json. Cakupan trial dapat dinilai tanpa menganggap no_match sebagai ketiadaan fasilitas.

## Operasi dan review

```text
.venv/Scripts/python.exe scripts/etl/geocode.py init --facility-evidence docs/pekerjaan/WF-064/output-verification.json --boundary-manifest docs/pekerjaan/WF-066/manifest-geometri.json --release-id draft-historical-2024 --report docs/pekerjaan/WF-067/antrean-review-lokasi.json
.venv/Scripts/python.exe scripts/etl/geocode.py search --provider-config docs/pekerjaan/WF-067/provider-trial.json --codes 35010200001 --checkpoint data/staging/geocoder-setup-trial.json
.venv/Scripts/python.exe scripts/etl/geocode.py review --candidate-file data/staging/candidate.json --decision-file data/staging/decision.json --output data/staging/reviewed-decision.json
```

Dua perintah pertama dijalankan exit 0. Perintah review merupakan contoh pengisian; belum ada keputusan lokasi aktual. Form review memakai field template-review.json: salin identity dan koordinat persis dari kandidat, isi precision, centroid, evidence, reviewer, tanggal timezone dan alasan. Accepted membutuhkan facility point bukan centroid serta evidence URL HTTPS atau note+SHA256. Validasi struktur tidak membuktikan isi bukti benar. Snapshot/eligibility tidak diubah oleh perintah review; import transaksi dan spatial checks tetap tahap berikutnya. Riwayat kandidat/keputusan tidak ditimpa.

Search menerima 1-25 kode eksplisit berurutan deterministik, checkpoint input-queue/config hash sebelum dan sesudah tiap kode, partition completed/blocked/pending, single-writer lock, artifact checksum saat resume, penghentian saat error, retry/cache HTTP terbatas dari modul bersama. Trial ceiling dicatat lintas pemanggilan; tidak ada loop seluruh antrean. Raw query/response/time/object/precision terikat per kode; hasil POI belum otomatis facility precision.

## Verifikasi

30 tes khusus lulus: 565/408 semantics sintetis, kandidat XLSX tambahan, identitas duplikat, koordinat invalid, konfigurasi provider eksplisit, pembatasan endpoint, query/cache receipt, POI/centroid tidak auto-accept, review source/release/code/point mismatch, evidence wajib, resume tanpa pengulangan dan penolakan output checkpoint yang berubah. Suite penuh 215 tes lulus; compileall exit 0. Ulang init mempertahankan artefak yang identik; output berbeda ditolak agar review tidak tertimpa.

Tahap setup antrean selesai. Review 565 titik lama dan pencarian 408 baseline missing belum dilakukan pada tiket ini. Provider trial tidak menjamin coverage dan tidak menggantikan bukti lokasi. Publikasi tetap false.
