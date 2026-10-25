"""Create synthetic design examples and implementation mappings, not app code."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT/'docs/pekerjaan'
catalog = json.loads((ROOT/'Planning/Waterfall/Tiket/daftar-tiket.json').read_text(encoding='utf-8'))

def dump(relative, obj):
    p=BASE/relative
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')

mapping=[]
for t in catalog['tickets'][52:104]:
    h=t['execution_handoff']
    targets=list(h['proposed_targets'])
    for path in list(targets):
        if path.startswith('scripts/etl/'):
            targets.append('python/gis_pipeline/etl/'+Path(path).name)
        elif path.startswith('scripts/analysis/') and path.endswith('.py'):
            targets.append('python/gis_pipeline/analysis/'+Path(path).name)
    if t['id']=='WF-055': targets+=['pyproject.toml','python/gis_pipeline/__init__.py']
    if t['id']=='WF-082': targets+=['app/Services/ReleaseContext.php']
    if t['id']=='WF-084': targets+=['app/Services/StatisticsService.php']
    mapping.append({'id':t['id'],'title':t['title'],'priority':t['priority'],
                    'scope':'conditional_pending_owner_selection' if t['priority']=='P1' else 'core',
                    'targets':list(dict.fromkeys(targets)),
                    'test_target':h['verification_target'],'commands':h['proposed_commands'],
                    'runner':h['runner'],'working_directory':'repository root',
                    'fixture_directory':h['fixture_directory'],
                    'manual_evidence':t['verification'] if not h['proposed_commands'] else None})
dump('WF-031/pemetaan-implementasi.json',{'version':1,'date':'2026-10-23','items':mapping})
md='# Pemetaan implementasi dan verifikasi\n\nVersi1 · 23 Oktober2026 · Penyusun Codex. Target file belum dibangun. Semua command dari root repo dengan runtime/locks WF-030; P1 hanya bila dipilih. Entry scripts Python memanggil shared package, bukan duplikasi algoritma.\n\n| Item | Target | Runner / verifikasi | Fixture |\n|---|---|---|---|\n'
for m in mapping:
    md+='| '+m['id']+' | '+'; '.join('`'+p+'`' for p in m['targets'])+' | '+m['runner']+': '+('; '.join('`'+c+'`' for c in m['commands']) or m['manual_evidence'])+' | `'+m['fixture_directory']+'` |\n'
md+='\nWF-068–070: batch≤25, queue hash/stable codes, pending+blocked+completed=initial; keputusan lokasi memerlukan bukti manusia. WF-086: checkpoint review→analyze→validate→publish→rollback→audit/cache/race, setiap substep punya negative test sebelum lanjut. CI PostgreSQL/PostGIS test harus tersedia sebelum WF-056, tidak menunggu WF-072.\n'
(BASE/'WF-031/pemetaan-implementasi.md').write_text(md,encoding='utf-8')

R='11111111-1111-4111-8111-111111111111'
RUN='22222222-2222-4222-8222-222222222222'
BOUND='33333333-3333-4333-8333-333333333333'
periods={'facilities':'2024-S1','population':'2023','area':'2023'}
meta={'release_id':R,'analysis_run_id':RUN,'boundary_set_id':BOUND,'source_periods':periods,
      'coordinate_coverage':{'registered':3,'coordinate_present':2,'eligible':1,'excluded':2},
      'warnings':['SYNTHETIC_FIXTURE','PARTIAL_LOCATIONS'],'generated_at':'2026-10-23T00:00:00Z'}
def square(x,y,d=.01):return [[x,y],[x+d,y],[x+d,y+d],[x,y+d],[x,y]]
features=[]
for code,name,value,complete,reason,geom in [
 ('0001001','Synthetic valid',2000,'complete',None,[[square(112,-7)]]),
 ('0001002','Synthetic zero',0,'complete',None,[[square(112.02,-7)]]),
 ('0001003','Synthetic unknown',None,'incomplete','POPULATION_MISSING',[[square(112.04,-7)]]),
 ('0001004','Synthetic islands',100,'complete',None,[[square(113,-7)],[square(113.02,-7.02)]]),
]:
    features.append({'type':'Feature','id':code,'geometry':{'type':'MultiPolygon','coordinates':geom},
                     'properties':{'code':code,'parent_code':'0001','name':name,'value':value,
                       'unit':'people_per_km2','metric':'density','completeness':complete,'reason':reason,
                       'without_facility':False,'source_ids':['44444444-4444-4444-8444-444444444444'],
                       'source_periods':periods,'release_id':R,'analysis_run_id':RUN,'synthetic':True}})
layer={'type':'FeatureCollection','features':features,'meta':{**meta,'metric':'density',
       'unit':'people_per_km2','geometry_detail':'display','legend':{'version':'fixed-v1','classes':['0','>0-1000','>1000-5000','>5000'],'no_data':'Belum tersedia'}}}
dump('WF-043/contoh-layer.json',layer)
facility={'code':'00000000001','name':'Synthetic clinic missing','address':'Synthetic address',
          'regency_code':'0001','district_code':'0001001','service_type':'Rawat Inap','area_type':'Perdesaan',
          'source_id':'44444444-4444-4444-8444-444444444444','source_locator':'fixture row1','location':None,'coordinate_status':'missing','precision_level':'unknown','synthetic':True}
examples=[
 {'path':'/api/v1/releases','status':200,'response':{'data':[{'release_id':R,'label':'SYNTHETIC-TEST','default_analysis_run_id':RUN,'status':'published'}],'meta':{'active_release_id':R,'page':1,'per_page':50,'total':1}}},
 {'path':'/api/v1/regions','query':{'level':'district','parent_code':'0001','release_id':R},'status':200,'response':{'data':[{'code':'0001001','name':'Synthetic district','parent_code':'0001','boundary_set_id':BOUND}],'meta':meta}},
 {'path':'/api/v1/facilities','status':200,'response':{'data':[facility],'meta':{**meta,'page':1,'per_page':50,'total':1}}},
 {'path':'/api/v1/facilities/{code}','status':200,'response':{'data':facility,'meta':meta}},
 {'path':'/api/v1/map/points','status':200,'response':{'type':'FeatureCollection','features':[{'type':'Feature','id':'00000000002','geometry':{'type':'Point','coordinates':[112,-7]},'properties':{'code':'00000000002','coordinate_status':'verified','precision_level':'facility','synthetic':True}}],'meta':{**meta,'filtered_registered':3,'filtered_mapped':2,'view_count':1,'bbox_applied':True}}},
 {'path':'/api/v1/map/regions','status':200,'response':layer},
 {'path':'/api/v1/statistics','status':200,'response':{'data':{'region_code':'0001','population':60000,'facility_count':3,'population_per_facility':20000,'T':30000,'completeness':'complete','reason':None},'meta':meta}},
 {'path':'/api/v1/analysis/buffers','query':{'analysis_run_id':RUN,'radius_m':3000,'release_id':R},'status':200,'response':{'type':'FeatureCollection','features':[{'type':'Feature','id':'0001003','geometry':None,'properties':{'code':'0001003','radius_m':3000,'covered_area_m2':None,'geometry_area_m2':1000000,'coverage_pct':None,'registered_count':1,'eligible_count':0,'excluded_count':1,'contributing_count':0,'completeness':'unavailable','reason':'NO_ELIGIBLE_INPUT','synthetic':True}}],'meta':meta}},
 {'path':'/api/v1/sources','status':200,'response':{'data':[{'source_id':'44444444-4444-4444-8444-444444444444','publisher':'Fixture','title':'Synthetic input','observation_period':'2023','locator':'fixture row1','license_note':'Synthetic test data','limitations':'Not research observations'}],'meta':meta}},
]
errors=[]
for status,code in [(400,'UNKNOWN_PARAMETER'),(401,'UNAUTHENTICATED'),(403,'FORBIDDEN'),(404,'RELEASE_NOT_FOUND'),(409,'STALE_ACTIVE_VERSION'),(419,'CSRF_TOKEN_MISMATCH'),(422,'INVALID_RADIUS'),(429,'RATE_LIMITED'),(503,'NO_PUBLISHED_RELEASE'),(503,'DEPENDENCY_UNAVAILABLE')]:
    errors.append({'status':status,'response':{'error':{'code':code,'message':'Synthetic error example','request_id':'synthetic-request'}}})
dump('WF-045/contoh-respons-API.json',{'schema_version':1,'synthetic':True,'success':examples,'errors':errors})

vectors=[]
for ident,p,f,a,t,density,ratio,need,deficit in [
 ('ceil-boundary',30000,1,'2',30000,'15000','30000',1,0),
 ('ceil-next',30001,1,'2',30000,'15000.5','30001',2,1),
 ('two-facilities',60000,2,'10',30000,'6000','30000',2,0),
 ('no-facility',10000,0,'2',30000,'5000',None,1,1),
 ('zero-population',0,0,'2',30000,'0',None,0,0),
 ('unknown-population',None,1,'2',30000,None,None,None,None),
 ('unknown-area',60000,3,None,30000,None,'20000',2,0),
 ('larger-deficit',90001,1,'2',30000,'45000.5','90001',4,3),
 ('changed-parameter',60000,2,'10',20000,'6000','30000',3,1),
]:
    vectors.append({'id':ident,'input':{'P':p,'F':f,'A':a,'T':t},'expected':{'density':density,'ratio':ratio,'need':need,'deficit':deficit,'without_facility':f==0}})
dump('WF-049/formula-fixtures.json',{'synthetic':True,'cases':vectors,'invalid_inputs':[{'P':-1,'F':1,'A':'1','T':30000},{'P':1,'F':-1,'A':'1','T':30000},{'P':1,'F':1,'A':'0','T':30000},{'P':1,'F':1,'A':'1','T':0}],
 'aggregates':[{'populations':[30000,90000],'facilities':[1,2],'expected_ratio':'40000'},{'populations':[30001,29999],'facilities':[1,1],'expected_sum_deficit':1,'T':30000}]})
dump('WF-049/contoh-spasial.json',{'synthetic':True,'crs':'EPSG:4326','radii_m':[1000,3000,5000],
 'points':[{'id':'overlap-a','coordinates':[112,-7],'eligible':True},{'id':'overlap-b','coordinates':[112.005,-7],'eligible':True},{'id':'centroid','coordinates':[112.01,-7.01],'eligible':False,'precision':'village'},{'id':'boundary','coordinates':[112,-7.02],'eligible':True}],
 'region':{'type':'MultiPolygon','coordinates':[[square(112,-7.02,.04)],[square(112.1,-7.1,.01)]]},
 'invalid_polygon':{'type':'Polygon','coordinates':[[[112,-7],[112.02,-6.98],[112,-6.98],[112.02,-7],[112,-7]]]},
 'expected':['centroid excluded','overlap union below sum','clip bounded by region','two islands preserved','invalid polygon rejected','r1 area <= r3 area <= r5 area']})

plan=(ROOT/'Planning/05-rencana-pengujian.md').read_text(encoding='utf-8')
rows=[]
suite={'D':('F-DATA/F-CROSS','python+PostGIS','data/schema/provenance'),
       'A':('F-RATIO','python+SQL','formula/aggregate'),
       'G':('F-GEO','PostGIS+pyproj','geometry/evidence'),
       'I':('F-ACCESS/F-RACE','PHP+PostGIS','integration/constraints'),
       'W':('F-DATA/F-ACCESS','Playwright','UI/state'),
       'S':('F-ACCESS/F-CLI/F-IMPORT','PHP+SQL+browser','security/recovery'),
       'P':('973 dataset and full boundary candidate','staging+k6/browser','performance'),
       'R':('F-REPRO','Colab+Python/browser','reproduction')}
for line in plan.splitlines():
    m=re.match(r'^\| ((?:[DAGIWSPR]\d{2})(?:-[A-Z]+)?) \| (.*?) \| (.*?) \|(?: (.*?) \|)?$',line)
    if not m:continue
    ident,action,expected,priority=m.groups()
    if ident=='S05':
        extra=[('S05-IMPORT','Importer file21MiB/salah header/jenis dan HTML input','Backend rejects invalid file; safe storage, escaped strings; no publish','P0'),
               ('S05-EXPORT','Export text beginning =,+,-,@ from selected public filter','Formula-neutralized CSV, exact filtered rows, metadata preserved','P1')]
    else:extra=[(ident,action,expected,priority or 'P0')]
    for ident,action,expected,priority in extra:
        if ident=='S01':action='Guest/disabled admin/invalid CLI token accesses protected operations and public draft URL';expected='401/403 or public404; actor cannot be forged; no draft data leak'
        fixture,runner,area=suite[ident[0]]
        rows.append({'id':ident,'priority':priority,'fixture':fixture,'environment':runner,
                     'setup':'Isolated TEST environment, candidate revision/locks; seed listed fixture; no production credentials',
                     'action':action,'expected':expected,'evidence':area+' expected/actual, code/release/run, logs/hash/role, defect/retest',
                     'status':'not_run'})
for ident,fixture,action,expected in [
 ('SRC-01','F-FAIL','Serve429+Retry-After then200','Respect delay, bounded attempts, no extra concurrency'),
 ('SRC-02','F-FAIL','Serve200loginHTML instead of PDF','Reject content/magic mismatch'),
 ('SRC-03','F-FAIL','Omit one expected page/feature ID','Incomplete source blocks promotion'),
 ('SRC-04','F-FAIL','Change mandatory header/unit','Schema change detected, raw preserved'),
 ('SRC-05','F-FAIL','Timeout on all3attempts','Job failed, no release promotion'),
 ('SRC-06','F-IMPORT','Replay same input/hash/version/target twice','Existing batch/no duplicate effects'),
 ('CLI-01','F-CLI','Forge actor/expired/revoked/wrong ability token','Deny; audited actor derived only from valid token'),
 ('LIFE-01','F-RACE','Concurrent publish same expected pointer version','One winner, one409; atomic pointer/run/audit'),
 ('LIFE-02','F-RACE','Inject failure before commit and after commit before outbox','Precommit all rollback; postcommit outbox retry, no mixed release'),
 ('LIFE-03','F-ACCESS','Withdraw release after cache populated','Public API/gateway404 even if server cache retained'),
 ('LIFE-04','F-ACCESS','Mutate published child/shared source/review or run','Denied; immutable history'),
 ('LIFE-05','F-ACCESS','Edit draft concurrently with validate','Lock serialization; report/input_revision must match'),
 ('P02-COLD','Performance profile','Measure cold API path separately before warm-up','Record uncached timings; do not present as warm target pass'),
 ('U01','F-DATA/UI','Inspect360/768/1366 layouts including panel/table','All controls usable, no page overflow hiding actions'),
 ('U02','F-DATA/UI','Navigate controls/dialog by keyboard and Escape','Labels and visible focus; dialog closes and restores focus'),
 ('U03','F-DATA/UI','Use no-data legend/table without map or color','Information equivalent; no-data distinguished from zero'),
 ('UAT-01','UAT staging','Participant finds specified facilities including missing point','Correct identity/address/service independently'),
 ('UAT-02','UAT staging','Participant compares two districts','Correct population/F/ratio and periods'),
 ('UAT-03','UAT staging','Participant enables3km and interprets result','Recognizes geometric distance and partial scope, not travel or population coverage'),
 ('UAT-04','UAT staging','Participant identifies unknown data and zero','Explains distinct meanings correctly'),
 ('UAT-05','UAT staging','Participant finds sources and versions','Identifies observation periods/release/run'),
]:
    env = 'human participants on staging' if ident.startswith('UAT-') else ('staging browser/performance profile' if ident.startswith(('P02-','U0')) else 'mock HTTP + PostGIS/PHP as applicable')
    rows.append({'id':ident,'priority':'P0','fixture':fixture,'environment':env,'setup':'Isolated TEST/staging fixture; two connections for race cases; participant consent for UAT','action':action,'expected':expected,'evidence':'timestamped actual, input/profile, observed outcome and sanitized logs; participant rubric for UAT','status':'not_run'})
assert len({r['id'] for r in rows})==len(rows)
dump('WF-050/prosedur-per-test.json',{'version':1,'date':'2026-10-23','cases':rows})
md='# Cakupan test per ID\n\nVersi1 · 23 Oktober2026 · Seluruh actual not_run; prosedur dan expected bukan bukti test pass. Setup dan environment per ID di prosedur-per-test.json; framework runner dari mapping WF-031.\n\n| ID | Prioritas | Fixture / environment | Tindakan | Expected |\n|---|---|---|---|---|\n'
for r in rows:md+='| '+' | '.join([r['id'],r['priority'],r['fixture']+' / '+r['environment'],r['action'],r['expected']])+' |\n'
(BASE/'WF-050/cakupan-test.md').write_text(md,encoding='utf-8')

fr_map={1:[33,34,37,38,40],2:[33,34,39,40],3:[43,45,46,47],4:[42,43,45,46],5:[33,41,45],6:[39,42,43,45],7:[30,31,44,49,50],8:[29,30,31],9:[30,33,34,35,36],10:[45,46,47],11:[41,45,46],12:[33,42,43,45,46],13:[37,40,44,45,46],14:[48,49,50],15:[32,35,36,48,49,50],16:[41,48,49,50],17:[49,50,51]}
nfr_map={1:[33,34,37,38,39,40],2:[46,47,50],3:[30,32,43,45,50],4:[46,47,50,51],5:[30,34,35,36,45,48,50],6:[30,31,36,41,42,44,50],7:[36,50],8:[39,41,42,43,44,46,51]}
trace=[]
phase2=(BASE/'WF-027/matriks-kebutuhan-pengujian.md').read_text(encoding='utf-8')
for prefix,mapping in [('FR',fr_map),('NFR',nfr_map)]:
    for n,designs in mapping.items():
        ident=f'{prefix}-{n:02}'
        row=next(line for line in phase2.splitlines() if line.startswith('| '+ident+' |'))
        trace.append({'requirement':ident,'design_items':[f'WF-{d:03}' for d in designs],
                      'tests':row.split('|')[2].strip(),
                      'scope':'conditional_P1' if ident in ['FR-14','FR-16'] else 'core_or_split_FR15'})
dump('WF-052/traceability-desain.json',{'requirements':trace})
dump('WF-052/kontrak-keluaran.json',{'version':1,'date':'2026-10-23','tickets':[{'id':t['id'],'title':t['title'],'artifacts':t['planned_artifacts'],'verification':t['verification']} for t in catalog['tickets'][28:52]]})
print(json.dumps({'implementation_items':52,'test_cases':len(rows),'requirements':len(trace)}))
