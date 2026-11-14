#!/usr/bin/env python3
# รับผลงานจาก n8n (env WORK = base64 ของ JSON) → เก็บลง repo → git push
# JSON: {name, cat, desc, tech[], icon, html_b64?, demo?, download?, polish?}
import os, json, base64, re, subprocess, datetime, urllib.request
REPO = '/data/cloud_1tb/jkpandora.github.io'
WORKS = REPO + '/assets/works.json'
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True).stdout.strip()
def out(**k): print(json.dumps(k, ensure_ascii=False)); raise SystemExit
SECRET = [r'\b\d{8,10}:[\w-]{30,}', r'AIza[\w-]{30,}', r'sk-[\w-]{20,}', r'ghp_\w{30,}', r'-----BEGIN [A-Z ]*PRIVATE KEY',
          r'-100\d{8,}', r'(?i)(password|passwd|secret|api_key|token)\s*[:=]\s*["\']?\w{6,}']
try:
    w = json.loads(base64.b64decode(os.environ['WORK']).decode())
except Exception as e:
    out(ok=False, error='อ่านข้อมูลไม่ได้: ' + str(e)[:100])
name = str(w.get('name', '')).strip()[:80]
if not name: out(ok=False, error='ต้องมี name')
html = base64.b64decode(w['html_b64']).decode('utf-8', 'replace') if w.get('html_b64') else ''
if len(html) > 3_000_000: out(ok=False, error='ไฟล์ HTML ใหญ่เกิน 3MB')
blob = json.dumps(w, ensure_ascii=False) + html
hits = [p for p in SECRET if re.search(p, blob)]
if hits: out(ok=False, error='พบข้อมูลที่ดูเหมือนรหัสลับ ไม่อัปขึ้นเว็บ (ตรวจแล้วส่งใหม่)', patterns=len(hits))
if re.search(r'\b(?!127\.)\d{1,3}(\.\d{1,3}){3}\b', blob) and not w.get('allow_ip'):
    out(ok=False, error='พบเลข IP ในงาน ลบออกก่อน หรือส่ง allow_ip:true ถ้าตั้งใจใส่')
slug = re.sub(r'[^a-z0-9]+', '-', (w.get('slug') or name).lower()).strip('-')[:40] or 'work-' + datetime.datetime.now().strftime('%m%d%H%M')
desc = str(w.get('desc', ''))[:300]
# ให้ Gemini ช่วยเขียนคำอธิบายให้น่าอ่าน (ถ้าขอ)
if w.get('polish', True):
    key = ''
    for l in sh('docker exec open-notebook env').splitlines():
        if l.startswith('GEMINI_API_KEY='): key = l.split('=', 1)[1]
    if key:
        try:
            p = ('เขียนคำอธิบายผลงานภาษาไทย 1-2 ประโยค ไม่เกิน 160 ตัวอักษร สำหรับการ์ดโชว์ผลงานคอร์ส AI '
                 'ห้ามแต่งความสามารถที่ไม่มีในข้อมูล ตอบเฉพาะข้อความ\nชื่อ: ' + name + '\nข้อมูล: ' + desc + '\n' + html[:3000])
            body = json.dumps({'contents': [{'parts': [{'text': p}]}]}).encode()
            req = urllib.request.Request('https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=' + key, data=body, headers={'Content-Type': 'application/json'})
            t = json.load(urllib.request.urlopen(req, timeout=60))['candidates'][0]['content']['parts'][0]['text'].strip()
            if 10 < len(t) < 300: desc = t
        except Exception: pass
sh('cd ' + REPO + ' && git pull -q --rebase')
demo = str(w.get('demo', ''))
if html:
    d = REPO + '/programs/' + slug
    os.makedirs(d, exist_ok=True)
    back = '<a href="../../" style="position:fixed;top:10px;right:10px;z-index:999;background:#0b1020cc;color:#5eead4;border:1px solid #22304f;border-radius:99px;padding:5px 12px;font:13px sans-serif;text-decoration:none">← JK Pandora</a>'
    html = re.sub(r'(<body[^>]*>)', r'\1' + back, html, count=1)
    open(d + '/index.html', 'w', encoding='utf-8').write(html)
    demo = 'programs/' + slug + '/'
try: works = json.load(open(WORKS, encoding='utf-8'))
except Exception: works = []
item = {'slug': slug, 'icon': str(w.get('icon', '🧩'))[:4], 'name': name, 'cat': str(w.get('cat', 'อื่นๆ'))[:30],
        'desc': desc, 'tech': [str(x)[:20] for x in (w.get('tech') or [])][:6],
        'download': str(w.get('download', '')), 'demo': demo,
        'added': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime('%Y-%m-%d %H:%M')}
works = [x for x in works if x.get('slug') != slug]
works.insert(0, item)
json.dump(works, open(WORKS, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
r = sh('cd ' + REPO + ' && git add -A assets/works.json programs && git commit -q -m "Add work: ' + slug + '" && git push -q 2>&1 && echo PUSHED')
url = 'https://jkpandora.github.io/' + (demo if demo and not demo.startswith('http') else '#programs')
out(ok='PUSHED' in r, slug=slug, name=name, desc=desc, url=url, error='' if 'PUSHED' in r else 'git push ไม่สำเร็จ')
