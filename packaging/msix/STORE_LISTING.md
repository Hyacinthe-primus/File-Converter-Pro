# Microsoft Store listing

Published: https://apps.microsoft.com/detail/9NSV0DS5R6JH

Copy for the Partner Center submission. Keep it in sync with what the MSIX
package actually does: the Store certifies the listing, not just the binary.

## Product name

File Converter Pro (Prime Enterprises)

## Short description

Convert documents, images, audio and video on your PC. Nothing is uploaded.

## Description

File Converter Pro converts your files locally on your Windows PC. No account,
no uploads, no waiting for a server.

**What you can do**

- Documents: PDF to Word, Office documents to PDF, HTML/Markdown/EPUB to PDF,
  CSV to JSON and more.
- Images: JPG, PNG, WebP, HEIC, TIFF, GIF, SVG and RAW formats; resize,
  compress, convert to icon, or combine into a PDF.
- PDF tools: merge, split, rotate, compress, password-protect, and convert to
  Word.
- Audio and video: common MP3, WAV, FLAC, AAC, MP4, MKV and MOV conversions.
- Archives: ZIP, 7Z, TAR and other common formats.
- Batch conversion, watch folders and scheduled tasks.
- Conversion history, statistics and reusable templates.
- Six interface languages (English, French, Italian, Russian, Turkish,
  Chinese) with a light or dark theme.

**Private by design**

Your files are processed on your device. There is no telemetry, no analytics
and no account. Settings and history are stored locally in
`%LOCALAPPDATA%\FileConverterPro`.

At launch the app requests the public GitHub releases API to show the latest
version number. That request contains no personal data and no file contents.

**Optional components**

Some formats rely on free third-party tools that are not included in this
package:

- FFmpeg - audio and video conversion
- LibreOffice - Microsoft Office format conversion
- Ghostscript - some PDF optimisations
- ImageMagick - additional image operations
- Tesseract - OCR
- 7-Zip - some archive formats
- Pandoc / wkhtmltopdf - additional document and HTML conversions

The app detects these tools automatically when they are installed. If one is
missing, the affected conversion is unavailable and the app tells you which
tool is needed. All other features keep working without them.

**About this Store version**

- The Explorer right-click entry ("Convert with FCP") is not part of the Store
  version. Open files from the app window, or double-click a `.fcproj`
  project.
- Watch folders and scheduled tasks run while the app is open. Starting the
  background daemon automatically at login is not available in the Store
  version.

## Features (for the "Features" field)

- Convert documents, images, audio, video and archives in one app
- Batch conversion and folder processing
- PDF merge, split, compress, protect and PDF-to-Word
- Image resizing, compression and icon export
- 100% local processing - no uploads, no account
- Watch folders and scheduled tasks while the app is open
- Conversion history, statistics and templates
- Six languages with light and dark themes

## Privacy policy (host this text and use the URL in Partner Center)

File Converter Pro processes files only on the user's device. It does not
upload, transmit or share file contents, and it contains no telemetry or
analytics.

The app stores settings, history and logs locally in
`%LOCALAPPDATA%\FileConverterPro`. Uninstalling the app removes the package;
the local data folder can be deleted by the user at any time.

At launch the app requests `https://api.github.com/repos/Hyacinthe-primus/File-Converter-Pro/releases/latest`
to compare version numbers. This request goes to GitHub and contains no
personal data, file contents or device identifiers beyond what any HTTPS
request includes.

The app opens external links (project website, donation page, GitHub) only
when the user chooses them.

## Support

- Issues: https://github.com/Hyacinthe-primus/File-Converter-Pro/issues
- Documentation: https://github.com/Hyacinthe-primus/File-Converter-Pro/wiki

## System requirements

- Windows 10 version 1809 (build 17763) or later, or Windows 11
- x64 processor
- About 400 MB of disk space
- No internet connection required for conversions

## Age rating

The app has no user-generated content, no advertising, no chat and no
location access. It should qualify for the lowest age rating.
