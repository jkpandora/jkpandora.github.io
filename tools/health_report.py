#!/usr/bin/env python3
# JK Pandora - daily health report -> Telegram (read-only checks, changes nothing)
import subprocess, json, sqlite3, datetime, urllib.request, urllib.parse, os, glob, time

H = '/data/cloud_1tb/aetox-harness'
REPO = '/data/cloud_1tb/jkpandora.github.io'
N8N_DB = '/data/n8n/database.sqlite'
TZ = datetime.timezone(datetime.timedelta(hours=7))

def sh(c):
    return subprocess.run(c, shell=True, capture_output=True, text=True).stdout.strip()

env = {}
for l in open(H + '/.env', encoding='utf-8'):
    if '=' in l and not l.startswith('#'):
        k, v = l.split('=', 1); env[k.strip()] = v.strip().strip('"').strip("'")
TOKEN = env.get('TELEGRAM_BOT_TOKEN'); CHAT = env.get('TELEGRAM_CHAT_ID')

ok, warn, bad = [], [], []   # (text)

# 1) Docker containers
rows = sh("docker ps -a --format '{{.Names}}|{{.Status}}'").splitlines()
down = [r.split('|')[0] for r in rows if r and not r.split('|')[1].startswith('Up')]
restarting = [r.split('|')[0] for r in rows if 'Restarting' in r]
up = len(rows) - len(down)
(ok if not down else bad).append(f"Docker: ทำงาน {up}/{len(rows)}" + (f" — หยุด: {', '.join(down)}" if down else ''))
unhealthy = [r.split('|')[0] for r in rows if 'unhealthy' in r]
if unhealthy: warn.append('Container unhealthy: ' + ', '.join(unhealthy))

# 2) Disk / RAM / load
df = sh("df -h / | tail -1").split()
pct = int(df[4].rstrip('%')) if len(df) > 4 else 0
(ok if pct < 80 else warn if pct < 90 else bad).append(f"ดิสก์: ใช้ {df[2]} / {df[1]} ({pct}%)")
mem = sh("free -m | awk '/Mem/{printf \"%d %d\", $3, $2}'").split()
if len(mem) == 2:
    mp = round(int(mem[0]) * 100 / int(mem[1]))
    (ok if mp < 85 else warn).append(f"RAM: {mp}% ({mem[0]}/{mem[1]} MB)")
load = sh("cut -d' ' -f1 /proc/loadavg"); cpus = sh('nproc') or '1'
(ok if float(load or 0) < float(cpus) * 1.5 else warn).append(f"CPU load: {load} ({cpus} cores)")

# 3) Endpoints
for name, url, good in [('n8n', 'https://n8n.169.58.247.45.sslip.io/healthz', '200'),
                        ('เว็บ jkpandora.github.io', 'https://jkpandora.github.io/', '200')]:
    code = sh(f"curl -s -o /dev/null -m 15 -w '%{{http_code}}' {url}")
    (ok if code == good else bad).append(f"{name}: HTTP {code or 'timeout'}")

# 4) Security
f2b = sh("systemctl is-active fail2ban")
banned = sh("fail2ban-client status sshd 2>/dev/null | grep 'Currently banned' | awk '{print $NF}'")
(ok if f2b == 'active' else bad).append(f"fail2ban: {f2b} · แบนอยู่ {banned or 0} IP")
port = sh("ss -tlnp | grep ':5678 ' | awk '{print $4}' | head -1")
(ok if port.startswith('127.0.0.1') or not port else bad).append(f"n8n port 5678: {'เปิดเฉพาะภายใน ✔' if port.startswith('127.0.0.1') else ('ไม่พบ' if not port else 'เปิดสู่ภายนอก ' + port)}")
fails = sh("journalctl -u ssh --since '24 hours ago' 2>/dev/null | grep -c 'Failed password'") or '0'
(ok if int(fails) < 200 else warn).append(f"SSH ล็อกอินผิด 24 ชม.: {fails} ครั้ง")
if sh("[ -f /var/run/reboot-required ] && echo y") == 'y': warn.append('ระบบรอ reboot หลังอัปเดต')
upd = sh("apt list --upgradable 2>/dev/null | grep -c security") or '0'
if int(upd) > 0: warn.append(f"มีอัปเดตความปลอดภัยรอติดตั้ง {upd} รายการ")

# 5) Backups
def age_h(pattern):
    fs = glob.glob(pattern)
    return round((time.time() - max(os.path.getmtime(f) for f in fs)) / 3600, 1) if fs else None
for name, pat in [('Backup n8n (tar)', '/data/cloud_1tb/backups/n8n/*'),
                  ('Export workflow -> GitHub', '/data/cloud_1tb/n8n-backup/*')]:
    a = age_h(pat)
    if a is None: bad.append(f"{name}: ไม่พบไฟล์")
    else: (ok if a <= 26 else bad).append(f"{name}: ล่าสุด {a} ชม.ก่อน")

# 6) Website auto-publish
last = sh(f"cd {REPO} && git log -1 --format=%ct -- projects/aetox-vps/data")
if last:
    m = round((time.time() - int(last)) / 60)
    (ok if m <= 70 else bad).append(f"AI อัปเดตเว็บล่าสุด: {m} นาทีก่อน")

# 7) n8n workflows (read-only from DB copy)
wf_lines = []
try:
    tmp = '/tmp/n8n_ro.sqlite'; sh(f"cp {N8N_DB} {tmp}")
    db = sqlite3.connect(f'file:{tmp}?mode=ro', uri=True); c = db.cursor()
    wfs = c.execute("select id,name,active from workflow_entity").fetchall()
    since = (datetime.datetime.utcnow() - datetime.timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')
    stats = {}
    for wid, st in c.execute("select workflowId,status from execution_entity where startedAt >= ?", (since,)):
        s = stats.setdefault(wid, {'ok': 0, 'err': 0})
        if st == 'success': s['ok'] += 1
        elif st in ('error', 'crashed'): s['err'] += 1
    lastrun = dict(c.execute("select workflowId,max(startedAt) from execution_entity group by workflowId").fetchall())
    act = [w for w in wfs if w[2]]
    ok.append(f"n8n: workflow ทั้งหมด {len(wfs)} · เปิดใช้งาน {len(act)}")
    for wid, name, a in sorted(act, key=lambda w: w[1]):
        s = stats.get(wid, {'ok': 0, 'err': 0}); lr = lastrun.get(wid)
        if s['err'] and not s['ok']: icon = '🔴'; bad.append(f"Workflow '{name}': ล้มเหลวทุกครั้งใน 24 ชม. ({s['err']} ครั้ง)")
        elif s['err']: icon = '🟡'; warn.append(f"Workflow '{name}': error {s['err']} / สำเร็จ {s['ok']} ใน 24 ชม.")
        elif not s['ok']: icon = '⚪'
        else: icon = '🟢'
        wf_lines.append(f"{icon} {name[:38]} — ✓{s['ok']} ✗{s['err']}" + ('' if s['ok'] or s['err'] else f" (รันล่าสุด {str(lr)[:16] if lr else 'ไม่เคย'})"))
except Exception as e:
    warn.append(f"อ่านสถานะ n8n ไม่ได้ ({type(e).__name__})")

# ---- compose message ----
now = datetime.datetime.now(TZ)
score = 'สมบูรณ์ ✅' if not bad and not warn else ('มีจุดต้องดู ⚠️' if not bad else 'มีปัญหา ❌')
msg = [f"🛡️ <b>รายงานสุขภาพระบบประจำวัน</b>", f"{now:%d/%m/%Y %H:%M} น. · สถานะรวม: <b>{score}</b>", '']
if bad: msg += ['❌ <b>ต้องแก้ไขด่วน</b>'] + [f"• {x}" for x in bad] + ['']
if warn: msg += ['⚠️ <b>ควรตรวจสอบ</b>'] + [f"• {x}" for x in warn] + ['']
msg += ['✅ <b>ปกติ</b>'] + [f"• {x}" for x in ok] + ['']
if wf_lines: msg += ['⚙️ <b>n8n Workflow (24 ชม.)</b>', '🟢ปกติ 🟡มี error 🔴ล้มเหลว ⚪ไม่ได้รัน'] + wf_lines
text = '\n'.join(msg)
text = text.replace('&', '&amp;').replace('<b>', '\x01').replace('</b>', '\x02').replace('<', '&lt;').replace('>', '&gt;').replace('\x01', '<b>').replace('\x02', '</b>')

if os.environ.get('DRY'):
    print(text)
else:
    for i in range(0, len(text), 3900):
        data = urllib.parse.urlencode({'chat_id': CHAT, 'text': text[i:i+3900], 'parse_mode': 'HTML', 'disable_web_page_preview': 'true'}).encode()
        r = json.load(urllib.request.urlopen(f'https://api.telegram.org/bot{TOKEN}/sendMessage', data, timeout=30))
    print('SENT' if r.get('ok') else 'FAIL')
