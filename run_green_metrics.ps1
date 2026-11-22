<#
 Create .venv (Python 3.12), install dependencies, then sample + simulate.
 Usage:
   .\run_green_metrics.ps1 -Scenario usa_chiller
   .\run_green_metrics.ps1 -Config config\scenarios\my_site.json [-Root D:\data] [-Overwrite]
 Setup only (no run):  .\run_green_metrics.ps1 -SetupOnly
#>
param(
    [string]$Scenario,
    [string]$Config,
    [string]$Root = $PSScriptRoot,
    [string]$PythonVersion = "3.12",
    [switch]$Overwrite,
    [switch]$SetupOnly
)
$ErrorActionPreference = "Stop"
$Project = $PSScriptRoot
Set-Location $Project
if ($Scenario -and $Config) { throw "Specify either -Scenario or -Config, not both." }

$venvPython = Join-Path $Project ".venv\Scripts\python.exe"
$needVenv = -not (Test-Path $venvPython)
if (-not $needVenv) {
    $v = & $venvPython -c "import sys; print('%d.%d' % sys.version_info[:2])"
    if ($v -notin @("3.10", "3.11", "3.12", "3.13")) {
        throw ".venv uses Python $v (supported: 3.10-3.13). Delete .venv and rerun."
    }
}

if ($needVenv) {
    if (Get-Command uv -ErrorAction SilentlyContinue) {
        # uv downloads Python privately; nothing is installed system-wide.
        uv venv --python $PythonVersion .venv
    } elseif ((Get-Command py -ErrorAction SilentlyContinue) -and ((py -$PythonVersion --version 2>$null) -match "Python")) {
        py -$PythonVersion -m venv .venv
    } else {
        throw "Python $PythonVersion not found. Follow docs/SETUP_GUIDE.md (install uv or Python $PythonVersion), then rerun."
    }
}

Write-Host "Installing dependencies..."
if (Get-Command uv -ErrorAction SilentlyContinue) {
    uv pip install --python $venvPython -r requirements.txt -e .
} else {
    & $venvPython -m pip install --upgrade pip
    & $venvPython -m pip install -r requirements.txt -e .
}
if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed." }
if ($SetupOnly) { Write-Host "Environment ready."; return }

if (-not ($Scenario -or $Config)) { $Scenario = "sri_lanka_dx" }
$cli = @()
if ($Config) { $cli += @("--config", (Resolve-Path $Config).Path) } else { $cli += @("--scenario", $Scenario) }
$cli += @("--root", $Root)

& $venvPython -m green_metrics sample @cli
if ($LASTEXITCODE -ne 0) { throw "Sample generation failed." }
$sim = @("simulate") + $cli
if ($Overwrite) { $sim += "--overwrite" }
& $venvPython -m green_metrics @sim
if ($LASTEXITCODE -ne 0) { throw "Simulation failed." }
Write-Host "Finished. Results are in the scenario's output directory."
