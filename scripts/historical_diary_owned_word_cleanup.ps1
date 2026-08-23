param(
    [Parameter(Mandatory = $true)]
    [string]$ControlPath
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$ExpectedSchema = "historical_diary.owned_word_process_control.v1"

function New-ClosedResult {
    param(
        [string]$Status,
        [string]$ReasonCode,
        [bool]$ExactOwnedProcessAbsent
    )

    return [ordered]@{
        schema_version = "historical_diary.owned_word_cleanup_result.v1"
        status = $Status
        reason_code = $ReasonCode
        exact_owned_process_absent = $ExactOwnedProcessAbsent
        broad_process_name_stop_used = $false
        source_value_emitted = $false
    }
}

$result = $null
try {
    if (-not (Test-Path -LiteralPath $ControlPath -PathType Leaf)) {
        $result = New-ClosedResult `
            -Status "passed" `
            -ReasonCode "control_file_absent" `
            -ExactOwnedProcessAbsent $true
    } else {
        try {
            $control = Get-Content -LiteralPath $ControlPath -Raw -Encoding UTF8 | ConvertFrom-Json
            if (
                $control.schema_version -ne $ExpectedSchema -or
                [string]$control.process_class -ne "WINWORD" -or
                [int64]$control.process_id -lt 1 -or
                [int64]$control.process_start_utc_ticks -lt 621355968000000000
            ) {
                throw [System.InvalidOperationException]::new("closed_control_invalid")
            }
        } catch {
            $result = New-ClosedResult `
                -Status "blocked" `
                -ReasonCode "control_file_invalid" `
                -ExactOwnedProcessAbsent $false
        }

        if ($null -eq $result) {
            $processId = [int]$control.process_id
            $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
            if ($null -eq $process) {
                Remove-Item -LiteralPath $ControlPath -Force -ErrorAction SilentlyContinue
                $result = New-ClosedResult `
                    -Status "passed" `
                    -ReasonCode "owned_process_already_absent" `
                    -ExactOwnedProcessAbsent $true
            } else {
                $matchesIdentity = (
                    $process.ProcessName -eq "WINWORD" -and
                    $process.StartTime.ToUniversalTime().Ticks -eq
                        [int64]$control.process_start_utc_ticks
                )
                if (-not $matchesIdentity) {
                    $result = New-ClosedResult `
                        -Status "blocked" `
                        -ReasonCode "owned_process_identity_mismatch" `
                        -ExactOwnedProcessAbsent $false
                } else {
                    Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
                    $deadline = (Get-Date).AddSeconds(10)
                    do {
                        $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
                        if ($null -eq $process) {
                            break
                        }
                        Start-Sleep -Milliseconds 250
                    } while ((Get-Date) -lt $deadline)
                    $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
                    if ($null -eq $process) {
                        Remove-Item -LiteralPath $ControlPath -Force -ErrorAction SilentlyContinue
                        $result = New-ClosedResult `
                            -Status "passed" `
                            -ReasonCode "owned_process_removed" `
                            -ExactOwnedProcessAbsent $true
                    } else {
                        $result = New-ClosedResult `
                            -Status "blocked" `
                            -ReasonCode "owned_process_remains" `
                            -ExactOwnedProcessAbsent $false
                    }
                }
            }
        }
    }
} catch {
    $result = New-ClosedResult `
        -Status "blocked" `
        -ReasonCode "cleanup_internal_failure" `
        -ExactOwnedProcessAbsent $false
}

$result | ConvertTo-Json -Depth 4 -Compress
if ($result.status -ne "passed") {
    exit 2
}
