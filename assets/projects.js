// รายชื่อระบบ/โปรเจกต์ทั้งหมดที่โชว์บนหน้า Hub
// ถ้าจะเพิ่มระบบใหม่ ให้เพิ่มทีละ 1 บรรทัดตรงนี้ (status: "live" หรือ "soon")
window.PROJECTS = [
  { icon:"🖥️", name:"Aetox VPS Ops", desc:"ดูแล VPS ด้วยทีม AI 20 แผนก + n8n AI Supervisor (Gemini) แจ้งเตือนผ่าน Telegram", path:"projects/aetox-vps/", tags:["AI Agent","n8n","Docker","VPS"], status:"live" },
  { icon:"📈", name:"XAUUSD Dashboard", desc:"แดชบอร์ดผล MT5 / Gold EA", path:"projects/xauusd-dashboard/", tags:["MT5","n8n","Trading"], status:"soon" },
  { icon:"💬", name:"JK Pandora LINE Bot", desc:"แชทบอต LINE + Telegram ตอบคำถามเรื่อง VPS ระบบเทรด และข่าวทอง ด้วยทีม AI", path:"projects/line-bot/", tags:["AI Agent","LINE","Telegram"], status:"live" },
  { icon:"📘", name:"AI Ebook", desc:"แผนอีบุ๊ก AI และ AI Agent เปรียบเทียบ Claude กับ Gemini วางโครงไว้ 8 บท ทำเป็นซีรีส์", path:"projects/ai-ebook/", tags:["Ebook","Claude","Gemini"], status:"live" },
  { icon:"⚙️", name:"n8n Automation", desc:"workflow อัตโนมัติบน n8n: AI Supervisor ดูแล VPS และ AI อัปผลงานขึ้นเว็บ", path:"n8n/", tags:["n8n","Gemini","Telegram"], status:"live" }
];

// ===== โปรแกรมที่สร้างด้วย Claude =====
// เพิ่มผลงานโดยเพิ่มบรรทัดใหม่ตรงนี้ หรือใช้ "เครื่องมือเพิ่มผลงาน" ท้ายหน้า Hub ช่วยสร้างบรรทัดให้
// cat: "เครื่องมือ" | "เอกสาร/PDF" | "Windows" | "สื่อ/มัลติมีเดีย" | "เทรด" | "อื่นๆ"
// download: ลิงก์ไฟล์ (แนะนำให้อัปไฟล์ไว้ที่ GitHub Releases) · demo: ลิงก์หน้าเว็บ (ถ้ามี)
window.PROGRAMS = [
  { icon:"📱", name:"JK Thai Reader Mobile", cat:"สื่อ/มัลติมีเดีย", desc:"แอปอ่านออกเสียงภาษาไทยบนมือถือ แบ่งข้อความเป็นช่วงแล้วไฮไลต์ประโยคที่กำลังอ่าน", tech:["HTML","JavaScript","Web Speech"], download:"", demo:"programs/thai-reader-mobile/" },
  { icon:"🔊", name:"อ่านออกเสียงภาษาไทย", cat:"เครื่องมือ", desc:"โปรแกรมอ่านข้อความภาษาไทยออกเสียง เลือกเสียงและปรับความเร็วได้ เปิดไฟล์ข้อความได้", tech:["HTML","JavaScript"], download:"", demo:"programs/thai-tts/" },
  { icon:"🛡️", name:"Aetox Supervisor + AI", cat:"ระบบอัตโนมัติ (n8n)", desc:"n8n ตรวจ VPS ทุก 5 นาที แก้ค่าอัตโนมัติ ให้ Gemini วิเคราะห์ แล้วแจ้งเข้า Telegram", tech:["n8n","SSH","Gemini"], download:"", demo:"projects/aetox-vps/" },
  { icon:"🌐", name:"JK Pandora Web AI Publisher", cat:"ระบบอัตโนมัติ (n8n)", desc:"n8n ให้ AI วิเคราะห์ระบบแล้วอัปผลขึ้นเว็บนี้เองทุก 30 นาที ตลอด 24 ชม.", tech:["n8n","GitHub","Gemini"], download:"", demo:"projects/aetox-vps/#ai" },
  { icon:"📥", name:"Work Submit Webhook", cat:"ระบบอัตโนมัติ (n8n)", desc:"ช่องรับผลงานผ่าน n8n: AI หรือ Claude Code ส่งงานเข้ามา ระบบสแกนรหัสลับ ให้ Gemini เขียนคำอธิบาย แล้วขึ้นเว็บเอง", tech:["n8n","Webhook","GitHub"], download:"", demo:"n8n/" },
  { icon:"📊", name:"บทอัดเสียง 1,000 ประโยค", cat:"Sheets", desc:"ตารางบทอัดเสียงภาษาไทย 1,000 ประโยค สำหรับใช้กับ JK Thai Reader (เก็บไว้ใน Claude Sheets)", tech:["Claude Sheets"], download:"", demo:"" }
];
