<#
.SYNOPSIS
    One-command EMR4 local dev stack launcher.

.DESCRIPTION
    Brings up: Postgres (Docker), FastAPI/uvicorn, ngrok tunnel (reserved domain),
    and the webpack dev-server. Idempotent -- re-running skips already-running services.

    CROSS-FILE INVARIANT: $NgrokDomain must match NGROK_URL in sync_taskpane.py.

.PARAMETER Down
    Tear down running app processes (uvicorn, ngrok, dev-server). Leaves Postgres up.

.PARAMETER NoNgrok
    Skip starting the ngrok tunnel (e.g. if you know it's already bound correctly).

.PARAMETER NoDevServer
    Skip starting the webpack dev-server on port 3000.

.PARAMETER LiveAiSurface
    Select keyless live-AI ADC/env for the surface being tested.
    Taskpane = Scribe/Copilot project. Diary = Bernie project. None = no live
    ADC switch.

.PARAMETER SkipAdcLogin
    With -LiveAiSurface, set project/env only and do not recreate ADC. Use when
    ADC is already known to point at the matching service account.

.EXAMPLE
    .\run_dev.ps1                        # Start everything
    .\run_dev.ps1 -Down                  # Stop app processes (leave Postgres)
    .\run_dev.ps1 -NoDevServer -NoNgrok  # Backend only
    .\run_dev.ps1 -LiveAiSurface Taskpane # Live Scribe/Copilot test
    .\run_dev.ps1 -LiveAiSurface Diary    # Live Bernie/diary test
#>

param(
    [switch]$Down,
    [switch]$NoDevServer,
    [switch]$NoNgrok,
    [ValidateSet("None", "Taskpane", "Diary")]
    [string]$LiveAiSurface = "None",
    [switch]$SkipAdcLogin
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"   # native-exe exit codes don't throw; we check manually

# -- Configuration -------------------------------------------------------------
# CROSS-FILE INVARIANT: $NgrokDomain must match NGROK_URL in sync_taskpane.py
$BackendPort   = 8001
$DbPort        = 5434
$DevServerPort = 3000
$NgrokApiPort  = 4040   # ngrok's local API / web UI

# INVARIANT: keep in sync with the NGROK_URL line in sync_taskpane.py
$NgrokDomain   = "property-cinch-backfield.ngrok-free.dev"

$DbContainer   = "gp-pms-postgres"
$Root          = $PSScriptRoot
$Venv          = Join-Path $Root ".venv\Scripts\Activate.ps1"
$SidebarPath   = Join-Path $Root "EMR4 Sidebar"
$ScribeAdcScript = Join-Path $Root "scripts\use_scribe_adc.ps1"
$BernieAdcScript = Join-Path $Root "scripts\use_bernie_adc.ps1"

# -- Helpers -------------------------------------------------------------------

function Write-Step([string]$msg) {
    Write-Host ""
    Write-Host "  $msg" -ForegroundColor Cyan
}

function Write-Ok([string]$msg)   { Write-Host "  [OK]   $msg" -ForegroundColor Green }
function Write-Warn([string]$msg) { Write-Host "  [WARN] $msg" -ForegroundColor Yellow }
function Write-Err([string]$msg)  { Write-Host "  [ERR]  $msg" -ForegroundColor Red }

function Test-PortListening([int]$Port) {
    return $null -ne (Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue)
}

function Get-PidOnPort([int]$Port) {
    $c = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($c) { return $c.OwningProcess }
    return $null
}

function Wait-ForPort([int]$Port, [int]$TimeoutSec = 30) {
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    while ($sw.Elapsed.TotalSeconds -lt $TimeoutSec) {
        if (Test-PortListening $Port) { return $true }
        Start-Sleep -Milliseconds 500
    }
    return $false
}

function Wait-ForHttp([string]$Url, [int]$TimeoutSec = 30) {
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    while ($sw.Elapsed.TotalSeconds -lt $TimeoutSec) {
        try {
            $r = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
            if ($r -and $r.StatusCode -lt 500) { return $true }
        } catch { }
        Start-Sleep -Milliseconds 750
    }
    return $false
}

function Test-RemoteNgrokDomain([string]$Domain) {
    try {
        $headers = @{ "ngrok-skip-browser-warning" = "1" }
        $r = Invoke-WebRequest -Uri "https://$Domain/health" -Headers $headers -UseBasicParsing -TimeoutSec 4 -ErrorAction Stop
        return ($r -and $r.StatusCode -ge 200 -and $r.StatusCode -lt 500)
    } catch {
        return $false
    }
}

function Show-StatusRow([string]$Name, [bool]$Up, [string]$Detail) {
    $icon  = if ($Up) { "[OK]  " } else { "[WARN]" }
    $color = if ($Up) { "Green" } else { "Yellow" }
    Write-Host ("  {0} {1,-24} {2}" -f $icon, $Name, $Detail) -ForegroundColor $color
}

function Invoke-LiveAiSetup([string]$Surface) {
    if ($Surface -eq "None") {
        Write-Warn "No live AI ADC selected. Scribe/Bernie live provider calls may fail unless configured separately."
        return
    }

    $script = if ($Surface -eq "Taskpane") { $ScribeAdcScript } else { $BernieAdcScript }
    if (-not (Test-Path $script)) {
        Write-Err "Live AI setup script not found: $script"
        exit 1
    }

    $scriptArgs = @()
    if ($SkipAdcLogin) {
        $scriptArgs += "-SkipAdcLogin"
    }

    try {
        & $script @scriptArgs
        if ($LASTEXITCODE -ne 0) {
            Write-Err "Live AI setup script exited with code $LASTEXITCODE"
            exit 1
        }
    } catch {
        Write-Err "Live AI setup failed: $($_.Exception.Message)"
        exit 1
    }
}

function Get-UvicornEnvCommand([string]$Surface) {
    $common = "Remove-Item Env:GOOGLE_APPLICATION_CREDENTIALS -ErrorAction SilentlyContinue; "
    if ($Surface -eq "Taskpane") {
        return $common +
            "`$env:GCP_PROJECT='scribe-emr4-dev'; " +
            "`$env:GOOGLE_CLOUD_PROJECT='scribe-emr4-dev'; " +
            "`$env:GCP_LOCATION='australia-southeast1'; " +
            "`$env:VERTEX_AI_LOCATION='australia-southeast1'; " +
            "Remove-Item Env:BERNIE_AI_PROJECT -ErrorAction SilentlyContinue; " +
            "Remove-Item Env:BERNIE_AI_LOCATION -ErrorAction SilentlyContinue; " +
            "Remove-Item Env:BERNIE_STAFF_PILOT_ENABLED -ErrorAction SilentlyContinue; " +
            "Remove-Item Env:BERNIE_STAFF_PILOT_PRACTICE_IDS -ErrorAction SilentlyContinue; " +
            "Remove-Item Env:BERNIE_STAFF_PILOT_USER_IDS -ErrorAction SilentlyContinue; " +
            "Remove-Item Env:BERNIE_BOOKING_INTERPRETER_PROVIDER -ErrorAction SilentlyContinue; "
    }
    if ($Surface -eq "Diary") {
        return $common +
            "`$env:GCP_PROJECT='bernie-emr4-dev'; " +
            "`$env:GOOGLE_CLOUD_PROJECT='bernie-emr4-dev'; " +
            "`$env:GCP_LOCATION='australia-southeast1'; " +
            "`$env:VERTEX_AI_LOCATION='australia-southeast1'; " +
            "`$env:BERNIE_AI_PROJECT='bernie-emr4-dev'; " +
            "`$env:BERNIE_AI_LOCATION='australia-southeast1'; " +
            "`$env:BERNIE_STAFF_PILOT_ENABLED='true'; " +
            "`$env:BERNIE_STAFF_PILOT_PRACTICE_IDS='d92314e3-aa1d-441e-81a5-f5db5ec22ca0'; " +
            "Remove-Item Env:BERNIE_STAFF_PILOT_USER_IDS -ErrorAction SilentlyContinue; " +
            "`$env:BERNIE_BOOKING_INTERPRETER_PROVIDER='gemini_vertex'; "
    }
    return $common
}

# ==============================================================================
# TEARDOWN (-Down)
# ==============================================================================

if ($Down) {
    Write-Host ""
    Write-Host "  EMR4 -- Stopping dev services" -ForegroundColor DarkCyan
    Write-Host "  --------------------------------" -ForegroundColor DarkCyan

    # uvicorn on port 8001
    $pid8001 = Get-PidOnPort $BackendPort
    if ($pid8001) {
        try { Stop-Process -Id $pid8001 -Force -ErrorAction Stop; Write-Ok "uvicorn (PID $pid8001) stopped" }
        catch { Write-Warn "Could not stop PID $pid8001 on :$BackendPort -- $($_.Exception.Message)" }
    } else {
        Write-Ok "uvicorn -- not running"
    }

    # ngrok (all processes)
    $ng = Get-Process -Name ngrok -ErrorAction SilentlyContinue
    if ($ng) {
        $ng | Stop-Process -Force -ErrorAction SilentlyContinue
        Write-Ok "ngrok stopped ($($ng.Count) process(es))"
    } else {
        Write-Ok "ngrok -- not running"
    }

    # dev-server on port 3000
    $pid3000 = Get-PidOnPort $DevServerPort
    if ($pid3000) {
        try { Stop-Process -Id $pid3000 -Force -ErrorAction Stop; Write-Ok "dev-server (PID $pid3000) stopped" }
        catch { Write-Warn "Could not stop PID $pid3000 on :$DevServerPort -- $($_.Exception.Message)" }
    } else {
        Write-Ok "dev-server -- not running"
    }

    Write-Host ""
    Write-Warn "Postgres container left running (restart: unless-stopped)."
    Write-Host "  To stop it: docker stop $DbContainer" -ForegroundColor Gray
    Write-Host ""
    exit 0
}

# ==============================================================================
# STARTUP
# ==============================================================================

Write-Host ""
Write-Host "  =======================================================" -ForegroundColor Cyan
Write-Host "    EMR4 Centaur -- Dev Stack Launcher" -ForegroundColor Cyan
Write-Host "  =======================================================" -ForegroundColor Cyan

# -- 1. Pre-flight -------------------------------------------------------------

Write-Step "1/6  Pre-flight checks..."

# venv
if (-not (Test-Path $Venv)) {
    Write-Err "Python venv not found at: $Venv"
    Write-Host "  Create it: python -m venv .venv  then  pip install -r requirements.txt" -ForegroundColor Gray
    exit 1
}
Write-Ok "Python venv present"

# Docker
docker ps | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Err "Docker is not responding -- start Docker Desktop first"
    exit 1
}
Write-Ok "Docker running"

# ngrok on PATH (unless skipped)
if (-not $NoNgrok) {
    if (-not (Get-Command ngrok -ErrorAction SilentlyContinue)) {
        Write-Err "ngrok not found on PATH -- install from https://ngrok.com/download"
        exit 1
    }
    Write-Ok "ngrok on PATH"
}

# .env (dev defaults exist in config.py, so a warning is enough)
if (-not (Test-Path (Join-Path $Root ".env"))) {
    Write-Warn ".env absent -- uvicorn uses config.py defaults (insecure JWT in dev)"
} else {
    Write-Ok ".env present"
}

# AI auth posture
if (Test-Path (Join-Path $Root "gcp-key.json")) {
    Write-Warn "gcp-key.json exists but run_dev no longer uses JSON keys for live AI."
} else {
    Write-Ok "No local gcp-key.json dependency"
}

# npm (only if dev-server requested)
if (-not $NoDevServer) {
    if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
        Write-Warn "npm not found -- skipping dev-server (use -NoDevServer to suppress this)"
        $NoDevServer = $true
    } else {
        Write-Ok "npm present"
    }
}

# -- 2. Live AI ADC/env --------------------------------------------------------

Write-Step "2/6  Live AI ADC/env selection..."
Invoke-LiveAiSetup $LiveAiSurface

# -- 3. Postgres ---------------------------------------------------------------

Write-Step "3/6  Postgres ($DbContainer on port $DbPort)..."

$running = docker ps --filter "name=$DbContainer" --filter "status=running" --format "{{.Names}}"
if ($running -match $DbContainer) {
    Write-Ok "Already running"
} else {
    Write-Host "  Starting container '$DbContainer'..." -ForegroundColor Gray
    docker start $DbContainer | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Warn "docker start failed -- falling back to docker compose up -d"
        docker compose up -d | Out-Null
    }
    if (Wait-ForPort $DbPort 25) {
        Write-Ok "Postgres ready on :$DbPort"
    } else {
        Write-Err "Postgres did not bind :$DbPort within 25 s"
        exit 1
    }
}

# -- 4. uvicorn ----------------------------------------------------------------

Write-Step "4/6  FastAPI / uvicorn (port $BackendPort)..."

if (Test-PortListening $BackendPort) {
    Write-Warn "Port $BackendPort already in use -- skipping (uvicorn may already be running)"
} else {
    # Build the command string. Single-quote path literals so spaces in $Root
    # are handled correctly when the string is evaluated in the new window.
    $uvEnvCmd = Get-UvicornEnvCommand $LiveAiSurface
    $uvCmd = "Set-Location '$Root'; . '$Venv'; $uvEnvCmd uvicorn app.main:app --reload --port $BackendPort"
    Start-Process powershell -ArgumentList "-NoProfile", "-NoExit", "-Command", $uvCmd `
        -WindowStyle Normal

    Write-Host "  Waiting for /docs to respond..." -ForegroundColor Gray
    if (Wait-ForHttp "http://127.0.0.1:$BackendPort/docs" 35) {
        Write-Ok "uvicorn ready at http://127.0.0.1:$BackendPort"
    } else {
        Write-Warn "uvicorn window opened but /docs did not respond in 35 s -- check its window"
    }
}

# -- 5. ngrok ------------------------------------------------------------------

if (-not $NoNgrok) {
    Write-Step "5/6  ngrok -> https://$NgrokDomain..."

    if (Test-PortListening $NgrokApiPort) {
        # ngrok already up -- verify the tunnel URL matches (catches the random-domain mistake)
        Write-Host "  ngrok already running -- verifying domain binding..." -ForegroundColor Gray
        try {
            $j   = Invoke-RestMethod "http://127.0.0.1:$NgrokApiPort/api/tunnels" -ErrorAction Stop
            $url = ($j.tunnels | Where-Object { $_.proto -eq "https" } | Select-Object -First 1).public_url
            if ($url -eq "https://$NgrokDomain") {
                Write-Ok "Tunnel confirmed: $url"
            } else {
                Write-Err "ngrok is up but tunnel URL is '$url'"
                Write-Err "Expected: https://$NgrokDomain"
                Write-Host "  Stop ngrok (.\run_dev.ps1 -Down) then re-run." -ForegroundColor Gray
                exit 1
            }
        } catch {
            Write-Warn "Could not query ngrok API -- assuming domain is correct"
        }
    } else {
        Write-Host "  No local ngrok API found -- checking whether the reserved domain is already online..." -ForegroundColor Gray
        if (Test-RemoteNgrokDomain $NgrokDomain) {
            Write-Warn "https://$NgrokDomain is already online, probably from another PC."
            Write-Host "  Skipping local ngrok start. GitHub Pages / Word Online will use that remote backend." -ForegroundColor Gray
            Write-Host "  To expose this PC instead, stop ngrok on the other PC and rerun .\run_dev.ps1 here." -ForegroundColor Gray
        } else {
            $ngCmd = "ngrok http --url=$NgrokDomain $BackendPort"
            Start-Process powershell -ArgumentList "-NoProfile", "-NoExit", "-Command", $ngCmd `
                -WindowStyle Normal

            Write-Host "  Waiting for ngrok API on :$NgrokApiPort..." -ForegroundColor Gray
            if (Wait-ForPort $NgrokApiPort 20) {
                Start-Sleep -Milliseconds 1500   # let the tunnel register before querying
                try {
                    $j   = Invoke-RestMethod "http://127.0.0.1:$NgrokApiPort/api/tunnels" -ErrorAction Stop
                    $url = ($j.tunnels | Where-Object { $_.proto -eq "https" } | Select-Object -First 1).public_url
                    if ($url -eq "https://$NgrokDomain") {
                        Write-Ok "Tunnel confirmed: $url"
                    } else {
                        Write-Err "ngrok started but tunnel URL is '$url'"
                        Write-Err "Expected: https://$NgrokDomain"
                        Write-Host "  Check that this authtoken owns the reserved domain:" -ForegroundColor Gray
                        Write-Host "  https://dashboard.ngrok.com/domains" -ForegroundColor Gray
                        exit 1
                    }
                } catch {
                    Write-Warn "ngrok API appeared but domain could not be verified -- check its window"
                }
            } else {
                Write-Warn "ngrok API did not appear on :$NgrokApiPort within 20 s -- check its window"
            }
        }
    }
} else {
    Write-Step "5/6  ngrok -- skipped (-NoNgrok)"
}

# -- 6. npm dev-server ---------------------------------------------------------

if (-not $NoDevServer) {
    Write-Step "6/6  npm dev-server (localhost:$DevServerPort)..."
    if (Test-PortListening $DevServerPort) {
        Write-Ok "Port $DevServerPort already in use -- skipping"
    } else {
        $npmCmd = "Set-Location '$SidebarPath'; npm run dev-server"
        Start-Process powershell -ArgumentList "-NoProfile", "-NoExit", "-Command", $npmCmd `
            -WindowStyle Normal
        Write-Host "  Webpack bundling (first run may take 10-20 s)..." -ForegroundColor Gray
        if (Wait-ForHttp "https://localhost:$DevServerPort/taskpane.html" 90) {
            Write-Ok "Dev-server ready at https://localhost:$DevServerPort/taskpane.html"
        } else {
            Write-Warn "Dev-server window opened but taskpane.html did not respond in 90 s -- check its window"
        }
    }
} else {
    Write-Step "6/6  npm dev-server -- skipped (-NoDevServer)"
}

# -- Summary -------------------------------------------------------------------

Write-Host ""
Write-Host "  =======================================================" -ForegroundColor Cyan
Write-Host "    EMR4 Dev Stack -- Status" -ForegroundColor Cyan
Write-Host "  =======================================================" -ForegroundColor Cyan
Write-Host ""

Show-StatusRow "Postgres"            (Test-PortListening $DbPort)        "postgresql://127.0.0.1:$DbPort/gp_pms_dev"
Show-StatusRow "FastAPI (uvicorn)"   (Test-PortListening $BackendPort)   "http://127.0.0.1:$BackendPort/docs"
Show-StatusRow "Live AI surface"     ($LiveAiSurface -ne "None")          $LiveAiSurface

if (-not $NoNgrok) {
    Show-StatusRow "ngrok tunnel"    (Test-PortListening $NgrokApiPort)  "https://$NgrokDomain"
}
if (-not $NoDevServer) {
    Show-StatusRow "npm dev-server"  (Wait-ForHttp "https://localhost:$DevServerPort/taskpane.html" 2) "https://localhost:$DevServerPort/taskpane.html"
}

Write-Host ""
Write-Host "  Word Online (GitHub Pages) -> ngrok -> uvicorn on :$BackendPort" -ForegroundColor DarkGray
Write-Host "  After any taskpane deploy: close and reopen the Word document." -ForegroundColor DarkGray
Write-Host "  To stop app processes:     .\run_dev.ps1 -Down" -ForegroundColor DarkGray
Write-Host ""
