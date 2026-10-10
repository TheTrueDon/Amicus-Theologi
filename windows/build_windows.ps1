# Amicus Theologi 1.0.5: build one-folder exe + Inno Setup on Windows.
# Called from the repository root, including by GitHub Actions.
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)
$repo = Get-Location
python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependencies could not be installed' }
python -m pip install 'pyinstaller>=6.15,<7'
if ($LASTEXITCODE -ne 0) { throw 'PyInstaller could not be installed' }
python -m PyInstaller --noconfirm --clean --onedir --windowed `
  --name 'AmicusTheologi' --paths '.' --icon 'assets/amicus.ico' `
  --add-data 'frontend;frontend' `
  --add-data 'modules/examples;modules/examples' `
  --add-data 'assets/amicus.ico;assets' `
  --add-data 'ANLEITUNG.html;.' `
  --add-data 'ANLEITUNG.css;.' `
  --add-data 'ANLEITUNG.js;.' `
  --collect-submodules 'uvicorn' `
  --collect-submodules 'fastapi' `
  --collect-submodules 'pysword' `
  'windows/launcher.py'
if ($LASTEXITCODE -ne 0) { throw 'PyInstaller build failed' }
Write-Host 'Testing frozen executable ...'
& '.\dist\AmicusTheologi\AmicusTheologi.exe' --self-test
if ($LASTEXITCODE -ne 0) { throw 'Frozen executable self-test failed' }
$paths = @(
  "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
  'C:\Program Files (x86)\Inno Setup 6\ISCC.exe',
  'C:\Program Files\Inno Setup 6\ISCC.exe'
)
$iscc = $paths | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $iscc) { throw 'Inno Setup 6 is missing. Install it from https://jrsoftware.org/isinfo.php' }
& $iscc 'windows/AmicusTheologi.iss'
if ($LASTEXITCODE -ne 0) { throw 'Inno Setup compilation failed' }
Write-Host 'Windows setup created in dist_installer/'
