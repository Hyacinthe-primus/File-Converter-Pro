# Build the dev channel (console window + icon_DEV + dev identity).

$ErrorActionPreference = "Stop"

Push-Location $PSScriptRoot
& .\build.ps1 -Channel dev
$code = $LASTEXITCODE
Pop-Location
exit $code
