param(
    [Parameter(Mandatory = $true)]
    [string]$Manifest
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$MaximumDocuments = 80
$MaximumCellsPerDocument = 100000
$MaximumCellCharacters = 65536
$MaximumPrivateCharacters = 16777216
$ExpectedSchema = "historical_diary.private_binding_manifest.v1"
$OutputSchema = "historical_diary.private_word_cell_extraction.v1"
$repositoryRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$expectedManifest = Join-Path $repositoryRoot "local_data\historical-diary-trove\measured-probes\2026-08-24-time-axis-v1\private-binding-manifest.json"

function Convert-WordColour {
    param($Value)

    try {
        $integer = [int]$Value
        if ($integer -lt -1 -or $integer -gt 16777215) {
            return -1
        }
        return $integer
    } catch {
        return -1
    }
}

function New-ClosedPayload {
    param(
        [string]$ReasonCode,
        [bool]$WordInvisible,
        [bool]$AlertsDisabled,
        [bool]$MacroSecurityForcedDisabled,
        [bool]$LinkUpdatesDisabled,
        [bool]$DocumentsOpenedReadOnly,
        [bool]$WordCleanupCompleted,
        [object[]]$Snapshots
    )

    return [ordered]@{
        schema_version = $OutputSchema
        status = if ($ReasonCode -eq "passed") { "passed" } else { "revision_required" }
        reason_code = $ReasonCode
        word_invisible = $WordInvisible
        alerts_disabled = $AlertsDisabled
        macro_security_forced_disabled = $MacroSecurityForcedDisabled
        link_updates_disabled = $LinkUpdatesDisabled
        documents_opened_read_only = $DocumentsOpenedReadOnly
        word_cleanup_completed = $WordCleanupCompleted
        snapshots = @($Snapshots)
    }
}

$word = $null
$payload = $null
$snapshots = [System.Collections.Generic.List[object]]::new()
$wordInvisible = $false
$alertsDisabled = $false
$macroSecurityForcedDisabled = $false
$linkUpdatesDisabled = $false
$documentsOpenedReadOnly = $true
$wordCleanupCompleted = $false
$wordQuitCompleted = $false
$ownedWordProcessId = $null
$reasonCode = "passed"
$privateCharacterCount = 0

try {
    $resolvedManifest = (Resolve-Path -LiteralPath $Manifest).Path
    if ($resolvedManifest -ne $expectedManifest) {
        $reasonCode = "manifest_invalid"
        throw [System.InvalidOperationException]::new("closed_manifest_boundary")
    }

    try {
        $binding = Get-Content -LiteralPath $resolvedManifest -Raw -Encoding UTF8 | ConvertFrom-Json
    } catch {
        $reasonCode = "manifest_invalid"
        throw [System.InvalidOperationException]::new("closed_manifest_parse")
    }
    if (
        $binding.schema_version -ne $ExpectedSchema -or
        $null -eq $binding.files -or
        $binding.files.Count -lt 2 -or
        $binding.files.Count -gt $MaximumDocuments
    ) {
        $reasonCode = "manifest_invalid"
        throw [System.InvalidOperationException]::new("closed_manifest_schema")
    }

    $baselineWordProcessIds = @(Get-Process -Name "WINWORD" -ErrorAction SilentlyContinue | ForEach-Object { $_.Id })
    try {
        $word = New-Object -ComObject Word.Application
    } catch {
        $reasonCode = "word_automation_unavailable"
        throw [System.InvalidOperationException]::new("closed_word_automation")
    }
    $createdWordProcessIds = @(
        Get-Process -Name "WINWORD" -ErrorAction SilentlyContinue |
            Where-Object { $baselineWordProcessIds -notcontains $_.Id } |
            ForEach-Object { $_.Id }
    )
    if ($createdWordProcessIds.Count -ne 1) {
        $reasonCode = "word_process_isolation_unavailable"
        throw [System.InvalidOperationException]::new("closed_word_process_ownership")
    }
    $ownedWordProcessId = [int]$createdWordProcessIds[0]

    $word.Visible = $false
    $word.DisplayAlerts = 0
    $wordInvisible = -not [bool]$word.Visible
    $alertsDisabled = ([int]$word.DisplayAlerts -eq 0)
    try {
        $word.AutomationSecurity = 3
        $macroSecurityForcedDisabled = ([int]$word.AutomationSecurity -eq 3)
    } catch {
        $reasonCode = "macro_security_unavailable"
        throw [System.InvalidOperationException]::new("closed_macro_security")
    }
    try {
        $word.Options.UpdateLinksAtOpen = $false
        $word.Options.ConfirmConversions = $false
        $linkUpdatesDisabled = -not [bool]$word.Options.UpdateLinksAtOpen
    } catch {
        $reasonCode = "macro_security_unavailable"
        throw [System.InvalidOperationException]::new("closed_link_update_control")
    }
    if (
        -not $wordInvisible -or
        -not $alertsDisabled -or
        -not $macroSecurityForcedDisabled -or
        -not $linkUpdatesDisabled
    ) {
        $reasonCode = "macro_security_unavailable"
        throw [System.InvalidOperationException]::new("closed_word_control_readback")
    }

    for ($sequence = 0; $sequence -lt $binding.files.Count; $sequence += 1) {
        $bound = $binding.files[$sequence]
        $cells = [System.Collections.Generic.List[object]]::new()
        $document = $null
        $documentError = $null
        try {
            if ([int]$bound.sequence_index -ne $sequence) {
                $reasonCode = "manifest_invalid"
                throw [System.InvalidOperationException]::new("closed_manifest_sequence")
            }
            $document = $word.Documents.Open([string]$bound.absolute_path, $false, $true, $false)
            if (-not [bool]$document.ReadOnly) {
                $documentsOpenedReadOnly = $false
                $documentError = "document_open_failed"
            } else {
                $cellCount = 0
                for ($tableIndex = 1; $tableIndex -le $document.Tables.Count; $tableIndex += 1) {
                    $table = $null
                    try {
                        $table = $document.Tables.Item($tableIndex)
                        for ($cellIndex = 1; $cellIndex -le $table.Range.Cells.Count; $cellIndex += 1) {
                            $cellCount += 1
                            if ($cellCount -gt $MaximumCellsPerDocument) {
                                $reasonCode = "private_text_limit_exceeded"
                                throw [System.InvalidOperationException]::new("closed_cell_count_limit")
                            }
                            $cell = $null
                            $range = $null
                            try {
                                $cell = $table.Range.Cells.Item($cellIndex)
                                $range = $cell.Range
                                $text = [string]$range.Text
                                if ($text.Length -gt $MaximumCellCharacters) {
                                    $reasonCode = "private_text_limit_exceeded"
                                    throw [System.InvalidOperationException]::new("closed_cell_text_limit")
                                }
                                $privateCharacterCount += $text.Length
                                if ($privateCharacterCount -gt $MaximumPrivateCharacters) {
                                    $reasonCode = "private_text_limit_exceeded"
                                    throw [System.InvalidOperationException]::new("closed_total_text_limit")
                                }
                                $cells.Add([ordered]@{
                                    table_index = $tableIndex
                                    row_index = [int]$cell.RowIndex
                                    column_index = [int]$cell.ColumnIndex
                                    text = $text
                                    shading = Convert-WordColour -Value $cell.Shading.BackgroundPatternColor
                                    font_color = Convert-WordColour -Value $range.Font.Color
                                    bold = [bool]([int]$range.Font.Bold -ne 0)
                                    italic = [bool]([int]$range.Font.Italic -ne 0)
                                })
                            } finally {
                                if ($null -ne $range) {
                                    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($range) | Out-Null
                                }
                                if ($null -ne $cell) {
                                    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($cell) | Out-Null
                                }
                            }
                        }
                    } finally {
                        if ($null -ne $table) {
                            [System.Runtime.InteropServices.Marshal]::ReleaseComObject($table) | Out-Null
                        }
                    }
                }
            }
        } catch {
            if ($reasonCode -eq "private_text_limit_exceeded" -or $reasonCode -eq "manifest_invalid") {
                throw
            }
            $documentError = if ($null -eq $document) { "document_open_failed" } else { "document_structure_failed" }
        } finally {
            if ($null -ne $document) {
                try {
                    $document.Close($false)
                } finally {
                    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($document) | Out-Null
                }
            }
        }
        if ($null -ne $documentError) {
            $reasonCode = "document_errors_present"
        }
        $snapshots.Add([ordered]@{
            sequence_index = $sequence
            observation_offset_seconds = [int]$bound.observation_offset_seconds
            cells = @($cells.ToArray())
            error_code = $documentError
        })
    }
} catch {
    if ($reasonCode -eq "passed") {
        $reasonCode = "document_errors_present"
    }
} finally {
    if ($null -ne $word) {
        if ($null -ne $ownedWordProcessId) {
            try {
                $word.Quit()
                $wordQuitCompleted = $true
            } catch {
                $wordQuitCompleted = $false
            }
        }
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
        $word = $null
    }
    [gc]::Collect()
    [gc]::WaitForPendingFinalizers()
    if ($null -ne $ownedWordProcessId) {
        $ownedProcess = Get-Process -Id $ownedWordProcessId -ErrorAction SilentlyContinue
        if ($null -ne $ownedProcess) {
            $ownedProcess.WaitForExit(10000) | Out-Null
        }
        $ownedProcess = Get-Process -Id $ownedWordProcessId -ErrorAction SilentlyContinue
        if ($null -ne $ownedProcess) {
            Stop-Process -Id $ownedWordProcessId -Force -ErrorAction SilentlyContinue
            Wait-Process -Id $ownedWordProcessId -Timeout 10 -ErrorAction SilentlyContinue
        }
        $wordCleanupCompleted = $wordQuitCompleted -and $null -eq (
            Get-Process -Id $ownedWordProcessId -ErrorAction SilentlyContinue
        )
    } else {
        $wordCleanupCompleted = $false
    }
}

$payload = New-ClosedPayload `
    -ReasonCode $reasonCode `
    -WordInvisible $wordInvisible `
    -AlertsDisabled $alertsDisabled `
    -MacroSecurityForcedDisabled $macroSecurityForcedDisabled `
    -LinkUpdatesDisabled $linkUpdatesDisabled `
    -DocumentsOpenedReadOnly $documentsOpenedReadOnly `
    -WordCleanupCompleted $wordCleanupCompleted `
    -Snapshots @($snapshots.ToArray())

$payload | ConvertTo-Json -Depth 12 -Compress
