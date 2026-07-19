<#
.SYNOPSIS
    Compatibility wrapper for EMR4's canonical verification entry point.

.DESCRIPTION
    Delegates to scripts/verify_repository.py so local checks and CI share
    pinned tools, exact lint scope, timeout semantics, and gate commands.

    Prerequisites:
      python -m pip install -r requirements-dev.txt

    Usage:
      .\scripts\check_backend.ps1
      .\scripts\check_backend.ps1 -SkipBandit

.PARAMETER SkipBandit
    Run only the canonical fast profile. Without this switch, the reviewed
    Bandit profile runs after the fast profile.
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

Step "Canonical fast verification" {
    & $Python scripts\verify_repository.py --profile fast
}

if (-not $SkipBandit) {
    Step "Canonical reviewed Bandit gate" {
        & $Python scripts\verify_repository.py --profile ci-bandit
    }
} else {
    Write-Host "`n[skip]  canonical Bandit profile (-SkipBandit set)" -ForegroundColor Yellow
}

Write-Host "`n[ok] Canonical backend checks passed." -ForegroundColor Green
Write-Host "     Disposable migration lifecycle:"
Write-Host "       $Python scripts\verify_repository.py --profile migration" -ForegroundColor Cyan
