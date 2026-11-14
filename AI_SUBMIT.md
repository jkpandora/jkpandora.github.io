# คู่มือสำหรับ AI / Claude Code: ส่งผลงานขึ้นเว็บ JK Pandora

เมื่อสร้างงานเสร็จแล้ว และ Jk ขอให้ "อัปขึ้นเว็บ" ให้ส่งงานเข้า n8n Webhook ตามนี้

## ส่งจาก Windows (PowerShell)
```powershell
.\tools\submit_work.ps1 -Name "ชื่อผลงาน" -Cat "เครื่องมือ" -Desc "ทำอะไรได้" -Tech "Python,Claude" -Html .\path\to\page.html
```
หมวด (Cat): เครื่องมือ · เอกสาร/PDF · Windows · สื่อ/มัลติมีเดีย · เทรด · ระบบอัตโนมัติ (n8n) · Sheets · อื่นๆ

## ส่งด้วย curl (Linux / VPS / Claude Code)
```bash
curl -s -X POST "$JKP_WEBHOOK" -H "X-JKP-Token: $JKP_TOKEN" -H "Content-Type: application/json" \
  -d "{\"name\":\"ชื่อผลงาน\",\"cat\":\"ระบบอัตโนมัติ (n8n)\",\"desc\":\"...\",\"tech\":[\"n8n\"],\"html_b64\":\"$(base64 -w0 page.html)\"}"
```

## ฟิลด์ที่ใช้ได้
| ฟิลด์ | ความหมาย |
|---|---|
| name (ต้องมี) | ชื่อผลงาน |
| cat, desc, icon, tech[] | หมวด คำอธิบาย ไอคอน และเทคโนโลยี |
| html_b64 | หน้าเว็บ HTML ไฟล์เดียว เข้ารหัส base64 (ไม่เกิน ~80KB) ระบบจะตั้งให้เป็นหน้า Demo เอง |
| demo / download | ลิงก์ Demo หรือลิงก์ดาวน์โหลด (ไฟล์ใหญ่ให้อัปไว้ที่ GitHub Releases) |
| polish | ให้ Gemini เขียนคำอธิบายให้ใหม่ (ค่าเริ่มต้น true) |
| slug | ส่งชื่อเดิมซ้ำ = อัปเดตผลงานเดิม |

## กฎ
- ห้ามส่ง Token, API key, รหัสผ่าน, Chat ID หรือ IP ของ VPS ถ้าเจอ ระบบจะไม่อัปขึ้นเว็บ
- ห้ามส่งข้อมูลส่วนตัวหรือข้อมูลของที่ทำงาน ถ้า Jk ไม่ได้อนุญาต
- ผลลัพธ์ที่ได้กลับมาจะมี `url` ให้ส่งลิงก์นั้นให้ Jk
