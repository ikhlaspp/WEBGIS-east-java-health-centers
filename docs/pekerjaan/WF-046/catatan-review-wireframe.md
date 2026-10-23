# Walkthrough wireframe

Versi 1 · 23 Oktober 2026 · Reviewer mandiri: Codex. Tidak ada sesi review stakeholder atau usability test yang diklaim.

| Skenario | Jalur desktop/mobile | Hasil desain / penyesuaian |
|---|---|---|
| UC-01 cari fasilitas missing | Header→tabel/search→Detail | Jalur tidak bergantung marker; tombol fokus hanya bila point ada |
| UC-02 bandingkan kecamatan | Selector/detail A dan B pinned release | Tahun tepat di nilai dan nav mempertahankan release; tanpa compare UI baru |
| UC-03 radius3km | Layer/radius→legend→partial information | Info x/y di banner, bukan hanya popup tersembunyi |
| UC-04 sumber | Detail source link→method table/locator | Selalu tap/keyboard, bukan hover-only |
| UC-05 filter bertingkat | Panel→parent→child→apply | Mobile dialog close+focus return; selected parent resets child |
| UC-06 tile/API failure | Banner+retry, daftar/tabel | Tile failure tidak memblokir table; API failure tidak menjadi empty sukses |

Temuan ditangani pada wireframe: popup mobile dibatasi tinggi; legenda teks dapat dibuka; data missing tetap tabel; detail mengikat periode; panel tidak menutup seluruh viewport permanen. Bukti aktual hanya walkthrough dokumen, belum screenshot aplikasi. Review visual pengguna dan keyboard/device tests dilakukan WF-119/126; penerima dapat meminta perubahan lewat catatan versi, bukan dianggap sudah menyetujui sketsa ini.
