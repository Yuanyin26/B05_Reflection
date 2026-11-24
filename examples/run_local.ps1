param(
    [string]$PythonExecutable = "",
    [string]$OutDir = ""
)

$ErrorActionPreference = "Stop"
$researchRoot = Split-Path -Parent $PSScriptRoot

if (-not $PythonExecutable) {
    if ($env:CONDA_PREFIX -and (Split-Path -Leaf $env:CONDA_PREFIX) -eq "b05-reflection") {
        $researchCondaPython = Join-Path $env:CONDA_PREFIX "python.exe"
        if (Test-Path -LiteralPath $researchCondaPython) {
            $PythonExecutable = $researchCondaPython
        }
    }
    if (-not $PythonExecutable) {
        throw "Activate Conda environment b05-reflection, or pass -PythonExecutable explicitly."
    }
}

if (-not $OutDir) {
    $OutDir = Join-Path $researchRoot "outputs\local"
}

$researchEntry = Join-Path $researchRoot "src\main.py"
$researchInput = Join-Path $researchRoot "data\examples"
& $PythonExecutable $researchEntry --task all --test --check-only --data-root $researchInput --out-dir $OutDir
exit $LASTEXITCODE
