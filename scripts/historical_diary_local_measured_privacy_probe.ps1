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
$MaximumStoryAnchorsPerDocument = 4096
$MaximumVerticalQuarterPoints = 100000
$ExpectedSchema = "historical_diary.private_binding_manifest.v1"
$OutputSchema = "historical_diary.private_word_story_coordinate_extraction.v2"
$repositoryRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$expectedManifest = Join-Path $repositoryRoot "local_data\historical-diary-trove\measured-probes\2026-08-24-story-coordinate-v1\private-binding-manifest.json"

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

function Convert-TimeTokenToMinute {
    param([string]$Value)

    if ($Value -notmatch '^(?<hour>[01]?\d|2[0-3])[:.](?<minute>[0-5]\d)(?:\s*(?<ampm>[AaPp][Mm]))?$') {
        return $null
    }
    $hour = [int]$Matches.hour
    $minute = [int]$Matches.minute
    $ampm = [string]$Matches.ampm
    if ($ampm.Length -gt 0 -and ($hour -lt 1 -or $hour -gt 12)) {
        return $null
    }
    if ($ampm -ieq 'pm' -and $hour -lt 12) {
        $hour += 12
    } elseif ($ampm -ieq 'am' -and $hour -eq 12) {
        $hour = 0
    }
    return ($hour * 60) + $minute
}

function Get-PrivateWordCoordinate {
    param($Range)

    try {
        $page = [int]$Range.Information(1)
        $vertical = [double]$Range.Information(6)
        if (
            $page -lt 1 -or $page -gt 4096 -or
            [double]::IsNaN($vertical) -or [double]::IsInfinity($vertical) -or
            $vertical -lt 0
        ) {
            throw [System.InvalidOperationException]::new('closed_coordinate_unavailable')
        }
        $quarterPoints = [int][math]::Round(
            $vertical * 4,
            [System.MidpointRounding]::AwayFromZero
        )
        if ($quarterPoints -lt 0 -or $quarterPoints -gt $MaximumVerticalQuarterPoints) {
            throw [System.InvalidOperationException]::new('closed_coordinate_out_of_range')
        }
        return [ordered]@{
            coordinate_available = $true
            page_ordinal = $page
            vertical_quarter_points = $quarterPoints
        }
    } catch {
        return [ordered]@{
            coordinate_available = $false
            page_ordinal = $null
            vertical_quarter_points = $null
        }
    }
}

function Get-PrivateCellSegmentCoordinates {
    param(
        $CellRange,
        [string]$Text
    )

    $body = $Text
    if ($body.EndsWith("`r$([char]7)")) {
        $body = $body.Substring(0, $body.Length - 2)
    } elseif ($body.EndsWith([string][char]7)) {
        $body = $body.Substring(0, $body.Length - 1)
    }
    $starts = [System.Collections.Generic.List[object]]::new()
    $starts.Add([ordered]@{ offset = 0; follows_manual_line = $false })
    $index = 0
    while ($index -lt $body.Length) {
        $character = $body[$index]
        if ($character -eq [char]13 -or $character -eq [char]10 -or $character -eq [char]11) {
            $manual = ($character -eq [char]11)
            if (
                $character -eq [char]13 -and
                $index + 1 -lt $body.Length -and
                $body[$index + 1] -eq [char]10
            ) {
                $index += 1
            }
            $starts.Add([ordered]@{
                offset = $index + 1
                follows_manual_line = $manual
            })
        }
        $index += 1
    }

    $coordinates = [System.Collections.Generic.List[object]]::new()
    for ($ordinal = 0; $ordinal -lt $starts.Count; $ordinal += 1) {
        $start = $starts[$ordinal]
        $coordinate = $null
        if ([bool]$start.follows_manual_line) {
            $coordinate = [ordered]@{
                coordinate_available = $false
                page_ordinal = $null
                vertical_quarter_points = $null
            }
        } else {
            $probeRange = $null
            try {
                $probeRange = $CellRange.Duplicate
                $absoluteStart = [int]$CellRange.Start + [int]$start.offset
                $probeRange.SetRange($absoluteStart, $absoluteStart)
                $coordinate = Get-PrivateWordCoordinate -Range $probeRange
            } finally {
                if ($null -ne $probeRange) {
                    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($probeRange) | Out-Null
                }
            }
        }
        $coordinates.Add([ordered]@{
            segment_ordinal = $ordinal
            coordinate_available = [bool]$coordinate.coordinate_available
            page_ordinal = $coordinate.page_ordinal
            vertical_quarter_points = $coordinate.vertical_quarter_points
        })
    }
    return @($coordinates.ToArray())
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
        $storyTimeAnchors = [System.Collections.Generic.List[object]]::new()
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
                $mainStory = $null
                $paragraphs = $null
                try {
                    $mainStory = $document.StoryRanges.Item(1)
                    $paragraphs = $mainStory.Paragraphs
                    for ($paragraphIndex = 1; $paragraphIndex -le $paragraphs.Count; $paragraphIndex += 1) {
                        $paragraph = $null
                        $paragraphRange = $null
                        try {
                            $paragraph = $paragraphs.Item($paragraphIndex)
                            $paragraphRange = $paragraph.Range
                            if (-not [bool]$paragraphRange.Information(12)) {
                                $storyText = [string]$paragraphRange.Text
                                $privateCharacterCount += $storyText.Length
                                if ($privateCharacterCount -gt $MaximumPrivateCharacters) {
                                    $reasonCode = "private_text_limit_exceeded"
                                    throw [System.InvalidOperationException]::new("closed_total_text_limit")
                                }
                                $closedToken = $storyText.Trim(
                                    [char[]]@([char]13, [char]7, [char]32, [char]9, [char]10, [char]11)
                                )
                                $timeMinute = Convert-TimeTokenToMinute -Value $closedToken
                                if ($null -ne $timeMinute) {
                                    if ($storyTimeAnchors.Count -ge $MaximumStoryAnchorsPerDocument) {
                                        $reasonCode = "private_text_limit_exceeded"
                                        throw [System.InvalidOperationException]::new("closed_story_anchor_limit")
                                    }
                                    $coordinate = Get-PrivateWordCoordinate -Range $paragraphRange
                                    if ([bool]$coordinate.coordinate_available) {
                                        $storyTimeAnchors.Add([ordered]@{
                                            time_minute = [int]$timeMinute
                                            page_ordinal = [int]$coordinate.page_ordinal
                                            vertical_quarter_points = [int]$coordinate.vertical_quarter_points
                                        })
                                    }
                                }
                                $storyText = $null
                                $closedToken = $null
                            }
                        } finally {
                            if ($null -ne $paragraphRange) {
                                [System.Runtime.InteropServices.Marshal]::ReleaseComObject($paragraphRange) | Out-Null
                            }
                            if ($null -ne $paragraph) {
                                [System.Runtime.InteropServices.Marshal]::ReleaseComObject($paragraph) | Out-Null
                            }
                        }
                    }
                } finally {
                    if ($null -ne $paragraphs) {
                        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($paragraphs) | Out-Null
                    }
                    if ($null -ne $mainStory) {
                        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($mainStory) | Out-Null
                    }
                }

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
                                $segmentCoordinates = @(
                                    Get-PrivateCellSegmentCoordinates -CellRange $range -Text $text
                                )
                                $cells.Add([ordered]@{
                                    table_index = $tableIndex
                                    row_index = [int]$cell.RowIndex
                                    column_index = [int]$cell.ColumnIndex
                                    text = $text
                                    shading = Convert-WordColour -Value $cell.Shading.BackgroundPatternColor
                                    font_color = Convert-WordColour -Value $range.Font.Color
                                    bold = [bool]([int]$range.Font.Bold -ne 0)
                                    italic = [bool]([int]$range.Font.Italic -ne 0)
                                    segment_coordinates = $segmentCoordinates
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
            story_time_anchors = @($storyTimeAnchors.ToArray())
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
