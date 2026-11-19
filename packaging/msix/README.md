# Microsoft Store (MSIX) packaging

The Store accepts two kinds of Windows submissions:

| Route | Account fee | Code signing | Recommendation |
|---|---|---|---|
| **MSIX package** | Free | Microsoft re-signs after certification | ✅ use this |
| MSI/EXE installer | Free | You must buy a CA-trusted certificate | ❌ costs money |

This folder contains everything needed for the MSIX route. The existing Inno
Setup installer stays as the direct-download/GitHub channel.

## Prerequisites

- Windows 10/11 SDK with `MakeAppx.exe` (installed with the Windows SDK or the
  "MSIX Packaging Tools" workload). The script searches
  `%ProgramFiles(x86)%\Windows Kits\10\bin\<version>\<arch>\`.
- Pillow in the build environment (`pip install pillow`) for logo rendering.
- A free Partner Center developer account: <https://storedeveloper.microsoft.com>.

## Build

```powershell
# 1. Produce packaging\dist\FCP
.\packaging\build.ps1

# 2. Package it
.\packaging\build_msix.ps1 `
    -Publisher "CN=00000000-0000-0000-0000-000000000000" `
    -PackageName "PrimeEnterprises.FileConverterPro"
```

Output: `packaging\dist\msix\FileConverterPro_<version>_<arch>.msix`.

### Where the identity values come from

- **Publisher** — Partner Center → Account settings → Organization profile →
  *Publisher DN*. It must match exactly, otherwise certification fails.
  Individual accounts usually get a `CN=<guid>` value.
- **PackageName** — Partner Center → your app → Product identity →
  *Package/Identity/Name*. Use the name you reserved, not a free-form value.
- **Version** — read from `packaging/setup.iss` (`MyAppVersion`) unless
  `-Version` is passed. MSIX needs four numeric parts and revision `0`.

## What the script does

1. Copies `dist\FCP` to a staging folder.
2. Removes local runtime state that must never ship: config, key, SQLite
   databases, `automation\`, and `config\external_binaries.conf`.
3. Removes `_internal\docx\templates\default-docx-template`, a python-docx
   source artifact containing `[Content_Types].xml`. MSIX payload paths cannot
   contain `[` `]` or `%`, and python-docx reads `templates\default.docx` at
   runtime instead.
4. Validates that no payload path still contains `[`, `]` or `%` (MakeAppx
   otherwise fails with the unhelpful `0x8007007b`).
5. Renders the Store logos from `src\Assets\icon.ico`.
6. Fills `AppxManifest.template.xml` and packs the `.msix`.

## Before submitting

1. Run the **Windows App Certification Kit** against the package.
2. In Partner Center, complete:
   - Store listing (description, screenshots, category)
   - Privacy policy URL (the app processes files locally, so a short page
     stating that is enough)
   - Support contact
   - Age rating questionnaire
3. Upload the `.msix` on the **Packages** page. Do not upload a signed copy:
   the Store replaces the signature after certification.

## Current limitations of the Store build

These are tracked separately from packaging:

- **Context menu entries** ("Convert with FCP") are written by the Inno Setup
  installer to `HKCU\Software\Classes`. MSIX cannot do that; it needs a
  `desktop6:Extension` (Windows 11 only). The Store build currently has no
  right-click integration.
- **Daemon autostart** writes a `Run` registry value in `src\daemon.py`. Under
  MSIX this is virtualized and will not start the daemon. It needs a
  `windows.startupTask` extension wired through the `StartupTask` API.
- **External tools** (ffmpeg, LibreOffice, Ghostscript, ImageMagick, Tesseract,
  7-Zip) are detected, never downloaded. The package is ~140 MB and those
  conversions only work when the tool is installed. The listing must say so.
- **Ghostscript is not bundled** (AGPL). Do not add it without a commercial
  license or complying with the AGPL.
- **PySide6 is LGPLv3.** Ship the license notices that PyInstaller already
  collects, and keep the Qt DLLs replaceable.

## Files

| File | Purpose |
|---|---|
| `build_msix.ps1` | Entry point; stages, validates and packs |
| `AppxManifest.template.xml` | Package manifest with `__TOKEN__` placeholders |
| `make_assets.py` | Renders Store logo PNGs from `icon.ico` |
