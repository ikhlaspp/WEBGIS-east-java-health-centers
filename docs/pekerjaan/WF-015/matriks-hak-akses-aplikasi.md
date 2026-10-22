# Hak akses aplikasi

Versi 1 · 23 Oktober 2026 · Penyusun: Codex. Role aplikasi hanya guest dan admin; bukan role pengelola data terpisah. Ini kontrak perilaku, belum bukti izin database terpasang.

| Operasi | Guest | Admin | Kanal dan pembatasan |
|---|---|---|---|
| Beranda/peta/tabel/detail/metode | Boleh rilis publik | Boleh rilis publik | GET; release_id dipatok per tampilan |
| Daftar rilis/wilayah/sumber/statistik/GeoJSON | Boleh rilis publik | Boleh rilis publik | API baca Laravel; draft tidak muncul |
| Membaca kode/rilis draft melalui URL publik | Tidak | Tidak melalui endpoint publik | 404 tanpa membocorkan keberadaan objek |
| Login | Boleh mencoba akun yang telah disediakan | Boleh | GET form; POST dengan CSRF dan throttling; tanpa registrasi |
| Logout | Tidak ada sesi untuk diakhiri | Boleh sesi sendiri | POST CSRF; invalidate sesi dan token terkait |
| Akuisisi/impor staging | Tidak | Boleh jika operator diberi izin | Command P0; validate file, sumber, hash, actor; bukan endpoint GET |
| Review mapping/lokasi | Tidak | Boleh | Alasan, bukti, reviewer, tanggal; perubahan membuat kandidat baru |
| Menjalankan analisis | Tidak | Boleh | Parameter allowlist, input snapshot, job/run audit; tidak publish otomatis |
| Publish/rollback | Tidak | Boleh dengan otorisasi khusus operasi | Command P0; transaksi/lock; audit dan rilis immutable |
| Mengubah data published langsung | Tidak | Tidak | Buat kandidat baru; rollback pointer tidak mengedit sejarah |
| Membaca audit/masalah internal | Tidak | Boleh sebatas kebutuhan operasi | Log tersanitasi; bukan API publik |
| Dashboard/review UI | Tidak | P1 jika dipilih | Menggunakan kebijakan backend yang sama |
| CSV publik | P1 rilis publik saja | Sama | Tidak membuka staging; formula-safe |
| Membuat akun admin | Tidak | Hanya operator provisioning yang ditetapkan | Tidak ada self-registration atau UI manajemen akun baru dalam scope |

Sesi: regenerate ID setelah login; cookie secure pada HTTPS, HttpOnly dan SameSite=Lax; idle timeout kandidat 30 menit, maksimum 8 jam. Login gagal generik; kandidat throttle 5 kegagalan/menit per identitas dan IP, respons 429 tanpa mengungkap akun valid. Nilai konfigurasi dibekukan di desain dan diuji sebelum rilis. Logout menginvalidasi sesi server; sesi kedaluwarsa tidak meneruskan aksi tulis setelah login ulang tanpa konfirmasi ulang.

Halaman admin tanpa sesi mengarah ke login. API terproteksi tanpa sesi 401; terautentikasi tanpa hak 403; objek unpublished via API publik 404. CSRF gagal pada web mengikuti respons framework (419 bila Laravel default); payload salah 422; format tidak dikenal 400. Jangan menyamakan semua kegagalan menjadi HTTP 200.

## Identitas teknis terpisah

Browser/guest/admin tidak memegang credential DB. Laravel memakai runtime non-owner dengan baca rilis terbit; worker boleh staging dan hasil kandidat, tidak boleh publish; publisher terbatas transisi rilis; migration role untuk DDL pada deployment terkontrol. Admin CLI harus dipetakan ke actor admin aktif, menolak actor kosong/tidak sah, dan memanggil service yang menguji izin. Pemisahan koneksi tidak menghapus kebutuhan otorisasi aplikasi.

Tidak ada Supabase Auth wajib. Data API anon/authenticated tidak boleh membaca schema privat; desain dapat menonaktifkan exposure atau memakai grants/RLS yang dibuktikan sebagai role nyata. Uji owner/postgres saja tidak cukup. Bukti penerimaan: matriks allow/deny, uji guest/draft/CSRF/expiry, actor CLI palsu dan publish bersaing; lihat WF-027.
