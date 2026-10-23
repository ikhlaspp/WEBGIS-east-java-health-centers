"""Check design artifacts and independent examples; does not test the app."""
import hashlib
import json
import math
import re
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
errors=[]
checks={}

def load(path):
    return json.loads(path.read_text(encoding='utf-8'),parse_constant=lambda c: (_ for _ in ()).throw(ValueError(c)))

def check(condition,message):
    if not condition: errors.append(message)

contract=load(HERE/'kontrak-keluaran.json')
ids=[f'WF-{n:03}' for n in range(29,53)]
check([t['id'] for t in contract['tickets']]==ids,'Expected exactly24 sequential design items')
links=0;required=0;json_count=0
for t in contract['tickets']:
    folder=BASE/t['id']
    for name in t['artifacts']+['handoff.md','checkpoint.json']:
        path=folder/name
        check(path.exists() and path.stat().st_size>0,f'Missing/empty {t["id"]}/{name}')
        required+=1
    cp=load(folder/'checkpoint.json')
    check(cp['status']=='in_review' and not cp['stakeholder_accepted'],f'Acceptance claim {t["id"]}')
    for p in folder.glob('*.json'):
        if p.name=='verifikasi-desain.json':continue
        try:load(p);json_count+=1
        except (ValueError,TypeError) as exc: errors.append(f'Invalid JSON {p.name}: {exc}')
    for p in folder.glob('*.md'):
        content=p.read_text(encoding='utf-8')
        check('\ufffd' not in content,f'Encoding error {p.name}')
        for link in re.findall(r'\]\(([^)]+)\)',content):
            if '://' in link or link.startswith('#'):continue
            links+=1;target=(p.parent/link.split('#')[0]).resolve()
            check(target==(HERE/'verifikasi-desain.json').resolve() or target.exists(),f'Broken link {p.name}: {link}')
checks.update(items=len(ids),required_artifacts_and_handoffs=required,local_links=links,json_files=json_count)

for filename in ['manifest-paket.json','manifest-input.json']:
    manifest=load(HERE/filename)
    for item in manifest['files']:
        p=BASE/item['path']
        check(p.exists() and hashlib.sha256(p.read_text(encoding='utf-8').encode('utf-8')).hexdigest()==item['sha256_utf8_lf'],f'Hash differs {item["path"]}')
    checks[filename+'_files']=len(manifest['files'])

mapping=load(BASE/'WF-031/pemetaan-implementasi.json')['items']
check([m['id'] for m in mapping]==[f'WF-{n:03}' for n in range(53,105)],'Implementation mapping52 IDs')
for m in mapping:
    check(bool(m['targets']) and bool(m['test_target']) and bool(m['fixture_directory']),f'Incomplete mapping {m["id"]}')
    check(m['working_directory']=='repository root',f'Unexpected working directory {m["id"]}')
    check(bool(m['commands']) or bool(m['manual_evidence']),f'No verification path {m["id"]}')
    check(all(not p.startswith(('/', 'C:', 'D:')) and '..' not in Path(p).parts for p in m['targets']),f'Invalid target path {m["id"]}')
checks['implementation_items']=len(mapping)

trace=load(HERE/'traceability-desain.json')['requirements']
expected={f'FR-{n:02}' for n in range(1,18)}|{f'NFR-{n:02}' for n in range(1,9)}
check({r['requirement'] for r in trace}==expected and len(trace)==25,'FR/NFR coverage')
for r in trace:check(bool(r['tests']) and r['design_items'] and set(r['design_items'])<=set(ids),f'Trace incomplete {r["requirement"]}')
checks['requirements']=len(trace)

test_cases=load(BASE/'WF-050/prosedur-per-test.json')['cases']
expected_tests=set()
for prefix,end in [('D',11),('A',7),('G',11),('I',8),('W',10),('S',7),('P',3),('R',3)]:
    expected_tests|={f'{prefix}{n:02}' for n in range(1,end+1)}
expected_tests.remove('S05')
expected_tests|={'S05-IMPORT','S05-EXPORT','A08-PARAM','A08-RANK','CLI-01','P02-COLD','U01','U02','U03'}
expected_tests|={f'SRC-{n:02}' for n in range(1,7)}|{f'LIFE-{n:02}' for n in range(1,6)}|{f'UAT-{n:02}' for n in range(1,6)}
check({t['id'] for t in test_cases}==expected_tests and len(test_cases)==len(expected_tests),'Test ID coverage mismatch')
for t in test_cases:
    check(all(t.get(k) for k in ['setup','action','expected','environment','evidence']),f'Incomplete test protocol {t["id"]}')
    check(t['status']=='not_run',f'False application test claim {t["id"]}')
for ident in ['S05-IMPORT','A08-PARAM']:
    check(next(t for t in test_cases if t['id']==ident)['priority']=='P0',f'Core test downgraded {ident}')
checks['test_protocols']=len(test_cases)

vectors=load(BASE/'WF-049/formula-fixtures.json')
for case in vectors['cases']:
    x=case['input'];p=x['P'];f=x['F'];a=Decimal(x['A']) if x['A'] is not None else None;t=x['T']
    # Independent acceptance arithmetic, not an application module invocation.
    need=math.ceil(Decimal(p)/Decimal(t)) if p is not None else None
    actual={'density':Decimal(p)/a if p is not None and a is not None else None,
            'ratio':Decimal(p)/Decimal(f) if p is not None and f else None,
            'need':need,'deficit':max(0,need-f) if need is not None else None,'without_facility':f==0}
    for k,value in case['expected'].items():
        expected_value=Decimal(value) if k in ['density','ratio'] and value is not None else value
        check(actual[k]==expected_value,f'Formula {case["id"]}/{k}: {actual[k]} != {expected_value}')
for case in vectors['invalid_inputs']:
    valid=(case['P'] is None or case['P']>=0) and case['F']>=0 and (case['A'] is None or Decimal(case['A'])>0) and case['T']>0
    check(not valid,'Invalid fixture unexpectedly meets declared domain')
check(Decimal(120000)/Decimal(3)==Decimal(vectors['aggregates'][0]['expected_ratio']),'Aggregate ratio')
check(sum(max(0,math.ceil(Decimal(p)/30000)-f) for p,f in zip([30001,29999],[1,1]))==vectors['aggregates'][1]['expected_sum_deficit'],'District deficit aggregate')
check(Decimal('1.005').quantize(Decimal('.01'),rounding=ROUND_HALF_UP)==Decimal('1.01'),'Display rounding')
checks['formula_vectors']=len(vectors['cases'])

layer=load(BASE/'WF-043/contoh-layer.json')
check(layer['type']=='FeatureCollection' and len({f['id'] for f in layer['features']})==len(layer['features']),'GeoJSON unique features')
for feature in layer['features']:
    props=feature['properties']
    check(props['release_id']==layer['meta']['release_id'] and props['analysis_run_id']==layer['meta']['analysis_run_id'],'GeoJSON release/run mismatch')
    check(feature['geometry']['type']=='MultiPolygon','GeoJSON geometry type')
    for polygon in feature['geometry']['coordinates']:
        for ring in polygon:
            check(len(ring)>=4 and ring[0]==ring[-1],'GeoJSON ring closure')
            check(all(len(pos)==2 and -180<=pos[0]<=180 and -90<=pos[1]<=90 for pos in ring),'GeoJSON position range')
check(any(f['properties']['value'] is None for f in layer['features']),'Missing null feature example')
check(any(f['properties']['value']==0 for f in layer['features']),'Missing zero feature example')
check(any(len(f['geometry']['coordinates'])==2 for f in layer['features']),'Missing island example')
checks['geojson_examples']=len(layer['features'])

api=load(BASE/'WF-045/contoh-respons-API.json')
endpoints={'/releases','/regions','/facilities','/facilities/{code}','/map/points','/map/regions','/statistics','/analysis/buffers','/sources'}
check({e['path'].removeprefix('/api/v1') for e in api['success']}==endpoints,'API endpoint examples incomplete')
for e in api['success']:
    response=e['response']
    check('meta' in response and ('data' in response or 'features' in response),'API envelope missing')
    if e['path']!='/api/v1/releases':
        check(response['meta']['release_id']==layer['meta']['release_id'] and response['meta']['analysis_run_id']==layer['meta']['analysis_run_id'],'API context differs')
check({e['status'] for e in api['errors']}>={400,401,403,404,409,419,422,429,503},'Error coverage')
checks['api_success_examples']=len(api['success'])
checks['api_error_examples']=len(api['errors'])

report={'checked_at':datetime.now(timezone.utc).isoformat(),'status':'passed' if not errors else 'failed',
        'checks':checks,'errors':errors,
        'scope':'Design artifacts, links/hashes, traceability, protocol coverage, JSON structure and independent arithmetic only. Not application/SQL/PostGIS/browser execution or stakeholder approval.'}
(HERE/'verifikasi-desain.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
raise SystemExit(bool(errors))
