<#
.SYNOPSIS
    Package an existing PyInstaller build as an MSIX for the Microsoft Store.

.DESCRIPTION
    Takes packaging\dist\FCP (onedir output), adds the generated logo assets
    and AppxManifest.xml, and calls MakeAppx.exe from the Windows SDK.

    The package is deliberately left unsigned: the Microsoft Store re-signs
    Store submissions after certification. For sideloading, sign it yourself
    with a trusted certificate.

    Publisher must be the exact Publisher DN shown in Partner Center
    (Account settings -> Organization profile, or the app identity page).
    A mismatched identity fails certification.

.PARAMETER Publisher
    Certificate subject / Publisher DN, for example "CN=1a2b3c4d-...".
    Mandatory: never ship a package with a placeholder identity.

.PARAMETER PackageName
    Identity Name reserved in Partner Center.

.EXAMPLE
    .\build_msix.ps1 -Publisher "CN=01234567-89ab-cdef-0123-456789abcdef" `
                     -PackageName "PrimeEnterprises.FileConverterPro"
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Publisher,

    [string]$PackageName = "PrimeEnterprises.FileConverterPro",
    [string]$DisplayName = "File Converter Pro",
    [string]$Description = "Convert documents, images, audio, video, archives and more.",
    [string]$PublisherDisplayName = "Prime Enterprises",
    [string]$Version = "",
    [ValidateSet("x64", "arm64", "x86")]
    [string]$Architecture = "x64",
    [string]$SourceDir = "",
    [string]$OutputDir = "",
    [string]$MinWindowsVersion = "10.0.17763.0"
)

$ErrorActionPreference = "Stop"

function Write-Step($message) { Write-Host "==> $message" -ForegroundColor Cyan }
function Write-Ok($message) { Write-Host "    $message" -ForegroundColor Green }

$PackagingDir = $PSScriptRoot
$RepoRoot = Split-Path -Parent $PackagingDir

if (-not $SourceDir) { $SourceDir = Join-Path $PackagingDir "dist\FCP" }
if (-not $OutputDir) { $OutputDir = Join-Path $PackagingDir "dist\msix" }

function Get-AppVersion {
    param([string]$Explicit)

    if ($Explicit) { return $Explicit }

    $iss = Join-Path $PackagingDir "setup.iss"
    if (Test-Path -LiteralPath $iss) {
        $match = Select-String -LiteralPath $iss -Pattern '#define\s+MyAppVersion\s+"([^"]+)"' |
            Select-Object -First 1
        if ($match) { return $match.Matches[0].Groups[1].Value }
    }
    throw "Could not determine the app version. Pass -Version x.y.z."
}

function ConvertTo-MsixVersion {
    param([string]$Raw)

    $parts = @($Raw.Trim().Split("."))
    if ($parts.Count -gt 4) { throw "Version '$Raw' has more than four components." }
    while ($parts.Count -lt 4) { $parts += "0" }

    foreach ($part in $parts) {
        if ($part -notmatch '^\d+$') { throw "Version '$Raw' is not numeric." }
    }
    if ([int]$parts[3] -ne 0) {
        throw "MSIX requires the revision (fourth component) to be 0 for Store submissions."
    }
    return ($parts -join ".")
}

function Find-MakeAppx {
    $roots = @(
        (Join-Path ${env:ProgramFiles(x86)} "Windows Kits\10\bin"),
        (Join-Path $env:ProgramFiles "Windows Kits\10\bin")
    ) | Where-Object { $_ -and (Test-Path -LiteralPath $_) }

    $candidates = foreach ($root in $roots) {
        Get-ChildItem -LiteralPath $root -Directory -ErrorAction SilentlyContinue | ForEach-Object {
            $candidate = Join-Path $_.FullName "$Architecture\makeappx.exe"
            if (Test-Path -LiteralPath $candidate) {
                $parsed = [version]"0.0"
                [void][version]::TryParse($_.Name, [ref]$parsed)
                [pscustomobject]@{
                    Path    = $candidate
                    Version = $parsed
                }
            }
        }
    }

    $best = $candidates | Sort-Object Version -Descending | Select-Object -First 1
    if (-not $best) {
        throw "MakeAppx.exe was not found. Install the Windows 10/11 SDK (App Certification Kit)."
    }
    return $best.Path
}

# --- Validate inputs -------------------------------------------------------

if ($Publisher -notmatch '^CN=') {
    throw "Publisher must be a certificate subject starting with 'CN=' (see Partner Center)."
}
if ($PackageName -notmatch '^[A-Za-z0-9.-]{3,50}$' -or $PackageName.EndsWith(".")) {
    throw "PackageName '$PackageName' is not a valid MSIX identity name."
}
if (-not (Test-Path -LiteralPath (Join-Path $SourceDir "FCP.exe"))) {
    throw "FCP.exe not found in '$SourceDir'. Run packaging\build.ps1 first."
}

$ResolvedVersion = ConvertTo-MsixVersion (Get-AppVersion $Version)
$MakeAppx = Find-MakeAppx
Write-Step "Using MakeAppx: $MakeAppx"
Write-Ok "Version $ResolvedVersion ($Architecture)"

# --- Stage the package contents -------------------------------------------

$StageDir = Join-Path $OutputDir "stage"
if (Test-Path -LiteralPath $StageDir) { Remove-Item -LiteralPath $StageDir -Recurse -Force }
New-Item -ItemType Directory -Path $StageDir -Force | Out-Null

Write-Step "Copying application files"
Get-ChildItem -LiteralPath $SourceDir -Force | Copy-Item -Destination $StageDir -Recurse -Force

# Never ship local runtime state: user data, databases, automation rules and
# machine-specific tool paths belong to the installer, not the package.
$localState = @(
    "file_converter_config.dat",
    "file_converter_key.key",
    "file_converter_stats.db",
    "file_converter_stats.db-wal",
    "file_converter_stats.db-shm",
    "file_converter_advanced.db",
    "file_converter_advanced.db-wal",
    "file_converter_advanced.db-shm",
    "achievements.db",
    "achievements.db-wal",
    "achievements.db-shm",
    "donor_pending.json"
)
foreach ($name in $localState) {
    $path = Join-Path $StageDir $name
    if (Test-Path -LiteralPath $path) {
        Remove-Item -LiteralPath $path -Force
        Write-Ok "Removed local state: $name"
    }
}
foreach ($relative in @("automation", "_internal\automation", "config\external_binaries.conf", "_internal\config\external_binaries.conf", "_internal\styles\custom_themes")) {
    $path = Join-Path $StageDir $relative
    if (Test-Path -LiteralPath $path) {
        Remove-Item -LiteralPath $path -Recurse -Force
        Write-Ok "Removed local state: $relative"
    }
}

# python-docx ships an exploded copy of its default template for maintainers.
# It contains "[Content_Types].xml", and MSIX payload paths cannot contain
# square brackets. python-docx reads templates\default.docx at runtime, never
# this folder.
$docxTemplate = Join-Path $StageDir "_internal\docx\templates\default-docx-template"
if (Test-Path -LiteralPath $docxTemplate) {
    Remove-Item -LiteralPath $docxTemplate -Recurse -Force
    Write-Ok "Removed python-docx source template (invalid MSIX path)"
}

# Fail early and clearly instead of letting MakeAppx report 0x8007007b.
$invalid = Get-ChildItem -LiteralPath $StageDir -Recurse -Force |
    Where-Object { $_.Name -match '[\[\]%]' }
if ($invalid) {
    $listing = ($invalid | Select-Object -First 10 | ForEach-Object {
        $_.FullName.Substring($StageDir.Length + 1)
    }) -join "`n  "
    throw "MSIX payload paths cannot contain '[' ']' or '%'. Rename or exclude:`n  $listing"
}

# --- Assets and manifest ---------------------------------------------------

Write-Step "Rendering store logos"
$assetsDir = Join-Path $StageDir "Assets"
& python (Join-Path $PackagingDir "msix\make_assets.py") (Join-Path $RepoRoot "src\Assets\icon.ico") $assetsDir
if ($LASTEXITCODE -ne 0) { throw "Asset generation failed." }

Write-Step "Writing AppxManifest.xml"
$template = Get-Content -LiteralPath (Join-Path $PackagingDir "msix\AppxManifest.template.xml") -Raw
$tokens = [ordered]@{
    "__PACKAGE_NAME__"           = $PackageName
    "__PUBLISHER__"              = $Publisher
    "__PUBLISHER_DISPLAY_NAME__" = [System.Security.SecurityElement]::Escape($PublisherDisplayName)
    "__DISPLAY_NAME__"           = [System.Security.SecurityElement]::Escape($DisplayName)
    "__DESCRIPTION__"            = [System.Security.SecurityElement]::Escape($Description)
    "__VERSION__"                = $ResolvedVersion
    "__ARCHITECTURE__"           = $Architecture
    "__MIN_VERSION__"            = $MinWindowsVersion
}
$manifest = $template
foreach ($token in $tokens.Keys) {
    $manifest = $manifest.Replace($token, $tokens[$token])
}

Set-Content -LiteralPath (Join-Path $StageDir "AppxManifest.xml") -Value $manifest -Encoding UTF8

# --- Pack ------------------------------------------------------------------

$packagePath = Join-Path $OutputDir ("FileConverterPro_{0}_{1}.msix" -f $ResolvedVersion, $Architecture)
if (Test-Path -LiteralPath $packagePath) { Remove-Item -LiteralPath $packagePath -Force }

Write-Step "Packing MSIX"
& $MakeAppx pack /d $StageDir /p $packagePath /o
if ($LASTEXITCODE -ne 0) { throw "MakeAppx failed with exit code $LASTEXITCODE." }

Remove-Item -LiteralPath $StageDir -Recurse -Force

$sizeMb = [math]::Round((Get-Item -LiteralPath $packagePath).Length / 1MB, 1)
Write-Host ""
Write-Host "Package: $packagePath" -ForegroundColor Green
Write-Host "Size:    $sizeMb MB" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Test the package with the Windows App Certification Kit."
Write-Host "  2. Upload it in Partner Center (Packages page of the submission)."
Write-Host "     The Store re-signs it after certification, so no certificate is needed."
