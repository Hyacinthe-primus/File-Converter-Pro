# Dev channel

This branch is the unstable channel for File Converter Pro. Features and fixes
land here before they are promoted to `main`.

## What is different from `main`

- The built executable keeps a **console window** (`console=True` in
  `packaging/build.spec`) so logs and tracebacks are visible.
- The app uses the **`icon_DEV`** asset for the window, tray, installer and
  shortcuts.
- Nothing else changes: `main` remains the release branch.

## Build

```powershell
.\packaging\build_dev.ps1
```

Output: `packaging\dist\FCP\FCP.exe`.

`build_dev.ps1` runs PyInstaller directly, without UPX and without building the
installer. `packaging\build.ps1` and `build_all.ps1` still work if you need an
installer build.

## Workflow

- Branch features from `dev`, open PRs against `dev`.
- Merge `main` into `dev` regularly so the channel keeps the latest fixes.
- Promote stable work from `dev` to `main` with a PR.

## Local data

Development runs use `src/` for settings, history, themes and languages.
Packaged builds use `%LOCALAPPDATA%\FileConverterPro`.
