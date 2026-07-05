param(
    [string] $GraphifyExe = $env:GRAPHIFY_EXE,
    [switch] $Cluster,
    [switch] $Watch
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")

if (-not $GraphifyExe) {
    $command = Get-Command graphify -ErrorAction SilentlyContinue
    if ($command) {
        $GraphifyExe = $command.Source
    }
}

if (-not $GraphifyExe -or -not (Test-Path $GraphifyExe)) {
    throw "Graphify CLI not found. Install with `uv tool install `"graphifyy[mcp]`"` or set GRAPHIFY_EXE to graphify.exe."
}

Push-Location $repoRoot
try {
    if ($Watch) {
        & $GraphifyExe watch .
        exit $LASTEXITCODE
    }

    if ($Cluster) {
        & $GraphifyExe update .
    } else {
        & $GraphifyExe update . --no-cluster
    }
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
