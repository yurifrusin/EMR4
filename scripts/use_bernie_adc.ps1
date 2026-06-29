<#
.SYNOPSIS
    Select keyless Bernie Google ADC for local EMR4 live AI testing.

.DESCRIPTION
    Configures gcloud and Application Default Credentials to impersonate the
    Bernie dev service account. Also sets PowerShell environment variables for
    the current process so child processes, such as uvicorn launched by
    run_dev.ps1, use the Bernie project and australia-southeast1 region.

    This script intentionally removes GOOGLE_APPLICATION_CREDENTIALS from the
    current process so local live tests use ADC impersonation rather than JSON
    service-account keys.

.PARAMETER SkipAdcLogin
    Set environment variables and gcloud's active project, but do not revoke or
    recreate ADC. Use only when ADC is already known to point at this service
    account.
#>

param(
    [switch]$SkipAdcLogin
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Project = "bernie-emr4-dev"
$Location = "australia-southeast1"
$ServiceAccount = "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
$Scope = "https://www.googleapis.com/auth/cloud-platform"
$DevPracticeId = "d92314e3-aa1d-441e-81a5-f5db5ec22ca0"

function Write-Step([string]$Message) {
    Write-Host "  $Message" -ForegroundColor Cyan
}

if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    throw "gcloud not found on PATH. Install or open a shell with Google Cloud CLI available."
}

Write-Step "Selecting Bernie GCP project: $Project"
gcloud config set project $Project | Out-Host
if ($LASTEXITCODE -ne 0) {
    throw "gcloud config set project failed for $Project"
}

if (-not $SkipAdcLogin) {
    Write-Step "Replacing local ADC with impersonated Bernie service account"
    gcloud auth application-default revoke --quiet | Out-Host
    if ($LASTEXITCODE -ne 0) {
        throw "gcloud auth application-default revoke failed"
    }

    gcloud auth application-default login `
        --impersonate-service-account=$ServiceAccount `
        --scopes=$Scope | Out-Host
    if ($LASTEXITCODE -ne 0) {
        throw "gcloud ADC login failed for $ServiceAccount"
    }
} else {
    Write-Step "Skipping ADC login; using existing local ADC"
}

Remove-Item Env:GOOGLE_APPLICATION_CREDENTIALS -ErrorAction SilentlyContinue

$env:GCP_PROJECT = $Project
$env:GOOGLE_CLOUD_PROJECT = $Project
$env:GCP_LOCATION = $Location
$env:VERTEX_AI_LOCATION = $Location
$env:BERNIE_AI_PROJECT = $Project
$env:BERNIE_AI_LOCATION = $Location
$env:BERNIE_STAFF_PILOT_ENABLED = "true"
$env:BERNIE_STAFF_PILOT_PRACTICE_IDS = $DevPracticeId
Remove-Item Env:BERNIE_STAFF_PILOT_USER_IDS -ErrorAction SilentlyContinue
$env:BERNIE_BOOKING_INTERPRETER_PROVIDER = "gemini_vertex"

Write-Host ""
Write-Host "  [OK] Bernie ADC/env selected" -ForegroundColor Green
Write-Host "       GCP_PROJECT=$env:GCP_PROJECT" -ForegroundColor Gray
Write-Host "       BERNIE_STAFF_PILOT_ENABLED=$env:BERNIE_STAFF_PILOT_ENABLED" -ForegroundColor Gray
Write-Host "       BERNIE_BOOKING_INTERPRETER_PROVIDER=$env:BERNIE_BOOKING_INTERPRETER_PROVIDER" -ForegroundColor Gray
Write-Host "       Service account: $ServiceAccount" -ForegroundColor Gray
