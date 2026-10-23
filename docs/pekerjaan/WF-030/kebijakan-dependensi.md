# Dependency dan kompatibilitas

Versi 1 · 23 Oktober 2026 · Penyusun: Codex.

Composer memakai composer.json/composer.lock; npm package.json/package-lock.json dan npm ci; Python pyproject.toml + requirements.lock berhash, generated dari resolver pada WF-055. Kunci seluruh transitive dependency dan versi native/geospatial; jangan menyebut lock tersedia sebelum dibuat. Paket utama: pandas, GeoPandas, Shapely, pyproj, Folium, geopy, psycopg dan pytest. Leaflet stable 1.9.4 menjadi target awal berdasar [referensi](https://leafletjs.com/reference.html); plugin cluster dipilih versi compatible dan diuji, bukan alpha.

Modul Python dikemas sebagai `gis_pipeline`; notebook menginstal wheel dari code_revision yang sama, bukan menyalin rumus ke cell. Manifest mencatat Python/OS, PHP, Node, PostgreSQL, PostGIS, PROJ, GEOS dan hashes lockfile. Lock Windows dan Linux/Colab dapat berbeda artefak binary tetapi harus menghasilkan versi metode dan hasil ekuivalen yang diuji. Pin image digest saat implementasi, bukan mengarang digest sekarang.

Smoke matrix WF-054/055/056: composer install + platform check; npm ci/build; Python locked install/import; query PostGIS_Full_Version dan buffer fixture; php artisan migrate/test pada DB test; notebook fixture dari environment baru. Semua command dijalankan dari root repo kecuali wheel/venv activation yang dinyatakan. Uji dependency gagal menghentikan build; tidak resolve paket latest diam-diam di notebook.

Upgrade dependency melalui perubahan terpisah dengan release notes, install dari lock, unit/integrasi sesuai modul serta golden formula/spasial. Kerentanan dependency dibahas berdasar paparan aktual; jangan membuang lock agar install berhasil. Output besar, venv, node_modules, vendor, cache, dumps dan .env diignore saat proyek dibuat; Planning tetap ignored sesuai pengguna.
