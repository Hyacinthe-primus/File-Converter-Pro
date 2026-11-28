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

## Channel is a build switch

The channel is **not** hardcoded per branch. `src/app_channel.py` reads it and
derives every channel-specific value (icon, data folder, pipe, autostart value,
toast id, donor marker, staging prefix). Stable is always the default.

`packaging/build.ps1` writes a gitignored `src/_build_channel.py` before
PyInstaller runs:

| Command | Channel | Result |
|---|---|---|
| `.\packaging\build.ps1` | stable | windowed, `icon.ico`, stable metadata |
| `.\packaging\build.ps1 -Channel dev` | dev | console, `icon_DEV`, dev metadata |
| `.\packaging\build_dev.ps1` | dev | shortcut for the command above |

Because the switch is a parameter, merging `dev` into `main` does **not** flip
the stable identity. `main` builds stable unless someone explicitly passes
`-Channel dev`.

## What is different in the dev build

- The executable keeps a **console window** (`console=True`) so logs and
  tracebacks are visible.
- The app uses the **`icon_DEV`** asset for the window, tray, installer and
  shortcuts.
- Task Manager shows **File Converter Pro (Dev version)** while the window title
  and product name stay **File Converter Pro**.

## Build

```powershell
.\packaging\build_dev.ps1
```

Output: `packaging\dist\FCP\FCP.exe`.

For a full dev build with installer and portable ZIP:

```powershell
.\packaging\build_all.ps1 -Channel dev
```

Result: `FileConverterPro_Dev_Setup_v1.0.8-dev.exe` and
`File_Converter_Pro_Dev_v1.0.8-dev.zip`.

For source runs, select the channel with an environment variable:

```powershell
$env:FCP_CHANNEL = "dev"
python src\main.py
```

## Dev MSIX

`packaging\build_msix.ps1 -Channel dev` uses the dev identity
(`PrimeEnterprisesHyacinthe.FileConverterProDev`) and the display name
`File Converter Pro (Dev)`. Use a local dev certificate and install it
alongside the Store app. The dev channel refuses the Store identity; the stable
channel still accepts it.

## Workflow

- Branch features from `dev`, open PRs against `dev`.
- Merge `main` into `dev` regularly so the channel keeps the latest fixes.
- Promote work from `dev` to `main` with a normal merge or PR. The channel
  switch keeps `main` stable by default.

## Local data

Development runs use `src/` for settings, history, themes and languages.
Packaged dev builds use `%LOCALAPPDATA%\FileConverterProDev`.
