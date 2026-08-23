param(
    [Parameter(Mandatory = $true)]
    [string]$ControlPath
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$repositoryRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$expectedControl = Join-Path $repositoryRoot "local_data\authored-synthetic-diary-word-coordinate-recovery\run-v1\timeout-owned-word-process-control.json"
$resolvedParent = (Resolve-Path -LiteralPath (Split-Path -Parent $ControlPath)).Path
$resolvedControl = Join-Path $resolvedParent (Split-Path -Leaf $ControlPath)
if ($resolvedControl -ne $expectedControl) {
    throw [System.InvalidOperationException]::new("closed_control_boundary")
}

$word = $null
$ownedWordProcessId = $null
try {
    $baseline = @(
        Get-Process -Name "WINWORD" -ErrorAction SilentlyContinue |
            ForEach-Object { $_.Id }
    )
    $word = New-Object -ComObject Word.Application
    $created = @(
        Get-Process -Name "WINWORD" -ErrorAction SilentlyContinue |
            Where-Object { $baseline -notcontains $_.Id }
    )
    if ($created.Count -ne 1) {
        throw [System.InvalidOperationException]::new("closed_word_process_ownership")
    }
    $ownedWordProcessId = [int]$created[0].Id
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $control = [ordered]@{
        schema_version = "historical_diary.owned_word_process_control.v1"
        process_id = $ownedWordProcessId
        process_class = "WINWORD"
        process_start_utc_ticks = [int64]$created[0].StartTime.ToUniversalTime().Ticks
    }
    $json = $control | ConvertTo-Json -Depth 4 -Compress
    [System.IO.File]::WriteAllText(
        $ControlPath,
        $json,
        [System.Text.UTF8Encoding]::new($false)
    )
    Start-Sleep -Seconds 60
} finally {
    if ($null -ne $word) {
        try { $word.Quit() } catch {}
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
    }
    [gc]::Collect()
    [gc]::WaitForPendingFinalizers()
    if ($null -ne $ownedWordProcessId) {
        Stop-Process -Id $ownedWordProcessId -Force -ErrorAction SilentlyContinue
    }
    Remove-Item -LiteralPath $ControlPath -Force -ErrorAction SilentlyContinue
}
