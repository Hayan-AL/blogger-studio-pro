# Blogger Studio Server Control Center - لوحة التحكم الاحترافية (Port 8000)
# Modeled after Hayan Server Control Center Standard

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Host.UI.RawUI.WindowTitle = "Blogger Studio Server Control Center - لوحة التحكم الاحترافية (Port 8000)"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
if (-not $ScriptDir) { $ScriptDir = (Get-Location).Path }
Set-Location $ScriptDir

function Open-UrlWithChoice {
    param([string]$Url)
    Write-Host ""
    Write-Host "=========================================================================" -ForegroundColor Cyan
    Write-Host "  Select a browser to open URL:" -ForegroundColor Yellow
    Write-Host "  $Url" -ForegroundColor White
    Write-Host "=========================================================================" -ForegroundColor Cyan
    Write-Host "  [1] Default Windows Browser"
    Write-Host "  [2] Google Chrome"
    Write-Host "  [3] Microsoft Edge"
    Write-Host "  [4] Mozilla Firefox"
    Write-Host "  [5] Brave Browser"
    Write-Host "  [6] Windows 'Open With' Dialog"
    Write-Host "  [0] Skip (Do not open browser)"
    Write-Host "=========================================================================" -ForegroundColor Cyan
    $b = Read-Host "Enter browser choice [1-6 or 0]"

    if ($b -eq "1") {
        Start-Process $Url
    } elseif ($b -eq "2") {
        try { Start-Process "chrome.exe" $Url } catch { Start-Process $Url }
    } elseif ($b -eq "3") {
        try { Start-Process "msedge.exe" $Url } catch { Start-Process $Url }
    } elseif ($b -eq "4") {
        try { Start-Process "firefox.exe" $Url } catch { Start-Process $Url }
    } elseif ($b -eq "5") {
        try { Start-Process "brave.exe" $Url } catch { Start-Process $Url }
    } elseif ($b -eq "6") {
        $tmp = Join-Path $env:TEMP "blogger_studio_link.url"
        "[InternetShortcut]`r`nURL=$Url" | Set-Content -Path $tmp -Encoding ascii
        try { Start-Process "openwith.exe" $tmp } catch { Start-Process $Url }
    } elseif ($b -eq "0") {
        Write-Host "Browser launch skipped." -ForegroundColor Gray
    } else {
        Write-Host "Default browser selected." -ForegroundColor Yellow
        Start-Process $Url
    }
}

function Get-ServerListening {
    return Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
}

function Stop-ServerPort {
    $conns = Get-ServerListening
    if ($conns) {
        $pids = $conns.OwningProcess | Select-Object -Unique
        foreach ($p in $pids) {
            try {
                Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
                Write-Host "Stopped process on port 8000 (PID: $p)" -ForegroundColor Yellow
            } catch {
                Write-Host "Could not stop PID $p : $_" -ForegroundColor Red
            }
        }
    } else {
        Write-Host "No process is listening on port 8000." -ForegroundColor Gray
    }
}

function Show-Header {
    Clear-Host
    Write-Host "=========================================================================" -ForegroundColor Cyan
    Write-Host "            BLOGGER STUDIO SERVER CONTROL CENTER - لوحة التحكم الاحترافية (PORT 8000)             " -ForegroundColor Yellow
    Write-Host "=========================================================================" -ForegroundColor Cyan
    Write-Host ""

    $conn = Get-ServerListening
    if ($conn) {
        $pidNum = $conn[0].OwningProcess
        $proc = Get-Process -Id $pidNum -ErrorAction SilentlyContinue
        $pName = if ($proc) { $proc.ProcessName } else { "python" }
        Write-Host "  Server Status : [ RUNNING on port 8000 (PID: $pidNum, $pName) ]" -ForegroundColor Green
    } else {
        Write-Host "  Server Status : [ STOPPED ]" -ForegroundColor Red
    }

    Write-Host ""
    Write-Host "  Quick Access URLs:" -ForegroundColor DarkCyan
    Write-Host "    - Blogger Studio Pro Dashboard  : http://localhost:8000/"
    Write-Host "    - Live Blogger Website      : https://www.blogger.com/"
    Write-Host "    - Blogger Posts Feed API    : http://localhost:8000/api/posts"
    Write-Host "    - Blog Analytics & Stats    : http://localhost:8000/api/stats"
    Write-Host "    - Theme Management API      : http://localhost:8000/api/theme"
    Write-Host "    - Backups & Snapshots API   : http://localhost:8000/api/backups"
    Write-Host ""
    Write-Host "  -------------------------------------------------------------------------" -ForegroundColor DarkGray
    Write-Host "   [1] Start Blogger Studio Studio Server (Port 8000)"
    Write-Host "   [2] Open Blogger Studio Dashboard in Browser"
    Write-Host "   [3] Open Live Blogger Website in Browser"
    Write-Host "   [4] Health Check & Diagnostics (API Status, Posts, Response Time)"
    Write-Host "   [5] Create Full Local Backup (Theme XML + Posts JSON)"
    Write-Host "   [6] Deploy Theme to Blogger Live (via Edge Automation)"
    Write-Host "   [7] Restart Server"
    Write-Host "   [8] View Recent Backups & Archive"
    Write-Host "   [9] Stop Server (Kill Port 8000)"
    Write-Host "   [0] Exit"
    Write-Host "  -------------------------------------------------------------------------" -ForegroundColor DarkGray
    Write-Host ""
}

while ($true) {
    Show-Header
    $choice = Read-Host "Select an option [0-9]"

    if ($choice -eq "1") {
        Write-Host ""
        $conn = Get-ServerListening
        if ($conn) {
            Write-Host "[!] Server is already running on port 8000." -ForegroundColor Yellow
            Open-UrlWithChoice "http://localhost:8000/"
        } else {
            Write-Host "[*] Starting Blogger Studio Studio Server in a new window..." -ForegroundColor Cyan
            Start-Process powershell.exe -WorkingDirectory $ScriptDir -ArgumentList "-NoProfile -ExecutionPolicy Bypass -NoExit -Command python run.py --no-browser" -WindowStyle Normal

            Write-Host "[*] Waiting for server initialization..." -ForegroundColor Gray
            Start-Sleep -Seconds 3

            try {
                $h = Invoke-RestMethod "http://localhost:8000/api/stats" -TimeoutSec 5
                Write-Host "[OK] Blogger Studio Studio is online and healthy!" -ForegroundColor Green
            } catch {
                Write-Host "[!] Server is starting up. Check the opened server window." -ForegroundColor Yellow
            }

            Open-UrlWithChoice "http://localhost:8000/"
        }
        Write-Host ""
        Read-Host "Press Enter to continue..."
    }
    elseif ($choice -eq "2") {
        Open-UrlWithChoice "http://localhost:8000/"
    }
    elseif ($choice -eq "3") {
        Open-UrlWithChoice "https://www.blogger.com/"
    }
    elseif ($choice -eq "4") {
        Write-Host ""
        Write-Host "Pinging http://localhost:8000/api/stats ..." -ForegroundColor Cyan
        $sw = [System.Diagnostics.Stopwatch]::StartNew()
        try {
            $m = Invoke-RestMethod "http://localhost:8000/api/stats" -TimeoutSec 5
            $sw.Stop()
            Write-Host "  Server Status  : " -NoNewline; Write-Host "ONLINE (200 OK)" -ForegroundColor Green
            Write-Host "  Response Time  : " -NoNewline; Write-Host "$($sw.ElapsedMilliseconds) ms" -ForegroundColor Yellow
            Write-Host "  Total Posts    : $($m.total_posts)" -ForegroundColor White
            Write-Host "  Arabic Posts   : $($m.arabic_posts)" -ForegroundColor White
            Write-Host "  English Posts  : $($m.english_posts)" -ForegroundColor White
            Write-Host "  Last Sync Time : $($m.last_sync)" -ForegroundColor Gray
        } catch {
            Write-Host "  [ERROR] Server is unreachable or not responding on port 8000." -ForegroundColor Red
        }
        Write-Host ""
        Read-Host "Press Enter to continue..."
    }
    elseif ($choice -eq "5") {
        Write-Host ""
        Write-Host "[*] Creating full snapshot of Theme and Posts..." -ForegroundColor Cyan
        try {
            $conn = Get-ServerListening
            if ($conn) {
                $res = Invoke-RestMethod -Uri "http://localhost:8000/api/backups/create" -Method Post -TimeoutSec 10
                Write-Host "[OK] $($res.message)" -ForegroundColor Green
                Write-Host "     Theme File : $($res.theme_file)" -ForegroundColor White
                Write-Host "     Posts File : $($res.posts_file)" -ForegroundColor White
            } else {
                # Fallback to direct Python runner if server is offline
                python -c "from app.main import api_create_backup; res = api_create_backup(); print('[OK]', res['message']); print('     Theme File:', res['theme_file']); print('     Posts File:', res['posts_file'])"
            }
        } catch {
            Write-Host "[ERROR] Backup failed: $_" -ForegroundColor Red
        }
        Write-Host ""
        Read-Host "Press Enter to continue..."
    }
    elseif ($choice -eq "6") {
        Write-Host ""
        $confirm = Read-Host "Are you sure you want to deploy the local theme to live Blogger via Edge automation? (y/n)"
        if ($confirm -eq "y" -or $confirm -eq "Y") {
            Write-Host "[*] Initiating deployment to Blogger..." -ForegroundColor Cyan
            try {
                $conn = Get-ServerListening
                if ($conn) {
                    $res = Invoke-RestMethod -Uri "http://localhost:8000/api/theme/deploy" -Method Post -TimeoutSec 15
                    Write-Host "[OK] $($res.message)" -ForegroundColor Green
                } else {
                    python -c "from app.automation import deploy_theme; res = deploy_theme(); print(res.get('message'))"
                }
            } catch {
                Write-Host "[ERROR] Deployment error: $_" -ForegroundColor Red
            }
        } else {
            Write-Host "Deployment cancelled." -ForegroundColor Yellow
        }
        Write-Host ""
        Read-Host "Press Enter to continue..."
    }
    elseif ($choice -eq "7") {
        Write-Host ""
        Write-Host "[*] Stopping existing server process on port 8000..." -ForegroundColor Cyan
        Stop-ServerPort
        Start-Sleep -Seconds 2

        Write-Host "[*] Restarting Blogger Studio Studio Server in a new window..." -ForegroundColor Cyan
        Start-Process powershell.exe -WorkingDirectory $ScriptDir -ArgumentList "-NoProfile -ExecutionPolicy Bypass -NoExit -Command python run.py --no-browser" -WindowStyle Normal
        Start-Sleep -Seconds 3

        try {
            $h = Invoke-RestMethod "http://localhost:8000/api/stats" -TimeoutSec 5
            Write-Host "[OK] Server restarted successfully!" -ForegroundColor Green
        } catch {
            Write-Host "[!] Server is starting up..." -ForegroundColor Yellow
        }

        Open-UrlWithChoice "http://localhost:8000/"
        Write-Host ""
        Read-Host "Press Enter to continue..."
    }
    elseif ($choice -eq "8") {
        Write-Host ""
        Write-Host "Local Backups Archive in data\backups:" -ForegroundColor Cyan
        Write-Host "-------------------------------------------------------------------------" -ForegroundColor DarkGray
        $backupDir = Join-Path $ScriptDir "data\backups"
        if (Test-Path $backupDir) {
            $files = Get-ChildItem -Path $backupDir | Where-Object { $_.Extension -in ".xml", ".json" } | Sort-Object LastWriteTime -Descending
            if ($files) {
                $files | Select-Object Name, @{Name="Size (KB)"; Expression={[math]::Round($_.Length/1KB, 1)}}, LastWriteTime | Format-Table -AutoSize
            } else {
                Write-Host "No backup files found yet." -ForegroundColor Gray
            }
        } else {
            Write-Host "Backup directory does not exist yet." -ForegroundColor Gray
        }
        Write-Host ""
        Read-Host "Press Enter to continue..."
    }
    elseif ($choice -eq "9") {
        Write-Host ""
        Write-Host "[*] Stopping server on port 8000..." -ForegroundColor Cyan
        Stop-ServerPort
        Write-Host ""
        Read-Host "Press Enter to continue..."
    }
    elseif ($choice -eq "0") {
        Write-Host "Exiting Blogger Studio Server Control Center - لوحة التحكم الاحترافية. Goodbye!" -ForegroundColor Cyan
        exit 0
    }
    else {
        Write-Host "Invalid option. Please choose a number between 0 and 9." -ForegroundColor Red
        Start-Sleep -Seconds 1
    }
}
