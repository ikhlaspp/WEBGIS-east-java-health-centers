$ErrorActionPreference = 'Stop'

$repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$pythonPath = Join-Path $repositoryRoot '.venv\Scripts\python.exe'
$runtimeDirectory = Join-Path $repositoryRoot ".tools\jupyter-runtime\$env:USERNAME"
$previousRuntimeDirectory = $env:JUPYTER_RUNTIME_DIR
$previousIPythonDirectory = $env:IPYTHONDIR
$previousConfigDirectory = $env:JUPYTER_CONFIG_DIR
$previousDataDirectory = $env:JUPYTER_DATA_DIR

if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw 'Python environment not found. Create .venv and install requirements.lock first.'
}

Push-Location $repositoryRoot
try {
    New-Item -ItemType Directory -Path $runtimeDirectory -Force | Out-Null
    $env:JUPYTER_RUNTIME_DIR = $runtimeDirectory
    $env:IPYTHONDIR = Join-Path $repositoryRoot '.tools\ipython'
    $env:JUPYTER_CONFIG_DIR = Join-Path $repositoryRoot '.tools\jupyter-config'
    $env:JUPYTER_DATA_DIR = Join-Path $repositoryRoot '.tools\jupyter-data'
    & $pythonPath -m jupyter notebook `
        --no-browser `
        --ServerApp.ip=127.0.0.1 `
        --ServerApp.port=8888 `
        --ServerApp.port_retries=0 `
        --ServerApp.allow_origin=https://colab.research.google.com `
        --ServerApp.allow_credentials=True `
        "--ServerApp.root_dir=$repositoryRoot"
    if ($LASTEXITCODE -ne 0) {
        throw "Jupyter server exited with code $LASTEXITCODE"
    }
}
finally {
    $env:JUPYTER_RUNTIME_DIR = $previousRuntimeDirectory
    $env:IPYTHONDIR = $previousIPythonDirectory
    $env:JUPYTER_CONFIG_DIR = $previousConfigDirectory
    $env:JUPYTER_DATA_DIR = $previousDataDirectory
    Pop-Location
}
