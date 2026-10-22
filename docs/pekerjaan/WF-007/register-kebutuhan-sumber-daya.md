# Register alat layanan dan lingkungan

Versi 1, 23 Oktober 2026. Pemeriksaan lokal bersifat read-only. Akun layanan tidak dibuat, kredensial tidak dicari atau disalin. Owner layanan belum ditunjuk; OP adalah peran tindak lanjut.

| Item | Bukti/status aktual | Kebutuhan dan tindakan | Owner / batas |
|---|---|---|---|
| PHP/Laragon | `php -v`: 8.4.22; `php -m`: PDO dan pdo_mysql tersedia, pdo_pgsql/pgsql tidak muncul | Aktifkan driver PostgreSQL dan verifikasi koneksi sebelum backend DB | BE/OP; WF-054/072 |
| Composer | `composer --version`: 2.4.1; warning deprecated E_STRICT pada PHP yang tersedia | Evaluasi pembaruan sesuai toolchain pada WF-054, bukan memasang dependency sekarang | BE |
| Node/npm | Node v24.14.1; npm 11.11.0 | Validasi kompatibilitas Vite/lockfile saat setup | FE; WF-054 |
| Python | Python 3.10.6 pada PATH | Rencana memakai 3.12; pilih environment terisolasi/versi kompatibel saat WF-030/055 | DG |
| PostgreSQL/PostGIS lokal | psql tidak ditemukan pada PATH; bukan bukti server tidak ada di mesin | Sediakan DB test terisolasi sebelum CI; provisioning final dev/test WF-072 | BE/OP |
| Git/GitHub | main melacak origin/main; remote HEAD terverifikasi pada 63b9e812fa0aca5eeccfc796aa3c24a3c86f0c6c saat cek | Gunakan identitas pengguna; akses baca terbukti, akses push belum dibuktikan | Pemilik repo/OP |
| Arsip/planning | Proposal, tujuh dokumen dan WBS terbaca; 49 berkas pada audit awal | Pertahankan sumber asli dan hash; staging bukan data final | DG |
| Master kode/polygon | Belum ada dataset resmi final dalam arsip menurut audit | Pilih edisi/lisensi, unduh dan verifikasi pada fase kebutuhan/data | DG; WF-018/019/059 |
| Supabase | Kepemilikan project/region/kuota belum diperiksa | Dev/test/prod terisolasi; SSL dan akun minimum; free bukan jaminan kapasitas polygon | Pemilik akun/BE |
| Colab | Akun/runtime belum diuji | Run all bersih dengan dependency terkunci; tanpa secret produksi | DG; WF-055/123 |
| Hosting PHP/HTTPS | Belum dipilih | Mendukung public root, worker/cron, HTTPS dan koneksi PostgreSQL; Colab bukan host aplikasi | OP; desain WF-030 |
| Geocoding | Provider belum diputuskan | Prioritaskan koordinat resmi dan provider batch berizin; bukti facility tetap wajib | DG; WF-G2 |
| Tile | Provider produksi belum dipilih | Atribusi/cache, fallback tabel dan kemampuan mengganti provider | FE/OP; WF-022/030 |
| Backup/artefak | Lokasi eksternal dan retensi belum dipilih | Backup DB serta raw/HTML/GeoJSON terpisah; restore nyata sebelum rilis | OP; WF-026/122 |
| CI/browser/load test | Aplikasi dan pipeline belum tersedia | PostgreSQL/PostGIS test, pytest, backend runner dan Playwright; mock layanan eksternal | QA; WF-056 |
| UAT | Tidak ada peserta/jadwal terkonfirmasi | Rekrut nyata sesuai baseline WF-G2; tidak menggantikan peserta dengan agen | QA; WF-125 |

Bukti command lengkap dan waktu tersedia pada `pemeriksaan-lingkungan.json`. Kegagalan Git sandbox `SEC_E_NO_CREDENTIALS` tidak dianggap kegagalan remote: pengulangan read-only di luar sandbox berhasil setelah izin diberikan. Tidak ada perubahan konfigurasi mesin dalam WF-007 ini.
