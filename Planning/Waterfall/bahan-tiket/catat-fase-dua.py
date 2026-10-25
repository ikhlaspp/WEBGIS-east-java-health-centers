import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[3]
base = root/'docs/pekerjaan'
catalog_path = root/'Planning/Waterfall/Tiket/daftar-tiket.json'
tickets = json.loads(catalog_path.read_text(encoding='utf-8'))['tickets'][12:28]
checks = [
    'UC-01–12 meliputi guest/admin, missing, no-data, error dan lifecycle; tidak ada akun guest.',
    'FR-01–17 dipetakan ke skenario/build/test; backend FR-15 P0, empat fitur P1 dipisahkan.',
    'Operasi read/write/command dipetakan guest/admin; role DB terpisah; actor CLI dan penolakan draft eksplisit.',
    'Tujuh halaman inti serta state loading/empty/error/no-data tersedia; missing dapat diakses melalui tabel.',
    '49 hash cocok audit lama; CSV dihitung ulang: 973 kode/38 kab, 565 pair/408 missing, 560 pair unik, 5 grup duplikat.',
    'Halaman resmi diperiksa; tiga PDF lokal diekstrak dengan pdftotext; sampel/locator disimpan. Belum full scraping/OCR/izin.',
    'Snapshot 2024-S1, target penduduk/master 2023, unit/identity/provenance ditulis; polygon 2026 belum diterima.',
    'DQ-01–11 membedakan raw/verified/null/zero/alias; eligibility, blocker dan partial denominator eksplisit.',
    'Delapan indikator dengan edge cases/agregasi; contoh aritmetika diperiksa independen pada validator paket.',
    'Titik/batas/choropleth/buffer, kelas tetap, no-data/zero dan filter administratif konsisten.',
    'Radius 1000/3000/5000 meter, union/clip/pulau/tetangga/zero eligible; bukan klaim buffer aktual.',
    'Notebook/HTML/tabel/peta/screenshot/laporan/manifest dipetakan; identitas rilis/run dan batas P2 tersedia.',
    'Profil dataset/perangkat/network/cache/VU/sample ditetapkan bersama target; belum hasil benchmark.',
    'Role/audit/session, backup DB+file, retensi, RPO/RTO dan restore/repro tertulis; layanan/owner belum dikonfirmasi.',
    '17 FR dan 8 NFR punya test/evidence; S05/A08 P0 terpisah P1; lima tugas UAT dan denominator 80% eksplisit.',
    'SRS menggabungkan 16 item, traceability dan scope; gerbang pending_review dengan blocker sumber/keputusan nyata.',
]
contract = {'version':1,'date':'2026-10-23',
            'source_catalog_sha256':hashlib.sha256(catalog_path.read_bytes()).hexdigest(),
            'tickets':[{'id':t['id'],'title':t['title'],'artifacts':t['planned_artifacts'],
                        'acceptance':t['verification']} for t in tickets]}
(base/'WF-028/kontrak-keluaran.json').write_text(json.dumps(contract,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for t,review in zip(tickets,checks):
    ident=t['id'];folder=base/ident;n=t['sequence']
    blockers=['Penerimaan reviewer eksternal belum tercatat; WF-G2 tidak diklaim accepted.']
    if n in [14,20,23,28]:
        blockers.append('Scope P1/full/partial memakai asumsi kerja, belum jawaban eksplisit pemilik.')
    if n in [18,19,28]:
        blockers.append('Edisi/izin polygon historis dan provider batch masih terbuka.')
    if n in [25,26,28]:
        blockers.append('Hosting/budget/owner aktual belum dikonfirmasi; target kandidat engineering.')
    checkpoint={'version':1,'date':'2026-10-23','ticket':ident,'status':'in_review',
                'local_deliverables':'prepared_and_self_reviewed','executor':'Codex',
                'stakeholder_accepted':False,
                'authorization':'User requested all 16 folder-02 items and one progress commit per item; stakeholder acceptance is separate.',
                'artifacts':t['planned_artifacts'],'review':review,'open_items':blockers,
                'git_delivery':{'kind':'progress_checkpoint','target':'origin/main',
                                'verification':'Exact commit and remote ancestry reported after push; final acceptance is separate.'}}
    (folder/'checkpoint.json').write_text(json.dumps(checkpoint,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    artifact_links='\n'.join('- ['+a+']('+a+')' for a in t['planned_artifacts'])
    blocker_lines='\n'.join('- '+b for b in blockers)
    handoff=f'''# Handoff {ident}

Versi 1 · 23 Oktober 2026 · Pelaksana: Codex · Status: in_review.

## Input dan otorisasi

Proposal/Planning lokal, revisi pengguna, paket fase 1 dan instruksi terbaru melanjutkan folder 02 dengan 16 commit. Pengguna mengotorisasi pekerjaan dan pengiriman progres; bukan bukti penerimaan akademik atau keputusan sumber yang belum ada. Planning tetap ignored; keluaran item ini tersedia dalam direktori sendiri.

## Keluaran

{artifact_links}

## Pemeriksaan expected/actual

Expected: {t['verification']}

Actual pemeriksaan mandiri: {review}

Pemeriksaan struktur/hash/coverage tersedia pada [verifikasi paket](../WF-028/verifikasi-paket.json). Uji aplikasi/UAT tidak dijalankan pada fase kebutuhan. Tidak ada angka estimasi yang disebut jam aktual.

## Tindak lanjut

{blocker_lines}

Commit progres satu item dikirim sesuai arahan; SHA/hasil remote dilaporkan setelah push. Setelah keputusan pemilik tersedia, revisi artefak dan catat reviewer/tanggal sebelum baseline accepted.
'''
    (folder/'handoff.md').write_text(handoff,encoding='utf-8')
    p=root/'Planning/Waterfall/Tiket'/t['file']
    s=p.read_text(encoding='utf-8').replace('| Status | `not_started` |','| Status | `in_review` |',1)
    s=s.replace('| Belum ada | — | Belum dijalankan | — |',
                f'| 2026-10-23 | Codex | Keluaran kebutuhan diperiksa; pengguna mengotorisasi lanjut dan commit progres; penerimaan eksternal pending. | [Handoff](../../../../docs/pekerjaan/{ident}/handoff.md) |',1)
    s=s.replace('- PIC aktual: belum ditetapkan.','- PIC aktual: Codex (pelaksana teknis); penerima eksternal belum dikonfirmasi.',1)
    s=s.replace('- Keputusan review: belum direview.','- Keputusan review: pemeriksaan mandiri pada handoff; baseline eksternal belum accepted.',1)
    p.write_text(s,encoding='utf-8')
print('Prepared 16 handoffs/checkpoints; ignored local ticket logs updated.')
