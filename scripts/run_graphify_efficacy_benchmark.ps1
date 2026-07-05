param(
    [string] $GraphifyExe = $env:GRAPHIFY_EXE,
    [string] $OutputDir = "graphify-out\benchmarks\efficacy",
    [switch] $RefreshGraph
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$graphPath = Join-Path $repoRoot "graphify-out\graph.json"
$resolvedOutputDir = Join-Path $repoRoot $OutputDir

if (-not $GraphifyExe) {
    $command = Get-Command graphify -ErrorAction SilentlyContinue
    if ($command) {
        $GraphifyExe = $command.Source
    }
}

if (-not $GraphifyExe -or -not (Test-Path $GraphifyExe)) {
    throw "Graphify CLI not found. Install with `uv tool install `"graphifyy[mcp]`"` or set GRAPHIFY_EXE to graphify.exe."
}

if ($RefreshGraph -or -not (Test-Path $graphPath)) {
    & (Join-Path $PSScriptRoot "refresh_code_graph.ps1") -GraphifyExe $GraphifyExe
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

if (-not (Test-Path $graphPath)) {
    throw "Graph not found at $graphPath. Run scripts\refresh_code_graph.ps1 first."
}

New-Item -ItemType Directory -Force -Path $resolvedOutputDir | Out-Null

$queries = @(
    @{
        Id = "symbol-proposal-route"
        Mode = "explain"
        Target = "propose_bernie_supervised_booking"
        Purpose = "Find the backend route and direct collaborators for Bernie supervised booking proposals."
    },
    @{
        Id = "impact-slot-normalizer"
        Mode = "affected"
        Target = "normalize_slot_search_command"
        Depth = "2"
        Purpose = "Find callers and tests affected by slot-search normalization changes."
    },
    @{
        Id = "symbol-booking-interpreter"
        Mode = "explain"
        Target = "BookingInstructionInterpreter"
        Purpose = "Find the AI interpreter seam used by Bernie booking instruction handling."
    },
    @{
        Id = "symbol-diary-loader"
        Mode = "explain"
        Target = "loadDiary"
        Purpose = "Find frontend diary loading code and adjacent UI dependencies."
    },
    @{
        Id = "query-clarification-merge"
        Mode = "query"
        Target = "What code handles Bernie clarification merge semantics?"
        Budget = "1200"
        Purpose = "Test whether broad natural-language graph search finds R2-relevant merge code without too much noise."
    },
    @{
        Id = "query-confirmation-evidence"
        Mode = "query"
        Target = "Where is Bernie confirmation evidence minted and verified?"
        Budget = "1200"
        Purpose = "Test whether a domain phrase finds confirmation evidence code paths."
    }
)

$summary = [System.Collections.Generic.List[object]]::new()

Push-Location $repoRoot
try {
    foreach ($query in $queries) {
        $outputPath = Join-Path $resolvedOutputDir "$($query.Id).txt"
        $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

        if ($query.Mode -eq "explain") {
            $output = & $GraphifyExe explain $query.Target --graph $graphPath 2>&1
        } elseif ($query.Mode -eq "affected") {
            $output = & $GraphifyExe affected $query.Target --graph $graphPath --depth $query.Depth 2>&1
        } elseif ($query.Mode -eq "query") {
            $output = & $GraphifyExe query $query.Target --graph $graphPath --budget $query.Budget 2>&1
        } else {
            throw "Unsupported query mode: $($query.Mode)"
        }

        $exitCode = $LASTEXITCODE
        $stopwatch.Stop()
        $output | Set-Content -Path $outputPath -Encoding UTF8
        $lineCount = ($output | Measure-Object -Line).Lines

        $summary.Add([pscustomobject]@{
            id = $query.Id
            mode = $query.Mode
            target = $query.Target
            purpose = $query.Purpose
            seconds = [math]::Round($stopwatch.Elapsed.TotalSeconds, 3)
            exit_code = $exitCode
            output_lines = $lineCount
            output_path = (Resolve-Path $outputPath).Path
        })
    }
} finally {
    Pop-Location
}

$summaryPath = Join-Path $resolvedOutputDir "summary.json"
$summary | ConvertTo-Json -Depth 4 | Set-Content -Path $summaryPath -Encoding UTF8
$summary | Format-Table id, mode, seconds, exit_code, output_lines, output_path -AutoSize
Write-Output "Summary: $summaryPath"
