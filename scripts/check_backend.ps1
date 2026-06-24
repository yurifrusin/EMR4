<#
.SYNOPSIS
    EMR4 Tier-1 backend fast check (~15 s, no DB required).

.DESCRIPTION
    Runs three sequential checks and exits 1 on the first failure:
      1. Syntax check  -- python -m compileall app/ scripts/ -q
      2. Security scan -- bandit -r app/ -ll -ii -c pyproject.toml
      3. Whitespace    -- git diff --check

    On success prints a reminder of the Tier-2 full-confidence command.

    Prerequisites (dev tools, not in requirements.txt):
      pip install bandit

    Usage:
      .\scripts\check_backend.ps1           # from repo root
      .\scripts\check_backend.ps1 -SkipBandit   # skip security scan (rare)

.PARAMETER SkipBandit
    Skip the bandit security scan (use only when bandit is not installed
    and the check is being run in a context where security scanning is
    handled elsewhere).
#>

param(
    [switch]$SkipBandit
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Python = if (Test-Path ".venv\Scripts\python.exe") {
    ".venv\Scripts\python.exe"
} elseif (Test-Path "..\..\EMR4\.venv\Scripts\python.exe") {
    "..\..\EMR4\.venv\Scripts\python.exe"
} else {
    "python"
}

function Step([string]$Label, [scriptblock]$Body) {
    Write-Host "`n[check] $Label" -ForegroundColor Cyan
    & $Body
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[FAIL]  $Label exited $LASTEXITCODE" -ForegroundColor Red
        exit 1
    }
    Write-Host "[ok]    $Label" -ForegroundColor Green
}

# ── 1. Syntax check (compileall) ──────────────────────────────────────────────
Step "Syntax: compileall app/ scripts/" {
    & $Python -m compileall app/ scripts/ -q
}

# ── 2. Security scan (bandit) ─────────────────────────────────────────────────
if (-not $SkipBandit) {
    Step "Security: bandit -r app/ (medium+/high findings block submit)" {
        & $Python -m bandit -r app/ -ll -ii -c pyproject.toml
    }
} else {
    Write-Host "`n[skip]  bandit (-SkipBandit flag set)" -ForegroundColor Yellow
}

# ── 3. Whitespace check ────────────────────────────────────────────────────────
Step "Whitespace: git diff --check" {
    git diff --check
}

# ── All Tier-1 checks passed ──────────────────────────────────────────────────
Write-Host "`n[ok] Tier-1 fast checks passed." -ForegroundColor Green
Write-Host "     Tier-2 full confidence (needs DB, ~7 min):"
Write-Host "       $Python -m pytest" -ForegroundColor Cyan
Write-Host "     Focused subset (faster):"
Write-Host "       $Python -m pytest tests/<file>.py" -ForegroundColor Cyan
