import os, json, glob, time, shutil, subprocess, datetime, re, urllib.request, base64
H = '/data/cloud_1tb/aetox-harness'; LOG = H + '/library/logs'
BK = '/data/cloud_1tb/backups/surrealdb'
REPO = '/data/cloud_1tb/jkpandora.github.io'
D = REPO + '/projects/aetox-vps/data'
MODE = os.environ.get('MODE', 'live')
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True).stdout.strip()
def clean(t):
    t = re.sub(r'\b\d{1,3}(\.\d{1,3}){3}\b', '[ip]', str(t))
    t = re.sub(r'-?100\d{8,}|\b\d{8,}:[\w-]{30,}', '[hidden]', t)
    return re.sub(r'(?i)(key|token|password|secret)\S*', '[hidden]', t)
sh('cd ' + REPO + ' && git pull -q --rebase')
run = tot = 0; down = []
for line in sh('docker ps -a --format "{{.Names}}|{{.State}}|{{.Status}}"').splitlines():
    n, st, ss = (line.split('|') + ['', '', ''])[:3]
    if n.startswith('surreal-restore-test'): continue
    tot += 1
    if st == 'running' and '(unhealthy)' not in ss: run += 1
    else: down.append(n)
fs = sorted(glob.glob(BK + '/open_notebook_*.surql'), key=os.path.getmtime)
bage = round((time.time() - os.path.getmtime(fs[-1])) / 3600) if fs else None
restore = 'PASS' if 'restore_test=PASS' in sh('tail -1 ' + LOG + '/backup_restore_test.log 2>/dev/null') else 'FAIL'
du = shutil.disk_usage('/data/cloud_1tb'); disk = du.used * 100 // du.total
deps = []
ap = LOG + '/audit_kpi.md'
if os.path.exists(ap):
    for l in open(ap, encoding='utf-8').read().splitlines():
        c = [x.strip() for x in l.strip().strip('|').split('|')]
        if len(c) >= 3 and c[0].isdigit():
            s = c[-1].upper(); s = 'FAIL' if 'FAIL' in s else 'PASS' if 'PASS' in s else 'NEED_ACTION'
            deps.append({'no': int(c[0]), 'name': clean(c[1]), 'status': s, 'note': clean(c[-2] if len(c) >= 4 else '')[:120]})
try: issues = json.load(open(LOG + '/supervisor_state.json'))
except Exception: issues = []
facts = {'containers': f'{run}/{tot}', 'down': down, 'restore': restore, 'disk_pct': disk,
         'backup_age_h': bage, 'issues': issues, 'kpi': deps,
         'recent_ai_orders': sh('tail -c 1500 ' + LOG + '/ai_orders.md 2>/dev/null')}
# ---- AI (Gemini) ----
key = ''
try:
    for l in open(H + '/.env', encoding='utf-8'):
        if l.startswith('GEMINI_API_KEY='): key = l.split('=', 1)[1].strip()
except Exception: pass
for l in ([] if key else sh('docker exec open-notebook env').splitlines()):
    if l.startswith('GEMINI_API_KEY='): key = l.split('=', 1)[1]
ai = {'summary': '', 'highlights': [], 'next': ''}
if key:
    prompt = ('คุณคือ AI ผู้รายงานผลงานระบบ Aetox VPS Ops บนเว็บสาธารณะ เขียนภาษาไทยสั้น กระชับ เป็นมิตร\n'
              'ห้ามใส่ IP, token, รหัสผ่าน, chat id หรือ path ภายในเครื่องเด็ดขาด\n'
              + ('นี่คือรายงานประจำวัน ให้สรุปภาพรวม 24 ชม.\n' if MODE == 'daily' else '')
              + 'ตอบเป็น JSON: {"summary":"สรุป 1-2 ประโยค","highlights":["จุดเด่น/สิ่งที่ระบบทำได้ 2-4 ข้อ"],"next":"สิ่งที่ควรทำต่อ 1 ประโยค"}\n\n'
              + json.dumps(facts, ensure_ascii=False))
    try:
        body = json.dumps({'contents': [{'parts': [{'text': prompt}]}], 'generationConfig': {'responseMimeType': 'application/json'}}).encode()
        req = urllib.request.Request('https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=' + key, data=body, headers={'Content-Type': 'application/json'})
        r = json.load(urllib.request.urlopen(req, timeout=90))
        ai.update(json.loads(r['candidates'][0]['content']['parts'][0]['text']))
    except Exception as e: ai['summary'] = 'AI ไม่ตอบในรอบนี้ (' + type(e).__name__ + ')'
ai = {'summary': clean(ai.get('summary', ''))[:400], 'highlights': [clean(x)[:160] for x in (ai.get('highlights') or [])][:4], 'next': clean(ai.get('next', ''))[:200]}
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))
os.makedirs(D, exist_ok=True)
hp = D + '/history.json'
try: hist = json.load(open(hp, encoding='utf-8'))
except Exception: hist = []
hist.insert(0, {'t': now.isoformat(timespec='minutes'), 'mode': MODE, 'containers': f'{run}/{tot}', 'issues': len(issues), 'summary': ai['summary']})
hist = hist[:30]
status = {'updated_at': now.isoformat(timespec='seconds'), 'containers': {'running': run, 'total': tot},
          'restore_test': restore, 'disk_pct': disk, 'backup_age_h': bage,
          'issues': ['x'] * len(issues), 'departments': deps, 'ai': ai}
json.dump(status, open(D + '/status.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(hist, open(hp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
# --- disk breakdown -> data/vps.json (auto) ---
try:
    def gb(path):
        o = sh('timeout 150 du -sb ' + path + ' 2>/dev/null | cut -f1')
        return round(sum(int(x) for x in o.split() if x.isdigit()) / 1e9, 2)
    df = sh("df -B1 / | tail -1").split()
    tot, used, free = int(df[1]) / 1e9, int(df[2]) / 1e9, int(df[3]) / 1e9
    parts = [['Docker (โปรแกรม/อิมเมจ)', gb('/var/lib/docker')],
             ['MT5 / ระบบเทรด', gb('/data/mt5*')],
             ['Coolify', gb('/data/coolify')], ['n8n', gb('/data/n8n')],
             ['ไฟล์โปรเจค (cloud_1tb)', gb('/data/cloud_1tb')],
             ['Backup เก่า', gb('/data/vps_old_backup')]]
    parts.insert(2, ['ระบบปฏิบัติการ + อื่นๆ', round(max(used - sum(x[1] for x in parts), 0), 2)])
    vp = REPO + '/data/vps.json'
    try: v = json.load(open(vp, encoding='utf-8'))
    except Exception: v = {}
    v.update({'disk_breakdown': [x for x in parts if x[1] > 0], 'disk_used_gb': round(used), 'disk_free_gb': round(free),
              'disk_total_gb': round(tot), 'disk_used_pct': round(used * 100 / tot), 'updated_at': now.isoformat()})
    json.dump(v, open(vp, 'w', encoding='utf-8'), ensure_ascii=False)
except Exception as e: print('disk err', type(e).__name__)
out = sh('cd ' + REPO + ' && git add projects/aetox-vps/data data/vps.json && git commit -q -m "AI update ' + now.strftime('%d/%m %H:%M') + '" && git push -q 2>&1 && echo PUSHED')
ok = 'PUSHED' in out
msg = '[เว็บ JK Pandora] ' + ('อัปเดตแล้ว ' if ok else 'อัปขึ้น GitHub ไม่สำเร็จ ') + now.strftime('%d/%m %H:%M') + '\n' + ai['summary']
print(json.dumps({'pushed': ok, 'mode': MODE, 'notify': (not ok) or MODE == 'daily', 'msg_b64': base64.b64encode(msg.encode()).decode()}, ensure_ascii=False))
