# Patch 4: ImageMagick argument and executable resolution

- **Affected component:** Image-to-PSD conversion through ImageMagick
  (`src/converter/mixins/image_converters.py` and `src/external_binaries.py`).
- **Affected versions:** v1.0.8 and earlier releases that include the
  ImageMagick-backed PSD conversion. The fix is in the unreleased development
  line after v1.0.8.
- **Root cause:** Source and destination paths were passed to ImageMagick
  without normalization, so a relative source path beginning with `-` or `@`
  could be interpreted as an ImageMagick option or listfile. On Windows, the
  ImageMagick executable names also included generic `convert`, which could
  resolve to the Windows filesystem conversion utility instead of ImageMagick.
- **Remediation:** ImageMagick now receives absolute source and destination
  paths. Its tool specification is platform-specific: Windows resolves only
  `magick` and Windows ImageMagick paths; POSIX retains `magick` followed by
  `convert` for ImageMagick 6 compatibility. The existing command, timeout,
  subprocess options, fallback behavior, and executable-resolution priority
  are unchanged.
- **Verification:** Focused ImageMagick argument tests passed 8 tests. The
  external-binary resolution suite passed 25 tests, including Windows and POSIX
  platform simulations. The full suite passed 1085 tests with 8 skipped.
- **Limitations:** ImageMagick policy remains unchanged and permissive; the
  content-based parser/delegate attack surface is tracked separately under the
  third-party parser finding. Output filename `%` expansion is not addressed,
  and no `--`, `-read`, `-write`, signature, or version checks were added.
  Windows ImageMagick 6 now requires an explicit configuration entry because
  generic `convert.exe` is no longer auto-resolved.
