# Build the dev channel (console window + icon_DEV).

$ErrorActionPreference = "Stop"

if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
    Write-Host "PyInstaller is not installed. Run: pip install pyinstaller" -ForegroundColor Red
    exit 1
}

Push-Location $PSScriptRoot
try {
    pyinstaller --clean --noconfirm build.spec
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed with exit code $LASTEXITCODE"
    }
} finally {
    Pop-Location
}

$exe = Join-Path $PSScriptRoot "dist\FCP\FCP.exe"
Write-Host ""
Write-Host "Dev build ready: $exe" -ForegroundColor Green
Write-Host "Console window and icon_DEV are enabled by build.spec." -ForegroundColor Cyan
