param(
    [Parameter(Mandatory = $true)]
    [string]$Manifest,
    [Parameter(Mandatory = $true)]
    [string]$ControlPath,
    [Parameter(Mandatory = $true)]
    [string]$ProgressPath,
    [Parameter(Mandatory = $true)]
    [ValidateSet("HistoricalMeasuredProbe", "AuthoredSyntheticRecovery")]
    [string]$ExecutionProfile
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$MaximumDocuments = 80
$MaximumCellsPerDocument = 100000
$MaximumCellCharacters = 65536
$MaximumPrivateCharacters = 16777216
$MaximumStoryAnchorsPerDocument = 4096
$MaximumVerticalQuarterPoints = 100000
$OutputSchema = "historical_diary.private_word_story_coordinate_extraction.v2"
$repositoryRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$historicalAttemptRoot = Join-Path $repositoryRoot "local_data\historical-diary-trove\measured-probes\2026-08-24-story-coordinate-v1"
$syntheticAttemptRoot = Join-Path $repositoryRoot "local_data\authored-synthetic-diary-word-coordinate-recovery\run-v1"
$syntheticDocumentRoot = Join-Path $syntheticAttemptRoot "documents"
if ($ExecutionProfile -eq "HistoricalMeasuredProbe") {
    $ExpectedSchema = "historical_diary.private_binding_manifest.v1"
    $expectedManifest = Join-Path $historicalAttemptRoot "private-binding-manifest.json"
    $expectedControl = Join-Path $historicalAttemptRoot "owned-word-process-control.json"
    $expectedProgress = Join-Path $historicalAttemptRoot "word-extraction-progress.json"
} else {
    $ExpectedSchema = "historical_diary.authored_synthetic_binding_manifest.v1"
    $expectedManifest = Join-Path $syntheticAttemptRoot "synthetic-binding-manifest.json"
    $expectedControl = Join-Path $syntheticAttemptRoot "owned-word-process-control.json"
    $expectedProgress = Join-Path $syntheticAttemptRoot "word-extraction-progress.json"
}

function Write-ClosedJson {
    param(
        [string]$Path,
        [object]$Value
    )

    $temporary = "$Path.tmp"
    $json = $Value | ConvertTo-Json -Depth 8 -Compress
    [System.IO.File]::WriteAllText(
        $temporary,
        $json,
        [System.Text.UTF8Encoding]::new($false)
    )
    Move-Item -LiteralPath $temporary -Destination $Path -Force
}

function Get-ElapsedBucket {
    param([double]$ElapsedSeconds)

    if ($ElapsedSeconds -lt 30) { return "under_30_seconds" }
    if ($ElapsedSeconds -lt 120) { return "30_to_119_seconds" }
    if ($ElapsedSeconds -lt 300) { return "120_to_299_seconds" }
    if ($ElapsedSeconds -lt 900) { return "300_to_899_seconds" }
    return "900_seconds_or_more"
}

function Get-CoordinateRateFloorBucket {
    param(
        [int64]$CoordinateCount,
        [double]$ElapsedSeconds
    )

    if ($CoordinateCount -eq 0 -or $ElapsedSeconds -le 0) { return "not_available" }
    $rate = $CoordinateCount / $ElapsedSeconds
    if ($rate -lt 1) { return "under_1_per_second" }
    if ($rate -lt 4) { return "1_to_3_per_second" }
    if ($rate -lt 8) { return "4_to_7_per_second" }
    if ($rate -lt 16) { return "8_to_15_per_second" }
    return "16_or_more_per_second"
}

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
$completedDocumentCount = 0
$tableCellCount = 0
$structuralSegmentCount = 0
$coordinateAttemptCount = 0
$explicitStoryAnchorCount = 0
$totalDocumentCount = 1
$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

function Write-ClosedProgress {
    param([string]$Stage)

    $elapsed = [double]$stopwatch.Elapsed.TotalSeconds
    Write-ClosedJson -Path $ProgressPath -Value ([ordered]@{
        schema_version = "historical_diary.word_extraction_progress.v1"
        stage = $Stage
        total_document_count = [int]$totalDocumentCount
        completed_document_count = [int]$completedDocumentCount
        table_cell_count = [int64]$tableCellCount
        structural_segment_count = [int64]$structuralSegmentCount
        coordinate_attempt_count = [int64]$coordinateAttemptCount
        explicit_story_anchor_count = [int64]$explicitStoryAnchorCount
        elapsed_bucket = Get-ElapsedBucket -ElapsedSeconds $elapsed
        coordinate_rate_floor_bucket = Get-CoordinateRateFloorBucket `
            -CoordinateCount $coordinateAttemptCount `
            -ElapsedSeconds $elapsed
        source_value_emitted = $false
    })
}

try {
    $resolvedManifest = (Resolve-Path -LiteralPath $Manifest).Path
    $resolvedControlParent = (Resolve-Path -LiteralPath (Split-Path -Parent $ControlPath)).Path
    $resolvedProgressParent = (Resolve-Path -LiteralPath (Split-Path -Parent $ProgressPath)).Path
    $resolvedControl = Join-Path $resolvedControlParent (Split-Path -Leaf $ControlPath)
    $resolvedProgress = Join-Path $resolvedProgressParent (Split-Path -Leaf $ProgressPath)
    if (
        $resolvedManifest -ne $expectedManifest -or
        $resolvedControl -ne $expectedControl -or
        $resolvedProgress -ne $expectedProgress
    ) {
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
    if ($ExecutionProfile -eq "AuthoredSyntheticRecovery" -and $binding.files.Count -ne 12) {
        $reasonCode = "manifest_invalid"
        throw [System.InvalidOperationException]::new("closed_synthetic_manifest_count")
    }
    $totalDocumentCount = [int]$binding.files.Count
    Write-ClosedProgress -Stage "initialized"

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
    $ownedProcess = Get-Process -Id $ownedWordProcessId -ErrorAction Stop
    Write-ClosedJson -Path $ControlPath -Value ([ordered]@{
        schema_version = "historical_diary.owned_word_process_control.v1"
        process_id = $ownedWordProcessId
        process_class = "WINWORD"
        process_start_utc_ticks = [int64]$ownedProcess.StartTime.ToUniversalTime().Ticks
    })
    Write-ClosedProgress -Stage "word_isolated"

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
            if ($ExecutionProfile -eq "AuthoredSyntheticRecovery") {
                $syntheticPath = (Resolve-Path -LiteralPath ([string]$bound.absolute_path)).Path
                $syntheticParent = (Split-Path -Parent $syntheticPath)
                $syntheticLeaf = (Split-Path -Leaf $syntheticPath)
                $syntheticItem = Get-Item -LiteralPath $syntheticPath -Force
                if (
                    $syntheticParent -ne $syntheticDocumentRoot -or
                    $syntheticLeaf -notmatch '^synthetic-[0-9]{2}\.docx$' -or
                    ($syntheticItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint)
                ) {
                    $reasonCode = "manifest_invalid"
                    throw [System.InvalidOperationException]::new("closed_synthetic_path_boundary")
                }
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
                                        $explicitStoryAnchorCount += 1
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
                            $tableCellCount += 1
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
                                $structuralSegmentCount += $segmentCoordinates.Count
                                $coordinateAttemptCount += $segmentCoordinates.Count
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
        $completedDocumentCount += 1
        Write-ClosedProgress -Stage "document_completed"
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
        if ($wordCleanupCompleted -and (Test-Path -LiteralPath $ControlPath -PathType Leaf)) {
            Remove-Item -LiteralPath $ControlPath -Force -ErrorAction SilentlyContinue
        }
    } else {
        $wordCleanupCompleted = $false
    }
    try {
        Write-ClosedProgress -Stage "cleanup"
    } catch {
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
