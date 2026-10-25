import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'docs/pekerjaan'
catalog=json.loads((ROOT/'Planning/Waterfall/Tiket/daftar-tiket.json').read_text(encoding='utf-8'))
reviews=[
 'Arsitektur Mermaid dan data flow mencakup browser/server/worker/Colab, secret boundary, release/run dan withdrawal.',
 'Matriks environment dan lock/smoke procedures tersedia; PG/PostGIS target disamakan actual provider sebelum setup; tidak memakai SQLite untuk spatial.',
 '52 item implementasi memiliki target/test/runner/workdir/fixture, shared package Python dan lifecycle checkpoint; secret/dump/private data excluded.',
 'State job/lease/idempotency/chunk25/retry/partial-count tersedia; sukses parser berbeda dari validasi rilis.',
 'ERD dan kamus24tabel domain/ops mendefinisikan tipe/null/key/FK termasuk source/period/run dan review terpilih.',
 'Composite FK lintas boundary/release/review, checks, immutability locks, indeks dan migration order didesain; SQL belum dieksekusi.',
 'Grants/RLS roles non-owner, session dan operator token/abilities dirancang; tidak percaya --actor/auth.uid tanpa identitas.',
 'Lifecycle/version CAS/audit/outbox/visibility-before-cache dan backupDB+file/restore/rollback dijelaskan dengan race failure cases.',
 'Enam adapter memiliki input/discovery/parser/completeness/failure contracts; source edition/license/provider masih prerequisite nyata.',
 'Raw/typed split, locale/unit/null, code+parent+edition, approved aliases dan Sempol–Ijen tanpa double-count didesain.',
 'Source→candidate→evidence→review→selected snapshot; precision/status, duplicate/boundary/pulau dan max25checkpoint ditetapkan.',
 'Staging envelope/headers/partition/quarantine dan qualityreport/promotion gates lengkap; gagal tidak hilang diam-diam.',
 'Formula/domain/aggregate/precision dan expected independen tersedia; nine vectors diuji oleh validator desain, bukan aplikasi.',
 'Buffer perpoint geography/meters, AEQD reference, spheroid area, union/clip dan toleransi predeclared; tidak ada spatial run diklaim.',
 'GeoJSON4feature sintetis (valid/zero/null/islands) dan legend fixed classes tersedia; JSON/rings/context diperiksa.',
 'Notebook cell order, locked shared package, sanitized snapshot, input/output manifests dan fail-fast reproduksi ditentukan.',
 '9endpoint sukses dan10error examples finite JSON; validation filters/context/missing data dan internal public boundary ditentukan.',
 'Wireframe desktop/mobile semua halaman publik tersedia; walkthrough6UC mandiri tercatat tanpa mengarang review manusia.',
 'State triggers/empty/error/no_release/withdraw/tile dan sequenceguard/AbortController/focus keyboard didesain.',
 'Login/logout/session/denied dan CLI preview P0 didesain; layarP1 belum selected tidak diklaim built.',
 'Synthetic data/formula/spatial/access/CLI/race/import/repro fixture specs dan negative expected tersedia.',
 '84testprotocols mencakup seluruh ID lama + splitP0/P1 + scraping/CLI/lifecycle + UAT/usability/cold path; aplikasi not_run.',
 '5tugasUAT tanpa solusi, consent/form/rubrik80% dan gates/severity/retest ditulis; belum peserta/hasil nyata.',
 '24paket desain, trace17FR/8NFR,52handoff dan pemeriksaanJSON/hash/arithmetic dikumpulkan; WF-G3 pending review.',
]
for t,review in zip(catalog['tickets'][28:52],reviews):
 ident=t['id'];folder=BASE/ident
 issues=['Review/penerimaan stakeholder belum tercatat; status in_review bukan done/accepted.']
 if t['sequence'] in [29,37,38,39,40,42,52]:issues.append('Edisi/izin polygon historis, provider lokasi dan keputusan full/partial belum final.')
 if t['sequence'] in [30,35,36,50,52]:issues.append('Hosting/akun/budget/versiDB aktual dan operator bernama perlu dikonfirmasi sebelum provisioning/operasi.')
 if t['sequence'] in [31,45,48,49,50,51,52]:issues.append('Empat P1 masih kandidat ditunda; tidak dinyatakan deferred resmi atau selected tanpa keputusan pemilik.')
 cp={'version':1,'date':'2026-10-23','ticket':ident,'status':'in_review','executor':'Codex','stakeholder_accepted':False,
     'authorization':'User requested all folder03 tasks; existing preference one progress commit per item, plain messages, Planning ignored.',
     'artifacts':t['planned_artifacts'],'self_review':review,'open_items':issues,
     'delivery':{'kind':'progress_checkpoint','remote':'origin','branch':'main','verification':'Commit SHA and remote ancestry reported after push; acceptance separate.'}}
 (folder/'checkpoint.json').write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 links='\n'.join('- ['+a+']('+a+')' for a in t['planned_artifacts'])
 issue_text='\n'.join('- '+x for x in issues)
 handoff=f'''# Handoff {ident}

Versi1 · 23 Oktober2026 · Pelaksana Codex · Status in_review.

## Dasar dan keluaran

Input: [SRS kandidat](../WF-028/SRS-baseline.md), dokumen kebutuhan terkait dan instruksi pengguna melanjutkan folder03. Otorisasi lanjut dipakai tanpa mengarang persetujuan akademik atau keputusan data. Sumber versi/hash dicatat pada [manifest input](../WF-052/manifest-input.json).

{links}

## Pemeriksaan mandiri

Expected: {t['verification']}

Actual: {review}

[Verifikasi paket](../WF-052/verifikasi-desain.json) menguji struktur/hash/traceability/JSON/arithmetic. Tidak membuktikan migration, PostGIS, browser aplikasi atau UAT sudah lulus. Jam aktual tidak diukur dan tidak diganti estimasi.

## Tindak lanjut dan pengiriman

{issue_text}

Satu progress commit memuat keluaran item ini; judul tanpa ID tiket sesuai pengguna. SHA/remote diverifikasi setelah push. Planning tetap ignored, tidak force-add. Setelah keputusan reviewer tersedia, perbarui versi/desain terdampak dan catat acceptance nyata.
'''
 (folder/'handoff.md').write_text(handoff,encoding='utf-8')
 path=ROOT/'Planning/Waterfall/Tiket'/t['file']
 s=path.read_text(encoding='utf-8').replace('| Status | `not_started` |','| Status | `in_review` |',1)
 s=s.replace('| Belum ada | — | Belum dijalankan | — |',f'| 2026-10-23 | Codex | Desain dan pemeriksaan mandiri tersedia; progress commit sesuai mandat, acceptance eksternal pending. | [Handoff](../../../../docs/pekerjaan/{ident}/handoff.md) |',1)
 s=s.replace('- PIC aktual: belum ditetapkan.','- PIC aktual: Codex untuk desain teknis; penerima eksternal belum ditetapkan.',1)
 s=s.replace('- Keputusan review: belum direview.','- Keputusan review: pemeriksaan mandiri tersedia; belum accepted oleh stakeholder.',1)
 path.write_text(s,encoding='utf-8')

def entry(p):return {'path':p.relative_to(BASE).as_posix(),'sha256_utf8_lf':hashlib.sha256(p.read_text(encoding='utf-8').encode('utf-8')).hexdigest()}
inputs=[BASE/t['id']/a for t in catalog['tickets'][12:28] for a in t['planned_artifacts']]
manifest={'version':1,'date':'2026-10-23','hash_policy':'UTF-8 text universal newlines normalized to LF','files':[entry(p) for p in inputs]}
(BASE/'WF-052/manifest-input.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
paths=[]
for n in range(29,53):
 for p in sorted((BASE/f'WF-{n:03}').glob('*')):
  if p.is_file() and p.name not in ['manifest-paket.json','verifikasi-desain.json']:paths.append(p)
manifest={'version':1,'date':'2026-10-23','hash_policy':'UTF-8 text universal newlines normalized to LF; excludes self and generated report','files':[entry(p) for p in paths]}
(BASE/'WF-052/manifest-paket.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Prepared24 handoffs/checkpoints, {len(paths)} design file hashes, {len(inputs)} requirement input hashes.')
