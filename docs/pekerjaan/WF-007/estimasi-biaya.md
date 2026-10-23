> Current baseline: accepted under [WF-G1](../WF-012/penerimaan-WF-G1.md) and [the college-project supplement](../WF-012/revisi-tugas-kuliah-untuk-persetujuan.md). The user is owner/approver; use free services and milestone-only scheduling. Earlier pending capacity, budget, and calendar statements below are historical assumptions superseded by that decision. No lecturer approval or team-hours commitment is implied.

# Opsi biaya dan batas penggunaan

Versi kandidat 1, pemeriksaan sumber resmi 23 Oktober 2026. Mata uang USD, belum termasuk pajak/kurs, kelebihan kuota, domain, geocoding, backup eksternal atau tenaga kerja. Tidak ada pembelian; budget pengguna belum diketahui.

| Komponen | Harga/ketentuan yang diperiksa | Implikasi |
|---|---|---|
| Supabase Free | USD0/bulan; DB 500 MB, storage 1 GB, 2 project aktif; pause setelah 1 minggu tidak aktif; automatic backup tidak termasuk | Kandidat dev/prototipe bila ukuran dan isolasi cukup; wajib backup sendiri |
| Supabase Pro | Mulai USD25/bulan, project pertama termasuk; project tambahan mulai USD10/bulan; daily backup 7 hari | Kandidat produksi; ukuran/egress dan compute tambahan tetap dihitung |
| VPS DigitalOcean Basic | 1 GiB USD6/bulan; 2 GiB USD12/bulan pada tabel resmi | Contoh pembanding hosting PHP; kecukupan beban belum diuji, bukan pemilihan vendor final |
| Colab Free | Tersedia gratis; kapasitas/masa runtime berubah dan tidak dijamin | Kandidat penelitian; simpan output dan checkpoint, jangan jadikan hosting Laravel |

Sumber: [Supabase pricing](https://supabase.com/pricing), [DigitalOcean Droplets](https://www.digitalocean.com/pricing/droplets), [Colab FAQ](https://research.google.com/colaboratory/faq.html). Kutipan angka adalah penawaran saat akses, bukan invoice atau kontrak. Verifikasi lagi sebelum pemesanan.

## Skenario

- **A, tanpa belanja baru untuk persiapan:** manfaatkan mesin dan koneksi yang sudah tersedia, kandidat Supabase Free dan Colab Free. Tambahan biaya layanan awal dapat USD0 selama kuota cukup. Produksi publik, backup eksternal, geocoding dan biaya internet/listrik tidak dijamin gratis. Skenario ini tidak menghapus kewajiban deployment P0; bila belum ada hosting yang memenuhi, rilis publik tetap menunggu keputusan.
- **B, kandidat produksi kecil:** satu Supabase Pro USD25 + VPS 2 GiB USD12 = **USD37/bulan** sebelum tambahan. Dua bulan = USD74 untuk dua komponen itu saja. Dev/test memakai lokal terisolasi; jika memerlukan satu project Supabase berbayar tambahan, subtotal menjadi sedikitnya USD47/bulan. Performa belum dijamin.
- **C, layanan sudah dimiliki pengguna:** gunakan biaya incremental nyata dari akun existing setelah kapasitas, izin dan isolasi diverifikasi. Tidak mengasumsikan akun tersedia hanya karena folder Laragon ada.

Biaya total = bulan aktif × (DB + hosting + storage/backup + tile) + domain + query unik geocoder × tarif + biaya lain yang disepakati. Parameter yang belum dipilih tetap unknown, bukan nol. Upah kerja tidak diasumsikan; effort manusia dilaporkan terpisah di WF-008.

## Geocoding tile dan cadangan

Provider geocoding masih terbuka; tidak ada kuota gratis yang diasumsikan menutup 408 pencarian. Opsi utama adalah koordinat resmi dan provider yang mengizinkan batch/cache. Nominatim publik bukan default: [kebijakan resminya](https://operations.osmfoundation.org/policies/nominatim/) membatasi maksimum 1 request/detik, satu thread/mesin untuk batch kecil, cache, identitas klien dan atribusi; pekerjaan reguler/lebih dari sehari dibatasi 4 request/menit. Bulk besar tidak dianjurkan dan pemakaian harus dipilih secara sadar. Tidak menjalankan query dalam fase ini.

[Tile OSM](https://operations.osmfoundation.org/policies/tiles/) memerlukan atribusi, identitas/referrer, caching dan melarang bulk/prefetch. Layanan best-effort bukan SLA produksi. Cadangan: provider tile berizin atau demo memakai tabel/artefak yang sudah dibuat; jangan mengunduh tile publik massal.

Owner keputusan anggaran adalah pengguna/pemilik proyek. Pilih batas biaya sebelum WF-G1; geocoder/edisi sumber final diputuskan paling lambat WF-G2. Sampai disetujui, seluruh opsi adalah kandidat tanpa komitmen pengeluaran.
