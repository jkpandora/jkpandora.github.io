# ส่งผลงานขึ้นเว็บ JK Pandora จาก Windows (หรือให้ Claude Code รันให้)
# ตัวอย่าง:
#   .\submit_work.ps1 -Name "โปรแกรม PDF" -Cat "เอกสาร/PDF" -Desc "รวมไฟล์ PDF" -Tech "Python,Claude" -Html .\pdf-tool.html
#   .\submit_work.ps1 -Name "Gold EA" -Cat "เทรด" -Download "https://github.com/jkpandora/gold-ea/releases"
# ตั้งค่าครั้งแรก:  setx JKP_WEBHOOK "http://<n8n>/webhook/jkpandora-submit"   และ   setx JKP_TOKEN "<รหัสของคุณ>"
param(
  [Parameter(Mandatory=$true)][string]$Name,
  [string]$Cat = "อื่นๆ", [string]$Desc = "", [string]$Tech = "", [string]$Icon = "🧩",
  [string]$Html = "", [string]$Demo = "", [string]$Download = "", [switch]$NoPolish
)
$body = @{ name=$Name; cat=$Cat; desc=$Desc; icon=$Icon; demo=$Demo; download=$Download; polish=(-not $NoPolish)
           tech=@($Tech -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ }) }
if ($Html) { $body.html_b64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes((Resolve-Path $Html))) }
$json = $body | ConvertTo-Json -Depth 4
$r = Invoke-RestMethod -Method Post -Uri $env:JKP_WEBHOOK -Headers @{ "X-JKP-Token" = $env:JKP_TOKEN } `
     -ContentType "application/json; charset=utf-8" -Body ([Text.Encoding]::UTF8.GetBytes($json))
$r | Format-List
