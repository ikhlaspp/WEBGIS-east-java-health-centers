"""Build reproducible phase-one estimates/manifests; never approve tickets."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'docs/pekerjaan'
catalog = json.loads((ROOT / 'Planning/Waterfall/Tiket/daftar-tiket.json').read_text(encoding='utf-8'))
tickets = catalog['tickets']

def write(relative, text):
    path = BASE / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + '\n', encoding='utf-8')

def dump(relative, value):
    write(relative, json.dumps(value, ensure_ascii=False, indent=2))

# Engineering estimates, not measured throughput or actual time spent.
work = (
    [4,2,3,4,3,3,3,5,3,3,3,3]
    + [4,5,3,4,6,8,4,5,5,4,5,3,3,4,5,4]
    + [5,4,6,5,8,6,5,8,8,8,6,6,6,8,5,5,5,5,5,4,8,6,5,6]
    + [3,5,5,8,12,16,12,8,6,16,20,10,12,12,6,565*5/60,408*12/60,16,5,
       6,14,10,16,6,10,8,10,14,8,8,10,12,10,24,8,10,8,12,10,6,6,10,8,6,
       12,16,6,10,16,20,16,6]
    + [6,6,8,6,8,8,12,10,6,10,10,8,6,6,8,8,8,8,8,5,4,8,16,6]
    + [6,5,5,4,4,4,4,6,4,4,6,3]
    + [6,8,8,8,16,12,8,6,4,4,4,3]
    + [6,4,12,6,4,4,4,3]
)
assert len(work) == 160, len(work)
rows = []
for t, hours in zip(tickets, work):
    review = round(max(.5, hours * .25), 2)
    rework = round(hours * .15, 2)
    base = round(hours + review + rework, 2)
    rows.append(dict(id=t['id'], phase=t['phase'], priority=t['priority'],
                     title=t['title'], work=round(hours,2), review=review,
                     rework=rework, base=base, contingency=round(base*.20,2)))
dump('WF-008/estimasi.json', {'version':1, 'date':'2026-10-23',
    'unit':'person_hours', 'basis':'unmeasured planning estimates', 'tickets':rows})
header = '''# Estimasi usaha per tiket

Versi 1 — 23 Oktober 2026. Estimasi engineering awal, belum disepakati tim dan bukan realisasi. Satuan jam orang. Waktu mesin/AI tidak otomatis sama dengan jam orang. Angka bergantung pada langkah, kompleksitas integrasi dan volume data; kalibrasi ulang setelah pilot kurasi dan implementasi pertama.

Pelaksanaan berbeda per tiket. Review = 25% pelaksanaan (minimum 0,5 jam), perbaikan normal = 15%; cadangan risiko = 20% dari ketiganya dan ditampilkan terpisah. Angka persentase adalah asumsi perencanaan, bukan hasil pengukuran. Cadangan menutup ketidakpastian sumber/OCR/crosswalk/integrasi (R01–R14 pada WF-009), bukan izin mengurangi kualitas. Incident support adalah alokasi awal; lama masa dukungan belum disepakati.

WF-068: 565 kandidat × 5 menit = 47,08 jam pelaksanaan; sensitivitas 3–8 menit = 28,25–75,33 jam. WF-069: 408 lokasi × 12 menit = 81,60 jam; sensitivitas 8–20 menit = 54,40–136 jam. Kedua asumsi harus diuji pada batch maksimum 25 objek. WF-070 menyediakan 16 jam untuk anomali tersisa, tidak menggandakan review rutin; jika kasus melampaui alokasi, estimasi diperbarui. Kecepatan geocoder tidak membuktikan lokasi benar.

Waktu tunggu sumber, konfirmasi, provisioning, review dan dukungan dicatat terpisah pada jadwal. Biaya layanan ada di WF-007 dan tidak dijumlahkan dengan jam orang. Semua P0 termasuk backend validasi file dan command lifecycle; empat tiket P1 ditampilkan terpisah.

| Tiket | P | Pekerjaan | Pelaksanaan | Review | Perbaikan | Dasar | Cadangan |
|---|---|---|---:|---:|---:|---:|---:|
'''
for r in rows:
    header += f"| {r['id']} | {r['priority']} | {r['title']} | {r['work']:.2f} | {r['review']:.2f} | {r['rework']:.2f} | {r['base']:.2f} | {r['contingency']:.2f} |\n"
totals = {}
for label, subset in [('P0',[r for r in rows if r['priority']=='P0']),('P0+P1',rows)]:
    sums = {key:round(sum(r[key] for r in subset),2) for key in ['work','review','rework','base','contingency']}
    sums['total'] = round(sums['base'] + sums['contingency'],2)
    totals[label] = sums
header += '\n## Rekonsiliasi\n\n| Scope | Pelaksanaan | Review | Perbaikan | Dasar | Cadangan | Total |\n|---|---:|---:|---:|---:|---:|---:|\n'
for label, s in totals.items():
    header += '| ' + label + ' | ' + ' | '.join(f'{s[k]:.2f}' for k in ['work','review','rework','base','contingency','total']) + ' |\n'
header += '\nP0 berisi 156 tiket. Empat P1 hanya boleh deferred melalui keputusan scope; tambahkan administrasi keputusan 0,25 jam per tiket (1 jam) pada skenario P0, di luar total tabel. Data terstruktur: `estimasi.json`; rumus pembentukan: `../susun-bukti-inisiasi.py`.\n'
write('WF-008/estimasi-usaha-per-tiket.md', header)
schedule = '''# Jadwal baseline kandidat

Versi 1 — 23 Oktober 2026. Belum menjadi kalender baseline yang diterima: kapasitas aktual dan tenggat belum tersedia. Angka berikut batas kapasitas agregat, bukan janji durasi dan bukan asumsi tiga orang dapat bekerja serentak pada antrean serial.

| Scope | Usaha termasuk cadangan | 36 jam tim/minggu | 45 jam tim/minggu | Solo 15 jam/minggu |
|---|---:|---:|---:|---:|
'''
for label,s in totals.items():
    h = s['total'] + (1 if label=='P0' else 0)
    schedule += f'| {label} | {h:.2f} | {h/36:.1f} minggu minimum kapasitas | {h/45:.1f} minggu minimum kapasitas | {h/15:.1f} minggu minimum kapasitas |\n'
schedule += '''
Durasi nyata dibatasi ketersediaan PIC pada setiap tiket, antrean reviewer, dan waktu tunggu. Jika hanya satu PIC aktif 12 jam/minggu, gunakan usaha serial/12, bukan /36. Reviewer dapat berbeda, tetapi penutupan dan pengiriman predecessor tetap harus selesai. Perubahan ke pekerjaan paralel memerlukan keputusan kendali proses, bukan asumsi diam-diam pada perhitungan ini.

Milestone relatif: G1 setelah 001–012; G2 013–028; G3 029–052; G4 053–104; G5 105–128; G6 129–140; G7 141–152; G8 153–160 termasuk masa dukungan yang disepakati. Tidak ada tanggal kalender yang dikarang.

| Waktu tunggu | Pemilik tindak lanjut | Perlakuan jadwal |
|---|---|---|
| Jawaban tim, budget, tenggat, reviewer | Pemilik proyek | Durasi belum diketahui; menghalangi pembekuan baseline |
| Polygon/master resmi dan izin sumber | DG | Catat tanggal permintaan dan respons nyata di WF-018/059 |
| Geocoding/rate limit dan bukti lokasi | DG | Jangan anggap throughput maksimum sebagai hasil terverifikasi |
| Provisioning akun/hosting/DB | OP | Sebelum implementasi/deploy terkait |
| Review tiap gerbang dan UAT | PM/penerima | Jadwalkan setelah kandidat tersedia; belum ada SLA |
| Masa dukungan | PM/OP | Durasi kalender wajib disepakati sebelum G7 |

Untuk membekukan jadwal: konfirmasi PIC/jam/hari kerja, availability reviewer, tanggal mulai/tenggat dan P1; alokasikan pekerjaan/review sesuai kalender; tambahkan hanya waktu tunggu yang tidak overlap; periksa critical path dan kapasitas per orang; minta penerimaan versi tersebut. Estimasi delapan minggu/352 jam pada planning lama tidak digunakan sebagai komitmen.
'''
write('WF-008/jadwal-baseline.md',schedule)
critical = '''# Dependensi dan jalur kritis

Versi 1 — 23 Oktober 2026. Katalog 160 tiket adalah sumber dependensi. Dengan kebijakan finish-to-start utama, seluruh tiket scope terpilih membentuk rantai kritis urutan. Dependensi hasil menambah syarat masuk dan tidak memberikan izin melewati predecessor. Gerbang, review dan push menambah waktu tunggu yang belum terukur.

Tabel berikut adalah earliest start/finish dalam **jam usaha dasar serial**, tanpa cadangan/waktu tunggu. Ini koordinat usaha, bukan jam kalender. ES tiket pertama=0; EF=ES+pelaksanaan+review+perbaikan; ES berikut=EF sebelumnya. Untuk P0-only, hapus usaha WF-097–100 hanya setelah deferred resmi lalu sisipkan 1 jam keputusan. Kalender tetap menunggu kapasitas PIC.

| Tiket | Predecessor | Dependensi hasil | ES | EF |
|---|---|---|---:|---:|
'''
elapsed=0
for t,r in zip(tickets,rows):
    end=round(elapsed+r['base'],2)
    critical += f"| {t['id']} | {t['previous_ticket'] or '-'} | {', '.join(d['ticket'] + ':' + d['condition'] for d in t['dependencies']) or '-'} | {elapsed:.2f} | {end:.2f} |\n"
    elapsed=end
critical += '\nBottleneck utama: kurasi 973 lokasi, crosswalk/polygon, lifecycle publish/rollback, integrasi dan retest. Pilot 25 objek mengukur ulang throughput 068/069; ketidaktersediaan polygon tidak diselesaikan dengan geometri fiktif. Cadangan 20% usaha bukan pengganti lead time sumber atau masa dukungan.\n'
write('WF-008/catatan-jalur-kritis.md',critical)
names={'PM':'Ikhlas (usulan)','BE':'Ikhlas (usulan)','OP':'Ikhlas (usulan)',
       'AN':'Ayudya (usulan)','DG':'Ayudya (usulan)','FE':'Effandy (usulan)','QA':'Effandy (usulan)'}
assignment = '# Penugasan per tiket\n\nVersi 1 — 23 Oktober 2026. Semua nama merupakan usulan, belum persetujuan atau bukti kapasitas. Codex menyiapkan paket fase 1; penanggung jawab manusia dan reviewer tetap perlu konfirmasi. Untuk peran gabungan/penerima eksternal, nama belum ditetapkan. Bila PIC dan reviewer sama, tetapkan reviewer lain sebelum penerimaan.\n\n| Tiket | PIC peran | Nama usulan | Reviewer peran | Nama usulan |\n|---|---|---|---|---|\n'
for t in tickets:
    assignment += f"| {t['id']} | {t['owner_role']} | {names.get(t['owner_role'],'Belum ditetapkan')} | {t['reviewer_role']} | {names.get(t['reviewer_role'],'Belum ditetapkan')} |\n"
write('WF-006/penugasan-per-tiket.md',assignment)
sources = [ROOT/'Archives/Proposal.docx', ROOT/'Planning/revisi.txt',
           ROOT/'Planning/Waterfall/01-WBS-waterfall.md', ROOT/'Planning/Waterfall/Tiket/daftar-tiket.json']
sources += sorted((ROOT/'Planning').glob('0[1-7]-*.md'))
dump('WF-001/manifest-input.json', {'date':'2026-10-23','algorithm':'sha256',
    'sources':[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,
                'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources]})
print(json.dumps({'ticket_count':len(rows),'totals':totals},ensure_ascii=False))
