# jkpandora.github.io

รวมผลงานระบบ AI ของ JK Pandora → https://jkpandora.github.io

## โครงสร้าง
```
index.html              หน้า Hub รวมผลงาน
assets/theme.css        ธีมกลางที่ทุกหน้าใช้ร่วมกัน
assets/projects.js      รายชื่อระบบที่แสดงบนหน้า Hub
projects/aetox-vps/     เว็บระบบ Aetox VPS Ops
projects/_template/     แม่แบบสำหรับสร้างระบบใหม่
.nojekyll               ให้ GitHub ส่งไฟล์ออกไปตามที่เป็น ไม่ต้องประมวลผลก่อน
```

## อัปโหลดครั้งแรก (Windows PowerShell)
1. ไปที่ github.com แล้วกด New repository → ตั้งชื่อ `jkpandora.github.io` → เลือก Public → Create
2. แตกไฟล์ zip แล้ว `cd` เข้าไปในโฟลเดอร์ที่ได้
```powershell
git init
git add .
git commit -m "JK Pandora portfolio"
git branch -M main
git remote add origin https://github.com/jkpandora/jkpandora.github.io.git
git push -u origin main
```
3. ไปที่ Settings → Pages → Deploy from a branch → เลือก `main` และ `/ (root)` → Save
4. รอ 1–2 นาที แล้วเปิด https://jkpandora.github.io

## เพิ่มระบบใหม่
1. copy โฟลเดอร์ `projects/_template` แล้วเปลี่ยนชื่อเป็นชื่อระบบ เช่น `projects/xauusd-dashboard`
2. แก้ข้อความในไฟล์ `index.html` ของโฟลเดอร์นั้น
3. ใน `assets/projects.js` เปลี่ยน `status` ของระบบนั้นเป็น `"live"` (ถ้าเป็นระบบที่ยังไม่มีในรายการ ให้เพิ่มบรรทัดใหม่)
4. รัน `git add . ; git commit -m "add xauusd" ; git push`

## ข้อควรระวัง
ห้ามใส่ Token, รหัสผ่าน, Chat ID หรือ IP ของ VPS ลงในเว็บ เพราะ repo นี้เป็น Public

## ระบบเรียลไทม์ + AI (n8n อัปขึ้นเว็บอัตโนมัติ 24 ชม.)
n8n workflow ชื่อ "JK Pandora Web" (ไฟล์ `n8n-jkpandora-web-ai.json`) ทำงานทุก 30 นาที และส่งรายงานประจำวันตอน 08:17:
SSH เข้า VPS → รัน `tools/ai_publish.py` (เก็บสถานะ → Gemini วิเคราะห์ → เขียน `data/status.json` กับ `history.json` → git push) → ถ้าอัปไม่สำเร็จ หรือเป็นรอบรายงานประจำวัน จะแจ้งเข้า Telegram JKth01

ก่อนส่งขึ้นเว็บ สคริปต์จะลบ IP, token และ chat id ออกให้อัตโนมัติ

### ตั้งค่าบน VPS ครั้งเดียว (SSH เข้า VPS แล้ว copy คำสั่งไปวางทีละบล็อก)
```bash
# 1) สร้าง deploy key
ssh-keygen -t ed25519 -f ~/.ssh/jkpandora_deploy -N ""
cat ~/.ssh/jkpandora_deploy.pub
```
เอาข้อความที่ได้ไปวางที่ GitHub → repo → Settings → Deploy keys → Add key แล้วติ๊ก **Allow write access**
```bash
# 2) clone repo
cat >> ~/.ssh/config <<'C'
Host github-jkpandora
  HostName github.com
  User git
  IdentityFile ~/.ssh/jkpandora_deploy
C
cd /data/cloud_1tb && git clone git@github-jkpandora:jkpandora/jkpandora.github.io.git
cd jkpandora.github.io && git config user.name "Aetox VPS" && git config user.email "vps@jkpandora.local"

# 3) ทดสอบรัน 1 ครั้ง (ต้องเห็น "pushed": true)
LANG=C.UTF-8 python3 tools/ai_publish.py
```
### ตั้งค่าใน n8n
1. Workflows → Import from File → เลือกไฟล์ `n8n-jkpandora-web-ai.json`
2. เปิด node SSH ทั้ง 2 ตัว แล้วเลือก Credential **VPS SSH Key (n8n)** ตัวเดิมที่ใช้อยู่
3. กด Execute Workflow ทดสอบ 1 ครั้ง ถ้าผ่านให้เปิด **Active**

## รับผลงานผ่าน n8n Webhook (ให้ AI ส่งงานขึ้นเว็บได้เอง)
workflow: `n8n/jkpandora-submit-work.json` · คู่มือสำหรับ AI: `AI_SUBMIT.md`

1. n8n → Import ไฟล์ `n8n/jkpandora-submit-work.json`
2. เปิด node **รับผลงาน (Webhook)** → Credential → Create new → **Header Auth** ตั้งชื่อ `JKP Submit Token` · Name: `X-JKP-Token` · Value: ตั้งรหัสยาวๆ ที่เดายาก
3. เลือก Credential **VPS SSH Key (n8n)** ให้ node SSH ทั้ง 2 ตัว → เปิด **Active** แล้ว copy **Production URL** ของ Webhook
4. บนเครื่อง Windows รัน `setx JKP_WEBHOOK "<Production URL>"` และ `setx JKP_TOKEN "<รหัส>"` แล้วปิดเปิด PowerShell ใหม่
5. ทดสอบ: `.\tools\submit_work.ps1 -Name "ทดสอบ" -Desc "ทดสอบระบบ" -NoPolish` ต้องได้ `ok : True` และมีข้อความเข้า Telegram

ความปลอดภัย: ก่อนขึ้นเว็บ ระบบสแกน token, API key, private key, chat id และ IP ถ้าเจอจะปฏิเสธงานนั้น · ตอนนี้ n8n ยังเป็น http แนะนำให้เปิด HTTPS ก่อนส่งงานจากนอกเครื่อง
