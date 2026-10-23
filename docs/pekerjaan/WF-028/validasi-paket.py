"""Validate requirement deliverables independently of ignored Planning files.

Run from any directory: python -B docs/pekerjaan/WF-028/validasi-paket.py
Checks document evidence only, never approves a gate or tests the application.
"""
import hashlib
import json
import re
from datetime import datetime, timezone
from decimal import Decimal, ROUND_CEILING
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
ROOT = BASE.parent.parent
contract = json.loads((HERE / 'kontrak-keluaran.json').read_text(encoding='utf-8'))
errors = []
links = 0
artifacts = 0
package_manifest = json.loads((HERE/'manifest-paket.json').read_text(encoding='utf-8'))
for item in package_manifest['files']:
    path = BASE/item['path']
    if not path.exists() or hashlib.sha256(path.read_text(encoding='utf-8').encode('utf-8')).hexdigest() != item['sha256_utf8_lf']:
        errors.append('Requirement package changed: '+item['path'])
for ticket in contract['tickets']:
    folder = BASE / ticket['id']
    for name in ticket['artifacts'] + ['handoff.md', 'checkpoint.json']:
        path = folder / name
        if not path.is_file() or not path.stat().st_size:
            errors.append(f'Missing or empty: {ticket["id"]}/{name}')
        artifacts += 1
    checkpoint = json.loads((folder/'checkpoint.json').read_text(encoding='utf-8'))
    if checkpoint['stakeholder_accepted']:
        record = checkpoint.get('acceptance_record', {})
        gate = (HERE/'penerimaan-WF-G2.md').read_text(encoding='utf-8')
        if checkpoint['status'] != 'done' or checkpoint.get('acceptance_gate') != 'WF-G2' or any(
            not record.get(key) for key in ('recipient', 'recorded_at', 'source', 'reviewed_commit')
        ) or record.get('decision') != 'accepted':
            errors.append(f'Missing acceptance provenance: {ticket["id"]}')
        if '**Status: accepted.**' not in gate or record.get('reviewed_commit', '') not in gate:
            errors.append(f'Acceptance does not match gate record: {ticket["id"]}')
    elif checkpoint['status'] != 'in_review':
        errors.append(f'Unsupported unaccepted status: {ticket["id"]}')
    for path in folder.glob('*.md'):
        content = path.read_text(encoding='utf-8')
        if '\ufffd' in content:
            errors.append(f'Encoding replacement character: {path.name}')
        for link in re.findall(r'\]\(([^)]+)\)', content):
            if '://' in link or link.startswith('#'):
                continue
            links += 1
            target = (path.parent/link.split('#')[0]).resolve()
            # The report is produced at the end of this same validation run.
            if target != (HERE/'verifikasi-paket.json').resolve() and not target.exists():
                errors.append(f'Broken link: {path.name} -> {link}')

fr = (BASE/'WF-014/matriks-FR-dan-scope-rilis.md').read_text(encoding='utf-8')
trace = (BASE/'WF-027/matriks-kebutuhan-pengujian.md').read_text(encoding='utf-8')
for n in range(1,18):
    key=f'FR-{n:02}'
    if fr.count('| '+key+' |') != 1 or trace.count('| '+key+' |') != 1:
        errors.append('FR coverage: '+key)
for n in range(1,9):
    key=f'NFR-{n:02}'
    if trace.count('| '+key+' |') != 1:
        errors.append('NFR coverage: '+key)
for key in ['A08-PARAM','A08-RANK','S05-IMPORT','S05-EXPORT']:
    if key not in trace:
        errors.append('Missing split test scope: '+key)

manifest = json.loads((BASE/'WF-017/manifest-arsip.json').read_text(encoding='utf-8'))
for row in manifest['files']:
    path=ROOT/row['path']
    if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest()!=row['sha256']:
        errors.append('Archive missing/changed: '+row['path'])
audit=json.loads((BASE/'WF-017/audit-readonly.json').read_text(encoding='utf-8'))
expected={'files':49,'facilities':973,'unique_codes':973,'regencies':38,
          'coordinate_pairs':565,'missing_pairs':408,'unique_pairs':560,
          'duplicate_groups':5,'sum_detail':973,'sum_all':2919}
for key,value in expected.items():
    if audit[key]!=value:
        errors.append('Raw baseline differs: '+key)

# Independently check the small arithmetic examples, not application code.
examples=[]
for p,f,need,deficit in [(30000,1,1,0),(30001,1,2,1),(10000,0,1,1),(0,0,0,0)]:
    actual_need=int((Decimal(p)/Decimal(30000)).to_integral_value(rounding=ROUND_CEILING))
    actual_deficit=max(0,actual_need-f)
    passed=(actual_need,actual_deficit)==(need,deficit)
    examples.append({'population':p,'facilities':f,'expected':[need,deficit],
                     'actual':[actual_need,actual_deficit],'passed':passed})
    if not passed: errors.append('Arithmetic fixture differs')
if Decimal(30000+90000)/Decimal(1+2)!=Decimal(40000):
    errors.append('Weighted ratio example differs')

report={'checked_at':datetime.now(timezone.utc).isoformat(),
        'status':'passed' if not errors else 'failed','tickets':len(contract['tickets']),
        'required_artifacts_and_handoffs':artifacts,'local_links_checked':links,
        'FR_rows':17,'NFR_rows':8,'archive_hashes_checked':len(manifest['files']),
        'package_files_checked':len(package_manifest['files']),
        'arithmetic_examples':examples,'errors':errors,
        'scope':'Document presence, trace coverage, local links, archive integrity, and arithmetic examples. Not application tests, source licensing, or stakeholder acceptance.'}
(HERE/'verifikasi-paket.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
raise SystemExit(bool(errors))
