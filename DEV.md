# Dev channel

This branch is the unstable channel for File Converter Pro. Features and fixes
land here before they are promoted to `main`.

## Side-by-side with the stable app

The dev channel is a separate product, not an update to the stable app.

| | Stable | Dev |
|---|---|---|
| Window title | File Converter Pro | File Converter Pro |
| Task Manager | File Converter Pro (64-bit) | File Converter Pro (Dev version) |
| Install folder | `%LOCALAPPDATA%\Programs\FCP` | `%LOCALAPPDATA%\Programs\FCP Dev` |
| Uninstall entry | File Converter Pro | File Converter Pro (Dev) |
| Start Menu / desktop | File Converter Pro | File Converter Pro (Dev) |
| User data | `%LOCALAPPDATA%\FileConverterPro` | `%LOCALAPPDATA%\FileConverterProDev` |
| Single-instance pipe | `FileConverterPro_SingleInstance` | `FileConverterProDev_SingleInstance` |
| Autostart Run value | `FileConverterProDaemon` | `FileConverterProDaemonDev` |

- The dev installer uses its own AppId, install folder, shortcuts and uninstall
  entry. It never upgrades or removes the stable installation.
- The dev installer does **not** register `.fcproj` associations or Explorer
  context-menu entries, so the stable shell integration is untouched.
- Both builds can run at the same time: the data folders and single-instance
  pipes are separate.

## What is different in the build

- The executable keeps a **console window** (`console=True`) so logs and
  tracebacks are visible.
- The app uses the **`icon_DEV`** asset for the window, tray, installer and
  shortcuts.
- Nothing else changes; `main` remains the release branch.

## Build

```powershell
.\packaging\build_dev.ps1
```

Output: `packaging\dist\FCP\FCP.exe`.

`build_dev.ps1` runs PyInstaller directly, without UPX and without building the
installer. `packaging\build.ps1` and `build_all.ps1` still work if you need an
installer build; the result is `FileConverterPro_Dev_Setup_v1.0.8-dev.exe`.

## Dev MSIX

`packaging\build_msix.ps1` defaults to the dev identity
(`PrimeEnterprisesHyacinthe.FileConverterProDev`) and the display name
`File Converter Pro (Dev)`. Use a local dev certificate and install it
alongside the Store app. The script refuses the Store identity.

## Workflow

- Branch features from `dev`, open PRs against `dev`.
- Merge `main` into `dev` regularly so the channel keeps the latest fixes.
- Promote stable work from `dev` to `main` with a PR.

## Local data

Development runs use `src/` for settings, history, themes and languages.
Packaged dev builds use `%LOCALAPPDATA%\FileConverterProDev`.
