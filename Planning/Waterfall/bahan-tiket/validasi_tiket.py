"""Validasi cakupan WBS, urutan, dependensi, isi wajib, dan tautan lokal tiket.

Tidak menjalankan aplikasi, menyetujui gerbang, atau mengubah status pekerjaan.
"""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import re
from github_ticket_rules import SECTION, render_push_closure
from execution_readiness import SECTION as HANDOFF_SECTION, TARGETS, render_handoff, handoff_metadata
from susun_tiket import DETAILS

BASE = Path(__file__).resolve().parents[1]
TICKETS = BASE / 'Tiket'
REPORT = TICKETS / 'verifikasi-tiket.json'

def main():
    report = {'checked_at': datetime.now(timezone.utc).isoformat(), 'status': 'running'}
    REPORT.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    errors = []
    data = json.loads((TICKETS/'daftar-tiket.json').read_text(encoding='utf-8'))
    tickets = data['tickets']
    by_id = {t['id']: t for t in tickets}
    wbs_path = BASE/'01-WBS-waterfall.md'
    wbs = wbs_path.read_text(encoding='utf-8')
    wbs_rows = re.findall(r'^\| (\d+\.\d+\.\d+) \| (.*?) \| (.*?) \| (.*?) \|$', wbs, re.M)
    wbs_lookup = {r[0]: r for r in wbs_rows}
    def check(condition, message):
        if not condition:
            errors.append(message)
    check(len(tickets) == 160, 'Jumlah tiket bukan 160')
    check(data.get('version') == 3, 'Versi katalog handoff harus 3')
    check(len(by_id) == len(tickets), 'ID tiket duplikat')
    check(len({t['wbs'] for t in tickets}) == len(tickets), 'WBS duplikat dalam katalog')
    check(set(wbs_lookup) == {t['wbs'] for t in tickets}, 'Cakupan kode WBS tidak cocok')
    check(data['wbs_sha256'] == hashlib.sha256(wbs_path.read_bytes()).hexdigest(), 'Hash WBS berubah: katalog perlu ditinjau')
    statuses = Counter()
    words = []
    body_files = set()
    required_sections = ['Identitas dan kendali', 'Tujuan dan batas pekerjaan',
                         'Urutan dan syarat mulai', 'Input dan dependensi hasil',
                         'Langkah pelaksanaan', 'Keluaran yang diserahkan',
                         'Kriteria penerimaan dan verifikasi',
                         'Jika terhambat atau gagal', 'Log kerja dan penutupan',
                         'Task tambahan — Commit dan push ke GitHub']
    allowed_statuses = {'not_started', 'in_progress', 'blocked', 'in_review', 'done', 'deferred'}
    for index, t in enumerate(tickets, 1):
        ident = t['id']
        check(ident == f'WF-{index:03d}' and t['sequence'] == index, f'{ident}: urutan salah')
        check(t['phase'] == int(t['wbs'].split('.')[0]), f'{ident}: fase salah')
        row = wbs_lookup.get(t['wbs'])
        if row:
            check(t['title'] == row[1] and t['owner_role'] == row[2] and t['acceptance_from_wbs'] == row[3], f'{ident}: judul/PIC/AC berbeda dari WBS')
        expected_prev = tickets[index-2]['id'] if index > 1 else None
        expected_next = tickets[index]['id'] if index < len(tickets) else None
        check(t['previous_ticket'] == expected_prev, f'{ident}: pendahulu urutan salah')
        check(t['next_ticket'] == expected_next, f'{ident}: penerus urutan salah')
        check(t['priority'] == ('P1' if t['wbs'].startswith('4.10.') else 'P0'), f'{ident}: prioritas salah')
        closing = t.get('additional_closing_task', {})
        check(closing.get('id') == ident+'-GIT' and closing.get('required') is True,
              f'{ident}: metadata task push hilang/tidak sesuai')
        check(len(t['steps']) >= 4 and len(set(t['steps'])) == len(t['steps']), f'{ident}: langkah tidak lengkap/duplikat')
        check(bool(t['planned_artifacts']) and bool(t['verification']), f'{ident}: keluaran/verifikasi kosong')
        source_detail = DETAILS.get(t['wbs'], {})
        check(t['steps'] == source_detail.get('steps')
              and t['planned_artifacts'] == source_detail.get('artifacts')
              and t['verification'] == source_detail.get('verification'),
              f'{ident}: instruksi katalog tidak sinkron dengan sumber generator')
        for d in t['dependencies']:
            dep = by_id.get(d['ticket'])
            check(dep is not None, f'{ident}: dependensi tidak ditemukan {d["ticket"]}')
            if dep:
                check(dep['wbs'] == d['wbs'], f'{ident}: kode dependensi tidak cocok')
                check(dep['sequence'] < t['sequence'], f'{ident}: dependensi maju/siklus {dep["id"]}')
        if t['gate_out']:
            phase_ids = {x['id'] for x in tickets if x['phase'] == t['phase'] and x['id'] != ident}
            check(phase_ids <= {d['ticket'] for d in t['dependencies']}, f'{ident}: dependensi gerbang tidak meliputi seluruh fase')
        file = TICKETS / t['file']
        check(file.is_file(), f'{ident}: file tidak ada')
        if not file.is_file():
            continue
        body_files.add(file.resolve())
        body = file.read_text(encoding='utf-8')
        dependency_inputs = [f"docs/pekerjaan/{d['ticket']}/{a}"
                             for d in t['dependencies'] if d['ticket'] in by_id
                             for a in by_id[d['ticket']]['planned_artifacts']]
        check(t.get('execution_handoff') == handoff_metadata(ident, dependency_inputs),
              f'{ident}: metadata handoff berbeda dari kontrak rencana')
        check(body.count(HANDOFF_SECTION) == 1 and render_handoff(ident, dependency_inputs).strip() in body,
              f'{ident}: handoff tidak lengkap/konsisten')
        check(body.startswith(f'# {ident} — {t["title"]}'), f'{ident}: judul file tidak cocok')
        for section in required_sections:
            check(f'## {section}\n' in body, f'{ident}: bagian hilang {section}')
        check(body.count(SECTION) == 1, f'{ident}: jumlah bagian push bukan satu')
        check(render_push_closure(ident, t['title']).strip() in body,
              f'{ident}: instruksi push tidak konsisten dengan kebijakan bersama')
        check(body.index(SECTION) > body.index('## Log kerja dan penutupan'),
              f'{ident}: task push tidak berada pada penutup tiket')
        match = re.search(r'^\| Status \| `([^`]+)` \|$', body, re.M)
        check(match is not None and match.group(1) in allowed_statuses, f'{ident}: status invalid')
        if match:
            statuses[match.group(1)] += 1
        step_section = body.split('## Langkah pelaksanaan\n')[1].split('\n## ')[0]
        actual_steps = re.findall(r'^\d+\. (.+)$', step_section, re.M)
        check(actual_steps == t['steps'], f'{ident}: langkah file berbeda dengan katalog awal; sinkronkan perubahan instruksi')
        check(t['verification'] in body, f'{ident}: verifikasi file berbeda dari katalog')
        check(len(re.findall(r'^- \[[ xX]\] ', body, re.M)) >= 4, f'{ident}: acceptance checklist kurang')
        words.append(len(body.split()))
    actual_files = {p.resolve() for p in TICKETS.glob('*/WF-*.md')}
    check(actual_files == body_files, 'Ada file tiket yatim/tidak tercantum katalog')
    check(len({t['gate_out'] for t in tickets if t['gate_out']}) == 8, 'Gerbang tidak lengkap')
    check(len([t for t in tickets if t['execution_mode']=='support_cycle']) == 4, 'Jumlah tiket siklus dukungan salah')
    check(set(TARGETS) == {t['id'] for t in tickets if t['phase'] == 4}, 'Handoff target implementasi harus mencakup 52 tiket fase 4')
    param_steps = ' '.join(by_id['WF-120']['steps'])
    check('A08-PARAM' in param_steps and 'A08-RANK' in param_steps and 'meskipun seluruh P1 ditunda' in param_steps,
          'WF-120: parameter P0 harus terpisah dari ranking P1')
    positions = {t['wbs']: t['sequence'] for t in tickets}
    check(positions['1.2.4'] < positions['1.2.3'], 'Sumber daya harus sebelum estimasi')
    check(positions['6.2.2'] < positions['6.1.3'] < positions['6.2.3'], 'Admin produksi harus setelah migration dan sebelum publish')
    # Dependensi seluruhnya ke nomor lebih kecil sudah membuktikan DAG; cek juga penutupan per fase.
    for phase in range(2, 9):
        previous_gate = next(t for t in tickets if t['gate_out'] == f'WF-G{phase-1}')
        current = [t for t in tickets if t['phase'] == phase]
        check(all(t['sequence'] > previous_gate['sequence'] and t['gate_in'] == f'WF-G{phase-1}' for t in current), f'Fase {phase}: gerbang masuk tidak konsisten')
    scanned_links = 0
    md_files = list(TICKETS.rglob('*.md')) + [BASE/'README.md', BASE.parent/'README.md',
                                            BASE/'panduan-eksekusi.md', BASE/'prasyarat-eksekusi.md']
    for file in md_files:
        check(file.is_file(), f'Dokumen pendukung tidak ditemukan: {file.name}')
        if not file.is_file():
            continue
        content = file.read_text(encoding='utf-8')
        width = None
        fence = False
        for n, line in enumerate(content.splitlines(), 1):
            if line.startswith('```'):
                fence = not fence
            if not fence and line.startswith('|'):
                new_width = line.count('|')
                check(width is None or width == new_width, f'{file.name}:{n}: kolom tabel tidak konsisten')
                width = new_width
            else:
                width = None
        for target in re.findall(r'\]\(([^)]+)\)', content):
            if target.startswith(('http:', 'https:', '#', 'mailto:')):
                continue
            scanned_links += 1
            local = (file.parent/target.split('#')[0]).resolve()
            check(local.exists(), f'{file.name}: tautan rusak {target}')
    report.update({
        'status': 'passed' if not errors else 'failed',
        'ticket_count': len(tickets), 'wbs_level_3_count': len(wbs_lookup),
        'one_ticket_per_wbs': len(tickets)==len(wbs_lookup)==len({t['wbs'] for t in tickets}),
        'phase_counts': dict(Counter(t['phase'] for t in tickets)),
        'priority_counts': dict(Counter(t['priority'] for t in tickets)),
        'ticket_status_counts': dict(statuses),
        'stage_gate_count': sum(bool(t['gate_out']) for t in tickets),
        'minimum_task_specific_steps': min(len(t['steps']) for t in tickets),
        'github_closing_task_count': sum(bool(t.get('additional_closing_task', {}).get('required')) for t in tickets),
        'execution_handoff_count': sum(bool(t.get('execution_handoff')) for t in tickets),
        'implementation_handoff_count': len(TARGETS),
        'ticket_word_count_min': min(words), 'ticket_word_count_max': max(words),
        'local_links_checked': scanned_links,
        'errors': errors,
        'scope_of_check': 'Validasi dokumen, pemetaan, urutan, dan tautan; bukan pengujian aplikasi atau penerimaan gerbang.',
    })
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(bool(errors))

if __name__ == '__main__':
    main()
