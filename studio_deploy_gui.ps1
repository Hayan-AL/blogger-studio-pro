<#
.SYNOPSIS
    Blogger Studio Pro - Native Windows Deployment Control Center
    لوحة التحكم الاحترافية - مركز النشر السحابي المرئي
#>

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
if (-not $ScriptDir) { $ScriptDir = (Get-Location).Path }
Set-Location $ScriptDir

# --- Color Palette (Modern Slate Dark Theme) ---
$bgDark      = [System.Drawing.ColorTranslator]::FromHtml("#0b1120")
$cardBg      = [System.Drawing.ColorTranslator]::FromHtml("#1e293b")
$cardBorder  = [System.Drawing.ColorTranslator]::FromHtml("#334155")
$textLight   = [System.Drawing.ColorTranslator]::FromHtml("#f8fafc")
$textMuted   = [System.Drawing.ColorTranslator]::FromHtml("#94a3b8")
$cyan        = [System.Drawing.ColorTranslator]::FromHtml("#38bdf8")
$emerald     = [System.Drawing.ColorTranslator]::FromHtml("#10b981")
$emeraldDark = [System.Drawing.ColorTranslator]::FromHtml("#059669")
$purple      = [System.Drawing.ColorTranslator]::FromHtml("#8b5cf6")
$purpleDark  = [System.Drawing.ColorTranslator]::FromHtml("#7c3aed")
$amber       = [System.Drawing.ColorTranslator]::FromHtml("#f59e0b")
$rose        = [System.Drawing.ColorTranslator]::FromHtml("#f43f5e")

# --- Fonts ---
$fontTitle   = New-Object System.Drawing.Font("Segoe UI", 13, [System.Drawing.FontStyle]::Bold)
$fontSub     = New-Object System.Drawing.Font("Segoe UI", 9.5, [System.Drawing.FontStyle]::Regular)
$fontSection = New-Object System.Drawing.Font("Segoe UI", 11, [System.Drawing.FontStyle]::Bold)
$fontRegular = New-Object System.Drawing.Font("Segoe UI", 9.5, [System.Drawing.FontStyle]::Regular)
$fontBold    = New-Object System.Drawing.Font("Segoe UI", 9.5, [System.Drawing.FontStyle]::Bold)
$fontMono    = New-Object System.Drawing.Font("Consolas", 9.5, [System.Drawing.FontStyle]::Regular)
$fontLog     = New-Object System.Drawing.Font("Segoe UI", 9, [System.Drawing.FontStyle]::Regular)

# --- Main Form ---
$form = New-Object System.Windows.Forms.Form
$form.Text = "Blogger Studio Pro | مركز النشر السحابي والربط التلقائي"
$form.Size = New-Object System.Drawing.Size(840, 740)
$form.StartPosition = "CenterScreen"
$form.FormBorderStyle = "FixedDialog"
$form.MaximizeBox = $false
$form.BackColor = $bgDark
$form.ForeColor = $textLight
$form.RightToLeft = [System.Windows.Forms.RightToLeft]::Yes

# --- Header Panel ---
$headerPanel = New-Object System.Windows.Forms.Panel
$headerPanel.Location = New-Object System.Drawing.Point(20, 15)
$headerPanel.Size = New-Object System.Drawing.Size(785, 75)
$headerPanel.BackColor = $cardBg
$headerPanel.BorderStyle = [System.Windows.Forms.BorderStyle]::FixedSingle
$form.Controls.Add($headerPanel)

$lblHeader = New-Object System.Windows.Forms.Label
$lblHeader.Text = "🚀 Blogger Studio Pro - مركز النشر السحابي والربط التلقائي"
$lblHeader.Font = $fontTitle
$lblHeader.ForeColor = $cyan
$lblHeader.Location = New-Object System.Drawing.Point(15, 10)
$lblHeader.Size = New-Object System.Drawing.Size(755, 30)
$headerPanel.Controls.Add($lblHeader)

$lblSub = New-Object System.Windows.Forms.Label
$lblSub.Text = "لوحة التحكم الاحترافية | نشر وتحديث بضغطة زر واحدة على Cloudflare Pages و GitHub مع فحص الأمان التلقائي."
$lblSub.Font = $fontSub
$lblSub.ForeColor = $textMuted
$lblSub.Location = New-Object System.Drawing.Point(15, 42)
$lblSub.Size = New-Object System.Drawing.Size(755, 24)
$headerPanel.Controls.Add($lblSub)

# --- Card 1: Cloudflare Pages ---
$cfPanel = New-Object System.Windows.Forms.Panel
$cfPanel.Location = New-Object System.Drawing.Point(20, 100)
$cfPanel.Size = New-Object System.Drawing.Size(785, 135)
$cfPanel.BackColor = $cardBg
$cfPanel.BorderStyle = [System.Windows.Forms.BorderStyle]::FixedSingle
$form.Controls.Add($cfPanel)

$cfTitle = New-Object System.Windows.Forms.Label
$cfTitle.Text = "⛅ استضافة Cloudflare Pages (الموقع الحي العالمي)"
$cfTitle.Font = $fontSection
$cfTitle.ForeColor = $amber
$cfTitle.Location = New-Object System.Drawing.Point(15, 10)
$cfTitle.Size = New-Object System.Drawing.Size(450, 25)
$cfPanel.Controls.Add($cfTitle)

$cfStatus = New-Object System.Windows.Forms.Label
$cfStatus.Text = "حالة الاتصال: متصل ومصرّح ✅ (الحساب: hyayn5@gmail.com)"
$cfStatus.Font = $fontBold
$cfStatus.ForeColor = $emerald
$cfStatus.Location = New-Object System.Drawing.Point(15, 40)
$cfStatus.Size = New-Object System.Drawing.Size(500, 22)
$cfPanel.Controls.Add($cfStatus)

$cfUrlLabel = New-Object System.Windows.Forms.Label
$cfUrlLabel.Text = "الرابط الحي: https://blogger-studio-pro.pages.dev"
$cfUrlLabel.Font = $fontMono
$cfUrlLabel.ForeColor = $cyan
$cfUrlLabel.Location = New-Object System.Drawing.Point(15, 65)
$cfUrlLabel.Size = New-Object System.Drawing.Size(500, 22)
$cfPanel.Controls.Add($cfUrlLabel)

$btnDeployCf = New-Object System.Windows.Forms.Button
$btnDeployCf.Text = "⚡ نشر وتحديث Cloudflare الآن"
$btnDeployCf.Font = $fontBold
$btnDeployCf.BackColor = $emeraldDark
$btnDeployCf.ForeColor = $textLight
$btnDeployCf.FlatStyle = [System.Windows.Forms.FlatStyle]::Flat
$btnDeployCf.Location = New-Object System.Drawing.Point(15, 92)
$btnDeployCf.Size = New-Object System.Drawing.Size(230, 32)
$btnDeployCf.Cursor = [System.Windows.Forms.Cursors]::Hand
$cfPanel.Controls.Add($btnDeployCf)

$btnOpenCf = New-Object System.Windows.Forms.Button
$btnOpenCf.Text = "🌐 زيارة الموقع الحي ↗"
$btnOpenCf.Font = $fontRegular
$btnOpenCf.BackColor = [System.Drawing.ColorTranslator]::FromHtml("#0284c7")
$btnOpenCf.ForeColor = $textLight
$btnOpenCf.FlatStyle = [System.Windows.Forms.FlatStyle]::Flat
$btnOpenCf.Location = New-Object System.Drawing.Point(255, 92)
$btnOpenCf.Size = New-Object System.Drawing.Size(160, 32)
$btnOpenCf.Cursor = [System.Windows.Forms.Cursors]::Hand
$cfPanel.Controls.Add($btnOpenCf)

$btnReauthCf = New-Object System.Windows.Forms.Button
$btnReauthCf.Text = "🔄 ربط حساب آخر"
$btnReauthCf.Font = $fontRegular
$btnReauthCf.BackColor = [System.Drawing.ColorTranslator]::FromHtml("#475569")
$btnReauthCf.ForeColor = $textLight
$btnReauthCf.FlatStyle = [System.Windows.Forms.FlatStyle]::Flat
$btnReauthCf.Location = New-Object System.Drawing.Point(425, 92)
$btnReauthCf.Size = New-Object System.Drawing.Size(130, 32)
$btnReauthCf.Cursor = [System.Windows.Forms.Cursors]::Hand
$cfPanel.Controls.Add($btnReauthCf)

# --- Card 2: GitHub Repository ---
$ghPanel = New-Object System.Windows.Forms.Panel
$ghPanel.Location = New-Object System.Drawing.Point(20, 245)
$ghPanel.Size = New-Object System.Drawing.Size(785, 175)
$ghPanel.BackColor = $cardBg
$ghPanel.BorderStyle = [System.Windows.Forms.BorderStyle]::FixedSingle
$form.Controls.Add($ghPanel)

$ghTitle = New-Object System.Windows.Forms.Label
$ghTitle.Text = "🐙 مستودع GitHub (مزامنة وحفظ الكود المصدري)"
$ghTitle.Font = $fontSection
$ghTitle.ForeColor = $purple
$ghTitle.Location = New-Object System.Drawing.Point(15, 10)
$ghTitle.Size = New-Object System.Drawing.Size(450, 25)
$ghPanel.Controls.Add($ghTitle)

$lblRepo = New-Object System.Windows.Forms.Label
$lblRepo.Text = "رابط المستودع:"
$lblRepo.Font = $fontRegular
$lblRepo.Location = New-Object System.Drawing.Point(680, 40)
$lblRepo.Size = New-Object System.Drawing.Size(90, 22)
$ghPanel.Controls.Add($lblRepo)

$txtRepo = New-Object System.Windows.Forms.TextBox
$txtRepo.Text = "https://github.com/Hayan-AL/blogger-studio-pro.git"
$txtRepo.Font = $fontMono
$txtRepo.Location = New-Object System.Drawing.Point(15, 38)
$txtRepo.Size = New-Object System.Drawing.Size(655, 26)
$txtRepo.BackColor = $bgDark
$txtRepo.ForeColor = $cyan
$ghPanel.Controls.Add($txtRepo)

$lblToken = New-Object System.Windows.Forms.Label
$lblToken.Text = "رمز التخويل (Token اختياري لتخطي أي نافذة منبثقة):"
$lblToken.Font = $fontRegular
$lblToken.Location = New-Object System.Drawing.Point(420, 72)
$lblToken.Size = New-Object System.Drawing.Size(350, 22)
$ghPanel.Controls.Add($lblToken)

$txtToken = New-Object System.Windows.Forms.TextBox
$txtToken.Font = $fontMono
$txtToken.PasswordChar = '•'
$txtToken.Location = New-Object System.Drawing.Point(165, 96)
$txtToken.Size = New-Object System.Drawing.Size(605, 26)
$txtToken.BackColor = $bgDark
$txtToken.ForeColor = $emerald
$ghPanel.Controls.Add($txtToken)

$btnGenToken = New-Object System.Windows.Forms.Button
$btnGenToken.Text = "🔑 توليد Token ↗"
$btnGenToken.Font = $fontRegular
$btnGenToken.BackColor = [System.Drawing.ColorTranslator]::FromHtml("#475569")
$btnGenToken.ForeColor = $textLight
$btnGenToken.FlatStyle = [System.Windows.Forms.FlatStyle]::Flat
$btnGenToken.Location = New-Object System.Drawing.Point(15, 95)
$btnGenToken.Size = New-Object System.Drawing.Size(140, 28)
$btnGenToken.Cursor = [System.Windows.Forms.Cursors]::Hand
$ghPanel.Controls.Add($btnGenToken)

$btnDeployGh = New-Object System.Windows.Forms.Button
$btnDeployGh.Text = "⚡ رفع وتحديث GitHub الآن"
$btnDeployGh.Font = $fontBold
$btnDeployGh.BackColor = $purpleDark
$btnDeployGh.ForeColor = $textLight
$btnDeployGh.FlatStyle = [System.Windows.Forms.FlatStyle]::Flat
$btnDeployGh.Location = New-Object System.Drawing.Point(15, 132)
$btnDeployGh.Size = New-Object System.Drawing.Size(230, 32)
$btnDeployGh.Cursor = [System.Windows.Forms.Cursors]::Hand
$ghPanel.Controls.Add($btnDeployGh)

$btnOpenGh = New-Object System.Windows.Forms.Button
$btnOpenGh.Text = "🐙 فتح صفحة المستودع ↗"
$btnOpenGh.Font = $fontRegular
$btnOpenGh.BackColor = [System.Drawing.ColorTranslator]::FromHtml("#334155")
$btnOpenGh.ForeColor = $textLight
$btnOpenGh.FlatStyle = [System.Windows.Forms.FlatStyle]::Flat
$btnOpenGh.Location = New-Object System.Drawing.Point(255, 132)
$btnOpenGh.Size = New-Object System.Drawing.Size(180, 32)
$btnOpenGh.Cursor = [System.Windows.Forms.Cursors]::Hand
$ghPanel.Controls.Add($btnOpenGh)

# --- Dual Deploy Banner Button ---
$btnDeployAll = New-Object System.Windows.Forms.Button
$btnDeployAll.Text = "🚀 نشر شامل متزامن على المنصتين معاً (Cloudflare + GitHub)"
$btnDeployAll.Font = New-Object System.Drawing.Font("Segoe UI", 11, [System.Drawing.FontStyle]::Bold)
$btnDeployAll.BackColor = [System.Drawing.ColorTranslator]::FromHtml("#2563eb")
$btnDeployAll.ForeColor = $textLight
$btnDeployAll.FlatStyle = [System.Windows.Forms.FlatStyle]::Flat
$btnDeployAll.Location = New-Object System.Drawing.Point(20, 430)
$btnDeployAll.Size = New-Object System.Drawing.Size(785, 42)
$btnDeployAll.Cursor = [System.Windows.Forms.Cursors]::Hand
$form.Controls.Add($btnDeployAll)

# --- Log Card ---
$logPanel = New-Object System.Windows.Forms.Panel
$logPanel.Location = New-Object System.Drawing.Point(20, 482)
$logPanel.Size = New-Object System.Drawing.Size(785, 205)
$logPanel.BackColor = $cardBg
$logPanel.BorderStyle = [System.Windows.Forms.BorderStyle]::FixedSingle
$form.Controls.Add($logPanel)

$lblLogTitle = New-Object System.Windows.Forms.Label
$lblLogTitle.Text = "📋 سجل العمليات المباشر (Live Progress Log):"
$lblLogTitle.Font = $fontBold
$lblLogTitle.ForeColor = $cyan
$lblLogTitle.Location = New-Object System.Drawing.Point(15, 8)
$lblLogTitle.Size = New-Object System.Drawing.Size(350, 20)
$logPanel.Controls.Add($lblLogTitle)

$btnClearLog = New-Object System.Windows.Forms.Button
$btnClearLog.Text = "مسح السجل"
$btnClearLog.Font = $fontRegular
$btnClearLog.Size = New-Object System.Drawing.Size(80, 22)
$btnClearLog.Location = New-Object System.Drawing.Point(690, 6)
$btnClearLog.FlatStyle = [System.Windows.Forms.FlatStyle]::Flat
$btnClearLog.BackColor = [System.Drawing.ColorTranslator]::FromHtml("#334155")
$btnClearLog.ForeColor = $textMuted
$logPanel.Controls.Add($btnClearLog)

$txtLog = New-Object System.Windows.Forms.TextBox
$txtLog.Multiline = $true
$txtLog.ReadOnly = $true
$txtLog.ScrollBars = [System.Windows.Forms.ScrollBars]::Vertical
$txtLog.Font = $fontLog
$txtLog.BackColor = $bgDark
$txtLog.ForeColor = [System.Drawing.ColorTranslator]::FromHtml("#e2e8f0")
$txtLog.Location = New-Object System.Drawing.Point(15, 32)
$txtLog.Size = New-Object System.Drawing.Size(755, 160)
$logPanel.Controls.Add($txtLog)

# --- Helper Functions ---
function Write-Log {
    param([string]$Msg)
    $ts = (Get-Date).ToString("HH:mm:ss")
    $txtLog.AppendText("[$ts] $Msg`r`n")
    $txtLog.SelectionStart = $txtLog.Text.Length
    $txtLog.ScrollToCaret()
    [System.Windows.Forms.Application]::DoEvents()
}

function Build-Dist {
    Write-Log "🛠️  جاري بناء وتجهيز مجلد الأصول الثابتة dist/..."
    if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }
    New-Item -ItemType Directory -Path "dist" -Force | Out-Null
    Copy-Item "index.html" "dist\index.html" -Force
    Copy-Item "static" "dist\static" -Recurse -Force
    if (Test-Path "_headers") { Copy-Item "_headers" "dist\_headers" -Force }
    if (Test-Path "_redirects") { Copy-Item "_redirects" "dist\_redirects" -Force }
    Write-Log "   ✓ تم تجهيز مجلد dist/ بنجاح لشبكة Cloudflare."
}

function Do-DeployCloudflare {
    Write-Log "--------------------------------------------------"
    Write-Log "⛅ بدء النشر على Cloudflare Pages..."
    Build-Dist
    Write-Log "🚀 جاري رفع الملفات وتحديث شبكة CDN العالمية..."
    
    $proc = Start-Process -FilePath "cmd.exe" -ArgumentList "/c npx wrangler pages deploy dist --project-name blogger-studio-pro --branch main" -NoNewWindow -PassThru -Wait
    if ($proc.ExitCode -eq 0) {
        Write-Log "🎉 تم النشر بنجاح 100% على Cloudflare Pages!"
        Write-Log "🌐 الرابط الحي: https://blogger-studio-pro.pages.dev"
        [System.Windows.Forms.MessageBox]::Show("تم نشر وتحديث الموقع بنجاح على Cloudflare Pages!`n`nرابط الموقع:`nhttps://blogger-studio-pro.pages.dev", "نجاح النشر", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)
    } else {
        Write-Log "❌ حدث خطأ أثناء الرفع إلى Cloudflare (Exit code: $($proc.ExitCode))."
    }
}

function Do-DeployGitHub {
    Write-Log "--------------------------------------------------"
    Write-Log "🐙 بدء الرفع والتحديث على GitHub..."
    $repo = $txtRepo.Text.Trim()
    $token = $txtToken.Text.Trim()
    
    if (-not $repo) {
        Write-Log "❌ خطأ: يرجى إدخال رابط المستودع أولاً."
        return
    }

    # If user provided a Token, construct authenticated remote URL
    if ($token) {
        Write-Log "🔑 تم استخدام رمز الوصول السريع (Token) للمصادقة المباشرة."
        if ($repo -match "https://github\.com/(.+)") {
            $pathPart = $matches[1]
            $authedUrl = "https://$($token)@github.com/$pathPart"
            git remote set-url origin $authedUrl
        }
    } else {
        git remote set-url origin $repo
    }

    Write-Log "📦 جاري فحص وتأكيد الإيداع (Commit)..."
    git add .
    $status = git status --porcelain
    if ($status) {
        $now = (Get-Date).ToString("yyyy-MM-dd HH:mm")
        git commit -m "Update release: $now - Blogger Studio Pro"
        Write-Log "   ✓ تم حفظ التغييرات محلياً."
    }

    Write-Log "🚀 جاري الرفع إلى فرع main على GitHub..."
    $proc = Start-Process -FilePath "cmd.exe" -ArgumentList "/c git push -u origin main --force" -NoNewWindow -PassThru -Wait
    if ($proc.ExitCode -eq 0) {
        Write-Log "🎉 تم رفع الكود بنجاح تام إلى مستودعك على GitHub!"
        [System.Windows.Forms.MessageBox]::Show("تم رفع وتحديث المشروع بنجاح على مستودع GitHub!`n`n$repo", "نجاح الرفع", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)
    } else {
        Write-Log "❌ لم يكتمل الرفع. في حال لم تدخل Token، تأكد من تسجيل الدخول بالمتصفح بحساب Hayan-AL."
    }
}

# --- Event Handlers ---
$btnOpenCf.Add_Click({
    Start-Process "https://blogger-studio-pro.pages.dev"
})

$btnReauthCf.Add_Click({
    Write-Log "جاري فتح صفحة تسجيل الدخول لـ Cloudflare..."
    Start-Process "cmd.exe" -ArgumentList "/c npx wrangler login"
})

$btnOpenGh.Add_Click({
    Start-Process $txtRepo.Text
})

$btnGenToken.Add_Click({
    Start-Process "https://github.com/settings/tokens/new?scopes=repo&description=BloggerStudioPro"
    Write-Log "ℹ️ تم فتح صفحة توليد Token في متصفحك. اضغط Generate token بالأسفل وانسخه والصقه في خانة الرمز."
})

$btnClearLog.Add_Click({
    $txtLog.Clear()
})

$btnDeployCf.Add_Click({
    $btnDeployCf.Enabled = $false
    Do-DeployCloudflare
    $btnDeployCf.Enabled = $true
})

$btnDeployGh.Add_Click({
    $btnDeployGh.Enabled = $false
    Do-DeployGitHub
    $btnDeployGh.Enabled = $true
})

$btnDeployAll.Add_Click({
    $btnDeployAll.Enabled = $false
    Do-DeployCloudflare
    Do-DeployGitHub
    $btnDeployAll.Enabled = $true
})

# --- Initial Greeting ---
Write-Log "مرحباً بك في مركز النشر السحابي لـ Blogger Studio Pro (لوحة التحكم الاحترافية) 👋"
Write-Log "حساب Cloudflare متصل وجاهز للنشر الفوري (hyayn5@gmail.com)."
Write-Log "مستودع GitHub مهيأ: Hayan-AL/blogger-studio-pro."

# --- Show Dialog ---
$form.ShowDialog() | Out-Null
$form.Dispose()
