param(
    [Parameter(Mandatory = $true)]
    [string[]]$Root,

    [string]$Output = "local_data/historical-diary-trove/inventory/word_extract_probe_h3.json",

    [int]$SampleSize = 2,

    [int]$DenseDays = 1
)

$ErrorActionPreference = "Stop"

function Get-RelativeRootLabel {
    param([string]$Path)

    $item = Get-Item -LiteralPath $Path
    return $item.Name
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

function Measure-DocumentText {
    param($Document)

    $text = [string]$Document.Content.Text
    $paragraphLengths = @()

    foreach ($paragraph in @($Document.Paragraphs)) {
        $paragraphText = [string]$paragraph.Range.Text
        $trimmed = $paragraphText.Trim()
        if ($trimmed.Length -gt 0) {
            $paragraphLengths += $trimmed.Length
        }
    }

    $tableCellCount = 0
    foreach ($table in @($Document.Tables)) {
        $tableCellCount += $table.Range.Cells.Count
    }

    $visibleLineCount = (($text -split "[\r\n]+") | Where-Object { $_.Trim().Length -gt 0 }).Count
    $timeLikeCount = ([regex]::Matches($text, "\b(?:[01]?\d|2[0-3])[:.][0-5]\d(?:\s?[AaPp][Mm])?\b")).Count
    $dateLikeCount = ([regex]::Matches($text, "\b\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?\b")).Count

    return @{
        char_count = $text.Length
        paragraph_count = $Document.Paragraphs.Count
        non_empty_paragraph_count = $paragraphLengths.Count
        non_empty_line_count = $visibleLineCount
        table_count = $Document.Tables.Count
        table_cell_count = $tableCellCount
        tab_count = ([regex]::Matches($text, "`t")).Count
        time_like_token_count = $timeLikeCount
        date_like_token_count = $dateLikeCount
        paragraph_length_range = Get-Range -Values $paragraphLengths
    }
}

$outputItem = New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Output)

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
        $label = Get-RelativeRootLabel -Path $resolvedRoot
        $candidates = @(Get-DenseCandidates -Path $resolvedRoot -DayCount $DenseDays)
        $sample = @($candidates | Select-Object -First $SampleSize)
        $measurements = @()
        $errorCount = 0

        foreach ($file in $sample) {
            $document = $null
            try {
                $document = $word.Documents.Open($file.FullName, $false, $true)
                $measurements += Measure-DocumentText -Document $document
            } catch {
                $errorCount += 1
            } finally {
                if ($null -ne $document) {
                    $document.Close($false)
                    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($document) | Out-Null
                }
            }
        }

        $results += @{
            root_label = $label
            dense_candidate_count = $candidates.Count
            requested_sample_size = $SampleSize
            sampled_count = $sample.Count
            opened_count = $measurements.Count
            error_count = $errorCount
            char_count_range = Get-Range -Values @($measurements | ForEach-Object { $_.char_count })
            paragraph_count_range = Get-Range -Values @($measurements | ForEach-Object { $_.paragraph_count })
            non_empty_paragraph_count_range = Get-Range -Values @($measurements | ForEach-Object { $_.non_empty_paragraph_count })
            non_empty_line_count_range = Get-Range -Values @($measurements | ForEach-Object { $_.non_empty_line_count })
            table_count_range = Get-Range -Values @($measurements | ForEach-Object { $_.table_count })
            table_cell_count_range = Get-Range -Values @($measurements | ForEach-Object { $_.table_cell_count })
            tab_count_range = Get-Range -Values @($measurements | ForEach-Object { $_.tab_count })
            time_like_token_count_range = Get-Range -Values @($measurements | ForEach-Object { $_.time_like_token_count })
            date_like_token_count_range = Get-Range -Values @($measurements | ForEach-Object { $_.date_like_token_count })
            paragraph_length_range = Get-Range -Values @($measurements | ForEach-Object {
                if ($null -ne $_.paragraph_length_range) {
                    @($_.paragraph_length_range.min, $_.paragraph_length_range.max)
                }
            })
        }
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
        opens_documents_read_only = $true
        macro_security_forced_disabled = $true
    }
    word = @{
        com_available = $true
    }
    roots = $results
}

$payload | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $Output -Encoding UTF8
$payload | ConvertTo-Json -Depth 8
