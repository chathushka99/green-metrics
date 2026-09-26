param(
    [string]$Scenario,
    [string]$Config,
    [string]$Root = $PSScriptRoot
)

$ErrorActionPreference = "Stop"
$Root = [System.IO.Path]::GetFullPath($Root)
Set-Location $Root

if ($Scenario -and $Config) {
    throw "Specify either -Scenario or -Config, not both."
}

$launcher = Get-Command py.exe -ErrorAction SilentlyContinue
if (-not $launcher) {
    Write-Host "CPython 3.7 was not found. Install CPython 3.7.9 from:"
    Write-Host "https://www.python.org/downloads/release/python-379/"
    Write-Host "Select the Python Launcher during installation, then rerun this script."
    Start-Process "https://www.python.org/downloads/release/python-379/"
    throw "Install CPython 3.7.9 and rerun run_green_metrics.bat."
}

& $launcher.Source -3.7 --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "The Python Launcher is installed, but CPython 3.7 is not available."
    Write-Host "Install CPython 3.7.9 from https://www.python.org/downloads/release/python-379/"
    Start-Process "https://www.python.org/downloads/release/python-379/"
    throw "Install CPython 3.7.9 and rerun run_green_metrics.bat."
}

$venv = Join-Path $Root ".venv"
$venvPython = Join-Path $venv "Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    & $launcher.Source -3.7 -m venv $venv
    if ($LASTEXITCODE -ne 0) {
        throw "Could not create the virtual environment at $venv."
    }
}

if (-not (Test-Path $venvPython)) {
    throw "The virtual environment was not created successfully: $venvPython"
}

$venvVersion = & $venvPython --version
if ($venvVersion -notmatch "^Python 3\.7\.") {
    throw "$venv uses $venvVersion; this project requires Python 3.7. Rename or remove .venv and rerun."
}

Write-Host "Installing the pinned project dependencies..."
& $venvPython -m pip install --upgrade "pip<24.1"
if ($LASTEXITCODE -ne 0) {
    throw "Could not install a Python 3.7-compatible pip version."
}

& $venvPython -m pip install -e .
if ($LASTEXITCODE -ne 0) {
    throw "Project installation failed. Review the pip error above."
}

$cliArgs = @()
if ($Config) {
    $configPath = $Config
    if (-not [System.IO.Path]::IsPathRooted($configPath)) {
        $configPath = Join-Path $Root $configPath
    }
    $cliArgs += @("--config", [System.IO.Path]::GetFullPath($configPath))
}
else {
    if (-not $Scenario) {
        $Scenario = "sri_lanka_dx"
    }
    $cliArgs += @("--scenario", $Scenario)
}
$cliArgs += @("--root", $Root)

Write-Host "Generating LHS samples..."
& $venvPython -m green_metrics sample @cliArgs
if ($LASTEXITCODE -ne 0) {
    throw "Sample generation failed. Review the error above."
}

Write-Host "Running EPW simulations..."
& $venvPython -m green_metrics simulate @cliArgs
if ($LASTEXITCODE -ne 0) {
    throw "Simulation failed. Review the error above."
}

Write-Host "Finished. Results are in the configured output directory."
