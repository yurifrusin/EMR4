param(
    [Parameter(Mandatory = $true)]
    [string[]]$Root,

    [string]$Output = "local_data/historical-diary-trove/inventory/structure_classifier_h4.json",

    [int]$SampleSize = 8,

    [int]$DenseDays = 1
)

$ErrorActionPreference = "Stop"

function Get-RootLabel {
    param([string]$Path)

    return (Get-Item -LiteralPath $Path).Name
}

function Get-DenseCandidates {
    param(
        [string]$Path,
        [int]$DayCount
    )

    $files = Get-ChildItem -LiteralPath $Path -File -Filter "*.doc" |
        Where-Object { $_.Length -gt 4096 }

    $denseDates = $files |
        Group-Object { $_.LastWriteTimeUtc.ToString("yyyy-MM-dd") } |
        Sort-Object @{ Expression = "Count"; Descending = $true }, @{ Expression = "Name"; Ascending = $true } |
        Select-Object -First $DayCount |
        ForEach-Object { $_.Name }

    return $files |
        Where-Object { $denseDates -contains $_.LastWriteTimeUtc.ToString("yyyy-MM-dd") } |
        Sort-Object LastWriteTimeUtc, Length
}

function Get-Range {
    param([int[]]$Values)

    if (-not $Values -or $Values.Count -eq 0) {
        return $null
    }

    return @{
        min = ($Values | Measure-Object -Minimum).Minimum
        max = ($Values | Measure-Object -Maximum).Maximum
    }
}

function Get-Distribution {
    param([string[]]$Values)

    if (-not $Values -or $Values.Count -eq 0) {
        return @()
    }

    $distribution = @($Values |
        Group-Object |
        Sort-Object @{ Expression = "Count"; Descending = $true }, @{ Expression = "Name"; Ascending = $true } |
        ForEach-Object {
            @{
                value = $_.Name
                count = $_.Count
            }
        })
    return ,$distribution
}

function Get-Mode {
    param([int[]]$Values)

    if (-not $Values -or $Values.Count -eq 0) {
        return $null
    }

    return ($Values |
        Group-Object |
        Sort-Object @{ Expression = "Count"; Descending = $true }, @{ Expression = "Name"; Ascending = $true } |
        Select-Object -First 1 |
        ForEach-Object { [int]$_.Name })
}

function Convert-TimeTokenToMinute {
    param([string]$Token)

    $match = [regex]::Match($Token.Trim(), "^(?<hour>\d{1,2})[:.](?<minute>\d{2})(?:\s?(?<ampm>[AaPp][Mm]))?$")
    if (-not $match.Success) {
        return $null
    }

    $hour = [int]$match.Groups["hour"].Value
    $minute = [int]$match.Groups["minute"].Value
    $ampm = $match.Groups["ampm"].Value.ToLowerInvariant()

    if ($hour -gt 23 -or $minute -gt 59) {
        return $null
    }

    if ($ampm -eq "pm" -and $hour -lt 12) {
        $hour += 12
    } elseif ($ampm -eq "am" -and $hour -eq 12) {
        $hour = 0
    }

    return ($hour * 60) + $minute
}

function Get-TimeIntervalMode {
    param([string[]]$Tokens)

    $minutes = @($Tokens |
        ForEach-Object { Convert-TimeTokenToMinute -Token $_ } |
        Where-Object { $null -ne $_ } |
        Sort-Object -Unique)

    if ($minutes.Count -lt 3) {
        return $null
    }

    $deltas = @()
    for ($index = 1; $index -lt $minutes.Count; $index += 1) {
        $delta = $minutes[$index] - $minutes[$index - 1]
        if ($delta -gt 0 -and $delta -le 120) {
            $deltas += $delta
        }
    }

    return Get-Mode -Values $deltas
}

function Measure-DocumentStructure {
    param($Document)

    $text = [string]$Document.Content.Text
    $nonEmptyParagraphLengths = @()

    foreach ($paragraph in @($Document.Paragraphs)) {
        $trimmed = ([string]$paragraph.Range.Text).Trim()
        if ($trimmed.Length -gt 0) {
            $nonEmptyParagraphLengths += $trimmed.Length
        }
    }

    $tableDimensions = @()
    $tableCellCount = 0
    foreach ($table in @($Document.Tables)) {
        $tableCellCount += $table.Range.Cells.Count
        $rows = $null
        $columns = $null
        try {
            $rows = $table.Rows.Count
            $columns = $table.Columns.Count
        } catch {
            $rows = $null
            $columns = $null
        }

        if ($null -ne $rows -and $null -ne $columns) {
            $tableDimensions += "$($rows)x$($columns)"
        } else {
            $tableDimensions += "irregular:$($table.Range.Cells.Count)"
        }
    }

    $timeMatches = @([regex]::Matches($text, "\b(?:[01]?\d|2[0-3])[:.][0-5]\d(?:\s?[AaPp][Mm])?\b") |
        ForEach-Object { $_.Value })
    $dateLikeCount = ([regex]::Matches($text, "\b\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?\b")).Count
    $nonEmptyLineCount = (($text -split "[\r\n]+") | Where-Object { $_.Trim().Length -gt 0 }).Count
    $dimensionSignature = ($tableDimensions | Sort-Object) -join "+"
    $timeIntervalMode = Get-TimeIntervalMode -Tokens $timeMatches

    $structureClass = "weak"
    if ($Document.Tables.Count -ge 1 -and $timeMatches.Count -ge 40 -and $nonEmptyLineCount -ge 100) {
        $structureClass = "likely_diary_grid"
    }
    if ($Document.Tables.Count -ge 2 -and $timeMatches.Count -ge 70 -and $dateLikeCount -ge 8) {
        $structureClass = "strong_diary_grid"
    }

    return @{
        char_count = $text.Length
        paragraph_count = $Document.Paragraphs.Count
        non_empty_paragraph_count = $nonEmptyParagraphLengths.Count
        non_empty_line_count = $nonEmptyLineCount
        table_count = $Document.Tables.Count
        table_cell_count = $tableCellCount
        table_dimension_signature = $dimensionSignature
        time_like_token_count = $timeMatches.Count
        unique_time_like_token_count = @($timeMatches | Sort-Object -Unique).Count
        date_like_token_count = $dateLikeCount
        inferred_time_interval_mode_minutes = $timeIntervalMode
        paragraph_length_range = Get-Range -Values $nonEmptyParagraphLengths
        structure_class = $structureClass
        neutral_signature = "tables=$($Document.Tables.Count);cells=$tableCellCount;paragraphs=$($Document.Paragraphs.Count);lines=$nonEmptyLineCount;times=$($timeMatches.Count);dates=$dateLikeCount;dims=$dimensionSignature;mode=$timeIntervalMode"
    }
}

function Get-AdjacentDeltaRanges {
    param([hashtable[]]$Measurements)

    if (-not $Measurements -or $Measurements.Count -lt 2) {
        return $null
    }

    $charDeltas = @()
    $paragraphDeltas = @()
    $lineDeltas = @()
    $timeDeltas = @()
    $dateDeltas = @()

    for ($index = 1; $index -lt $Measurements.Count; $index += 1) {
        $previous = $Measurements[$index - 1]
        $current = $Measurements[$index]
        $charDeltas += [math]::Abs($current.char_count - $previous.char_count)
        $paragraphDeltas += [math]::Abs($current.paragraph_count - $previous.paragraph_count)
        $lineDeltas += [math]::Abs($current.non_empty_line_count - $previous.non_empty_line_count)
        $timeDeltas += [math]::Abs($current.time_like_token_count - $previous.time_like_token_count)
        $dateDeltas += [math]::Abs($current.date_like_token_count - $previous.date_like_token_count)
    }

    return @{
        char_count_abs_delta_range = Get-Range -Values $charDeltas
        paragraph_count_abs_delta_range = Get-Range -Values $paragraphDeltas
        non_empty_line_count_abs_delta_range = Get-Range -Values $lineDeltas
        time_like_token_count_abs_delta_range = Get-Range -Values $timeDeltas
        date_like_token_count_abs_delta_range = Get-Range -Values $dateDeltas
    }
}

function Summarize-Root {
    param(
        [string]$Label,
        [object[]]$Candidates,
        [object[]]$Sample,
        [hashtable[]]$Measurements,
        [int]$ErrorCount
    )

    return @{
        root_label = $Label
        dense_candidate_count = $Candidates.Count
        requested_sample_size = $SampleSize
        sampled_count = $Sample.Count
        opened_count = $Measurements.Count
        error_count = $ErrorCount
        structure_class_distribution = Get-Distribution -Values @($Measurements | ForEach-Object { $_.structure_class })
        neutral_signature_distribution = Get-Distribution -Values @($Measurements | ForEach-Object { $_.neutral_signature })
        table_dimension_signature_distribution = Get-Distribution -Values @($Measurements | ForEach-Object { $_.table_dimension_signature })
        char_count_range = Get-Range -Values @($Measurements | ForEach-Object { $_.char_count })
        paragraph_count_range = Get-Range -Values @($Measurements | ForEach-Object { $_.paragraph_count })
        non_empty_paragraph_count_range = Get-Range -Values @($Measurements | ForEach-Object { $_.non_empty_paragraph_count })
        non_empty_line_count_range = Get-Range -Values @($Measurements | ForEach-Object { $_.non_empty_line_count })
        table_count_range = Get-Range -Values @($Measurements | ForEach-Object { $_.table_count })
        table_cell_count_range = Get-Range -Values @($Measurements | ForEach-Object { $_.table_cell_count })
        time_like_token_count_range = Get-Range -Values @($Measurements | ForEach-Object { $_.time_like_token_count })
        unique_time_like_token_count_range = Get-Range -Values @($Measurements | ForEach-Object { $_.unique_time_like_token_count })
        date_like_token_count_range = Get-Range -Values @($Measurements | ForEach-Object { $_.date_like_token_count })
        inferred_time_interval_mode_minutes_distribution = Get-Distribution -Values @($Measurements | ForEach-Object { [string]$_.inferred_time_interval_mode_minutes })
        paragraph_length_range = Get-Range -Values @($Measurements | ForEach-Object {
            if ($null -ne $_.paragraph_length_range) {
                @($_.paragraph_length_range.min, $_.paragraph_length_range.max)
            }
        })
        adjacent_neutral_delta_ranges = Get-AdjacentDeltaRanges -Measurements $Measurements
    }
}

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Output) | Out-Null

$word = $null
$results = @()

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    try {
        $word.AutomationSecurity = 3
    } catch {
        # Older Office builds may not expose AutomationSecurity through COM.
    }

    foreach ($rootPath in $Root) {
        $resolvedRoot = (Resolve-Path -LiteralPath $rootPath).Path
        $label = Get-RootLabel -Path $resolvedRoot
        $candidates = @(Get-DenseCandidates -Path $resolvedRoot -DayCount $DenseDays)
        $sample = @($candidates | Select-Object -First $SampleSize)
        $measurements = @()
        $errorCount = 0

        foreach ($file in $sample) {
            $document = $null
            try {
                $document = $word.Documents.Open($file.FullName, $false, $true)
                $measurements += Measure-DocumentStructure -Document $document
            } catch {
                $errorCount += 1
            } finally {
                if ($null -ne $document) {
                    $document.Close($false)
                    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($document) | Out-Null
                }
            }
        }

        $results += Summarize-Root -Label $label -Candidates $candidates -Sample $sample -Measurements $measurements -ErrorCount $errorCount
    }
} finally {
    if ($null -ne $word) {
        $word.Quit()
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
    }
    [gc]::Collect()
    [gc]::WaitForPendingFinalizers()
}

$payload = @{
    generated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    privacy = @{
        emits_document_text = $false
        emits_filenames = $false
        emits_raw_paths = $false
        emits_exact_document_timestamps = $false
        emits_patient_or_staff_labels = $false
        opens_documents_read_only = $true
        macro_security_forced_disabled = $true
    }
    classifier = @{
        version = 1
        sample_only = $true
        output_class = "aggregate_neutral_layout_facts"
    }
    roots = $results
}

$payload | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $Output -Encoding UTF8
$payload | ConvertTo-Json -Depth 10
