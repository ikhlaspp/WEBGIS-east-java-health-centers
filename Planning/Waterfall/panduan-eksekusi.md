# Panduan eksekusi satu tiket

Paket ini tetap memiliki 160 tiket. Handoff, batch dan checkpoint adalah bagian tiket yang sama. Penyempurnaan instruksi tidak memulai tugas, menerima gerbang, atau membuat aplikasi.

## Sebelum mengerjakan

1. Baca tiket, hasil pendahulu, keputusan scope, dan [register prasyarat](prasyarat-eksekusi.md). Jangan memuat seluruh 160 tiket ke setiap sesi; baca tambahan hanya jika dibutuhkan dependensi.
2. Pastikan status pendahulu, gerbang dan pengiriman Git memenuhi aturan [indeks](Tiket/README.md). P1 deferred menggunakan bukti keputusan, bukan file implementasi yang memang tidak dibuat.
3. Buat `docs/pekerjaan/WF-xxx/handoff.md` dari template di bawah pada awal pelaksanaan. Salin path input lengkap dari handoff tiket, lalu verifikasi versi/hash dan penerimaannya. Target yang belum dibuat oleh pendahulu merupakan penghalang, bukan izin untuk mengarang isi.
4. Untuk kode, resolusikan target usulan ke file yang disahkan WF-031/WF-G3. Inspeksi kode yang sudah ada sebelum memilih nama baru. Catat kontrak input/output, tipe/error, fixture acuan dan command konkret. File/direktori pada handoff adalah rencana; jangan menganggap `php artisan`, pytest atau Playwright sudah terpasang saat ini.
5. Jalankan satu tiket aktif. Keputusan teknis rutin boleh mengikuti desain diterima; keputusan scope, biaya, sumber, penerimaan atau akses yang belum tersedia dicatat dengan owner. Konfirmasi yang sudah ada tetap berlaku dan tidak ditanyakan ulang. Review teknis oleh agen tidak sama dengan persetujuan dosen/penerima atau hasil UAT manusia.

## Template handoff aktual

```markdown
# Handoff WF-xxx
Status kesiapan: pending / ready / blocked
Revision awal dan kondisi working tree:
Input: path aktual, tiket asal, versi/hash, bukti penerimaan
Prasyarat: ID keputusan, nilai yang dipakai, sumber keputusan
Scope: perilaku yang harus berubah dan batas tiket
File aktual: path + perubahan yang direncanakan; pemetaan dari target usulan
Kontrak: input/output, tipe, error, izin, rilis/run, unit/toleransi jika berlaku
Fixture: path, kasus normal/negatif, expected result independen
Verifikasi: working directory, command lengkap, environment test, expected exit/result
Checkpoint: daftar bagian, bukti yang harus disimpan, langkah berikutnya
Review: pemeriksa teknis dan penerima eksternal bila memang diperlukan
Penghalang: masalah, owner, tiket terdampak, tindakan berikutnya
```

Isi kolom dengan fakta aktual ketika tiket dijalankan. `ready` adalah kesiapan bekerja, bukan `done` atau persetujuan gerbang. Jangan menyalin placeholder sebagai nilai final. Perintah contoh baru boleh digunakan setelah file/runner dibuat dan dikonfigurasi. Test harus menemukan kasus yang dimaksud; suite kosong, assertion dimatikan, atau SQLite untuk bukti PostGIS tidak memenuhi penerimaan. Periksa output aktual bersama exit code.

## Checkpoint dan melanjutkan sesi

Simpan `checkpoint.json` setelah bagian bermakna selesai atau sebelum sesi berakhir. Struktur contoh ini masih template, bukan catatan eksekusi:

```json
{
  "ticket_id": "WF-xxx",
  "input_hashes": {},
  "code_revision": null,
  "working_tree_paths": [],
  "completed": [],
  "pending": [],
  "blocked": [],
  "evidence_paths": [],
  "checks": [],
  "next_action": null
}
```

`checks` memuat command/langkah aktual, environment, expected, actual, exit code bila ada, dan path log. Untuk batch lokasi, ketiga daftar berisi kode fasilitas, `blocked` juga menyimpan alasan/owner dalam hasil review. Daftar saling terpisah dan jumlahnya direkonsiliasi dengan manifest antrean awal. Update file secara atomik (file sementara lalu replace); jangan mengosongkan hasil lama sebelum hasil baru tersimpan.

Saat melanjutkan, baca status tiket, handoff, checkpoint dan diff. Cocokkan input/revision dan perubahan belum dikomit. Bila input berubah, tentukan bagian terdampak dan ulang hanya verifikasi yang relevan. Jangan menganggap checkpoint lama tetap valid untuk rilis/input baru.

WF-068/069/070 menggunakan maksimal 25 fasilitas per checkpoint dalam satu kabupaten. WF-086 memakai enam checkpoint pada tiketnya. WF-101/102/103 dan WF-127 menyimpan progres per alur/suite/defect; satu penghalang tetap dilaporkan tanpa menghapus bukti bagian yang lulus. WF-153–156 tetap mengikuti siklus insiden, bukan dipaksa menjadi satu batch serial sampai masa dukungan berakhir.

Checkpoint tidak wajib membuat commit tersendiri. Penutupan tiket tetap memakai kebijakan commit/push yang sudah ada; jangan maju antrean hanya karena satu checkpoint selesai. Catat perubahan tanpa commit pada checkpoint agar sesi berikutnya dapat meneruskan dengan aman.

## Penutupan

- Hasil implementasi aktual tersedia, bukan hanya laporan yang menyatakan telah dibuat.
- Pemeriksaan relevan memiliki expected/actual serta revision/input yang sama dengan hasil akhir.
- Setiap persetujuan eksternal, UAT, serah akses dan interval dukungan didukung peristiwa nyata. Jika belum tersedia, simpan pekerjaan yang sudah selesai dan catat penghalang yang tepat.
- Perbarui status/log tiket, lalu jalankan penutupan Git sesuai tujuan yang ditetapkan. Katalog JSON menyimpan rencana awal; status live tetap di file tiket dan bukti pengiriman terpisah.

## Memelihara paket

Perubahan instruksi harus konsisten antara file tiket, `daftar-tiket.json`, dan sumber generator di `bahan-tiket/`. Handoff dirender dari `execution_readiness.py`. Jangan menjalankan generator untuk menimpa tiket aktif. Jalankan `python -B Planning/Waterfall/bahan-tiket/validasi_tiket.py` dari root workspace setelah perubahan. Validasi dokumen tidak menggantikan pengujian aplikasi atau penerimaan gerbang.
