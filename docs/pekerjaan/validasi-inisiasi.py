"""Validate phase-one evidence presence, input integrity and estimate arithmetic."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parents[2]
base = root / 'docs/pekerjaan'
tickets = json.loads((root/'Planning/Waterfall/Tiket/daftar-tiket.json').read_text(encoding='utf-8'))['tickets']
errors = []
count = 0
for t in tickets[:12]:
    for name in t['planned_artifacts'] + ['handoff.md','checkpoint.json']:
        p=base/t['id']/name
        if not p.is_file() or not p.stat().st_size:
            errors.append(f'Missing/empty: {p.relative_to(root)}')
        count+=1
    p=base/t['id']/'checkpoint.json'
    if p.exists():
        c=json.loads(p.read_text(encoding='utf-8'))
        if c['accepted'] or c['delivery']['status']!='pending':
            errors.append(f"Unexpected acceptance/delivery claim: {t['id']}")
manifest=json.loads((base/'WF-001/manifest-input.json').read_text(encoding='utf-8'))
for item in manifest['sources']:
    if hashlib.sha256((root/item['path']).read_bytes()).hexdigest()!=item['sha256']:
        errors.append('Source changed: '+item['path'])
rows=json.loads((base/'WF-008/estimasi.json').read_text(encoding='utf-8'))['tickets']
if [r['id'] for r in rows]!=[t['id'] for t in tickets]:
    errors.append('Estimate IDs/order differ from catalog')
for r in rows:
    if abs(round(r['work']+r['review']+r['rework'],2)-r['base'])>.011:
        errors.append('Estimate sum: '+r['id'])
    if abs(round(r['base']*.2,2)-r['contingency'])>.011:
        errors.append('Contingency: '+r['id'])
assignment=(base/'WF-006/penugasan-per-tiket.md').read_text(encoding='utf-8')
for t in tickets:
    if assignment.count('| '+t['id']+' |')!=1:
        errors.append('Assignment missing/duplicate: '+t['id'])
report={'checked_at':datetime.now(timezone.utc).isoformat(),'status':'passed' if not errors else 'failed',
        'phase_one_tickets':12,'artifact_and_handoff_files_checked':count,
        'source_hashes_checked':len(manifest['sources']),'estimate_rows':len(rows),
        'assignment_rows':160,'errors':errors,
        'scope':'Presence, source hashes and arithmetic only; not stakeholder acceptance, application tests or Git delivery.'}
(base/'verifikasi-inisiasi.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
raise SystemExit(bool(errors))
