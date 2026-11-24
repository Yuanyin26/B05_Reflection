param(
    [string]$PythonExecutable = "",
    [string]$OutDir = ""
)

$ErrorActionPreference = "Stop"
$researchRoot = Split-Path -Parent $PSScriptRoot

if (-not $PythonExecutable) {
    $researchVenvPython = Join-Path $researchRoot ".venv\Scripts\python.exe"
    if (Test-Path -LiteralPath $researchVenvPython) {
        $PythonExecutable = $researchVenvPython
    } else {
        $PythonExecutable = "python"
    }
}

if (-not $OutDir) {
    $OutDir = Join-Path $researchRoot "outputs\local"
}

$researchEntry = Join-Path $researchRoot "src\main.py"
$researchInput = Join-Path $researchRoot "data\examples"
& $PythonExecutable $researchEntry --task all --test --check-only --data-root $researchInput --out-dir $OutDir
exit $LASTEXITCODE
